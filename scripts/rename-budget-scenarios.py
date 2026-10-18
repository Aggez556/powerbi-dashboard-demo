"""Rename scenario labels without changing IDs, amounts or partition types."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
folders=['powerbi-ledningsrapport/data','powerbi-ledningsrapport/Ledningsrapport.SemanticModel/definition','powerbi-ledningsrapport/LedningsrapportUtanScroll.Report/definition','scripts']
changed=[]
for folder in folders:
 for p in (root/folder).rglob('*'):
  if p.suffix not in {'.csv','.json','.tmdl','.py','.cjs','.mjs'} or p==Path(__file__).resolve():continue
  raw=p.read_bytes();s=raw.decode('utf-8-sig');old=s
  for before,after in [('Fastställd budget','Huvudscenario'),('Försiktigt','Försiktigt scenario'),('Offensivt','Offensivt scenario')]:
   s=re.sub(re.escape(before)+r'(?! scenario)',after,s)
  if s!=old:
   p.write_bytes((b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'')+s.encode('utf-8'));changed.append(str(p.relative_to(root)))
print('\n'.join(changed))
