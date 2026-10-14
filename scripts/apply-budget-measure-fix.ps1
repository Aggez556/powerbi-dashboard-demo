# Correct only the six demo measures in the existing local Desktop model.
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$engine = Get-CimInstance Win32_Process -Filter "name='msmdsrv.exe'" | Select-Object -First 1
$dataFolder = [regex]::Match($engine.CommandLine, '-s "([^"]+)"').Groups[1].Value
$port = (Get-Content -LiteralPath (Join-Path $dataFolder 'msmdsrv.port.txt') -Encoding Unicode -Raw).Trim([char]0,[char]13,[char]10)
foreach ($library in @('Microsoft.AnalysisServices.Core.dll','Microsoft.AnalysisServices.Tabular.Json.dll','Microsoft.AnalysisServices.Tabular.dll')) {
    [Reflection.Assembly]::LoadFrom((Join-Path $projectRoot ".tools/tom/lib/net45/$library")) | Out-Null
}
$definition = [Microsoft.AnalysisServices.Tabular.TmdlSerializer]::DeserializeDatabaseFromFolder((Join-Path $projectRoot 'powerbi/AubecoHandel.SemanticModel/definition'))
$sourceTable = $definition.Model.Tables | Where-Object { $_.Measures.Count -gt 0 } | Select-Object -First 1
$server = New-Object Microsoft.AnalysisServices.Tabular.Server
$server.Connect("localhost:$port")
try {
    $database = $server.Databases | Select-Object -First 1
    $targetTable = $database.Model.Tables[$sourceTable.Name]
    $measures = @($sourceTable.Measures | Where-Object { $_.DisplayFolder -eq 'Budgetplanering' })
    if ($measures.Count -ne 6) { throw 'Expected six budget measures.' }
    $before = @($measures | ForEach-Object { @{name=$_.Name; expression=$targetTable.Measures[$_.Name].Expression} })
    $before | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath (Join-Path $projectRoot 'powerbi/validation/budget-measures-before-fix.json') -Encoding UTF8
    foreach ($measure in $measures) {
        if (-not $targetTable.Measures[$measure.Name]) { throw 'Live model missing budget measure.' }
        $targetTable.Measures[$measure.Name].Expression = $measure.Expression
    }
    $database.Model.RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Calculate)
    $database.Model.SaveChanges()
    $states = @($measures | ForEach-Object { @{name=$_.Name;state=$targetTable.Measures[$_.Name].State.ToString();error=$targetTable.Measures[$_.Name].ErrorMessage} })
    if (@($states | Where-Object { $_.error }).Count -gt 0) { throw 'A corrected measure still has an engine error.' }
    @{status='passed';operation='Update six local budget measure expressions and calculate';measures=$states} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $projectRoot 'powerbi/validation/budget-live-fix.json') -Encoding UTF8
    'Six local budget measures corrected and calculated successfully.'
} finally { $server.Disconnect() }
