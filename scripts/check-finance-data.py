"""Compare live finance DAX with independent Decimal sums of the source CSV."""
from pathlib import Path
from decimal import Decimal
import csv
import json
from collections import defaultdict

root = Path(__file__).resolve().parents[1] / 'powerbi-sales-finance'
facts = list(csv.DictReader((root / 'data/FactSales.csv').open(encoding='utf-8-sig')))
sellers = {r['SellerKey']: r['Team'] for r in csv.DictReader((root / 'data/DimSeller.csv').open(encoding='utf-8-sig'))}
products = {r['ProductKey']: r['Category'] for r in csv.DictReader((root / 'data/DimProduct.csv').open(encoding='utf-8-sig'))}
actual = json.loads((root / 'validation/desktop-finance.json').read_text(encoding='utf-8-sig'))['rows']
cases = {'Helår': set(range(1, 13)), 'Oktober': {10}, 'September–oktober': {9, 10}}
checks = []
for result in actual:
    months = cases[result['[Period]']]
    rows = [r for r in facts if r['DateKey'][:4] == '2025' and int(r['DateKey'][4:6]) in months]
    revenue = sum(Decimal(r['Revenue']) for r in rows)
    cost = sum(Decimal(r['Cost']) for r in rows)
    quantity = sum(int(r['Quantity']) for r in rows)
    expected = {'[Vinst]': revenue-cost, '[Kostnad]': cost, '[Omsättning]': revenue, '[Enheter]': Decimal(quantity), '[Marginal]': (revenue-cost)/revenue, '[Omsättning per enhet]': revenue/quantity, '[Vinst per enhet]': (revenue-cost)/quantity}
    for field, value in expected.items():
        tolerance = Decimal('0.0001') if 'per enhet' in field else Decimal('0.00000001')
        error = abs(Decimal(str(result[field]))-value)
        assert error <= tolerance, (result['[Period]'], field, error)
    checks.append({'period': result['[Period]'], 'fields': len(expected), 'passed': True})

monthly = json.loads((root / 'validation/desktop-finance-multiples.json').read_text(encoding='utf-8-sig'))['rows']
sums = defaultdict(Decimal)
for r in facts:
    if r['DateKey'][:4] != '2025':
        continue
    month = int(r['DateKey'][4:6])
    profit = Decimal(r['Revenue'])-Decimal(r['Cost'])
    sums[('Säljteam', sellers[r['SellerKey']], month)] += profit
    sums[('Kategori', products[r['ProductKey']], month)] += profit
for result in monthly:
    kind, name, month = result['Finansaxel[Typ]'], result['Finansaxel[Namn]'], result['Datum[Månadsnummer]']
    value = sums[(kind, name, month)]/Decimal(1000000)
    mean = sum(sums[(kind, name, m)] for m in range(1, 13))/Decimal(12000000)
    assert abs(Decimal(str(result['[Vinst]']))-value) <= Decimal('0.0001')
    assert abs(Decimal(str(result['[Medel]']))-mean) <= Decimal('0.0001')
checks.append({'monthlyGroups': len(monthly), 'passed': True, 'toleranceMillions': '0.0001 (existing currency-typed million measures)'})
(root / 'validation/finance-comparison.json').write_text(json.dumps({'status': 'passed', 'source': 'Independent CSV Decimal sums versus live Desktop DAX', 'checks': checks}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(f'Passed {len(actual)} period totals and {len(monthly)} monthly team/category groups.')
