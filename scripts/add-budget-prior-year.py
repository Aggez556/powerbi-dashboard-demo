"""Add prior-year actuals as scenario 4, reusing the existing actual-versus-reference layout."""
from pathlib import Path
import csv,re,json
root=Path(__file__).resolve().parents[1]/'powerbi-ledningsrapport'
def readcsv(name):
 with (root/'data'/name).open(encoding='utf-8-sig',newline='') as f:
  reader=csv.DictReader(f);return reader.fieldnames,list(reader)
def writecsv(name,fields,rows):
 with (root/'data'/name).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
fields,rows=readcsv('Budgetscenarion.csv')
if not any(r['ScenarioID']=='4' for r in rows):rows.append(dict(ScenarioID=4,Scenario='Föregående års utfall',Ordning=4))
writecsv('Budgetscenarion.csv',fields,rows)
fields,rows=readcsv('Budgetkolumner.csv')
if not any(r['ScenarioA']=='4' for r in rows):
 for r in list(rows):
  if r['LägeID']=='1' and r['ScenarioA']=='1':
   v=dict(r);v['ScenarioA']='4'
   if v['Position']=='1':v['Kolumn']='Föregående år'
   rows.append(v)
writecsv('Budgetkolumner.csv',fields,rows)
# Preserve the existing M partition type: PBIP cannot change it against its cache.
for table in ['Budgetscenarion','Budgetkolumner']:
 fields,items=readcsv(table+'.csv')
 strings={'Scenario','Grupp','Kolumn'}
 types=','.join('{'+json.dumps(c,ensure_ascii=False)+', '+('type text' if c in strings else 'Int64.Type')+'}' for c in fields)
 source=f'let\n Source=Csv.Document(File.Contents(DataFolder & "/{table}.csv"),[Delimiter=",",Encoding=65001,QuoteStyle=QuoteStyle.Csv]),\n Headers=Table.PromoteHeaders(Source,[PromoteAllScalars=true]),\n Typed=Table.TransformColumnTypes(Headers,{{{types}}},"en-US")\nin Typed'
 p=root/'Ledningsrapport.SemanticModel/definition/tables'/(table+'.tmdl')
 content=p.read_text(encoding='utf-8-sig')
 content=re.sub(r'sourceColumn: \[([^\n]+)\]',lambda m:'sourceColumn: '+m[1],content)
 content=content[:content.index('\n\tpartition ')]+f'\n\tpartition {table} = m\n\t\tmode: import\n\t\tsource =\n'+''.join('\t\t\t'+line+'\n' for line in source.splitlines())
 p.write_text(content,encoding='utf-8')
file=root/'Ledningsrapport.SemanticModel/definition/tables/Budgetscenarier.tmdl'
text=file.read_text(encoding='utf-8-sig')
if "measure 'RR föregående år en post'" not in text:
 actual=re.search(r"\tmeasure 'RR utfall en post' =(.*?)(?=\n\t\tformatString)",text,re.S)[1]
 actual=actual.replace('VAR _year=[Budget valt år]','VAR _year=[Budget valt år]-1').replace('&& _year=2026','&& [Budget valt år]=2026')
 addition="\n\tmeasure 'RR föregående år en post' ="+actual+'\n\t\tformatString: #,##0\n\t\tisHidden\n\t\tdisplayFolder: Budget\n'
 addition+="\n\tmeasure 'RR föregående år konton' = CALCULATE(SUMX(VALUES('Budgetkonton'[KontoID]),[RR föregående år en post]),REMOVEFILTERS('Datum'),REMOVEFILTERS('Områden'),REMOVEFILTERS('Kunder'),REMOVEFILTERS('Artiklar'))\n\t\tformatString: #,##0\n\t\tisHidden\n\t\tdisplayFolder: Budget\n"
 pos=text.index('\n\tcolumn ');text=text[:pos]+addition+text[pos:]
def measure(name,dax):
 global text
 pattern=r"(\tmeasure '"+re.escape(name)+r"' =).*?(?=\n\t\t(?:formatString|displayFolder|isHidden))"
 text,count=re.subn(pattern,lambda m:m.group(1)+' '+dax,text,count=1,flags=re.S)
 assert count==1,name
measure('Budget jämförelseläge',"IF(SELECTEDVALUE('Budgetscenarion'[ScenarioID])=4 || [Budget valt år]<2026,1,SELECTEDVALUE('Budgetjämförelse'[Ordning],1))")
measure('Budget scenario A',"VAR _s=SELECTEDVALUE('Budgetscenarion'[ScenarioID],1) RETURN IF(_s=4,4,IF([Budget valt år]<2026,1,_s))")
measure('Budget scenario tillgängligt',"VAR _s=SELECTEDVALUE('Budgetscenarion'[ScenarioID]) RETURN IF(_s=4 || [Budget valt år]=2026 || _s=1,1,0)")
measure('Budget jämförelse tillgänglig',"IF(SELECTEDVALUE('Budgetjämförelse'[Ordning])=1 || ([Budget valt år]=2026 && [Budget scenario A]<>4),1,0)")
measure('Budget matrisrubrik','IF([Budget scenario A]=4,"Utfall mot föregående år",IF([Budget jämförelseläge]=1,[Budget A namn] & " mot utfall","A: " & [Budget A namn] & " · B: " & [Budget B namn])) & " · " & [Budget periodetikett]')
measure('Budget utfallsnot','IF([Budget jämförelseläge]=1,"Utfall · " & [Budget periodetikett],"Budgetscenarier från Excel · ingen utfallsjämförelse")')
pattern=r"(\tmeasure 'RR budget A konton' =)(.*?)(?=\n\t\tformatString)"
m=re.search(pattern,text,re.S);body=m[2]
if 'VAR _prior=' not in body:
 body=body.replace('VAR _scenario=[Budget scenario A] RETURN ',"VAR _scenario=[Budget scenario A]\n\t\t\tVAR _prior=CALCULATE([RR utfall konton],REMOVEFILTERS('Budgetår'),TREATAS({_year-1},'Budgetår'[År]),REMOVEFILTERS('Budgetmånader'),TREATAS(_months,'Budgetmånader'[Nummer]))\n\t\t\tRETURN IF(_scenario=4,_prior,")+')'
 text=text[:m.start(2)]+body+text[m.end(2):]
text=re.sub(r"VAR _prior=CALCULATE\(\[RR utfall konton\].*?\n",'VAR _prior=[RR föregående år konton]\n',text)
text=text.replace('IF([Budget jämförelseläge]=1,"Budget: ",[Budget B namn] & ": ")','IF([Budget scenario A]=4,"Föregående år: ",IF([Budget jämförelseläge]=1,"Budget: ",[Budget B namn] & ": "))')
file.write_text(text,encoding='utf-8')
# Fit a fourth choice in the existing selector without moving the period controls.
folder=root/'LedningsrapportUtanScroll.Report/definition/pages/cbe967640ff6843fb323/visuals'
for name in ['ba6fadd0299c9b660668','02ab4eacb4cbda1f85b7','b82c0ffb21913724e395']:
 f=folder/name/'visual.json';v=json.loads(f.read_text(encoding='utf-8-sig'))
 if name=='ba6fadd0299c9b660668':
  v['position']['height']=160
  v['visual']['objects']['layout'][0]['properties']['rowCount']['expr']['Literal']['Value']='4D'
 else:
  for p in v['visual']['objects']['general'][0]['properties']['paragraphs']:
   for r in p['textRuns']:r['value']='Jämförelseunderlag' if name=='b82c0ffb21913724e395' else ''
 f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Added prior-year actuals reference and retained existing budget scenarios.')
