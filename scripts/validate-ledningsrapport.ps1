$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
foreach ($library in @('Microsoft.AnalysisServices.Core.dll','Microsoft.AnalysisServices.Tabular.Json.dll','Microsoft.AnalysisServices.Tabular.dll')) {
    [Reflection.Assembly]::LoadFrom((Join-Path $taskRoot ".tools/tom/lib/net45/$library")) | Out-Null
}
try {
    $database = [Microsoft.AnalysisServices.Tabular.TmdlSerializer]::DeserializeDatabaseFromFolder((Join-Path $taskRoot 'powerbi-ledningsrapport/Ledningsrapport.SemanticModel/definition'))
} catch {
    Write-Output $_.Exception.InnerException.ToString()
    throw
}
if ($database.Model.Tables.Count -ne 27) { throw 'Expected 27 tables, including six existing automatic date tables.' }
if ($database.Model.Relationships.Count -ne 18) { throw 'Expected 18 relationships.' }
if ($database.Model.Tables['Försäljning'].Measures.Count -ne 191) { throw 'Expected 191 measures.' }
$result = @{status='passed';source='Microsoft TOM TMDL deserialization (not DAX execution)';tables=$database.Model.Tables.Count;relationships=$database.Model.Relationships.Count;measures=$database.Model.Tables['Försäljning'].Measures.Count}
$result | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskRoot 'powerbi-ledningsrapport/validation/tmdl-check.json') -Encoding utf8
$result | ConvertTo-Json
