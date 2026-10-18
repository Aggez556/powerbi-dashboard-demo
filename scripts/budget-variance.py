"""Add a favourable/unfavourable percentage indicator, preserving lineage."""
from pathlib import Path
import re
BASE=Path(__file__).resolve().parents[1]/'powerbi-ledningsrapport'
p=BASE/'Ledningsrapport.SemanticModel/definition/tables/Budgetrapportnoder.tmdl'
s=p.read_text(encoding='utf-8-sig')
expression='''VAR _rad=SELECTEDVALUE('Budgetrapportnoder'[Rad])
VAR _sub=SELECTEDVALUE('Budgetrapportnoder'[Undergrupp])
VAR _post=SELECTEDVALUE('Budgetrapportnoder'[Post])
VAR _ids=SELECTCOLUMNS(FILTER(ALL('Budgetrader'),'Budgetrader'[Rad]=_rad && (_sub="" || 'Budgetrader'[Undergrupp]=_sub) && (_post="" || 'Budgetrader'[Post]=_post)),"KontoID",'Budgetrader'[KontoID])
VAR _mode=[Budget jämförelseläge]
VAR _a=CALCULATE([RR rad A],REMOVEFILTERS('Budgetrader'),TREATAS(_ids,'Budgetrader'[KontoID]))
VAR _b=IF(_mode=1,CALCULATE([RR rad utfall],REMOVEFILTERS('Budgetrader'),TREATAS(_ids,'Budgetrader'[KontoID])),CALCULATE([RR rad B],REMOVEFILTERS('Budgetrader'),TREATAS(_ids,'Budgetrader'[KontoID])))
VAR _difference=IF(_mode=1,_b-_a,_a-_b)
VAR _reference=IF(_mode=1,_a,_b)
RETURN IF(HASONEVALUE('Budgetrapportnoder'[NodID]) && SELECTEDVALUE('Budgetkolumner'[Position])=3 && [Budget kolumn synlig]=1 && NOT ISBLANK(_a) && NOT ISBLANK(_b),IF(SELECTEDVALUE('Budgetrapportnoder'[Typ])="marginal",_difference*100,DIVIDE(_difference,ABS(_reference))))'''
text='''VAR _v=[Rapportvärde] VAR _slot=SELECTEDVALUE('Budgetkolumner'[Position])
VAR _margin=SELECTEDVALUE('Budgetrapportnoder'[Typ])="marginal"
VAR _variance=[Rapportavvikelse]
VAR _rounded=IF(_margin,ROUND(_variance,1),DIVIDE(ROUND(_variance*100,1),100))
RETURN IF(ISBLANK(_v),BLANK(),IF(_slot=3,IF(ISBLANK(_variance),"—",IF(_margin,FORMAT(_rounded,"+0.0;−0.0;0.0","sv-SE") & " pp",FORMAT(_rounded,"+0.0 %;−0.0 %;0.0 %","sv-SE"))),IF(_margin,FORMAT(_v,"0.0 %","sv-SE"),FORMAT(_v,"#,##0;−#,##0;0","sv-SE"))))'''
colour='''VAR _v=[Rapportvärde] VAR _variance=[Rapportavvikelse]
VAR _rounded=ROUND(IF(SELECTEDVALUE('Budgetrapportnoder'[Typ])="marginal",_variance,_variance*100),1)
RETURN IF(ISBLANK(_v),BLANK(),IF(SELECTEDVALUE('Budgetkolumner'[Position])=3,IF(ISBLANK(_variance) || _rounded=0,"#5B6B80",IF(_rounded>0,"#007956","#B42318")),IF(SELECTEDVALUE('Budgetrapportnoder'[Typ])="marginal","#5B6B80","#0F3163")))'''
for name,expr,fmt in [('Rapportavvikelse',expression,'0.0 %'),('Rapporttext',text,'@'),('Rapportfärg',colour,'@')]:
 body="\tmeasure '"+name+"' = ```\n"+''.join('\t\t\t'+line+'\n' for line in expr.splitlines())+'\t\t\t```'
 pattern=r"\tmeasure '?"+name+r"'? =\s*.*?(?=\n\t\tformatString:)"
 if re.search(pattern,s,re.S):s=re.sub(pattern,lambda _:body,s,flags=re.S)
 else:s=s.replace('\n\tcolumn ', '\n'+body+'\n\t\tformatString: '+fmt+'\n\t\tdisplayFolder: Budget\\Resultaträkning\n\n\tcolumn ',1)
p.write_text(s,encoding='utf-8')
print('Added percentage / percentage-point variance, correct cost signs, zero-budget dash and neutral rounded zero.')
