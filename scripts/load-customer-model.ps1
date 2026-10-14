param([switch]$QueryOnly,[switch]$SkipRefresh,[switch]$RefreshCustomerLabels)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot;$base=Join-Path $taskRoot 'powerbi-ledningsrapport'
foreach($dll in @('Microsoft.AnalysisServices.Core.dll','Microsoft.AnalysisServices.Tabular.Json.dll','Microsoft.AnalysisServices.Tabular.dll')){[Reflection.Assembly]::LoadFrom((Join-Path $taskRoot ".tools/tom/lib/net45/$dll"))|Out-Null}
$source=[Microsoft.AnalysisServices.Tabular.TmdlSerializer]::DeserializeDatabaseFromFolder((Join-Path $base 'Ledningsrapport.SemanticModel/definition'))
$engine=Get-CimInstance Win32_Process -Filter "name='msmdsrv.exe'"|Sort-Object CreationDate -Descending|Select-Object -First 1
if(-not $engine){throw 'Current report Desktop engine not found.'}
$folder=[regex]::Match($engine.CommandLine,'-s "([^"]+)"').Groups[1].Value
$binary=[regex]::Match($engine.CommandLine,'^"([^"]+)"').Groups[1].Value
$port=(Get-Content -LiteralPath (Join-Path $folder 'msmdsrv.port.txt') -Encoding Unicode -Raw).Trim([char]0,[char]13,[char]10)
$server=New-Object Microsoft.AnalysisServices.Tabular.Server;$server.Connect("Data Source=localhost:$port;Timeout=60")
try{
 $db=$server.Databases|Select-Object -First 1
 if($db.Model.Expressions['DataFolder'].Expression -notlike '*powerbi-ledningsrapport/data*'){throw 'Wrong Desktop project.'}
 if(-not $QueryOnly){
  foreach($name in @('Kundstatusval','Kundgrupper','Kundbassteg','Kundintäktssteg')){if(-not $db.Model.Tables[$name]){$db.Model.Tables.Add($source.Model.Tables[$name].Clone())}}
  foreach($name in @('Kunder','Direkta kostnader')){
   foreach($column in $source.Model.Tables[$name].Columns){if(-not $db.Model.Tables[$name].Columns[$column.Name]){$db.Model.Tables[$name].Columns.Add($column.Clone())}}
   $db.Model.Tables[$name].Partitions[0].Source.Expression=$source.Model.Tables[$name].Partitions[0].Source.Expression
  }
  $measureNames=Get-Content -LiteralPath (Join-Path $base 'validation/customer-measure-names.json') -Raw -Encoding utf8|ConvertFrom-Json
  foreach($name in $measureNames){
   if($db.Model.Tables['Försäljning'].Measures[$name]){$db.Model.Tables['Försäljning'].Measures[$name].Expression=$source.Model.Tables['Försäljning'].Measures[$name].Expression}
   else{$db.Model.Tables['Försäljning'].Measures.Add($source.Model.Tables['Försäljning'].Measures[$name].Clone())}
  }
  if(-not $db.Model.Relationships['Kundanalys direkta kostnader']){
   $r=New-Object Microsoft.AnalysisServices.Tabular.SingleColumnRelationship;$r.Name='Kundanalys direkta kostnader';$r.FromColumn=$db.Model.Tables['Direkta kostnader'].Columns['Kundnyckel'];$r.ToColumn=$db.Model.Tables['Kunder'].Columns['Kundnyckel'];$r.FromCardinality='Many';$r.ToCardinality='One';$r.CrossFilteringBehavior='OneDirection';$db.Model.Relationships.Add($r)
  }
  'Saving customer metadata.';$db.Model.SaveChanges()|Out-Null
  if($RefreshCustomerLabels){
   foreach($name in @('Kundstatusval','Kundgrupper')){$db.Model.Tables[$name].RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Full)}
   $db.Model.SaveChanges()|Out-Null
  }
  if(-not $SkipRefresh -and -not $RefreshCustomerLabels){
  'Customer metadata saved; refreshing changed imports.'
  foreach($name in @('Kundstatusval','Kundgrupper','Kundbassteg','Kundintäktssteg','Kunder','Försäljning','Direkta kostnader','Uppdrag')){$db.Model.Tables[$name].RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Full)}
  $db.Model.SaveChanges()|Out-Null;'Imports refreshed.'
  }
 }
 $errors=@($db.Model.Tables|ForEach-Object Measures|Where-Object ErrorMessage);if($errors.Count){throw ($errors.ErrorMessage -join '; ')}
 [Reflection.Assembly]::LoadFrom((Join-Path (Split-Path -Parent $binary) 'Microsoft.PowerBI.AdomdClient.dll'))|Out-Null
 $conn=New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$port;Initial Catalog=$($db.ID)");$conn.Open()
 try{
  $cmd=$conn.CreateCommand();$cmd.CommandTimeout=120;$cmd.CommandText=Get-Content -LiteralPath (Join-Path $base 'validation/customer-live-check.dax') -Raw -Encoding utf8
  $reader=$cmd.ExecuteReader();$sets=@()
  do{$rows=@();while($reader.Read()){$row=[ordered]@{};for($i=0;$i -lt $reader.FieldCount;$i++){$row[$reader.GetName($i)]=if($reader.IsDBNull($i)){$null}else{$reader.GetValue($i)}};$rows+=$row};$sets+=,@($rows)}while($reader.NextResult())
  $reader.Close();$result=@{status='queried';source='Actual refreshed Desktop model';resultSets=$sets}
  $result|ConvertTo-Json -Depth 10|Set-Content -LiteralPath (Join-Path $base 'validation/customer-live-result.json') -Encoding utf8
  @{status='queried';results=$sets[0];resultSets=$sets.Count}|ConvertTo-Json -Depth 5
 }finally{$conn.Close()}
}finally{$server.Disconnect()}
