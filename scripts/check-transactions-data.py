import csv,json,math
from decimal import Decimal
from pathlib import Path
p=Path('powerbi-sales-finance')
def read(n):
 with (p/'data'/f'{n}.csv').open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
facts=read('FactSales');customers={r['CustomerKey']:r for r in read('DimCustomer')};products={r['ProductKey']:r for r in read('DimProduct')}
live=json.loads((p/'validation/desktop-transaction-periods.json').read_text(encoding='utf-8-sig'))['rows']
for r in live:
 name=r['[Kontext]']; selected=[]
 for f in facts:
  if not f['DateKey'].startswith('2025'):continue
  m=int(f['DateKey'][4:6])
  if name in ('Oktober','Marknad') and m!=10:continue
  if name=='Flera månader' and m not in (1,2,3):continue
  if name=='Marknad' and customers[f['CustomerKey']]['Country']!='Norge':continue
  if name=='Produktsökning' and 'hantel' not in products[f['ProductKey']]['ProductName'].lower():continue
  if name=='Tomt':continue
  selected.append(f)
 revenue=sum(Decimal(f['Revenue']) for f in selected);cost=sum(Decimal(f['Cost']) for f in selected)
 expected={'Rader':len(selected),'Omsättning':revenue,'Kostnad':cost,'Bruttovinst':revenue-cost,'Antal':sum(int(f['Quantity']) for f in selected),'Leveranser':len(set(f['OrderKey'] for f in selected))}
 if selected:expected['Marginal']=(revenue-cost)/revenue
 for k,v in expected.items():assert math.isclose(float(v),float(r[f'[{k}]'] or 0),rel_tol=1e-8,abs_tol=1e-5),(name,k,v,r)
print('Passed: six filter contexts independently checked against CSV; weighted margins and distinct-order deliveries match.')
