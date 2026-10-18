"""Independent source reconciliation and read-only DAX cases for historical page."""
from pathlib import Path
from collections import defaultdict
from datetime import date
import csv,json,calendar
BASE=Path(__file__).resolve().parents[1]/'powerbi-ledningsrapport';DATA=BASE/'data';OUT=BASE/'validation'
def read(n):return list(csv.DictReader((DATA/(n+'.csv')).open(encoding='utf-8-sig')))
resources={int(r['ResursID']):r for r in read('Resurser')};jobs={int(r['UppdragID']):r for r in read('Uppdragsregister')}
time=read('Utförd tid');capacity=read('Arbetskapacitet');economy=read('Uppdragsekonomi');mix=read('Tidsanvändning')
for rows in [time,capacity,economy,mix]:
 for r in rows:r['Datumnyckel']=int(r['Datumnyckel'])
latest=int(read('Planinställning')[0]['SenasteUtfall'].replace('-',''))
monthly_time=defaultdict(float)
for r in time:
 if r['Godkänd']=='Ja' and r['Debiterbar']=='Ja':monthly_time[int(jobs[int(r['UppdragID'])]['ResursID']),r['Datumnyckel']//100]+=float(r['Timmar'])
over=[]
for r in mix:
 k=int(r['ResursID']),r['Datumnyckel']//100
 assert abs(float(r['Debiterbart'])-monthly_time[k])<.001
 actual=sum(float(r[c]) for c in ['Debiterbart','EjDebiterbartKundarbete','InterntArbete','EjTidrapporterat']);available=float(r['Tillgängligt'])
 assert actual>=available-.001
 if actual>available+.001:over.append(dict(resource=k[0],month=k[1],hours=actual-available))
 assert r['Datumnyckel']<=latest
periods=[('year2024','Helår','2024',20240101,20241231),('year2025','Helår','2025',20250101,20251231),('r12sep2026','R12','September 2026',20251001,20260930),('sep2026','Månad','September 2026',20260901,20260930),('futureOct2026','Månad','Oktober 2026',20261001,20261031)]
scopes=[('all',None,'Alla'),('technical','Teknisk service','Alla'),('staffing','Bemanning','Alla'),('north','Teknisk service','Tekniker Nord'),('dish','Bemanning','Diskpersonal'),('invalidGroup','Teknisk service','Diskpersonal')]
cases=[];queries=[]
def literal(s):return '"'+s.replace('"','""')+'"'
for period,mode,label,start,selected_end in periods:
 end=min(selected_end,latest)
 for scope,area,group in scopes:
  ids={k for k,r in resources.items() if area is None or r['Område']==area}
  valid=any(resources[k]['Resursgrupp']==group for k in ids)
  if group!='Alla' and valid:ids={k for k in ids if resources[k]['Resursgrupp']==group}
  selected_jobs={k for k,r in jobs.items() if int(r['ResursID']) in ids}
  closed={k for k in selected_jobs if jobs[k]['Status']=='Avslutat' and start<=int(jobs[k]['Slutförd'] or 0)<=end}
  hours=sum(float(r['Timmar']) for r in time if int(r['UppdragID']) in selected_jobs and start<=r['Datumnyckel']<=end and r['Godkänd']=='Ja' and r['Debiterbar']=='Ja')
  cap=sum(float(r['Tillgängligt']) for r in capacity if int(r['ResursID']) in ids and start<=r['Datumnyckel']<=end)
  rev=sum(float(r['Intäkt']) for r in economy if int(r['UppdragID']) in selected_jobs and start<=r['Datumnyckel']<=end)
  cost=sum(float(r['DirektKostnad']) for r in economy if int(r['UppdragID']) in selected_jobs and start<=r['Datumnyckel']<=end)
  actual_by_job=defaultdict(float)
  for r in time:
   if int(r['UppdragID']) in closed and r['Datumnyckel']<=end and r['Godkänd']=='Ja':actual_by_job[int(r['UppdragID'])]+=float(r['Timmar'])
  over_plan=sum(actual_by_job[k]>float(jobs[k]['PlaneradeTimmar'])+1e-8 for k in closed)
  selected_mix=[r for r in mix if int(r['ResursID']) in ids and start<=r['Datumnyckel']<=end]
  fields={name:sum(float(r[col]) for r in selected_mix) for name,col in [('Billable','Debiterbart'),('CustomerNonbillable','EjDebiterbartKundarbete'),('Internal','InterntArbete'),('Unreported','EjTidrapporterat'),('Available','Tillgängligt')]}
  cid=period+':'+scope
  expected=dict(Case=cid,Jobs=len(closed),Hours=hours,Capacity=cap,Rate=hours/cap if cap else None,Margin=(rev-cost)/rev if rev else None,OverPlan=over_plan,**fields)
  cases.append(expected)
  if end<start:assert not hours and not cap and not selected_mix
  values={'Jobs':'Uppdrag utförda','Hours':'Utfall timmar','Capacity':'Utfall kapacitet','Rate':'Utfall debiteringsgrad','Margin':'Utfall marginal','OverPlan':'Uppdrag över tidskalkyl','Billable':'Tid debiterbar','CustomerNonbillable':'Tid kundarbete','Internal':'Tid internt','Unreported':'Tid ej rapporterat','Available':'Tid tillgänglig'}
  selector='Helårsval' if mode=='Helår' else 'R12val' if mode=='R12' else 'Månadsval'
  filters=[f"TREATAS({{{literal(mode)}}},'Periodtyp'[Periodtyp])",f"TREATAS({{{literal(label)}}},'{selector}'[Period])",f"TREATAS({{{literal(group)}}},'Resursval'[Resursgrupp])"]
  if area:filters.append(f"TREATAS({{{literal(area)}}},'Uppdragsområden'[Område])")
  queries.append('CALCULATETABLE(ROW("Case",'+literal(cid)+','+','.join(literal(k)+',['+v+']' for k,v in values.items())+'),'+','.join(filters)+')')

# Cumulative row values must stop at 2025 even for projects that continue in 2026.
by_job=defaultdict(list)
for r in time:by_job[int(r['UppdragID'])].append(r)
candidate=[k for k,rows in by_job.items() if any(r['Datumnyckel']<=20251231 for r in rows) and any(r['Datumnyckel']>20251231 for r in rows)]
assert candidate,'Need a cross-year project to exercise period-end safety'
snapshots=[];snapshot_queries=[]
for k in sorted(candidate)[:8]:
 r=jobs[k];cut=20251231
 h=sum(float(t['Timmar']) for t in by_job[k] if t['Datumnyckel']<=cut and t['Godkänd']=='Ja')
 revenue=sum(float(t['Intäkt']) for t in economy if int(t['UppdragID'])==k and t['Datumnyckel']<=cut)
 cost=sum(float(t['DirektKostnad']) for t in economy if int(t['UppdragID'])==k and t['Datumnyckel']<=cut)
 status='Avslutat' if 0<int(r['Slutförd'] or 0)<=cut else 'Pågående'
 snapshots.append(dict(Job=k,Hours=h,Revenue=revenue,Cost=cost,Margin=(revenue-cost)/revenue if revenue else None,Status=status))
 snapshot_queries.append(f'''CALCULATETABLE(ROW("Job",{k},"Hours",[Uppdrag timmar periodslut],"Revenue",[Uppdrag intäkt periodslut],"Cost",[Uppdrag kostnad periodslut],"Margin",[Uppdrag faktisk marginal],"Status",[Uppdrag status historisk]),TREATAS({{"Helår"}},'Periodtyp'[Periodtyp]),TREATAS({{"2025"}},'Helårsval'[Period]),TREATAS({{{k}}},'Uppdragsregister'[UppdragID]))''')
q='EVALUATE\nUNION(\n'+',\n'.join(queries)+'\n)\nORDER BY [Case]\n\nEVALUATE\nUNION(\n'+',\n'.join(snapshot_queries)+'\n)\nORDER BY [Job]\n'
q+='''
EVALUATE
CALCULATETABLE(FILTER(SUMMARIZECOLUMNS('Resurser'[Resursgrupp],'Trendaxel'[Månad],"Rate",[Historisk cellgrad],"Color",[Historisk cellfärg]),NOT ISBLANK([Rate])),TREATAS({"Helår"},'Periodtyp'[Periodtyp]),TREATAS({"2025"},'Helårsval'[Period]))
ORDER BY 'Resurser'[Resursgrupp], 'Trendaxel'[Månad]
'''
(OUT/'historical-assignment-check.dax').write_text(q,encoding='utf-8')
(OUT/'historical-assignment-expected.json').write_text(json.dumps(dict(status='passed',cases=cases,snapshots=snapshots,overreportedResourceMonths=over),indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(dict(status='passed',cases=len(cases),periodEndSnapshots=len(snapshots),overreportedResourceMonths=over)))
