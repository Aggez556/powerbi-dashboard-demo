$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
foreach($dll in @('Microsoft.AnalysisServices.Core.dll','Microsoft.AnalysisServices.Tabular.Json.dll','Microsoft.AnalysisServices.Tabular.dll')){[Reflection.Assembly]::LoadFrom((Join-Path $taskRoot ".tools/tom/lib/net45/$dll"))|Out-Null}
$source=[Microsoft.AnalysisServices.Tabular.TmdlSerializer]::DeserializeDatabaseFromFolder((Join-Path $taskRoot 'powerbi-ledningsrapport/Ledningsrapport.SemanticModel/definition'))
$name=[string]([char]66)+'ryggans '+[char]246+'vre axelgr'+[char]228+'ns'
$sales='F'+[char]246+'rs'+[char]228+'ljning'
$engine=Get-CimInstance Win32_Process -Filter "name='msmdsrv.exe'"|Where-Object ParentProcessId -eq 31412|Select-Object -First 1
if(-not $engine){throw 'Current report Desktop engine not found; persisted edits retained.'}
$folder=[regex]::Match($engine.CommandLine,'-s "([^"]+)"').Groups[1].Value
$binary=[regex]::Match($engine.CommandLine,'^"([^"]+)"').Groups[1].Value
$port=(Get-Content -LiteralPath (Join-Path $folder 'msmdsrv.port.txt') -Encoding Unicode -Raw).Trim([char]0,[char]13,[char]10)
$server=New-Object Microsoft.AnalysisServices.Tabular.Server;$server.Connect("localhost:$port")
try{
 $db=$server.Databases|Select-Object -First 1
 if($db.Model.Expressions['DataFolder'].Expression -notlike '*powerbi-ledningsrapport/data*'){throw 'Wrong Desktop project.'}
 if($db.Model.Tables[$sales].Measures[$name]){$db.Model.Tables[$sales].Measures[$name].Expression=$source.Model.Tables[$sales].Measures[$name].Expression}else{$db.Model.Tables[$sales].Measures.Add($source.Model.Tables[$sales].Measures[$name].Clone())}
 $db.Model.SaveChanges()|Out-Null
 [Reflection.Assembly]::LoadFrom((Join-Path (Split-Path -Parent $binary) 'Microsoft.PowerBI.AdomdClient.dll'))|Out-Null
 $conn=New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$port;Initial Catalog=$($db.ID)");$conn.Open()
 try{
  $cmd=$conn.CreateCommand();$cmd.CommandTimeout=30
  $cmd.CommandText="EVALUATE CALCULATETABLE(ROW(""AxisMaximum"",[$name]),TREATAS({""R12""},'Periodtyp'[Periodtyp]),TREATAS({""September 2026""},'R12val'[Period]))"
  $r=$cmd.ExecuteReader();while($r.Read()){'Verified live DAX axis maximum: '+$r.GetValue(0)};$r.Close()
 }finally{$conn.Close()}
}finally{$server.Disconnect()}
