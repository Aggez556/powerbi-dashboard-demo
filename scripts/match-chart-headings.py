"""Match the two dynamic chart headings to the lower panels' typography."""
from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[1];report=root/'powerbi-ledningsrapport/LedningsrapportUtanScroll.Report'
def lit(v):return {'expr':{'Literal':{'Value':str(v).lower() if isinstance(v,bool) else str(v)+'D' if isinstance(v,(int,float)) else "'"+v+"'"}}}
count=0
for f in (report/'definition/pages').glob('*/visuals/*/visual.json'):
    v=json.loads(f.read_text(encoding='utf-8-sig'))
    if v.get('visual',{}).get('visualType')!='cardVisual':continue
    query=json.dumps(v['visual'].get('query',{}),ensure_ascii=False)
    if not any(n in query for n in ['Trendrubrik','Uppdragsrubrik']):continue
    for item in v['visual']['objects']['value']:
        item['properties'].update(fontSize=lit(19),fontFamily=lit('Segoe UI Semibold'),bold=lit(False),horizontalAlignment=lit('left'),textWrap=lit(False))
    props={k:lit(0) for k in ['paddingUniform','cellPadding','leftOuterMargin','rightOuterMargin','topOuterMargin','bottomOuterMargin']}
    v['visual']['objects']['layout']=[{'properties':props},{'selector':{'id':'default'},'properties':props}]
    v['visual']['objects']['cardCalloutArea']=[{'properties':{'show':lit(False),'paddingUniform':lit(0),'backgroundTransparency':lit(100)}}]
    # Dynamic cards retain an intrinsic text inset relative to a textbox.
    # Compensate so the rendered titles share the lower panels' 24px left inset.
    v['position']['x']=296 if 'Trendrubrik' in query else 1110
    v['position']['width']=766
    v['position']['y']=364
    f.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8');count+=1
assert count==2,count
charts=0
for f in (report/'definition/pages').glob('*/visuals/*/visual.json'):
    v=json.loads(f.read_text(encoding='utf-8-sig'))
    kind=v.get('visual',{}).get('visualType')
    if kind not in ['lineStackedColumnComboChart','columnChart'] or v['position']['y']>500:continue
    # Separate the legend strip from the plot, so moving the plot does not move the legend.
    v['position'].update(y=424,height=312)
    for item in v['visual']['objects'].get('legend',[]):
        item['properties'].update(show=lit(False),position=lit('TopRight'),fontSize=lit(13.75),fontFamily=lit('Segoe UI'),bold=lit(False))
    if kind=='lineStackedColumnComboChart':
        for projection in v['visual']['query']['queryState'].get('Y2',{}).get('projections',[]):
            projection['displayName']='Rörelsemarginal'
            projection['nativeQueryRef']='Rörelsemarginal'
    f.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8');charts+=1
    labels=['Omsättning','Rörelsemarginal'] if kind=='lineStackedColumnComboChart' else ['Teknisk service','Bemanning']
    runs=[]
    for i,(label,color) in enumerate(zip(labels,['#0F3163','#007956'])):
        runs.append({'value':'● ','textStyle':{'fontFamily':'Segoe UI','fontSize':'13.75pt','color':color}})
        runs.append({'value':label+('   ' if i==0 else ''),'textStyle':{'fontFamily':'Segoe UI','fontSize':'13.75pt','color':'#5B6B80'}})
    name=hashlib.sha256(('chart-header-legend:'+kind).encode()).hexdigest()[:20]
    legend={'$schema':v['$schema'],'name':name,'position':{'x':v['position']['x']+406,'y':380,'width':344,'height':32,'z':1700+charts,'tabOrder':1700+charts},'visual':{'visualType':'textbox','objects':{'general':[{'properties':{'paragraphs':[{'textRuns':runs,'horizontalTextAlignment':'right'}]}}]},'visualContainerObjects':{'background':[{'properties':{'show':lit(False)}}],'border':[{'properties':{'show':lit(False)}}],'padding':[{'properties':{side:lit(0) for side in ['top','bottom','left','right']}}],'title':[{'properties':{'show':lit(False)}}],'general':[{'properties':{'altText':lit('Teckenförklaring: '+', '.join(labels))}}]}}}
    target=f.parent.parent/name/'visual.json';target.parent.mkdir(exist_ok=True);target.write_text(json.dumps(legend,ensure_ascii=False,indent=2),encoding='utf-8')
assert charts==2,charts
print('Upper plots start 56px lower, with separate right-aligned header legends; bottom edges unchanged.')
