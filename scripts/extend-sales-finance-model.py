"""Add the finance and sales-analysis measures without changing existing sales."""
from pathlib import Path
import csv, hashlib, json, re
root=Path(__file__).resolve().parents[1]/'powerbi-sales-finance'
definition=root/'AubecoSalesFinance.SemanticModel/definition'
data=root/'data'
rows=[{'Type':'Säljteam','Name':n} for n in ['Nord','Väst','Syd']]+[{'Type':'Kategori','Name':n} for n in ['Kontor','Hem och kök','Elektronik','Sport och fritid','Trädgård']]
with (data/'Finansaxel.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['Type','Name']);w.writeheader();w.writerows(rows)
(definition/'tables/Finansaxel.tmdl').write_text('''table Finansaxel

	column Typ
		dataType: string
		sourceColumn: Type
		summarizeBy: none

	column Namn
		dataType: string
		sourceColumn: Name
		summarizeBy: none

	partition Finansaxel = m
		mode: import
		source =
			let
				Source = Csv.Document(File.Contents(DataFolder & "/Finansaxel.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
				Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
				Typed = Table.TransformColumnTypes(Headers, {{"Type", type text}, {"Name", type text}}, "en-US")
			in
				Typed
''',encoding='utf-8')
model=definition/'model.tmdl';s=model.read_text(encoding='utf-8')
if 'ref table Finansaxel' not in s:model.write_text(s+'\nref table Finansaxel\n',encoding='utf-8')
money='#,##0.0" kr"';millions='0.0" mn kr"';percent='+0.0 %;-0.0 %;0.0 %'
measures={}
def add(name,expr,fmt,folder):measures[name]=(expr,fmt,folder)
finance='Ekonomi och lönsamhet';sales='Försäljningsanalys'
add('Kostnad miljoner','[Kostnad] / 1000000',millions,finance)
add('Omsättning per enhet','DIVIDE([Omsättning], [Sålda enheter])',money,finance)
add('Bruttovinst per enhet','DIVIDE([Bruttovinst], [Sålda enheter])',money,finance)
add('Aktiva säljare',"DISTINCTCOUNT('Försäljning'[Säljarnyckel])",'#,##0',sales)
add('Omsättning per säljare','DIVIDE([Omsättning], [Aktiva säljare])','#,##0" kr"',sales)
add('Omsättning per säljare miljoner','[Omsättning per säljare] / 1000000',millions,sales)
add('Genomsnittlig order','DIVIDE([Omsättning], [Antal order])','#,##0" kr"',sales)
add('Topp 5 säljare andel',"""VAR SellerRevenue = ADDCOLUMNS(ALLSELECTED('Säljare'[Säljarnyckel]), "@Revenue", CALCULATE([Omsättning]))
VAR BestSellers = TOPN(5, SellerRevenue, [@Revenue], DESC, 'Säljare'[Säljarnyckel], ASC)
RETURN DIVIDE(SUMX(BestSellers, [@Revenue]), [Omsättning])""",'0.0 %',sales)
for base in ['Kostnad','Omsättning per enhet','Bruttovinst per enhet','Aktiva säljare','Omsättning per säljare','Genomsnittlig order','Topp 5 säljare andel']:
    folder=finance if base in ['Kostnad','Omsättning per enhet','Bruttovinst per enhet'] else sales
    fmt='0.0 %' if base=='Topp 5 säljare andel' else '#,##0" kr"' if base!='Aktiva säljare' else '#,##0'
    add(base+' föregående år',f"CALCULATE([{base}], SAMEPERIODLASTYEAR('Datum'[Datum]))",fmt,folder)
    if base=='Topp 5 säljare andel':
        add('Topp 5 andel förändring',f'IF(ISBLANK([{base} föregående år]), BLANK(), ([{base}] - [{base} föregående år]) * 100)','+0.0" pp";-0.0" pp";0.0" pp"',folder)
    else:add(base+' årsförändring',f'DIVIDE([{base}] - [{base} föregående år], [{base} föregående år])',percent,folder)
add('Bruttovinst analys',"""VAR AxisName = SELECTEDVALUE('Finansaxel'[Namn])
RETURN IF(SELECTEDVALUE('Finansaxel'[Typ], "Säljteam") = "Kategori", CALCULATE([Bruttovinst], TREATAS({AxisName}, 'Produkter'[Kategori])), CALCULATE([Bruttovinst], TREATAS({AxisName}, 'Säljare'[Team])))""",'#,##0" kr"',finance)
add('Bruttovinst analys miljoner','[Bruttovinst analys] / 1000000',millions,finance)
add('Månadsmedel bruttovinst',"AVERAGEX(ALLSELECTED('Datum'[Månad]), [Bruttovinst analys miljoner])",millions,finance)
add('Bruttovinst andel land',"DIVIDE([Bruttovinst], CALCULATE([Bruttovinst], ALLSELECTED('Kunder'[Land])))",'0.0 %',finance)
add('Omsättning andel land',"DIVIDE([Omsättning], CALCULATE([Omsättning], ALLSELECTED('Kunder'[Land])))",'0.0 %',sales)
path=definition/'tables/Försäljning.tmdl';s=path.read_text(encoding='utf-8')
for name in measures:
    s=re.sub(r"\n\tmeasure '"+re.escape(name)+r"' =.*?(?=\n\tmeasure |\n\tcolumn |\n\tpartition |\Z)",'',s,flags=re.S)
block=''
for name,(expr,fmt,folder) in measures.items():
    block+=f"\n\tmeasure '{name}' =\n"+'\n'.join('\t\t\t'+line for line in expr.splitlines())+f'\n\t\tformatString: {fmt}\n\t\tdisplayFolder: {folder}\n'
s=s.replace('\n\tcolumn ',block+'\n\tcolumn ',1);path.write_text(s,encoding='utf-8')
manifest=json.loads((data/'manifest.json').read_text(encoding='utf-8-sig'))
manifest['rows']['Finansaxel']=8;manifest['sha256']['Finansaxel']=hashlib.sha256((data/'Finansaxel.csv').read_bytes()).hexdigest()
manifest['extensions']=['scripts/extend-sales-finance-model.py']
(data/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Added finance selector and {len(measures)} measures; sales data unchanged.')
