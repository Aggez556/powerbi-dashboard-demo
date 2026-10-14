"""Keep KPI comparisons readable using explicit lines, not clipped callouts."""
from pathlib import Path
import json,hashlib,copy,re
root=Path(__file__).resolve().parents[1];base=root/'powerbi-ledningsrapport';report=base/'LedningsrapportUtanScroll.Report'
def lit(v):return {'expr':{'Literal':{'Value':str(v).lower() if isinstance(v,bool) else str(v)+'D' if isinstance(v,(int,float)) else "'"+v+"'"}}}
extra=[('Rörelsemarginal korttext','FORMAT([Rörelsemarginal],"0.0 %","sv-SE") & " marginal"'),('Kundförändring korttext','FORMAT([Aktiva kunder]-[Aktiva kunder föregående år],"+0;−0;0","sv-SE") & " kunder"')]
model=base/'Ledningsrapport.SemanticModel/definition/tables/Försäljning.tmdl'
s=model.read_text(encoding='utf-8-sig')
for name,dax in extra:
    if re.search(r"measure '?"+re.escape(name)+r"'? =",s):continue
    block=f"\n\t/// Visning på en egen textrad i KPI-kort.\n\tmeasure '{name}' = {dax}\n\t\tformatString: General\n\t\tdisplayFolder: Visning\n"
    index=s.index('\n\tcolumn ');s=s[:index]+block+s[index:]
model.write_text(s,encoding='utf-8')
changed=[]
for f in list((report/'definition/pages').glob('*/visuals/*/visual.json')):
    v=json.loads(f.read_text(encoding='utf-8-sig'));p=v['position']
    if v.get('visual',{}).get('visualType')!='cardVisual' or p['y']!=280:continue
    projection=v['visual']['query']['queryState']['Data']['projections'][0]
    measure=projection['field']['Measure']['Property']
    if not ('undertext' in measure or 'jämförelsetext' in measure):continue
    p.update(y=276,height=56)
    for a in v['visual']['objects']['value']:
        a['properties'].update(bold=lit(False),fontSize=lit(11),textWrap=lit(False))
    for obj in ['padding','layout']:
        v['visual']['objects'][obj]=[{'selector':{'id':'default'},'properties':{'paddingUniform':lit(0)}}]
    if measure in ['Rörelseresultat undertext','Kunder undertext']:
        p.update(y=272,height=32)
        new=copy.deepcopy(v);new['name']=hashlib.sha256(('kpi-second-line:'+measure).encode()).hexdigest()[:20]
        new['position'].update(y=304,height=32,z=p['z']+100,tabOrder=p['tabOrder']+100)
        first='Rörelsemarginal korttext' if measure=='Rörelseresultat undertext' else 'Kundförändring korttext'
        projection['field']['Measure']['Property']=first;projection['queryRef']='Försäljning.'+first;projection['nativeQueryRef']=first
        if measure=='Rörelseresultat undertext':
            q=new['visual']['query']['queryState']['Data']['projections'][0];q['field']['Measure']['Property']='Rörelseresultat jämförelsetext';q['queryRef']='Försäljning.Rörelseresultat jämförelsetext';q['nativeQueryRef']='Rörelseresultat jämförelsetext'
        else:
            new['visual']['visualType']='textbox';new['visual'].pop('query',None)
            new['visual']['objects']={'general':[{'properties':{'paragraphs':[{'textRuns':[{'value':'mot föregående år','textStyle':{'fontFamily':'Segoe UI','fontSize':'11pt','color':'#5B6B80'}}],'horizontalTextAlignment':'left'}]}}]}
        target=f.parent.parent/new['name']/'visual.json';target.parent.mkdir(exist_ok=True);target.write_text(json.dumps(new,ensure_ascii=False,indent=2),encoding='utf-8')
    f.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8');changed.append(measure)
print('KPI text updated:', ', '.join(changed))
