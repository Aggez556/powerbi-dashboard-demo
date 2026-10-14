from pathlib import Path
import re,json
root=Path(__file__).resolve().parents[1];model=root/'powerbi-ledningsrapport/Ledningsrapport.SemanticModel/definition';p=model/'tables/Försäljning.tmdl';text=p.read_text(encoding='utf-8-sig')
measures=[]
def add(n,dax,fmt='General'):measures.append((n,dax,fmt))
add('Sälj områdesval',"SELECTEDVALUE('Områdesval'[Områdesval],0)",'0')
for n,base in [('Sälj omsättning','Nettoomsättning'),('Sälj omsättning föregående år','Nettoomsättning föregående år'),('Sälj bruttovinst','Bruttovinst'),('Sälj bruttovinst föregående år','Bruttovinst föregående år'),('Sälj kunder','Aktiva kunder'),('Sälj kunder föregående år','Aktiva kunder föregående år')]:
    add(n,f"VAR a=[Sälj områdesval] RETURN IF(a=0,[{base}],CALCULATE([{base}],KEEPFILTERS(TREATAS({{a}},'Områden'[Områdesnyckel]))))",'#,##0')
for n,base in [('Sälj omsättning Mkr','Sälj omsättning'),('Sälj omsättning föregående år Mkr','Sälj omsättning föregående år'),('Sälj bruttovinst Mkr','Sälj bruttovinst'),('Sälj bruttovinst föregående år Mkr','Sälj bruttovinst föregående år')]:add(n,f'[{base}]/1000000','0.0 "Mkr"' if 'omsättning' in n else '0.00 "Mkr"')
add('Sälj tillväxt','DIVIDE([Sälj omsättning]-[Sälj omsättning föregående år],[Sälj omsättning föregående år])','+0.0 %;−0.0 %;0.0 %')
add('Sälj bruttomarginal','DIVIDE([Sälj bruttovinst],[Sälj omsättning])','0.0 %')
add('Sälj marginal föregående år','DIVIDE([Sälj bruttovinst föregående år],[Sälj omsättning föregående år])','0.0 %')
add('Sälj marginal procent','[Sälj bruttomarginal]*100','0.0')
add('Sälj omsättning per kund','DIVIDE([Sälj omsättning],[Sälj kunder])','0.0')
add('Sälj omsättning per kund föregående år','DIVIDE([Sälj omsättning föregående år],[Sälj kunder föregående år])','0.0')
add('Produktorder bas',"CALCULATE(DISTINCTCOUNT('Försäljning'[Ordernyckel]),'Försäljning'[Områdesnyckel]=1,'Försäljning'[Nettointäkt]>0)",'#,##0')
add('Orderintäkt bas',"VAR orders=CALCULATETABLE(VALUES('Försäljning'[Ordernyckel]),'Försäljning'[Områdesnyckel]=1,'Försäljning'[Nettointäkt]>0) RETURN CALCULATE(SUM('Försäljning'[Nettointäkt]),KEEPFILTERS(TREATAS(orders,'Försäljning'[Ordernyckel])),'Försäljning'[Områdesnyckel]=1)",'#,##0')
add('Debiterade timmar bas',"CALCULATE(SUM('Försäljning'[Debiterade timmar]),'Försäljning'[Debitering]=\"Timdebiterat\")",'#,##0.0')
add('Timintäkt bas',"CALCULATE(SUM('Försäljning'[Nettointäkt]),'Försäljning'[Debitering]=\"Timdebiterat\")",'#,##0.00')
for n,base in [('Sälj produktorder','Produktorder bas'),('Sälj orderintäkt','Orderintäkt bas'),('Sälj debiterade timmar','Debiterade timmar bas'),('Sälj timintäkt','Timintäkt bas')]:
    for suffix,s,e in [('', 'Periodstart','Periodslut'),(' föregående år','Jämförelsestart','Jämförelseslut')]:
        add(n+suffix,f"VAR s=[{s}] VAR e=[{e}] VAR a=[Sälj områdesval] RETURN IF(a=0,CALCULATE([{base}],REMOVEFILTERS('Datum'),DATESBETWEEN('Datum'[Datum],s,e)),CALCULATE([{base}],REMOVEFILTERS('Datum'),DATESBETWEEN('Datum'[Datum],s,e),KEEPFILTERS(TREATAS({{a}},'Områden'[Områdesnyckel]))))",'#,##0.00')
for suffix in ['', ' föregående år']:
    add('Sälj ordervärde'+suffix,f'DIVIDE([Sälj orderintäkt{suffix}],[Sälj produktorder{suffix}])','#,##0.00')
    add('Sälj timpris'+suffix,f'DIVIDE([Sälj timintäkt{suffix}],[Sälj debiterade timmar{suffix}])','#,##0.00')
add('Sälj kort 5 rubrik','SWITCH([Sälj områdesval],1,"Antal försäljningsorder",2,"Debiterade servicetimmar",3,"Debiterade bemanningstimmar","Köpande kunder")')
add('Sälj kort 6 rubrik','SWITCH([Sälj områdesval],1,"Genomsnittligt ordervärde",2,"Genomsnittligt timpris",3,"Genomsnittligt timpris","Omsättning per kund")')
add('Sälj kort 5 tal','SWITCH([Sälj områdesval],1,[Sälj produktorder],2,[Sälj debiterade timmar],3,[Sälj debiterade timmar],[Sälj kunder])','#,##0')
add('Sälj kort 5 föregående år','SWITCH([Sälj områdesval],1,[Sälj produktorder föregående år],2,[Sälj debiterade timmar föregående år],3,[Sälj debiterade timmar föregående år],[Sälj kunder föregående år])','#,##0')
add('Sälj kort 6 tal','SWITCH([Sälj områdesval],1,[Sälj ordervärde],2,[Sälj timpris],3,[Sälj timpris],[Sälj omsättning per kund])','#,##0.00')
add('Sälj kort 6 föregående år','SWITCH([Sälj områdesval],1,[Sälj ordervärde föregående år],2,[Sälj timpris föregående år],3,[Sälj timpris föregående år],[Sälj omsättning per kund föregående år])','#,##0.00')
add('Sälj kort 5 värde','IF(ISBLANK([Sälj kort 5 tal]),"—",FORMAT([Sälj kort 5 tal],"# ##0","sv-SE"))')
add('Sälj kort 6 värde','VAR v=[Sälj kort 6 tal] RETURN IF(ISBLANK(v),"—",IF([Sälj områdesval]<2,FORMAT(v/1000,"0.0","sv-SE") & " tkr",FORMAT(v,"# ##0.0","sv-SE") & " kr"))')
add('Sälj netto undertext','"Föregående år: " & FORMAT([Sälj omsättning föregående år]/1000000,"0.0","sv-SE") & " Mkr"')
add('Sälj tillväxt undertext','FORMAT(([Sälj omsättning]-[Sälj omsättning föregående år])/1000000,"+0.0;−0.0;0.0","sv-SE") & " Mkr mot föregående år"')
add('Sälj brutto undertext','"Föregående år: " & FORMAT([Sälj bruttovinst föregående år]/1000000,"0.00","sv-SE") & " Mkr"')
add('Sälj marginal undertext','FORMAT(([Sälj bruttomarginal]-[Sälj marginal föregående år])*100,"+0.0;−0.0;0.0","sv-SE") & " procentenheter"')
add('Sälj kort 5 undertext','IF([Sälj områdesval]=0,FORMAT([Sälj kort 5 tal]-[Sälj kort 5 föregående år],"+0;−0;0","sv-SE") & " kunder mot föregående år","Föregående år: " & FORMAT([Sälj kort 5 föregående år],"# ##0","sv-SE"))')
add('Sälj kort 6 undertext','VAR v=[Sälj kort 6 föregående år] RETURN IF(ISBLANK(v),"—","Föregående år: " & IF([Sälj områdesval]<2,FORMAT(v/1000,"0.0","sv-SE") & " tkr",FORMAT(v,"# ##0.0","sv-SE") & " kr"))')
add('Sälj tillväxt färg','IF([Sälj tillväxt]<0,"#B42318","#007956")')
add('Sälj marginal färg','IF([Sälj bruttomarginal]<[Sälj marginal föregående år],"#B42318","#007956")')
add('Sälj trend rubrik','IF([Vald periodtyp]="Månad","Försäljning över tid · historisk kontext","Försäljning över tid")')
add('Sälj trend bas',"VAR m=SELECTEDVALUE('Trendaxel'[Månadsstart]) RETURN IF(m>=[Trendstart] && m<=[Periodslut],CALCULATE([Nettoomsättning bas],REMOVEFILTERS('Datum'),DATESBETWEEN('Datum'[Datum],m,EOMONTH(m,0))))",'#,##0')
add('Sälj trend',"VAR a=[Sälj områdesval] VAR typ=SELECTEDVALUE('Försäljningsserie'[Typ]) VAR k=SELECTEDVALUE('Försäljningsserie'[Nyckel]) RETURN SWITCH(TRUE(),a=0 && typ=\"Område\",CALCULATE([Sälj trend bas],KEEPFILTERS(TREATAS({k},'Områden'[Områdesnyckel])))/1000000,a>0 && typ=\"Kategori\",CALCULATE([Sälj trend bas],KEEPFILTERS(TREATAS({a},'Områden'[Områdesnyckel])),KEEPFILTERS(TREATAS({k},'Artiklar'[Kategoriordning])))/1000000)",'0.0')
add('Sälj trend föregående år',"VAR m=SELECTEDVALUE('Trendaxel'[Månadsstart]) VAR a=[Sälj områdesval] VAR typ=SELECTEDVALUE('Försäljningsserie'[Typ]) VAR k=SELECTEDVALUE('Försäljningsserie'[Nyckel]) RETURN IF(NOT ISBLANK([Sälj trend]),IF(a=0,CALCULATE([Nettoomsättning bas],REMOVEFILTERS('Datum'),DATESBETWEEN('Datum'[Datum],EDATE(m,-12),EOMONTH(m,-12)),TREATAS({k},'Områden'[Områdesnyckel])),CALCULATE([Nettoomsättning bas],REMOVEFILTERS('Datum'),DATESBETWEEN('Datum'[Datum],EDATE(m,-12),EOMONTH(m,-12)),TREATAS({a},'Områden'[Områdesnyckel]),TREATAS({k},'Artiklar'[Kategoriordning])))/1000000)",'0.0')
add('Sälj trend vald månad',"IF([Vald periodtyp]=\"Månad\" && EOMONTH(SELECTEDVALUE('Trendaxel'[Månadsstart]),0)=[Periodslut],\"Vald månad\",\"\")")
add('Sälj trend färg',"VAR typ=SELECTEDVALUE('Försäljningsserie'[Typ]) VAR k=SELECTEDVALUE('Försäljningsserie'[Nyckel]) RETURN IF([Vald periodtyp]=\"Månad\" && EOMONTH(SELECTEDVALUE('Trendaxel'[Månadsstart]),0)=[Periodslut],\"#9B570B\",IF(typ=\"Område\",SWITCH(k,1,\"#0F3163\",2,\"#007956\",3,\"#4A6BCE\"),SWITCH(MOD(k-1,3),0,\"#0F3163\",1,\"#007956\",2,\"#4A6BCE\")))")
for n,dax,fmt in measures:
    pattern=r"(?m)^\tmeasure '?"+re.escape(n)+r"'? = .*?(?=\n\t(?:///|measure |column |partition )|\Z)"
    block=f"\t/// Försäljningsöversikt: beräknas från gemensamt underlag och aktuellt områdes-/periodval.\n\tmeasure '{n}' = {dax}\n\t\tformatString: {fmt}\n\t\tdisplayFolder: Försäljningsöversikt\n"
    # Generated measures are replaceable; other model metadata is retained.
    if re.search(r"(?m)^\tmeasure '?"+re.escape(n)+r"'? =",text):
        def replace_existing(match):
            retained=re.findall(r'(?m)^\t\t(?:lineageTag: .*|isHidden)\s*$',match.group(0))
            return block.split('\n',1)[1]+''.join(line.rstrip()+'\n' for line in retained)
        text=re.sub(pattern,replace_existing,text,flags=re.S)
    else:
        index=text.index('\n\tcolumn ');text=text[:index]+'\n'+block+text[index:]
p.write_text(text,encoding='utf-8')
(root/'powerbi-ledningsrapport/validation/sales-measure-names.json').write_text(json.dumps([n for n,_,_ in measures],ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Added {len(measures)} sales measures, sharing period and accounting definitions with the overview.')
