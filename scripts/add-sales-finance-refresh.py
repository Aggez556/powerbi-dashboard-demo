"""Add Import-time UTC metadata; never use NOW() as a refresh timestamp."""
from pathlib import Path

definition = Path(__file__).resolve().parents[1] / 'powerbi-sales-finance/AubecoSalesFinance.SemanticModel/definition'
(definition / 'tables/Rapportstatus.tmdl').write_text('''table Rapportstatus

	measure 'Senast uppdaterad' = IF(ISBLANK(MAX('Rapportstatus'[Uppdaterad UTC])), BLANK(), "Senast uppdaterad: " & FORMAT(MAX('Rapportstatus'[Uppdaterad UTC]), "yyyy-MM-dd HH:mm") & " UTC")
		formatString: @
		displayFolder: Rapportstatus

	column 'Uppdaterad UTC'
		dataType: dateTime
		isHidden
		formatString: yyyy-MM-dd HH:mm
		summarizeBy: none
		sourceColumn: Uppdaterad UTC

	partition Rapportstatus = m
		mode: import
		source =
			let
				Timestamp = DateTimeZone.RemoveZone(DateTimeZone.FixedUtcNow()),
				Result = #table(type table [#"Uppdaterad UTC" = datetime], {{Timestamp}})
			in
				Result
''', encoding='utf-8')
p = definition / 'model.tmdl'
s = p.read_text(encoding='utf-8')
if 'ref table Rapportstatus' not in s:
    s += '\nref table Rapportstatus\n'
p.write_text(s, encoding='utf-8')
for p in (definition / 'tables').glob('*.tmdl'):
    s = p.read_text(encoding='utf-8')
    changed = s.replace('#187447', '#078A36').replace('#B83232', '#D92D20')
    if changed != s:
        p.write_text(changed, encoding='utf-8')
print('Refresh metadata: Import-time UTC, one row, no relationships.')
