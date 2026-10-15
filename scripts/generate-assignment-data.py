"""Add operational detail without changing any established finance or job facts."""
from pathlib import Path
from datetime import date,timedelta
from collections import defaultdict
import csv,json,calendar,hashlib,math
BASE=Path(__file__).resolve().parents[1]/'powerbi-ledningsrapport'
DATA=BASE/'data'
def read(n):return list(csv.DictReader((DATA/(n+'.csv')).open(encoding='utf-8-sig')))
def write(n,rows):
 with (DATA/(n+'.csv')).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def dk(d):return int(d.strftime('%Y%m%d'))
groups=[(1,'Tekniker Nord',2,5,40),(2,'Tekniker Syd',2,5,40),(3,'Diskpersonal',3,10,35),(4,'Städpersonal',3,10,25)]
people=[];members={}
for gid,g,area,n,h in groups:
 members[gid]=[]
 for i in range(n):
  pid=gid*100+i+1;members[gid].append(pid)
  people.append(dict(ResursID=pid,Medarbetare=f'Medarbetare {pid}',Resursgrupp=g,GruppID=gid,Områdesnyckel=area,Område='Teknisk service' if area==2 else 'Bemanning',Veckotimmar=h,Mål=.82))
resource={p['ResursID']:p for p in people}
jobs=[];by_customer_area=defaultdict(list);time=[]
for r in read('Uppdrag'):
 if r['Status']!='Avslutat':continue
 if int(r['Datumnyckel'])>20260930:continue
 jid=int(r['Uppdragsnyckel']);a=int(r['Områdesnyckel']);cid=int(r['Kundnyckel']);end=date.fromisoformat(str(r['Datumnyckel'])[:4]+'-'+str(r['Datumnyckel'])[4:6]+'-'+str(r['Datumnyckel'])[6:]);start=end-timedelta(days=14)
 gid=(1+jid%2) if a==2 else (3+jid%2);pid=members[gid][jid%len(members[gid])]
 job=dict(UppdragID=jid,Uppdrag=f'U-{jid:04d} · '+('Serviceuppdrag' if a==2 else 'Bemanningsuppdrag'),Kundnyckel=cid,ResursID=pid,Typ='Teknisk service' if a==2 else 'Bemanning',Status='Avslutat',Startdatum=start.isoformat(),Slutdatum=end.isoformat(),Slutförd=dk(end),PlaneradeTimmar=int(r['Timmar'])+2,Kalkylmarginal=.30 if a==2 else .14,Slutintäkt=0,KostnadHittills=0,ÅterståendeKostnad=0,Ansvarig=f'Medarbetare {pid}')
 jobs.append(job);by_customer_area[(cid,a)].append(job)
 time.append(dict(UppdragID=jid,Datumnyckel=dk(end),Timmar=int(r['Timmar']),Godkänd='Ja',Debiterbar='Ja'))
nextid=10000
def ongoing(cid,a,label=None):
 global nextid
 nextid+=1;gid=(1+cid%2) if a==2 else (3+cid%2);pid=members[gid][cid%len(members[gid])]
 job=dict(UppdragID=nextid,Uppdrag=f'U-{nextid} · '+(label or 'Löpande kunduppdrag'),Kundnyckel=cid,ResursID=pid,Typ='Teknisk service' if a==2 else 'Bemanning',Status='Pågående',Startdatum='2023-01-01',Slutdatum='',Slutförd=0,PlaneradeTimmar=240,Kalkylmarginal=.30 if a==2 else .14,Slutintäkt=0,KostnadHittills=0,ÅterståendeKostnad=0,Ansvarig=f'Medarbetare {pid}')
 jobs.append(job);by_customer_area[(cid,a)].append(job);return job
# Four traceable risk/example contracts; identities reuse the customer dimension.
customers={r['Kund']:int(r['Kundnyckel']) for r in read('Kunder')}
for name,a,label,plan,hours,margin,forecast in [('Bistro Strand',2,'Installation diskmaskin',120,138,.30,.22),('Hotell Björken',3,'Diskbemanning',320,280,.15,.12),('Kontor Väster',2,'Serviceavtal',80,46,.32,.33),('Restaurang Torget',3,'Städbemanning',240,160,.14,.14)]:
 if name not in customers:continue
 j=ongoing(customers[name],a,label);j.update(Startdatum='2026-09-01',PlaneradeTimmar=plan,Kalkylmarginal=margin)
 j['_forecast']=forecast
 time.append(dict(UppdragID=j['UppdragID'],Datumnyckel=20260923,Timmar=hours,Godkänd='Ja',Debiterbar='Ja'))
# Aggregate each existing financial row exactly once. Prefer a completed delivery
# in the same month/customer/area; otherwise the customer's ongoing contract.
finance=defaultdict(lambda:[0,0]);source=defaultdict(lambda:[0,0]);unassigned=defaultdict(int)
def assign(r):
 cid=int(r.get('Kundnyckel') or 0);a=int(r['Områdesnyckel']);d=int(r['Datumnyckel']);candidates=by_customer_area[(cid,a)]
 same=[j for j in candidates if j['Slutförd']//100==d//100]
 if same:return same[d%len(same)]
 live=[j for j in candidates if j['Status']=='Pågående' and j['Startdatum']<=f'{d//10000:04d}-{d//100%100:02d}-28']
 return live[0] if live else ongoing(cid,a)
for name,field,idx in [('Försäljning','Nettointäkt',0),('Direkta kostnader','Belopp',1)]:
 for r in read(name):
  a=int(r['Områdesnyckel']);d=int(r['Datumnyckel'])
  if a not in [2,3] or d>20260930:continue
  amount=int(r[field]);source[(d,a)][idx]+=amount
  if idx==1 and int(r.get('Kundnyckel') or 0)==0:
   # Shared economics keeps these costs. No invented task or employee allocation.
   unassigned[(d,a)]+=amount;continue
  j=assign(r);finance[(j['UppdragID'],d)][idx]+=amount
byid={j['UppdragID']:j for j in jobs};totals=defaultdict(lambda:[0,0])
rows=[]
for (jid,d),(rev,cost) in sorted(finance.items()):
 j=byid[jid];calc=round(rev*(1-j['Kalkylmarginal']),4)
 rows.append(dict(UppdragID=jid,Datumnyckel=d,Intäkt=rev,DirektKostnad=cost,Kalkylkostnad=calc));totals[jid][0]+=rev;totals[jid][1]+=cost
for j in jobs:
 rev,cost=totals[j['UppdragID']];forecast=j.pop('_forecast',None)
 j['KostnadHittills']=cost
 if j['Status']=='Avslutat':j['Slutintäkt']=rev
 else:
  j['Slutintäkt']=max(round(rev*1.25),100000)
  target=forecast if forecast is not None else j['Kalkylmarginal']-.01
  j['ÅterståendeKostnad']=max(0,round(j['Slutintäkt']*(1-target)-cost))
# Individual calendar, one row per person/day. Separate plan date role has no
# relationship to historical Datum. Plan holiday absence is explicitly zero.
def holidays(year):
 # Gregorian Easter, Swedish public holidays and known company leave days.
 a=year%19;b=year//100;c=year%100;d=b//4;e=b%4;f=(b+8)//25;g=(b-f+1)//3;h=(19*a+b-d-g+15)%30;i=c//4;k=c%4;l=(32+2*e+2*i-h-k)%7;m=(a+11*h+22*l)//451
 month=(h+l-7*m+114)//31;dom=(h+l-7*m+114)%31+1;easter=date(year,month,dom)
 midsummer=next(date(year,6,x) for x in range(19,26) if date(year,6,x).weekday()==4)
 return {date(year,1,1),date(year,1,6),date(year,5,1),date(year,6,6),date(year,12,24),date(year,12,25),date(year,12,26),date(year,12,31),easter-timedelta(days=2),easter+timedelta(days=1),easter+timedelta(days=39),midsummer}
known_holidays={y:holidays(y) for y in range(2023,2027)}
capacity=[];day=date(2023,1,1)
while day<=date(2026,9,30):
 if day.weekday()<5:
  for p in people:
   schema=p['Veckotimmar']/5
   absence=schema if (day.month==7 and day.day<=7) or (day.month==12 and day.day>=24) or day in known_holidays[day.year] else 0
   capacity.append(dict(ResursID=p['ResursID'],Datumnyckel=dk(day),Schematimmar=schema,Frånvaro=absence,Tillgängligt=schema-absence))
 day+=timedelta(days=1)
weeks=[];plan=[]
for w in range(8):
 monday=date(2026,10,5)+timedelta(weeks=w);weeks.append(dict(VeckaID=41+w,Vecka=f'v{41+w}',Veckostart=monday.isoformat(),Veckoslut=(monday+timedelta(days=6)).isoformat()))
 for gid,g,a,n,h in groups:
  booked=([220 if w<4 else 180,180 if w<4 else 160,300,180][gid-1])
  for pid in members[gid]:
   contracts=[j for j in jobs if j['ResursID']==pid and j['Status']=='Pågående']
   if not contracts:
    j=ongoing(81 if a==2 else 82,a);j['ResursID']=pid;j['Ansvarig']=f'Medarbetare {pid}';contracts=[j]
   for dayindex in range(5):
    d=monday+timedelta(days=dayindex);cap=h/5;b=booked/n/5
    plan.append(dict(ResursID=pid,Datumnyckel=dk(d),VeckaID=41+w,Snapshot=20260930,UppdragID=contracts[0]['UppdragID'],Kapacitet=cap,Bokat=b,Ledigt=max(cap-b,0),Överbokat=max(b-cap,0)))
# Complete previously missing time on ongoing contracts. The monthly demo
# profiles describe performed work, independently of invoice dates. Existing
# completed-task hours and explicit example hours remain untouched.
seed_hours=defaultdict(float);daily_seed=defaultdict(float);monthly_capacity=defaultdict(list)
for r in time:
 pid=byid[r['UppdragID']]['ResursID'];seed_hours[(pid,r['Datumnyckel']//100)]+=r['Timmar'];daily_seed[(pid,r['Datumnyckel'])]+=r['Timmar']
for r in capacity:monthly_capacity[(r['ResursID'],r['Datumnyckel']//100)].append(r)
ongoing_by_person=defaultdict(list)
for j in jobs:
 if j['Status']=='Pågående' and j['Uppdrag'].endswith('Löpande kunduppdrag'):ongoing_by_person[j['ResursID']].append(j)
technical=[.74,.75,.76,.77,.78,.79,.80,.81,.82,.80,.82,.83]
staffing=[.79,.80,.81,.82,.81,.80,.79,.80,.79,.80,.79,.78]
added=[];profiles=[]
for (pid,month),days in sorted(monthly_capacity.items()):
 year,m=divmod(month,100);a=resource[pid]['Områdesnyckel'];cap=sum(r['Tillgängligt'] for r in days)
 rate=(technical if a==2 else staffing)[m-1]+(year-2025)*.02
 target=round(cap*rate,2);missing=round(max(0,target-seed_hours[(pid,month)]),2)
 contracts=sorted(ongoing_by_person[pid],key=lambda j:j['UppdragID'])
 assert contracts or not missing,('No ongoing contract for resource',pid)
 usable=[r for r in days if r['Tillgängligt']>daily_seed[(pid,r['Datumnyckel'])]]
 profiles.append(dict(ResursID=pid,Månad=month,Kapacitet=cap,Profil=rate,BefintligaTimmar=seed_hours[(pid,month)],KompletteradeTimmar=missing))
 # Integer hundredths preserve exact sums across all dates and contracts.
 units=round(missing*100);weights=[r['Tillgängligt']-daily_seed[(pid,r['Datumnyckel'])] for r in usable]
 assert missing<=sum(weights)+.011,('Insufficient remaining daily capacity',pid,month)
 allocation=[math.floor(units*w/sum(weights)) for w in weights] if weights else []
 if weights:
  remainder=units-sum(allocation)
  order=sorted(range(len(weights)),key=lambda i:units*weights[i]/sum(weights)-allocation[i],reverse=True)
  for i in order[:remainder]:allocation[i]+=1
 for i,(day,amount) in enumerate(zip(usable,allocation)):
  if not amount:continue
  j=contracts[(month+i)%len(contracts)]
  r=dict(UppdragID=j['UppdragID'],Datumnyckel=day['Datumnyckel'],Timmar=amount/100,Godkänd='Ja',Debiterbar='Ja')
  time.append(r);added.append(r)
 assert math.isclose(seed_hours[(pid,month)]+missing,max(target,seed_hours[(pid,month)]),abs_tol=.011),(pid,month)
# Generic multi-year contracts need a whole-contract time estimate; retaining
# the old 240-hour placeholder would incorrectly flag every completed timesheet.
whole_hours=defaultdict(float)
for r in time:whole_hours[r['UppdragID']]+=r['Timmar']
for contracts in ongoing_by_person.values():
 for j in contracts:j['PlaneradeTimmar']=max(240,math.ceil(whole_hours[j['UppdragID']]*1.10/8)*8)
write('Utförd tid komplettering',added);write('Tidrapporteringsprofiler',profiles)
write('Resurser',people);write('Uppdragsregister',jobs);write('Utförd tid',time);write('Uppdragsekonomi',rows);write('Arbetskapacitet',capacity);write('Planbokningar',plan);write('Planveckor',weeks)
write('Planinställning',[dict(Planläge='2026-09-30',Från='2026-10-05',Till='2026-11-29',SenasteUtfall='2026-09-30')])
write('Uppdragsområden',[dict(Områdesnyckel=2,Område='Teknisk service'),dict(Områdesnyckel=3,Område='Bemanning')])
write('Resursval',[dict(Resursgrupp='Alla')]+[dict(Resursgrupp=g) for _,g,_,_,_ in groups])
write('Uppdragsstatusval',[dict(Urval=x,Visningsordning=i) for i,x in enumerate(['Alla','Pågående','Avslutade','Behöver uppföljning'])])
write('Ej uppdragsfördelade kostnader',[dict(Datumnyckel=d,Områdesnyckel=a,Belopp=v) for (d,a),v in sorted(unassigned.items())])
checks=dict(capacity=sum(r['Kapacitet'] for r in plan),booked=sum(r['Bokat'] for r in plan),free=sum(r['Ledigt'] for r in plan),over=sum(r['Överbokat'] for r in plan),jobsR12=sum(20251001<=j['Slutförd']<=20260930 for j in jobs),hoursR12=sum(r['Timmar'] for r in time if 20251001<=r['Datumnyckel']<=20260930),financeRows=len(rows),resources=len(people),registryRows=len(jobs))
assert all(math.isclose(checks[k],v,abs_tol=1e-7) for k,v in zip(['capacity','booked','free','over'],[8000,6800,1280,80])),checks
assert checks['jobsR12']==960
assert len({(r['ResursID'],r['Datumnyckel']) for r in capacity})==len(capacity)
recon=defaultdict(lambda:[0,0])
for r in rows:
 a=resource[byid[r['UppdragID']]['ResursID']]['Områdesnyckel'];v=recon[(r['Datumnyckel'],a)];v[0]+=r['Intäkt'];v[1]+=r['DirektKostnad']
for key,value in unassigned.items():recon[key][1]+=value
assert dict(recon)==dict(source),'Assigned plus unassigned costs do not reconcile'
(BASE/'validation/assignment-data-check.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print(json.dumps(checks))
