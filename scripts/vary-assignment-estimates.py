"""Make demo original time estimates useful for historical overrun analysis."""
from pathlib import Path
from collections import defaultdict
import csv,json,random,hashlib,math
BASE=Path(__file__).resolve().parents[1]/'powerbi-ledningsrapport';DATA=BASE/'data'
if json.loads((DATA/'manifest.json').read_text(encoding='utf-8')).get('historicalTimeEstimates'):
 print('Historical demo estimates already varied; unchanged.');raise SystemExit(0)
def read(n):return list(csv.DictReader((DATA/(n+'.csv')).open(encoding='utf-8-sig')))
registry=read('Uppdragsregister');hours=defaultdict(float)
for r in read('Utförd tid'):
 if r['Godkänd']=='Ja':hours[int(r['UppdragID'])]+=float(r['Timmar'])
years=defaultdict(list)
for r in registry:
 if r['Status']=='Avslutat' and int(r['Slutförd'] or 0)>0 and hours[int(r['UppdragID'])]>1:years[int(r['Slutförd'])//10000].append(r)
summary={}
for year,rows in sorted(years.items()):
 rng=random.Random(20261016+year)
 fixed={int(r['UppdragID']) for r in rows if int(r['UppdragID'])>=10000 and float(r['PlaneradeTimmar'])<hours[int(r['UppdragID'])]}
 others=[r for r in rows if int(r['UppdragID']) not in fixed]
 target=max(len(fixed),round(len(rows)*.17))
 picked=fixed|{int(r['UppdragID']) for r in rng.sample(others,target-len(fixed))}
 for r in rows:
  k=int(r['UppdragID'])
  if k in fixed:continue
  if k in picked:r['PlaneradeTimmar']=str(max(1,math.floor(hours[k]/rng.uniform(1.06,1.32))))
  elif float(r['PlaneradeTimmar'])<hours[k]:r['PlaneradeTimmar']=str(math.ceil(hours[k]*rng.uniform(1.03,1.25)))
 actual=sum(hours[int(r['UppdragID'])]>float(r['PlaneradeTimmar']) for r in rows)
 assert actual==target
 summary[year]=dict(completed=len(rows),overOriginalEstimate=actual)
p=DATA/'Uppdragsregister.csv'
with p.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(registry[0]));w.writeheader();w.writerows(registry)
p=DATA/'manifest.json';m=json.loads(p.read_text(encoding='utf-8'));m['rows']['Uppdragsregister']=len(registry);m['sha256']['Uppdragsregister']=hashlib.sha256((DATA/'Uppdragsregister.csv').read_bytes()).hexdigest();m['historicalTimeEstimates']='scripts/vary-assignment-estimates.py; synthetic original planned hours varied; actual hours and financial data unchanged.';p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(BASE/'validation/historical-time-estimates.json').write_text(json.dumps(dict(status='passed',years=summary,actualsUnchanged=True),indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary))
