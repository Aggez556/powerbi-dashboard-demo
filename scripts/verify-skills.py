"""Verify project skill metadata and local Markdown reference targets."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1] / '.agents' / 'skills'
skills = list(root.glob('*/SKILL.md'))
assert len(skills) == 3, f'Expected three skills, found {len(skills)}'
for path in skills:
    content = path.read_text(encoding='utf-8')
    assert content.startswith('---'), path
    assert re.search(r'(?m)^name: .+', content), path
    assert re.search(r'(?m)^description: .+', content), path
    print(f'OK: {path.parent.name}')

missing = []
checked = 0
for path in root.rglob('*.md'):
    for link in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
        link = link.split('#')[0]
        if not link or ':' in link or ' ' in link or '<' in link:
            continue
        checked += 1
        if not (path.parent / link).exists():
            missing.append((str(path.relative_to(root)), link))
print(f'Checked {checked} relative file links; {len(missing)} missing.')
for path, link in missing:
    print(f'MISSING: {path} -> {link}')
raise SystemExit(bool(missing))
