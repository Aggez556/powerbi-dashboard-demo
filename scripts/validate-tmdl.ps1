$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$libraryRoot = Join-Path $projectRoot '.tools/tom/lib/net45'
foreach ($library in @('Microsoft.AnalysisServices.Core.dll', 'Microsoft.AnalysisServices.Tabular.Json.dll', 'Microsoft.AnalysisServices.Tabular.dll')) {
    [Reflection.Assembly]::LoadFrom((Join-Path $libraryRoot $library)) | Out-Null
}
$modelPath = Join-Path $projectRoot 'powerbi/AubecoHandel.SemanticModel/definition'
$database = [Microsoft.AnalysisServices.Tabular.TmdlSerializer]::DeserializeDatabaseFromFolder($modelPath)
$model = $database.Model
foreach ($tableName in @('Försäljning', 'Datum', 'Kunder', 'Produkter')) {
    if (-not $model.Tables[$tableName]) { throw "Missing core table: $tableName" }
}
$budgetTables = @('Resultatrader','Budgetscenario','Budgetversion','Budgetjustering','Budgetbelopp','Budgetfördelning','Budgetkommentarer')
$expectedTableCount = if ($model.Tables['Resultatrader']) { 11 } else { 4 }
if ($model.Tables.Count -ne $expectedTableCount) { throw "Expected $expectedTableCount tables." }
if ($expectedTableCount -eq 11) {
    foreach ($tableName in $budgetTables) { if (-not $model.Tables[$tableName]) { throw "Missing budget table: $tableName" } }
}
if ($model.Relationships.Count -ne 3) { throw 'Expected three relationships.' }
if ($model.Expressions.Count -ne 1 -or -not $model.Expressions['DataFolder']) { throw 'Expected a DataFolder parameter.' }
$partitions = @($model.Tables | ForEach-Object { $_.Partitions } | ForEach-Object { @{ name = $_.Name; mode = $_.Mode.ToString(); sourceType = $_.SourceType.ToString() } })
if (@($partitions | Where-Object { $_.mode -ne 'Import' }).Count -gt 0) { throw 'All partitions must use Import mode.' }
foreach ($relationship in $model.Relationships) {
    if ($relationship.FromCardinality.ToString() -ne 'Many' -or $relationship.ToCardinality.ToString() -ne 'One' -or $relationship.CrossFilteringBehavior.ToString() -ne 'OneDirection') { throw 'Unexpected relationship configuration.' }
}
if ($model.Tables['Datum'].DataCategory -ne 'Time' -or -not $model.Tables['Datum'].Columns['Datum'].IsKey) { throw 'Date table must be marked with a date key.' }
$result = @{
    status = 'passed'; validation = 'Microsoft TOM TMDL deserialization and structural checks'
    libraryVersion = [Microsoft.AnalysisServices.Tabular.TmdlSerializer].Assembly.GetName().Version.ToString()
    tables = @($model.Tables | ForEach-Object { @{ name = $_.Name; columns = $_.Columns.Count; measures = $_.Measures.Count } })
    modelMetadata = @($model.Tables | ForEach-Object { @{ name = $_.Name; columns = @($_.Columns | ForEach-Object { @{ name = $_.Name; hidden = $_.IsHidden; sourceColumn = $_.SourceColumn; dataType = $_.DataType.ToString() } }); measures = @($_.Measures | ForEach-Object { @{ name = $_.Name; expression = $_.Expression; formatString = $_.FormatString } }) } })
    dataFolder = $model.Expressions['DataFolder'].Expression
    relationships = @($model.Relationships | ForEach-Object { @{ name = $_.Name; fromTable = $_.FromTable.Name; toTable = $_.ToTable.Name; fromCardinality = $_.FromCardinality.ToString(); toCardinality = $_.ToCardinality.ToString(); crossFiltering = $_.CrossFilteringBehavior.ToString() } })
    partitions = $partitions
    dateTableMarked = $true
    limitations = @('No Power Query execution, data processing, DAX compilation or query evaluation.', 'No Power BI Desktop import or screenshot verification.')
}
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $projectRoot 'powerbi/validation/tmdl-result.json') -Encoding UTF8
$result | ConvertTo-Json -Depth 8
