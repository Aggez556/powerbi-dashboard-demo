from pathlib import Path
import csv,json,math
base=Path(__file__).resolve().parents[1]/'powerbi-ledningsrapport'
axis={r['Månad']:int(r['Ordning']) for r in csv.DictReader((base/'data/Trendaxel.csv').open(encoding='utf-8-sig'))}
expected=next(r['result'] for r in json.loads((base/'validation/customer-independent-checks.json').read_text(encoding='utf-8'))['scenarios'] if r['mode']=='Helår 2025' and r['industry']=='Alla')
live=json.loads((base/'validation/customer-acquisition-live-result.json').read_text(encoding='utf-8-sig'))['resultSets'][0]
actual={}
for r in live:
 month=axis[r['Trendaxel[Månad]']];group=r['Kundgrupper[Kundgrupp]'];index=['Befintliga','Helt nya','Återaktiverade'].index(group)
 assert math.isclose(r['[Mkr]']*1000000,expected['monthly'][str(month)][index],abs_tol=.0001)
 actual[month,index]=r['[Mkr]']
assert all(actual.get((202500+m,1),0)>0 for m in range(1,13))
assert actual[202502,2]>0 and actual[202506,2]>0
report=dict(status='passed',source='Actual refreshed Desktop DAX versus independent transaction cohorts',newCustomerRevenueMonths2025=12,reactivatedCustomerRevenueMonths2025=sum(actual.get((202500+m,2),0)>0 for m in range(1,13)),monthlyCellsVerified=len(live),activeCustomers2025=expected['active'],lostCustomers2025=expected['lost'])
(base/'validation/customer-acquisition-live-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
