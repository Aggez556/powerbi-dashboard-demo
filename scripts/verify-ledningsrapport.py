"""Independent checks against persisted CSV, report bindings, and period rules."""
from pathlib import Path
from datetime import date
import csv, json, hashlib,re

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'powerbi-ledningsrapport'
DATA=BASE/'data'
def load(n):
    with (DATA/(n+'.csv')).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
tables={p.stem:load(p.stem) for p in DATA.glob('*.csv')}
manifest=json.loads((DATA/'manifest.json').read_text(encoding='utf-8'))
assert all(hashlib.sha256((DATA/(n+'.csv')).read_bytes()).hexdigest()==h for n,h in manifest['sha256'].items())
def summary(start,stop,area=None):
    lo=int(start.replace('-',''));hi=int(stop.replace('-',''))
    def filt(n):return [r for r in tables[n] if lo<=int(r['Datumnyckel'])<=hi and (area is None or int(r.get('Områdesnyckel',area))==area)]
    sales=filt('Försäljning');revenue=sum(int(r['Nettointäkt']) for r in sales)
    gp=revenue-sum(int(r['Belopp']) for r in filt('Direkta kostnader'))
    central=sum(int(r['Belopp']) for r in filt('Gemensamma kostnader'))
    return {'revenue':revenue,'grossProfit':gp,'operatingProfit':gp-central,'centralCosts':central,'budget':sum(int(r['Rörelseresultat']) for r in filt('Budget')),'jobs':len({r['Uppdragsnyckel'] for r in filt('Uppdrag') if r['Status']=='Avslutat'}),'customers':len({r['Kundnyckel'] for r in sales if int(r['Nettointäkt'])>0})}
now=summary('2025-10-01','2026-09-30');old=summary('2024-10-01','2025-09-30')
expected={'revenue':139500000,'grossProfit':36040000,'operatingProfit':8000000,'centralCosts':28040000,'budget':9750000,'jobs':960,'customers':270}
assert now==expected,(now,expected)
assert old['revenue']==120000000 and old['grossProfit']==33000000 and old['centralCosts']==24000000 and old['operatingProfit']==9000000 and old['jobs']==840 and old['customers']==240,old
areas=[summary('2025-10-01','2026-09-30',a) for a in (1,2,3)]
assert [a['revenue'] for a in areas]==[85000000,30000000,24500000]
assert [a['grossProfit'] for a in areas]==[23800000,9300000,2940000]
assert [a['customers'] for a in areas]==[230,145,80]
assert [a['jobs'] for a in areas]==[0,640,320]
prior_areas=[summary('2024-10-01','2025-09-30',a) for a in (1,2,3)]
bridge=[old['operatingProfit']]+[a['grossProfit']-b['grossProfit'] for a,b in zip(areas,prior_areas)]+[-(now['centralCosts']-old['centralCosts'])]
assert bridge==[9000000,3300000,2550000,-2810000,-4040000]
assert sum(bridge)==now['operatingProfit']
for fact in ['Försäljning','Direkta kostnader','Gemensamma kostnader','Uppdrag','Budget']:
    for row in tables[fact]:
        assert row['Datumnyckel'] in {d['Datumnyckel'] for d in tables['Datum']}
        if 'Områdesnyckel' in row:assert row['Områdesnyckel'] in {'1','2','3'}
        if 'Kundnyckel' in row:assert (0 if fact=='Direkta kostnader' else 1)<=int(row['Kundnyckel'])<=301
assert len({r['Uppdragsnyckel'] for r in tables['Uppdrag']})==len(tables['Uppdrag'])
assert not any(r['Kundnyckel']=='301' and int(r['Nettointäkt'])>0 for r in tables['Försäljning'])
assert len(tables['Datum'])==(date(2026,10,31)-date(2023,1,1)).days+1
assert max(r['Datum'] for r in tables['Datum'])=='2026-10-31'
assert max(r['Slutdatum'] for r in tables['R12val'])=='2026-10-31'
assert max(r['Slutdatum'] for r in tables['Månadsval'])=='2026-10-31'
assert [r['Period'] for r in tables['Helårsval']]==['2024','2025']
for year,expected_months in [(2023,12),(2024,12),(2025,12),(2026,10)]:
    assert len({r['Datumnyckel'][:6] for r in tables['Försäljning'] if r['Datumnyckel'].startswith(str(year))})==expected_months
report=BASE/json.loads((BASE/'Ledningsrapport.pbip').read_text(encoding='utf-8-sig'))['artifacts'][0]['report']['path']
metadata=json.loads((report/'definition/pages/pages.json').read_text(encoding='utf-8'))
assert len(metadata['pageOrder'])==4
model_text=(BASE/'Ledningsrapport.SemanticModel/definition/tables/Försäljning.tmdl').read_text(encoding='utf-8')
for f in (report/'definition/pages').glob('*/visuals/*/visual.json'):
    v=json.loads(f.read_text(encoding='utf-8'))
    p=v['position'];assert p['x']>=0 and p['y']>=0 and p['x']+p['width']<=1920 and p['y']+p['height']<=1200
    for role in v['visual'].get('query',{}).get('queryState',{}).values():
        for projection in role['projections']:
            field=projection['field'];kind=next(iter(field));q=field[kind];t=q['Expression']['SourceRef']['Entity'];n=q['Property']
            assert t in tables
            assert re.search(r"measure '?"+re.escape(n)+r"'? =",model_text) if kind=='Measure' else n in tables[t][0]
scenarios=[]
for mode,s,e,ps,pe in [('R12','2025-11-01','2026-10-31','2024-11-01','2025-10-31'),('Helår','2025-01-01','2025-12-31','2024-01-01','2024-12-31'),('Helår','2024-01-01','2024-12-31','2023-01-01','2023-12-31'),('Månad','2026-10-01','2026-10-31','2025-10-01','2025-10-31')]:
    a,b=summary(s,e),summary(ps,pe)
    steps=[b['operatingProfit']]+[summary(s,e,i)['grossProfit']-summary(ps,pe,i)['grossProfit'] for i in (1,2,3)]+[-(a['centralCosts']-b['centralCosts'])]
    assert sum(steps)==a['operatingProfit']
    scenarios.append({'mode':mode,'start':s,'end':e,'comparisonStart':ps,'comparisonEnd':pe,'actual':a,'comparison':b,'bridge':steps,'budgetVariance':a['operatingProfit']-a['budget'],'grossMargin':a['grossProfit']/a['revenue']})
result={'status':'passed','source':'Independent Python calculations against persisted CSV; NOT live DAX or screenshots','latest':scenarios[0]['actual'],'referenceSeptember':now,'previousReference':old,'areasReference':areas,'bridgeReference':bridge,'scenarios':scenarios,'checks':['exact September reference controls preserved','full years 2024 and 2025','January to October 2026','unique customers and overlapping areas','credit-only customer exclusion','completed unique jobs and canceled exclusion','all foreign keys','contiguous dates','four period scenarios','budget matching period','waterfall reconciliation','PBIR field bindings','two pages and bounds']}
(BASE/'validation/data-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'passed','latestR12':scenarios[0]['actual'],'latestMonth':'2026-10'},ensure_ascii=False))
