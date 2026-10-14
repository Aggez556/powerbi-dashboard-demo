"""Append deterministic Jan-Oct 2026 dummy orders; preserve historical rows."""
from pathlib import Path
import csv, datetime as dt, hashlib, json, random
from decimal import Decimal

root = Path(__file__).resolve().parents[1] / 'powerbi-sales-finance'
data = root / 'data'
def load(name):
    with (data / (name + '.csv')).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))
def save(name, rows):
    with (data / (name + '.csv')).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0]); writer.writeheader(); writer.writerows(rows)

dates = [r for r in load('DimDate') if int(r['Year']) < 2026]
for offset in range(304):
    date = dt.date(2026, 1, 1) + dt.timedelta(days=offset)
    template = next(r for r in dates if r['Date'] == date.replace(year=2025).isoformat())
    row = dict(template, DateKey=date.strftime('%Y%m%d'), Date=date.isoformat(), Year='2026',
               YearMonth=date.strftime('%Y-%m'), YearMonthSort=date.strftime('%Y%m'))
    dates.append(row)
save('DimDate', dates)
facts = [r for r in load('FactSales') if not r['DateKey'].startswith('2026')]
old_rows = len(facts)
line = max(int(r['SalesLineKey']) for r in facts)
order = max(int(r['OrderKey']) for r in facts)
orders = {}
rng = random.Random(20261031)
for previous in list(facts):
    if not previous['DateKey'].startswith('2025') or int(previous['DateKey'][4:6]) > 10:
        continue
    row = dict(previous)
    old_order = previous['OrderKey']
    if old_order not in orders:
        order += 1; orders[old_order] = order
    line += 1
    quantity = max(1, round(int(previous['Quantity']) * rng.uniform(.95, 1.35)))
    row.update(SalesLineKey=str(line), OrderKey=str(orders[old_order]), DateKey='2026'+previous['DateKey'][4:], Quantity=str(quantity),
               Revenue=f"{Decimal(previous['UnitPrice']) * quantity:.2f}", Cost=f"{Decimal(previous['UnitCost']) * quantity:.2f}")
    facts.append(row)
save('FactSales', facts)
manifest = json.loads((data / 'manifest.json').read_text(encoding='utf-8-sig'))
manifest['coverage'] = {'start': '2024-01-01', 'end': '2026-10-31', 'partialYear': 2026}
manifest['extension'] = {'generator': 'scripts/extend-sales-finance-2026.py', 'seed': 20261031, 'addedRows': len(facts)-old_rows, 'addedOrders': len(orders)}
manifest['assumptions'] = [s for s in manifest['assumptions'] if 'Full calendar years' not in s]
manifest['assumptions'].append('Full years 2024-2025; 2026 through October 31. Historical rows preserved; 2026 is fictional.')
for p in data.glob('*.csv'):
    with p.open(encoding='utf-8-sig', newline='') as f: manifest['rows'][p.stem] = sum(1 for _ in csv.DictReader(f))
    manifest['sha256'][p.stem] = hashlib.sha256(p.read_bytes()).hexdigest()
(data / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(manifest['extension']))
