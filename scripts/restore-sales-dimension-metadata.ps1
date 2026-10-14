$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
foreach($dll in @('Microsoft.AnalysisServices.Core.dll','Microsoft.AnalysisServices.Tabular.Json.dll','Microsoft.AnalysisServices.Tabular.dll')){[Reflection.Assembly]::LoadFrom((Join-Path $taskRoot ".tools/tom/lib/net45/$dll"))|Out-Null}
$engine=Get-CimInstance Win32_Process -Filter "name='msmdsrv.exe'"|Where-Object ParentProcessId -eq 31412|Select-Object -First 1
$folder=[regex]::Match($engine.CommandLine,'-s "([^"]+)"').Groups[1].Value
$port=(Get-Content -LiteralPath (Join-Path $folder 'msmdsrv.port.txt') -Encoding Unicode -Raw).Trim([char]0,[char]13,[char]10)
$server=New-Object Microsoft.AnalysisServices.Tabular.Server;$server.Connect("localhost:$port")
try{
 $db=$server.Databases|Select-Object -First 1
 if($db.Model.Expressions['DataFolder'].Expression -notlike '*powerbi-ledningsrapport/data*'){throw 'Wrong model.'}
 $snapshot=Join-Path $taskRoot ('.tools/customer-metadata-snapshot-'+[guid]::NewGuid().ToString())
 [Microsoft.AnalysisServices.Tabular.TmdlSerializer]::SerializeDatabaseToFolder($db,$snapshot)
 foreach($name in @('Artiklar','Försäljningsserie','Områdesval')){
  Copy-Item -LiteralPath (Join-Path $snapshot "tables/$name.tmdl") -Destination (Join-Path $taskRoot "powerbi-ledningsrapport/Ledningsrapport.SemanticModel/definition/tables/$name.tmdl") -Force
 }
 'Restored the three established dimension metadata files from the matching live model.'
}finally{$server.Disconnect()}
