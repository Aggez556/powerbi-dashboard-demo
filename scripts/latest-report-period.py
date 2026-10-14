"""Update saved slicer and bookmark defaults without rebuilding the design."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
base=root/'powerbi-ledningsrapport'
report=base/json.loads((base/'Ledningsrapport.pbip').read_text(encoding='utf-8-sig'))['artifacts'][0]['report']['path']
def replace(v):
    if isinstance(v,str):return v.replace('Oktober 2026','September 2026')
    if isinstance(v,list):return [replace(x) for x in v]
    if isinstance(v,dict):return {k:replace(x) for k,x in v.items()}
    return v
count=0
for f in (report/'definition').rglob('*.json'):
    v=json.loads(f.read_text(encoding='utf-8-sig'));new=replace(v)
    if new!=v:f.write_text(json.dumps(new,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');count+=1
builder=root/'scripts/build-ledningsrapport.cjs';s=builder.read_text(encoding='utf-8');builder.write_text(s.replace('Oktober 2026','September 2026'),encoding='utf-8')
print(f'Updated {count} slicer/bookmark definitions to September 2026.')
