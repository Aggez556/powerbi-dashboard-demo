$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
foreach($dll in @('Microsoft.AnalysisServices.Core.dll','Microsoft.AnalysisServices.Tabular.Json.dll','Microsoft.AnalysisServices.Tabular.dll')){[Reflection.Assembly]::LoadFrom((Join-Path $taskRoot ".tools/tom/lib/net45/$dll"))|Out-Null}
foreach($engine in @(Get-CimInstance Win32_Process -Filter "name='msmdsrv.exe'")){
 $folder=[regex]::Match($engine.CommandLine,'-s "([^"]+)"').Groups[1].Value
 $port=(Get-Content -LiteralPath (Join-Path $folder 'msmdsrv.port.txt') -Encoding Unicode -Raw).Trim([char]0,[char]13,[char]10)
 $server=New-Object Microsoft.AnalysisServices.Tabular.Server;$server.Connect("localhost:$port")
 try{foreach($db in $server.Databases){
  if(-not $db.Model.Expressions['DataFolder'] -or $db.Model.Expressions['DataFolder'].Expression -notlike '*powerbi-ledningsrapport/data*'){continue}
  $tables=@($db.Model.Tables|Where-Object {$_.Name -in @('Budgetscenarion','Budgetkolumner') -or $_.Name -like 'Budgetj*mf*relsescenario'})
  if($tables.Count -ne 3){throw 'Expected exactly three scenario label tables.'}
  foreach($table in $tables){$table.RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Full)}
  $db.Model.SaveChanges()|Out-Null
  Write-Output 'Refreshed three label tables; budget facts, IDs and amounts unchanged.'
 }}finally{$server.Disconnect()}
}
