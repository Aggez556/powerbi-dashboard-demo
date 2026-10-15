"""Targeted, lineage-preserving fixes for missing forecasts and status order."""
from pathlib import Path
import re,csv
BASE=Path(__file__).resolve().parents[1]/'powerbi-ledningsrapport'
TABLES=BASE/'Ledningsrapport.SemanticModel/definition/tables'
risk='''VAR _forecast=[Uppdrag prognos]
VAR _estimate=[Uppdrag kalkyl]
VAR _hours=[Uppdrag hela timmar]
VAR _planned=[Uppdrag planerade]
RETURN IF(SELECTEDVALUE('Uppdragsregister'[Status])="Pågående" &&
((NOT ISBLANK(_hours) && NOT ISBLANK(_planned) && _hours>_planned) ||
(NOT ISBLANK(_forecast) && NOT ISBLANK(_estimate) && _forecast<=_estimate-.02+0.0000001)),1,0)'''
colour='VAR _forecast=[Uppdrag prognos] RETURN IF(ISBLANK(_forecast),"#5B6B80",IF(_forecast<=[Uppdrag kalkyl]-.02+0.0000001,"#B42318",IF(_forecast>[Uppdrag kalkyl],"#007956","#0F3163")))'
p=TABLES/'Planinställning.tmdl';s=p.read_text(encoding='utf-8-sig')
for name,expr in [('Uppdrag risk',risk),('Uppdrag marginalfärg',colour),('Uppdrag trendrubrik','"Debiteringsgrad över tid"')]:
 pattern=r"\tmeasure '"+name+r"' =\s*.*?(?=\n\t\tformatString:)"
 replacement="\tmeasure '"+name+"' = ```\n"+''.join('\t\t\t'+line+'\n' for line in expr.splitlines())+'\t\t\t```'
 s,count=re.subn(pattern,lambda _:replacement,s,flags=re.S);assert count==1
p.write_text(s,encoding='utf-8')
p=TABLES/'Planinställning.tmdl';s=p.read_text(encoding='utf-8-sig')
for name in ['Utfall timmar','Plan ledigt']:
 s,count=re.subn(r"(\tmeasure '"+name+r"' =\s*.*?\n\t\tformatString: )[^\n]+",lambda m:m.group(1)+'#,##0" h"',s,flags=re.S);assert count==1
p.write_text(s,encoding='utf-8')
p=TABLES/'Planinställning.tmdl';s=p.read_text(encoding='utf-8-sig')
if "measure 'Uppdrag prognostext'" not in s:
 s=s.replace('\n\tcolumn ', '\n\tmeasure \'Uppdrag prognostext\' = IF(HASONEVALUE(\'Uppdragsregister\'[UppdragID]),IF(ISBLANK([Uppdrag prognos]),"—",FORMAT([Uppdrag prognos],"0.0 %","sv-SE")))\n\t\tformatString: @\n\t\tdisplayFolder: Uppdrag\n\n\tcolumn ',1)
p.write_text(s,encoding='utf-8')
p=TABLES/'Uppdragsstatusval.tmdl';s=p.read_text(encoding='utf-8-sig')
if 'sortByColumn: Visningsordning' not in s:s=s.replace('\t\tsourceColumn: Urval','\t\tsourceColumn: Urval\n\t\tsortByColumn: Visningsordning')
if re.search(r'\tcolumn Visningsordning\s*=',s):s=re.sub(r'\tcolumn Visningsordning.*?(?=\n\tpartition)', '',s,flags=re.S)
if '\tcolumn Visningsordning' not in s:s=s.replace('\tpartition Uppdragsstatusval','\tcolumn Visningsordning\n\t\tdataType: int64\n\t\tisHidden\n\t\tsummarizeBy: none\n\t\tsourceColumn: Visningsordning\n\n\tpartition Uppdragsstatusval')
s=s.replace('{{"Urval", type text}}','{{"Urval", type text},{"Visningsordning", Int64.Type}}')
p.write_text(s,encoding='utf-8')
with (BASE/'data/Uppdragsstatusval.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['Urval','Visningsordning']);w.writerows((label,i) for i,label in enumerate(['Alla','Pågående','Avslutade','Behöver uppföljning']))
print('Preserved lineage; missing forecasts no longer imply poor margin; status order explicit.')
import runpy
runpy.run_path(str(Path(__file__).with_name('dynamic-assignment-axis.py')))
