"""Independent verification of the disconnected finance-axis TREATAS totals."""
import csv,json,math
from decimal import Decimal
from pathlib import Path
root=Path(__file__).resolve().parents[1]/'powerbi-sales-finance'
def rows(name):
    with (root/'data'/f'{name}.csv').open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
products={r['ProductKey']:r['Category'] for r in rows('DimProduct')}
sellers={r['SellerKey']:r['Team'] for r in rows('DimSeller')}
totals={}
for row in rows('FactSales'):
    for kind,name in [('Kategori',products[row['ProductKey']]),('Säljteam',sellers[row['SellerKey']])]:
        key=(int(row['DateKey'][:4]),kind,name)
        totals[key]=totals.get(key,Decimal(0))+Decimal(row['Revenue'])-Decimal(row['Cost'])
assert len(totals)==16
for year in (2024,2025):
    assert sum(v for (y,t,n),v in totals.items() if y==year and t=='Kategori')==sum(v for (y,t,n),v in totals.items() if y==year and t=='Säljteam')
output={'status':'passed','source':'Independent CSV product/category and seller/team joins','rows':[{'year':y,'type':t,'name':n,'profit':float(v)} for (y,t,n),v in sorted(totals.items())]}
actual=root/'validation/desktop-finance-axis.json'
if actual.exists():
    live=json.loads(actual.read_text(encoding='utf-8-sig'))['rows'];assert len(live)==16
    for row in live:
        key=(row['Datum[År]'],row['Finansaxel[Typ]'],row['Finansaxel[Namn]'])
        assert math.isclose(float(totals[key]),row['[Bruttovinst analys]'],rel_tol=1e-8,abs_tol=1e-5)
    output['desktopComparison']='passed'
(root/'validation/finance-axis-expectations.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f"Finance axis: 16 independent totals passed; Desktop: {output.get('desktopComparison','pending')}.")
