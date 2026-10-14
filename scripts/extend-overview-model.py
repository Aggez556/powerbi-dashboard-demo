"""One measure required by the reference's market-bar growth labels."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
path = root / 'powerbi-sales-finance/AubecoSalesFinance.SemanticModel/definition/tables/Försäljning.tmdl'
text = path.read_text(encoding='utf-8')
name = 'Analys årsförändring'
text = re.sub(r"\n\tmeasure '" + name + r"' =.*?(?=\n\tmeasure |\n\tcolumn |\n\tpartition |\Z)", '', text, flags=re.S)
block = '''
	measure 'Analys årsförändring' = DIVIDE([Analysvärde] - [Analys föregående år], [Analys föregående år])
		formatString: +0.0 %;-0.0 %;0.0 %
		displayFolder: Ledningsöversikt
'''
path.write_text(text.replace('\n\tcolumn ', block + '\n\tcolumn ', 1), encoding='utf-8')
print('Added market growth measure; data unchanged.')
labels = {
    'Marknadsbelopp etikett': 'FORMAT([Analysvärde] / 1000000, "0.00", "sv-SE") & " mn kr"',
    'Omsättning etikett': 'FORMAT([Omsättning] / 1000000, "0.00", "sv-SE") & " mn kr"',
    'Produktvärde etikett': 'IF(SELECTEDVALUE(\'Produktval\'[Mått], "Omsättning") = "Sålda enheter", FORMAT([Produktvärde], "#,##0", "sv-SE") & " st", FORMAT([Produktvärde] / 1000000, "0.00", "sv-SE") & " mn kr")',
}
text = path.read_text(encoding='utf-8')
for label, expr in labels.items():
    text = re.sub(r"\n\tmeasure '" + label + r"' =.*?(?=\n\tmeasure |\n\tcolumn |\n\tpartition |\Z)", '', text, flags=re.S)
    block = f"\n\tmeasure '{label}' = {expr}\n\t\tformatString: @\n\t\tdisplayFolder: Ledningsöversikt\n"
    text = text.replace('\n\tcolumn ', block + '\n\tcolumn ', 1)
path.write_text(text, encoding='utf-8')
print('Added three Swedish display labels; numerical measures unchanged.')

# Scalar rank measures let independent native cards share one deterministic seller ranking.
pool = '''VAR _pool = FILTER(ADDCOLUMNS(ALLSELECTED('Säljare'), "__sales", CALCULATE([Omsättning])), [__sales] > 0)'''
seller_measures = {}
for rank in range(1, 4):
    selected = pool + f'''\nVAR _seller = TOPN(1, TOPN({rank}, _pool, [__sales], DESC, 'Säljare'[Säljarnyckel], ASC), [__sales], ASC, 'Säljare'[Säljarnyckel], DESC)
VAR _enough = COUNTROWS(_pool) >= {rank}'''
    seller_measures[f'Säljartopp {rank} namn'] = (selected + "\nRETURN IF(_enough, MAXX(_seller, 'Säljare'[Säljare]))", '@')
    seller_measures[f'Säljartopp {rank} belopp'] = (selected + '\nRETURN IF(_enough, SUMX(_seller, [__sales]))', '#,##0" kr"')
    seller_measures[f'Säljartopp {rank} förändring'] = (selected + '''
VAR _sales = SUMX(_seller, [__sales])
VAR _prior = SUMX(_seller, CALCULATE([Omsättning föregående år]))
RETURN IF(_enough, DIVIDE(_sales - _prior, _prior))''', '+0.0 %;-0.0 %;0.0 %')
    seller_measures[f'Säljartopp {rank} initialer'] = (f'''VAR _name = [Säljartopp {rank} namn]
RETURN IF(NOT ISBLANK(_name), LEFT(_name, 1) & MID(_name, SEARCH(" ", _name, 1, LEN(_name)) + 1, 1))''', '@')
    seller_measures[f'Säljartopp {rank} etikett'] = (f'''VAR _value = [Säljartopp {rank} belopp]
RETURN IF(NOT ISBLANK(_value), FORMAT(_value / 1000000, "0.00", "sv-SE") & " mn kr")''', '@')
    seller_measures[f'Säljartopp {rank} förändring etikett'] = (f'''VAR _value = [Säljartopp {rank} förändring]
RETURN IF(NOT ISBLANK(_value), FORMAT(_value, "+0.0 %;-0.0 %;0.0 %", "sv-SE") & IF(_value > 0, " ▲", IF(_value < 0, " ▼", " –")) & " mot föreg. år")''', '@')
    seller_measures[f'Säljartopp {rank} segment'] = (f'''VAR _value = [Säljartopp {rank} belopp]
RETURN IF(NOT ISBLANK(_value), REPT(UNICHAR(9648), MAX(1, ROUNDUP(18 * DIVIDE(_value, [Säljartopp 1 belopp]), 0))))''', '@')
seller_measures['Säljartopp andel etikett'] = (pool + '''
VAR _top = TOPN(3, _pool, [__sales], DESC, 'Säljare'[Säljarnyckel], ASC)
VAR _share = DIVIDE(SUMX(_top, [__sales]), [Omsättning])
RETURN IF(NOT ISBLANK(_share), "Topp 3 står för " & FORMAT(_share, "0.0 %", "sv-SE") & " av omsättningen")''', '@')
seller_measures['Produktaxel max'] = ('''VAR _max = MAXX(ALLSELECTED('Produkter'[Produkt]), CALCULATE([Produktvärde]))
RETURN IF(_max > 0, _max * 1.28)''', '#,##0')
for index, driver in enumerate(['Tillväxt mot föregående år', 'Enheter YoY', 'Bruttovinst YoY', 'Marginal förändring', 'Leveranser YoY']):
    fmt = '+0.0" pp";-0.0" pp";0.0" pp"' if index == 3 else '+0.0 %;-0.0 %;0.0 %'
    quoted_fmt = fmt.replace('"', '""')
    seller_measures[f'KPI förändring {index} etikett'] = (f'''VAR _value = [{driver}]
RETURN IF(NOT ISBLANK(_value), FORMAT(_value, "{quoted_fmt}", "sv-SE") & IF(_value > 0, " ▲", IF(_value < 0, " ▼", " –")))''', '@')
text = path.read_text(encoding='utf-8')
for name, (expr, fmt) in seller_measures.items():
    text = re.sub(r"\n\tmeasure '" + re.escape(name) + r"' =.*?(?=\n\tmeasure |\n\tcolumn |\n\tpartition |\Z)", '', text, flags=re.S)
    dax = '\n'.join('\t\t\t' + line for line in expr.splitlines())
    block = f"\n\tmeasure '{name}' = ```\n{dax}\n\t\t\t```\n\t\tformatString: {fmt}\n\t\tisHidden\n\t\tdisplayFolder: Ledningsöversikt\\Säljartopp\n"
    text = text.replace('\n\tcolumn ', block + '\n\tcolumn ', 1)
path.write_text(text, encoding='utf-8')
print('Added dynamic top-three seller presentation measures; Import data unchanged.')
