"""Keep KPI comparisons on one line without reducing the font size."""
from pathlib import Path
import json,hashlib,re
root=Path(__file__).resolve().parents[1];base=root/'powerbi-ledningsrapport';report=base/'LedningsrapportUtanScroll.Report'
def lit(v):return {'expr':{'Literal':{'Value':str(v).lower() if isinstance(v,bool) else str(v)+'D' if isinstance(v,(int,float)) else "'"+v+"'"}}}
extra=[('Rörelsemarginal korttext','FORMAT([Rörelsemarginal],"0.0 %","sv-SE") & " marginal · " & FORMAT([Rörelseresultat förändring],"+0.0 %;−0.0 %;0.0 %","sv-SE")'),('Kundförändring korttext','FORMAT([Aktiva kunder]-[Aktiva kunder föregående år],"+0;−0;0","sv-SE") & " mot föregående år"')]
model=base/'Ledningsrapport.SemanticModel/definition/tables/Försäljning.tmdl';s=model.read_text(encoding='utf-8-sig')
for name,dax in extra:
    pattern=r"(?m)^(\tmeasure '?"+re.escape(name)+r"'? = ).*$"
    assert re.search(pattern,s),name
    s=re.sub(pattern,lambda m:m[1]+dax,s)
model.write_text(s,encoding='utf-8')
for page in (report/'definition/pages').iterdir():
    visuals=page/'visuals'
    if not visuals.exists():continue
    for measure in ['Rörelseresultat undertext','Kunder undertext']:
        old=visuals/hashlib.sha256(('kpi-second-line:'+measure).encode()).hexdigest()[:20]/'visual.json'
        if old.exists():
            old.unlink()
            if not any(old.parent.iterdir()):old.parent.rmdir()
    for f in visuals.glob('*/visual.json'):
        v=json.loads(f.read_text(encoding='utf-8-sig'));p=v['position']
        if v.get('visual',{}).get('visualType')!='cardVisual' or not 270<=p['y']<=280:continue
        q=v['visual']['query']['queryState']['Data']['projections'][0];n=q['field']['Measure']['Property']
        if n=='Rörelseresultat undertext':n='Rörelsemarginal korttext'
        if n in ['Kunder undertext','Kundförändring korttext']:n='Kundförändring korttext'
        q['field']['Measure']['Property']=n;q['queryRef']='Försäljning.'+n;q['nativeQueryRef']=n
        p.update(y=280,height=48)
        if n=='Kundförändring korttext':p['width']=230
        for a in v['visual']['objects']['value']:a['properties'].update(bold=lit(False),fontSize=lit(11),textWrap=lit(False),horizontalAlignment=lit('left'))
        for obj in ['padding','layout']:v['visual']['objects'][obj]=[{'selector':{'id':'default'},'properties':{'paddingUniform':lit(0)}}]
        if n=='Kundförändring korttext':
            v['visual']['objects']['layout']=[{'properties':{'paddingUniform':lit(0),'cellPadding':lit(0),'leftOuterMargin':lit(0),'rightOuterMargin':lit(0),'topOuterMargin':lit(0),'bottomOuterMargin':lit(0)}},{'selector':{'id':'default'},'properties':{'paddingUniform':lit(0),'cellPadding':lit(0),'leftOuterMargin':lit(0),'rightOuterMargin':lit(0)}}]
        f.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
print('Single-line comparisons applied; second-line visuals removed.')
