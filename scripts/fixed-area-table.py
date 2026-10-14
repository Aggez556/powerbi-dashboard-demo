"""A fixed report grid with native, period-sensitive cards; no scrollable visual."""
from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[1];report=root/'powerbi-ledningsrapport/LedningsrapportUtanScroll.Report'
def lit(v):return {'expr':{'Literal':{'Value':str(v).lower() if isinstance(v,bool) else f'{v}D' if isinstance(v,(int,float)) else "'"+v+"'"}}}
def fill(c):return {'solid':{'color':lit(c)}}
def entries(p):return [{'properties':p}]
def name(s):return hashlib.sha256(('fixed-area:'+s).encode()).hexdigest()[:20]
for page in (report/'definition/pages').iterdir():
    visuals=page/'visuals'
    if not visuals.exists():continue
    matrices=[]
    for f in visuals.glob('*/visual.json'):
        v=json.loads(f.read_text(encoding='utf-8-sig'))
        if v.get('visual',{}).get('visualType')=='pivotTable' and 'Områden' in json.dumps(v['visual'].get('query',{}),ensure_ascii=False):matrices.append(f)
    if not matrices and not (visuals/name('header-0')).exists():continue
    z=1500
    def write(key,typ,x,y,w,h,objects,query=None,back=None):
        global z
        z+=1
        n=name(key);vc={'background':entries({'show':lit(bool(back)),'color':fill(back or '#FFFFFF'),'transparency':lit(0 if back else 100)}),'border':entries({'show':lit(False)}),'padding':entries({s:lit(0) for s in ['top','bottom','left','right']}),'title':entries({'show':lit(False)}),'subTitle':entries({'show':lit(False)}),'general':entries({'altText':lit(key)})}
        v={'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json','name':n,'position':{'x':x,'y':y,'width':w,'height':h,'z':z,'tabOrder':z},'visual':{'visualType':typ,'objects':objects,'visualContainerObjects':vc}}
        if query:v['visual']['query']={'queryState':{'Data':{'projections':[query]}}}
        f=visuals/n/'visual.json';f.parent.mkdir(exist_ok=True);return f,v
    def text(key,label,x,y,w,h,bold=False,back=None,align='left'):
        obj={'general':entries({'paragraphs':[{'textRuns':[{'value':line,'textStyle':{'fontFamily':'Segoe UI Semibold' if bold else 'Segoe UI','fontSize':'11pt','fontWeight':'bold' if bold else 'normal','color':'#0F3163' if bold else '#5B6B80'}}],'horizontalTextAlignment':align} for line in label.split('\n')]})}
        f,v=write(key,'textbox',x,y,w,h,obj,back=back);f.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
    widths=[204,120,116,142,84,84];xs=[312]
    text('table-background','',312,864,750,240,False,'#D5DDE7')
    text('header-background','',312,864,750,48,False,'#EEF2F7')
    for w in widths[:-1]:xs.append(xs[-1]+w)
    labels=['Område','Omsättning','Bruttovinst','Bruttomarginal','Uppdrag','Kunder']
    for i,(x,w,label) in enumerate(zip(xs,widths,labels)):text(f'header-{i}',label,x+8,878,w-16,28,True,None,'left' if i==0 else 'right')
    measures=['Nettoomsättning Mkr','Bruttovinst Mkr','Bruttomarginal','Utförda uppdrag','Aktiva kunder']
    for row,label in enumerate(['Produktförsäljning','Teknisk service','Bemanning','Totalt']):
        y=912+row*48;back='#EEF2F7' if row==3 else '#FFFFFF'
        text(f'row-{row}-background','',312,y+1,750,47,False,back)
        text(f'row-{row}-label',label,320,y+14,188,28,row==3)
        for i,measure in enumerate(measures):
            field={'Measure':{'Expression':{'SourceRef':{'Entity':'Försäljning'}},'Property':measure}}
            q={'field':field,'queryRef':'Försäljning.'+measure,'nativeQueryRef':measure}
            obj={k:[{'selector':{'id':'default'},'properties':{'show':lit(False)}}] for k in ['outline','fillCustom','shadowCustom','label']}
            obj['value']=[{'selector':{'id':'default'},'properties':{'fontSize':lit(11),'bold':lit(row==3),'fontFamily':lit('Segoe UI Semibold' if row==3 else 'Segoe UI'),'fontColor':fill('#0F3163' if row==3 else '#5B6B80'),'horizontalAlignment':lit('right'),'textWrap':lit(False),'showBlankAs':lit('—'),'labelDisplayUnits':lit(1)}}]
            obj['fillCustom']=[{'properties':{'show':lit(True),'fillColor':fill(back),'transparency':lit(0)}},{'selector':{'id':'default'},'properties':{'show':lit(True),'fillColor':fill(back),'transparency':lit(0)}}]
            obj['layout']=[{'properties':{'backgroundShow':lit(False),'backgroundTransparency':lit(100),'rectangleRoundedCurve':lit(0),'paddingUniform':lit(0),'cellPadding':lit(0)}},{'selector':{'id':'default'},'properties':{'backgroundShow':lit(False),'rectangleRoundedCurve':lit(0),'paddingUniform':lit(0)}}]
            obj['padding']=[{'selector':{'id':'default'},'properties':{'paddingUniform':lit(0)}}]
            obj['cardCalloutArea']=entries({'show':lit(False),'backgroundTransparency':lit(100),'paddingUniform':lit(0)})
            f,v=write(f'value-{row}-{i}','cardVisual',xs[i+1]+8,y+5,widths[i+1]-16,38,obj,q)
            if row<3:
                v['filterConfig']={'filters':[{'name':name(f'filter-{row}-{i}'),'field':{'Column':{'Expression':{'SourceRef':{'Entity':'Områden'}},'Property':'Områdesnyckel'}},'type':'Categorical','howCreated':'User','filter':{'Version':2,'From':[{'Name':'o','Entity':'Områden','Type':0}],'Where':[{'Condition':{'In':{'Expressions':[{'Column':{'Expression':{'SourceRef':{'Source':'o'}},'Property':'Områdesnyckel'}}],'Values':[[{'Literal':{'Value':str(row+1)+'L'}}]]}}}]}}]}
            f.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
    for f in matrices:
        f.unlink()
        if not any(f.parent.iterdir()):f.parent.rmdir()
    for d in visuals.iterdir():
        if d.is_dir() and not any(d.iterdir()):d.rmdir()
    generated=[json.loads(f.read_text(encoding='utf-8-sig')) for f in visuals.glob('*/visual.json')]
    assert not any(v.get('visual',{}).get('visualType')=='pivotTable' for v in generated)
    assert all((visuals/name(f'value-{r}-{i}')/'visual.json').exists() for r in range(4) for i in range(5))
print('Replaced area matrix with fixed headers and 20 native measure cards, including unique total customers.')
