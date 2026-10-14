"""Check Desktop's actual row-level query against independent CSV joins."""
import csv,json,math,re
from datetime import datetime
from decimal import Decimal
from pathlib import Path
root=Path(__file__).resolve().parents[1]/'powerbi-sales-finance'
def rows(name):
    with (root/'data'/f'{name}.csv').open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
facts={int(r['SalesLineKey']):r for r in rows('FactSales')}
sellers={r['SellerKey']:r for r in rows('DimSeller')}
products={r['ProductKey']:r for r in rows('DimProduct')}
customers={r['CustomerKey']:r for r in rows('DimCustomer')}
live=json.loads((root/'validation/desktop-transactions.json').read_text(encoding='utf-8-sig'))['rows']
assert len(live)==5
for r in live:
    f=facts[r['Försäljning[Radnyckel]']]
    assert r['Försäljning[Ordernyckel]']==int(f['OrderKey'])
    seller=sellers[f['SellerKey']];product=products[f['ProductKey']];customer=customers[f['CustomerKey']]
    for key,value in [('Säljare[Säljare]',seller['Seller']),('Säljare[Team]',seller['Team']),('Kunder[Land]',customer['Country']),('Produkter[Kategori]',product['Category']),('Produkter[Produkt]',product['ProductName'])]:assert r[key]==value,(key,value,r[key])
    epoch=int(re.search(r'Date\((-?\d+)\)',r['Datum[Datum]']).group(1))
    assert epoch==round(datetime.strptime(f['DateKey'],'%Y%m%d').timestamp()*1000)
    revenue=Decimal(f['Revenue']);cost=Decimal(f['Cost'])
    expected={'[Enhetspris]':Decimal(f['UnitPrice']),'[Antal]':int(f['Quantity']),'[Varukostnad]':cost,'[Omsättning]':revenue,'[Bruttovinst]':revenue-cost,'[Marginal]':(revenue-cost)/revenue}
    for key,value in expected.items():assert math.isclose(float(value),float(r[key]),rel_tol=1e-8,abs_tol=1e-5),(key,value,r[key])
out={'status':'passed','source':'Actual read-only Desktop DAX versus CSV joins and Decimal arithmetic','rowsChecked':len(live),'scope':'Current Desktop model; latest transaction PBIR visual review still pending'}
(root/'validation/transaction-comparison.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print('Five actual transaction rows: dates, keys, dimension joins, unit prices, quantities, cost, revenue, profit and margins passed.')
