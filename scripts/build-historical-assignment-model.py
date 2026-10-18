"""Historical assignment analysis; never read bookings or forecast amounts."""
from pathlib import Path
from collections import defaultdict
from decimal import Decimal
import csv,json,re,hashlib,random
BASE=Path(__file__).resolve().parents[1]/'powerbi-ledningsrapport';DATA=BASE/'data';MODEL=BASE/'Ledningsrapport.SemanticModel/definition'
def read(n):
 with (DATA/(n+'.csv')).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
jobs={int(r['UppdragID']):r for r in read('Uppdragsregister')}
capacity=defaultdict(Decimal);billed=defaultdict(Decimal);other=defaultdict(Decimal)
latest=int(read('Planinställning')[0]['SenasteUtfall'].replace('-',''))
for r in read('Arbetskapacitet'):
 if int(r['Datumnyckel'])<=latest:capacity[int(r['ResursID']),int(r['Datumnyckel'])//100]+=Decimal(r['Tillgängligt'])
for r in read('Utförd tid'):
 if int(r['Datumnyckel'])>latest or r['Godkänd']!='Ja':continue
 key=int(jobs[int(r['UppdragID'])]['ResursID']),int(r['Datumnyckel'])//100
 (billed if r['Debiterbar']=='Ja' else other)[key]+=Decimal(r['Timmar'])
rows=[];over=0
for (resource,month),cap in sorted(capacity.items()):
 bill=billed[resource,month];non=other[resource,month];remaining=max(Decimal(0),cap-bill-non)
 rng=random.Random(resource*1000000+month)
 # Synthetic historical time classifications; capacity and approved billable
 # hours are existing observations. They are not future bookings.
 unreported=(remaining*Decimal(str(rng.uniform(.10,.22)))).quantize(Decimal('.0001'))
 customer=(remaining*Decimal(str(rng.uniform(.09,.22)))).quantize(Decimal('.0001'))
 internal=remaining-customer-unreported
 if bill+non>cap:over+=1
 rows.append(dict(ResursID=resource,Datumnyckel=month*100+1,Debiterbart=str(bill),EjDebiterbartKundarbete=str(non+customer),InterntArbete=str(internal),EjTidrapporterat=str(unreported),Tillgängligt=str(cap)))
 assert abs(bill+non+customer+internal+unreported-cap)<Decimal('.001') or bill+non>cap
p=DATA/'Tidsanvändning.csv'
with p.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
fields=list(rows[0]);s="/// Historisk tid per resurs och månad; residualens kategorier är syntetisk demodata.\ntable 'Tidsanvändning'\n"
for field in fields:
 s+=f"\n\tcolumn '{field}'\n\t\tdataType: {'int64' if field in ['ResursID','Datumnyckel'] else 'double'}\n\t\tisHidden\n\t\tsourceColumn: {field}\n\t\tsummarizeBy: none\n"
casts=','.join('{"'+field+'", '+('Int64.Type' if field in ['ResursID','Datumnyckel'] else 'type number')+'}' for field in fields)
s+='''
\tpartition 'Tidsanvändning' = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t Source=Csv.Document(File.Contents(DataFolder & "/Tidsanvändning.csv"),[Delimiter=",",Encoding=65001,QuoteStyle=QuoteStyle.Csv]),
\t\t\t Headers=Table.PromoteHeaders(Source,[PromoteAllScalars=true]),
\t\t\t Typed=Table.TransformColumnTypes(Headers,{'''+casts+'''},"en-US")
\t\t\tin Typed
'''
target=MODEL/'tables/Tidsanvändning.tmdl'
if not target.exists():target.write_text(s,encoding='utf-8')
p=MODEL/'model.tmdl';s=p.read_text(encoding='utf-8-sig')
if "ref table 'Tidsanvändning'" not in s:p.write_text(s+"\nref table 'Tidsanvändning'\n",encoding='utf-8')
p=MODEL/'relationships.tmdl';s=p.read_text(encoding='utf-8-sig')
if "relationship 'Historisk tidsanvändning till Resurser'" not in s:
 s+="\nrelationship 'Historisk tidsanvändning till Resurser'\n\tfromColumn: 'Tidsanvändning'.ResursID\n\ttoColumn: Resurser.ResursID\n\tfromCardinality: many\n\ttoCardinality: one\n\tcrossFilteringBehavior: oneDirection\n"
 p.write_text(s,encoding='utf-8')

measures={}
def add(name,expr,fmt='#,##0'):measures[name]=(expr,fmt)
selection='''VAR _g=SELECTEDVALUE('Resursval'[Resursgrupp],"Alla")
VAR _valid=CALCULATE(COUNTROWS('Resurser'),REMOVEFILTERS('Resurser'[ResursID],'Resurser'[Medarbetare],'Resurser'[Resursgrupp]),'Resurser'[Resursgrupp]=_g)>0
VAR _ids=CALCULATETABLE(VALUES('Resurser'[ResursID]),KEEPFILTERS(FILTER(VALUES('Resurser'[Resursgrupp]),_g="Alla" || NOT _valid || 'Resurser'[Resursgrupp]=_g)))
'''
add('Historiskt periodslut',"MIN([Periodslut],MAX('Planinställning'[SenasteUtfall]))",'yyyy-MM-dd')
add('Historiskt jämförelseslut','EOMONTH([Historiskt periodslut],-12)','yyyy-MM-dd')
add('Utfall periodtext','VAR _s=[Periodstart] VAR _e=[Historiskt periodslut] RETURN IF(_e<_s,"Ingen historik i vald period", "Vald period: " & FORMAT(_s,"MMMM yyyy","sv-SE") & "–" & FORMAT(_e,"MMMM yyyy","sv-SE"))','@')
add('Historisk tabellrubrik','"Uppdrag aktiva under vald period · Utfall t.o.m. " & FORMAT([Historiskt periodslut],"d MMMM yyyy","sv-SE")','@')
add('Historisk trendtext','IF([Vald periodtyp]="Månad","12 månaders historik till " & FORMAT([Historiskt periodslut],"MMM yyyy","sv-SE"),FORMAT([Periodstart],"MMM yyyy","sv-SE") & "–" & FORMAT([Historiskt periodslut],"MMM yyyy","sv-SE"))','@')
add('Historisk tidsrubrik','"Tillgängliga timmar per månad · " & FORMAT([Periodstart],"MMM yyyy","sv-SE") & "–" & FORMAT([Historiskt periodslut],"MMM yyyy","sv-SE")','@')
add('Historisk heatrubrik','"Historiskt utfall · " & FORMAT([Periodstart],"MMM yyyy","sv-SE") & "–" & FORMAT([Historiskt periodslut],"MMM yyyy","sv-SE")','@')

for label,field in [('Tid debiterbar','Debiterbart'),('Tid kundarbete','EjDebiterbartKundarbete'),('Tid internt','InterntArbete'),('Tid ej rapporterat','EjTidrapporterat'),('Tid tillgänglig','Tillgängligt')]:
 for suffix,trend in [('',False),(' trend',True)]:
  dates="VAR _m=SELECTEDVALUE('Trendaxel'[Månadsstart]) VAR _s=VALUE(FORMAT(_m,\"yyyyMMdd\")) VAR _e=VALUE(FORMAT(MIN(EOMONTH(_m,0),[Historiskt periodslut]),\"yyyyMMdd\"))" if trend else 'VAR _s=VALUE(FORMAT([Periodstart],"yyyyMMdd")) VAR _e=VALUE(FORMAT([Historiskt periodslut],"yyyyMMdd"))'
  guard="_m>=[Periodstart] && _m<=[Historiskt periodslut]" if trend else '[Periodstart]<=[Historiskt periodslut]'
  add(label+suffix,selection+dates+f" RETURN IF({guard},CALCULATE(SUM('Tidsanvändning'[{field}]),REMOVEFILTERS('Datum'),TREATAS(_ids,'Resurser'[ResursID]),FILTER(ALL('Tidsanvändning'[Datumnyckel]),'Tidsanvändning'[Datumnyckel]>=_s && 'Tidsanvändning'[Datumnyckel]<=_e)))",'#,##0' if trend else '#,##0" h"')
add('Utfall ej debiterbara timmar','[Tid kundarbete]+[Tid internt]+[Tid ej rapporterat]','#,##0" h"')
add('Ej debiterbart jämförelse','FORMAT(DIVIDE([Utfall ej debiterbara timmar],[Tid tillgänglig]),"0.0 %","sv-SE") & " av tillgänglig tid"','@')
add('Tid kapacitetsavvikelse','VAR _total=[Tid debiterbar]+[Tid kundarbete]+[Tid internt]+[Tid ej rapporterat] RETURN IF(NOT ISBLANK([Tid tillgänglig]),MAX(0,_total-[Tid tillgänglig]))','#,##0" h"')
add('Tid kapacitetsavvikelse trend','VAR _total=[Tid debiterbar trend]+[Tid kundarbete trend]+[Tid internt trend]+[Tid ej rapporterat trend] RETURN IF(NOT ISBLANK([Tid tillgänglig trend]),MAX(0,_total-[Tid tillgänglig trend]))','#,##0" h"')
add('Tid summering','VAR _total=[Tid tillgänglig] VAR _over=[Tid kapacitetsavvikelse] RETURN IF(NOT ISBLANK(_total),"Tillgängligt: " & FORMAT(_total,"#,##0","sv-SE") & " h · Debiterbart " & FORMAT([Tid debiterbar],"#,##0","sv-SE") & " h (" & FORMAT(DIVIDE([Tid debiterbar],_total),"0.0 %","sv-SE") & ")" & IF(_over>.01," · Rapporterat över kapacitet: " & FORMAT(_over,"#,##0","sv-SE") & " h"))','@')
add('Historisk cellgrad','DIVIDE([Tid debiterbar trend],[Tid tillgänglig trend])','0 %')
add('Historisk cellfärg','VAR _v=[Historisk cellgrad] RETURN IF(ISBLANK(_v),BLANK(),IF(_v<.75,"#FAD5D1",IF(_v<.82,"#DCEBFA","#CDEEE5")))','@')

# Keep existing public KPI names, but cut all history at the latest actual date.
for name,base,table,col,extra,fmt in [
 ('Uppdrag utförda',"DISTINCTCOUNT('Uppdragsregister'[UppdragID])",'Uppdragsregister','Slutförd',",'Uppdragsregister'[Status]=\"Avslutat\"",'#,##0'),
 ('Utfall timmar',"SUM('Utförd tid'[Timmar])",'Utförd tid','Datumnyckel',",'Utförd tid'[Godkänd]=\"Ja\",'Utförd tid'[Debiterbar]=\"Ja\"",'#,##0" h"'),
 ('Utfall kapacitet',"SUM('Arbetskapacitet'[Tillgängligt])",'Arbetskapacitet','Datumnyckel','', '#,##0'),
 ('Utfall intäkt',"SUM('Uppdragsekonomi'[Intäkt])",'Uppdragsekonomi','Datumnyckel','', '#,##0'),
 ('Utfall kostnad',"SUM('Uppdragsekonomi'[DirektKostnad])",'Uppdragsekonomi','Datumnyckel','', '#,##0'),
 ('Utfall kalkylkostnad',"SUM('Uppdragsekonomi'[Kalkylkostnad])",'Uppdragsekonomi','Datumnyckel','', '#,##0')]:
 for suffix,start,end in [('', '[Periodstart]','[Historiskt periodslut]'),(' föregående','[Jämförelsestart]','[Historiskt jämförelseslut]')]:
  add(name+suffix,selection+f'VAR _s=VALUE(FORMAT({start},"yyyyMMdd")) VAR _e=VALUE(FORMAT({end},"yyyyMMdd")) RETURN IF(_s<=_e,CALCULATE({base},REMOVEFILTERS(\'Datum\'),TREATAS(_ids,\'Resurser\'[ResursID]),FILTER(ALL(\'{table}\'[{col}]),\'{table}\'[{col}]>=_s && \'{table}\'[{col}]<=_e){extra}))',fmt)
for name,table,base in [('Trend timmar','Utförd tid',"SUM('Utförd tid'[Timmar])"),('Trend kapacitet','Arbetskapacitet',"SUM('Arbetskapacitet'[Tillgängligt])")]:
 extra=",'Utförd tid'[Godkänd]=\"Ja\",'Utförd tid'[Debiterbar]=\"Ja\"" if table=='Utförd tid' else ''
 add(name,selection+f'VAR _m=SELECTEDVALUE(\'Trendaxel\'[Månadsstart]) VAR _s=VALUE(FORMAT(_m,"yyyyMMdd")) VAR _e=VALUE(FORMAT(MIN(EOMONTH(_m,0),[Historiskt periodslut]),"yyyyMMdd")) RETURN IF(_m>=[Trendstart] && _m<=[Historiskt periodslut],CALCULATE({base},REMOVEFILTERS(\'Datum\'),TREATAS(_ids,\'Resurser\'[ResursID]),FILTER(ALL(\'{table}\'[Datumnyckel]),\'{table}\'[Datumnyckel]>=_s && \'{table}\'[Datumnyckel]<=_e){extra}))')

for name,table,base in [('Uppdrag timmar periodslut','Utförd tid',"SUM('Utförd tid'[Timmar])"),('Uppdrag intäkt periodslut','Uppdragsekonomi',"SUM('Uppdragsekonomi'[Intäkt])"),('Uppdrag kostnad periodslut','Uppdragsekonomi',"SUM('Uppdragsekonomi'[DirektKostnad])")]:
 extra=",'Utförd tid'[Godkänd]=\"Ja\"" if table=='Utförd tid' else ''
 add(name,f'VAR _e=VALUE(FORMAT([Historiskt periodslut],"yyyyMMdd")) RETURN IF(HASONEVALUE(\'Uppdragsregister\'[UppdragID]),CALCULATE({base},REMOVEFILTERS(\'Datum\'),REMOVEFILTERS(\'Trendaxel\'),FILTER(ALL(\'{table}\'[Datumnyckel]),\'{table}\'[Datumnyckel]<=_e){extra}))','#,##0" h"' if table=='Utförd tid' else '#,##0')
add('Uppdrag planerade',"SELECTEDVALUE('Uppdragsregister'[PlaneradeTimmar])",'#,##0" h"')
add('Uppdrag faktisk marginal','VAR _r=[Uppdrag intäkt periodslut] RETURN DIVIDE(_r-[Uppdrag kostnad periodslut],_r)','0.0 %')
add('Uppdrag faktisk marginaltext','VAR _v=[Uppdrag faktisk marginal] RETURN IF(ISBLANK(_v),"—",FORMAT(_v,"0.0 %","sv-SE"))','@')
add('Uppdrag status historisk','VAR _end=SELECTEDVALUE(\'Uppdragsregister\'[Slutförd]) VAR _e=VALUE(FORMAT([Historiskt periodslut],"yyyyMMdd")) RETURN IF(HASONEVALUE(\'Uppdragsregister\'[UppdragID]),IF(NOT ISBLANK(_end) && _end>0 && _end<=_e,"Avslutat","Pågående"))','@')
add('Uppdrag risk','VAR _h=[Uppdrag timmar periodslut] VAR _p=[Uppdrag planerade] VAR _m=[Uppdrag faktisk marginal] VAR _c=[Uppdrag kalkyl] RETURN IF(HASONEVALUE(\'Uppdragsregister\'[UppdragID]) && ((NOT ISBLANK(_h) && NOT ISBLANK(_p) && _h>_p) || (NOT ISBLANK(_m) && NOT ISBLANK(_c) && _m<=_c-.02)),1,0)')
add('Uppdrag marginalfärg','VAR _v=[Uppdrag faktisk marginal] RETURN IF(ISBLANK(_v),"#5B6B80",IF(_v<[Uppdrag kalkyl],"#B42318",IF(_v>[Uppdrag kalkyl],"#007956","#0F3163")))','@')
add('Uppdrag marginalbakgrund','VAR _v=[Uppdrag faktisk marginal] RETURN IF(ISBLANK(_v),"#F3F6FA",IF(_v<[Uppdrag kalkyl],"#FAD5D1",IF(_v>[Uppdrag kalkyl],"#CDEEE5","#EEF2F7")))','@')
add('Uppdrag synligt',selection+'''VAR _s=[Periodstart] VAR _e=[Historiskt periodslut]
VAR _start=SELECTEDVALUE('Uppdragsregister'[Startdatum]) VAR _end=SELECTEDVALUE('Uppdragsregister'[Slutdatum])
VAR _status=SELECTEDVALUE('Uppdragsstatusval'[Urval],"Alla") VAR _pid=SELECTEDVALUE('Uppdragsregister'[ResursID])
RETURN IF(HASONEVALUE('Uppdragsregister'[UppdragID]) && _pid IN _ids && _start<=_e && _s<=_e && (ISBLANK(_end) || _end>=_s) && SWITCH(_status,"Pågående",[Uppdrag status historisk]="Pågående","Avslutade",[Uppdrag status historisk]="Avslutat","Behöver uppföljning",[Uppdrag risk]=1,TRUE()),1,0)''')
add('Uppdrag över tidskalkyl',selection+'''VAR _s=VALUE(FORMAT([Periodstart],"yyyyMMdd")) VAR _e=VALUE(FORMAT([Historiskt periodslut],"yyyyMMdd"))
VAR _jobs=CALCULATETABLE(VALUES('Uppdragsregister'[UppdragID]),TREATAS(_ids,'Resurser'[ResursID]),FILTER(ALL('Uppdragsregister'[Slutförd]),'Uppdragsregister'[Slutförd]>=_s && 'Uppdragsregister'[Slutförd]<=_e),'Uppdragsregister'[Status]="Avslutat")
RETURN IF(_s<=_e,COALESCE(COUNTROWS(FILTER(_jobs,VAR _hours=[Uppdrag timmar periodslut] VAR _plan=[Uppdrag planerade] RETURN NOT ISBLANK(_hours) && NOT ISBLANK(_plan) && _hours>_plan)),0))''')
add('Tidskalkyl jämförelse','FORMAT(DIVIDE([Uppdrag över tidskalkyl],[Uppdrag utförda]),"0.0 %","sv-SE") & " av " & FORMAT([Uppdrag utförda],"#,##0","sv-SE") & " avslutade"','@')
add('Uppdrag detaljtext','IF(HASONEVALUE(\'Uppdragsregister\'[UppdragID]),SELECTEDVALUE(\'Uppdragsregister\'[Ansvarig]) & " · Intäkt " & FORMAT([Uppdrag intäkt periodslut]/1000,"#,##0","sv-SE") & " tkr · Direkt kostnad " & FORMAT([Uppdrag kostnad periodslut]/1000,"#,##0","sv-SE") & " tkr · Faktiskt utfall t.o.m. " & FORMAT([Historiskt periodslut],"d MMM yyyy","sv-SE"),"Klicka på ett uppdrag för historiska intäkter, kostnader och ansvarig.")','@')
add('Grad jämförelsefärg','IF([Utfall debiteringsgrad]<[Utfall mål],"#B42318","#007956")','@')
add('Marginal jämförelsefärg','IF([Utfall marginal]<[Utfall kalkylmarginal],"#B42318","#007956")','@')
p=MODEL/'tables/Planinställning.tmdl';s=p.read_text(encoding='utf-8-sig')
for name,(expr,fmt) in measures.items():
 block="\tmeasure '"+name+"' = ```\n"+''.join('\t\t\t'+line+'\n' for line in expr.splitlines())+'\t\t\t```'
 pattern=r"\tmeasure '"+re.escape(name)+r"' =\s*.*?(?=\n\t\tformatString:)"
 if re.search(pattern,s,re.S):
  s=re.sub(pattern,lambda _:block,s,flags=re.S)
  s=re.sub(r"(\tmeasure '"+re.escape(name)+r"' =\s*.*?\n\t\tformatString: )[^\n]+",lambda m:m.group(1)+fmt,s,flags=re.S)
 else:s=s.replace('\n\tcolumn ','\n'+block+'\n\t\tformatString: '+fmt+'\n\t\tdisplayFolder: Uppdrag\\Historik\n\n\tcolumn ',1)
p.write_text(s,encoding='utf-8')
manifest=json.loads((DATA/'manifest.json').read_text(encoding='utf-8'))
manifest['rows']['Tidsanvändning']=len(rows);manifest['sha256']['Tidsanvändning']=hashlib.sha256((DATA/'Tidsanvändning.csv').read_bytes()).hexdigest()
(DATA/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report=dict(status='prepared',newTable='Tidsanvändning',monthlyResourceRows=len(rows),overreportedResourceMonths=over,changedMeasures=list(measures),latestActual=latest,syntheticFields=['EjDebiterbartKundarbete residual','InterntArbete','EjTidrapporterat'])
(BASE/'validation/historical-assignment-model.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='changedMeasures'}))
