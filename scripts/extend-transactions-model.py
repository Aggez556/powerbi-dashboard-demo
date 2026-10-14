from pathlib import Path
import re
p=Path('powerbi-sales-finance/AubecoSalesFinance.SemanticModel/definition/tables/Försäljning.tmdl')
s=p.read_text(encoding='utf-8-sig')
name='Transaktion marginalspår'
expression='''VAR _margin = [Bruttomarginal]
VAR _length = MIN(1, ABS(_margin)) * 60
VAR _left = IF(_margin < 0, 60 - _length, 60)
VAR _color = IF(_margin < 0, "rgb(184,50,50)", "rgb(24,116,71)")
RETURN IF(NOT ISBLANK(_margin), "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 22'><rect x='0' y='6' width='120' height='10' rx='5' fill='rgb(232,232,232)'/><rect x='" & FORMAT(_left, "0.00", "en-US") & "' y='6' width='" & FORMAT(_length, "0.00", "en-US") & "' height='10' rx='5' fill='" & _color & "'/><path d='M60 4v14' stroke='rgb(189,195,203)' stroke-width='0.7'/></svg>")'''
block="\tmeasure '"+name+"' =\n"+'\n'.join('\t\t\t'+line for line in expression.splitlines())+'''\n\t\tformatString: @
\t\tisHidden
\t\tdisplayFolder: Transaktioner\\Presentation
\t\tlineageTag: 1a7ee464-5c88-45f5-978a-d4e697b8dcbd
\t\tdataCategory: ImageUrl

'''
s=re.sub(r"\tmeasure 'Transaktion marginalspår' =.*?(?=\t(?:measure |column |partition )|\Z)",'',s,flags=re.S)
s=s.replace('\tcolumn Radnyckel',block+'\tcolumn Radnyckel',1)
p.write_text(s,encoding='utf-8')
