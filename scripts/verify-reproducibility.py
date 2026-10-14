"""Regenerate twice and assert identical CSV content and TMDL files."""
from pathlib import Path
import subprocess,sys,hashlib,json
root=Path(__file__).resolve().parents[1]
def snapshot():
    files=list((root/'powerbi/data').glob('*.csv'))+list((root/'powerbi/AubecoHandel.SemanticModel').rglob('*.tmdl'))
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
before=snapshot()
subprocess.run([sys.executable,str(root/'scripts/generate-sales-project.py')],check=True)
after=snapshot()
assert before==after, 'Generated files changed between successive runs.'
(root/'powerbi/validation/reproducibility.json').write_text(json.dumps({'status':'passed','twoSuccessiveRunsIdentical':True,'sha256':after},indent=2)+'\n',encoding='utf-8')
print('CSV and TMDL reproducibility: passed')
