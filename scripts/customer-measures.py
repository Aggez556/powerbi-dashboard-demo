from pathlib import Path
import re,json
root=Path(__file__).resolve().parents[1];p=root/'powerbi-ledningsrapport/Ledningsrapport.SemanticModel/definition/tables/Försäljning.tmdl'
text=p.read_text(encoding='utf-8-sig');measures=[]
def add(n,dax,fmt='General'):measures.append((n,dax,fmt))
add('Kundperiod start','IF([Vald periodtyp]="Helår",[Periodstart],EOMONTH([Periodslut],-12)+1)','yyyy-MM-dd')
add('Kundperiod föregående start','EDATE([Kundperiod start],-12)','yyyy-MM-dd')
add('Kundperiod föregående slut','EOMONTH([Periodslut],-12)','yyyy-MM-dd')
add('Kundperiod text','"Vald period: " & FORMAT([Kundperiod start],"MMM yyyy","sv-SE") & " – " & FORMAT([Periodslut],"MMM yyyy","sv-SE") & "  |  Jämför med: " & FORMAT([Kundperiod föregående start],"MMM yyyy","sv-SE") & " – " & FORMAT([Kundperiod föregående slut],"MMM yyyy","sv-SE") & IF([Vald periodtyp]="Månad"," · Kundanalys avser R12","")')
for suffix,s,e in [('A','Kundperiod start','Periodslut'),('B','Kundperiod föregående start','Kundperiod föregående slut')]:
    for label,base in [('netto','Nettoomsättning bas'),('köp','Kunder bas'),('kostnad','Direkta kostnader bas')]:
        # Avoid constructing cohort status from area or article-level activity.
        add(f'Kund {label} {suffix}',f"VAR s=[{s}] VAR e=[{e}] RETURN CALCULATE([{base}],REMOVEFILTERS('Datum'),REMOVEFILTERS('Områden'),REMOVEFILTERS('Artiklar'),DATESBETWEEN('Datum'[Datum],s,e))",'#,##0.00')
add('Kundstatus kod',"VAR a=[Kund köp A]>0 VAR b=[Kund köp B]>0 VAR firstKey=SELECTEDVALUE('Kunder'[Första köp],0) VAR s=[Kundperiod start] VAR previousStart=[Kundperiod föregående start] VAR startKey=YEAR(s)*10000+MONTH(s)*100+DAY(s) VAR priorKey=YEAR(previousStart)*10000+MONTH(previousStart)*100+DAY(previousStart) RETURN SWITCH(TRUE(),a && b,1,a && firstKey>=startKey,2,a && NOT b && firstKey>0 && firstKey<priorKey,3,NOT a && b,4,0)",'0')
add('Kundstatus text','SWITCH([Kundstatus kod],1,"Befintlig",2,"Ny",3,"Återaktiverad",4,"Förlorad",BLANK())')
for code,label in [(1,'fortsatta'),(2,'helt nya'),(3,'återaktiverade'),(4,'förlorade')]:
    add('Kunder '+label,f"COALESCE(COUNTROWS(FILTER(VALUES('Kunder'[Kundnyckel]),[Kundstatus kod]={code})),0)",'#,##0')
    for suffix in ['A','B']:
        add(f'Kundintäkt {label} {suffix}',f"SUMX(FILTER(VALUES('Kunder'[Kundnyckel]),[Kundstatus kod]={code}),[Kund netto {suffix}])",'#,##0.00')
add('Kunder aktiva','[Kunder fortsatta]+[Kunder helt nya]+[Kunder återaktiverade]','#,##0')
add('Kunder föregående','[Kunder fortsatta]+[Kunder förlorade]','#,##0')
add('Kunder nya','[Kunder helt nya]+[Kunder återaktiverade]','#,##0')
add('Kundintäkt aktuell','[Kund netto A]','#,##0')
add('Kundintäkt föregående','[Kund netto B]','#,##0')
add('Kundintäkt ingående bas A','[Kundintäkt fortsatta A]+[Kundintäkt förlorade A]','#,##0')
add('Kunder logo churn','DIVIDE([Kunder förlorade],[Kunder föregående])','0.0 %')
add('Kunder befintlig tillväxt','IF(ISBLANK([Kunder revenue churn]),BLANK(),-[Kunder revenue churn])')
add('Kunder revenue churn','DIVIDE([Kundintäkt föregående]-[Kundintäkt ingående bas A],[Kundintäkt föregående])','0.0 %;−0.0 %;0.0 %')
add('Kunder retention','DIVIDE([Kundintäkt ingående bas A],[Kundintäkt föregående])','0.0 %')
add('Kunder nyförsäljningsandel','DIVIDE([Kundintäkt helt nya A]+[Kundintäkt återaktiverade A],[Kundintäkt aktuell])','0.0 %')
add('Kunder minskade köp',"SUMX(FILTER(VALUES('Kunder'[Kundnyckel]),[Kundstatus kod]=1 && [Kund netto A]<[Kund netto B]),[Kund netto A]-[Kund netto B])",'#,##0')
add('Kunder ökade köp',"SUMX(FILTER(VALUES('Kunder'[Kundnyckel]),[Kundstatus kod]=1 && [Kund netto A]>=[Kund netto B]),[Kund netto A]-[Kund netto B])",'#,##0')
add('Kunder aktiva undertext','FORMAT([Kunder aktiva]-[Kunder föregående],"+0;−0;0","sv-SE") & " mot föregående period"')
add('Kunder nya undertext','FORMAT([Kunder helt nya],"0","sv-SE") & " nya + " & FORMAT([Kunder återaktiverade],"0","sv-SE") & " återaktiverade"')
add('Kunder förlorade undertext','"Av " & FORMAT([Kunder föregående],"0","sv-SE") & " i föregående kundbas"')
add('Kunder logo undertext','FORMAT([Kunder förlorade],"0","sv-SE") & " förlorade av " & FORMAT([Kunder föregående],"0","sv-SE") & " kunder"')
add('Kunder churn undertext','VAR _d=[Kundintäkt ingående bas A]-[Kundintäkt föregående] RETURN IF(ISBLANK([Kunder revenue churn]),"Ej jämförbart",FORMAT(_d/1000000,"+0.0;−0.0;0.0","sv-SE") & " Mkr mot föregående period")')
add('Kunder andel undertext','FORMAT(([Kundintäkt helt nya A]+[Kundintäkt återaktiverade A])/1000000,"0.0","sv-SE") & " Mkr av " & FORMAT([Kundintäkt aktuell]/1000000,"0.0","sv-SE") & " Mkr"')
add('Kunder churn färg','SWITCH(TRUE(),ISBLANK([Kunder revenue churn]),"#5B6B80",[Kunder revenue churn]>0,"#B42318",[Kunder revenue churn]<0,"#007956","#5B6B80")')
add('Kundgrupp månadsintäkt',"VAR _month=SELECTEDVALUE('Trendaxel'[Månadsstart]) VAR _groupCode=SELECTEDVALUE('Kundgrupper'[Ordning])+1 VAR _start=[Kundperiod start] VAR _end=[Periodslut] VAR _cohortCustomers=FILTER(VALUES('Kunder'[Kundnyckel]),[Kundstatus kod]=_groupCode) RETURN IF(_month>=_start && _month<=_end,CONVERT(SUMX(_cohortCustomers,CALCULATE([Nettoomsättning bas],REMOVEFILTERS('Datum'),DATESBETWEEN('Datum'[Datum],_month,EOMONTH(_month,0)))),DOUBLE)/1000000)",'0.0')
add('Kundgrupp andel',"DIVIDE([Kundgrupp månadsintäkt],SUMX(ALL('Kundgrupper'),[Kundgrupp månadsintäkt]))",'0.0 %')
add('Kundgrupp summering','"Befintliga " & FORMAT([Kundintäkt fortsatta A]/1000000,"0.0","sv-SE") & " · Helt nya " & FORMAT([Kundintäkt helt nya A]/1000000,"0.0","sv-SE") & " · Återaktiverade " & FORMAT([Kundintäkt återaktiverade A]/1000000,"0.0","sv-SE") & " Mkr"')
add('Kundbas bryggsteg',"SWITCH(SELECTEDVALUE('Kundbassteg'[Ordning]),0,[Kunder föregående],1,[Kunder helt nya],2,[Kunder återaktiverade],3,-[Kunder förlorade])",'0')
add('Kundintäkt bryggsteg',"SWITCH(SELECTEDVALUE('Kundintäktssteg'[Ordning]),0,[Kundintäkt föregående],1,[Kundintäkt förlorade A]-[Kundintäkt förlorade B],2,[Kunder minskade köp],3,[Kunder ökade köp],4,[Kundintäkt helt nya A],5,[Kundintäkt återaktiverade A])/1000000",'0.0')
add('Kundbas bryggtak','MAX([Kunder aktiva]+[Kunder förlorade],[Kunder föregående])*1.2','0')
add('Kundintäkt bryggtak','MAX([Kundintäkt föregående],[Kundintäkt aktuell])/1000000*1.2','0.0')
add('Kundbas ekvation','FORMAT([Kunder föregående],"0") & " + " & FORMAT([Kunder helt nya],"0") & " + " & FORMAT([Kunder återaktiverade],"0") & " − " & FORMAT([Kunder förlorade],"0") & " = " & FORMAT([Kunder aktiva],"0")')
add('Kundintäkt ekvation','"Befintliga kunder: " & FORMAT(([Kundintäkt ingående bas A]-[Kundintäkt föregående])/1000000,"+0.0;−0.0;0.0","sv-SE") & " Mkr · Förändring " & IF(ISBLANK([Kunder befintlig tillväxt]),"Ej jämförbart",FORMAT([Kunder befintlig tillväxt],"+0.0 %;−0.0 %;0.0 %","sv-SE"))')
add('Kund omsättning Mkr','IF([Kundstatus kod]>0,COALESCE([Kund netto A],0)/1000000)','0.0 "Mkr"')
add('Kund förändring kr','IF([Kundstatus kod]>0,[Kund netto A]-[Kund netto B])','#,##0')
add('Kund förändring procent','IF([Kundstatus kod]>0,DIVIDE([Kund netto A]-[Kund netto B],[Kund netto B]))','+0.0 %;−0.0 %;0.0 %')
add('Kund bruttovinst','IF([Kund köp A]>0,[Kund netto A]-[Kund kostnad A])','#,##0')
add('Kund marginal','DIVIDE([Kund bruttovinst],[Kund netto A])','0.0 %')
add('Kund senaste köp',"VAR e=[Periodslut] RETURN IF([Kundstatus kod]>0,CALCULATE(MAX('Försäljning'[Datumnyckel]),REMOVEFILTERS('Datum'),'Försäljning'[Nettointäkt]>0,'Försäljning'[Datumnyckel]<=YEAR(e)*10000+MONTH(e)*100+DAY(e)))",'0')
add('Kund senaste köp text','VAR k=[Kund senaste köp] RETURN IF(NOT ISBLANK(k),FORMAT(DATE(INT(k/10000),INT(MOD(k,10000)/100),MOD(k,100)),"yyyy-MM-dd"))')
add('Kund köpta områden',"VAR s=[Kundperiod start] VAR e=[Periodslut] RETURN IF([Kundstatus kod]>0,CONCATENATEX(FILTER(ALL('Områden'),CALCULATE([Kunder bas],REMOVEFILTERS('Datum'),DATESBETWEEN('Datum'[Datum],s,e))>0),'Områden'[Område],\", \"))")
add('Kund prioritet','ABS([Kund netto A]-[Kund netto B])+ABS([Kund netto A])','#,##0')
add('Kund tabell synlig',"VAR _selectedStatus=SELECTEDVALUE('Kundstatusval'[Ordning],0) VAR _customerStatus=[Kundstatus kod] RETURN IF(_customerStatus>0 && (_selectedStatus=0 || _customerStatus=_selectedStatus),1,0)",'0')
add('Kund radfärg','SWITCH([Kundstatus kod],2,"#007956",3,"#4A6BCE",4,"#B42318","#0F3163")')
add('Kund detaljrad 1',"IF(HASONEVALUE('Kunder'[Kundnyckel]),SELECTEDVALUE('Kunder'[Kundbransch]) & \" · Områden: \" & IF([Kundstatus kod]=4,\"Inga köp i aktuell period\",[Kund köpta områden]),\"Skrolla för fler kunder · välj status eller klicka på en kundrad för detaljer.\")")
add('Kund detaljrad 2','IF(HASONEVALUE(\'Kunder\'[Kundnyckel]),"Förändring " & FORMAT([Kund förändring kr],"+0;−0;0","sv-SE") & " kr · Bruttovinst " & FORMAT([Kund bruttovinst]/1000000,"0.00","sv-SE") & " Mkr", "Statusfiltret styr endast kundtabellen. Churn avser hela vald bransch och period.")')
for name,dax,fmt in measures:
    pat=r"(?m)^\tmeasure '?"+re.escape(name)+r"'? = .*?(?=\n\t(?:///|measure |column |partition )|\Z)"
    block=f"\tmeasure '{name}' = {dax}\n\t\tformatString: {fmt}\n\t\tdisplayFolder: Kundanalys\n"
    if re.search(r"(?m)^\tmeasure '?"+re.escape(name)+r"'? =",text):
        def replace_existing(match):
            retained=re.findall(r'(?m)^\t\t(?:lineageTag: .*|isHidden)\s*$',match.group(0))
            return block+''.join(line.rstrip()+'\n' for line in retained)
        text=re.sub(pat,replace_existing,text,flags=re.S)
    else:
        i=text.index('\n\tcolumn ');text=text[:i]+'\n'+block+text[i:]
p.write_text(text,encoding='utf-8')
(root/'powerbi-ledningsrapport/validation/customer-measure-names.json').write_text(json.dumps([n for n,_,_ in measures],ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Added {len(measures)} customer measures.')
