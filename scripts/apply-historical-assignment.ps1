param([switch]$SkipRefresh)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
foreach($dll in @('Microsoft.AnalysisServices.Core.dll','Microsoft.AnalysisServices.Tabular.Json.dll','Microsoft.AnalysisServices.Tabular.dll')){[Reflection.Assembly]::LoadFrom((Join-Path $taskRoot ".tools/tom/lib/net45/$dll"))|Out-Null}
$base=Join-Path $taskRoot 'powerbi-ledningsrapport'
$source=[Microsoft.AnalysisServices.Tabular.TmdlSerializer]::DeserializeDatabaseFromFolder((Join-Path $base 'Ledningsrapport.SemanticModel/definition'))
$manifest=Get-Content (Join-Path $base 'validation/historical-assignment-model.json') -Raw -Encoding utf8|ConvertFrom-Json
$count=0
foreach($engine in @(Get-CimInstance Win32_Process -Filter "name='msmdsrv.exe'")){
 $folder=[regex]::Match($engine.CommandLine,'-s "([^"]+)"').Groups[1].Value
 $port=(Get-Content -LiteralPath (Join-Path $folder 'msmdsrv.port.txt') -Encoding Unicode -Raw).Trim([char]0,[char]13,[char]10)
 $server=New-Object Microsoft.AnalysisServices.Tabular.Server
 $server.Connect("Data Source=localhost:$port;Timeout=60")
 try{
  $db=$server.Databases|Where-Object {$_.Model.Expressions['DataFolder'] -and $_.Model.Expressions['DataFolder'].Expression -like '*powerbi-ledningsrapport/data*' -and $_.Model.Tables['Planinställning']}|Select-Object -First 1
  if(-not $db){continue}
  if(-not $db.Model.Tables['Tidsanvändning']){$db.Model.Tables.Add($source.Model.Tables['Tidsanvändning'].Clone())}
  $relName='Historisk tidsanvändning till Resurser'
  if(-not $db.Model.Relationships[$relName]){
   $r=New-Object Microsoft.AnalysisServices.Tabular.SingleColumnRelationship
   $r.Name=$relName;$r.FromColumn=$db.Model.Tables['Tidsanvändning'].Columns['ResursID'];$r.ToColumn=$db.Model.Tables['Resurser'].Columns['ResursID'];$r.FromCardinality='Many';$r.ToCardinality='One';$r.CrossFilteringBehavior='OneDirection';$db.Model.Relationships.Add($r)
  }
  foreach($name in $manifest.changedMeasures){
   $from=$source.Model.Tables['Planinställning'].Measures[$name];$to=$db.Model.Tables['Planinställning'].Measures[$name]
   if($to){$to.Expression=$from.Expression;$to.FormatString=$from.FormatString}else{$db.Model.Tables['Planinställning'].Measures.Add($from.Clone())}
  }
  $db.Model.Tables['Trendaxel'].Columns['Månadsstart'].FormatString='MMM'
  $db.Model.SaveChanges()|Out-Null
  if(-not $SkipRefresh){
   Write-Output 'Historical measures saved; loading monthly time classifications.'
   $db.Model.Tables['Tidsanvändning'].RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Full)
   $db.Model.Tables['Uppdragsregister'].RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Full)
   $db.Model.SaveChanges()|Out-Null
  }
  $errors=@($db.Model.Tables|ForEach-Object Measures|Where-Object ErrorMessage)
  if($errors.Count){throw ($errors.ErrorMessage -join '; ')}
  Write-Output 'Historical time data loaded; measure metadata reports no errors.'
  $count++
 }finally{$server.Disconnect()}
}
if(-not $count){Write-Output 'No original Desktop model is open; changes saved to source.'}
