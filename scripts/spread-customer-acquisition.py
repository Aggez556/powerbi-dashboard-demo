"""Spread actual demo acquisition/reactivation events across calendar years."""
from pathlib import Path
from collections import defaultdict
from decimal import Decimal
import csv,json,hashlib,calendar

BASE=Path(__file__).resolve().parents[1]/'powerbi-ledningsrapport';DATA=BASE/'data'
def read(name):
 with (DATA/(name+'.csv')).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(name,rows):
 p=DATA/(name+'.csv');temp=p.with_suffix('.csv.tmp')
 with temp.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 temp.replace(p)
manifest=json.loads((DATA/'manifest.json').read_text(encoding='utf-8'))
if manifest.get('spreadCustomerAcquisition'):
 print('Acquisition already spread; no changes.');raise SystemExit(0)
sales=read('Försäljning');costs=read('Direkta kostnader');customers=read('Kunder')
for r in sales:
 for k in ['Fakturarad','Datumnyckel','Kundnyckel','Områdesnyckel','Artikelnyckel','Nettointäkt']:r[k]=int(r[k])
def totals(rows):
 out=defaultdict(lambda:[0,Decimal(0)])
 for r in rows:
  key=(r['Datumnyckel']//100,r['Områdesnyckel'],r['Artikelnyckel'],r['Debitering'],(r['Kundnyckel']-1)%5)
  out[key][0]+=r['Nettointäkt'];out[key][1]+=Decimal(r['Debiterade timmar'])
 return dict(out)
before=totals(sales)
plan={**{221+i:202400+1+i*12//20 for i in range(20)},**{241+i:202500+1+i*12//20 for i in range(20)},**{261+i:202600+1+i*9//15 for i in range(15)},**dict(zip(range(276,281),[202502,202506,202510,202603,202607]))}
original={k:min(r['Datumnyckel']//100 for r in sales if r['Kundnyckel']==k and r['Nettointäkt']>0) for k in plan}
def dated(month,k):
 y,m=divmod(month,100)
 return month*100+1+int(hashlib.sha256(f'{month}:{k}:purchase'.encode()).hexdigest()[:8],16)%calendar.monthrange(y,m)[1]
# Transactions before a planned start belong to a retained customer of the same
# industry; they cannot make the planned new customer active prematurely.
for r in sales:
 k=r['Kundnyckel'];month=r['Datumnyckel']//100
 if k in plan and month<plan[k]:
  recipient=11+(k-1)%5
  r['Kundnyckel']=recipient;r['Datumnyckel']=dated(month,recipient)

next_id=max(r['Fakturarad'] for r in sales)+1;added=[]
for k,start in plan.items():
 year,month=divmod(start,100)
 while year*100+month<=max(start,original[k]-1):
  current=year*100+month
  remaining=18000+(k*971+current*37)%27000
  donors=sorted([r for r in sales if r['Datumnyckel']//100==current and 11<=r['Kundnyckel']<=200 and (r['Kundnyckel']-k)%5==0 and r['Nettointäkt']>0],key=lambda r:r['Nettointäkt'],reverse=True)
  for r in donors:
   amount=min(remaining,r['Nettointäkt']//3)
   if not amount:continue
   clone=dict(r);hours=Decimal(r['Debiterade timmar']);part=(hours*amount/r['Nettointäkt']).quantize(Decimal('.0001'))
   clone.update(Fakturarad=next_id,Kundnyckel=k,Nettointäkt=amount,Datumnyckel=dated(current,k));next_id+=1
   clone['Debiterade timmar']=str(part);r['Debiterade timmar']=str(hours-part);r['Nettointäkt']-=amount
   added.append(clone);remaining-=amount
   if not remaining:break
  assert remaining==0,(k,current,remaining)
  month+=1
  if month==13:year+=1;month=1
sales.extend(added)
for r in sales:
 if r['Områdesnyckel']==1:r['Ordernyckel']=(r['Datumnyckel']//100)*1000+r['Kundnyckel']
assert totals(sales)==before
first={}
for r in sales:
 if r['Nettointäkt']>0:first[r['Kundnyckel']]=min(first.get(r['Kundnyckel'],99999999),r['Datumnyckel'])
for k,start in plan.items():assert first[k]//100==start,(k,start,first[k])
for r in customers:
 if r['Historiskt köp före data']!='Ja':r['Första köp']=str(first.get(int(r['Kundnyckel']),0))

weights=defaultdict(lambda:defaultdict(int));buckets=defaultdict(int)
for r in sales:weights[r['Datumnyckel']//100,r['Områdesnyckel'],r['Artikelnyckel']][r['Kundnyckel']]+=r['Nettointäkt']
for r in costs:buckets[int(r['Datumnyckel'])//100,int(r['Områdesnyckel']),int(r['Artikelnyckel']),r['Kostnadstyp']]+=int(r['Belopp'])
new_costs=[]
for (month,area,article,kind),total in buckets.items():
 pairs=[(k,v) for k,v in sorted(weights[month,area,article].items()) if v>0]
 if 'fördelad' in kind.lower():pairs=[(0,1)]
 assert pairs
 denom=sum(v for _,v in pairs);amounts=[total*v//denom for _,v in pairs]
 for i in range(total-sum(amounts)):amounts[i%len(amounts)]+=1
 for (k,_),amount in zip(pairs,amounts):
  if amount:new_costs.append(dict(Datumnyckel=dated(month,k) if k else month*100+15,Områdesnyckel=area,Artikelnyckel=article,Kostnadstyp=kind,Belopp=amount,Kundnyckel=k))
check=defaultdict(int)
for r in new_costs:check[r['Datumnyckel']//100,r['Områdesnyckel'],r['Artikelnyckel'],r['Kostnadstyp']]+=r['Belopp']
assert dict(check)==dict(buckets)
for name,rows in [('Försäljning',sales),('Direkta kostnader',new_costs),('Kunder',customers)]:
 write(name,rows);manifest['rows'][name]=len(rows);manifest['sha256'][name]=hashlib.sha256((DATA/(name+'.csv')).read_bytes()).hexdigest()
manifest['spreadCustomerAcquisition']='scripts/spread-customer-acquisition.py; customer starts spread over 2024-2026, actual reactivation events; monthly finance unchanged, period cohort totals intentionally recalculated.'
(DATA/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=BASE/'validation/budget-source-manifest.json';m=json.loads(p.read_text(encoding='utf-8'))
for name in ['Försäljning','Direkta kostnader','Kunder']:m['sourceActualHashes'][name]=manifest['sha256'][name]
p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
summary=dict(status='passed',monthlyFinanceAndHourBucketsPreserved=len(before),plannedFirstActivity=plan,referenceCohortsIntentionallyChanged=True)
(BASE/'validation/customer-acquisition-spread.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary))
