$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
foreach($dll in @('Microsoft.AnalysisServices.Core.dll','Microsoft.AnalysisServices.Tabular.Json.dll','Microsoft.AnalysisServices.Tabular.dll')){[Reflection.Assembly]::LoadFrom((Join-Path $taskRoot ".tools/tom/lib/net45/$dll"))|Out-Null}
$source=[Microsoft.AnalysisServices.Tabular.TmdlSerializer]::DeserializeDatabaseFromFolder((Join-Path $taskRoot 'powerbi-ledningsrapport/Ledningsrapport.SemanticModel/definition'))
$engine=Get-CimInstance Win32_Process -Filter "name='msmdsrv.exe'"|Sort-Object CreationDate -Descending|Select-Object -First 1
if(-not $engine){Write-Output 'No Desktop instance: source changes are saved for next open.';exit 0}
$folder=[regex]::Match($engine.CommandLine,'-s "([^"]+)"').Groups[1].Value
$port=(Get-Content -LiteralPath (Join-Path $folder 'msmdsrv.port.txt') -Encoding Unicode -Raw).Trim([char]0,[char]13,[char]10)
$server=New-Object Microsoft.AnalysisServices.Tabular.Server
$server.Connect("Data Source=localhost:$port;Timeout=30")
try{
 $db=$server.Databases|Where-Object {$null -ne $_.Model.Tables['Budgetrapportnoder']}|Select-Object -First 1
 if(-not $db -or $db.Model.Expressions['DataFolder'].Expression -notlike '*powerbi-ledningsrapport/data*'){throw 'Wrong model.'}
 $from=$source.Model.Tables['Budgetrapportnoder'];$to=$db.Model.Tables['Budgetrapportnoder']
 foreach($m in $from.Measures){if($to.Measures[$m.Name]){$to.Measures[$m.Name].Expression=$m.Expression}else{$to.Measures.Add($m.Clone())}}
 $db.Model.SaveChanges()|Out-Null
 Write-Output 'Updated statement variance measures; no data refresh.'
}finally{$server.Disconnect()}
