$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
foreach($dll in @('Microsoft.AnalysisServices.Core.dll','Microsoft.AnalysisServices.Tabular.Json.dll','Microsoft.AnalysisServices.Tabular.dll')){[Reflection.Assembly]::LoadFrom((Join-Path $taskRoot ".tools/tom/lib/net45/$dll"))|Out-Null}
$count=0
foreach($engine in @(Get-CimInstance Win32_Process -Filter "name='msmdsrv.exe'")){
 $folder=[regex]::Match($engine.CommandLine,'-s "([^"]+)"').Groups[1].Value
 $port=(Get-Content -LiteralPath (Join-Path $folder 'msmdsrv.port.txt') -Encoding Unicode -Raw).Trim([char]0,[char]13,[char]10)
 $server=New-Object Microsoft.AnalysisServices.Tabular.Server
 $server.Connect("Data Source=localhost:$port;Timeout=60")
 try{
  $db=$server.Databases|Where-Object {$_.Model.Expressions['DataFolder'] -and $_.Model.Expressions['DataFolder'].Expression -like '*powerbi-ledningsrapport/data*' -and $_.Model.Tables['Budgetrapportnoder']}|Select-Object -First 1
  if(-not $db){continue}
  foreach($name in @('Kunder','Försäljning','Direkta kostnader')){$db.Model.Tables[$name].RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Full)}
  $db.Model.SaveChanges()|Out-Null
  $count++
  Write-Output 'Refreshed customer history, sales and attributable costs in the original loaded model.'
 }finally{$server.Disconnect()}
}
if(-not $count){Write-Output 'No matching original model is open; source files are ready for Desktop Refresh.'}
