"""Download Microsoft's TOM package for offline TMDL deserialization only."""
from pathlib import Path
from urllib.request import urlopen
import json, zipfile, io

root=Path(__file__).resolve().parents[1]/'.tools/tom'
name='microsoft.analysisservices.retail.amd64'
with urlopen(f'https://api.nuget.org/v3-flatcontainer/{name}/index.json',timeout=45) as r:
    versions=json.load(r)['versions']
version=next(v for v in reversed(versions) if '-' not in v)
with urlopen(f'https://api.nuget.org/v3-flatcontainer/{name}/{version}/{name}.{version}.nupkg',timeout=60) as r:
    content=r.read()
root.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(io.BytesIO(content)) as package:
    for entry in package.infolist():
        target=(root/entry.filename).resolve()
        if not target.is_relative_to(root.resolve()): raise ValueError('Unsafe archive path')
    package.extractall(root)
(root/'source.json').write_text(json.dumps({'package':name,'version':version,'purpose':'TMDL file parsing; no server or data engine'},indent=2))
print(version)
print('\n'.join(str(p.relative_to(root)) for p in root.rglob('*.dll')))
