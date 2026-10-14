$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$modelName=if($env:PBI_BUDGET_MODEL){$env:PBI_BUDGET_MODEL}else{'Ledningsrapport.SemanticModel'}
foreach($name in @('Microsoft.AnalysisServices.Core.dll','Microsoft.AnalysisServices.Tabular.Json.dll','Microsoft.AnalysisServices.Tabular.dll')){[Reflection.Assembly]::LoadFrom((Join-Path $root ".tools/tom/lib/net45/$name"))|Out-Null}
try{$db=[Microsoft.AnalysisServices.Tabular.TmdlSerializer]::DeserializeDatabaseFromFolder((Join-Path $root "powerbi-ledningsrapport/$modelName/definition"))}catch{Write-Output $_.Exception.InnerException.ToString();throw}
$expectedTables=if($db.Model.Tables['Planbokningar']){50}elseif($db.Model.Tables['Budgetrapportnoder']){39}else{38}
if($db.Model.Tables.Count -ne $expectedTables){throw 'Unexpected model table count.'}
if($db.Model.Tables['Budgetrapportnoder'] -and $db.Model.Tables['Budgetrapportnoder'].Measures.Count -ne 3){throw 'Expected 3 statement measures.'}
$expectedRelationships=if($db.Model.Tables['Planbokningar']){29}else{21}
if($db.Model.Relationships.Count -ne $expectedRelationships){throw 'Expected existing 18 + 3 budget relationships.'}
if($db.Model.Tables['Försäljning'].Measures.Count -ne 191){throw 'Existing measures unexpectedly changed.'}
if($db.Model.Tables['Budgetscenarier'].Measures.Count -ne 44){throw 'Budget measures missing.'}
foreach($table in $db.Model.Tables){
 foreach($measure in $table.Measures){
  if($null -ne $measure.FormatStringDefinition -and -not [string]::IsNullOrEmpty($measure.FormatString)){
   throw "Both static and dynamic format defined: $($table.Name)[$($measure.Name)]"
  }
 }
}
@{status='passed';tables=$db.Model.Tables.Count;relationships=$db.Model.Relationships.Count;existingMeasures=191;budgetMeasures=44;engine='Microsoft TOM TMDL parser; not live DAX'}|ConvertTo-Json|Tee-Object -FilePath (Join-Path $root 'powerbi-ledningsrapport/validation/budget-tmdl-check.json')
