"""Deterministic CSV test data and an Import TMDL star schema. Python stdlib only."""
from pathlib import Path
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
import csv
import hashlib
import json
import random

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'powerbi/data'
MODEL = ROOT / 'powerbi/AubecoHandel.SemanticModel'
SEED = 20261006
rng = random.Random(SEED)
def money(value):
    return Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
def write_csv(name, rows):
    DATA.mkdir(parents=True, exist_ok=True)
    with (DATA / (name + '.csv')).open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)
    return hashlib.sha256((DATA / (name + '.csv')).read_bytes()).hexdigest()

months = ['januari','februari','mars','april','maj','juni','juli','augusti','september','oktober','november','december']
dates = [date(2024,1,1)+timedelta(days=i) for i in range(731)]
dim_date = [{'DateKey':int(d.strftime('%Y%m%d')), 'Date':d.isoformat(), 'Year':d.year,
             'MonthNumber':d.month, 'Month':months[d.month-1], 'YearMonth':d.strftime('%Y-%m'),
             'YearMonthSort':d.year*100+d.month, 'Quarter':f'Q{(d.month-1)//3+1}'} for d in dates]
customers = [{'CustomerKey':i,'CustomerName':f'Handelskund {i:03d} AB',
              'City':['Stockholm','Göteborg','Malmö','Uppsala','Västerås'][i%5],
              'Segment':['Småföretag','Mellanstora företag','Större företag'][i%3]} for i in range(1,101)]
categories = [('Kontor',120,0.28),('Hem och kök',320,0.40),('Elektronik',1400,0.18),('Sport och fritid',550,0.35),('Trädgård',420,0.45)]
products = []
for i in range(1,31):
    category,base,margin = categories[(i-1)//6]
    price=money(base*rng.uniform(0.65,1.6))
    rate=round(max(.10,min(.60,margin+rng.uniform(-.06,.06))),4)
    products.append({'ProductKey':i,'ProductName':f'{category} – produkt {(i-1)%6+1:02d}',
                     'Category':category,'ListPrice':price,'StandardUnitCost':money(price*Decimal(str(1-rate))),
                     'StandardMargin':rate})

# 4,000 multi-line orders, exactly 10,000 lines; a customer and date per order.
order_sizes=[2]*4000
for index in rng.sample(range(4000),2000): order_sizes[index]+=1
season=[.78,.80,.95,.98,1.05,1.04,.78,.95,1.08,1.18,1.55,1.48]
weights=[season[d.month-1]*(1.16 if d.year==2025 else 1)*(.55 if d.weekday()>=5 else 1) for d in dates]
facts=[]
for order_id,size in enumerate(order_sizes,1):
    d=rng.choices(dates,weights=weights,k=1)[0]
    customer=rng.choices(range(1,101),weights=[1+(i%13)*.22 for i in range(1,101)],k=1)[0]
    available=products[:]
    for _ in range(size):
        product_weights=[2.3 if p['Category']=='Trädgård' and d.month in (4,5,6,7,8) else 1 for p in available]
        product=rng.choices(available,weights=product_weights,k=1)[0]
        available.remove(product)
        quantity=rng.randint(1,8)
        discount=rng.choice([0,0,0,.03,.05,.08,.10])
        price=money(product['ListPrice']*Decimal(str(1-discount))*(Decimal('1.03') if d.year==2025 else Decimal('1')))
        cost=money(product['StandardUnitCost']*(Decimal('1.02') if d.year==2025 else Decimal('1')))
        revenue=money(price*quantity); line_cost=money(cost*quantity)
        facts.append({'SalesLineKey':len(facts)+1,'OrderKey':order_id,'DateKey':int(d.strftime('%Y%m%d')),
                      'CustomerKey':customer,'ProductKey':product['ProductKey'],'Quantity':quantity,
                      'UnitPrice':price,'UnitCost':cost,'Revenue':revenue,'Cost':line_cost})
hashes={name:write_csv(name,rows) for name,rows in [('FactSales',facts),('DimDate',dim_date),('DimCustomer',customers),('DimProduct',products)]}
(DATA/'manifest.json').write_text(json.dumps({'seed':SEED,'generator':'scripts/generate-sales-project.py',
    'rows':{'FactSales':10000,'DimDate':731,'DimCustomer':100,'DimProduct':30},'orders':4000,
    'sha256':hashes,'encoding':'UTF-8 BOM','separator':',','decimal_separator':'.',
    'assumptions':'Exklusive moms; inga returer; orderrader inom samma order delar kund och datum.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def save(relative,text):
    target=MODEL/relative; target.parent.mkdir(parents=True,exist_ok=True); target.write_text(text,encoding='utf-8')
save('definition.pbism',json.dumps({'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json','version':'4.2','settings':{'qnaEnabled':False}},indent=2)+'\n')
save('definition/database.tmdl','database AubecoHandel\n\tcompatibilityLevel: 1600\n')
save('definition/model.tmdl',"model Model\n\tculture: sv-SE\n\tsourceQueryCulture: en-US\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n\tdiscourageImplicitMeasures\n\n\tannotation PBI_TimeIntelligenceEnabled = 0\n\nref table Försäljning\nref table Datum\nref table Kunder\nref table Produkter\n")
save('definition/expressions.tmdl',f'expression DataFolder = "{str(DATA).replace(chr(92),chr(47))}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n')
specs = {
 'Försäljning':('FactSales',[
 ('Radnyckel','SalesLineKey','int64',True),('Ordernyckel','OrderKey','int64',True),('Datumnyckel','DateKey','int64',True),
 ('Kundnyckel','CustomerKey','int64',True),('Produktnyckel','ProductKey','int64',True),('Antal enheter','Quantity','int64',True),
 ('Enhetspris','UnitPrice','decimal',True),('Enhetskostnad','UnitCost','decimal',True),('Radomsättning','Revenue','decimal',True),('Radkostnad','Cost','decimal',True)]),
 'Datum':('DimDate', [('Datumnyckel','DateKey','int64',True),('Datum','Date','dateTime',False),('År','Year','int64',False),
 ('Månadsnummer','MonthNumber','int64',True),('Månad','Month','string',False),('År–månad','YearMonth','string',False),
 ('Årsmånadsnummer','YearMonthSort','int64',True),('Kvartal','Quarter','string',False)]),
 'Kunder':('DimCustomer',[('Kundnyckel','CustomerKey','int64',True),('Kund','CustomerName','string',False),('Ort','City','string',False),('Segment','Segment','string',False)]),
 'Produkter':('DimProduct',[('Produktnyckel','ProductKey','int64',True),('Produkt','ProductName','string',False),('Kategori','Category','string',False),
 ('Listpris','ListPrice','decimal',True),('Standardkostnad','StandardUnitCost','decimal',True),('Standardmarginal','StandardMargin','decimal',True)]),
}
measures=[
 ('Omsättning','SUM(\'Försäljning\'[Radomsättning])','#,##0.00 " kr"','Nettoomsättning exklusive moms efter rabatt.'),
 ('Kostnad','SUM(\'Försäljning\'[Radkostnad])','#,##0.00 " kr"','Varukostnad; exkluderar rörelsekostnader.'),
 ('Bruttovinst','[Omsättning] - [Kostnad]','#,##0.00 " kr"','Omsättning minus varukostnad.'),
 ('Bruttomarginal','DIVIDE([Bruttovinst], [Omsättning])','0.0 %','Viktad marginal; inte medelvärdet av produktmarginalerna.'),
 ('Antal order',"DISTINCTCOUNT('Försäljning'[Ordernyckel])",'#,##0','Unika order med minst en orderrad i aktuellt filter.'),
 ('Omsättning föregående år',"CALCULATE([Omsättning], SAMEPERIODLASTYEAR('Datum'[Datum]))",'#,##0.00 " kr"','Omsättning för motsvarande kalenderdatum föregående år; 2023 saknas.'),
 ('Tillväxt mot föregående år',"IF(HASONEVALUE('Datum'[År]), DIVIDE([Omsättning] - [Omsättning föregående år], [Omsättning föregående år]), BLANK())",'0.0 %;-0.0 %;0.0 %','Visas endast vid ett valt år och tillgänglig jämförelse; annars blank.'),
 ('Antal orderrader',"COUNTROWS('Försäljning')",'#,##0','Antal orderrader i aktuellt filter.'),
 ('Kundrankning',"RANKX(ALLSELECTED('Kunder'[Kund]), [Omsättning], , DESC, DENSE)",'0','Kundrankning inom aktuellt urval; lika belopp delar rankning.'),
]
for name,(filename,columns) in specs.items():
    text=f'/// Lokal testdata från {filename}.csv.\ntable {name}\n'
    if name=='Datum': text+='\tdataCategory: Time\n'
    if name=='Försäljning':
        for label,dax,fmt,description in measures:
            text+=f"\n\t/// {description}\n\tmeasure '{label}' = {dax}\n\t\tformatString: {fmt}\n\t\tdisplayFolder: Nyckeltal\n"
    for label,source,kind,hidden in columns:
        text+=f"\n\tcolumn '{label}'\n\t\tdataType: {kind}\n\t\tsourceColumn: {source}\n\t\tsummarizeBy: none\n"
        if hidden: text+='\t\tisHidden\n'
        if label=='Datum' or (name in ('Kunder','Produkter') and label.endswith('nyckel')): text+='\t\tisKey\n'
        if label=='Datum': text+='\t\tformatString: yyyy-MM-dd\n'
        if label=='Månad': text+="\t\tsortByColumn: 'Månadsnummer'\n"
        if label=='År–månad': text+="\t\tsortByColumn: 'Årsmånadsnummer'\n"
    types={'int64':'Int64.Type','dateTime':'type date','decimal':'Currency.Type','string':'type text'}
    cast=', '.join('{"'+source+'", '+types[kind]+'}' for _,source,kind,_ in columns)
    text+=f'\n\tpartition {name} = m\n\t\tmode: import\n\t\tsource =\n\t\t\tlet\n\t\t\t\tSource = Csv.Document(File.Contents(DataFolder & "/{filename}.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n\t\t\t\tHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n\t\t\t\tTyped = Table.TransformColumnTypes(Headers, {{{cast}}}, "en-US")\n\t\t\tin\n\t\t\t\tTyped\n'
    save('definition/tables/'+name+'.tmdl',text)
relationships=''
for dimension,key in [('Datum','Datumnyckel'),('Kunder','Kundnyckel'),('Produkter','Produktnyckel')]:
    relationships+=f"relationship SalesTo{dimension}\n\tfromColumn: Försäljning.'{key}'\n\ttoColumn: {dimension}.'{key}'\n\tfromCardinality: many\n\ttoCardinality: one\n\tcrossFilteringBehavior: oneDirection\n\n"
save('definition/relationships.tmdl',relationships)
print('Generated 10000 lines / 4000 orders, 731 dates, 100 customers, 30 products, Import TMDL.')
