"""Vary demo hourly prices by month and margin development; preserve all financial fields."""
from pathlib import Path
from decimal import Decimal
from collections import defaultdict
import csv, json, hashlib

root=Path(__file__).resolve().parents[1]/'powerbi-ledningsrapport'
file=root/'data/Försäljning.csv'
with file.open(encoding='utf-8-sig',newline='') as f:
 reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
totals=defaultdict(lambda:[0,0]);timed=defaultdict(list)
for row in rows:
 key=(int(row['Datumnyckel'])//100,int(row['Områdesnyckel']))
 totals[key][0]+=int(row['Nettointäkt'])
 if key[1] in (2,3) and row['Debitering']=='Timdebiterat':timed[key].append(row)
with (root/'data/Direkta kostnader.csv').open(encoding='utf-8-sig',newline='') as f:
 for row in csv.DictReader(f):totals[(int(row['Datumnyckel'])//100,int(row['Områdesnyckel']))][1]+=int(row['Belopp'])
margins={k:(r-c)/r for k,(r,c) in totals.items() if r}
targets={};monthly=[]
for key,group in sorted(timed.items()):
 ym,area=key;month=ym%100;previous=(ym-100,area)
 if previous in targets:
  delta=margins[key]-margins[previous]
  growth=-min(.20,.005+abs(delta)*1.5) if delta<-.00001 else min(.20,.005+delta*1.5)
  target=targets[previous]*(1+growth)
 else:target=(780+month*2) if area==2 else (390+month*.5)
 targets[key]=target
 # Keep article/customer differences, without imposing a constant price on every row.
 raw=[]
 for row in group:
  noise=int(hashlib.sha256(('hourly-v1:'+row['Fakturarad']).encode()).hexdigest()[:8],16)/0xffffffff
  factor=Decimal(str(1+(int(row['Artikelnyckel'])%10-2)*.025+(noise-.5)*.08))
  raw.append(Decimal(row['Nettointäkt'])/(Decimal(str(target))*factor))
 income=sum(int(r['Nettointäkt']) for r in group)
 scale=(Decimal(income)/Decimal(str(target)))/sum(raw)
 for row,hours in zip(group,raw):row['Debiterade timmar']=str((hours*scale).quantize(Decimal('.0001')))
 actual=income/float(sum(Decimal(r['Debiterade timmar']) for r in group))
 assert abs(actual-target)<.01
 monthly.append(dict(month=ym,area=area,margin=margins[key],hourlyRate=actual))
# Changing hours must leave every other field, row identity and financial total intact.
before=[{k:v for k,v in r.items() if k!='Debiterade timmar'} for r in csv.DictReader(file.open(encoding='utf-8-sig'))]
assert before==[{k:v for k,v in r.items() if k!='Debiterade timmar'} for r in rows]
cases=[]
def summary(lo,hi,area):
 selected=[r for r in rows if lo<=int(r['Datumnyckel'])<=hi and int(r['Områdesnyckel'])==area and r['Debitering']=='Timdebiterat']
 return sum(int(r['Nettointäkt']) for r in selected)/float(sum(Decimal(r['Debiterade timmar']) for r in selected))
for area in (2,3):
 for year in (2024,2025):
  cases.append(dict(area=area,period=str(year),current=summary(year*10000+101,year*10000+1231,area),previous=summary((year-1)*10000+101,(year-1)*10000+1231,area)))
 cases.append(dict(area=area,period='R12 2026-09',current=summary(20251001,20260930,area),previous=summary(20241001,20250930,area)))
for key,target in targets.items():
 prior=(key[0]-100,key[1])
 if prior in targets:assert (target<targets[prior])==(margins[key]<margins[prior]-.00001)
for case in cases:
 year=int(case['period']) if case['period'].isdigit() else None
 lo,hi=(year*100+1,year*100+12) if year else (202510,202609)
 def margin_between(start,end):
  values=[v for (ym,area),v in totals.items() if area==case['area'] and start<=ym<=end]
  revenue=sum(v[0] for v in values)
  return (revenue-sum(v[1] for v in values))/revenue
 case['margin']=margin_between(lo,hi);case['previousMargin']=margin_between(lo-100,hi-100)
 assert (case['current']<case['previous'])==(case['margin']<case['previousMargin']-.00001),case
with file.open('w',encoding='utf-8',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
result=dict(status='passed',monthlyCases=len(monthly),financialFieldsUnchanged=True,monthly=monthly,periods=cases)
(root/'validation/hourly-rate-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(cases,indent=2))
