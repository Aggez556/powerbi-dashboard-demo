"""Independent CSV totals, integrity checks, and comparison with Desktop DAX."""
import csv, datetime, hashlib, json, math
from decimal import Decimal
from pathlib import Path

root = Path(__file__).resolve().parents[1] / 'powerbi-sales-finance'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
manifest = read(root / 'data/manifest.json')
tables = {}
for name, count in manifest['rows'].items():
    file = root / 'data' / (name + '.csv')
    assert hashlib.sha256(file.read_bytes()).hexdigest() == manifest['sha256'][name], name
    with file.open(encoding='utf-8-sig', newline='') as f:
        tables[name] = list(csv.DictReader(f))
    assert len(tables[name]) == count, name
keys = {}
for table, key in [('DimDate','DateKey'),('DimCustomer','CustomerKey'),('DimProduct','ProductKey'),('DimSeller','SellerKey'),('FactSales','SalesLineKey')]:
    keys[key] = {r[key] for r in tables[table]}
    assert len(keys[key]) == len(tables[table]), key
dates = [datetime.date.fromisoformat(r['Date']) for r in tables['DimDate']]
end = datetime.date.fromisoformat(manifest.get('coverage', {}).get('end', '2025-12-31'))
assert dates == [datetime.date(2024,1,1) + datetime.timedelta(days=i) for i in range((end-datetime.date(2024,1,1)).days+1)]
annual = {y: dict(revenue=Decimal(0), cost=Decimal(0), units=0, orders=set(), sellers={}) for y in range(2024,end.year+1)}
order_dimensions = {}
for r in tables['FactSales']:
    for key in ('DateKey','CustomerKey','ProductKey','SellerKey'):
        assert r[key] in keys[key], (r['SalesLineKey'], key)
    n = int(r['Quantity'])
    assert n > 0
    revenue, cost = Decimal(r['Revenue']), Decimal(r['Cost'])
    assert revenue == n * Decimal(r['UnitPrice'])
    assert cost == n * Decimal(r['UnitCost']) and 0 < cost < revenue
    dimensions = tuple(r[k] for k in ('DateKey','CustomerKey','SellerKey'))
    assert order_dimensions.setdefault(r['OrderKey'], dimensions) == dimensions
    a = annual[int(r['DateKey'][:4])]
    a['revenue'] += revenue; a['cost'] += cost; a['units'] += n; a['orders'].add(r['OrderKey'])
    a['sellers'][r['SellerKey']] = a['sellers'].get(r['SellerKey'], Decimal(0)) + revenue
expected = []
for year, a in annual.items():
    p = annual.get(year-1)
    if p and year == end.year and (end.month, end.day) != (12,31):
        prior = [r for r in tables['FactSales'] if int(r['DateKey'][:4]) == year-1 and r['DateKey'][4:] <= end.strftime('%m%d')]
        p = dict(revenue=sum((Decimal(r['Revenue']) for r in prior), Decimal(0)), cost=sum((Decimal(r['Cost']) for r in prior), Decimal(0)), units=sum(int(r['Quantity']) for r in prior), orders={r['OrderKey'] for r in prior})
    margin = (a['revenue']-a['cost'])/a['revenue']
    values = {'Datum[År]':year, '[Omsättning]':float(a['revenue']), '[Kostnad]':float(a['cost']), '[Bruttovinst]':float(a['revenue']-a['cost']), '[Bruttomarginal]':float(margin), '[Sålda enheter]':a['units'], '[Leveranser]':len(a['orders']), '[Omsättning PY]':float(p['revenue']) if p else None}
    for name, curr, prior in [('Omsättning',a['revenue'],p['revenue'] if p else None),('Enheter',a['units'],p['units'] if p else None),('Vinst',a['revenue']-a['cost'],p['revenue']-p['cost'] if p else None),('Leveranser',len(a['orders']),len(p['orders']) if p else None)]:
        values[f'[{name} YoY]'] = float(curr/prior-1) if prior else None
    values['[Marginal pp]'] = float((margin-(p['revenue']-p['cost'])/p['revenue'])*100) if p else None
    if 'Finansaxel' in tables:
        values.update({'[Aktiva säljare]':len(a['sellers']), '[Kostnad miljoner]':float(a['cost']/1000000), '[Omsättning per enhet]':float(a['revenue']/a['units']), '[Bruttovinst per enhet]':float((a['revenue']-a['cost'])/a['units']), '[Omsättning per säljare]':float(a['revenue']/len(a['sellers'])), '[Genomsnittlig order]':float(a['revenue']/len(a['orders'])), '[Topp 5 säljare andel]':float(sum(sorted(a['sellers'].values(),reverse=True)[:5])/a['revenue'])})
    expected.append(values)
layout = read(root / 'validation/layout.json')
metadata = read(root / 'validation/tmdl-result.json')
model = {t['name']:t for t in metadata['tables']}
page_ids = {p['id'] for p in layout['pages']}
for v in layout['placements']:
    x,y,w,h = v['box']
    assert x >= 0 and y >= 0 and x+w <= 1920 and y+h <= 1080, v['key']
    for field in v['fields']:
        kind = 'Column' if 'Column' in field else 'Measure'
        f = field[kind]
        assert f['Property'] in model[f['Expression']['SourceRef']['Entity']]['columns' if kind=='Column' else 'measures'], f
for path in (root/'AubecoSalesFinance.Report/definition/pages').glob('*/visuals/*/visual.json'):
    visual = read(path)['visual']
    for link in visual.get('visualContainerObjects',{}).get('visualLink',[]):
        target = link['properties']['navigationSection']['expr']['Literal']['Value'].strip("'")
        assert target in page_ids, target
out = {'status':'passed','independentSource':'CSV arithmetic using Decimal; no DAX implementation reused','rows':expected,'checks':['CSV counts and hashes','calendar completeness','unique primary keys and valid foreign keys','order consistency','row amounts and positive product margins','report bounds, model fields and navigation']}
actual_path = root / 'validation/desktop-dax.json'
if actual_path.exists() and len(read(actual_path)['rows']) == len(expected):
    actual = read(actual_path)
    assert len(actual['rows']) == len(expected)
    for want, got in zip(expected, actual['rows']):
        for key, value in want.items():
            assert key in got, (key,list(got))
            assert got[key] is None if value is None else got[key] is not None and math.isclose(float(got[key]),float(value),rel_tol=1e-8,abs_tol=1e-5), (key,value,got[key])
    out['desktopComparison'] = 'passed: both years and all query fields agree'
(root/'validation/data-expectations.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':out['status'],'orders':len(order_dimensions),'annual':expected,'desktopComparison':out.get('desktopComparison','not executed')},ensure_ascii=False))
