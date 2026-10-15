from pathlib import Path
import re
p=Path(__file__).resolve().parents[1]/'powerbi-ledningsrapport/Ledningsrapport.SemanticModel/definition/tables/Planinställning.tmdl'
s=p.read_text(encoding='utf-8-sig')
points='''VAR _points=GENERATE(ALLSELECTED('Trendaxel'),
VAR _technical=[Trend teknisk] VAR _staffing=[Trend bemanning]
VAR _target=[Trend mål] VAR _selected=[Trend vald månad]
RETURN UNION(ROW("Value",_technical),ROW("Value",_staffing),ROW("Value",_target),ROW("Value",_selected)))
VAR _valid=FILTER(_points,NOT ISBLANK([Value]))
VAR _low=MINX(_valid,[Value]) VAR _high=MAXX(_valid,[Value])
VAR _padding=MAX(.03,(_high-_low)*.15)
'''
for name,tail in [('Trend axel min','MAX(0,FLOOR(_low-_padding,.05))'),('Trend axel max','CEILING(_high+_padding,.05)')]:
 expr=points+'RETURN IF(COUNTROWS(_valid)>0,'+tail+')'
 block="\tmeasure '"+name+"' = ```\n"+''.join('\t\t\t'+line+'\n' for line in expr.splitlines())+'\t\t\t```\n\t\tformatString: 0 %\n\t\tdisplayFolder: Uppdrag\n'
 if "measure '"+name+"'" in s:s=re.sub(r"\tmeasure '"+name+r"' =\s*.*?(?=\n\t(?:measure|column|partition) |\Z)",lambda _:block,s,flags=re.S)
 else:s=s.replace('\n\tcolumn ','\n'+block+'\n\tcolumn ',1)
p.write_text(s,encoding='utf-8')
print('Added filtered min/max axis bounds, including target and selected month, with padding.')
