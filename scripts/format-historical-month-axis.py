from pathlib import Path
import re
p=Path(__file__).resolve().parents[1]/'powerbi-ledningsrapport/Ledningsrapport.SemanticModel/definition/tables/Trendaxel.tmdl'
s=p.read_text(encoding='utf-8-sig')
pattern=r"(\tcolumn '?Månadsstart'?\n)(.*?)(?=\n\t(?:column|partition|hierarchy)|\Z)"
def update(m):
 body=re.sub(r'^\t\tformatString: [^\n]*\n?','',m.group(2),flags=re.M)
 return m.group(1)+'\t\tformatString: MMM\n'+body
s,count=re.subn(pattern,update,s,flags=re.S)
assert count==1
s=re.sub(r'(\t///[^\n]+\n)\n+(?=\tcolumn )',r'\1',s)
p.write_text(s,encoding='utf-8')
