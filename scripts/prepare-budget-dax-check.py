from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
text=(root/'powerbi/AubecoHandel.SemanticModel/definition/tables/Försäljning.tmdl').read_text(encoding='utf-8-sig')
definitions=[]
for name,expression in re.findall(r"\tmeasure '([^']+)' =\n(.*?)\n\t\tformatString:",text,re.S):
    if name not in ['Planering bas','Planering justerad','Planerad omsättning','Resultat utfall','Resultat budget','Resultatrad bakgrund']:continue
    expression='\n'.join(line.removeprefix('\t\t\t') for line in expression.splitlines())
    definitions.append(f"MEASURE 'Försäljning'[{name}] = {expression}")
query=(root/'powerbi/validation/budget-diagnostic.dax').read_text(encoding='utf-8')
(root/'powerbi/validation/budget-fixed-check.dax').write_text('DEFINE\n'+'\n'.join(definitions)+'\n'+query,encoding='utf-8')
assert len(definitions)==6
