from pathlib import Path
import csv,json,sys
root=Path(__file__).resolve().parents[1]/'powerbi-ledningsrapport'
totals={}
for filename,index,field in [('Försäljning.csv',0,'Nettointäkt'),('Direkta kostnader.csv',1,'Belopp'),('Gemensamma kostnader.csv',2,'Belopp')]:
 with (root/'data'/filename).open(encoding='utf-8-sig') as f:
  for r in csv.DictReader(f):
   ym=int(r['Datumnyckel'])//100;totals.setdefault(ym,[0,0,0])[index]+=int(r[field])
def aggregate(year,months):
 v=[sum(totals.get(year*100+m,[0,0,0])[i] for m in months) for i in range(3)]
 return dict(Revenue=v[0],EBIT=v[0]-v[1]-v[2],Margin=(v[0]-v[1])/v[0])
cases=[];queries=[]
for year in (2024,2025,2026):
 for selected in ([1,2,3,4,5,6,7,8,9,10,11,12],[1,3,9]):
  for accumulated in (1,2):
   for column in (3,13):
    months=[m for m in selected if (year!=2026 or m<=9) and (column==13 or (m<=column if accumulated==2 else m==column))]
    case=dict(id=len(cases),year=year,months=months,current=aggregate(year,months),prior=aggregate(year-1,months));cases.append(case)
    filters=f"TREATAS({{{year}}},'Budgetår'[År]),TREATAS({{{','.join(map(str,selected))}}},'Budgetmånader'[Nummer]),TREATAS({{4}},'Budgetscenarion'[ScenarioID]),TREATAS({{1}},'Budgetjämförelse'[Ordning]),TREATAS({{{accumulated}}},'Budgetvisning'[Ordning]),TREATAS({{{column}}},'Budgetkolumner'[MånadID])"
    values=[f'"ID",{case["id"]}']
    for prefix,measure in [('Current','RR rad utfall'),('Prior','Check prior row')]:
     for name,row in [('Revenue','Nettoomsättning'),('EBIT','Rörelseresultat'),('Margin','Bruttomarginal')]:values.append(f'"{prefix}{name}",CALCULATE([{measure}],\'Budgetrader\'[Rad]="{row}")')
    queries.append('CALCULATETABLE(ROW('+','.join(values)+'),'+filters+')')
(root/'validation/prior-year-expected.json').write_text(json.dumps(cases,indent=2)+'\n',encoding='utf-8')
import re
model=(root/'Ledningsrapport.SemanticModel/definition/tables/Budgetscenarier.tmdl').read_text(encoding='utf-8-sig')
definitions=['MEASURE \'Budgetscenarier\'[Budget scenario A] = 4','MEASURE \'Budgetscenarier\'[Budget jämförelseläge] = 1']
aliases={'RR föregående år en post':'Check prior post','RR föregående år konton':'Check prior accounts','RR rad A':'Check prior row'}
for name,alias in aliases.items():
 body=re.search(r"\tmeasure '"+re.escape(name)+r"' =(.*?)(?=\n\t\tformatString)",model,re.S)[1]
 for old,new in aliases.items():body=body.replace('['+old+']','['+new+']')
 body=body.replace('[RR budget A konton]','[Check prior accounts]')
 definitions.append("MEASURE 'Budgetscenarier'["+alias+'] ='+body)
(root/'validation/prior-year-check.dax').write_text('DEFINE\n'+'\n'.join(definitions)+'\nEVALUATE\nUNION(\n'+',\n'.join(queries)+'\n)\nORDER BY [ID]\n',encoding='utf-8')
if '--verify' in sys.argv:
 live=json.loads((root/'validation/prior-year-live.json').read_text(encoding='utf-8-sig'))['resultSets'][0]
 assert len(live)==len(cases)
 for row in live:
  case=cases[row['[ID]']]
  for prefix,key in [('Current','current'),('Prior','prior')]:
   for name,value in case[key].items():assert abs(row['['+prefix+name+']']-value)<.00001,(case,row,name,value)
 (root/'validation/prior-year-verification.json').write_text(json.dumps(dict(status='passed',cases=len(cases),checks=len(cases)*6,source='Source measure expressions under separate query-scoped test names against live imported facts; selector loading and Desktop screenshot still require reopening'),indent=2)+'\n',encoding='utf-8')
 print(f'PASS: {len(cases)} cases, {len(cases)*6} actual/prior amounts and margins; monthly, accumulated, sparse selections and 2024/2025/2026.')
else:print(f'Prepared {len(cases)} independently calculated cases.')
