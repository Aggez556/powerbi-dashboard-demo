from pathlib import Path
import re
base=Path(__file__).resolve().parents[1]/'powerbi-ledningsrapport'
s=(base/'Ledningsrapport.SemanticModel/definition/tables/Planinställning.tmdl').read_text(encoding='utf-8-sig')
definitions=[]
for name in ['Trend axel min','Trend axel max']:
 expr=re.search(r"measure '"+name+r"' = ```\n(.*?)\n\s*```",s,re.S).group(1)
 definitions.append("MEASURE 'Planinställning'["+name+'] = '+expr)
p=base/'validation/assignment-axis-check.dax';query=p.read_text(encoding='utf-8')
query=query[query.index('EVALUATE'):]
p.write_text('DEFINE\n'+'\n'.join(definitions)+'\n'+query,encoding='utf-8')
print('Prepared read-only DAX validation of persisted axis formulas against live trend data.')
