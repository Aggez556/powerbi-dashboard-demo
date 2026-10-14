"""Independent relational and financial checks; no DAX engine is implied."""
from pathlib import Path
from collections import Counter, defaultdict
from decimal import Decimal
from datetime import date,timedelta
import csv,json,sqlite3,hashlib

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'powerbi/data'
OUT=ROOT/'powerbi/validation'
def rows(name):
    with (DATA/f'{name}.csv').open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
tables={name:rows(name) for name in ['FactSales','DimDate','DimCustomer','DimProduct']}
assert {k:len(v) for k,v in tables.items()}=={'FactSales':10000,'DimDate':731,'DimCustomer':100,'DimProduct':30}
keys={}
for table,key in [('FactSales','SalesLineKey'),('DimDate','DateKey'),('DimCustomer','CustomerKey'),('DimProduct','ProductKey')]:
    values=[int(row[key]) for row in tables[table]]
    assert len(values)==len(set(values)) and min(values)>0
    keys[key]=set(values)
calendar=[date.fromisoformat(r['Date']) for r in tables['DimDate']]
assert calendar==[date(2024,1,1)+timedelta(days=i) for i in range(731)]
assert all(int(r['DateKey'])==int(date.fromisoformat(r['Date']).strftime('%Y%m%d')) for r in tables['DimDate'])
assert len(set(r['Category'] for r in tables['DimProduct']))==5
assert all(count==6 for count in Counter(r['Category'] for r in tables['DimProduct']).values())
assert len(set(r['StandardMargin'] for r in tables['DimProduct']))>20
orders=defaultdict(set)
for r in tables['FactSales']:
    for key in ('DateKey','CustomerKey','ProductKey'):assert int(r[key]) in keys[key]
    q=int(r['Quantity']); revenue=Decimal(r['Revenue']); cost=Decimal(r['Cost'])
    assert q>0 and revenue==q*Decimal(r['UnitPrice']) and cost==q*Decimal(r['UnitCost'])
    assert Decimal('0')<cost<revenue
    orders[r['OrderKey']].add((r['DateKey'],r['CustomerKey']))
assert len(orders)==4000 and all(len(pair)==1 for pair in orders.values())
assert set(int(r['CustomerKey']) for r in tables['FactSales'])==keys['CustomerKey']
assert set(int(r['ProductKey']) for r in tables['FactSales'])==keys['ProductKey']

# Aggregate integer cents in SQL independently of the generator and DAX.
con=sqlite3.connect(':memory:')
con.execute('create table sales(order_id integer, date_key integer, customer_key integer, product_key integer, revenue_cents integer,cost_cents integer)')
con.executemany('insert into sales values(?,?,?,?,?,?)',[(int(r['OrderKey']),int(r['DateKey']),int(r['CustomerKey']),int(r['ProductKey']),int(Decimal(r['Revenue'])*100),int(Decimal(r['Cost'])*100)) for r in tables['FactSales']])
con.execute('create table products(product_key integer, category text, product text)')
con.executemany('insert into products values(?,?,?)',[(int(r['ProductKey']),r['Category'],r['ProductName']) for r in tables['DimProduct']])
con.execute('create view joined as select s.*,p.category,p.product,cast(s.date_key/10000 as integer) as year,cast(s.date_key/100 as integer) as yearmonth from sales s join products p using(product_key)')
def totals(where='',params=()):
    revenue,cost,order_count,line_count=con.execute('select sum(revenue_cents),sum(cost_cents),count(distinct order_id),count(*) from joined '+where,params).fetchone()
    if revenue is None:return None
    return {'Omsättning':revenue/100,'Kostnad':cost/100,'Bruttovinst':(revenue-cost)/100,'Bruttomarginal':float(Decimal(revenue-cost)/Decimal(revenue)), 'Antal order':order_count,'Antal orderrader':line_count}
annual={str(year):totals('where year=?',(year,)) for year in (2024,2025)}
annual['2024']['Omsättning föregående år']=None;annual['2024']['Tillväxt mot föregående år']=None
annual['2025']['Omsättning föregående år']=annual['2024']['Omsättning']
annual['2025']['Tillväxt mot föregående år']=annual['2025']['Omsättning']/annual['2024']['Omsättning']-1
year_category=[]
for category in sorted(set(r['Category'] for r in tables['DimProduct'])):
    py=totals('where year=2024 and category=?',(category,))
    current=totals('where year=2025 and category=?',(category,))
    current.update({'År':2025,'Kategori':category,'Omsättning föregående år':py['Omsättning'],'Tillväxt mot föregående år':current['Omsättning']/py['Omsättning']-1})
    year_category.append(current)
monthly=[{'År–månad':str(ym),**totals('where yearmonth=?',(ym,))} for (ym,) in con.execute('select distinct yearmonth from joined order by yearmonth').fetchall()]
assert len(monthly)==24
autumn=con.execute('select count(*) from joined where yearmonth%100 in (11,12)').fetchone()[0]
summer=con.execute('select count(*) from joined where yearmonth%100 in (6,7)').fetchone()[0]
assert autumn>summer
assert annual['2025']['Omsättning']>annual['2024']['Omsättning']
layout=json.loads((OUT/'layout-and-bindings.json').read_text(encoding='utf-8'))
metadata=json.loads((OUT/'tmdl-result.json').read_text(encoding='utf-8-sig'))['modelMetadata']
model={t['name']:{'Column':{c['name'] for c in t['columns']},'Measure':{m['name'] for m in t['measures']}} for t in metadata}
for placement in layout['placements']:
    x,y,w,h=placement['box'];assert x>=0 and y>=0 and x+w<=1920 and y+h<=1080
    for field in placement['fields']:
        kind=next(iter(field));expression=field[kind]
        assert expression['Property'] in model[expression['Expression']['SourceRef']['Entity']][kind]
    for other in layout['placements']:
        if placement['page']!=other['page'] or placement['key']==other['key']:continue
        a,b,c,d=other['box'];assert not(x<a+c and x+w>a and y<b+d and y+h>b),f"Overlap: {placement['key']} / {other['key']}"
manifest=json.loads((DATA/'manifest.json').read_text(encoding='utf-8'))
assert all(hashlib.sha256((DATA/f'{name}.csv').read_bytes()).hexdigest()==expected for name,expected in manifest['sha256'].items())
results={'status':'passed','rowCounts':{k:len(v) for k,v in tables.items()},'uniqueOrders':len(orders),
 'allForeignKeysValid':True,'dateContinuity':True,'orderConsistency':True,'allCustomersAndProductsRepresented':True,
 'monetaryIdentities':True,'novDecLines':autumn,'junJulLines':summer,'visuals':len(layout['placements']),
 'boundsAndOverlap':'passed','fieldBindings':'match TOM metadata','annual':annual,
 'year2025ByCategory':year_category,'monthly':monthly,
 'limitations':['Expected values computed with independent SQL on CSV; DAX and Power Query were not executed.','Order counts across categories are not additive because one order can contain multiple categories.']}
(OUT/'data-and-measure-expectations.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'passed','annual':annual,'seasonalityLines':{'novDec':autumn,'junJul':summer},'visuals':len(layout['placements'])},ensure_ascii=False))
