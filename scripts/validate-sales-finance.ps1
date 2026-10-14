param([int]$DesktopProcessId = 0, [string]$QueryName = 'measure-check.dax', [string]$OutputName = 'desktop-dax.json', [switch]$SkipRefresh)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$project = Join-Path $root 'powerbi-sales-finance'
foreach ($library in @('Microsoft.AnalysisServices.Core.dll','Microsoft.AnalysisServices.Tabular.Json.dll','Microsoft.AnalysisServices.Tabular.dll')) {
    [Reflection.Assembly]::LoadFrom((Join-Path $root ".tools/tom/lib/net45/$library")) | Out-Null
}
$database = [Microsoft.AnalysisServices.Tabular.TmdlSerializer]::DeserializeDatabaseFromFolder((Join-Path $project 'AubecoSalesFinance.SemanticModel/definition'))
if ($database.Model.Tables.Count -ne 10 -or $database.Model.Relationships.Count -ne 4 -or -not $database.Model.Tables['Rapportstatus']) { throw 'Expected ten tables (including refresh metadata) and four relationships.' }
foreach ($r in $database.Model.Relationships) { if ($r.CrossFilteringBehavior.ToString() -ne 'OneDirection' -or $r.FromCardinality.ToString() -ne 'Many' -or $r.ToCardinality.ToString() -ne 'One') { throw 'Invalid relationship'; } }
$metadata = @($database.Model.Tables | ForEach-Object { @{name=$_.Name;columns=@($_.Columns | ForEach-Object Name);measures=@($_.Measures | ForEach-Object Name);mode=$_.Partitions[0].Mode.ToString()} })
if (@($metadata | Where-Object mode -ne 'Import').Count) { throw 'Non Import partition'; }
@{status='passed';tool='Microsoft TOM';tables=$metadata;limitations='No DAX executed in static mode.'} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $project 'validation/tmdl-result.json') -Encoding UTF8
if ($DesktopProcessId -eq 0) { 'TMDL: passed, ten Import tables and four single-direction relationships.'; exit }
$engine = Get-CimInstance Win32_Process -Filter "name='msmdsrv.exe'" | Where-Object ParentProcessId -eq $DesktopProcessId | Select-Object -First 1
if (-not $engine) { throw 'The requested Desktop process has no model engine.' }
$folder = [regex]::Match($engine.CommandLine,'-s "([^"]+)"').Groups[1].Value
$binary = [regex]::Match($engine.CommandLine,'^"([^"]+)"').Groups[1].Value
$port = (Get-Content -LiteralPath (Join-Path $folder 'msmdsrv.port.txt') -Encoding Unicode -Raw).Trim([char]0,[char]13,[char]10)
$server = New-Object Microsoft.AnalysisServices.Tabular.Server
$server.Connect("localhost:$port")
try {
    $live = $server.Databases | Select-Object -First 1
    if ($live.Model.Tables.Count -ne 10 -or $live.Model.Expressions['DataFolder'].Expression -notlike '*powerbi-sales-finance/data*') { throw "Wrong live project: $($live.Name)" }
    if (-not $SkipRefresh) {
        $live.Model.RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Full)
        $live.Model.SaveChanges() | Out-Null
    }
    $errors = @($live.Model.Tables | ForEach-Object Measures | Where-Object ErrorMessage)
    if ($errors.Count) { throw ($errors.ErrorMessage -join '; ') }
    [Reflection.Assembly]::LoadFrom((Join-Path (Split-Path -Parent $binary) 'Microsoft.PowerBI.AdomdClient.dll')) | Out-Null
    $connection = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$port;Initial Catalog=$($live.ID)")
    $connection.Open()
    try {
        $command=$connection.CreateCommand();$command.CommandTimeout=60
        $command.CommandText=Get-Content -LiteralPath (Join-Path (Join-Path $project 'validation') $QueryName) -Raw -Encoding UTF8
        $reader=$command.ExecuteReader();$rows=@()
        while ($reader.Read()) { $row=[ordered]@{};for($i=0;$i -lt $reader.FieldCount;$i++) { $row[$reader.GetName($i)]=if($reader.IsDBNull($i)){$null}else{$reader.GetValue($i)} };$rows += [pscustomobject]$row }
        $reader.Close()
        @{status='passed';source='Actual Desktop engine, DAX query';desktopProcessId=$DesktopProcessId;rows=$rows} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path (Join-Path $project 'validation') $OutputName) -Encoding UTF8
        $rows | ConvertTo-Json -Depth 4
    } finally { $connection.Close() }
} finally { $server.Disconnect() }
