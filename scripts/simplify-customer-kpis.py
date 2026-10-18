"""Plain Swedish KPI labels and a growth-oriented display, preserving canonical churn."""
from pathlib import Path
import re,json
root=Path(__file__).resolve().parents[1]
model=root/'powerbi-ledningsrapport/Ledningsrapport.SemanticModel/definition/tables/Försäljning.tmdl'
text=model.read_text(encoding='utf-8-sig')
name='Kunder befintlig tillväxt'
if f"measure '{name}'" not in text:
 pos=text.index('\n\tcolumn ')
 text=text[:pos]+f"\n\tmeasure '{name}' = -[Kunder revenue churn]\n\t\tformatString: +0.0 %;−0.0 %;0.0 %\n\t\tdisplayFolder: Kunder\n"+text[pos:]
definitions={
 'Kunder befintlig tillväxt':'IF(ISBLANK([Kunder revenue churn]),BLANK(),-[Kunder revenue churn])',
 'Kunder churn undertext':'VAR _d=[Kundintäkt ingående bas A]-[Kundintäkt föregående] RETURN IF(ISBLANK([Kunder revenue churn]),"Ej jämförbart",FORMAT(_d/1000000,"+0.0;−0.0;0.0","sv-SE") & " Mkr mot föregående period")',
 'Kundintäkt ekvation':'"Befintliga kunder: " & FORMAT(([Kundintäkt ingående bas A]-[Kundintäkt föregående])/1000000,"+0.0;−0.0;0.0","sv-SE") & " Mkr · Förändring " & IF(ISBLANK([Kunder befintlig tillväxt]),"Ej jämförbart",FORMAT([Kunder befintlig tillväxt],"+0.0 %;−0.0 %;0.0 %","sv-SE"))'
}
for key,dax in definitions.items():
 text,n=re.subn(r"(\tmeasure '"+re.escape(key)+r"' =).*?(?=\n\t\tformatString)",lambda m:m[1]+' '+dax,text,count=1,flags=re.S);assert n==1
model.write_text(text,encoding='utf-8')
footer_old='Negativ nettochurn betyder tillväxt i befintlig kundstock.'
footer_new='Försäljningsförändringen avser föregående periods kundbas, inklusive förlorade kunder.'
page=root/'powerbi-ledningsrapport/LedningsrapportUtanScroll.Report/definition/pages/f429b020315c602ce0ed/visuals'
for file in page.glob('*/visual.json'):
 original=file.read_text(encoding='utf-8-sig');v=json.loads(original)
 for para in v['visual'].get('objects',{}).get('general',[{}])[0].get('properties',{}).get('paragraphs',[]):
  for run in para.get('textRuns',[]):
   run['value']=run['value'].replace('Logo churn','Andel förlorade kunder').replace('Revenue churn netto','Försäljning till\nbefintliga kunder').replace(footer_old,footer_new)
 if 'Kunder revenue churn' in original:
  def walk(o):
   if not isinstance(o,dict):return
   for k,value in o.items():
    if isinstance(value,str):o[k]=value.replace('Kunder revenue churn',name)
    elif isinstance(value,dict):walk(value)
    elif isinstance(value,list):
     for entry in value:walk(entry)
  walk(v)
 content=json.dumps(v,ensure_ascii=False,indent=2)+'\n'
 if json.loads(original)!=v:file.write_text(content,encoding='utf-8')
# Keep the authoring sources in sync without rebuilding the established page.
p=root/'scripts/build-customer-page.cjs';s=p.read_text(encoding='utf-8')
s=s.replace("['Logo churn'","['Andel förlorade kunder'").replace("['Revenue churn netto','Kunder revenue churn'","['Försäljning till\\nbefintliga kunder','Kunder befintlig tillväxt'").replace(footer_old,footer_new)
p.write_text(s,encoding='utf-8')
p=root/'scripts/customer-measures.py';s=p.read_text(encoding='utf-8')
if "add('Kunder befintlig tillväxt'" not in s:s=s.replace("add('Kunder revenue churn'","add('Kunder befintlig tillväxt','-[Kunder revenue churn]','+0.0 %;−0.0 %;0.0 %')\nadd('Kunder revenue churn'",1)
for key,dax in definitions.items():s=re.sub(r"^add\('"+re.escape(key)+r"'.*$",lambda m:"add('"+key+"',"+repr(dax)+")",s,flags=re.M)
p.write_text(s,encoding='utf-8')
print('Renamed customer KPIs and added a conventional signed growth display; canonical churn remains unchanged.')
