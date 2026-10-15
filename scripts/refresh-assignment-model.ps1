param([string[]]$Tables,[switch]$TimeOnly)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
foreach($dll in @('Microsoft.AnalysisServices.Core.dll','Microsoft.AnalysisServices.Tabular.Json.dll','Microsoft.AnalysisServices.Tabular.dll')){[Reflection.Assembly]::LoadFrom((Join-Path $taskRoot ".tools/tom/lib/net45/$dll"))|Out-Null}
$engine=Get-CimInstance Win32_Process -Filter "name='msmdsrv.exe'"|Sort-Object CreationDate -Descending|Select-Object -First 1
if(-not $engine){throw 'Open the original Ledningsrapport project first.'}
$folder=[regex]::Match($engine.CommandLine,'-s "([^"]+)"').Groups[1].Value
$port=(Get-Content -LiteralPath (Join-Path $folder 'msmdsrv.port.txt') -Encoding Unicode -Raw).Trim([char]0,[char]13,[char]10)
$server=New-Object Microsoft.AnalysisServices.Tabular.Server
$server.Connect("Data Source=localhost:$port;Timeout=60")
try{
 $db=$server.Databases|Where-Object {$null -ne $_.Model.Tables['Planbokningar']}|Select-Object -First 1
 if(-not $db){throw 'The assignment model is not loaded.'}
 if($db.Model.Expressions['DataFolder'].Expression -notlike '*powerbi-ledningsrapport/data*'){throw 'Wrong project.'}
 $manifest=Get-Content (Join-Path $taskRoot 'powerbi-ledningsrapport/validation/assignment-model-manifest.json') -Encoding utf8 -Raw|ConvertFrom-Json
 $refreshTables=if($TimeOnly){@($manifest.tables|Where-Object {$_ -eq 'Uppdragsregister' -or $_ -like 'Utf*'})}elseif($Tables){$Tables}else{$manifest.tables}
 foreach($name in $refreshTables){if($name -notin $manifest.tables){throw 'Unexpected refresh table.'};$db.Model.Tables[$name].RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Full)}
 $db.Model.SaveChanges()|Out-Null
 @{status='refreshed';tables=$refreshTables.Count;scope='Only assignment tables; no report reload or other fact-table processing'}|ConvertTo-Json
}finally{$server.Disconnect()}
