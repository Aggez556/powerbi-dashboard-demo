"""Reproducible independent data/model for the new Sales & Finance project."""
from pathlib import Path
import csv,json,hashlib,random
root=Path(__file__).resolve().parents[1]
project=root/'powerbi-sales-finance'
source=(root/'scripts/generate-sales-project.py').read_text(encoding='utf-8')
source=source.replace("ROOT / 'powerbi/data'","ROOT / 'powerbi-sales-finance/data'").replace("powerbi/AubecoHandel.SemanticModel","powerbi-sales-finance/AubecoSalesFinance.SemanticModel").replace('AubecoHandel','AubecoSalesFinance').replace('SEED = 20261006','SEED = 20261007')
exec(compile(source,'sales-finance-base-generator','exec'),{'__file__':str(root/'scripts/generate-sales-project.py'),'__name__':'__main__'})
data=project/'data';definition=project/'AubecoSalesFinance.SemanticModel/definition'
def load(name):
    with (data/f'{name}.csv').open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def save_csv(name,rows):
    with (data/f'{name}.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
customers=load('DimCustomer')
for c in customers:c['Country']=['Sverige','Norge','Danmark','Finland'][(int(c['CustomerKey'])-1)%4]
save_csv('DimCustomer',customers)
names=['Alva Lind','Elias Berg','Maja Holm','Noah Ek','Ella Lund','William Dahl','Alice Sjö','Hugo Vik','Olivia Sand','Liam West','Astrid Nord','Lucas Strand','Vera Björk','Oscar Gran','Selma Wall','Leo Palm','Freja Alm','Adam Ros','Signe Falk','Nils Hed','Clara Ås','Arvid Bro','Ebba Dal','Erik Löv']
sellers=[{'SellerKey':i+1,'Seller':name,'Team':['Nord','Väst','Syd'][i//8]} for i,name in enumerate(names)]
save_csv('DimSeller',sellers)
rng=random.Random(20261007);order_seller={}
facts=load('FactSales')
for row in facts:
    order=int(row['OrderKey'])
    if order not in order_seller:order_seller[order]=rng.choices(range(1,25),weights=[1+(i%8)*.16 for i in range(24)])[0]
    row['SellerKey']=order_seller[order]
save_csv('FactSales',facts)
def add_column(table,name,source,type='string',hidden=False):
    p=definition/'tables'/f'{table}.tmdl';s=p.read_text(encoding='utf-8')
    col=f"\n\tcolumn '{name}'\n\t\tdataType: {type}\n\t\tsourceColumn: {source}\n\t\tsummarizeBy: none\n"+('\t\tisHidden\n' if hidden else '')
    s=s.replace('\n\tpartition ',col+'\n\tpartition ',1)
    # CSV's new field must be cast alongside existing source types.
    typ='Int64.Type' if type=='int64' else 'type text'
    s=s.replace('Typed = Table.TransformColumnTypes(Headers, {','Typed = Table.TransformColumnTypes(Headers, {{"'+source+'", '+typ+'}, ',1)
    p.write_text(s,encoding='utf-8')
add_column('Kunder','Land','Country')
add_column('Försäljning','Säljarnyckel','SellerKey','int64',True)
def table(name,file,cols,rows):
    save_csv(file,rows)
    text=f'table {name}\n'
    for label,src,typ in cols:
        text+=f"\n\tcolumn '{label}'\n\t\tdataType: {typ}\n\t\tsourceColumn: {src}\n\t\tsummarizeBy: none\n"
        if label=='Säljarnyckel':text+='\t\tisHidden\n\t\tisKey\n'
    casts=', '.join('{"'+src+'", '+('Int64.Type' if typ=='int64' else 'type text')+'}' for label,src,typ in cols)
    text+=f'\n\tpartition {name} = m\n\t\tmode: import\n\t\tsource =\n\t\t\tlet\n\t\t\t\tSource = Csv.Document(File.Contents(DataFolder & "/{file}.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n\t\t\t\tHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n\t\t\t\tTyped = Table.TransformColumnTypes(Headers, {{{casts}}}, "en-US")\n\t\t\tin\n\t\t\t\tTyped\n'
    (definition/'tables'/f'{name}.tmdl').write_text(text,encoding='utf-8')
    p=definition/'model.tmdl';p.write_text(p.read_text(encoding='utf-8')+'\nref table '+name+'\n',encoding='utf-8')
table('Säljare','DimSeller',[('Säljarnyckel','SellerKey','int64'),('Säljare','Seller','string'),('Team','Team','string')],sellers)
table('Trendval','Trendval',[('Mått','Metric','string')],[{'Metric':'Omsättning'},{'Metric':'Bruttovinst'}])
table('Produktval','Produktval',[('Mått','Metric','string')],[{'Metric':'Omsättning'},{'Metric':'Sålda enheter'}])
axis=[{'Type':'Land','Name':x} for x in ['Sverige','Norge','Danmark','Finland']]+[{'Type':'Kategori','Name':x} for x in ['Kontor','Hem och kök','Elektronik','Sport och fritid','Trädgård']]
table('Analysaxel','Analysaxel',[('Typ','Type','string'),('Namn','Name','string')],axis)
p=definition/'relationships.tmdl';p.write_text(p.read_text(encoding='utf-8')+"\nrelationship SalesToSeller\n\tfromColumn: Försäljning.'Säljarnyckel'\n\ttoColumn: Säljare.'Säljarnyckel'\n\tfromCardinality: many\n\ttoCardinality: one\n\tcrossFilteringBehavior: oneDirection\n",encoding='utf-8')
measures={
 'Omsättning miljoner':('[Omsättning] / 1000000','0.0" mn kr"'),
 'Bruttovinst miljoner':('[Bruttovinst] / 1000000','0.0" mn kr"'),
 'Sålda enheter':("SUM('Försäljning'[Antal enheter])",'#,##0'),
 'Leveranser':('[Antal order]','#,##0'),
 'Enheter föregående år':("CALCULATE([Sålda enheter], SAMEPERIODLASTYEAR('Datum'[Datum]))",'#,##0'),
 'Bruttovinst föregående år':("CALCULATE([Bruttovinst], SAMEPERIODLASTYEAR('Datum'[Datum]))",'#,##0'),
 'Leveranser föregående år':("CALCULATE([Leveranser], SAMEPERIODLASTYEAR('Datum'[Datum]))",'#,##0'),
 'Enheter YoY':('DIVIDE([Sålda enheter] - [Enheter föregående år], [Enheter föregående år])','+0.0 %;-0.0 %;0.0 %'),
 'Bruttovinst YoY':('DIVIDE([Bruttovinst] - [Bruttovinst föregående år], [Bruttovinst föregående år])','+0.0 %;-0.0 %;0.0 %'),
 'Leveranser YoY':('DIVIDE([Leveranser] - [Leveranser föregående år], [Leveranser föregående år])','+0.0 %;-0.0 %;0.0 %'),
 'Marginal föregående år':("CALCULATE([Bruttomarginal], SAMEPERIODLASTYEAR('Datum'[Datum]))",'0.0 %'),
 'Marginal förändring':('IF(ISBLANK([Marginal föregående år]), BLANK(), ([Bruttomarginal] - [Marginal föregående år]) * 100)','+0.0" pp";-0.0" pp";0.0" pp"'),
 'Trendvärde':("IF(SELECTEDVALUE('Trendval'[Mått], \"Omsättning\") = \"Bruttovinst\", [Bruttovinst], [Omsättning])",'#,##0" kr"'),
 'Trend föregående år':("CALCULATE([Trendvärde], SAMEPERIODLASTYEAR('Datum'[Datum]))",'#,##0" kr"'),
 'Produktvärde':("IF(SELECTEDVALUE('Produktval'[Mått], \"Omsättning\") = \"Sålda enheter\", [Sålda enheter], [Omsättning])",'#,##0'),
 'Analysvärde':("VAR AxisName = SELECTEDVALUE('Analysaxel'[Namn])\nRETURN IF(SELECTEDVALUE('Analysaxel'[Typ], \"Land\") = \"Land\", CALCULATE([Omsättning], TREATAS({AxisName}, 'Kunder'[Land])), CALCULATE([Omsättning], TREATAS({AxisName}, 'Produkter'[Kategori])))",'#,##0" kr"'),
 'Analys föregående år':("CALCULATE([Analysvärde], SAMEPERIODLASTYEAR('Datum'[Datum]))",'#,##0" kr"'),
}
text=''
for name,(expr,fmt) in measures.items():text+=f"\n\tmeasure '{name}' =\n"+'\n'.join('\t\t\t'+line for line in expr.splitlines())+f'\n\t\tformatString: {fmt}\n\t\tdisplayFolder: Ledningsöversikt\n'
p=definition/'tables/Försäljning.tmdl';s=p.read_text(encoding='utf-8');s=s.replace('\n\tcolumn ',text+'\n\tcolumn ',1);p.write_text(s,encoding='utf-8')
import runpy
runpy.run_path(str(root/'scripts/rename-sales-finance-products.py'), run_name='__main__')
manifest={'seed':20261007,'generator':'scripts/generate-sales-finance.py','rows':{},'sha256':{},'assumptions':['All data is fictional.','One order is treated as one shipment.','Currency SEK, excluding VAT.','Full calendar years 2024–2025; default comparison year 2025.']}
for p in data.glob('*.csv'):
    with p.open(encoding='utf-8-sig',newline='') as f:manifest['rows'][p.stem]=sum(1 for _ in csv.DictReader(f))
    manifest['sha256'][p.stem]=hashlib.sha256(p.read_bytes()).hexdigest()
(data/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Independent Sales & Finance model: 8 tables, 4 one-direction relationships, 24 sellers and 10,000 sales lines.')
import runpy
runpy.run_path(str(root/'scripts/extend-sales-finance-model.py'), run_name='__main__')
runpy.run_path(str(root/'scripts/extend-overview-model.py'), run_name='__main__')
runpy.run_path(str(root/'scripts/extend-finance-model.py'), run_name='__main__')
runpy.run_path(str(root/'scripts/extend-sales-analysis-model.py'), run_name='__main__')
runpy.run_path(str(root/'scripts/add-sales-finance-refresh.py'), run_name='__main__')
runpy.run_path(str(root/'scripts/extend-sales-finance-2026.py'), run_name='__main__')
