"""Restore schema references omitted by Desktop when saving project shortcuts."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
for relative,schema in [
 ('powerbi/AubecoHandel.pbip','https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json'),
 ('powerbi/AubecoHandel.Report/definition.pbir','https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json')]:
    path=root/relative
    obj=json.loads(path.read_text(encoding='utf-8-sig'))
    if '$schema' not in obj:
        obj={'$schema':schema,**obj}
        path.write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
