param([switch]$SkipRefresh)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
foreach($dll in @('Microsoft.AnalysisServices.Core.dll','Microsoft.AnalysisServices.Tabular.Json.dll','Microsoft.AnalysisServices.Tabular.dll')){[Reflection.Assembly]::LoadFrom((Join-Path $taskRoot ".tools/tom/lib/net45/$dll"))|Out-Null}
$source=[Microsoft.AnalysisServices.Tabular.TmdlSerializer]::DeserializeDatabaseFromFolder((Join-Path $taskRoot 'powerbi-ledningsrapport/Ledningsrapport.SemanticModel/definition'))
$found=$false
foreach($engine in @(Get-CimInstance Win32_Process -Filter "name='msmdsrv.exe'")){
 $folder=[regex]::Match($engine.CommandLine,'-s "([^"]+)"').Groups[1].Value
 $port=(Get-Content -LiteralPath (Join-Path $folder 'msmdsrv.port.txt') -Encoding Unicode -Raw).Trim([char]0,[char]13,[char]10)
 $server=New-Object Microsoft.AnalysisServices.Tabular.Server;$server.Connect("localhost:$port")
 try{foreach($db in $server.Databases){
  if(-not $db.Model.Expressions['DataFolder'] -or $db.Model.Expressions['DataFolder'].Expression -notlike '*powerbi-ledningsrapport/data*'){continue}
  foreach($m in $source.Model.Tables['Budgetscenarier'].Measures){
   $live=$db.Model.Tables['Budgetscenarier'].Measures[$m.Name]
   if($live){$live.Expression=$m.Expression}else{$db.Model.Tables['Budgetscenarier'].Measures.Add($m.Clone())}
  }
  if(-not $SkipRefresh){foreach($name in @('Budgetscenarion','Budgetkolumner')){
   foreach($column in $source.Model.Tables[$name].Columns){$db.Model.Tables[$name].Columns[$column.Name].SourceColumn=$column.SourceColumn}
   $partitionSource=New-Object Microsoft.AnalysisServices.Tabular.MPartitionSource
   $partitionSource.Expression=$source.Model.Tables[$name].Partitions[0].Source.Expression
   $db.Model.Tables[$name].Partitions[0].Source=$partitionSource
  }}
  $db.Model.SaveChanges()|Out-Null
  if(-not $SkipRefresh){foreach($name in @('Budgetscenarion','Budgetkolumner')){$db.Model.Tables[$name].RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Full)}}
  $db.Model.SaveChanges()|Out-Null;$found=$true
  Write-Output 'Applied prior-year comparison measures; selector refresh is optional.'
 }}finally{$server.Disconnect()}
}
if(-not $found){throw 'Original project is not open.'}
