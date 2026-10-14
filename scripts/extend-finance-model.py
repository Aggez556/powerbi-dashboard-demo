"""Presentation measures for the reference-led finance page; sources stay unchanged."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
path = root / 'powerbi-sales-finance/AubecoSalesFinance.SemanticModel/definition/tables/Försäljning.tmdl'
text = path.read_text(encoding='utf-8')
measures = {}
for i, driver in enumerate(['Bruttovinst YoY', 'Marginal förändring', 'Kostnad årsförändring', 'Omsättning per enhet årsförändring', 'Bruttovinst per enhet årsförändring']):
    fmt = '+0.0;-0.0;0.0' if i == 1 else '+0.0 %;-0.0 %;0.0 %'
    suffix = ' & " pp"' if i == 1 else ''
    measures[f'Finans KPI {i} förändring etikett'] = (f'''VAR _value = [{driver}]
RETURN IF(NOT ISBLANK(_value), FORMAT(_value, "{fmt}", "sv-SE"){suffix} & IF(_value > 0, " ▲", IF(_value < 0, " ▼", " –")))''', '@', None)

measures.update({
    'Finans sammanställningsrubrik': ('IF(SELECTEDVALUE(\'Analysaxel\'[Typ], "Land") = "Kategori", "Lönsamhet per kategori", "Lönsamhet per marknad")', '@', None),
    'Finans sammanställning vinst miljoner': ('[Finans sammanställning vinst] / 1000000', '0.00" mn kr"', None),
    'Finans sammanställning tillväxt etikett': ('''VAR _value = [Finans sammanställning tillväxt]
RETURN IF(NOT ISBLANK(_value), FORMAT(_value, "+0.0 %;-0.0 %;0.0 %", "sv-SE") & IF(_value > 0, " ▲", IF(_value < 0, " ▼", " –")))''', '@', None),
    'Finans sammanställning marginalbild': ('''VAR _margin = [Finans sammanställning marginal]
VAR _portion = MIN(1, MAX(0, ABS(_margin)))
VAR _angle = _portion * 2 * PI()
VAR _x = FORMAT(12 + 7 * SIN(_angle), "0.00", "en-US")
VAR _y = FORMAT(14 - 7 * COS(_angle), "0.00", "en-US")
VAR _ink = IF(_margin < 0, "%23B83232", "%230F3163")
RETURN IF(NOT ISBLANK(_margin), "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 96 28'><circle cx='12' cy='14' r='7' fill='%23E7EDF5'/><path d='M12,14 L12,7 A7,7 0 " & IF(_portion > 0.5, "1", "0") & " 1 " & _x & "," & _y & " Z' fill='" & _ink & "'/><text x='25' y='18' font-family='Segoe UI,Arial' font-size='12' fill='%230F3163'>" & FORMAT(_margin, "0.0 %", "sv-SE") & "</text></svg>")''', '@', 'ImageUrl'),
    'Finans sammanställning trend': ('''VAR _months = ADDCOLUMNS(ALLSELECTED('Datum'[Månadsnummer]), "__value", CALCULATE([Finans sammanställning vinst]))
VAR _low = MINX(_months, [__value])
VAR _high = MAXX(_months, [__value])
VAR _points = CONCATENATEX(_months, FORMAT(4 + ('Datum'[Månadsnummer] - 1) * 8, "0", "en-US") & "," & FORMAT(23 - 18 * DIVIDE([__value] - _low, _high - _low, 0.5), "0", "en-US"), " ", 'Datum'[Månadsnummer], ASC)
VAR _last = TOPN(1, _months, 'Datum'[Månadsnummer], DESC)
VAR _lastX = FORMAT(MAXX(_last, 4 + ('Datum'[Månadsnummer] - 1) * 8), "0", "en-US")
VAR _lastY = FORMAT(MAXX(_last, 23 - 18 * DIVIDE([__value] - _low, _high - _low, 0.5)), "0", "en-US")
RETURN IF(NOT ISBLANK([Finans sammanställning vinst]), "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 96 28'><polyline fill='none' stroke='%230F3163' stroke-width='1.3' points='" & _points & "'/><circle cx='" & _lastX & "' cy='" & _lastY & "' r='1.8' fill='%230F3163'/></svg>")''', '@', 'ImageUrl'),
    'Finans gruppvinst miljoner': ("SUMX(VALUES('Finansaxel'[Namn]), CALCULATE([Bruttovinst analys miljoner]))", '0.00" mn kr"', None),
    'Finans gruppnamn': ("SELECTEDVALUE('Finansaxel'[Kategori grupp])", '@', None),
    'Finans månadsaxel max': ('''VAR _groups = CALCULATETABLE(VALUES('Finansaxel'[Kategori grupp]), REMOVEFILTERS('Finansaxel'[Panel]), REMOVEFILTERS('Finansaxel'[Kategori grupp]), REMOVEFILTERS('Finansaxel'[Namn]))
VAR _months = SUMMARIZE(ALLSELECTED('Datum'), 'Datum'[År], 'Datum'[Månadsnummer])
RETURN MAXX(CROSSJOIN(_groups, _months), CALCULATE([Finans gruppvinst miljoner], REMOVEFILTERS('Finansaxel'[Panel]), REMOVEFILTERS('Finansaxel'[Namn]))) * 1.15''', '0.00" mn kr"', None),
    'Finans medel sista månad': ("IF(MAX('Datum'[Månadsnummer]) = MAXX(ALLSELECTED('Datum'), 'Datum'[Månadsnummer]), [Finans månadsmedel])", '0.00" mn kr"', None),
    'Finans medeletikett': ('IF(NOT ISBLANK([Finans medel sista månad]), "Medel")', '@', None),
    'Finans månadsmedel': ('''VAR _dates = ALLSELECTED('Datum')
VAR _months = SUMMARIZE(_dates, 'Datum'[År], 'Datum'[Månadsnummer])
RETURN AVERAGEX(_months, VAR _year = 'Datum'[År] VAR _month = 'Datum'[Månadsnummer]
RETURN CALCULATE([Bruttovinst analys miljoner], REMOVEFILTERS('Datum'), _dates, TREATAS({_year}, 'Datum'[År]), TREATAS({_month}, 'Datum'[Månadsnummer])))''', '0.00" mn kr"', None),
    'Finans över månadsmedel': ('[Bruttovinst analys miljoner] - [Finans månadsmedel]', '0.00" mn kr"', None),
    'Finans vinst över medel': ('IF([Bruttovinst analys miljoner] >= [Finans månadsmedel], [Bruttovinst analys miljoner])', '0.00" mn kr"', None),
    'Finans vinst under medel': ('IF([Bruttovinst analys miljoner] < [Finans månadsmedel], [Bruttovinst analys miljoner])', '0.00" mn kr"', None),
    'Finans antal grupper': ("COUNTROWS(ALLSELECTED('Finansaxel'[Namn]))", '0', None),
    'Finans andelsaxel max': ("MAXX(ALLSELECTED('Kunder'[Land]), CALCULATE([Bruttovinst andel land])) * 1.5", '0.0 %', None),
    'Finans andel återstående': ('[Finans andelsaxel max] - [Bruttovinst andel land]', '0.0 %', None),
    'Finans produktbelopp etikett': ('IF(NOT ISBLANK([Bruttovinst]), FORMAT([Bruttovinst] / 1000000, "0.00", "sv-SE") & " mn kr")', '@', None),
    'Finans produktaxel max': ('MAXX(ALLSELECTED(\'Produkter\'[Produkt]), CALCULATE([Bruttovinst])) * 1.6', '#,##0', None),
    'Finans produktspår återstående': ('IF(NOT ISBLANK([Bruttovinst]), MAX(0, [Finans produktaxel max] * 0.8 - [Bruttovinst]))', '#,##0', None),
    'Finans topprodukter andel etikett': ('''VAR _top = TOPN(5, ALLSELECTED('Produkter'[Produkt]), [Bruttovinst], DESC, 'Produkter'[Produkt], ASC)
VAR _share = DIVIDE(SUMX(_top, [Bruttovinst]), [Bruttovinst])
RETURN IF(NOT ISBLANK(_share), "Topp 5 står för " & FORMAT(_share, "0.0 %", "sv-SE") & " av bruttovinsten")''', '@', None),
    'Finans medelkostnad produkt': ("AVERAGEX(ALLSELECTED('Produkter'[Produkt]), CALCULATE([Kostnad miljoner]))", '0.00" mn kr"', None),
    'Finans medelvinst produkt': ("AVERAGEX(ALLSELECTED('Produkter'[Produkt]), CALCULATE([Bruttovinst miljoner]))", '0.00" mn kr"', None),
    'Finans marknadstillväxt etikett': ('''VAR _value = [Bruttovinst YoY]
RETURN IF(NOT ISBLANK(_value), FORMAT(_value, "+0.0 %;-0.0 %;0.0 %", "sv-SE") & IF(_value > 0, " ▲", IF(_value < 0, " ▼", " –")))''', '@', None),
    'Finans marknadstrend': ('''VAR _months = ADDCOLUMNS(ALLSELECTED('Datum'[Månadsnummer]), "__value", CALCULATE([Bruttovinst]))
VAR _low = MINX(_months, [__value])
VAR _high = MAXX(_months, [__value])
VAR _points = CONCATENATEX(_months, FORMAT(4 + ('Datum'[Månadsnummer] - 1) * 8, "0", "en-US") & "," & FORMAT(23 - 18 * DIVIDE([__value] - _low, _high - _low, 0.5), "0", "en-US"), " ", 'Datum'[Månadsnummer], ASC)
RETURN IF(NOT ISBLANK([Bruttovinst]), "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 96 28'><polyline fill='none' stroke='%230F3163' stroke-width='1.5' points='" & _points & "'/></svg>")''', '@', 'ImageUrl'),
})
for name, driver, fmt in [('vinst', 'Bruttovinst', '#,##0" kr"'), ('marginal', 'Bruttomarginal', '0.0 %'), ('tillväxt', 'Bruttovinst YoY', '+0.0 %;-0.0 %;0.0 %')]:
    measures['Finans sammanställning ' + name] = (f'''VAR _names = VALUES('Analysaxel'[Namn])
RETURN IF(SELECTEDVALUE('Analysaxel'[Typ], "Land") = "Land", CALCULATE([{driver}], KEEPFILTERS(TREATAS(_names, 'Kunder'[Land]))), CALCULATE([{driver}], KEEPFILTERS(TREATAS(_names, 'Produkter'[Kategori]))))''', fmt, None)
for rank in range(1, 5):
    pool = "VAR _pool = FILTER(ADDCOLUMNS(ALLSELECTED('Kunder'[Land]), \"__profit\", CALCULATE([Bruttovinst])), NOT ISBLANK([__profit]))"
    selected = pool + f"\nVAR _row = TOPN(1, TOPN({rank}, _pool, [__profit], DESC, 'Kunder'[Land], ASC), [__profit], ASC, 'Kunder'[Land], DESC)\nVAR _enough = COUNTROWS(_pool) >= {rank}"
    measures[f'Finans marknad {rank} etikett'] = (selected + '''
VAR _profit = SUMX(_row, [__profit])
VAR _share = DIVIDE(_profit, [Bruttovinst])
RETURN IF(_enough, MAXX(_row, 'Kunder'[Land]) & " | " & FORMAT(_profit / 1000000, "0.00", "sv-SE") & " mn kr (" & FORMAT(_share, "0.0 %", "sv-SE") & ")")''', '@', None)
    measures[f'Finans marknad {rank} andel'] = (selected + '\nRETURN IF(_enough, DIVIDE(SUMX(_row, [__profit]), [Bruttovinst]))', '0.0 %', None)

for rank in range(1, 6):
    measures[f'Finans produkt {rank} belopp'] = (f'''VAR _pool = FILTER(ADDCOLUMNS(ALLSELECTED('Produkter'[Produkt]), "__profit", CALCULATE([Bruttovinst])), NOT ISBLANK([__profit]))
VAR _row = TOPN(1, TOPN({rank}, _pool, [__profit], DESC, 'Produkter'[Produkt], ASC), [__profit], ASC, 'Produkter'[Produkt], DESC)
RETURN IF(COUNTROWS(_pool) >= {rank}, FORMAT(SUMX(_row, [__profit]) / 1000000, "0.00", "sv-SE") & " mn kr")''', '@', None)

for name, (expr, fmt, category) in measures.items():
    if category == 'ImageUrl':
        expr = expr.replace('%230F3163', 'rgb(15,49,99)').replace('%23E7EDF5', 'rgb(231,237,245)').replace('%23B83232', 'rgb(184,50,50)')
    if name != 'Finans gruppvinst miljoner':
        expr = expr.replace('[Bruttovinst analys miljoner]', '[Finans gruppvinst miljoner]')
    text = re.sub(r"\n\tmeasure '" + re.escape(name) + r"' =.*?(?=\n\tmeasure |\n\tcolumn |\n\tpartition |\Z)", '', text, flags=re.S)
    dax = '\n'.join('\t\t\t' + line for line in expr.splitlines())
    block = f"\n\tmeasure '{name}' =\n{dax}\n\t\tformatString: {fmt}\n\t\tisHidden\n\t\tdisplayFolder: Ekonomi och lönsamhet\\Presentation\n"
    if category:
        block += f'\t\tdataCategory: {category}\n'
    text = text.replace('\n\tcolumn ', block + '\n\tcolumn ', 1)
path.write_text(text, encoding='utf-8')
print(f'Upserted {len(measures)} finance presentation measures.')

# A short month label keeps twelve months legible inside the small multiples.
date_path = path.with_name('Datum.tmdl')
date_text = date_path.read_text(encoding='utf-8')
if "column 'Månad kort'" not in date_text:
    date_text = date_text.replace('\n\tpartition ', '''
\tcolumn 'Månad kort' = FORMAT('Datum'[Datum], "mmm", "sv-SE")
\t\tdataType: string
\t\tsummarizeBy: none
\t\tsortByColumn: Månadsnummer

\tpartition ''', 1)
    date_path.write_text(date_text, encoding='utf-8')

axis_path = path.with_name('Finansaxel.tmdl')
axis_text = axis_path.read_text(encoding='utf-8')
if 'column Val' not in axis_text:
    axis_text = axis_text.replace('\n\tpartition ', '''
\tcolumn Val = IF('Finansaxel'[Typ] = "Säljteam", "Team", 'Finansaxel'[Typ])
\t\tdataType: string
\t\tsummarizeBy: none

\tpartition ''', 1)
    axis_path.write_text(axis_text, encoding='utf-8')

if "column 'Kategori grupp'" not in axis_text:
    axis_text = axis_text.replace('\n\tpartition ', '''
\tcolumn 'Kategori grupp' = IF('Finansaxel'[Typ] = "Kategori" && NOT('Finansaxel'[Namn] IN {"Elektronik", "Hem och kök"}), "Övrigt", 'Finansaxel'[Namn])
\t\tdataType: string
\t\tsummarizeBy: none

\tpartition ''', 1)
    axis_path.write_text(axis_text, encoding='utf-8')

if 'column Panel' not in axis_text:
    axis_text = axis_text.replace('\n\tpartition ', '''
\tcolumn Panel = SWITCH('Finansaxel'[Namn], "Nord", 1, "Syd", 2, "Väst", 3, "Elektronik", 1, "Hem och kök", 2, 3)
\t\tdataType: int64
\t\tsummarizeBy: none

\tpartition ''', 1)
    axis_path.write_text(axis_text, encoding='utf-8')

if "column 'Månad bokstav'" not in date_text:
    date_text = date_text.replace('\n\tpartition ', '''
\tcolumn 'Månad bokstav' = UPPER(LEFT(FORMAT('Datum'[Datum], "mmm", "sv-SE"), 1)) & REPT(UNICHAR(8203), 'Datum'[Månadsnummer])
\t\tdataType: string
\t\tsummarizeBy: none
\t\tsortByColumn: Månadsnummer

\tpartition ''', 1)
    date_path.write_text(date_text, encoding='utf-8')

summary_path = path.with_name('Analysaxel.tmdl')
summary_text = summary_path.read_text(encoding='utf-8')
if 'column Område' not in summary_text:
    summary_text = summary_text.replace('\n\tpartition ', '''
\tcolumn Område = IF('Analysaxel'[Typ] = "Kategori" && NOT('Analysaxel'[Namn] IN {"Elektronik", "Hem och kök"}), "Övrigt", 'Analysaxel'[Namn])
\t\tdataType: string
\t\tsummarizeBy: none

\tpartition ''', 1)
    summary_path.write_text(summary_text, encoding='utf-8')

product_path = path.with_name('Produkter.tmdl')
product_text = product_path.read_text(encoding='utf-8')
if 'column Finansgrupp' not in product_text:
    product_text = product_text.replace('\n\tpartition ', '''
\tcolumn Finansgrupp = IF('Produkter'[Kategori] IN {"Elektronik", "Hem och kök"}, 'Produkter'[Kategori], "Övrigt")
\t\tdataType: string
\t\tsummarizeBy: none

\tpartition ''', 1)
    product_path.write_text(product_text, encoding='utf-8')
