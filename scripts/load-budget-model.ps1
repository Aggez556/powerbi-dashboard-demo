param([switch]$QueryOnly,[string]$QueryFile='validation/budget-live-check.dax',[string]$OutputFile='validation/budget-live-result.json')
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
foreach($dll in @('Microsoft.AnalysisServices.Core.dll','Microsoft.AnalysisServices.Tabular.Json.dll','Microsoft.AnalysisServices.Tabular.dll')){[Reflection.Assembly]::LoadFrom((Join-Path $root ".tools/tom/lib/net45/$dll"))|Out-Null}
$base=Join-Path $root 'powerbi-ledningsrapport'
$modelName=if($env:PBI_BUDGET_MODEL){$env:PBI_BUDGET_MODEL}else{'Ledningsrapport.SemanticModel'}
$source=[Microsoft.AnalysisServices.Tabular.TmdlSerializer]::DeserializeDatabaseFromFolder((Join-Path $base "$modelName/definition"))
$engine=Get-CimInstance Win32_Process -Filter "name='msmdsrv.exe'"|Sort-Object CreationDate -Descending|Select-Object -First 1
if(-not $engine){throw 'Open the Ledningsrapport PBIP in Power BI Desktop first.'}
$folder=[regex]::Match($engine.CommandLine,'-s "([^"]+)"').Groups[1].Value
$binary=[regex]::Match($engine.CommandLine,'^"([^"]+)"').Groups[1].Value
$port=(Get-Content -LiteralPath (Join-Path $folder 'msmdsrv.port.txt') -Encoding Unicode -Raw).Trim([char]0,[char]13,[char]10)
$server=New-Object Microsoft.AnalysisServices.Tabular.Server
$server.Connect("Data Source=localhost:$port;Timeout=60")
try{
 $db=$server.Databases|Where-Object {$null -ne $_.Model.Tables['Planbokningar']}|Select-Object -First 1
 if(-not $db){$db=$server.Databases|Where-Object {$null -ne $_.Model.Tables['Budgetrapportnoder']}|Select-Object -First 1}
 if(-not $db){$db=$server.Databases|Where-Object {$null -ne $_.Model.Tables['Budgetscenarier']}|Select-Object -First 1}
 if(-not $db){throw 'No loaded Budget model found in this Desktop instance.'}
 if($db.Model.Expressions['DataFolder'].Expression -notlike '*powerbi-ledningsrapport/data*'){throw 'Wrong project: budget load stopped.'}
 $manifest=Get-Content (Join-Path $base 'validation/budget-model-manifest.json') -Raw -Encoding utf8|ConvertFrom-Json
 if(-not $QueryOnly){
  if($source.Model.Tables['Budgetrapportnoder']){$manifest.tables+=@('Budgetrapportnoder')}
  if(-not $db.Model.Expressions['BudgetWorkbook']){$db.Model.Expressions.Add($source.Model.Expressions['BudgetWorkbook'].Clone())}
  foreach($name in $manifest.tables){if(-not $db.Model.Tables[$name]){$db.Model.Tables.Add($source.Model.Tables[$name].Clone())}}
  foreach($relationship in $source.Model.Relationships){
   if(-not $db.Model.Relationships[$relationship.Name]){
    $r=New-Object Microsoft.AnalysisServices.Tabular.SingleColumnRelationship
    $r.Name=$relationship.Name;$r.FromColumn=$db.Model.Tables[$relationship.FromTable.Name].Columns[$relationship.FromColumn.Name];$r.ToColumn=$db.Model.Tables[$relationship.ToTable.Name].Columns[$relationship.ToColumn.Name]
    $r.FromCardinality='Many';$r.ToCardinality='One';$r.CrossFilteringBehavior='OneDirection';$db.Model.Relationships.Add($r)
   }
  }
  $db.Model.Tables['Budget'].Partitions[0].Source.Expression=$source.Model.Tables['Budget'].Partitions[0].Source.Expression
  $db.Model.SaveChanges()|Out-Null
  foreach($name in $manifest.tables){$db.Model.Tables[$name].RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Full)}
  $db.Model.Tables['Budget'].RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Full)
  $db.Model.SaveChanges()|Out-Null
 }
 $errors=@($db.Model.Tables|ForEach-Object Measures|Where-Object ErrorMessage);if($errors.Count){throw ($errors.ErrorMessage -join '; ')}
 [Reflection.Assembly]::LoadFrom((Join-Path (Split-Path -Parent $binary) 'Microsoft.PowerBI.AdomdClient.dll'))|Out-Null
 $conn=New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$port;Initial Catalog=$($db.ID)");$conn.Open()
 try{
  $cmd=$conn.CreateCommand();$cmd.CommandTimeout=120;$cmd.CommandText=Get-Content (Join-Path $base $QueryFile) -Raw -Encoding utf8
  $reader=$cmd.ExecuteReader();$sets=@()
  do{$rows=@();while($reader.Read()){$row=[ordered]@{};for($i=0;$i -lt $reader.FieldCount;$i++){$row[$reader.GetName($i)]=if($reader.IsDBNull($i)){$null}else{$reader.GetValue($i)}};$rows+=$row};$sets+=,@($rows)}while($reader.NextResult())
  $reader.Close();$result=@{status='queried';source='Actual local Power BI Desktop DAX';resultSets=$sets}
  $result|ConvertTo-Json -Depth 10|Set-Content (Join-Path $base $OutputFile) -Encoding utf8
  @{status='queried';resultSets=$sets.Count;rowCounts=@($sets|ForEach-Object {@($_).Count});first=($sets[0]|Select-Object -First 1)}|ConvertTo-Json -Depth 5
 }finally{$conn.Close()}
}finally{$server.Disconnect()}
