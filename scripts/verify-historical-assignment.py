from pathlib import Path
import csv,json,math
BASE=Path(__file__).resolve().parents[1]/'powerbi-ledningsrapport';OUT=BASE/'validation'
expected=json.loads((OUT/'historical-assignment-expected.json').read_text(encoding='utf-8'))
live=json.loads((OUT/'historical-assignment-live.json').read_text(encoding='utf-8-sig'))['resultSets']
normal=lambda r:{k.strip('[]'):v for k,v in r.items()}
lookup={r['Case']:r for r in expected['cases']};checks=0
for raw in live[0]:
 r=normal(raw);e=lookup[r['Case']]
 for name,value in e.items():
  if name=='Case':continue
  if value is None:assert r[name] is None,(r['Case'],name,r[name],value)
  else:assert math.isclose(r[name] or 0,value,rel_tol=1e-8,abs_tol=.001),(r['Case'],name,r[name],value)
  checks+=1
snapshots={r['Job']:r for r in expected['snapshots']}
for raw in live[1]:
 r=normal(raw);e=snapshots[r['Job']]
 for name,value in e.items():
  if value is None:assert r[name] is None,(r,e)
  elif isinstance(value,str):assert r[name]==value,(r,e)
  else:assert math.isclose(r[name] or 0,value,rel_tol=1e-8,abs_tol=.001),(name,r,e)
  checks+=1
assert len(live[2])==48
for r in live[2]:
 value=r['[Rate]'];color=r['[Color]'];assert color==('#FAD5D1' if value<.75 else '#DCEBFA' if value<.82 else '#CDEEE5')
 checks+=1
# Inspect the source report: no page content may consume plan or forecast data.
page=BASE/'LedningsrapportUtanScroll.Report/definition/pages/30e52cac0a5174639318'
visuals=[json.loads(p.read_text(encoding='utf-8-sig')) for p in (page/'visuals').glob('*/visual.json')]
for v in visuals:
 for forbidden in ['Planbokningar','Planveckor','Uppdrag prognos','ÅterståendeKostnad','Plan beläggning','Plan ledigt','Planperiod text']:
  assert forbidden not in json.dumps(v,ensure_ascii=False),(forbidden,v['name'])
 p=v['position'];assert 0<=p['x'] and 0<=p['y'] and p['x']+p['width']<=1920 and p['y']+p['height']<=1200
assert not (page.parent/'9b71739249a33de0815d').exists()
year2025=normal(next(r for r in live[0] if r['[Case]']=='year2025:all'))
result=dict(status='passed',source='Actual Desktop DAX versus independently calculated CSVs, plus persisted PBIR checks',cases=len(live[0]),periodEndSnapshots=len(live[1]),resourceMonthCells=len(live[2]),fieldChecks=checks,year2025=year2025,forwardLookingBindingsRemoved=True,overreportedResourceMonths=expected['overreportedResourceMonths'])
(OUT/'historical-assignment-verification.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(result))
