from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
dax='VAR mode=[Vald periodtyp] VAR currentLabel=SWITCH(mode,"Helår",FORMAT([Periodslut],"yyyy"),"Månad",FORMAT([Periodslut],"MMMM yyyy","sv-SE"),FORMAT([Periodstart],"MMM yyyy","sv-SE") & " – " & FORMAT([Periodslut],"MMM yyyy","sv-SE")) VAR previousLabel=SWITCH(mode,"Helår",FORMAT([Jämförelseslut],"yyyy"),"Månad",FORMAT([Jämförelseslut],"MMMM yyyy","sv-SE"),FORMAT([Jämförelsestart],"MMM yyyy","sv-SE") & " – " & FORMAT([Jämförelseslut],"MMM yyyy","sv-SE")) RETURN "Vald period: " & currentLabel & "    |    Jämför med: " & previousLabel'
p=root/'powerbi-ledningsrapport/Ledningsrapport.SemanticModel/definition/tables/Försäljning.tmdl'
s=p.read_text(encoding='utf-8-sig');s,n=re.subn(r"(?m)^(\tmeasure '?Periodtext'? = ).*$",lambda m:m[1]+dax,s);assert n==1;p.write_text(s,encoding='utf-8')
p=root/'scripts/generate-ledningsrapport.py';s=p.read_text(encoding='utf-8');s,n=re.subn(r"(?m)^add\('Periodtext',.*$",lambda m:"add('Periodtext',"+repr(dax)+",'General','Period')",s);assert n==1;p.write_text(s,encoding='utf-8')
print('Period text now uses month ranges, year numbers or a single month.')
