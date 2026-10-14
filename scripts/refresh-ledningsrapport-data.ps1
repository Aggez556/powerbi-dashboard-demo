$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$base = Join-Path $taskRoot 'powerbi-ledningsrapport'
foreach ($library in @('Microsoft.AnalysisServices.Core.dll','Microsoft.AnalysisServices.Tabular.Json.dll','Microsoft.AnalysisServices.Tabular.dll')) {
    [Reflection.Assembly]::LoadFrom((Join-Path $taskRoot ".tools/tom/lib/net45/$library")) | Out-Null
}
$manifest=Get-Content -LiteralPath (Join-Path $base 'data/manifest.json') -Raw -Encoding utf8 | ConvertFrom-Json
$expected=Get-Content -LiteralPath (Join-Path $base 'validation/data-checks.json') -Raw -Encoding utf8 | ConvertFrom-Json
$count=0
foreach ($engine in @(Get-CimInstance Win32_Process -Filter "name='msmdsrv.exe'")) {
    $folder=[regex]::Match($engine.CommandLine,'-s "([^"]+)"').Groups[1].Value
    $port=(Get-Content -LiteralPath (Join-Path $folder 'msmdsrv.port.txt') -Encoding Unicode -Raw).Trim([char]0,[char]13,[char]10)
    $server=New-Object Microsoft.AnalysisServices.Tabular.Server
    $server.Connect("localhost:$port")
    try {
        $db=$server.Databases | Select-Object -First 1
        if (-not $db.Model.Expressions['DataFolder'] -or $db.Model.Expressions['DataFolder'].Expression -notlike '*powerbi-ledningsrapport/data*') { continue }
        $count++
        foreach ($name in $manifest.rows.PSObject.Properties.Name) {
            if (-not $db.Model.Tables[$name]) { throw "Missing table $name" }
            $db.Model.Tables[$name].RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Full)
        }
        $db.Model.SaveChanges() | Out-Null
        $errors=@($db.Model.Tables | ForEach-Object Measures | Where-Object ErrorMessage)
        if ($errors.Count) { throw ($errors.ErrorMessage -join '; ') }
        $binary=[regex]::Match($engine.CommandLine,'^"([^"]+)"').Groups[1].Value
        [Reflection.Assembly]::LoadFrom((Join-Path (Split-Path -Parent $binary) 'Microsoft.PowerBI.AdomdClient.dll')) | Out-Null
        $connection=New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$port;Initial Catalog=$($db.ID)")
        $connection.Open()
        try {
            $results=@()
            foreach ($case in $expected.scenarios) {
                $mode=$case.mode
                $period=if($mode -eq 'Helår'){$case.end.Substring(0,4)}else{'Oktober 2026'}
                $selector=if($mode -eq 'Helår'){'Helårsval'}elseif($mode -eq 'Månad'){'Månadsval'}else{'R12val'}
                $query=@'
EVALUATE CALCULATETABLE(ROW("Start",[Periodstart],"Slut",[Periodslut],"Omsättning",[Nettoomsättning],"Bruttovinst",[Bruttovinst],"Resultat",[Rörelseresultat],"Budget",[Budgetresultat],"Uppdrag",[Utförda uppdrag],"Kunder",[Aktiva kunder],"Bryggfel",[Bryggkontroll]), TREATAS({"MODE"},'Periodtyp'[Periodtyp]), TREATAS({"PERIOD"},'SELECTOR'[Period]))
'@
                $command=$connection.CreateCommand();$command.CommandTimeout=60
                $command.CommandText=$query.Replace('MODE',$mode).Replace('PERIOD',$period).Replace('SELECTOR',$selector)
                $reader=$command.ExecuteReader()
                if(-not $reader.Read()){throw 'DAX returned no row'}
                $row=[ordered]@{mode=$mode;period=$period}
                for($i=0;$i -lt $reader.FieldCount;$i++){$row[$reader.GetName($i)]=$reader.GetValue($i)}
                if([decimal]$reader.GetValue(2) -ne [decimal]$case.actual.revenue -or [decimal]$reader.GetValue(4) -ne [decimal]$case.actual.operatingProfit -or [decimal]$reader.GetValue(8) -ne 0){throw 'Live DAX does not match independent CSV calculation'}
                $reader.Close();$results+=$row
            }
            $out=@{status='passed';source='Refreshed live Desktop model; DAX compared with independent CSV calculations';lastMonth='2026-10';desktopProcessId=$engine.ParentProcessId;scenarios=$results}
            $out | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $base 'validation/october-live-data.json') -Encoding utf8
            $out | ConvertTo-Json -Depth 6
        } finally {$connection.Close()}
    } finally {$server.Disconnect()}
}
if($count -eq 0){throw 'No matching open Ledningsrapport model.'}
