param([string]$TableName='Budgetscenarier',[string]$MeasureName='RR utfall en post')
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
  $target=$db.Model.Tables[$TableName].Measures[$MeasureName]
  if($target){$target.Expression=$source.Model.Tables[$TableName].Measures[$MeasureName].Expression}else{$db.Model.Tables[$TableName].Measures.Add($source.Model.Tables[$TableName].Measures[$MeasureName].Clone())}
  $db.Model.SaveChanges()|Out-Null;$found=$true
  if($db.Model.Tables[$TableName].Measures[$MeasureName].ErrorMessage){throw 'Measure evaluation error.'}
  Write-Output "Updated $TableName.$MeasureName in original live model."
 }}finally{$server.Disconnect()}
}
if(-not $found){throw 'Original project is not open.'}
