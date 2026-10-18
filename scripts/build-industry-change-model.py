"""Monthly YoY industry comparisons. No fact data, relationships or partitions change."""
from pathlib import Path
import re,json
root=Path(__file__).resolve().parents[1]/'powerbi-ledningsrapport'
file=root/'Ledningsrapport.SemanticModel/definition/tables/Kunder.tmdl'
text=file.read_text(encoding='utf-8-sig')
measures={}
def add(name,dax,fmt):measures[name]=(dax,fmt)
gate="VAR _m=SELECTEDVALUE('Trendaxel'[Månadsstart]) VAR _start=[Periodstart] VAR _end=MIN([Periodslut],[Senaste utfall]) "
add('Bransch månadsförsäljning',gate+"RETURN IF(NOT ISBLANK(_m) && _m>=_start && _m<=_end,CALCULATE([Nettoomsättning bas],REMOVEFILTERS('Datum'),DATESBETWEEN('Datum'[Datum],_m,EOMONTH(_m,0))))",'#,##0 "kr"')
add('Bransch månadsförsäljning föregående år',gate+"VAR _previous=EDATE(_m,-12) RETURN IF(NOT ISBLANK(_m) && _m>=_start && _m<=_end,CALCULATE([Nettoomsättning bas],REMOVEFILTERS('Datum'),DATESBETWEEN('Datum'[Datum],_previous,EOMONTH(_previous,0))))",'#,##0 "kr"')
add('Bransch månadsförändring kronor',"VAR _a=[Bransch månadsförsäljning] VAR _b=[Bransch månadsförsäljning föregående år] RETURN IF(ISBLANK(_a)&&ISBLANK(_b),BLANK(),COALESCE(_a,0)-COALESCE(_b,0))",'+#,##0 "kr";−#,##0 "kr";0 "kr"')
add('Bransch månadsförändring procent',"VAR _b=[Bransch månadsförsäljning föregående år] RETURN IF(_b>0,DIVIDE([Bransch månadsförändring kronor],_b))",'+0.0 %;−0.0 %;0.0 %')
add('Bransch månadsförändring Mkr','VAR _v=[Bransch månadsförändring kronor] RETURN IF(ISBLANK(_v),BLANK(),CONVERT(_v,DOUBLE)/1000000)','+0.00 "Mkr";−0.00 "Mkr";0.00 "Mkr"')
scope="VAR _start=[Periodstart] VAR _end=MIN([Periodslut],[Senaste utfall]) VAR _months=FILTER(ALLSELECTED('Trendaxel'[Månadsstart]),'Trendaxel'[Månadsstart]>=_start && 'Trendaxel'[Månadsstart]<=_end) VAR _branches=ALLSELECTED('Kunder'[Kundbransch]) "
for unit,measure in [('procent','Bransch månadsförändring procent'),('Mkr','Bransch månadsförändring Mkr')]:
 step='0.05' if unit=='procent' else '0.1'
 values=f"VAR _values=ADDCOLUMNS(CROSSJOIN(_months,_branches),\"@value\",CALCULATE([{measure}])) "
 add('Bransch axeltak '+unit,scope+values+f"VAR _maximum=MAX(0,MAXX(_values,[@value])) VAR _minimum=MIN(0,MINX(_values,[@value])) VAR _padding=MAX({step},(_maximum-_minimum)*0.08) RETURN CEILING(_maximum+_padding,{step})",'0.00')
 add('Bransch axelgolv '+unit,scope+values+f"VAR _maximum=MAX(0,MAXX(_values,[@value])) VAR _minimum=MIN(0,MINX(_values,[@value])) VAR _padding=MAX({step},(_maximum-_minimum)*0.08) RETURN -CEILING(-_minimum+_padding,{step})",'0.00')
for name,(dax,fmt) in measures.items():
 pattern=r"\n\tmeasure '"+re.escape(name)+r"' =.*?(?=\n\t(?:measure |column |partition |///)|\Z)"
 text=re.sub(pattern,'',text,flags=re.S)
 block=f"\n\tmeasure '{name}' = {dax}\n\t\tformatString: {fmt}\n\t\tdisplayFolder: Kunder\\Branschutveckling\n"
 pos=text.index('\n\tcolumn ');text=text[:pos]+block+text[pos:]
file.write_text(text,encoding='utf-8')
(root/'validation/industry-change-measures.json').write_text(json.dumps(list(measures),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Created {len(measures)} measures; existing fact data and partition types are preserved.')
