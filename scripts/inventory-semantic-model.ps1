$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
foreach($dll in @('Microsoft.AnalysisServices.Core.dll','Microsoft.AnalysisServices.Tabular.Json.dll','Microsoft.AnalysisServices.Tabular.dll')){[Reflection.Assembly]::LoadFrom((Join-Path $taskRoot ".tools/tom/lib/net45/$dll"))|Out-Null}
$db=[Microsoft.AnalysisServices.Tabular.TmdlSerializer]::DeserializeDatabaseFromFolder((Join-Path $taskRoot 'powerbi-ledningsrapport/Ledningsrapport.SemanticModel/definition'))
$tables=@(foreach($t in $db.Model.Tables){
 [pscustomobject]@{name=$t.Name;hidden=$t.IsHidden;columns=$t.Columns.Count;measures=$t.Measures.Count;calculatedColumns=@($t.Columns|Where-Object {$_ -is [Microsoft.AnalysisServices.Tabular.CalculatedColumn]}).Count;hierarchies=$t.Hierarchies.Count;partitionTypes=@($t.Partitions|ForEach-Object {$_.Source.GetType().Name});dynamicFormats=@($t.Measures|Where-Object {$null -ne $_.FormatStringDefinition}).Count}
})
$relationships=@(foreach($r in $db.Model.Relationships){[pscustomobject]@{name=$r.Name;active=$r.IsActive;from=$r.FromTable.Name;to=$r.ToTable.Name;filterDirection=$r.CrossFilteringBehavior.ToString()}})
$report=[pscustomobject]@{source='Persisted original PBIP semantic model, parsed with Microsoft TOM';tables=$tables.Count;columns=($tables|Measure-Object columns -Sum).Sum;measures=($tables|Measure-Object measures -Sum).Sum;calculatedColumns=($tables|Measure-Object calculatedColumns -Sum).Sum;hierarchies=($tables|Measure-Object hierarchies -Sum).Sum;dynamicFormats=($tables|Measure-Object dynamicFormats -Sum).Sum;relationships=$relationships.Count;activeRelationships=@($relationships|Where-Object active).Count;roles=$db.Model.Roles.Count;expressions=@($db.Model.Expressions|ForEach-Object {$_.Name});tableDetails=$tables;relationshipDetails=$relationships}
$report|ConvertTo-Json -Depth 7|Set-Content -Encoding utf8 (Join-Path $taskRoot 'powerbi-ledningsrapport/validation/semantic-model-inventory.json')
$report|ConvertTo-Json -Depth 7
