$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
foreach($dll in @('Microsoft.AnalysisServices.Core.dll','Microsoft.AnalysisServices.Tabular.Json.dll','Microsoft.AnalysisServices.Tabular.dll')){[Reflection.Assembly]::LoadFrom((Join-Path $taskRoot ".tools/tom/lib/net45/$dll"))|Out-Null}
$found=$false
foreach($engine in @(Get-CimInstance Win32_Process -Filter "name='msmdsrv.exe'")){
 $folder=[regex]::Match($engine.CommandLine,'-s "([^"]+)"').Groups[1].Value
 $port=(Get-Content -LiteralPath (Join-Path $folder 'msmdsrv.port.txt') -Encoding Unicode -Raw).Trim([char]0,[char]13,[char]10)
 $server=New-Object Microsoft.AnalysisServices.Tabular.Server
 $server.Connect("Data Source=localhost:$port;Timeout=60")
 try{
  foreach($db in $server.Databases){
   if(-not $db.Model.Expressions['DataFolder'] -or $db.Model.Expressions['DataFolder'].Expression -notlike '*powerbi-ledningsrapport/data*'){continue}
   $tableName='F'+[char]246+'rs'+[char]228+'ljning'
   $db.Model.Tables[$tableName].RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Full)
   $db.Model.SaveChanges()|Out-Null
   $found=$true;Write-Output 'Refreshed sales fact table in the original project.'
  }
 }finally{$server.Disconnect()}
}
if(-not $found){throw 'Original project is not open.'}
