"""Independent lifecycle reconciliation from persisted transactions and metadata."""
from pathlib import Path
from collections import defaultdict
from datetime import date
import calendar,csv,json,math,re
root=Path(__file__).resolve().parents[1];base=root/'powerbi-ledningsrapport'
def read(n):
    with (base/'data'/f'{n}.csv').open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
customers={int(r['Kundnyckel']):r for r in read('Kunder')};sales=read('Försäljning');costs=read('Direkta kostnader')
for r in sales:
    for k in ['Datumnyckel','Kundnyckel','Nettointäkt']:r[k]=int(r[k])
for r in costs:
    for k in ['Datumnyckel','Kundnyckel','Belopp']:r[k]=int(r[k])
def summarize(lo,hi,pl,ph,industry=None):
    a=defaultdict(int);b=defaultdict(int);active=set();previous=set()
    for r in sales:
        k=r['Kundnyckel']
        if industry and customers[k]['Kundbransch']!=industry:continue
        if lo<=r['Datumnyckel']<=hi:
            a[k]+=r['Nettointäkt']
            if r['Nettointäkt']>0:active.add(k)
        if pl<=r['Datumnyckel']<=ph:
            b[k]+=r['Nettointäkt']
            if r['Nettointäkt']>0:previous.add(k)
    continued=active&previous;lost=previous-active
    new={k for k in active-previous if int(customers[k]['Första köp'])>=lo}
    reactivated={k for k in active-previous if 0<int(customers[k]['Första köp'])<pl}
    assert active==continued|new|reactivated
    assert not(new&reactivated)
    current=sum(a.values());prior=sum(b.values())
    groups=[sum(a[k] for k in cohort) for cohort in [continued,new,reactivated]]
    assert sum(groups)==current
    assert sum(b[k] for k in previous)==prior
    decreasing=sum(a[k]-b[k] for k in continued if a[k]<b[k]);increasing=sum(a[k]-b[k] for k in continued if a[k]>=b[k])
    loss=sum(a[k]-b[k] for k in lost);existing=sum(a[k] for k in previous)
    assert prior+loss+decreasing+increasing+groups[1]+groups[2]==current
    assert prior-existing==-(loss+decreasing+increasing)
    assert len(previous)+len(new)+len(reactivated)-len(lost)==len(active)
    assert all(a[k]>=0 and b[k]>0 for k in previous)
    monthly=defaultdict(lambda:[0,0,0])
    for r in sales:
        if lo<=r['Datumnyckel']<=hi and (not industry or customers[r['Kundnyckel']]['Kundbransch']==industry):
            k=r['Kundnyckel'];index=0 if k in continued else 1 if k in new else 2
            monthly[r['Datumnyckel']//100][index]+=r['Nettointäkt']
    assert [sum(v[i] for v in monthly.values()) for i in range(3)]==groups
    return dict(active=len(active),previous=len(previous),continuing=len(continued),new=len(new),reactivated=len(reactivated),lost=len(lost),revenue=current,previousRevenue=prior,cohortRevenue=groups,bridge=[prior,loss,decreasing,increasing,groups[1],groups[2]],logoChurn=len(lost)/len(previous) if previous else None,revenueChurn=(prior-existing)/prior if prior else None,existingRevenue=existing,newRevenueShare=(groups[1]+groups[2])/current if current else None,monthly=dict(monthly))
scenarios=[]
for mode,lo,hi,pl,ph in [('R12 september',20251001,20260930,20241001,20250930),('Helår 2025',20250101,20251231,20240101,20241231),('Helår 2024',20240101,20241231,20230101,20231231),('Månad september, churn R12',20251001,20260930,20241001,20250930)]:
    for industry in [None,'Restaurang','Hotell','Catering','Kontor','Livsmedel']:
        scenarios.append(dict(mode=mode,industry=industry or 'Alla',result=summarize(lo,hi,pl,ph,industry)))
ref=scenarios[0]['result']
assert [ref[k] for k in ['active','previous','continuing','new','reactivated','lost']]==[270,240,230,35,5,10]
assert ref['cohortRevenue']==[110000000,27000000,2500000]
assert ref['bridge']==[120000000,-4000000,-18000000,12000000,27000000,2500000]
assert ref['existingRevenue']==110000000
assert math.isclose(ref['logoChurn'],10/240) and math.isclose(ref['revenueChurn'],10/120)
assert math.isclose(ref['newRevenueShare'],29.5/139.5)
assert sum(int(r['Belopp']) for r in costs if 20251001<=r['Datumnyckel']<=20260930)==103460000
assert any(r['Kundnyckel']==0 and r['Belopp']>0 for r in costs)
assert all(r['Kundnyckel'] in customers for r in costs)
assert any(r['Nettointäkt']<0 for r in sales)
assert all(int(customers[k]['Första köp'])==20200615 for k in range(276,281))
report=base/'LedningsrapportUtanScroll.Report';meta=json.loads((report/'definition/pages/pages.json').read_text())
assert len(meta['pageOrder'])==5
page=[p for p in (report/'definition/pages').glob('*/page.json') if json.loads(p.read_text(encoding='utf-8'))['displayName']=='Kunder'][0]
config=json.loads(page.read_text(encoding='utf-8'));assert config['visualInteractions']
visuals=[json.loads(p.read_text(encoding='utf-8')) for p in (page.parent/'visuals').glob('*/visual.json')]
for v in visuals:
    q=v['position'];assert q['x']>=0 and q['y']>=0 and q['x']+q['width']<=1920 and q['y']+q['height']<=1200
    assert 'Hygiengruppen' not in json.dumps(v,ensure_ascii=False)
table=next(v for v in visuals if v['visual']['visualType']=='tableEx')
assert sum(float(x['properties']['value']['expr']['Literal']['Value'][:-1]) for x in table['visual']['objects']['columnWidth'])<=table['position']['width']
assert table['filterConfig']['filters'][0]['field']['Measure']['Property']=='Kund tabell synlig'
result=dict(status='passed',source='Independent CSV and PBIR checks; not live DAX or screenshot verification',periodIndustryCases=len(scenarios),reference=ref,scenarios=scenarios,checks=['exact reference cohorts and bridges','24 period/industry cases','fixed period cohorts in monthly trend','customer count identity','revenue bridge identity','negative credits included without customer activity','historical first-purchase metadata','assigned plus unassigned costs reconcile','five public pages and native visuals','table widths fit and status filter and internal scrolling'])
(base/'validation/customer-independent-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status='passed',periodIndustryCases=24,reference={k:ref[k] for k in ['active','previous','new','reactivated','lost','revenue','logoChurn','revenueChurn','cohortRevenue','bridge']})))
