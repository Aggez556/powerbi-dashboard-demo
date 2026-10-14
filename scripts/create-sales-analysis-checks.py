from pathlib import Path

root = Path(__file__).resolve().parents[1] / 'powerbi-sales-finance/validation'
rows = []
for rank in range(1, 8):
    rows.append(f'ROW("Rank", {rank}, "Namn", [Säljanalys säljare {rank} namn], "Belopp", [Säljanalys säljare {rank} belopp], "Tillväxt", [Säljanalys säljare {rank} tillväxt])')
ranking = 'UNION(' + ',\n'.join(rows) + ')'
periods = []
for label, months in [('Full', None), ('October', '10'), ('SepOct', '9,10')]:
    filters = ", TREATAS({" + months + "}, 'Datum'[Månadsnummer])" if months else ''
    periods.append('ADDCOLUMNS(CALCULATETABLE(' + ranking + filters + '), "Period", "' + label + '")')
query = 'EVALUATE\nCALCULATETABLE(UNION(' + ',\n'.join(periods) + "), TREATAS({2025}, 'Datum'[År]))\nORDER BY [Period], [Rank]"
(root / 'sales-ranking-check.dax').write_text(query, encoding='utf-8')
rows = []
for rank in range(1, 5):
    rows.append(f'''SELECTCOLUMNS(SUMMARIZECOLUMNS('Datum'[Månadsnummer], "Group", [Säljanalys trend {rank} namn], "Value", [Säljanalys trend {rank} värde], "Max", [Säljanalys trend {rank} max], "Min", [Säljanalys trend {rank} min]), "Month", 'Datum'[Månadsnummer], "Group", [Group], "Value", [Value], "Max", [Max], "Min", [Min], "Rank", {rank})''')
for mode in ['Land', 'Kategori']:
    query = 'EVALUATE\nCALCULATETABLE(UNION(' + ',\n'.join(rows) + f'''), TREATAS({{2025}}, 'Datum'[År]), TREATAS({{"{mode}"}}, 'Analysaxel'[Typ]))\nORDER BY [Rank], [Month]'''
    (root / ('sales-trends-' + mode.lower() + '-check.dax')).write_text(query, encoding='utf-8')
print('Generated ranking and trend queries with UTF-8 model names.')
