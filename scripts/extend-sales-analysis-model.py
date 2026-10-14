"""Presentation measures for Sales Analytics. Sources and base measures are preserved."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
path = root / 'powerbi-sales-finance/AubecoSalesFinance.SemanticModel/definition/tables/Försäljning.tmdl'
measures = {}
def add(name, expression, fmt='@', category=None):
    measures['Säljanalys ' + name] = (expression, fmt, category)

drivers = ['Aktiva säljare årsförändring', 'Omsättning per säljare årsförändring', 'Leveranser YoY', 'Genomsnittlig order årsförändring', 'Topp 5 andel förändring']
for i, driver in enumerate(drivers):
    fmt = '+0.0" pp";-0.0" pp";0.0" pp"' if i == 4 else '+0.0 %;-0.0 %;0.0 %'
    add(f'KPI {i} förändring', f'''VAR _value = [{driver}]
RETURN IF(NOT ISBLANK(_value), IF(_value = 0, "Oförändrat mot föreg. år", FORMAT(_value, "{fmt.replace(chr(34), chr(34)*2)}", "sv-SE") & IF(_value > 0, " ▲", " ▼") & " mot föreg. år"))''')
    favorable = '_value > 0'
    add(f'KPI {i} färg', f'''VAR _value = [{driver}]
RETURN IF(ISBLANK(_value) || _value = 0, "#5B6B80", IF({favorable}, "#187447", "#B83232"))''')

add('marknad tillväxt etikett', '''VAR _value = [Tillväxt mot föregående år]
RETURN IF(NOT ISBLANK(_value), FORMAT(_value, "+0.0 %;-0.0 %;0.0 %", "sv-SE") & IF(_value > 0, " ▲", IF(_value < 0, " ▼", " –")))''')
add('marknad tillväxt färg', 'IF([Tillväxt mot föregående år] < 0, "#B83232", "#187447")')
add('marknad andelsbild', '''VAR _share = [Omsättning andel land]
VAR _bounded = MIN(1, MAX(0, _share))
VAR _offset = FORMAT(31.416 * (1 - _bounded), "0.00", "en-US")
RETURN IF(NOT ISBLANK(_share), "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 96 28'><circle cx='9' cy='14' r='5' fill='rgb(231,237,245)'/><circle cx='9' cy='14' r='2.5' fill='none' stroke='rgb(15,49,99)' stroke-width='5' stroke-dasharray='15.708' stroke-dashoffset='" & FORMAT(15.708 * (1 - _bounded), "0.00", "en-US") & "' transform='rotate(-90 9 14)'/><text x='21' y='18' font-family='Segoe UI' font-size='16' fill='rgb(15,49,99)'>" & FORMAT(_share, "0.0 %", "sv-SE") & "</text></svg>")''', category='ImageUrl')

add('gruppomsättning', '''VAR _names = VALUES('Analysaxel'[Namn])
RETURN IF(SELECTEDVALUE('Analysaxel'[Typ], "Land") = "Land",
 CALCULATE([Omsättning], KEEPFILTERS(TREATAS(_names, 'Kunder'[Land]))),
 CALCULATE([Omsättning], KEEPFILTERS(TREATAS(_names, 'Produkter'[Kategori]))))''', '#,##0" kr"')
add('trendrubrik', 'IF(SELECTEDVALUE(\'Analysaxel\'[Typ], "Land") = "Land", "Omsättningstrend per marknad", "Omsättningstrend per kategori")')
group_pool = '''VAR _dates = ALLSELECTED('Datum')
VAR _pool = FILTER(ADDCOLUMNS(ALLSELECTED('Analysaxel'[Område]), "__value", CALCULATE([Säljanalys gruppomsättning], REMOVEFILTERS('Datum'), _dates)), [__value] > 0)'''
for quarter in range(1, 5):
    add(f'kvartal {quarter}', f'IF(COUNTROWS(VALUES(\'Datum\'[Månadsnummer])) = 12, "K{quarter}", UNICHAR(8203))')

for rank in range(1, 5):
    chosen = group_pool + f'''
VAR _chosen = TOPN(1, TOPN({rank}, _pool, [__value], DESC, 'Analysaxel'[Område], ASC), [__value], ASC, 'Analysaxel'[Område], DESC)
VAR _name = MAXX(_chosen, 'Analysaxel'[Område])
VAR _enough = COUNTROWS(_pool) >= {rank}'''
    add(f'trend {rank} namn', chosen + '\nRETURN IF(_enough, _name)')
    add(f'trend {rank} värde', chosen + "\nRETURN IF(_enough, CALCULATE([Säljanalys gruppomsättning], KEEPFILTERS(TREATAS({_name}, 'Analysaxel'[Område]))))", '#,##0" kr"')
    for extreme, fn in [('max', 'MAXX'), ('min', 'MINX')]:
        add(f'trend {rank} {extreme}', f'''VAR _name = [Säljanalys trend {rank} namn]
VAR _dates = ALLSELECTED('Datum')
VAR _months = SUMMARIZE(_dates, 'Datum'[År], 'Datum'[Månadsnummer])
VAR _limit = {fn}(_months, VAR _year = 'Datum'[År] VAR _month = 'Datum'[Månadsnummer]
 RETURN CALCULATE([Säljanalys gruppomsättning], REMOVEFILTERS('Datum'), _dates, TREATAS({{_year}}, 'Datum'[År]), TREATAS({{_month}}, 'Datum'[Månadsnummer]), KEEPFILTERS(TREATAS({{_name}}, 'Analysaxel'[Område]))))
VAR _value = [Säljanalys trend {rank} värde]
RETURN IF(NOT ISBLANK(_value) && ABS(_value - _limit) < 0.01, _value)''', '#,##0" kr"')

add('stapelfärg', '''VAR _dates = ALLSELECTED('Datum')
VAR _months = SUMMARIZE(_dates, 'Datum'[År], 'Datum'[Månadsnummer])
VAR _max = MAXX(_months, CALCULATE([Omsättning], REMOVEFILTERS('Datum'), _dates, 'Datum'[År] = EARLIER('Datum'[År]), 'Datum'[Månadsnummer] = EARLIER('Datum'[Månadsnummer])))
RETURN IF([Omsättning] = _max, "#0F3163", "#E4E7EC")''')

for label, base in [('omsättning', 'Omsättning'), ('bruttovinst', 'Bruttovinst')]:
    for extreme, fn in [('max', 'MAXX'), ('min', 'MINX')]:
        add(f'{label} {extreme} vald period', f'''VAR _dates = ALLSELECTED('Datum')
VAR _months = SUMMARIZE(_dates, 'Datum'[År], 'Datum'[Månadsnummer])
RETURN {fn}(_months, VAR _year = 'Datum'[År] VAR _month = 'Datum'[Månadsnummer]
 RETURN CALCULATE([{base}], REMOVEFILTERS('Datum'), _dates, TREATAS({{_year}}, 'Datum'[År]), TREATAS({{_month}}, 'Datum'[Månadsnummer])))''', '#,##0" kr"')
add('omsättning övriga månader', 'VAR _value = [Omsättning] RETURN IF(NOT ISBLANK(_value) && ABS(_value - [Säljanalys omsättning max vald period]) >= 0.01, _value / 1000000)', '0.0" mn kr"')
add('omsättning toppmånad', 'VAR _value = [Omsättning] RETURN IF(NOT ISBLANK(_value) && ABS(_value - [Säljanalys omsättning max vald period]) < 0.01, _value / 1000000)', '0.0" mn kr"')
for extreme in ['max', 'min']:
    add(f'bruttovinst {extreme} punkt', f'VAR _value = [Bruttovinst] RETURN IF(NOT ISBLANK(_value) && ABS(_value - [Säljanalys bruttovinst {extreme} vald period]) < 0.01, _value / 1000000)', '0.0" mn kr"')

seller_pool = '''VAR _pool = FILTER(ADDCOLUMNS(ALLSELECTED('Säljare'), "__sales", CALCULATE([Omsättning])), [__sales] > 0)'''
for rank in range(1, 8):
    selected = seller_pool + f'''
VAR _seller = TOPN(1, TOPN({rank}, _pool, [__sales], DESC, 'Säljare'[Säljarnyckel], ASC), [__sales], ASC, 'Säljare'[Säljarnyckel], DESC)
VAR _enough = COUNTROWS(_pool) >= {rank}'''
    add(f'säljare {rank} namn', selected + "\nRETURN IF(_enough, MAXX(_seller, 'Säljare'[Säljare]))")
    add(f'säljare {rank} belopp', selected + '\nRETURN IF(_enough, SUMX(_seller, [__sales]))', '#,##0" kr"')
    add(f'säljare {rank} tillväxt', selected + '''
VAR _current = SUMX(_seller, [__sales])
VAR _prior = SUMX(_seller, CALCULATE([Omsättning föregående år]))
RETURN IF(_enough, DIVIDE(_current - _prior, _prior))''', '+0.0 %;-0.0 %;0.0 %')
    add(f'säljare {rank} initialer', f'''VAR _name = [Säljanalys säljare {rank} namn]
RETURN IF(NOT ISBLANK(_name), LEFT(_name, 1) & MID(_name, SEARCH(" ", _name, 1, LEN(_name)) + 1, 1))''')
    add(f'säljare {rank} belopp etikett', f'''VAR _value = [Säljanalys säljare {rank} belopp]
RETURN IF(NOT ISBLANK(_value), FORMAT(_value / 1000000, "0.00", "sv-SE") & " mn kr")''')
    add(f'säljare {rank} tillväxt etikett', f'''VAR _value = [Säljanalys säljare {rank} tillväxt]
RETURN IF(NOT ISBLANK(_value), FORMAT(_value, "+0.0 %;-0.0 %;0.0 %", "sv-SE") & IF(_value > 0, " ▲", IF(_value < 0, " ▼", " –")) & " mot föreg. år")''')
    add(f'säljare {rank} segment', f'''VAR _value = [Säljanalys säljare {rank} belopp]
RETURN IF(NOT ISBLANK(_value), REPT(UNICHAR(9648), MAX(1, ROUNDUP(18 * DIVIDE(_value, [Säljanalys säljare 1 belopp]), 0))))''')

for rank in range(1, 5):
    add(f'trend {rank} bild', f'''VAR _name = [Säljanalys trend {rank} namn]
VAR _dates = ALLSELECTED('Datum')
VAR _months = SUMMARIZE(_dates, 'Datum'[År], 'Datum'[Månadsnummer])
VAR _values = ADDCOLUMNS(_months, "__v", VAR _year = 'Datum'[År] VAR _month = 'Datum'[Månadsnummer] RETURN CALCULATE([Säljanalys gruppomsättning], REMOVEFILTERS('Datum'), TREATAS({{_year}}, 'Datum'[År]), TREATAS({{_month}}, 'Datum'[Månadsnummer]), TREATAS({{_name}}, 'Analysaxel'[Område])))
VAR _min = MINX(_values, [__v])
VAR _max = MAXX(_values, [__v])
VAR _first = MINX(_months, 'Datum'[Månadsnummer])
VAR _last = MAXX(_months, 'Datum'[Månadsnummer])
VAR _scaled = ADDCOLUMNS(_values, "__x", 8 + 308*DIVIDE('Datum'[Månadsnummer]-_first, _last-_first, 0.5))
VAR _points = CONCATENATEX(_scaled, FORMAT([__x], "0.0", "en-US") & "," & FORMAT(22 - 18*DIVIDE([__v]-_min, _max-_min, 0.5), "0.0", "en-US"), " ", 'Datum'[Månadsnummer], ASC)
VAR _markers = CONCATENATEX(FILTER(_scaled, ABS([__v]-_max)<0.01 || ABS([__v]-_min)<0.01), "<circle cx='" & FORMAT([__x], "0.0", "en-US") & "' cy='" & FORMAT(22 - 18*DIVIDE([__v]-_min,_max-_min,0.5), "0.0", "en-US") & "' r='2.2' fill='" & IF(ABS([__v]-_max)<0.01,"rgb(24,116,71)","rgb(184,50,50)") & "'/>", "")
VAR _area = IF(COUNTROWS(_months) > 1, "<polygon points='8,26 " & _points & " 316,26' fill='rgb(231,237,245)'/>")
RETURN IF(NOT ISBLANK(_name), "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 324 28'>" & _area & "<polyline points='" & _points & "' fill='none' stroke='rgb(15,49,99)' stroke-width='1.5'/>" & _markers & "</svg>")''', category='ImageUrl')

for rank in range(1, 5):
    add(f'trend {rank} namn etikett', f'COALESCE([Säljanalys trend {rank} namn], UNICHAR(8203))')

text = path.read_text(encoding='utf-8')
for name, (expression, fmt, category) in measures.items():
    text = re.sub(r"\n\tmeasure '" + re.escape(name) + r"' =.*?(?=\n\tmeasure |\n\tcolumn |\n\tpartition |\Z)", '', text, flags=re.S)
    dax = '\n'.join('\t\t\t' + line for line in expression.splitlines())
    block = f"\n\tmeasure '{name}' = ```\n{dax}\n\t\t\t```\n\t\tformatString: {fmt}\n\t\tisHidden\n\t\tdisplayFolder: Försäljningsanalys\\Presentation\n"
    if category:
        block += f'\t\tdataCategory: {category}\n'
    text = text.replace('\n\tcolumn ', block + '\n\tcolumn ', 1)
path.write_text(text, encoding='utf-8')
print(f'Upserted {len(measures)} sales-analysis presentation measures; sources unchanged.')



