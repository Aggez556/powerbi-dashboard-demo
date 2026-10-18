from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
folder=root/'powerbi-ledningsrapport/LedningsrapportUtanScroll.Report/definition/pages/f429b020315c602ce0ed/visuals'
def visit(value):
 if isinstance(value,dict):return {k:visit(v) for k,v in value.items()}
 if isinstance(value,list):return [visit(v) for v in value]
 if isinstance(value,str):return value.replace('Försäljning per kundgrupp','Omsättning per kundgrupp (Mkr)')
 return value
for p in folder.glob('*/visual.json'):
 value=json.loads(p.read_text(encoding='utf-8-sig'));updated=visit(value)
 if updated!=value:p.write_text(json.dumps(updated,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=root/'scripts/build-customer-page.cjs';s=p.read_text(encoding='utf-8');p.write_text(s.replace('Försäljning per kundgrupp','Omsättning per kundgrupp (Mkr)'),encoding='utf-8')
print('Clarified that the customer-group chart shows revenue in Mkr, not customer counts.')
