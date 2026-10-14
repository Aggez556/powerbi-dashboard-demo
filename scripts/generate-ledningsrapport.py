"""Reproducible Ledningsrapport demo; integer SEK, never rounded target allocations."""
from pathlib import Path
from datetime import date, timedelta
import calendar, csv, hashlib, json, math, sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'powerbi-ledningsrapport'
DATA = BASE / 'data'
MODEL = BASE / 'Ledningsrapport.SemanticModel'
MONTHS = ['januari','februari','mars','april','maj','juni','juli','augusti','september','oktober','november','december']

def save(path, text):
    if '--data-only' in sys.argv and path.is_relative_to(MODEL):return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')

def dump(path, value):
    save(path, json.dumps(value, ensure_ascii=False, indent=2)+'\n')

def allocate(total, weights):
    raw = [total*w/sum(weights) for w in weights]
    out = [math.floor(v) for v in raw]
    for i in sorted(range(len(raw)), key=lambda i: raw[i]-out[i], reverse=True)[:total-sum(out)]:
        out[i] += 1
    assert sum(out) == total
    return out

def end(d):
    return date(d.year, d.month, calendar.monthrange(d.year,d.month)[1])

def shift(d, n):
    ym = d.year*12+d.month-1+n
    return date(ym//12,ym%12+1,1)

def key(d):
    return int(d.strftime('%Y%m%d'))

months = [shift(date(2023,1,1),i) for i in range(46)]
current = months[33:45]
previous = months[21:33]
weights = [1.80,1.62,1.80,1.92,2.06,2.34,2.46,2.61,2.82,2.84,3.08,3.26]
actual = {}
for m in months:
    season = [0.91,0.89,1.03,1.04,1.08,1.09,0.81,1.03,1.13,1.09,1.03,1.08][m.month-1]
    growth = 1+.065*(m.year-2023)
    rev = [round(5_000_000*season*growth),round(1_750_000*season*growth),round(1_350_000*season*growth)]
    gp = [round(rev[0]*.285),round(rev[1]*.30),round(rev[2]*.22)]
    actual[m] = {'revenue':rev, 'gp':gp, 'central':round(sum(gp)*.76), 'budget':round(sum(gp)*.27), 'jobs':[round(40*season*growth),round(22*season*growth)]}

for period,revenues,gross,central,jobs in [
    (previous,[73_000_000,25_000_000,22_000_000],[20_500_000,6_750_000,5_750_000],24_000_000,[560,280]),
    (current,[85_000_000,30_000_000,24_500_000],[23_800_000,9_300_000,2_940_000],28_040_000,[640,320])]:
    revenues_by_area = [allocate(v,weights) for v in revenues]
    gross_by_area = [allocate(v,[w*(1+.035*math.sin(i+a)) for i,w in enumerate(weights)]) for a,v in enumerate(gross)]
    if period == current:
        opweights = [w*p for w,p in zip(weights,[10,8.8,8.8,8.1,7.3,6.9,6,5.5,5.3,4.6,4,4])]
        op = allocate(8_000_000,opweights)
        centrals = [sum(gross_by_area[a][i] for a in range(3))-op[i] for i in range(12)]
        jobtotal = allocate(960,[50,60,65,70,75,85,90,95,100,80,95,105])
        technical = allocate(640,[35,41,45,50,53,57,61,65,70,53,63,67])
        assert sum(technical)==640
        jobseries = [technical,[a-b for a,b in zip(jobtotal,technical)]]
    else:
        centrals = allocate(central,weights)
        jobseries = [allocate(v,weights) for v in jobs]
    budgets = allocate(9_750_000 if period==current else 9_500_000,weights)
    for i,m in enumerate(period):
        actual[m]={'revenue':[revenues_by_area[a][i] for a in range(3)],'gp':[gross_by_area[a][i] for a in range(3)],'central':centrals[i],'budget':budgets[i],'jobs':[jobseries[a][i] for a in range(2)]}

# Extend the established history by one month without rewriting prior outcomes.
september=actual[date(2026,9,1)]
actual[date(2026,10,1)]= {
    'revenue':[round(v*1.035) for v in september['revenue']],
    'gp':[round(v*1.045) for v in september['gp']],
    'central':round(september['central']*1.02),
    'budget':round(september['budget']*1.035),
    'jobs':[round(v*1.04) for v in september['jobs']]}
rows = {}
days = [date(2023,1,1)+timedelta(days=i) for i in range((date(2026,10,31)-date(2023,1,1)).days+1)]
rows['Datum'] = [{'Datumnyckel':key(d),'Datum':d.isoformat(),'År':d.year,'Månadsnummer':d.month,'Månad':MONTHS[d.month-1].capitalize(),'Årmånad':d.strftime('%Y-%m'),'Kvartal':f'K{(d.month-1)//3+1}'} for d in days]
rows['Kunder'] = [{'Kundnyckel':i,'Kund':f'Hygienkund {i:03d} AB','Ort':['Stockholm','Göteborg','Malmö','Uppsala','Västerås'][i%5]} for i in range(1,302)]
rows['Områden'] = [{'Områdesnyckel':i+1,'Område':n} for i,n in enumerate(['Produktförsäljning','Teknisk service','Bemanning'])]
rows['Försäljning'],rows['Direkta kostnader'],rows['Gemensamma kostnader'],rows['Uppdrag'],rows['Budget'] = [],[],[],[],[]
for mi,m in enumerate(months):
    v = actual[m]
    pools = [list(range(1,231)),list(range(126,271)),list(range(191,271))] if m>=current[0] else [list(range(1,206)),list(range(101,231)),list(range(161,241))] if m in previous else [list(range(1,181)),list(range(81,211)),list(range(141,221))]
    for a,pool in enumerate(pools):
        # Rotating recurring buyers give variable monthly counts, exact R12 unions.
        buyers = [pool[(mi*19+j)%len(pool)] for j in range(min(len(pool),[100,70,45][a]))]
        d = m.replace(day=15)
        credit = 2500+(mi%5)*500
        amounts = allocate(v['revenue'][a]+credit,[1+(c%13)*.12 for c in buyers])
        for c,amount in zip(buyers,amounts):
            rows['Försäljning'].append({'Fakturarad':len(rows['Försäljning'])+1,'Datumnyckel':key(d),'Kundnyckel':c,'Områdesnyckel':a+1,'Nettointäkt':amount,'Typ':'Försäljning'})
        rows['Försäljning'].append({'Fakturarad':len(rows['Försäljning'])+1,'Datumnyckel':key(d),'Kundnyckel':301,'Områdesnyckel':a+1,'Nettointäkt':-credit,'Typ':'Kreditnota'})
        total = v['revenue'][a]-v['gp'][a]
        costtypes = ['Varukostnad','Direkt leveranspersonal','Underleverantörer','Övrigt direkt','Ej uppdragsfördelad personal']
        shares = [85,5,4,5,1] if a==0 else [8,60,17,7,8] if a==1 else [0,82,5,3,10]
        for ct,amount in zip(costtypes,allocate(total,shares)):
            rows['Direkta kostnader'].append({'Datumnyckel':key(d),'Områdesnyckel':a+1,'Kostnadstyp':ct,'Belopp':amount})
        if a:
            for j in range(v['jobs'][a-1]+2):
                rows['Uppdrag'].append({'Uppdragsnyckel':len(rows['Uppdrag'])+1,'Datumnyckel':key(m.replace(day=5+j%23)),'Kundnyckel':pool[j%len(pool)],'Områdesnyckel':a+1,'Status':'Avslutat' if j<v['jobs'][a-1] else 'Avbokat','Timmar':6+(j%11)*2})
    for ct,amount in zip(['Administration','Lokaler och drift','Avskrivningar'],allocate(v['central'],[72,22,6])):
        rows['Gemensamma kostnader'].append({'Datumnyckel':key(m.replace(day=15)),'Kostnadstyp':ct,'Belopp':amount})
    rows['Budget'].append({'Datumnyckel':key(m.replace(day=15)),'Rörelseresultat':v['budget']})

rows['Periodtyp'] = [{'Periodtyp':t,'Ordning':i} for i,t in enumerate(['R12','Helår','Månad'])]
for name,available in [('R12val',months[23:]),('Månadsval',months[12:]),('Helårsval',[date(2024,12,1),date(2025,12,1)])]:
    rows[name] = [{'Period':str(m.year) if name=='Helårsval' else f'{MONTHS[m.month-1].capitalize()} {m.year}','Slutdatum':end(m).isoformat(),'Ordning':m.year*100+m.month} for m in available]
rows['Trendaxel'] = [{'Månad':f'{MONTHS[m.month-1][:3].capitalize()} {str(m.year)[2:]}','Månadsstart':m.isoformat(),'Ordning':m.year*100+m.month} for m in months]
# Waterfall axes for every valid period; endpoints are data categories, never hardcoded.
bridge=[]
for typ,table in [('R12','R12val'),('Helår','Helårsval'),('Månad','Månadsval')]:
    for row in rows[table]:
        d=date.fromisoformat(row['Slutdatum'])
        prefix='R12 ' if typ=='R12' else ''
        label=str(d.year) if typ=='Helår' else f'{prefix}{MONTHS[d.month-1][:3]} {d.year}'
        old=str(d.year-1) if typ=='Helår' else f'{prefix}{MONTHS[d.month-1][:3]} {d.year-1}'
        for i,n in enumerate([old,'Produkter','Teknisk service','Bemanning','Gemensamma kostnader']):
            bridge.append({'Periodtyp':typ,'Slutdatum':d.isoformat(),'Steg':n,'Ordning':i})
rows['Bryggaxel']=bridge

specs = {
 'Datum': [('Datumnyckel','int64',True),('Datum','dateTime',False),('År','int64',False),('Månadsnummer','int64',True),('Månad','string',False),('Årmånad','string',False),('Kvartal','string',False)],
 'Kunder':[('Kundnyckel','int64',True),('Kund','string',False),('Ort','string',False)],
 'Områden':[('Områdesnyckel','int64',True),('Område','string',False)],
 'Försäljning':[('Fakturarad','int64',True),('Datumnyckel','int64',True),('Kundnyckel','int64',True),('Områdesnyckel','int64',True),('Nettointäkt','decimal',True),('Typ','string',True)],
 'Direkta kostnader':[('Datumnyckel','int64',True),('Områdesnyckel','int64',True),('Kostnadstyp','string',False),('Belopp','decimal',True)],
 'Gemensamma kostnader':[('Datumnyckel','int64',True),('Kostnadstyp','string',False),('Belopp','decimal',True)],
 'Uppdrag':[('Uppdragsnyckel','int64',True),('Datumnyckel','int64',True),('Kundnyckel','int64',True),('Områdesnyckel','int64',True),('Status','string',False),('Timmar','int64',True)],
 'Budget':[('Datumnyckel','int64',True),('Rörelseresultat','decimal',True)],
 'Periodtyp':[('Periodtyp','string',False),('Ordning','int64',True)],
 'Trendaxel':[('Månad','string',False),('Månadsstart','dateTime',True),('Ordning','int64',True)],
 'Bryggaxel':[('Periodtyp','string',True),('Slutdatum','dateTime',True),('Steg','string',False),('Ordning','int64',True)]}
for t in ['R12val','Månadsval','Helårsval']:
    specs[t]=[('Period','string',False),('Slutdatum','dateTime',True),('Ordning','int64',True)]

measures=[]
def add(name,dax,fmt='0',folder='Beräkningar',description=None):
    measures.append((name,dax,fmt,folder,description or f'{name}; räknas från modellen och aktuellt periodval.'))

add('Vald periodtyp','SELECTEDVALUE(\'Periodtyp\'[Periodtyp], "R12")','General','Period')
add('Senaste utfall','EOMONTH(MAXX(ALL(\'Försäljning\'), RELATED(\'Datum\'[Datum])),0)','yyyy-MM-dd','Period')
add('Periodslut','SWITCH([Vald periodtyp], "Helår", MAX(\'Helårsval\'[Slutdatum]), "Månad", MAX(\'Månadsval\'[Slutdatum]), MAX(\'R12val\'[Slutdatum]))','yyyy-MM-dd','Period')
add('Periodstart','VAR e=[Periodslut] RETURN SWITCH([Vald periodtyp], "Helår", DATE(YEAR(e),1,1), "Månad", DATE(YEAR(e),MONTH(e),1), EOMONTH(e,-12)+1)','yyyy-MM-dd','Period')
add('Jämförelsestart','EDATE([Periodstart],-12)','yyyy-MM-dd','Period')
add('Jämförelseslut','EOMONTH([Periodslut],-12)','yyyy-MM-dd','Period')
add('Periodtext','VAR mode=[Vald periodtyp] VAR currentLabel=SWITCH(mode,"Helår",FORMAT([Periodslut],"yyyy"),"Månad",FORMAT([Periodslut],"MMMM yyyy","sv-SE"),FORMAT([Periodstart],"MMM yyyy","sv-SE") & " – " & FORMAT([Periodslut],"MMM yyyy","sv-SE")) VAR previousLabel=SWITCH(mode,"Helår",FORMAT([Jämförelseslut],"yyyy"),"Månad",FORMAT([Jämförelseslut],"MMMM yyyy","sv-SE"),FORMAT([Jämförelsestart],"MMM yyyy","sv-SE") & " – " & FORMAT([Jämförelseslut],"MMM yyyy","sv-SE")) RETURN "Vald period: " & currentLabel & "    |    Jämför med: " & previousLabel','General','Period')
base = {'Nettoomsättning bas':"SUM('Försäljning'[Nettointäkt])",'Direkta kostnader bas':"SUM('Direkta kostnader'[Belopp])",'Bruttovinst bas':'[Nettoomsättning bas]-[Direkta kostnader bas]','Gemensamma kostnader bas':"SUM('Gemensamma kostnader'[Belopp])",'Rörelseresultat bas':'[Bruttovinst bas]-[Gemensamma kostnader bas]','Budget bas':"SUM('Budget'[Rörelseresultat])",'Uppdrag bas':"CALCULATE(DISTINCTCOUNT('Uppdrag'[Uppdragsnyckel]), 'Uppdrag'[Status]=\"Avslutat\")",'Kunder bas':"CALCULATE(DISTINCTCOUNT('Försäljning'[Kundnyckel]), 'Försäljning'[Nettointäkt]>0)"}
for n,dax in base.items(): add(n,dax,'#,##0','Bas')
for public,b in [('Nettoomsättning','Nettoomsättning bas'),('Bruttovinst','Bruttovinst bas'),('Rörelseresultat','Rörelseresultat bas'),('Gemensamma kostnader','Gemensamma kostnader bas'),('Budgetresultat','Budget bas'),('Utförda uppdrag','Uppdrag bas'),('Aktiva kunder','Kunder bas')]:
    for suffix,start,stop in [('', 'Periodstart','Periodslut'),(' föregående år','Jämförelsestart','Jämförelseslut')]:
        dax=f"VAR s=[{start}] VAR e=[{stop}] RETURN CALCULATE([{b}], REMOVEFILTERS('Datum'), DATESBETWEEN('Datum'[Datum],s,e))"
        if public=='Utförda uppdrag': dax=f"IF(SELECTEDVALUE('Områden'[Områdesnyckel])=1, BLANK(), {dax})"
        add(public+suffix,dax,'#,##0','Nyckeltal')
add('Bruttomarginal','DIVIDE([Bruttovinst],[Nettoomsättning])','0.0 %','Nyckeltal')
add('Rörelsemarginal','DIVIDE([Rörelseresultat],[Nettoomsättning])','0.0 %','Nyckeltal')
add('Resultat mot budget','[Rörelseresultat]-[Budgetresultat]','#,##0','Nyckeltal')
for n in ['Nettoomsättning','Bruttovinst','Rörelseresultat','Budgetresultat','Resultat mot budget']:
    add(n+' Mkr',f'[{n}]/1000000','0.0 "Mkr"' if n=='Nettoomsättning' else '0.00 "Mkr"','Visning')
for n in ['Nettoomsättning','Rörelseresultat','Utförda uppdrag']:
    add(n+' förändring',f'DIVIDE([{n}]-[{n} föregående år],[{n} föregående år])','+0.0 %;-0.0 %;0.0 %','Nyckeltal')
    add(n+' jämförelsetext',f'FORMAT([{n} förändring],"+0.0 %;−0.0 %;0.0 %","sv-SE") & " mot föregående år"','General','Visning')
add('Bruttovinst undertext','FORMAT([Bruttomarginal],"0.0 %","sv-SE") & " bruttomarginal"','General','Visning')
add('Rörelseresultat undertext','FORMAT([Rörelsemarginal],"0.0 %","sv-SE") & " marginal · " & FORMAT([Rörelseresultat förändring],"+0.0 %;−0.0 %;0.0 %","sv-SE") & " mot föregående år"','General','Visning')
add('Budget undertext','"Budget: " & FORMAT([Budgetresultat Mkr],"0.00","sv-SE") & " Mkr"','General','Visning')
add('Kunder undertext','FORMAT([Aktiva kunder]-[Aktiva kunder föregående år],"+0;−0;0","sv-SE") & " kunder mot föregående år"','General','Visning')
add('Budgetfärg','IF([Resultat mot budget]<0,"#B42318","#007956")','General','Visning')
for n in ['Nettoomsättning','Rörelseresultat','Utförda uppdrag']:
    add(n+' statusfärg',f'IF([{n} förändring]<0,"#B42318","#007956")','General','Visning')
add('Trendstart','IF([Vald periodtyp]="Helår",[Periodstart],EOMONTH([Periodslut],-12)+1)','yyyy-MM-dd','Trend')
add('Trendrubrik','IF([Vald periodtyp]="Månad","Omsättning och rörelsemarginal · historisk kontext","Omsättning och rörelsemarginal")','General','Trend')
add('Uppdragsrubrik','IF([Vald periodtyp]="Månad","Utförda uppdrag per månad · historisk kontext","Utförda uppdrag per månad")','General','Trend')
for n,b in [('Trendomsättning','Nettoomsättning bas'),('Trendresultat','Rörelseresultat bas'),('Trenduppdrag','Uppdrag bas')]:
    add(n,f"VAR m=SELECTEDVALUE('Trendaxel'[Månadsstart]) RETURN IF(m>=[Trendstart] && m<=[Periodslut], CALCULATE([{b}], REMOVEFILTERS('Datum'), DATESBETWEEN('Datum'[Datum],m,EOMONTH(m,0))))",'#,##0','Trend')
add('Omsättning','[Trendomsättning]/1000000','0.0','Trend')
add('Rörelsemarginal trend','DIVIDE([Trendresultat],[Trendomsättning])*100','0.0','Trend')
add('Teknisk service','CALCULATE([Trenduppdrag],\'Områden\'[Områdesnyckel]=2)','#,##0','Trend')
add('Bemanning','CALCULATE([Trenduppdrag],\'Områden\'[Områdesnyckel]=3)','#,##0','Trend')
add('Vald månadsmarkering','IF([Vald periodtyp]="Månad" && EOMONTH(SELECTEDVALUE(\'Trendaxel\'[Månadsstart]),0)=[Periodslut], [Rörelsemarginal trend])','0.0','Trend')
add('Trendfärg','IF([Vald periodtyp]="Månad" && EOMONTH(SELECTEDVALUE(\'Trendaxel\'[Månadsstart]),0)=[Periodslut],"#9B570B","#0F3163")','General','Trend')
add('Trendomsättning föregående år',"VAR m=SELECTEDVALUE('Trendaxel'[Månadsstart]) RETURN IF(NOT ISBLANK([Trendomsättning]), CALCULATE([Nettoomsättning bas], REMOVEFILTERS('Datum'), DATESBETWEEN('Datum'[Datum],EDATE(m,-12),EOMONTH(m,-12))))",'#,##0','Trend')
add('Trendomsättning förändring','DIVIDE([Trendomsättning]-[Trendomsättning föregående år],[Trendomsättning föregående år])','+0.0 %;-0.0 %;0.0 %','Trend')
add('Bryggsteg',"VAR t=[Vald periodtyp] VAR e=[Periodslut] VAR step=SELECTEDVALUE('Bryggaxel'[Ordning]) VAR valid=CALCULATE(COUNTROWS('Bryggaxel'),'Bryggaxel'[Periodtyp]=t,'Bryggaxel'[Slutdatum]=e) RETURN IF(valid>0, SWITCH(step,0,[Rörelseresultat föregående år],1,CALCULATE([Bruttovinst]-[Bruttovinst föregående år],'Områden'[Områdesnyckel]=1),2,CALCULATE([Bruttovinst]-[Bruttovinst föregående år],'Områden'[Områdesnyckel]=2),3,CALCULATE([Bruttovinst]-[Bruttovinst föregående år],'Områden'[Områdesnyckel]=3),4,-([Gemensamma kostnader]-[Gemensamma kostnader föregående år])))/1000000",'0.00','Brygga')
add('Bryggans slutetikett','IF([Vald periodtyp]="Helår",FORMAT([Periodslut],"yyyy"),IF([Vald periodtyp]="R12","R12 ","") & FORMAT([Periodslut],"MMM yyyy","sv-SE"))','General','Brygga')
add('Bryggkontroll',"[Rörelseresultat föregående år]+SUMX(ALL('Områden'),[Bruttovinst]-[Bruttovinst föregående år])-([Gemensamma kostnader]-[Gemensamma kostnader föregående år])-[Rörelseresultat]",'0','Kontroller')

add('Rörelsemarginal korttext','FORMAT([Rörelsemarginal],"0.0 %","sv-SE") & " marginal · " & FORMAT([Rörelseresultat förändring],"+0.0 %;−0.0 %;0.0 %","sv-SE")','General','Visning')
add('Kundförändring korttext','FORMAT([Aktiva kunder]-[Aktiva kunder föregående år],"+0;−0;0","sv-SE") & " mot föregående år"','General','Visning')

dump(MODEL/'definition.pbism',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json','version':'4.2','settings':{'qnaEnabled':False}})
save(MODEL/'definition/database.tmdl','database Ledningsrapport\n\tcompatibilityLevel: 1702\n')
save(MODEL/'definition/model.tmdl',"model Model\n\tculture: sv-SE\n\tsourceQueryCulture: en-US\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n\tdiscourageImplicitMeasures\n\n\tannotation PBI_TimeIntelligenceEnabled = 0\n\n"+''.join(f"ref table '{n}'\n" for n in specs))
save(MODEL/'definition/expressions.tmdl',f'expression DataFolder = "{DATA.as_posix()}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n')
types={'int64':'Int64.Type','dateTime':'type date','decimal':'Currency.Type','string':'type text'}
hashes={}
for name,columns in specs.items():
    DATA.mkdir(parents=True,exist_ok=True)
    with (DATA/(name+'.csv')).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=[n for n,_,_ in columns],lineterminator='\n');w.writeheader();w.writerows(rows[name])
    hashes[name]=hashlib.sha256((DATA/(name+'.csv')).read_bytes()).hexdigest()
    text=f"/// Reproducerbar lokal demodata; {name}.csv.\ntable '{name}'\n"
    if name=='Datum':text+='\tdataCategory: Time\n'
    if name=='Försäljning':
        for n,dax,fmt,folder,description in measures:
            text+=f"\n\t/// {description}\n\tmeasure '{n}' = {dax}\n\t\tformatString: {fmt}\n\t\tdisplayFolder: {folder}\n"
            if folder in ['Bas','Beräkningar','Kontroller']:text+='\t\tisHidden\n'
    for col,kind,hidden in columns:
        text+=f"\n\t/// Källfält i lokal demodata: {name}.{col}.\n\tcolumn '{col}'\n\t\tdataType: {kind}\n\t\tsourceColumn: {col}\n\t\tsummarizeBy: none\n"
        if hidden:text+='\t\tisHidden\n'
        if kind=='dateTime':text+='\t\tformatString: yyyy-MM-dd\n'
        if name=='Datum' and col=='Datum':text+='\t\tisKey\n'
        sorts={'Periodtyp':'Ordning','Period':'Ordning','Månad':'Månadsnummer' if name=='Datum' else 'Ordning','Område':'Områdesnyckel','Steg':'Ordning'}
        if col in sorts:text+=f"\t\tsortByColumn: '{sorts[col]}'\n"
    cast=', '.join('{"'+col+'", '+types[kind]+'}' for col,kind,_ in columns)
    text+=f'\n\tpartition "PLACEHOLDER" = m\n\t\tmode: import\n\t\tsource =\n\t\t\tlet\n\t\t\t\tSource = Csv.Document(File.Contents(DataFolder & "/{name}.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n\t\t\t\tHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n\t\t\t\tTyped = Table.TransformColumnTypes(Headers, {{{cast}}}, "en-US")\n\t\t\tin\n\t\t\t\tTyped\n'
    text=text.replace('"PLACEHOLDER"',"'"+name+"'")
    save(MODEL/f'definition/tables/{name}.tmdl',text)
rels=[]
for fact in ['Försäljning','Direkta kostnader','Gemensamma kostnader','Uppdrag','Budget']:
    dims=[('Datum','Datumnyckel')]
    if fact in ['Försäljning','Direkta kostnader','Uppdrag']:dims+=[('Områden','Områdesnyckel')]
    if fact in ['Försäljning','Uppdrag']:dims+=[('Kunder','Kundnyckel')]
    for dim,col in dims:
        rels.append(f"relationship '{fact} till {dim}'\n\tfromColumn: '{fact}'.'{col}'\n\ttoColumn: '{dim}'.'{col}'\n\tcrossFilteringBehavior: oneDirection\n\tfromCardinality: many\n\ttoCardinality: one\n")
save(MODEL/'definition/relationships.tmdl','\n'.join(rels))
dump(DATA/'manifest.json',{'generator':'scripts/generate-ledningsrapport.py','period':'2023-01-01–2026-10-31','currency':'SEK, redan skalat 5× jämfört med referensbilden','rows':{n:len(r) for n,r in rows.items()},'sha256':hashes,'measures':len(measures),'assumptions':'Nettointäkter exkl moms inklusive kreditnotor. Alla direkta personalkostnader inkluderade, också ej uppdragsfördelade. Gemensamma kostnader inkluderar avskrivningar. Uppdrag har en rad per unik identitet; avbokade exkluderas. Kund 301 har endast kreditnotor. Oktober 2026 är komplett demoutfall.'})
print(f'Generated {len(specs)} tables and {len(measures)} measures in {BASE}')
if '--data-only' in sys.argv and (MODEL/'definition/tables/Artiklar.tmdl').exists():
    # Preserve the installed sales extension whenever the common dummy facts are regenerated.
    import subprocess
    subprocess.run([sys.executable,str(ROOT/'scripts/extend-sales-overview-data.py')],check=True)
