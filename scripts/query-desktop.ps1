param([string]$QueryFile = 'powerbi/validation/budget-diagnostic.dax')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$engine = Get-CimInstance Win32_Process -Filter "name='msmdsrv.exe'" | Select-Object -First 1
if (-not $engine) { throw 'No local Desktop engine found.' }
$dataFolder = [regex]::Match($engine.CommandLine, '-s "([^"]+)"').Groups[1].Value
$engineBinary = [regex]::Match($engine.CommandLine, '^"([^"]+)"').Groups[1].Value
$port = (Get-Content -LiteralPath (Join-Path $dataFolder 'msmdsrv.port.txt') -Encoding Unicode -Raw).Trim([char]0, [char]13, [char]10)
foreach ($library in @('Microsoft.AnalysisServices.Core.dll','Microsoft.AnalysisServices.Tabular.Json.dll','Microsoft.AnalysisServices.Tabular.dll')) {
    [Reflection.Assembly]::LoadFrom((Join-Path $projectRoot ".tools/tom/lib/net45/$library")) | Out-Null
}
$server = New-Object Microsoft.AnalysisServices.Tabular.Server
$server.Connect("localhost:$port")
$database = $server.Databases | Select-Object -First 1
[Reflection.Assembly]::LoadFrom((Join-Path (Split-Path -Parent $engineBinary) 'Microsoft.PowerBI.AdomdClient.dll')) | Out-Null
$connection = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$port;Initial Catalog=$($database.ID)")
$connection.Open()
try {
    $command = $connection.CreateCommand()
    $command.CommandText = Get-Content -LiteralPath (Join-Path $projectRoot $QueryFile) -Encoding UTF8 -Raw
    $command.CommandTimeout = 60
    $reader = $command.ExecuteReader()
    $rows = @()
    while ($reader.Read()) {
        $row = [ordered]@{}
        for ($i=0; $i -lt $reader.FieldCount; $i++) { $row[$reader.GetName($i)] = if ($reader.IsDBNull($i)) { $null } else { $reader.GetValue($i) } }
        $rows += [pscustomobject]$row
    }
    $reader.Close()
    $result = @{ status='passed'; source='Actual local Desktop DAX engine'; rowCount=$rows.Count; rows=$rows }
    $result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $projectRoot 'powerbi/validation/budget-dax-result.json') -Encoding UTF8
    @{status='passed';rowCount=$rows.Count;firstRows=@($rows | Select-Object -First 3)} | ConvertTo-Json -Depth 5
} finally { $connection.Close(); $server.Disconnect() }
