"""Apply Swedish copy and consistent spacing to the reproducible report builder."""
from pathlib import Path
p = Path(__file__).with_name('build-sales-finance.cjs')
s = p.read_text(encoding='utf-8')
s = s.replace("const pages=['Hem','Executive Overview','Finance & Profitability','Sales Analytics','Transactions'],ids=pages.map(x=>id('sales-finance:'+x));", "const pageKeys=['Hem','Executive Overview','Finance & Profitability','Sales Analytics','Transactions'];\nconst pages=['Hem','Ledningsöversikt','Ekonomi och lönsamhet','Försäljningsanalys','Transaktioner'],ids=pageKeys.map(x=>id('sales-finance:'+x));")
s = s.replace("const labels=['Executive Overview','Finance & Profitability','Sales Analytics','Transactions']", "const labels=pages.slice(1)")
for a,b in [('BUSINESS INTELLIGENCE','VERKSAMHETSANALYS'),('SALES & FINANCE DASHBOARD','FÖRSÄLJNING OCH EKONOMI'),('Sales & Finance Dashboard','Försäljning och ekonomi'),('SALES & FINANCE','FÖRSÄLJNING OCH EKONOMI'),('Executive Overview är den första färdiga analyssidan.','Ledningsöversikt är den första färdiga analyssidan.')]:
    s = s.replace(a,b)
s = s.replace("top:lit(4),bottom:lit(4),left:lit(8),right:lit(8)", "top:lit(0),bottom:lit(0),left:lit(0),right:lit(0)")
s = s.replace("v.howCreated='InsertVisualButton';", "v.visual.visualContainerObjects.padding=[{properties:{top:lit(0),bottom:lit(0),left:lit(0),right:lit(0)}}];v.howCreated='InsertVisualButton';")
s = s.replace("horizontalAlignment:lit('center'),leftMargin", "horizontalAlignment:lit('center'),topMargin:lit(0),bottomMargin:lit(0),leftMargin")
s = s.replace("text('suite','VERKSAMHETSANALYS',[312,60,640,44]", "text('suite','VERKSAMHETSANALYS',[312,68,640,36]")
s = s.replace("text('status','●  Lokal rapportsvit',[1640,48,216,44],10,'#4A6BCE','#FFFFFF');", "text('status-panel','',[1640,48,216,44],10,'#4A6BCE','#FFFFFF');text('status','●  Lokal rapportsvit',[1656,60,184,28],10,'#4A6BCE');")
s = s.replace("text('scope','4 rapportområden                    360°\\nEn sammanhängande bild av verksamheten',[1304,200,552,108],16,'#0F3163','#FFFFFF',true);", "text('scope-panel','',[1304,200,552,108],16,'#0F3163','#FFFFFF');text('scope-areas','4 rapportområden',[1328,218,280,32],16,'#0F3163',null,true);text('scope-view','360°',[1640,218,192,32],16,'#0F3163',null,true);text('scope-description','En sammanhängande bild av verksamheten',[1328,260,504,32],12,'#5B6B80');")
s = s.replace('const x=64+i*448;', 'const x=64+i*454;').replace('[x,384,424,384]', '[x,384,430,384]')
s = s.replace("text('icon'+i,icons[i],[x+32,416,72,64],20,i===2?'#9B570B':'#4A6BCE','#FDF6EC',true);", "image('icon'+i,iconFiles[i],[x+32,416,64,64]);")
s = s.replace("image('icon'+i,iconFiles[i],[x+32,416,64,64]);", "centerIcon('icon'+i,icons[i],[x+32,416,64,64],i===2?'#9B570B':'#4A6BCE');")
if 'function centerIcon(' not in s:
    s = s.replace('function image(key,file,box,back=null)', "function centerIcon(key,symbol,box,ink){text(key+'-panel','',box,12,ink,'#FDF6EC');const v=text(key,symbol,[box[0]+8,box[1]+16,48,36],20,ink,null,true);v.visual.objects.general[0].properties.paragraphs[0].horizontalTextAlignment='center';save(v);}\nfunction image(key,file,box,back=null)")
s = s.replace("i===0?'Öppna översikt →':'Se nästa rapportområde →',[x+32,704,352,48]", "['Öppna översikt →','Visa lönsamhet →','Analysera försäljning →','Visa transaktioner →'][i],[x+32,696,366,48]")
s = s.replace("text('yoy-label'+i,'YoY',[x+16,396,56,32]", "text('yoy-label'+i,'Årsförändring',[x+16,396,128,32]")
s = s.replace('[x+80,396,200,32]', '[x+152,396,128,32]')
s = s.replace('[x,276,296,196]', '[x,276,296,232]')
s = s.replace('[x+20,436,256,24]', '[x+20,428,256,64]')
s = s.replace('[320,496,952,264]', '[320,532,952,228]')
s = s.replace('[984,504,264,64]', '[984,540,264,64]')
s = s.replace('[1296,496,568,264]', '[1296,532,568,228]')
marker="const r=read(path.join(report,'definition/report.json'));"
icons = """const iconFiles=['Overview','Profit','Growth','Ledger'].map(n=>'PortalIcon'+n+'20261007.svg');
const iconPaths=['<rect x="18" y="18" width="11" height="11" rx="2"/><rect x="35" y="18" width="11" height="11" rx="2"/><rect x="18" y="35" width="11" height="11" rx="2"/><rect x="35" y="35" width="11" height="11" rx="2"/>','<path d="M20 44V30M32 44V20M44 44V26"/>','<path d="M18 44l12-12 8 5 10-17M37 20h11v11"/>','<rect x="21" y="17" width="22" height="30" rx="3"/><path d="M27 25h10M27 32h10M27 39h6"/>'];
iconFiles.forEach((file,i)=>fs.writeFileSync(path.join(resources,file),`<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><rect x=".5" y=".5" width="63" height="63" rx="12" fill="#FDF6EC" stroke="#D5DDE7"/><g fill="none" stroke="${i===2?'#9B570B':'#4A6BCE'}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${iconPaths[i]}</g></svg>`));
"""
if 'const iconFiles=' not in s:
    s = s.replace(marker,icons+marker)
s = s.replace("{name:bg,path:bg,type:'Image'}]", "{name:bg,path:bg,type:'Image'},...iconFiles.map(file=>({name:file,path:file,type:'Image'}))]")
p.write_text(s,encoding='utf-8')
