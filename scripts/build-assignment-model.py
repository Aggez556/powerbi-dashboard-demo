"""Add separate historical/plan facts to the original semantic model."""
from pathlib import Path
import csv,json
BASE=Path(__file__).resolve().parents[1]/'powerbi-ledningsrapport';MODEL=BASE/'Ledningsrapport.SemanticModel/definition';DATA=BASE/'data'
def q(s):return "'"+s.replace("'","''")+"'"
names=['Resurser','Uppdragsregister','Utförd tid','Uppdragsekonomi','Arbetskapacitet','Planbokningar','Planveckor','Planinställning','Uppdragsområden','Resursval','Uppdragsstatusval']
integer={'ResursID','GruppID','Områdesnyckel','UppdragID','Kundnyckel','Datumnyckel','Slutförd','VeckaID','Snapshot'}
dates={'Startdatum','Slutdatum','Veckostart','Veckoslut','Planläge','Från','Till','SenasteUtfall'}
numeric={'Veckotimmar','Mål','PlaneradeTimmar','Kalkylmarginal','Slutintäkt','KostnadHittills','ÅterståendeKostnad','Timmar','Intäkt','DirektKostnad','Kalkylkostnad','Schematimmar','Frånvaro','Tillgängligt','Kapacitet','Bokat','Ledigt','Överbokat'}
measures={}
def add(n,e,f='#,##0'):measures[n]=(e,f)
# The disconnected group selector falls back to all resources in the selected
# area if an old selected group no longer belongs to that area. The visible
# effective-selection label makes that fallback explicit.
selection="""VAR _g=SELECTEDVALUE('Resursval'[Resursgrupp],"Alla")
VAR _valid=CALCULATE(COUNTROWS('Resurser'),REMOVEFILTERS('Resurser'[ResursID],'Resurser'[Medarbetare],'Resurser'[Resursgrupp]),'Resurser'[Resursgrupp]=_g)>0
VAR _ids=CALCULATETABLE(VALUES('Resurser'[ResursID]),KEEPFILTERS(FILTER(VALUES('Resurser'[Resursgrupp]),_g="Alla" || NOT _valid || 'Resurser'[Resursgrupp]=_g)))
"""
add('Resursval tillgängligt','VAR _g=SELECTEDVALUE(\'Resursval\'[Resursgrupp]) RETURN IF(_g="Alla" || CALCULATE(COUNTROWS(\'Resurser\'),\'Resurser\'[Resursgrupp]=_g)>0,1,0)')
add('Resursurval text',selection+'RETURN IF(_g="Alla","Alla resursgrupper",IF(_valid,_g,"Alla resursgrupper · tidigare grupp gäller inte området"))','@')
add('Planläge datum',"MAX('Planinställning'[Planläge])",'yyyy-MM-dd')
add('Planperiod text','"Kommande beläggning · Planläge: " & FORMAT([Planläge datum],"d MMM yyyy","sv-SE") & " · " & FORMAT(MAX(\'Planinställning\'[Från]),"d MMM","sv-SE") & "–" & FORMAT(MAX(\'Planinställning\'[Till]),"d MMM yyyy","sv-SE")','@')
add('Utfall periodtext','"Historiskt utfall · " & FORMAT([Periodstart],"MMM yyyy","sv-SE") & "–" & FORMAT([Periodslut],"MMM yyyy","sv-SE")','@')
add('Uppdrag trendrubrik','IF([Vald periodtyp]="Månad","Debiteringsgrad · senaste 12 mån, vald månad markerad","Debiteringsgrad över tid")','@')
for name,base in [('Uppdrag utförda',"DISTINCTCOUNT('Uppdragsregister'[UppdragID])"),('Utfall timmar',"SUM('Utförd tid'[Timmar])"),('Utfall kapacitet',"SUM('Arbetskapacitet'[Tillgängligt])"),('Utfall intäkt',"SUM('Uppdragsekonomi'[Intäkt])"),('Utfall kostnad',"SUM('Uppdragsekonomi'[DirektKostnad])"),('Utfall kalkylkostnad',"SUM('Uppdragsekonomi'[Kalkylkostnad])")]:
 for suffix,start,end in [('', '[Periodstart]','[Periodslut]'),(' föregående','[Jämförelsestart]','[Jämförelseslut]')]:
  table='Uppdragsregister' if name=='Uppdrag utförda' else 'Utförd tid' if name=='Utfall timmar' else 'Arbetskapacitet' if name=='Utfall kapacitet' else 'Uppdragsekonomi'
  col='Slutförd' if name=='Uppdrag utförda' else 'Datumnyckel'
  extra=",'Uppdragsregister'[Status]=\"Avslutat\"" if name=='Uppdrag utförda' else ''
  add(name+suffix,selection+f'VAR _s=VALUE(FORMAT({start},"yyyyMMdd")) VAR _e=VALUE(FORMAT({end},"yyyyMMdd")) RETURN CALCULATE({base},REMOVEFILTERS(\'Datum\'),TREATAS(_ids,\'Resurser\'[ResursID]),FILTER(ALL({q(table)}[{col}]),{q(table)}[{col}]>=_s && {q(table)}[{col}]<=_e){extra})')
add('Utfall debiteringsgrad','DIVIDE([Utfall timmar],[Utfall kapacitet])','0.0 %')
add('Utfall mål',selection+"VAR _s=VALUE(FORMAT([Periodstart],\"yyyyMMdd\")) VAR _e=VALUE(FORMAT([Periodslut],\"yyyyMMdd\")) RETURN DIVIDE(CALCULATE(SUMX('Arbetskapacitet','Arbetskapacitet'[Tillgängligt]*RELATED('Resurser'[Mål])),TREATAS(_ids,'Resurser'[ResursID]),FILTER(ALL('Arbetskapacitet'[Datumnyckel]),'Arbetskapacitet'[Datumnyckel]>=_s && 'Arbetskapacitet'[Datumnyckel]<=_e)),[Utfall kapacitet])",'0.0 %')
add('Utfall marginal','DIVIDE([Utfall intäkt]-[Utfall kostnad],[Utfall intäkt])','0.0 %')
add('Utfall kalkylmarginal','DIVIDE([Utfall intäkt]-[Utfall kalkylkostnad],[Utfall intäkt])','0.0 %')
for name,col in [('Plan bokat','Bokat'),('Plan kapacitet','Kapacitet'),('Plan ledigt','Ledigt'),('Plan överbeläggning','Överbokat')]:
 add(name,selection+f"VAR _snap=VALUE(FORMAT([Planläge datum],\"yyyyMMdd\")) RETURN CALCULATE(SUM('Planbokningar'[{col}]),TREATAS(_ids,'Resurser'[ResursID]),REMOVEFILTERS('Datum'),REMOVEFILTERS('Trendaxel'),REMOVEFILTERS('Periodtyp'),REMOVEFILTERS('R12val'),REMOVEFILTERS('Helårsval'),REMOVEFILTERS('Månadsval'),'Planbokningar'[Snapshot]=_snap)")
add('Plan beläggning','DIVIDE([Plan bokat],[Plan kapacitet])','0 %')
add('Plan celltext','IF([Plan kapacitet]=0,IF([Plan bokat]>0,"⚠ Saknar kapacitet","—"),FORMAT([Plan beläggning],"0 %","sv-SE"))','@')
add('Plan cellfärg','SWITCH(TRUE(),[Plan kapacitet]=0,"#E5E7EB",[Plan beläggning]>1,"#FAD5D1",[Plan beläggning]>=.8,"#CDEEE5","#DCEBFA")','@')
add('Plan textfärg','IF([Plan överbeläggning]>0,"#B42318","#0F3163")','@')
add('Plan bokat teknisk',"CALCULATE([Plan bokat],KEEPFILTERS('Resurser'[Områdesnyckel]=2))")
add('Plan bokat bemanning',"CALCULATE([Plan bokat],KEEPFILTERS('Resurser'[Områdesnyckel]=3))")
for n,base in [('Trend timmar',"SUM('Utförd tid'[Timmar])"),('Trend kapacitet',"SUM('Arbetskapacitet'[Tillgängligt])")]:
 t='Utförd tid' if n=='Trend timmar' else 'Arbetskapacitet'
 add(n,selection+f"VAR _m=SELECTEDVALUE('Trendaxel'[Månadsstart]) VAR _s=VALUE(FORMAT(_m,\"yyyyMMdd\")) VAR _e=VALUE(FORMAT(EOMONTH(_m,0),\"yyyyMMdd\")) RETURN IF(_m>=[Trendstart] && _m<=[Periodslut],CALCULATE({base},TREATAS(_ids,'Resurser'[ResursID]),FILTER(ALL({q(t)}[Datumnyckel]),{q(t)}[Datumnyckel]>=_s && {q(t)}[Datumnyckel]<=_e)))")
add('Trend grad','DIVIDE([Trend timmar],[Trend kapacitet])','0 %')
add('Trend teknisk',"CALCULATE([Trend grad],KEEPFILTERS('Resurser'[Områdesnyckel]=2))",'0 %')
add('Trend bemanning',"CALCULATE([Trend grad],KEEPFILTERS('Resurser'[Områdesnyckel]=3))",'0 %')
add('Trend mål',"IF(NOT ISBLANK([Trend kapacitet]),DIVIDE(SUMX('Resurser','Resurser'[Veckotimmar]*'Resurser'[Mål]),SUM('Resurser'[Veckotimmar])))",'0 %')
add('Trend vald månad','IF([Vald periodtyp]="Månad" && EOMONTH(SELECTEDVALUE(\'Trendaxel\'[Månadsstart]),0)=[Periodslut],[Trend grad])','0 %')
add('Uppdrag hela timmar',"IF(HASONEVALUE('Uppdragsregister'[UppdragID]),CALCULATE(SUM('Utförd tid'[Timmar]),REMOVEFILTERS('Datum'),REMOVEFILTERS('Trendaxel')))")
add('Uppdrag hela intäkt',"IF(HASONEVALUE('Uppdragsregister'[UppdragID]),SUM('Uppdragsekonomi'[Intäkt]))")
add('Uppdrag hela kostnad',"IF(HASONEVALUE('Uppdragsregister'[UppdragID]),SUM('Uppdragsekonomi'[DirektKostnad]))")
add('Uppdrag planerade',"SELECTEDVALUE('Uppdragsregister'[PlaneradeTimmar])")
add('Uppdrag kalkyl',"SELECTEDVALUE('Uppdragsregister'[Kalkylmarginal])",'0.0 %')
add('Uppdrag prognos',"VAR _r=SELECTEDVALUE('Uppdragsregister'[Slutintäkt]) RETURN DIVIDE(_r-SELECTEDVALUE('Uppdragsregister'[KostnadHittills])-SELECTEDVALUE('Uppdragsregister'[ÅterståendeKostnad]),_r)",'0.0 %')
add('Uppdrag risk',"IF(SELECTEDVALUE('Uppdragsregister'[Status])=\"Pågående\" && ([Uppdrag hela timmar]>[Uppdrag planerade] || [Uppdrag prognos]<=[Uppdrag kalkyl]-.02+0.0000001),1,0)")
add('Uppdrag riskikon','IF([Uppdrag risk]=1,"⚠","")','@')
add('Uppdrag riskfärg','IF([Uppdrag risk]=1,"#B42318","#0F3163")','@')
add('Uppdrag marginalfärg','IF([Uppdrag prognos]<=[Uppdrag kalkyl]-.02+0.0000001,"#B42318",IF([Uppdrag prognos]>[Uppdrag kalkyl],"#007956","#0F3163"))','@')
add('Uppdrag kund',"SELECTEDVALUE('Kunder'[Kund],MAXX('Uppdragsregister',RELATED('Kunder'[Kund])))",'@')
add('Uppdrag synligt',selection+"VAR _s=[Periodstart] VAR _e=[Periodslut] VAR _start=SELECTEDVALUE('Uppdragsregister'[Startdatum]) VAR _end=SELECTEDVALUE('Uppdragsregister'[Slutdatum]) VAR _status=SELECTEDVALUE('Uppdragsstatusval'[Urval],\"Alla\") VAR _pid=SELECTEDVALUE('Uppdragsregister'[ResursID]) RETURN IF(HASONEVALUE('Uppdragsregister'[UppdragID]) && _pid IN _ids && _start<=_e && (ISBLANK(_end) || _end>=_s) && SWITCH(_status,\"Pågående\",SELECTEDVALUE('Uppdragsregister'[Status])=\"Pågående\",\"Avslutade\",SELECTEDVALUE('Uppdragsregister'[Status])=\"Avslutat\",\"Behöver uppföljning\",[Uppdrag risk]=1,TRUE()),1,0)")
add('Uppdrag detaljtext','VAR _id=SELECTEDVALUE(\'Uppdragsregister\'[UppdragID]) RETURN IF(ISBLANK(_id),"Klicka på ett uppdrag för intäkter, kostnader och ansvarig.",SELECTEDVALUE(\'Uppdragsregister\'[Ansvarig]) & " · Intäkt " & FORMAT([Uppdrag hela intäkt]/1000,"#,##0","sv-SE") & " tkr · Direkt kostnad " & FORMAT([Uppdrag hela kostnad]/1000,"#,##0","sv-SE") & " tkr · Återstående kostnad " & FORMAT(SELECTEDVALUE(\'Uppdragsregister\'[ÅterståendeKostnad])/1000,"#,##0","sv-SE") & " tkr · " & IF(SELECTEDVALUE(\'Uppdragsregister\'[Status])="Avslutat","Faktiskt slututfall","Aktuell slutprognos"))','@')
add('Uppdrag jämförelse', 'FORMAT([Uppdrag utförda]-[Uppdrag utförda föregående],"+#,##0;−#,##0;0","sv-SE") & " mot föregående period"','@')
add('Timmar jämförelse','FORMAT([Utfall timmar]-[Utfall timmar föregående],"+#,##0;−#,##0;0","sv-SE") & " h mot föregående period"','@')
add('Grad jämförelse','"Mål: " & FORMAT([Utfall mål],"0.0 %","sv-SE") & " · " & FORMAT(([Utfall debiteringsgrad]-[Utfall mål])*100,"+0.0;−0.0;0.0","sv-SE") & " pp"','@')
add('Marginal jämförelse','"Kalkyl: " & FORMAT([Utfall kalkylmarginal],"0.0 %","sv-SE") & " · " & FORMAT(([Utfall marginal]-[Utfall kalkylmarginal])*100,"+0.0;−0.0;0.0","sv-SE") & " pp"','@')
add('Plan jämförelse','FORMAT([Plan bokat],"#,##0","sv-SE") & " av " & FORMAT([Plan kapacitet],"#,##0","sv-SE") & " h"','@')
add('Ledigt jämförelse','"Överbeläggning: " & FORMAT([Plan överbeläggning],"#,##0","sv-SE") & " h"','@')
for n in names:
 fields=next(csv.reader((DATA/(n+'.csv')).open(encoding='utf-8-sig')))
 s=f'/// Reproducerbar uppdragsanalys. Separata datumroller för utfall och plan.\ntable {q(n)}\n'
 if n=='Planinställning':
  for name,(expr,fmt) in measures.items():s+=f'\n\tmeasure {q(name)} = ```\n'+''.join('\t\t\t'+line+'\n' for line in expr.splitlines())+f'\t\t\t```\n\t\tformatString: {fmt}\n\t\tdisplayFolder: Uppdrag\n'
 types=[]
 for c in fields:
  typ='int64' if c in integer else 'dateTime' if c in dates else 'double' if c in numeric else 'string';mt='Int64.Type' if c in integer else 'type date' if c in dates else 'type number' if c in numeric else 'type text'
  s+=f'\n\tcolumn {q(c)}\n\t\tdataType: {typ}\n\t\tsummarizeBy: none\n\t\tsourceColumn: {c}\n'
  if c in integer or c in numeric:s+='\t\tisHidden\n'
  if n=='Planveckor' and c=='Vecka':s+='\t\tsortByColumn: VeckaID\n'
  types.append('{"'+c+'", '+mt+'}')
 s+=f'\n\tpartition {q(n)} = m\n\t\tmode: import\n\t\tsource =\n\t\t\tlet\n\t\t\t Source=Csv.Document(File.Contents(DataFolder & "/{n}.csv"),[Delimiter=",",Encoding=65001,QuoteStyle=QuoteStyle.Csv]),\n\t\t\t Headers=Table.PromoteHeaders(Source,[PromoteAllScalars=true]),\n\t\t\t Typed=Table.TransformColumnTypes(Headers,{{'+','.join(types)+'},"en-US")\n\t\t\tin Typed\n'
 (MODEL/'tables'/f'{n}.tmdl').write_text(s,encoding='utf-8')
p=MODEL/'model.tmdl';s=p.read_text(encoding='utf-8-sig')
for n in names:
 if 'ref table '+q(n) not in s:s+='\nref table '+q(n)+'\n'
p.write_text(s,encoding='utf-8')
rels=[('Resurser','Områdesnyckel','Uppdragsområden','Områdesnyckel'),('Uppdragsregister','ResursID','Resurser','ResursID'),('Uppdragsregister','Kundnyckel','Kunder','Kundnyckel'),('Utförd tid','UppdragID','Uppdragsregister','UppdragID'),('Uppdragsekonomi','UppdragID','Uppdragsregister','UppdragID'),('Arbetskapacitet','ResursID','Resurser','ResursID'),('Planbokningar','ResursID','Resurser','ResursID'),('Planbokningar','VeckaID','Planveckor','VeckaID')]
p=MODEL/'relationships.tmdl';s=p.read_text(encoding='utf-8-sig')
for i,(ft,fc,tt,tc) in enumerate(rels):
 name=f'Uppdragsanalys {i}'
 if 'relationship '+q(name) not in s:s+=f'\nrelationship {q(name)}\n\tfromColumn: {q(ft)}.{q(fc)}\n\ttoColumn: {q(tt)}.{q(tc)}\n\tcrossFilteringBehavior: oneDirection\n'
p.write_text(s,encoding='utf-8')
(BASE/'validation/assignment-model-manifest.json').write_text(json.dumps(dict(tables=names,measures=list(measures),relationships=len(rels)),ensure_ascii=False,indent=2),encoding='utf-8')
print('Added',len(names),'tables,',len(measures),'measures,',len(rels),'single-direction relationships.')
