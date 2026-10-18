"""Presentation nodes and DAX for one interactive financial statement visual.
No financial amounts are stored in the presentation table.
"""
from pathlib import Path
import csv,json,re,os
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'powerbi-ledningsrapport';DATA=BASE/'data';MODEL=BASE/'Ledningsrapport.SemanticModel/definition'
q=lambda s:"'"+s.replace("'","''")+"'"
rows=list(csv.DictReader((DATA/'Budgetrader.csv').open(encoding='utf-8-sig')))
nodes=[];tops={};children={}
for r in rows:
 order=int(r['Radordning']);key='r'+str(order)
 if key not in tops:
  calc=int(r['KontoID'])<0;kind='marginal' if calc and r['Rad'].endswith('marginal') else 'resultat' if calc else 'grupp'
  section={1:'Intäkter',2:'Kostnader',5:'Gemensamma kostnader'}.get(order,'')
  tops[key]=[key,r['Rad'],'','',r['Rad'],'','',0,kind,order*1000,0,section]
for r in rows:
 if int(r['KontoID'])<0:continue
 top='r'+r['Radordning'];sub=r['Undergrupp'];leaf=r['Post'];subkey=top+'_s'+r['Underordning']
 if subkey not in children:
  children[subkey]=[subkey,r['Rad'],sub,'',sub,top,'',1,'grupp' if leaf else 'konto',int(r['Radordning'])*1000+int(r['Underordning'])*10,0,'']
  tops[top][10]=1
 if leaf:
  children[subkey][10]=1
  key='a'+r['KontoID'];children[key]=[key,r['Rad'],sub,leaf,leaf,subkey,top,2,'konto',int(r['Radordning'])*1000+int(r['Underordning'])*10+int(r['Postordning']),0,'']
nodes=sorted(list(tops.values())+list(children.values()),key=lambda r:r[9])
columns=[('NodID','string'),('Rad','string'),('Undergrupp','string'),('Post','string'),('Etikett','string'),('Förälder','string'),('Överförälder','string'),('Nivå','int64'),('Typ','string'),('Ordning','int64'),('HarBarn','int64'),('Avsnitt','string')]
with (DATA/'Budgetrapportnoder.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow([c for c,_ in columns]);w.writerows(nodes)
base='''VAR _rad=SELECTEDVALUE('Budgetrapportnoder'[Rad])
VAR _sub=SELECTEDVALUE('Budgetrapportnoder'[Undergrupp])
VAR _post=SELECTEDVALUE('Budgetrapportnoder'[Post])
VAR _ids=SELECTCOLUMNS(FILTER(ALL('Budgetrader'),'Budgetrader'[Rad]=_rad && (_sub="" || 'Budgetrader'[Undergrupp]=_sub) && (_post="" || 'Budgetrader'[Post]=_post)),"KontoID",'Budgetrader'[KontoID])
VAR _mode=[Budget jämförelseläge]
VAR _slot=SELECTEDVALUE('Budgetkolumner'[Position])
VAR _a=CALCULATE([RR rad A],REMOVEFILTERS('Budgetrader'),TREATAS(_ids,'Budgetrader'[KontoID]))
VAR _b=IF(_mode=1,CALCULATE([RR rad utfall],REMOVEFILTERS('Budgetrader'),TREATAS(_ids,'Budgetrader'[KontoID])),CALCULATE([RR rad B],REMOVEFILTERS('Budgetrader'),TREATAS(_ids,'Budgetrader'[KontoID])))
VAR _margin=SELECTEDVALUE('Budgetrapportnoder'[Typ])="marginal"
VAR _diff=IF(_mode=1,_b-_a,_a-_b)
VAR _value=SWITCH(_slot,1,_a,2,_b,3,IF(_margin,_diff*100,_diff))
RETURN IF(HASONEVALUE('Budgetrapportnoder'[NodID]) && [Budget kolumn synlig]=1 && NOT ISBLANK(_a) && NOT ISBLANK(_b),IF(_margin,_value,DIVIDE(_value,1000)))'''
measures={
 'Rapportvärde':(base,'#,##0'),
 'Rapporttext':('''VAR _v=[Rapportvärde] VAR _slot=SELECTEDVALUE('Budgetkolumner'[Position]) VAR _margin=SELECTEDVALUE('Budgetrapportnoder'[Typ])="marginal"
RETURN IF(ISBLANK(_v),BLANK(),IF(_margin,IF(_slot=3,FORMAT(_v,"+0.0;−0.0;0.0","sv-SE") & " pp",FORMAT(_v,"0.0 %","sv-SE")),FORMAT(_v,IF(_slot=3,"+#,##0;−#,##0;0","#,##0;−#,##0;0"),"sv-SE")))''','@'),
 'Rapportfärg':('''VAR _v=[Rapportvärde] RETURN IF(ISBLANK(_v),BLANK(),IF(SELECTEDVALUE('Budgetkolumner'[Position])=3,IF(_v<0,"#B42318",IF(_v>0,"#007956","#5B6B80")),IF(SELECTEDVALUE('Budgetrapportnoder'[Typ])="marginal","#5B6B80","#0F3163")))''','@')}
p=MODEL/'tables/Budgetrapportnoder.tmdl'
s="/// Disconnected financial statement presentation tree. Amounts are calculated from shared actuals and Excel budgets.\ntable Budgetrapportnoder\n"
for name,(expr,fmt) in measures.items():
 s+=f'\n\tmeasure {q(name)} = ```\n'+''.join('\t\t\t'+line+'\n' for line in expr.splitlines())+f'\t\t\t```\n\t\tformatString: {fmt}\n\t\tdisplayFolder: Budget\\Resultaträkning\n'
for name,typ in columns:
 s+=f'\n\tcolumn {q(name)}\n\t\tdataType: {typ}\n\t\tsourceColumn: {name}\n\t\tsummarizeBy: none\n'
 if name=='NodID':s+='\t\tsortByColumn: Ordning\n'
types=', '.join('{"'+c+'", '+('Int64.Type' if t=='int64' else 'type text')+'}' for c,t in columns)
s+='\n\tpartition Budgetrapportnoder = m\n\t\tmode: import\n\t\tsource =\n\t\t\tlet\n\t\t\t Source=Csv.Document(File.Contents(DataFolder & "/Budgetrapportnoder.csv"),[Delimiter=",",Encoding=65001,QuoteStyle=QuoteStyle.Csv]),\n\t\t\t Headers=Table.PromoteHeaders(Source,[PromoteAllScalars=true]),\n\t\t\t Typed=Table.TransformColumnTypes(Headers,{'+types+'},"sv-SE")\n\t\t\tin Typed\n'
if p.exists() and 'lineageTag:' in p.read_text(encoding='utf-8-sig'):raise RuntimeError('Presentation model already loaded; preserve its lineage and use targeted measure updates.')
p.write_text(s,encoding='utf-8')
p=MODEL/'model.tmdl';s=p.read_text(encoding='utf-8-sig')
if 'ref table Budgetrapportnoder' not in s:s+='\nref table Budgetrapportnoder\n'
p.write_text(s,encoding='utf-8')
(BASE/'validation/budget-statement-model.json').write_text(json.dumps({'nodes':len(nodes),'rootRows':len(tops),'expandableNodes':[n[0] for n in nodes if n[10]],'calculatedNodes':[n[0] for n in nodes if n[8] in ['resultat','marginal']],'financialAmountsInNodeTable':False,'measures':list(measures)},indent=2)+'\n',encoding='utf-8')
print('Created',len(nodes),'presentation nodes and 3 measures; existing amounts and measures unchanged.')
import runpy
runpy.run_path(str(Path(__file__).with_name('budget-variance.py')))
