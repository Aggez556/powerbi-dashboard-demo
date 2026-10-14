"""Verify additive page bindings, canvas bounds and disconnected local data."""
from pathlib import Path
import csv,json,hashlib
root=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
meta=read(root/'powerbi/validation/tmdl-result.json')
models={t['name']:{'Column':{c['name'] for c in t['columns']},'Measure':{m['name'] for m in t['measures']}} for t in meta['modelMetadata']}
page=read(root/'powerbi/validation/budget-page.json')
assert len(models)==11 and meta['dateTableMarked'] and len(meta['relationships'])==3
for v in page['placements']:
    x,y,w,h=v['box']; assert x>=0 and y>=0 and x+w<=1920 and y+h<=1080
    for field in v['fields']:
        kind=next(iter(field)); f=field[kind]
        assert f['Property'] in models[f['Expression']['SourceRef']['Entity']][kind],f
for name,digest in read(root/'powerbi/data/manifest.json')['sha256'].items():
    assert hashlib.sha256((root/f'powerbi/data/{name}.csv').read_bytes()).hexdigest()==digest
expected={'Resultatrader':18,'Budgetscenario':2,'Budgetversion':4,'Budgetjustering':26,'Budgetbelopp':81,'Budgetfördelning':2,'Budgetkommentarer':3}
for name,count in expected.items():
    with (root/f'powerbi/data/{name}.csv').open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f)); assert len(rows)==count
    assert name in models
    assert not any(name in (r['fromTable'],r['toTable']) for r in meta['relationships'])
page['status']='static-checks-passed'
live_check=root/'powerbi/validation/budget-dax-checks.json'
dax_status='passed against actual Desktop engine' if live_check.exists() and read(live_check)['status']=='passed' else 'not yet verified'
page['checks']={'bindings':'match TOM metadata','bounds':'passed','originalSalesCSV':'SHA-256 unchanged','budgetRowCounts':expected,'budgetTablesDisconnected':True,'TMDL':'Microsoft TOM passed','DAXExecution':dax_status,'DesktopRendering':'not yet verified'}
(root/'powerbi/validation/budget-page.json').write_text(json.dumps(page,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Budget bindings, geometry, original sales hashes and 7 local Import tables: passed.')
