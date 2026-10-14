from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
base=root/'powerbi-ledningsrapport'
model=base/'Ledningsrapport.SemanticModel/definition/tables/Försäljning.tmdl'
s=model.read_text(encoding='utf-8-sig')
for line in s.splitlines():
    if ('measure Bryggsteg =' in line or "measure 'Bryggsteg' =" in line) and line.rstrip().endswith('/1000000)'):
        s=s.replace(line,line.rstrip()[:-1])
model.write_text(s,encoding='utf-8')
generator=root/'scripts/generate-ledningsrapport.py'
s=generator.read_text(encoding='utf-8');s=s.replace(')))/1000000)\",',')))/1000000\",');generator.write_text(s,encoding='utf-8')
def lit(x):return {'expr':{'Literal':{'Value':str(x).lower() if isinstance(x,bool) else str(x)+'D' if isinstance(x,(int,float)) else "'"+x+"'"}}}
for p in (base/'LedningsrapportUtanScroll.Report/definition/pages').glob('*/visuals/*/visual.json'):
    v=json.loads(p.read_text(encoding='utf-8-sig'))
    if v.get('visual',{}).get('visualType')!='pivotTable' or 'Områden' not in json.dumps(v['visual'].get('query',{}),ensure_ascii=False):continue
    v['position'].update(y=864,height=256,width=750)
    projections=v['visual']['query']['queryState']['Values']['projections']
    labels=['Omsättning','Bruttovinst','Bruttomarginal','Uppdrag','Kunder']
    # displayName controls the visible header; nativeQueryRef alone is insufficient.
    for item,label in zip(projections,labels):item['displayName']=label;item['nativeQueryRef']=label
    o=v['visual']['objects']
    o['columnHeaders'][0]['properties'].update(autoSizeColumnWidth=lit(False),columnAdjustment=lit('fixedWidth'),customColumnWidth=lit(True),wordWrap=lit(True),fontSize=lit(11))
    fields=v['visual']['query']['queryState']['Rows']['projections']+projections
    o['columnWidth']=[{'selector':{'metadata':f['queryRef']},'properties':{'value':lit(w)}} for f,w in zip(fields,[204,116,116,116,88,88])]
    o['grid'][0]['properties']['rowPadding']=lit(8)
    v['visual']['visualContainerObjects']['padding']=[{'properties':{k:lit(0) for k in ['top','bottom','left','right']}}]
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Corrected waterfall DAX and set six columns to 728px within a 750px table; 256px height for header and four rows.')
