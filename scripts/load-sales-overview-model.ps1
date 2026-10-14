$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
$base=Join-Path $taskRoot 'powerbi-ledningsrapport'
foreach($library in @('Microsoft.AnalysisServices.Core.dll','Microsoft.AnalysisServices.Tabular.Json.dll','Microsoft.AnalysisServices.Tabular.dll')){[Reflection.Assembly]::LoadFrom((Join-Path $taskRoot ".tools/tom/lib/net45/$library"))|Out-Null}
$source=[Microsoft.AnalysisServices.Tabular.TmdlSerializer]::DeserializeDatabaseFromFolder((Join-Path $base 'Ledningsrapport.SemanticModel/definition'))
$names=Get-Content -LiteralPath (Join-Path $base 'validation/sales-measure-names.json') -Raw -Encoding utf8|ConvertFrom-Json
$found=0
foreach($engine in @(Get-CimInstance Win32_Process -Filter "name='msmdsrv.exe'")){
    $folder=[regex]::Match($engine.CommandLine,'-s "([^"]+)"').Groups[1].Value
    $port=(Get-Content -LiteralPath (Join-Path $folder 'msmdsrv.port.txt') -Encoding Unicode -Raw).Trim([char]0,[char]13,[char]10)
    $server=New-Object Microsoft.AnalysisServices.Tabular.Server;$server.Connect("localhost:$port")
    try{
        $db=$server.Databases|Select-Object -First 1
        if(-not $db.Model.Expressions['DataFolder'] -or $db.Model.Expressions['DataFolder'].Expression -notlike '*powerbi-ledningsrapport/data*'){continue}
        $found++
        'Connected to matching local model; applying sales metadata.'
        foreach($table in @('Artiklar','Försäljningsserie','Områdesval')){
            if(-not $db.Model.Tables[$table]){$db.Model.Tables.Add($source.Model.Tables[$table].Clone())}
        }
        foreach($table in @('Försäljning','Direkta kostnader','Kunder')){
            foreach($column in $source.Model.Tables[$table].Columns){
                if(-not $db.Model.Tables[$table].Columns[$column.Name]){$db.Model.Tables[$table].Columns.Add($column.Clone())}
            }
            $db.Model.Tables[$table].Partitions[0].Source.Expression=$source.Model.Tables[$table].Partitions[0].Source.Expression
        }
        foreach($name in $names){
            if($db.Model.Tables['Försäljning'].Measures[$name]){$db.Model.Tables['Försäljning'].Measures[$name].Expression=$source.Model.Tables['Försäljning'].Measures[$name].Expression}
            else{$db.Model.Tables['Försäljning'].Measures.Add($source.Model.Tables['Försäljning'].Measures[$name].Clone())}
        }
        foreach($table in @('Försäljning','Direkta kostnader')){
            $name='Sälj '+$table+' artikel'
            if(-not $db.Model.Relationships[$name]){
                $r=New-Object Microsoft.AnalysisServices.Tabular.SingleColumnRelationship
                $r.Name=$name;$r.FromColumn=$db.Model.Tables[$table].Columns['Artikelnyckel'];$r.ToColumn=$db.Model.Tables['Artiklar'].Columns['Artikelnyckel'];$r.FromCardinality='Many';$r.ToCardinality='One';$r.CrossFilteringBehavior='OneDirection';$db.Model.Relationships.Add($r)
            }
        }
        # Save metadata independently before asking Desktop to process new M partitions.
        $db.Model.SaveChanges()|Out-Null
        'Metadata saved; processing enriched tables.'
        foreach($table in @('Artiklar','Försäljningsserie','Områdesval','Försäljning','Direkta kostnader','Kunder')){$db.Model.Tables[$table].RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Full)}
        $db.Model.SaveChanges()|Out-Null
        $errors=@($db.Model.Tables|ForEach-Object Measures|Where-Object ErrorMessage);if($errors.Count){throw ($errors.ErrorMessage -join '; ')}
        $binary=[regex]::Match($engine.CommandLine,'^"([^"]+)"').Groups[1].Value
        [Reflection.Assembly]::LoadFrom((Join-Path (Split-Path -Parent $binary) 'Microsoft.PowerBI.AdomdClient.dll'))|Out-Null
        $conn=New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$port;Initial Catalog=$($db.ID)");$conn.Open()
        try{
            $cmd=$conn.CreateCommand();$cmd.CommandTimeout=120;$cmd.CommandText=Get-Content -LiteralPath (Join-Path $base 'validation/sales-live-check.dax') -Raw -Encoding utf8
            $reader=$cmd.ExecuteReader();$sets=@()
            do{$rows=@();while($reader.Read()){$row=[ordered]@{};for($i=0;$i -lt $reader.FieldCount;$i++){$row[$reader.GetName($i)]=if($reader.IsDBNull($i)){$null}else{$reader.GetValue($i)}};$rows+=$row};$sets+=,@($rows)}while($reader.NextResult())
            $reader.Close();$result=@{status='passed';source='Actual local Desktop model, refreshed enriched facts and DAX';desktopProcessId=$engine.ParentProcessId;resultSets=$sets}
            $result|ConvertTo-Json -Depth 10|Set-Content -LiteralPath (Join-Path $base 'validation/sales-live-result.json') -Encoding utf8
            @{status='passed';resultSetCount=$sets.Count;controls=$sets[0];overview=$sets[3]}|ConvertTo-Json -Depth 7
        }finally{$conn.Close()}
    }finally{$server.Disconnect()}
}
if($found -eq 0){throw 'No matching Desktop model.'}
