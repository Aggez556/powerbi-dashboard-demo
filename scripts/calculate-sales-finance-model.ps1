param([Parameter(Mandatory=$true)][int]$DesktopProcessId)
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
foreach ($library in @('Microsoft.AnalysisServices.Core.dll','Microsoft.AnalysisServices.Tabular.Json.dll','Microsoft.AnalysisServices.Tabular.dll')) {
    [Reflection.Assembly]::LoadFrom((Join-Path $taskRoot ".tools/tom/lib/net45/$library")) | Out-Null
}
$engine = Get-CimInstance Win32_Process -Filter "name='msmdsrv.exe'" | Where-Object ParentProcessId -eq $DesktopProcessId | Select-Object -First 1
if (-not $engine) { throw 'Selected Desktop has no model engine.' }
$folder = [regex]::Match($engine.CommandLine,'-s "([^"]+)"').Groups[1].Value
$port = (Get-Content -LiteralPath (Join-Path $folder 'msmdsrv.port.txt') -Encoding Unicode -Raw).Trim([char]0,[char]13,[char]10)
$server = New-Object Microsoft.AnalysisServices.Tabular.Server
$server.Connect("localhost:$port")
try {
    $live = $server.Databases | Select-Object -First 1
    if ($live.Model.Tables.Count -ne 10 -or -not $live.Model.Tables['Rapportstatus'] -or $live.Model.Expressions['DataFolder'].Expression -notlike '*powerbi-sales-finance/data*') { throw 'Wrong live project.' }
    $live.Model.RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Calculate)
    $live.Model.SaveChanges() | Out-Null
    $errors = @($live.Model.Tables | ForEach-Object Measures | Where-Object ErrorMessage)
    if ($errors.Count) { throw ($errors.ErrorMessage -join '; ') }
    'Model calculation completed; Import source data unchanged.'
} finally { $server.Disconnect() }
