$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$modelName=if($env:PBI_BUDGET_MODEL){$env:PBI_BUDGET_MODEL}else{'Ledningsrapport.SemanticModel'}
foreach($name in @('Microsoft.AnalysisServices.Core.dll','Microsoft.AnalysisServices.Tabular.Json.dll','Microsoft.AnalysisServices.Tabular.dll')){[Reflection.Assembly]::LoadFrom((Join-Path $root ".tools/tom/lib/net45/$name"))|Out-Null}
try{$db=[Microsoft.AnalysisServices.Tabular.TmdlSerializer]::DeserializeDatabaseFromFolder((Join-Path $root "powerbi-ledningsrapport/$modelName/definition"))}catch{Write-Output $_.Exception.InnerException.ToString();throw}
$automaticDateTables=@($db.Model.Tables|Where-Object {$_.Name -match '^(LocalDateTable_|DateTableTemplate_)'}).Count
$expectedBusinessTables=if($db.Model.Tables['Planbokningar']){44}elseif($db.Model.Tables['Budgetrapportnoder']){33}else{32}
if($db.Model.Tables['Tidsanvändning']){$expectedBusinessTables++}
$expectedTables=$expectedBusinessTables+$automaticDateTables
if($db.Model.Tables.Count -ne $expectedTables){throw 'Unexpected model table count.'}
$expectedStatementMeasures=if($db.Model.Tables['Budgetrapportnoder'].Measures['Rapportavvikelse']){4}else{3}
if($db.Model.Tables['Budgetrapportnoder'] -and $db.Model.Tables['Budgetrapportnoder'].Measures.Count -ne $expectedStatementMeasures){throw 'Unexpected statement measure count.'}
$automaticDateRelationships=@($db.Model.Relationships|Where-Object {$_.ToTable.Name -like 'LocalDateTable_*'}).Count
$expectedBusinessRelationships=if($db.Model.Tables['Planbokningar']){24}else{16}
if($db.Model.Tables['Tidsanvändning']){$expectedBusinessRelationships++}
$expectedRelationships=$expectedBusinessRelationships+$automaticDateRelationships
if($db.Model.Relationships.Count -ne $expectedRelationships){throw 'Expected existing 18 + 3 budget relationships.'}
if($db.Model.Tables['Försäljning'].Measures.Count -ne 192){throw 'Existing measures unexpectedly changed.'}
if($db.Model.Tables['Budgetscenarier'].Measures.Count -ne 46){throw 'Budget measures missing.'}
foreach($name in @('Budgetscenarion','Budgetkolumner')){
 if($db.Model.Tables[$name].Partitions[0].Source -isnot [Microsoft.AnalysisServices.Tabular.MPartitionSource]){throw "Preserve the original M partition type for $name; PBIP cache migration is unsupported."}
 foreach($column in $db.Model.Tables[$name].Columns){if($column.SourceColumn -ne $column.Name){throw "Unexpected source column mapping in $name."}}
}
foreach($table in $db.Model.Tables){
 foreach($measure in $table.Measures){
  if($null -ne $measure.FormatStringDefinition -and -not [string]::IsNullOrEmpty($measure.FormatString)){
   throw "Both static and dynamic format defined: $($table.Name)[$($measure.Name)]"
  }
 }
}
@{status='passed';tables=$db.Model.Tables.Count;relationships=$db.Model.Relationships.Count;existingMeasures=$db.Model.Tables['Försäljning'].Measures.Count;budgetMeasures=$db.Model.Tables['Budgetscenarier'].Measures.Count;engine='Microsoft TOM TMDL parser; not live DAX'}|ConvertTo-Json|Tee-Object -FilePath (Join-Path $root 'powerbi-ledningsrapport/validation/budget-tmdl-check.json')
