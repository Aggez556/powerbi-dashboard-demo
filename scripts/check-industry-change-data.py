"""Independent monthly CSV reconciliation of the new chart's DAX results."""
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import csv,json,sys,math
root=Path(__file__).resolve().parents[1]/'powerbi-ledningsrapport'
def read(name):
 with (root/'data'/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
customers={int(r['Kundnyckel']):r['Kundbransch'] for r in read('Kunder.csv')}
dimension_matches_csv=True
if '--verify' in sys.argv:
 live=json.loads((root/'validation/industry-change-live.json').read_text(encoding='utf-8-sig'))['resultSets']
 imported={r['[CustomerKey]']:r['[Industry]'] for r in live[2]}
 dimension_matches_csv=imported==customers
 customers=imported  # Reconcile the chart against the imported dimension it actually uses.
sales=read('Försäljning.csv');totals=defaultdict(int);present=set()
for r in sales:
 key=(int(r['Datumnyckel'])//100,customers[int(r['Kundnyckel'])]);totals[key]+=int(r['Nettointäkt']);present.add(key)
latest=max(int(r['Datumnyckel'])//100 for r in sales)
industries=['Restaurang','Hotell','Catering','Kontor','Livsmedel']
scopes=[('R12',202510,202609,industries),('R12',202510,202609,['Hotell']),('R12',202510,202609,['Hotell','Restaurang']),('Helår',202501,202512,industries),('Helår',202401,202412,industries),('Månad',202609,202609,industries)]
queries=[];ranges=[];expected=[]
for case,(mode,start,end,selected) in enumerate(scopes):
 months=[year*100+month for year in range(start//100,end//100+1) for month in range(1,13) if start<=year*100+month<=min(end,latest)]
 for month in months:
  for industry in selected:
   a,b=totals[(month,industry)],totals[(month-100,industry)]
   if (month,industry) not in present and (month-100,industry) not in present:continue
   expected.append(dict(case=case,month=month,industry=industry,current=a,previous=b,delta=a-b,percent=(a-b)/b if b>0 else None))
 filters=[f'TREATAS({{"{mode}"}},\'Periodtyp\'[Periodtyp])',"TREATAS({"+','.join('"'+s+'"' for s in selected)+"},'Kunder'[Kundbransch])"]
 if mode=='R12':filters.append('TREATAS({"September 2026"},\'R12val\'[Period])')
 elif mode=='Helår':filters.append(f'TREATAS({{"{end//100}"}},\'Helårsval\'[Period])')
 else:filters.append('TREATAS({"September 2026"},\'Månadsval\'[Period])')
 common=','.join(filters)
 queries.append('CALCULATETABLE(ADDCOLUMNS(SUMMARIZECOLUMNS(\'Trendaxel\'[Månadsstart],\'Kunder\'[Kundbransch],"Current",[Bransch månadsförsäljning],"Previous",[Bransch månadsförsäljning föregående år],"Delta",[Bransch månadsförändring kronor],"Percent",[Bransch månadsförändring procent],"Mkr",[Bransch månadsförändring Mkr]),"Case",'+str(case)+'),'+common+')')
 ranges.append(f'CALCULATETABLE(ROW("Case",{case},"TopPercent",[Bransch axeltak procent],"BottomPercent",[Bransch axelgolv procent],"TopMoney",[Bransch axeltak Mkr],"BottomMoney",[Bransch axelgolv Mkr]),'+common+')')
query='EVALUATE\nUNION(\n'+',\n'.join(queries)+')\nORDER BY [Case],\'Trendaxel\'[Månadsstart],\'Kunder\'[Kundbransch]\n\nEVALUATE\nUNION(\n'+',\n'.join(ranges)+')\nORDER BY [Case]\n\nEVALUATE SELECTCOLUMNS(\'Kunder\',"CustomerKey",\'Kunder\'[Kundnyckel],"Industry",\'Kunder\'[Kundbransch])\nORDER BY [CustomerKey]\n'
(root/'validation/industry-change-check.dax').write_text(query,encoding='utf-8')
(root/'validation/industry-change-expected.json').write_text(json.dumps(expected,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if '--verify' not in sys.argv:print(f'Prepared {len(expected)} monthly/industry cases across {len(scopes)} period and industry selections.');sys.exit()
live=json.loads((root/'validation/industry-change-live.json').read_text(encoding='utf-8-sig'))['resultSets']
actual={}
for row in live[0]:
 raw=row['Trendaxel[Månadsstart]']
 if raw.startswith('/Date('):date=datetime.fromtimestamp(int(raw[6:raw.index(')')])/1000)
 else:date=datetime.fromisoformat(raw)
 actual[(row['[Case]'],date.year*100+date.month,row['Kunder[Kundbransch]'])]=row
assert len(actual)==len(expected),(len(actual),len(expected))
for e in expected:
 r=actual[(e['case'],e['month'],e['industry'])]
 for key,name in [('current','Current'),('previous','Previous'),('delta','Delta'),('percent','Percent')]:
  if e[key] is None:assert r['['+name+']'] is None,(e,r)
  else:assert r['['+name+']'] is not None and math.isclose(r['['+name+']'],e[key],abs_tol=.00001),(e,r,name)
 assert math.isclose(r['[Mkr]'],e['delta']/1000000,abs_tol=1e-8)
for r in live[1]:
 assert r['[BottomPercent]']<0<r['[TopPercent]'] and r['[BottomMoney]']<0<r['[TopMoney]']
 rows=[e for e in expected if e['case']==r['[Case]']]
 assert all(r['[BottomMoney]']<=e['delta']/1000000<=r['[TopMoney]'] for e in rows)
 assert all(e['percent'] is None or r['[BottomPercent]']<=e['percent']<=r['[TopPercent]'] for e in rows)
 for key,top,bottom,step in [('percent','TopPercent','BottomPercent',.05),('delta','TopMoney','BottomMoney',.1)]:
  values=[e[key]/(1000000 if key=='delta' else 1) for e in rows if e[key] is not None]
  low=min([0]+values);high=max([0]+values);padding=max(step,(high-low)*.08)
  assert math.isclose(r['['+top+']'],math.ceil(round((high+padding)/step,10))*step)
  assert math.isclose(r['['+bottom+']'],-math.ceil(round((-low+padding)/step,10))*step)
result=dict(status='passed',monthlyIndustryCases=len(expected),periodIndustrySelections=len(scopes),customerDimensionMatchesCSV=dimension_matches_csv,reference='Independent CSV fact aggregation using the current imported customer-industry mapping; existing imported data was not changed.',checks=['monthly same-month prior-year comparison','single-month view contains one month','single and multiple industry selections','raw signed kronor and percentage values','future/outside-period points excluded','independent dynamic bounds contain zero and all points with tight padding'])
(root/'validation/industry-change-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
