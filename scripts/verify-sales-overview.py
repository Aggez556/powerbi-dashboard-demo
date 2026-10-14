"""Independent checks of the shared persisted facts, not a DAX emulator."""
from pathlib import Path
from decimal import Decimal
from collections import defaultdict
import csv,json,math

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'powerbi-ledningsrapport'
def load(n):
    with (BASE/'data'/f'{n}.csv').open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
sales=load('Försäljning');costs=load('Direkta kostnader')
articles={int(r['Artikelnyckel']):r for r in load('Artiklar')}
customers={int(r['Kundnyckel']):r for r in load('Kunder')}
for r in sales:
    for k in ['Datumnyckel','Kundnyckel','Områdesnyckel','Artikelnyckel','Ordernyckel','Nettointäkt']:r[k]=int(r[k])
    r['Debiterade timmar']=Decimal(r['Debiterade timmar'])
    assert int(articles[r['Artikelnyckel']]['Områdesordning'])==r['Områdesnyckel']
    assert r['Kundnyckel'] in customers
    assert (r['Debitering']=='Timdebiterat')==(r['Debiterade timmar']!=0)
    assert r['Områdesnyckel']!=1 or r['Debitering']=='Produkt'
for r in costs:
    for k in ['Datumnyckel','Områdesnyckel','Artikelnyckel','Belopp']:r[k]=int(r[k])
    assert int(articles[r['Artikelnyckel']]['Områdesordning'])==r['Områdesnyckel']
assert len({r['Fakturarad'] for r in sales})==len(sales)

def summary(lo,hi,area=0):
    rows=[r for r in sales if lo<=r['Datumnyckel']<=hi and (not area or r['Områdesnyckel']==area)]
    direct=[r for r in costs if lo<=r['Datumnyckel']<=hi and (not area or r['Områdesnyckel']==area)]
    revenue=sum(r['Nettointäkt'] for r in rows);gp=revenue-sum(r['Belopp'] for r in direct)
    cat=defaultdict(lambda:[0,0]);industry=defaultdict(int);months=defaultdict(int)
    for r in rows:
        cat[articles[r['Artikelnyckel']]['Kategori']][0]+=r['Nettointäkt']
        industry[customers[r['Kundnyckel']]['Kundbransch']]+=r['Nettointäkt']
        months[r['Datumnyckel']//100]+=r['Nettointäkt']
    for r in direct:cat[articles[r['Artikelnyckel']]['Kategori']][1]+=r['Belopp']
    assert sum(v[0] for v in cat.values())==sum(industry.values())==sum(months.values())==revenue
    assert sum(v[0]-v[1] for v in cat.values())==gp
    buyers=len({r['Kundnyckel'] for r in rows if r['Nettointäkt']>0})
    positive_orders={r['Ordernyckel'] for r in rows if r['Områdesnyckel']==1 and r['Nettointäkt']>0}
    order_net=sum(r['Nettointäkt'] for r in rows if r['Områdesnyckel']==1 and r['Ordernyckel'] in positive_orders)
    timed=[r for r in rows if r['Debitering']=='Timdebiterat']
    hours=sum((r['Debiterade timmar'] for r in timed),Decimal(0));hour_net=sum(r['Nettointäkt'] for r in timed)
    assert all(r['Nettointäkt']>0 or r['Kundnyckel']!=301 for r in rows if r['Ordernyckel'] in positive_orders)
    return dict(revenue=revenue,grossProfit=gp,margin=gp/revenue,buyers=buyers,revenuePerCustomer=revenue/buyers,
        orders=len(positive_orders),orderNet=order_net,orderAverage=order_net/len(positive_orders) if positive_orders else None,
        billedHours=str(hours),hourRevenue=hour_net,hourlyRate=float(Decimal(hour_net)/hours) if hours else None,
        categories={k:dict(revenue=v[0],grossProfit=v[0]-v[1]) for k,v in cat.items()},industries=dict(industry),months=dict(months))

cases=[]
for mode,lo,hi,pl,ph in [('R12',20251001,20260930,20241001,20250930),('Helår 2025',20250101,20251231,20240101,20241231),('Helår 2024',20240101,20241231,20230101,20231231),('Månad',20260901,20260930,20250901,20250930)]:
    variants=[]
    for area in range(4):
        current,previous=summary(lo,hi,area),summary(pl,ph,area)
        variants.append(dict(area=area,current=current,previous=previous,growth=current['revenue']/previous['revenue']-1))
    assert sum(v['current']['revenue'] for v in variants[1:])==variants[0]['current']['revenue']
    assert sum(v['current']['grossProfit'] for v in variants[1:])==variants[0]['current']['grossProfit']
    cases.append(dict(mode=mode,start=lo,end=hi,previousStart=pl,previousEnd=ph,variants=variants))
ref=cases[0]['variants'][0];now,old=ref['current'],ref['previous']
assert [now[k] for k in ['revenue','grossProfit','buyers']]==[139500000,36040000,270]
assert [old[k] for k in ['revenue','grossProfit','buyers']]==[120000000,33000000,240]
assert math.isclose(now['revenuePerCustomer']/1000,516.6666666666666)
assert math.isclose(old['revenuePerCustomer']/1000,500)
assert round((now['margin']-old['margin'])*100,1)==-1.7
assert round(ref['growth']*100,1)==16.3
expected=[('Maskiner',35000000,30000000,7000000),('Rengöringsprodukter',30000000,25000000,10800000),('Förbrukningsmaterial',20000000,18000000,6000000),('Service',12000000,9000000,4320000),('Reparationer',10000000,8000000,2300000),('Installationer',8000000,6000000,2680000),('Diskpersonal',14000000,14000000,1680000),('Städpersonal',10500000,10000000,1260000)]
for name,rev,prior,gp in expected:
    assert now['categories'][name]==dict(revenue=rev,grossProfit=gp)
    assert old['categories'][name]['revenue']==prior
assert now['industries']==dict(Restaurang=52000000,Hotell=36000000,Catering=22000000,Kontor=17500000,Livsmedel=12000000)
assert old['industries']==dict(Restaurang=45000000,Hotell=31000000,Catering=18000000,Kontor=15000000,Livsmedel=11000000)
assert [v['previous']['grossProfit'] for v in cases[0]['variants'][1:]]==[20500000,6750000,5750000]
assert any(r['Debiterade timmar']<0 for r in sales)
assert any(r['Debitering']=='Fastpris' for r in sales) and any(r['Debitering']=='Material' for r in sales)
assert len(summary(20251001,20260930)['months'])==12

report=BASE/'LedningsrapportUtanScroll.Report'
pages=json.loads((report/'definition/pages/pages.json').read_text())['pageOrder']
assert len(pages)==5
for page in pages:
    values=[json.loads(p.read_text(encoding='utf-8')) for p in (report/'definition/pages'/page/'visuals').glob('*/visual.json')]
    assert not any('Hygiengruppen' in json.dumps(v,ensure_ascii=False) for v in values)
    links=[v['visual'].get('visualContainerObjects',{}).get('visualLink',[]) for v in values]
    assert any(any(e['properties'].get('navigationSection',{}).get('expr',{}).get('Literal',{}).get('Value')=="'"+pages[2]+"'" for e in link) for link in links)
result=dict(status='passed',source='Independent persisted CSV and PBIR checks; not live DAX or rendered screenshots',periodAreaCases=16,cases=cases,checks=['shared sales and costs','category/article and area integrity','unique positive-order set and matching net order income','time-billed income only; negative credited hours included','16 period/area cases','category, industry and area reconciliation','weighted margins and unique buyers','September reference controls','three-page sales navigation'])
(BASE/'validation/sales-independent-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status='passed',periodAreaCases=16,categories=8,industries=5,referenceRevenue=now['revenue'],referenceGrossProfit=now['grossProfit'],referenceBuyers=now['buyers'])))
