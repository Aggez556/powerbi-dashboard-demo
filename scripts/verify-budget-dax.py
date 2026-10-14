from pathlib import Path
import json,math
root=Path(__file__).resolve().parents[1]
def read(name):return json.loads((root/'powerbi/validation'/name).read_text(encoding='utf-8-sig'))
actual=read('budget-dax-result.json')
expected=read('data-and-measure-expectations.json')['annual']
rows=actual['rows']
def total(label,measure):
    values=[r[f'[{measure}]'] for r in rows if r['Resultatrader[Rad]'].strip()==label]
    assert len(values)==12,(label,len(values))
    return sum(values)
sales=total('Nettoomsättning','Actuals')
cost=-total('Varu- och underkonsultkostnader','Actuals')
budget=total('Nettoomsättning','Budget')
assert math.isclose(sales,expected['2025']['Omsättning'],abs_tol=0.01)
assert math.isclose(cost,expected['2025']['Kostnad'],abs_tol=0.01)
assert math.isclose(budget,expected['2024']['Omsättning']*1.05*1.03,abs_tol=0.01)
assert math.isclose(total('Summa intäkter','Actuals'),sales*1.04,abs_tol=0.01)
assert math.isclose(total('Rörelseresultat','Actuals'),sales*.81-cost,abs_tol=0.01)
live=read('budget-live-fix.json');assert all(not m['error'] for m in live['measures'])
result={'status':'passed','source':'Actual Desktop DAX compared with independent CSV/SQL expectations','rowCount':len(rows),'annualActualRevenue':sales,'annualActualCost':cost,'annualBudgetRevenue':budget,'budgetMeasuresReady':True,'visualRendering':'not verified'}
(root/'powerbi/validation/budget-dax-checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
