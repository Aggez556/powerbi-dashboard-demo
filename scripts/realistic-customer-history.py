"""Broaden demo lifecycle history, retaining monthly finance and reference cohorts."""
from pathlib import Path
from collections import defaultdict
from decimal import Decimal
import csv,json,hashlib,calendar

ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'powerbi-ledningsrapport';DATA=BASE/'data'
def read(name):
 with (DATA/(name+'.csv')).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(name,rows):
 p=DATA/(name+'.csv');temp=p.with_suffix('.csv.tmp')
 with temp.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 temp.replace(p)
manifest=json.loads((DATA/'manifest.json').read_text(encoding='utf-8'))
if manifest.get('realisticCustomerHistory'):
 print('Customer history already enriched; no changes.');raise SystemExit(0)
sales=read('Försäljning');customers=read('Kunder');costs=read('Direkta kostnader')
for r in sales:
 for k in ['Fakturarad','Datumnyckel','Kundnyckel','Områdesnyckel','Artikelnyckel','Nettointäkt']:r[k]=int(r[k])
def bucket(r):return (r['Datumnyckel']//100,r['Områdesnyckel'],r['Artikelnyckel'],r['Debitering'],(r['Kundnyckel']-1)%5)
def financial(rows):
 out=defaultdict(lambda:[0,Decimal(0)])
 for r in rows:
  b=out[bucket(r)];b[0]+=r['Nettointäkt'];b[1]+=Decimal(r['Debiterade timmar'])
 return dict(out)
before=financial(sales)
reference=defaultdict(int)
for r in sales:
 if 20241001<=r['Datumnyckel']<=20250930:reference[r['Kundnyckel']]+=r['Nettointäkt']
next_id=max(r['Fakturarad'] for r in sales)+1
added=[]
def transfer(row,customer,amount):
 global next_id
 assert 0<amount<=row['Nettointäkt']
 if amount==row['Nettointäkt']:row['Kundnyckel']=customer;return
 new=dict(row);new['Fakturarad']=next_id;next_id+=1
 hours=Decimal(row['Debiterade timmar']);part=(hours*Decimal(amount)/Decimal(row['Nettointäkt'])).quantize(Decimal('.0001'))
 new.update(Kundnyckel=customer,Nettointäkt=amount)
 new['Debiterade timmar']=str(part)
 row['Nettointäkt']-=amount;row['Debiterade timmar']=str(hours-part)
 added.append(new)

# Move each lost client's late purchases earlier, exchanging equal revenue with
# retained clients in identical area/article/billing/industry buckets.
# Their annual reference revenue and each month's financial total remain exact.
for customer in range(1,11):
 cutoff=202500+min(9,customer)
 late=[r for r in sales if r['Kundnyckel']==customer and cutoff<r['Datumnyckel']//100<=202509 and r['Nettointäkt']>0]
 early=defaultdict(list)
 for r in sales:
  if 202410<=r['Datumnyckel']//100<=cutoff and 11<=r['Kundnyckel']<=240 and r['Nettointäkt']>0:
   early[bucket(r)[1:]].append(r)
 for row in late:
  old=row['Nettointäkt'];remaining=old;recipient=None
  for donor in early[bucket(row)[1:]]:
   if donor['Kundnyckel']==customer:continue
   # Leave a positive transaction so retained clients remain active.
   amount=min(remaining,max(0,donor['Nettointäkt']-1))
   if amount:
    recipient=donor['Kundnyckel'];transfer(donor,customer,amount);transfer(row,recipient,amount);remaining-=amount
   if not remaining:break
  assert remaining==0,(customer,bucket(row),remaining)
 # Make the new early transactions available for subsequent source handling.
 sales.extend(added);added=[]

# Previously unused customers form genuine historic lapsed cohorts, spread over
# months. Matching industry IDs keeps every industry subtotal unchanged.
for row in sales:
 k=row['Kundnyckel'];month=row['Datumnyckel']//100
 if 81<=k<=95 and 202301<=month<=202400+2+(k-81)%8:
  row['Kundnyckel']=k+200
 elif 101<=k<=105 and 202301<=month<=202303+(k-101)*2:
  row['Kundnyckel']=k+195

def dated(key,customer):
 month=int(key)//100;y,m=divmod(month,100)
 day=1+int(hashlib.sha256(f'{month}:{customer}:purchase'.encode()).hexdigest()[:8],16)%calendar.monthrange(y,m)[1]
 return month*100+day
for row in sales:row['Datumnyckel']=dated(row['Datumnyckel'],row['Kundnyckel'])
assert financial(sales)==before,'Monthly finance, hours or industry totals changed'
after_reference=defaultdict(int)
for r in sales:
 if 20241001<=r['Datumnyckel']<=20250930:after_reference[r['Kundnyckel']]+=r['Nettointäkt']
assert dict(after_reference)==dict(reference),'Reference customer revenues changed'

# Reattribute existing monthly cost buckets to actual purchasing customers.
# Unallocated delivery personnel remains explicitly unallocated.
weights=defaultdict(lambda:defaultdict(int))
for r in sales:weights[(r['Datumnyckel']//100,r['Områdesnyckel'],r['Artikelnyckel'])][r['Kundnyckel']]+=r['Nettointäkt']
totals=defaultdict(int)
for r in costs:totals[(int(r['Datumnyckel'])//100,int(r['Områdesnyckel']),int(r['Artikelnyckel']),r['Kostnadstyp'])]+=int(r['Belopp'])
out=[]
for (month,area,article,kind),total in totals.items():
 pairs=[(k,v) for k,v in sorted(weights[month,area,article].items()) if v>0]
 if 'fördelad' in kind.lower():pairs=[(0,1)]
 assert pairs
 denom=sum(v for _,v in pairs);amounts=[total*v//denom for _,v in pairs]
 for i in range(total-sum(amounts)):amounts[i%len(amounts)]+=1
 for (customer,_),amount in zip(pairs,amounts):
  if amount:out.append(dict(Datumnyckel=dated(month*100+15,customer) if customer else month*100+15,Områdesnyckel=area,Kostnadstyp=kind,Belopp=amount,Artikelnyckel=article,Kundnyckel=customer))
check=defaultdict(int)
for r in out:check[(r['Datumnyckel']//100,r['Områdesnyckel'],r['Artikelnyckel'],r['Kostnadstyp'])]+=r['Belopp']
assert dict(check)==dict(totals)
first={}
for r in sales:
 if r['Nettointäkt']>0:first[r['Kundnyckel']]=min(first.get(r['Kundnyckel'],99999999),r['Datumnyckel'])
for r in customers:
 k=int(r['Kundnyckel'])
 if r['Historiskt köp före data']!='Ja':r['Första köp']=str(first.get(k,0))

def cohort(lo,hi,plo,phi):
 active={r['Kundnyckel'] for r in sales if lo<=r['Datumnyckel']<=hi and r['Nettointäkt']>0}
 previous={r['Kundnyckel'] for r in sales if plo<=r['Datumnyckel']<=phi and r['Nettointäkt']>0}
 lost=previous-active
 last={k:max(r['Datumnyckel'] for r in sales if r['Kundnyckel']==k and r['Nettointäkt']>0 and r['Datumnyckel']<=hi) for k in lost}
 return dict(active=len(active),previous=len(previous),lost=len(lost),distinctLastPurchaseDates=len(set(last.values())),lastPurchases=last)
cases={'2024':cohort(20240101,20241231,20230101,20231231),'2025':cohort(20250101,20251231,20240101,20241231),'R12 September 2026':cohort(20251001,20260930,20241001,20250930)}
assert cases['2024']['lost']>=5 and cases['2025']['lost']>=15
assert cases['R12 September 2026']['lost']==10
assert all(v['distinctLastPurchaseDates']>1 for v in cases.values())
for name,rows in [('Försäljning',sales),('Direkta kostnader',out),('Kunder',customers)]:
 write(name,rows);manifest['rows'][name]=len(rows);manifest['sha256'][name]=hashlib.sha256((DATA/(name+'.csv')).read_bytes()).hexdigest()
manifest['realisticCustomerHistory']='scripts/realistic-customer-history.py; varied purchase dates and historical lapsed cohorts; exact monthly financial/industry/hour totals and reference customer revenues preserved.'
(DATA/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
budget_manifest=BASE/'validation/budget-source-manifest.json'
if budget_manifest.exists():
 m=json.loads(budget_manifest.read_text(encoding='utf-8'))
 for name in ['Försäljning','Direkta kostnader','Kunder']:m['sourceActualHashes'][name]=manifest['sha256'][name]
 m['customerHistoryUpdate']='Customer/date redistribution; independently checked monthly financial totals unchanged. See customer-history-realism.json.'
 budget_manifest.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
result=dict(status='passed',monthlyFinancialBucketsPreserved=len(before),referenceCustomerRevenuesPreserved=True,cases=cases)
(BASE/'validation/customer-history-realism.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
