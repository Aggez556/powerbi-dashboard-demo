// Focused, reproducible report-only corrections; semantic data stays unchanged.
const fs=require('fs'),path=require('path');
const p=path.join(__dirname,'build-sales-finance.cjs');
let s=fs.readFileSync(p,'utf8');
s=s.replace("text('suite','VERKSAMHETSANALYS',[312,68,640,36],12,'#0F3163',null,true);",'');
s=s.replace("text('eyebrow','FÖRSÄLJNING OCH EKONOMI',[64,152,960,40],12,'#9B570B',null,true);",'');
s=s.replace("r.themeCollection.customTheme=", "r.settings.locale='sv-SE';r.themeCollection.customTheme=");
// Suppress the additional box inside each KPI and align its value with its label.
s=s.replace("labelDisplayUnits:lit(1),showBlankAs", "horizontalAlignment:lit('left'),labelDisplayUnits:lit(1),showBlankAs");
s=s.replace("{value:[{selector:{id:'default'},properties:props}],label:", "{outline:[{selector:{id:'default'},properties:{show:lit(false)}}],fillCustom:[{selector:{id:'default'},properties:{show:lit(false)}}],cardCalloutArea:[{properties:{paddingUniform:lit(0),show:lit(false),backgroundTransparency:lit(100)}}],value:[{selector:{id:'default'},properties:props}],label:");
// New panels reserve a real header band instead of laying a slicer over the plot.
const marker='function page(index)';
if(!s.includes('function chartWithChoice('))s=s.replace(marker,`function chartWithChoice(key,type,title,box,table,column,measures,choice,top){
 text(key+'-panel','',box,12,'#0F3163','#FFFFFF');
 text(key+'-heading',title,[box[0]+16,box[1]+12,box[2]-32,36],13,'#0F3163',null,true);
 const v=chart(key,type,'',[box[0],box[1]+72,box[2],box[3]-72],table,column,measures,top);
 v.visual.visualContainerObjects.background=[{properties:{show:lit(false)}}];
 v.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];
 if(measures.length===2)v.visual.query.queryState.Y.projections.forEach((projection,i)=>projection.nativeQueryRef=i?'Föregående år':'Aktuellt år');
 save(v);select(key+'-choice',choice.table,choice.column,choice.box,choice.selected);
}
`+marker);
s=s.replace("chart('trend','clusteredColumnChart','Månadsutveckling',[320,532,952,228],'Datum','Månad',['Trendvärde','Trend föregående år']);select('trend-choice','Trendval','Mått',[984,540,264,64],'Omsättning');", "chartWithChoice('trend','clusteredColumnChart','Månadsutveckling',[320,532,952,228],'Datum','Månad',['Trendvärde','Trend föregående år'],{table:'Trendval',column:'Mått',box:[984,536,264,64],selected:'Omsättning'});");
s=s.replace("chart('country','clusteredBarChart','Omsättning per marknad',[320,784,472,248],'Analysaxel','Namn',['Analysvärde','Analys föregående år']);select('axis-choice','Analysaxel','Typ',[584,792,192,64],'Land');", "chartWithChoice('country','clusteredBarChart','Omsättning per marknad',[320,784,472,248],'Analysaxel','Namn',['Analysvärde','Analys föregående år'],{table:'Analysaxel',column:'Typ',box:[584,788,192,64],selected:'Land'});");
s=s.replace("chart('products','clusteredBarChart','Topp 5 produkter',[1296,784,568,248],'Produkter','Produkt',['Produktvärde'],5);select('product-choice','Produktval','Mått',[1584,792,256,64],'Omsättning');", "chartWithChoice('products','clusteredBarChart','Topp 5 produkter',[1296,784,568,248],'Produkter','Produkt',['Produktvärde'],{table:'Produktval',column:'Mått',box:[1584,788,256,64],selected:'Omsättning'},5);");
// Friendly legend names on the unselected team chart as well.
s=s.replace("return save(v);\n}\nfunction chartWithChoice", "if(measures.length===2)v.visual.query.queryState.Y.projections.forEach((projection,i)=>projection.nativeQueryRef=i?'Föregående år':'Aktuellt år');\n return save(v);\n}\nfunction chartWithChoice");
// Remove only known retired generated visuals, never arbitrary report content.
if(!s.includes('const retiredVisuals='))s=s.replace("write(path.join(base,'validation/layout.json')", `const retiredVisuals=[[ids[0],'suite'],[ids[0],'eyebrow'],[ids[0],'scope'],[ids[1],'axis-choice'],[ids[1],'product-choice']];
for(const [pageName,key] of retiredVisuals){const dir=path.join(report,'definition/pages',pageName,'visuals',id(pageName+':'+key));const file=path.join(dir,'visual.json');if(!file.startsWith(report+path.sep))throw Error('Invalid cleanup target');if(fs.existsSync(file))fs.unlinkSync(file);if(fs.existsSync(dir)&&fs.readdirSync(dir).length===0)fs.rmdirSync(dir);}
write(path.join(base,'validation/layout.json')`);
fs.writeFileSync(p,s);
