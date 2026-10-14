param([string]$QueryFile = '')
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
foreach ($library in @('Microsoft.AnalysisServices.Core.dll','Microsoft.AnalysisServices.Tabular.Json.dll','Microsoft.AnalysisServices.Tabular.dll')) {
    [Reflection.Assembly]::LoadFrom((Join-Path $taskRoot ".tools/tom/lib/net45/$library")) | Out-Null
}
$source = [Microsoft.AnalysisServices.Tabular.TmdlSerializer]::DeserializeDatabaseFromFolder((Join-Path $taskRoot 'powerbi-ledningsrapport/Ledningsrapport.SemanticModel/definition'))
$matches = 0
foreach ($engine in @(Get-CimInstance Win32_Process -Filter "name='msmdsrv.exe'")) {
    $folder = [regex]::Match($engine.CommandLine,'-s "([^"]+)"').Groups[1].Value
    $port = (Get-Content -LiteralPath (Join-Path $folder 'msmdsrv.port.txt') -Encoding Unicode -Raw).Trim([char]0,[char]13,[char]10)
    $server = New-Object Microsoft.AnalysisServices.Tabular.Server
    $server.Connect("localhost:$port")
    try {
        $db = $server.Databases | Select-Object -First 1
        if (-not $db.Model.Expressions['DataFolder'] -or $db.Model.Expressions['DataFolder'].Expression -notlike '*powerbi-ledningsrapport/data*') { continue }
        $matches++
        $changes = @()
        foreach ($name in @('Kundförändring korttext','Rörelsemarginal korttext','Periodtext')) {
            $measure = $db.Model.Tables['Försäljning'].Measures[$name]
            if (-not $measure) { throw "Missing display measure $name" }
            $previous = $measure.Expression
            $measure.Expression = $source.Model.Tables['Försäljning'].Measures[$name].Expression
            $changes += @{name=$name;before=$previous;after=$measure.Expression}
        }
        $db.Model.RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Calculate)
        $db.Model.SaveChanges() | Out-Null
        foreach ($name in @('Kundförändring korttext','Rörelsemarginal korttext','Periodtext')) { if ($db.Model.Tables['Försäljning'].Measures[$name].ErrorMessage) { throw $db.Model.Tables['Försäljning'].Measures[$name].ErrorMessage } }
        $binary = [regex]::Match($engine.CommandLine,'^"([^"]+)"').Groups[1].Value
        [Reflection.Assembly]::LoadFrom((Join-Path (Split-Path -Parent $binary) 'Microsoft.PowerBI.AdomdClient.dll')) | Out-Null
        $connection = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$port;Initial Catalog=$($db.ID)")
        $connection.Open()
        try {
            $command = $connection.CreateCommand()
            $command.CommandText = 'EVALUATE ROW("Kundtext", [Kundförändring korttext], "Resultattext", [Rörelsemarginal korttext])'
            if ($QueryFile) { $command.CommandText=Get-Content -LiteralPath (Join-Path $taskRoot $QueryFile) -Raw -Encoding utf8 }
            $reader = $command.ExecuteReader()
            $rows=@()
            while ($reader.Read()) { $row=[ordered]@{};for($i=0;$i -lt $reader.FieldCount;$i++){$row[$reader.GetName($i)]=$reader.GetValue($i)};$rows += $row }
            $reader.Close()
            $result=@{status='passed';source='Live Desktop DAX engine';desktopProcessId=$engine.ParentProcessId;changes=$changes;rows=$rows}
            $outputName=if($QueryFile){'powerbi-ledningsrapport/validation/period-text-live.json'}else{'powerbi-ledningsrapport/validation/kpi-live-text.json'}
            $result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskRoot $outputName) -Encoding utf8
            $result | ConvertTo-Json -Depth 5
        } finally { $connection.Close() }
    } finally { $server.Disconnect() }
}
if ($matches -eq 0) { throw 'No matching live Ledningsrapport model found.' }
