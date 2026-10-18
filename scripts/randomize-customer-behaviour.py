"""Seeded irregular customer behaviour, with unchanged monthly financial totals."""
from pathlib import Path
from collections import defaultdict
from decimal import Decimal
import csv,json,random,hashlib,calendar
BASE=Path(__file__).resolve().parents[1]/'powerbi-ledningsrapport';DATA=BASE/'data'
def read(n):
 with (DATA/(n+'.csv')).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(n,rows):
 p=DATA/(n+'.csv');t=p.with_suffix('.csv.tmp')
 with t.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 t.replace(p)
manifest=json.loads((DATA/'manifest.json').read_text(encoding='utf-8'))
if manifest.get('randomizedCustomerBehaviour'):print('Already randomized; unchanged.');raise SystemExit(0)
rng=random.Random(20261016)
sales=read('Försäljning');costs=read('Direkta kostnader');customers=read('Kunder')
for r in sales:
 for k in ['Fakturarad','Datumnyckel','Kundnyckel','Områdesnyckel','Artikelnyckel','Nettointäkt']:r[k]=int(r[k])
def finance(rows):
 d=defaultdict(lambda:[0,Decimal(0)])
 for r in rows:
  key=r['Datumnyckel']//100,r['Områdesnyckel'],r['Artikelnyckel'],r['Debitering']
  d[key][0]+=r['Nettointäkt'];d[key][1]+=Decimal(r['Debiterade timmar'])
 return dict(d)
before=finance(sales)
plan={}
for year,lo,hi,last in [(2024,221,240,12),(2025,241,260,12),(2026,261,275,9)]:
 for k in range(lo,hi+1):plan[k]=year*100+rng.choices(range(1,last+1),weights=[rng.uniform(.3,2.8) for _ in range(last)])[0]
 plan[lo]=year*100+1
for k,m in zip(range(276,281),[202502,202507,202511,202602,202608]):plan[k]=m
def dated(month,k,salt):
 y,m=divmod(month,100);day=1+int(hashlib.sha256(f'{month}:{k}:{salt}'.encode()).hexdigest()[:8],16)%calendar.monthrange(y,m)[1]
 return month*100+day
for r in sales:
 k=r['Kundnyckel'];month=r['Datumnyckel']//100
 if k in plan and month<plan[k]:r['Kundnyckel']=11+(k%170)
next_id=max(r['Fakturarad'] for r in sales)+1
added=[]
for k,start in plan.items():
 y,m=divmod(start,100)
 # A genuine start and occasional additional purchases, rather than a fixed
 # monthly acquisition amount repeated for every customer.
 for month in range(m,13 if y<2026 else 10):
  current=y*100+month
  has=any(r['Kundnyckel']==k and r['Datumnyckel']//100==current and r['Nettointäkt']>0 for r in sales)
  if has or (month!=m and rng.random()<.48):continue
  amount=int(rng.lognormvariate(10.05,.85));amount=max(1800,min(170000,amount))
  donors=sorted([r for r in sales if r['Datumnyckel']//100==current and 11<=r['Kundnyckel']<=200 and r['Nettointäkt']>6000],key=lambda r:rng.random())
  assert donors,(k,current,amount)
  donor=donors[0];amount=min(amount,donor['Nettointäkt']//3);new=dict(donor);hours=Decimal(donor['Debiterade timmar']);part=(hours*amount/donor['Nettointäkt']).quantize(Decimal('.0001'))
  donor['Nettointäkt']-=amount;donor['Debiterade timmar']=str(hours-part)
  new.update(Fakturarad=next_id,Kundnyckel=k,Nettointäkt=amount);next_id+=1;new['Debiterade timmar']=str(part);added.append(new)
sales.extend(added)
# Irregular basket sizes inside each existing finance bucket; positive rows stay
# positive so date/activity definitions remain grounded in real transactions.
buckets=defaultdict(list)
for r in sales:
 if r['Nettointäkt']>0:buckets[r['Datumnyckel']//100,r['Områdesnyckel'],r['Artikelnyckel'],r['Debitering']].append(r)
for rows in buckets.values():
 total=sum(r['Nettointäkt'] for r in rows);weights=[r['Nettointäkt']*rng.lognormvariate(0,.65) for r in rows];denom=sum(weights)
 amounts=[max(1,int(total*w/denom)) for w in weights];residual=total-sum(amounts)
 amounts[max(range(len(rows)),key=lambda i:amounts[i])]+=residual
 assert min(amounts)>0 and sum(amounts)==total
 for r,amount in zip(rows,amounts):r['Nettointäkt']=amount
for r in sales:
 r['Datumnyckel']=dated(r['Datumnyckel']//100,r['Kundnyckel'],r['Fakturarad'])
 if r['Områdesnyckel']==1:r['Ordernyckel']=(r['Datumnyckel']//100)*1000+r['Kundnyckel']
assert finance(sales)==before
first={}
for r in sales:
 if r['Nettointäkt']>0:first[r['Kundnyckel']]=min(first.get(r['Kundnyckel'],99999999),r['Datumnyckel'])
for k,start in plan.items():assert first[k]//100==start
industries=['Restaurang','Hotell','Catering','Kontor','Livsmedel']
for r in customers:
 k=int(r['Kundnyckel'])
 if r['Historiskt köp före data']!='Ja':r['Första köp']=str(first.get(k,0))
 if 221<=k<=300 and k not in [241,276]:r['Kundbransch']=rng.choices(industries,weights=[3,2,1,2,1])[0]
weights=defaultdict(lambda:defaultdict(int));cost_buckets=defaultdict(int)
for r in sales:weights[r['Datumnyckel']//100,r['Områdesnyckel'],r['Artikelnyckel']][r['Kundnyckel']]+=r['Nettointäkt']
for r in costs:cost_buckets[int(r['Datumnyckel'])//100,int(r['Områdesnyckel']),int(r['Artikelnyckel']),r['Kostnadstyp']]+=int(r['Belopp'])
new_costs=[]
for (month,area,article,kind),total in cost_buckets.items():
 pairs=[(k,v*rng.uniform(.75,1.25)) for k,v in sorted(weights[month,area,article].items()) if v>0]
 if 'fördelad' in kind.lower():pairs=[(0,1)]
 denom=sum(v for _,v in pairs);amounts=[int(total*v/denom) for _,v in pairs]
 for i in range(total-sum(amounts)):amounts[i%len(amounts)]+=1
 assert sum(amounts)==total
 for (k,_),amount in zip(pairs,amounts):
  if amount:new_costs.append(dict(Datumnyckel=dated(month,k,kind),Områdesnyckel=area,Artikelnyckel=article,Kostnadstyp=kind,Belopp=amount,Kundnyckel=k))
for name,rows in [('Försäljning',sales),('Direkta kostnader',new_costs),('Kunder',customers)]:
 write(name,rows);manifest['rows'][name]=len(rows);manifest['sha256'][name]=hashlib.sha256((DATA/(name+'.csv')).read_bytes()).hexdigest()
manifest['randomizedCustomerBehaviour']='scripts/randomize-customer-behaviour.py; seeded uneven customer starts, purchase sizes, dates, industries and margins. Monthly area/article/billing revenue and hours, monthly cost buckets unchanged. Industry and customer totals intentionally vary.'
(DATA/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=BASE/'validation/budget-source-manifest.json';m=json.loads(p.read_text(encoding='utf-8'))
for name in ['Försäljning','Direkta kostnader','Kunder']:m['sourceActualHashes'][name]=manifest['sha256'][name]
p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
summary=dict(status='passed',seed=20261016,preservedMonthlyFinanceBuckets=len(before),firstActivity=plan)
(BASE/'validation/customer-behaviour-randomization.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary))
