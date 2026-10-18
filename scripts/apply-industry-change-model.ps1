$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
foreach($dll in @('Microsoft.AnalysisServices.Core.dll','Microsoft.AnalysisServices.Tabular.Json.dll','Microsoft.AnalysisServices.Tabular.dll')){[Reflection.Assembly]::LoadFrom((Join-Path $taskRoot ".tools/tom/lib/net45/$dll"))|Out-Null}
$source=[Microsoft.AnalysisServices.Tabular.TmdlSerializer]::DeserializeDatabaseFromFolder((Join-Path $taskRoot 'powerbi-ledningsrapport/Ledningsrapport.SemanticModel/definition'))
$names=Get-Content (Join-Path $taskRoot 'powerbi-ledningsrapport/validation/industry-change-measures.json') -Raw -Encoding utf8 | ConvertFrom-Json
$found=$false
foreach($engine in @(Get-CimInstance Win32_Process -Filter "name='msmdsrv.exe'")){
 $folder=[regex]::Match($engine.CommandLine,'-s "([^"]+)"').Groups[1].Value
 $port=(Get-Content -LiteralPath (Join-Path $folder 'msmdsrv.port.txt') -Encoding Unicode -Raw).Trim([char]0,[char]13,[char]10)
 $server=New-Object Microsoft.AnalysisServices.Tabular.Server;$server.Connect("localhost:$port")
 try{foreach($db in $server.Databases){
  if(-not $db.Model.Expressions['DataFolder'] -or $db.Model.Expressions['DataFolder'].Expression -notlike '*powerbi-ledningsrapport/data*'){continue}
  foreach($name in $names){
   $m=$source.Model.Tables['Kunder'].Measures[$name];$live=$db.Model.Tables['Kunder'].Measures[$name]
   if($live){$live.Expression=$m.Expression;$live.FormatString=$m.FormatString}else{$db.Model.Tables['Kunder'].Measures.Add($m.Clone())}
  }
  $db.Model.SaveChanges()|Out-Null;$found=$true
  foreach($name in $names){if($db.Model.Tables['Kunder'].Measures[$name].ErrorMessage){throw $db.Model.Tables['Kunder'].Measures[$name].ErrorMessage}}
  Write-Output "Applied $($names.Count) industry trend measures; no import refresh."
 }}finally{$server.Disconnect()}
}
if(-not $found){throw 'Open the original Ledningsrapport project to validate the new measures.'}
