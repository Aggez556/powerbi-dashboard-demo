"""Apply only number formatting, preserving Desktop-authored layout and theme."""
from pathlib import Path
import json,hashlib,re
root=Path(__file__).resolve().parents[1]
report=root/'powerbi/AubecoHandel.Report'
nbsp='\u00a0'
def literal(value):
    return {'expr':{'Literal':{'Value':str(value)+'D' if isinstance(value,int) else "'"+value.replace("'","''")+"'"}}}
def fingerprints():
    files=[report/'definition/report.json',*report.glob('StaticResources/**/*.json'),*report.glob('definition/pages/*/page.json')]
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
unchanged=fingerprints()
changed=[]
for path in report.glob('definition/pages/*/visuals/*/visual.json'):
    visual=json.loads(path.read_text(encoding='utf-8-sig'))
    if visual['visual']['visualType']!='cardVisual':continue
    before=json.loads(json.dumps(visual))
    name=visual['visual']['query']['queryState']['Data']['projections'][0]['field']['Measure']['Property']
    percentage=name in ('Bruttomarginal','Tillväxt mot föregående år')
    fmt=f'0.0{nbsp}%;-0.0{nbsp}%;0.0{nbsp}%' if percentage else '#,##0' if name=='Antal order' else f'#,##0 "{nbsp}kr"'
    for item in visual['visual']['objects']['value']:
        item['properties'].update(labelDisplayUnits=literal(1),labelPrecision=literal(1 if percentage else 0),customFormatString=literal(fmt))
    assert before['position']==visual['position']
    assert before['visual']['query']==visual['visual']['query']
    assert before['visual']['visualContainerObjects']==visual['visual']['visualContainerObjects']
    path.write_text(json.dumps(visual,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    changed.append(name)
model=root/'powerbi/AubecoHandel.SemanticModel/definition/tables/Försäljning.tmdl'
def formats(text):
    text=text.replace('#,##0.00 "kr"',f'#,##0.00 "{nbsp}kr"')
    return re.sub(r'(?<![\d.])0\.0(?!'+nbsp+')%',f'0.0{nbsp}%',text)
model.write_text(formats(model.read_text(encoding='utf-8-sig')),encoding='utf-8')
generator=root/'scripts/generate-sales-project.py'
generator.write_text(formats(generator.read_text(encoding='utf-8')),encoding='utf-8')
assert unchanged==fingerprints(),'Page layout or report theme changed.'
result={'status':'passed','cards':changed,'orderDisplayUnits':'None (1)','orderFormat':'#,##0','currencyCardDecimals':0,'currencyModelDecimals':2,'unitSpacing':'nonbreaking space','themeAndPageFilesUnchanged':True,'desktopRendering':'not yet verified'}
(root/'powerbi/validation/number-formats.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=True))
