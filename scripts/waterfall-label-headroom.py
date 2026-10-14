"""Leave room above the highest cumulative bridge level in every period."""
from pathlib import Path
import json,re
root=Path(__file__).resolve().parents[1]
model=root/'powerbi-ledningsrapport/Ledningsrapport.SemanticModel/definition/tables/Försäljning.tmdl'
name='Bryggans övre axelgräns'
dax="VAR opening=[Rörelseresultat föregående år]/1000000 VAR products=CALCULATE([Bruttovinst]-[Bruttovinst föregående år],'Områden'[Områdesnyckel]=1)/1000000 VAR service=CALCULATE([Bruttovinst]-[Bruttovinst föregående år],'Områden'[Områdesnyckel]=2)/1000000 VAR staffing=CALCULATE([Bruttovinst]-[Bruttovinst föregående år],'Områden'[Områdesnyckel]=3)/1000000 VAR peak=MAXX({opening,opening+products,opening+products+service,opening+products+service+staffing,[Rörelseresultat]/1000000},[Value]) RETURN MAX(peak,0.1)*1.25"
text=model.read_text(encoding='utf-8-sig')
block=f"\n\t/// Ger etiketter utrymme ovanför resultatbryggans högsta kumulativa nivå, även vid periodbyte.\n\tmeasure '{name}' = {dax}\n\t\tformatString: 0.00\n\t\tdisplayFolder: Presentation\n\t\tisHidden\n"
if not re.search(r"(?m)^\tmeasure '"+name+r"' =",text):
    index=text.index('\n\tcolumn ');text=text[:index]+block+text[index:];model.write_text(text,encoding='utf-8')
directory=root/'powerbi-ledningsrapport/LedningsrapportUtanScroll.Report/definition/pages/e2f0addc480f40543797/visuals'
for file in directory.glob('*/visual.json'):
    v=json.loads(file.read_text(encoding='utf-8-sig'))
    if v['visual']['visualType']!='waterfallChart':continue
    for item in v['visual']['objects']['labels']:item['properties']['labelPosition']={'expr':{'Literal':{'Value':"'Auto'"}}}
    v['visual']['objects']['valueAxis'][0]['properties']['end']={'expr':{'Measure':{'Expression':{'SourceRef':{'Entity':'Försäljning'}},'Property':name}}}
    file.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Added dynamic 25% headroom above the highest bridge level; native labels restored to Auto.')
