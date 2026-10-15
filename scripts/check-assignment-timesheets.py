"""Validate the supplementary demo time ledger independently of Power BI."""
from pathlib import Path
from collections import defaultdict
import csv,json,math
BASE=Path(__file__).resolve().parents[1]/'powerbi-ledningsrapport';DATA=BASE/'data'
def read(n):return list(csv.DictReader((DATA/(n+'.csv')).open(encoding='utf-8-sig')))
registry={int(r['UppdragID']):r for r in read('Uppdragsregister')}
capacity={(int(r['ResursID']),int(r['Datumnyckel'])):float(r['Tillgängligt']) for r in read('Arbetskapacitet')}
time=read('Utförd tid');extra=read('Utförd tid komplettering')
seed=defaultdict(float);monthly=defaultdict(float);whole=defaultdict(float)
extra_ids={int(r['UppdragID']) for r in extra}
for r in time:
 jid=int(r['UppdragID']);pid=int(registry[jid]['ResursID']);d=int(r['Datumnyckel']);h=float(r['Timmar'])
 monthly[(pid,d//100)]+=h;whole[jid]+=h
 if jid not in extra_ids:seed[(pid,d)]+=h
daily_added=defaultdict(float)
for r in extra:
 j=registry[int(r['UppdragID'])];pid=int(j['ResursID']);d=int(r['Datumnyckel']);h=float(r['Timmar'])
 assert j['Status']=='Pågående' and j['Uppdrag'].endswith('Löpande kunduppdrag')
 assert int(j['Startdatum'].replace('-',''))<=d<=20260930
 assert capacity[(pid,d)]>0 and r['Godkänd']==r['Debiterbar']=='Ja'
 daily_added[(pid,d)]+=h
for key,h in daily_added.items():assert h+seed[key]<=capacity[key]+.011,(key,h,seed[key],capacity[key])
for p in read('Tidrapporteringsprofiler'):
 key=int(p['ResursID']),int(p['Månad']);expected=max(float(p['Kapacitet'])*float(p['Profil']),float(p['BefintligaTimmar']))
 assert math.isclose(monthly[key],expected,abs_tol=.011),(key,monthly[key],expected)
for r in read('Uppdrag'):
 if r['Status']=='Avslutat' and int(r['Datumnyckel'])<=20260930:assert whole[int(r['Uppdragsnyckel'])]==float(r['Timmar'])
for jid in extra_ids:assert float(registry[jid]['PlaneradeTimmar'])>=whole[jid]
periods={}
for label,start,end in [('Helår 2025',20250101,20251231),('Helår 2024',20240101,20241231),('R12 september 2026',20251001,20260930),('September 2026',20260901,20260930)]:
 hours=sum(float(r['Timmar']) for r in time if start<=int(r['Datumnyckel'])<=end)
 cap=sum(h for (pid,d),h in capacity.items() if start<=d<=end)
 periods[label]=dict(hours=round(hours,2),capacity=cap,rate=hours/cap)
result=dict(status='passed',source='Independent CSV validation, not UI',supplementaryRows=len(extra),periods=periods,originalCompletedHoursPreserved=True,supplementWithinDailyCapacity=True)
(BASE/'validation/assignment-timesheet-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=True))
