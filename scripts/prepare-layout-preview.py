"""Create a separate local PBIP preview so the open original is never reloaded."""
from pathlib import Path
import shutil,json,uuid
root=Path(__file__).resolve().parents[1]
target=root/'.tools/previews'/('budget-layout-'+uuid.uuid4().hex[:12])
target.mkdir(parents=True)
for name in ['AubecoHandel.pbip','AubecoHandel.Report','AubecoHandel.SemanticModel']:
    src=root/'powerbi'/name
    if src.is_dir():shutil.copytree(src,target/name)
    else:shutil.copy2(src,target/name)
result={'folder':str(target/'AubecoHandel.pbip'),'directory':str(target),'purpose':'Isolated Desktop preview of latest PBIR; original open instance unchanged'}
(root/'powerbi/validation/layout-preview-run.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
