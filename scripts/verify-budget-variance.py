import json
import math
from pathlib import Path

base = Path('powerbi-ledningsrapport/validation')
live = json.loads((base / 'budget-statement-live-result.json').read_text(encoding='utf-8-sig'))['resultSets']
checks = 0
variances = 0
for actual, name in zip(live, ['budget-statement-fixture.json', 'budget-statement-scenarios-fixture.json']):
    expected = json.loads((base / name).read_text(encoding='utf-8-sig'))
    lookup = {(r['Node'], r['GroupOrder'], r['Slot']): r for r in expected}
    assert len(actual) == len(expected)
    for source in actual:
        row = {k.strip('[]'): v for k, v in source.items()}
        ref = lookup[(row['Node'], row['GroupOrder'], row['Slot'])]
        assert math.isclose(row['Amount'], ref['Amount'], abs_tol=1e-7), (row, ref)
        checks += 1
        if row['Slot'] == 3:
            assert row['Text'] == ref['Text'], (row, ref)
            assert row['Color'] == ref['Color'], (row, ref)
            variances += 1
report = dict(status='passed', actualDesktopDAXCells=checks, varianceTextAndColorChecks=variances,
              modes=['budget versus actual', 'scenario A versus B'])
(base / 'budget-variance-verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report))
