$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
foreach($dll in @('Microsoft.AnalysisServices.Core.dll','Microsoft.AnalysisServices.Tabular.Json.dll','Microsoft.AnalysisServices.Tabular.dll')){[Reflection.Assembly]::LoadFrom((Join-Path $taskRoot ".tools/tom/lib/net45/$dll"))|Out-Null}
$source=[Microsoft.AnalysisServices.Tabular.TmdlSerializer]::DeserializeDatabaseFromFolder((Join-Path $taskRoot 'powerbi-ledningsrapport/Ledningsrapport.SemanticModel/definition'))
$engine=Get-CimInstance Win32_Process -Filter "name='msmdsrv.exe'"|Sort-Object CreationDate -Descending|Select-Object -First 1
if(-not $engine){throw 'Open the original report first.'}
$folder=[regex]::Match($engine.CommandLine,'-s "([^"]+)"').Groups[1].Value
$port=(Get-Content -LiteralPath (Join-Path $folder 'msmdsrv.port.txt') -Encoding Unicode -Raw).Trim([char]0,[char]13,[char]10)
$server=New-Object Microsoft.AnalysisServices.Tabular.Server
$server.Connect("Data Source=localhost:$port;Timeout=60")
try{
 $db=$server.Databases|Where-Object {$null -ne $_.Model.Tables['Planbokningar']}|Select-Object -First 1
 if(-not $db -or $db.Model.Expressions['DataFolder'].Expression -notlike '*powerbi-ledningsrapport/data*'){throw 'Wrong model.'}
 $from=$source.Model.Tables|Where-Object {$null -ne $_.Measures['Uppdrag risk']}
 $to=$db.Model.Tables[$from.Name]
 foreach($measure in $from.Measures|Where-Object {$_.Name -in @('Uppdrag risk','Uppdrag prognostext','Uppdrag trendrubrik','Utfall timmar','Plan ledigt') -or $_.Name -like 'Uppdrag marginalf*' -or $_.Name -like 'Trend axel *'}){
  if($to.Measures[$measure.Name]){$to.Measures[$measure.Name].Expression=$measure.Expression;$to.Measures[$measure.Name].FormatString=$measure.FormatString}else{$to.Measures.Add($measure.Clone())}
 }
 $status=$db.Model.Tables['Uppdragsstatusval']
 $needsStatusRefresh=-not $status.Columns['Visningsordning']
 if($needsStatusRefresh){$status.Columns.Add($source.Model.Tables['Uppdragsstatusval'].Columns['Visningsordning'].Clone())}
 $status.Columns['Urval'].SortByColumn=$status.Columns['Visningsordning']
 if($needsStatusRefresh){$status.Partitions[0].Source.Expression=$source.Model.Tables['Uppdragsstatusval'].Partitions[0].Source.Expression;$status.RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Full)}
 $db.Model.SaveChanges()|Out-Null
 Write-Output 'Updated forecast guards and status order; refreshed only the four-row status lookup.'
}finally{$server.Disconnect()}
