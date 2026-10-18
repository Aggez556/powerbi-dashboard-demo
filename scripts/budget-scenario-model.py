"""Add Excel-backed budgets and disconnected RR presentation utilities to TMDL."""
from pathlib import Path
import csv,json,re,os
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'powerbi-ledningsrapport';MODEL=BASE/os.environ.get('PBI_BUDGET_MODEL','Ledningsrapport.SemanticModel')/'definition';DATA=BASE/'data'
q=lambda s:"'"+s.replace("'","''")+"'"
def table(name,cols,source=None):
 s=f'/// Budget: {name}. Utility selectors are intentionally disconnected.\ntable {q(name)}\n'
 for col,typ,sort in cols:
  s+=f'\n\tcolumn {q(col)}\n\t\tdataType: {typ}\n\t\tsourceColumn: {col}\n\t\tsummarizeBy: none\n'
  if col.endswith('ID') or col in ['Belopp','Månadsnyckel','Ordning','Position','Radordning','Gruppordning','Underordning','Postordning']:s+='\t\tisHidden\n'
  if sort:s+=f'\t\tsortByColumn: {q(sort)}\n'
 if source is None:
  types=', '.join('{'+f'"{c}", '+('Int64.Type' if t=='int64' else 'Currency.Type' if t=='decimal' else 'type text')+'}' for c,t,_ in cols)
  source=f'let\n Source=Csv.Document(File.Contents(DataFolder & "/{name}.csv"),[Delimiter=",",Encoding=65001,QuoteStyle=QuoteStyle.Csv]),\n Headers=Table.PromoteHeaders(Source,[PromoteAllScalars=true]),\n Typed=Table.TransformColumnTypes(Headers,{{{types}}},"en-US")\nin Typed'
 s+=f'\n\tpartition {q(name)} = m\n\t\tmode: import\n\t\tsource =\n'+''.join('\t\t\t'+line+'\n' for line in source.splitlines())
 file=MODEL/'tables'/f'{name}.tmdl'
 # Only regenerate our own additions before Desktop loads them.
 if file.exists() and 'lineageTag:' in file.read_text(encoding='utf-8-sig'):return
 file.write_text(s,encoding='utf-8')
cols={
 'Budgetkonton':[('KontoID','int64',None),('RRgrupp','string','Gruppordning'),('Undergrupp','string',None),('Post','string',None),('Gruppordning','int64',None),('Underordning','int64',None),('Postordning','int64',None)],
 'Budgetrader':[('KontoID','int64',None),('Rad','string','Radordning'),('Undergrupp','string','Underordning'),('Post','string','Postordning'),('Radordning','int64',None),('Underordning','int64',None),('Postordning','int64',None)],
 'Budgetscenarion':[('ScenarioID','int64',None),('Scenario','string','Ordning'),('Ordning','int64',None)],
 'Budgetjämförelsescenario':[('ScenarioID','int64',None),('Scenario','string','Ordning'),('Ordning','int64',None)],
 'Budgetår':[('År','int64',None)],
 'Budgetmånader':[('Nummer','int64',None),('Månad','string','Nummer'),('Kortnamn','string','Nummer')],
 'Budgetperioder':[('Månadsnyckel','int64',None),('År','int64',None),('Nummer','int64',None)],
 'Budgetjämförelse':[('Läge','string','Ordning'),('Ordning','int64',None)],
 'Budgetvisning':[('Visning','string','Ordning'),('Ordning','int64',None)],
 'Budgetkolumner':[('LägeID','int64',None),('ScenarioA','int64',None),('ScenarioB','int64',None),('MånadID','int64',None),('Grupp','string','MånadID'),('Position','int64',None),('Kolumn','string','Position')],
 'Budgetscenarier':[('Månadsnyckel','int64',None),('KontoID','int64',None),('ScenarioID','int64',None),('Belopp','decimal',None)]}
excel='''let
 Source=Excel.Workbook(File.Contents(BudgetWorkbook),null,true),
 Tables=Table.SelectRows(Source,each [Kind]="Table" and Text.StartsWith([Name],"Budget_")),
 Combined=Table.Combine(Tables[Data]),
 Unpivot=Table.UnpivotOtherColumns(Combined,{"År","ScenarioID","KontoID","Post"},"Månad","Belopp"),
 Months={"Januari","Februari","Mars","April","Maj","Juni","Juli","Augusti","September","Oktober","November","December"},
 Key=Table.AddColumn(Unpivot,"Månadsnyckel",each Number.From([År])*100+List.PositionOf(Months,[Månad])+1,Int64.Type),
 Selected=Table.SelectColumns(Key,{"Månadsnyckel","KontoID","ScenarioID","Belopp"}),
 Typed=Table.TransformColumnTypes(Selected,{{"Månadsnyckel",Int64.Type},{"KontoID",Int64.Type},{"ScenarioID",Int64.Type},{"Belopp",Currency.Type}},"sv-SE")
in Typed'''
for name,columns in cols.items():table(name,columns,excel if name=='Budgetscenarier' else None)
exprfile=MODEL/'expressions.tmdl';s=exprfile.read_text(encoding='utf-8-sig')
if 'expression BudgetWorkbook' not in s:s+='\nexpression BudgetWorkbook = DataFolder & "/Budgetscenarier.xlsx" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n\tannotation PBI_ResultType = Text\n'
exprfile.write_text(s,encoding='utf-8')
modelfile=MODEL/'model.tmdl';s=modelfile.read_text(encoding='utf-8-sig')
for name in cols:
 if f'ref table {q(name)}' not in s:s+=f'\nref table {q(name)}\n'
modelfile.write_text(s,encoding='utf-8')
relfile=MODEL/'relationships.tmdl';s=relfile.read_text(encoding='utf-8-sig')
for fk,dim,pk in [('KontoID','Budgetkonton','KontoID'),('ScenarioID','Budgetscenarion','ScenarioID'),('Månadsnyckel','Budgetperioder','Månadsnyckel')]:
 name='Excelbudget till '+dim
 if q(name) not in s:s+=f'\nrelationship {q(name)}\n\tfromColumn: Budgetscenarier.{q(fk)}\n\ttoColumn: {q(dim)}.{q(pk)}\n'
relfile.write_text(s,encoding='utf-8')
# The existing Budget table becomes an aggregation of the very same Excel baseline.
# Keep its schema, lineage and historical 46-month coverage; no second competing budget.
p=MODEL/'tables/Budget.tmdl';s=p.read_text(encoding='utf-8-sig');pos=s.index('\n\tpartition ')
s=s[:pos]+'''\n\tpartition Budget = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t Source=Table.SelectRows(Budgetscenarier,each [ScenarioID]=1 and [Månadsnyckel]<=202610),
\t\t\t Grouped=Table.Group(Source,{"Månadsnyckel"},{{"Rörelseresultat",each List.Sum([Belopp]),Currency.Type}}),
\t\t\t Key=Table.AddColumn(Grouped,"Datumnyckel",each [Månadsnyckel]*100+15,Int64.Type),
\t\t\t Selected=Table.SelectColumns(Key,{"Datumnyckel","Rörelseresultat"})
\t\t\tin Selected
'''
p.write_text(s,encoding='utf-8')

measures={}
def add(name,expression,fmt='0',hidden=False,dynamic=None):measures[name]=(expression,fmt,hidden,dynamic)
add('Budget valt år',"SELECTEDVALUE('Budgetår'[År],2026)")
add('Budget jämförelseläge',"IF([Budget valt år]<2026,1,SELECTEDVALUE('Budgetjämförelse'[Ordning],1))")
add('Budget scenario A',"IF([Budget valt år]<2026,1,SELECTEDVALUE('Budgetscenarion'[ScenarioID],1))")
add('Budget scenario B',"VAR _a=[Budget scenario A] VAR _b=SELECTEDVALUE('Budgetjämförelsescenario'[ScenarioID],2) RETURN IF(_a=_b,IF(_a=1,2,1),_b)")
add('Budget scenario tillgängligt',"VAR _s=SELECTEDVALUE('Budgetscenarion'[ScenarioID]) RETURN IF([Budget valt år]=2026 || _s=1,1,0)")
add('Budget jämförelse tillgänglig',"IF(SELECTEDVALUE('Budgetjämförelse'[Ordning])=1 || [Budget valt år]=2026,1,0)")
add('Budget B tillgängligt',"IF([Budget jämförelseläge]=2 && SELECTEDVALUE('Budgetjämförelsescenario'[ScenarioID])<>[Budget scenario A],1,0)")
add('Budget månad tillgänglig',"IF([Budget jämförelseläge]=2 || [Budget valt år]<2026 || SELECTEDVALUE('Budgetmånader'[Nummer])<=9,1,0)")
add('Budget A namn',"VAR _s=[Budget scenario A] RETURN MAXX(FILTER(ALL('Budgetscenarion'),'Budgetscenarion'[ScenarioID]=_s),'Budgetscenarion'[Scenario])",'@')
add('Budget B namn',"VAR _s=[Budget scenario B] RETURN MAXX(FILTER(ALL('Budgetjämförelsescenario'),'Budgetjämförelsescenario'[ScenarioID]=_s),'Budgetjämförelsescenario'[Scenario])",'@')
keyvars="""VAR _year=[Budget valt år]
VAR _limit=IF([Budget jämförelseläge]=1 && _year=2026,9,12)
VAR _column=SELECTEDVALUE('Budgetkolumner'[MånadID],13)
VAR _acc=SELECTEDVALUE('Budgetvisning'[Ordning],1)=2
VAR _months=FILTER(VALUES('Budgetmånader'[Nummer]),'Budgetmånader'[Nummer]<=_limit && (_column=13 || IF(_acc,'Budgetmånader'[Nummer]<=_column,'Budgetmånader'[Nummer]=_column)))
VAR _keys=SELECTCOLUMNS(_months,"MonthKey",_year*100+'Budgetmånader'[Nummer])"""
baseActual="""VAR _k=SELECTEDVALUE('Budgetkonton'[KontoID])
RETURN SUMX(_keys,VAR _date=[MonthKey]*100+1
VAR _last=[MonthKey]*100+DAY(EOMONTH(DATE(_year,MOD([MonthKey],100),1),0))
VAR _admin=CALCULATE(SUM('Gemensamma kostnader'[Belopp]),REMOVEFILTERS('Datum'),REMOVEFILTERS('Gemensamma kostnader'[Kostnadstyp]),'Gemensamma kostnader'[Datumnyckel]>=_date,'Gemensamma kostnader'[Datumnyckel]<=_last,'Gemensamma kostnader'[Kostnadstyp]="Administration")
RETURN SWITCH(_k,
1001,CALCULATE(SUM('Försäljning'[Nettointäkt]),'Försäljning'[Datumnyckel]>=_date,'Försäljning'[Datumnyckel]<=_last,'Försäljning'[Områdesnyckel]=1),
1002,CALCULATE(SUM('Försäljning'[Nettointäkt]),'Försäljning'[Datumnyckel]>=_date,'Försäljning'[Datumnyckel]<=_last,'Försäljning'[Områdesnyckel]=2),
1003,CALCULATE(SUM('Försäljning'[Nettointäkt]),'Försäljning'[Datumnyckel]>=_date,'Försäljning'[Datumnyckel]<=_last,'Försäljning'[Områdesnyckel]=3),
2001,-CALCULATE(SUM('Direkta kostnader'[Belopp]),'Direkta kostnader'[Datumnyckel]>=_date,'Direkta kostnader'[Datumnyckel]<=_last,'Direkta kostnader'[Kostnadstyp]="Varukostnad"),
2002,-CALCULATE(SUM('Direkta kostnader'[Belopp]),'Direkta kostnader'[Datumnyckel]>=_date,'Direkta kostnader'[Datumnyckel]<=_last,'Direkta kostnader'[Kostnadstyp]="Direkt leveranspersonal"),
2003,-CALCULATE(SUM('Direkta kostnader'[Belopp]),'Direkta kostnader'[Datumnyckel]>=_date,'Direkta kostnader'[Datumnyckel]<=_last,'Direkta kostnader'[Kostnadstyp]="Underleverantörer"),
2004,-CALCULATE(SUM('Direkta kostnader'[Belopp]),'Direkta kostnader'[Datumnyckel]>=_date,'Direkta kostnader'[Datumnyckel]<=_last,'Direkta kostnader'[Kostnadstyp]="Övrigt direkt"),
2005,-CALCULATE(SUM('Direkta kostnader'[Belopp]),'Direkta kostnader'[Datumnyckel]>=_date,'Direkta kostnader'[Datumnyckel]<=_last,'Direkta kostnader'[Kostnadstyp]="Ej uppdragsfördelad personal"),
3001,-ROUND(_admin*.6,0),
4001,-CALCULATE(SUM('Gemensamma kostnader'[Belopp]),'Gemensamma kostnader'[Datumnyckel]>=_date,'Gemensamma kostnader'[Datumnyckel]<=_last,'Gemensamma kostnader'[Kostnadstyp]="Lokaler och drift"),
4002,-ROUND(_admin*.10,0),4003,-ROUND(_admin*.06,0),4004,-ROUND(_admin*.04,0),4005,-ROUND(_admin*.08,0),
4006,-(_admin-ROUND(_admin*.6,0)-ROUND(_admin*.10,0)-ROUND(_admin*.06,0)-ROUND(_admin*.04,0)-ROUND(_admin*.08,0)),
5001,-CALCULATE(SUM('Gemensamma kostnader'[Belopp]),'Gemensamma kostnader'[Datumnyckel]>=_date,'Gemensamma kostnader'[Datumnyckel]<=_last,'Gemensamma kostnader'[Kostnadstyp]="Avskrivningar")))"""
# Context transition inside the account iterator is explicit; existing report selectors cannot change company totals here.
add('RR utfall en post',keyvars+'\n'+baseActual,'#,##0',True)
add('RR utfall konton',"CALCULATE(SUMX(VALUES('Budgetkonton'[KontoID]),[RR utfall en post]),REMOVEFILTERS('Datum'),REMOVEFILTERS('Områden'),REMOVEFILTERS('Kunder'),REMOVEFILTERS('Artiklar'))",'#,##0',True)
for which in ['A','B']:
 add(f'RR budget {which} konton',keyvars+f"\nVAR _scenario=[Budget scenario {which}] RETURN CALCULATE(SUM('Budgetscenarier'[Belopp]),REMOVEFILTERS('Budgetscenarion'),REMOVEFILTERS('Budgetperioder'),TREATAS(_keys,'Budgetscenarier'[Månadsnyckel]),TREATAS({{_scenario}},'Budgetscenarier'[ScenarioID]))",'#,##0',True)
for tag,base in [('utfall','RR utfall konton'),('A','RR budget A konton'),('B','RR budget B konton')]:
 add('RR rad '+tag,f"""VAR _row=SELECTEDVALUE('Budgetrader'[KontoID],0)
VAR _ids=VALUES('Budgetrader'[KontoID])
VAR _blank=(ISINSCOPE('Budgetrader'[Undergrupp]) && ISBLANK(SELECTEDVALUE('Budgetrader'[Undergrupp]))) || (ISINSCOPE('Budgetrader'[Post]) && ISBLANK(SELECTEDVALUE('Budgetrader'[Post])))
VAR _sales=CALCULATE([{base}],REMOVEFILTERS('Budgetkonton'),'Budgetkonton'[RRgrupp]="Nettoomsättning")
VAR _direct=CALCULATE([{base}],REMOVEFILTERS('Budgetkonton'),'Budgetkonton'[RRgrupp]="Direkta kostnader")
VAR _all=CALCULATE([{base}],REMOVEFILTERS('Budgetkonton'))
RETURN IF(_blank,BLANK(),SWITCH(_row,-1,_sales+_direct,-2,DIVIDE(_sales+_direct,_sales),-3,_all,-4,DIVIDE(_all,_sales),CALCULATE([{base}],TREATAS(_ids,'Budgetkonton'[KontoID]))))""",'#,##0',True)
add('Budget kolumn synlig',"""VAR _m=SELECTEDVALUE('Budgetkolumner'[MånadID]) VAR _mode=[Budget jämförelseläge] VAR _a=[Budget scenario A] VAR _b=[Budget scenario B]
VAR _match=COUNTROWS(FILTER('Budgetkolumner','Budgetkolumner'[LägeID]=_mode && 'Budgetkolumner'[ScenarioA]=_a && 'Budgetkolumner'[ScenarioB]=IF(_mode=1,0,_b)))>0
RETURN IF(_match && (_m=13 || CONTAINS(VALUES('Budgetmånader'[Nummer]),'Budgetmånader'[Nummer],_m)) && (_m=13 || _mode=2 || [Budget valt år]<2026 || _m<=9),1,0)""")
add('Budget matrisvärde',"""VAR _slot=SELECTEDVALUE('Budgetkolumner'[Position]) VAR _mode=[Budget jämförelseläge]
VAR _a=[RR rad A] VAR _b=IF(_mode=1,[RR rad utfall],[RR rad B])
VAR _margin=SELECTEDVALUE('Budgetrader'[KontoID]) IN {-2,-4}
VAR _diff=IF(_mode=1,_b-_a,_a-_b)
VAR _value=SWITCH(_slot,1,_a,2,_b,3,IF(_margin,_diff*100,_diff))
RETURN IF(ISINSCOPE('Budgetrader'[Rad]) && [Budget kolumn synlig]=1 && NOT ISBLANK(_a) && NOT ISBLANK(_b),IF(_margin,_value,DIVIDE(_value,1000)))""",'#,##0',dynamic="IF(SELECTEDVALUE('Budgetrader'[KontoID]) IN {-2,-4},IF(SELECTEDVALUE('Budgetkolumner'[Position])=3,\"+0.0 \\\"pp\\\";−0.0 \\\"pp\\\";0.0 \\\"pp\\\"\",\"0.0 %\"),IF(SELECTEDVALUE('Budgetkolumner'[Position])=3,\"+#,##0;−#,##0;0\",\"#,##0;−#,##0;0\"))".replace('\\"','""'))
add('Budget matrisfärg',"IF(SELECTEDVALUE('Budgetkolumner'[Position])=3,IF([Budget matrisvärde]<0,\"#B42318\",IF([Budget matrisvärde]>0,\"#007956\",\"#5B6B80\")),\"#0F3163\")",'@')
add('Budget radbakgrund',"IF(NOT ISINSCOPE('Budgetrader'[Undergrupp]),SWITCH(SELECTEDVALUE('Budgetrader'[Rad]),\"Bruttovinst\",\"#E8EEF6\",\"Rörelseresultat\",\"#E8EEF6\",\"Bruttomarginal\",\"#F5F7FB\",\"Rörelsemarginal\",\"#F5F7FB\",\"#FFFFFF\"),\"#FFFFFF\")",'@')
for label,rr in [('omsättning','Nettoomsättning'),('resultat','Rörelseresultat'),('marginal','Bruttomarginal')]:
 for side in ['huvud','bas']:
  tag='A' if side=='huvud' else 'B'
  expr="IF([Budget jämförelseläge]=1,[RR rad utfall],[RR rad A])" if side=='huvud' else "IF([Budget jämförelseläge]=1,[RR rad A],[RR rad B])"
  add(f'Budget {label} {side}',f"CALCULATE({expr},REMOVEFILTERS('Budgetkolumner'),REMOVEFILTERS('Budgetrader'),'Budgetrader'[Rad]={q(rr)})",'0.0 %' if label=='marginal' else '#,##0',True)
 add(f'Budget {label} värde',f'VAR _v=[Budget {label} huvud] RETURN IF(ISBLANK(_v),"—",FORMAT('+('_v,"0.0 %"' if label=='marginal' else '_v/1000000,\'0.00 "Mkr"\'')+',"sv-SE"))','@')
 add(f'Budget {label} jämförelse',f'VAR _v=[Budget {label} bas] RETURN IF([Budget jämförelseläge]=1,"Budget: ",[Budget B namn] & ": ") & IF(ISBLANK(_v),"—",FORMAT('+('_v,"0.0 %"' if label=='marginal' else '_v/1000000,\'0.00 "Mkr"\'')+',"sv-SE"))','@')
 diff=f'[Budget {label} huvud]-[Budget {label} bas]'
 add(f'Budget {label} avvikelse',f'VAR _h=[Budget {label} huvud] VAR _b=[Budget {label} bas] VAR _d=_h-_b RETURN IF(ISBLANK(_h)||ISBLANK(_b),"—",'+('FORMAT(_d*100,"+0.0;−0.0;0.0","sv-SE") & " procentenheter"' if label=='marginal' else 'FORMAT(_d/1000000,\'+0.00 "Mkr";−0.00 "Mkr";0.00 "Mkr"\',"sv-SE") & " · " & IF(_b>0,FORMAT(DIVIDE(_d,_b),"+0.0 %;−0.0 %;0.0 %","sv-SE"),"—")')+')','@')
 add(f'Budget {label} färg',f'IF({diff}<0,"#B42318",IF({diff}>0,"#007956","#5B6B80"))','@')
add('Budget periodetikett',"""VAR _year=[Budget valt år] VAR _max=IF([Budget jämförelseläge]=1 && _year=2026,9,12)
VAR _months=FILTER(VALUES('Budgetmånader'[Nummer]),'Budgetmånader'[Nummer]<=_max)
VAR _first=MINX(_months,'Budgetmånader'[Nummer]) VAR _last=MAXX(_months,'Budgetmånader'[Nummer]) VAR _count=COUNTROWS(_months)
VAR _text=IF(_count=0,"Ingen avslutad månad vald",IF(_count=_last-_first+1,FORMAT(DATE(_year,_first,1),"MMMM","sv-SE") & IF(_last<>_first,"–" & FORMAT(DATE(_year,_last,1),"MMMM","sv-SE"),""),CONCATENATEX(_months,FORMAT(DATE(_year,'Budgetmånader'[Nummer],1),"MMM","sv-SE"),", ",'Budgetmånader'[Nummer],ASC)))
RETURN _text & " " & _year""",'@')
add('Budget matrisrubrik',"IF([Budget jämförelseläge]=1,[Budget A namn] & \" mot utfall\",\"A: \" & [Budget A namn] & \" · B: \" & [Budget B namn]) & \" · \" & [Budget periodetikett]",'@')
add('Budget visningsetikett',"IF(SELECTEDVALUE('Budgetvisning'[Ordning],1)=2,\"Ackumulerat inom vald period · Belopp i tkr\",\"Belopp i tkr · Marginaler i %\")",'@')
add('Budget KPI prefix',"IF([Budget jämförelseläge]=2,\"Scenario A · \" & [Budget A namn],\"Utfall · \" & [Budget periodetikett])",'@')
add('Budget utfallsnot',"IF([Budget jämförelseläge]=1,\"Utfall t.o.m. september 2026\",\"Budgetscenarier från Excel · ingen utfallsjämförelse\")",'@')
# Render measures belong to the new fact table, leaving all 191 established measures intact.
p=MODEL/'tables/Budgetscenarier.tmdl';s=p.read_text(encoding='utf-8-sig');a=s.index('\n\tcolumn ')
head=s[:a];tail=s[a:]
for name,(expr,fmt,hidden,dyn) in measures.items():
 # DAX strings use double quotes; q() above is only for TMDL object identifiers.
 for label in ['Nettoomsättning','Rörelseresultat','Bruttomarginal']:
  expr=expr.replace("='"+label+"'",'="'+label+'"')
 expr=re.sub(r"'([^']*\"Mkr\"[^']*)'",lambda m:'"'+m[1].replace('"','""')+'"',expr)
 head+=f'\n\t/// Budget calculation: {name}.\n\tmeasure {q(name)} = ```\n'+''.join('\t\t\t'+line+'\n' for line in expr.splitlines())+'\t\t\t```\n'
 if not dyn:head+=f'\t\tformatString: {fmt}\n'
 head+='\t\tdisplayFolder: Budget\n'
 if hidden:head+='\t\tisHidden\n'
 if dyn:head+='\t\tformatStringDefinition = '+dyn+'\n'
p.write_text(head+tail,encoding='utf-8')
(BASE/'validation/budget-model-manifest.json').write_text(json.dumps({'tables':list(cols),'measures':list(measures),'relationshipsAdded':3,'source':'Excel.Workbook(BudgetWorkbook)','actuals':'existing shared facts, virtual month alignment; no duplicate actual fact'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Added {len(cols)} budget tables and {len(measures)} measures; existing actual measures unchanged.')
