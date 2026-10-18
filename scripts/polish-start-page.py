"""Align the existing original report homepage with its five completed pages."""
from pathlib import Path
from copy import deepcopy
import json

root=Path(__file__).resolve().parents[1]
report=root/'powerbi-ledningsrapport/LedningsrapportUtanScroll.Report'
page=report/'definition/pages/6ff94a05bddfe7036ec7/visuals'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
visuals={p.parent.name:read(p) for p in page.glob('*/visual.json')}
lit=lambda value:{'expr':{'Literal':{'Value':"'"+value.replace("'","''")+"'"}}}

def label(key,value):
    v=visuals[key]
    paragraphs=v['visual']['objects']['general'][0]['properties']['paragraphs']
    run=deepcopy(paragraphs[0]['textRuns'][0])
    run['value']=value
    paragraphs[:]=[{'textRuns':[run],'horizontalTextAlignment':'left'}]

label('188309eb63f37b04b616','UPPDRAG OCH BELÄGGNING')
label('7822dc2c86b21b54094e','Gemensamma nyckeltal. Period och urval väljs på respektive sida.')
visuals['7822dc2c86b21b54094e']['position']['height']=64
label('86b78584d5746804a912','Budgetscenarier, utfall och en detaljerad resultaträkning.')
label('599d58431927ed5e2eb2','Försäljning, tillväxt och lönsamhet per kategori.')
label('95fa0d51b93ab7ee425d','Kundbas, kundförändringar och försäljning per kundgrupp.')
label('4523c14f425e64cf8df3','Utförda uppdrag, debiteringsgrad och kommande beläggning.')
for key in ['b7b2fc71d8df4ec650e5','f0727e06d7ccef610a11','14652459cc26d6e07efa','314e9d3ce19b1171ae71','6d66d3f28cc6bdbf2707']:
    for paragraph in visuals[key]['visual']['objects']['general'][0]['properties']['paragraphs']:
        for run in paragraph['textRuns']:
            run['textStyle']['fontSize']='20pt'

template=read(report/'definition/pages/e2f0addc480f40543797/visuals/44861332c68e7a64992f/visual.json')
def image(key,filename,position,alt):
    v=deepcopy(template)
    v['name']=key
    v['position']=position
    obj=v['visual']['objects']['image'][0]['properties']
    obj['sourceFile']['image']['name']=lit(filename)
    obj['sourceFile']['image']['url']['expr']['ResourcePackageItem']['ItemName']=filename
    obj['altText']=lit(alt)
    v['visual']['visualContainerObjects'].pop('visualLink',None)
    visuals[key]=v

for key,name,alt in [('64a0c6022a771343b9b3','overview','Ledningsöversikt'),('f669ed3b904499315713','sales','Försäljningsöversikt'),('f385801e04362e4bd107','customers','Kunder'),('8205013ebefa15ff9ebf','budget','Budget'),('e387e91859f457aa56e8','projects','Uppdrag och beläggning')]:
    pos=deepcopy(visuals[key]['position'])
    pos.update(width=64,height=64,y=440)
    image(key,f'navigation-{name}-0F3163.png',pos,alt)
image('513ac37856ed4795bd07','DemobolagetBlue.png',dict(x=1576,y=56,width=280,height=80,z=45,tabOrder=45),'Demobolaget')

buttons=['5324b8344ad9f7ff304a','5182a941debce80251ac','c7b089159c40f45a3495','dda3a372cc316fd4f667','8848cd1078507132576f']
targets=['e2f0addc480f40543797','b4eda99cffce7ac04192','f429b020315c602ce0ed','cbe967640ff6843fb323','30e52cac0a5174639318']
for key,target in zip(buttons,targets):
    v=visuals[key]['visual']
    for state in v['objects']['text']:
        if 'selector' in state:
            state['properties']['fontColor']={'solid':{'color':lit('#FFFFFF')}}
    for state in v['objects']['fill']:
        if 'selector' in state:
            color='#0F3163' if state['selector']['id']=='default' else '#234C7C'
            state['properties']['fillColor']={'solid':{'color':lit(color)}}
    link=v['visualContainerObjects']['visualLink'][0]['properties']
    link.update(show={'expr':{'Literal':{'Value':'true'}}},type=lit('PageNavigation'),navigationSection=lit(target))
    assert (report/'definition/pages'/target/'page.json').exists()

for key,v in visuals.items():
    p=page/key/'visual.json'
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Updated original Start page: five active routes, consistent buttons/icons, Aubeco logo and accurate period guidance.')
