"""Independent CSV verification of Sales Analytics totals, rankings and markers."""
from pathlib import Path
from collections import defaultdict
from decimal import Decimal
import csv
import json

root = Path(__file__).resolve().parents[1] / 'powerbi-sales-finance'
def csv_rows(name):
    with (root / 'data' / (name + '.csv')).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))
def actual(name):
    return json.loads((root / 'validation' / name).read_text(encoding='utf-8-sig'))['rows']
facts = csv_rows('FactSales')
sellers = {int(r['SellerKey']): r['Seller'] for r in csv_rows('DimSeller')}
customers = {r['CustomerKey']: r['Country'] for r in csv_rows('DimCustomer')}
products = {r['ProductKey']: r['Category'] for r in csv_rows('DimProduct')}
periods = {'Full': set(range(1, 13)), 'October': {10}, 'SepOct': {9, 10}}
labels = {'Helår': 'Full', 'Oktober': 'October', 'September–oktober': 'SepOct'}
def close(value, expected, tolerance=Decimal('.01')):
    assert abs(Decimal(str(value)) - Decimal(expected)) < tolerance, (value, expected)
for result in actual('desktop-sales-analysis.json'):
    months = periods[labels[result['[Period]']]]
    rows = [r for r in facts if r['DateKey'][:4] == '2025' and int(r['DateKey'][4:6]) in months]
    revenue = sum(Decimal(r['Revenue']) for r in rows)
    profit = revenue - sum(Decimal(r['Cost']) for r in rows)
    active = len({r['SellerKey'] for r in rows})
    orders = len({r['OrderKey'] for r in rows})
    totals = defaultdict(Decimal)
    for r in rows:
        totals[int(r['SellerKey'])] += Decimal(r['Revenue'])
    close(result['[Omsättning]'], revenue)
    close(result['[Bruttovinst]'], profit)
    assert result['[Aktiva]'] == active and result['[Leveranser]'] == orders
    close(result['[Ordervärde]'], revenue / orders)
    close(result['[Omsättning per säljare]'], revenue / active)
    close(result['[Topp 5]'], sum(sorted(totals.values(), reverse=True)[:5]) / revenue, Decimal('.00000001'))
for result in actual('desktop-sales-ranking.json'):
    months = periods[result['[Period]']]
    totals, prior = defaultdict(Decimal), defaultdict(Decimal)
    for r in facts:
        if int(r['DateKey'][4:6]) not in months:
            continue
        target = totals if r['DateKey'][:4] == '2025' else prior
        target[int(r['SellerKey'])] += Decimal(r['Revenue'])
    ranked = sorted(totals, key=lambda k: (-totals[k], k))
    key = ranked[result['[Rank]'] - 1]
    assert result['[Namn]'] == sellers[key]
    close(result['[Belopp]'], totals[key])
    close(result['[Tillväxt]'], (totals[key] - prior[key]) / prior[key], Decimal('.00000001'))
for mode in ['land', 'kategori']:
    rows = actual('desktop-sales-trends-' + mode + '.json')
    source = defaultdict(lambda: defaultdict(Decimal))
    for r in facts:
        if r['DateKey'][:4] != '2025':
            continue
        group = customers[r['CustomerKey']] if mode == 'land' else products[r['ProductKey']]
        if mode == 'kategori' and group not in {'Elektronik', 'Hem och kök'}:
            group = 'Övrigt'
        source[group][int(r['DateKey'][4:6])] += Decimal(r['Revenue'])
    assert len(rows) == len(source) * 12
    for result in rows:
        group, month = result['[Group]'], result['[Month]']
        expected = source[group][month]
        close(result['[Value]'], expected)
        lo, hi = min(source[group].values()), max(source[group].values())
        assert (result['[Min]'] is not None) == (expected == lo), (mode, group, month, 'min')
        assert (result['[Max]'] is not None) == (expected == hi), (mode, group, month, 'max')
print('Passed 3 period totals, 21 seller ranks, 84 monthly group values and all min/max markers.')
