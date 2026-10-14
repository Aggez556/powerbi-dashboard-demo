// Deterministic native PBIR visuals bound to the generated Swedish TMDL model.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),report=path.join(root,'powerbi/AubecoHandel.Report');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const write=(p,o)=>{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(o,null,2)+'\n');};
const id=s=>crypto.createHash('sha256').update(s).digest('hex').slice(0,20);
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?`${v}D`:`'${v.replace(/'/g,"''")}'`}}});
const color=c=>({solid:{color:lit(c)}});
const col=(t,p,alias)=>({Column:{Expression:{SourceRef:alias?{Source:alias}:{Entity:t}},Property:p}});
const measure=p=>({Measure:{Expression:{SourceRef:{Entity:'Försäljning'}},Property:p}});
const projection=field=>{const q=field.Column||field.Measure;return {field,queryRef:`${q.Expression.SourceRef.Entity}.${q.Property}`,nativeQueryRef:q.Property};};
const themeName='AubecoHandel-541a68b3.json';
const theme=read(path.join(root,'themes/aubeco-powerbi.json')); theme.name=themeName;
// CLI 0.5.0 treats these card object names as native objects, while metadata
// resolves their container variants. Put safeguards explicitly on each card.
for(const object of ['border','padding','spacing'])delete theme.visualStyles.cardVisual['*'][object];
write(path.join(report,'StaticResources/RegisteredResources',themeName),theme);
const reportJson=read(path.join(report,'definition/report.json'));
reportJson.themeCollection.customTheme={name:themeName,reportVersionAtImport:{visual:'2.11.0',report:'3.4.0',page:'2.3.1'},type:'RegisteredResources'};
reportJson.resourcePackages=reportJson.resourcePackages.filter(x=>x.name!=='RegisteredResources');
reportJson.resourcePackages.push({name:'RegisteredResources',type:'RegisteredResources',items:[{name:themeName,path:themeName,type:'CustomTheme'}]});
write(path.join(report,'definition/report.json'),reportJson);
const pagesFile=path.join(report,'definition/pages/pages.json'),pageMeta=read(pagesFile);
// Preserve the scaffold's first page identity, add a stable second page.
const overviewId=pageMeta.pageOrder[0],productId=id('product-analysis');
pageMeta.pageOrder=[overviewId,productId];pageMeta.activePageName=overviewId;write(pagesFile,pageMeta);
const placements=[];
let currentPage,tab;
function visual(key,type,title,box,queryState={},objects={},filters) {
 const name=id(`${currentPage}:${key}`);
 const content={$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json',name,
   position:{x:box[0],y:box[1],width:box[2],height:box[3],z:tab,tabOrder:tab++},
   visual:{visualType:type,objects,visualContainerObjects:{
     title:[{properties:{show:lit(!!title),text:lit(title||''),fontFamily:lit('Segoe UI Semibold'),fontSize:lit(14),fontColor:color('#0F3163')}}],
     general:[{properties:{altText:lit(title||key)}}],
     padding:[{properties:{top:lit(8),bottom:lit(8),left:lit(8),right:lit(8)}}],
   }}};
 if(Object.keys(queryState).length)content.visual.query={queryState:Object.fromEntries(Object.entries(queryState).map(([role,fields])=>[role,{projections:fields.map(projection)}]))};
 if(filters)content.filterConfig={filters};
 write(path.join(report,'definition/pages',currentPage,'visuals',name,'visual.json'),content);
 placements.push({page:currentPage,key,type,box,fields:Object.values(queryState).flat()});
 return content;
}
function saveVisual(v){write(path.join(report,'definition/pages',currentPage,'visuals',v.name,'visual.json'),v);}
function textbox(key,text,box,size=11,foreground='#5B6B80',background){
 const v=visual(key,'textbox',null,box,{}, {general:[{properties:{paragraphs:[{textRuns:[{value:text,textStyle:{fontFamily:size>=20?'Segoe UI Semibold':'Segoe UI',fontSize:`${size}pt`,color:foreground}}],horizontalTextAlignment:'left'}]}}]});
 v.visual.visualContainerObjects.title=[{properties:{show:lit(false)}}];
 v.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];
 v.visual.visualContainerObjects.padding=[{properties:{top:lit(background?12:0),bottom:lit(0),left:lit(background?16:0),right:lit(0)}}];
 v.visual.visualContainerObjects.background=[{properties:{show:lit(!!background),color:color(background||'#FFFFFF'),transparency:lit(0)}}];
 saveVisual(v);
}
function slicer(key,table,column,x,label,defaultYear){
 const objects={data:[{properties:{mode:lit('Dropdown')}}],header:[{properties:{show:lit(true),text:lit(label)}}]};
 if(defaultYear)objects.general=[{properties:{filter:{filter:{Version:2,From:[{Name:'d',Entity:table,Type:0}],Where:[{Condition:{In:{Expressions:[col(table,column,'d')],Values:[[{Literal:{Value:'2025L'}}]]}}}]}}}}];
 visual(key,'slicer',null,[x,32,column==='År'?304:320,80],{Values:[col(table,column)]},objects);
}
function card(key,label,box,accent){
 const v=visual(key,'cardVisual',null,box,{Data:[measure(label)]},{value:[{selector:{id:'default'},properties:{fontFamily:lit('Segoe UI Semibold'),fontSize:lit(32),fontColor:color('#0F3163'),showBlankAs:lit('–')}}],label:[{selector:{id:'default'},properties:{show:lit(true),fontFamily:lit('Segoe UI'),fontSize:lit(11),fontColor:color('#5B6B80')}}]});
 const value=v.visual.objects.value[0].properties;
 value.labelDisplayUnits=lit(1);
 value.labelPrecision=lit(label==='Bruttomarginal'||label==='Tillväxt mot föregående år'?1:0);
 value.customFormatString=lit(label==='Antal order'?'#,##0':label==='Bruttomarginal'||label==='Tillväxt mot föregående år'?'0.0\u00a0%;-0.0\u00a0%;0.0\u00a0%':'#,##0 "\u00a0kr"');
 v.visual.visualContainerObjects.padding=[{properties:{top:lit(0),bottom:lit(0),left:lit(0),right:lit(0)}}];
 v.visual.visualContainerObjects.spacing=[{selector:{id:'default'},properties:{customizeSpacing:lit(true),verticalSpacing:lit(-6)}}];
 v.visual.visualContainerObjects.general[0].properties.altText=lit(`${label} inom valt år och kategori. Tillväxt kräver jämförbara föregåendeårsdata.`);
 saveVisual(v);
}
function topN(table,column,n){
 const source={Name:'c',Entity:table,Type:0},fact={Name:'f',Entity:'Försäljning',Type:0};
 return [{name:id(`${table}:${column}:top${n}`),field:col(table,column),type:'TopN',howCreated:'User',filter:{Version:2,From:[
   {Name:'subquery',Type:2,Expression:{Subquery:{Query:{Version:2,From:[source,fact],Select:[{...col(table,column,'c'),Name:'field'}],OrderBy:[{Direction:2,Expression:{Aggregation:{Expression:col('Försäljning','Radomsättning','f'),Function:0}}}],Top:n}}}},source],Where:[{Condition:{In:{Expressions:[col(table,column,'c')],Table:{SourceRef:{Source:'subquery'}}}}}]}}];
}
function bar(key,title,table,column,label,box,take){
 const v=visual(key,'clusteredBarChart',title,box,{Category:[col(table,column)],Y:[measure(label)],Tooltips:['Omsättning','Bruttomarginal'].filter(m=>m!==label).map(measure)},
   {dataPoint:[{properties:{defaultColor:color(label==='Bruttomarginal'?'#9B570B':'#0F3163')}}],legend:[{properties:{show:lit(false)}}],valueAxis:[{properties:{show:lit(true),start:lit(0),showAxisTitle:lit(false)}}]},take?topN(table,column,take):undefined);
 v.visual.query.sortDefinition={sort:[{field:measure(label),direction:'Descending'}],isDefaultSort:true};saveVisual(v);
}
function page(pageId,name){
 currentPage=pageId;tab=0;
 write(path.join(report,'definition/pages',pageId,'page.json'),{$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json',name:pageId,displayName:name,displayOption:'FitToPage',height:1080,width:1920,objects:{background:[{properties:{color:color('#FDF6EC'),transparency:lit(0)}}]}});
 textbox('page_title',`${name} · Aubeco Handel`,[32,24,1184,88],20,'#FFFFFF','#09224A');
 slicer('year','Datum','År',1240,'År',true); slicer('category','Produkter','Kategori',1568,'Kategori',false);
 textbox('context','Fiktivt handelsföretag · Belopp exklusive moms · År och kategori filtrerar denna sida',[32,128,1856,32]);
 textbox('footer','Testdata 2024–2025 · Byt sida med Power BI:s sidflikar · 2024 saknar jämförelsedata för 2023',[32,1032,1856,24]);
}
page(overviewId,'Försäljningsöversikt');
const kpis=['Omsättning','Bruttovinst','Bruttomarginal','Antal order','Tillväxt mot föregående år'];
kpis.forEach((label,i)=>card(`kpi${i}`,label,[32+i*376,184,i===4?352:352,152]));
const trend=visual('monthly','lineChart','Omsättning per månad',[32,368,1088,640],{Category:[col('Datum','År–månad')],Y:[measure('Omsättning')],Tooltips:[measure('Bruttovinst'),measure('Bruttomarginal')]},{dataPoint:[{properties:{defaultColor:color('#0F3163')}}],lineStyles:[{properties:{strokeWidth:lit(2.5),lineChartType:lit('linear'),areaShow:lit(false)}}],labels:[{properties:{show:lit(false)}}]});
trend.visual.query.sortDefinition={sort:[{field:col('Datum','År–månad'),direction:'Ascending'}],isDefaultSort:true};saveVisual(trend);
bar('customers','10 största kunder efter omsättning','Kunder','Kund','Omsättning',[1144,368,744,640],10);
page(productId,'Produktanalys');
bar('category-revenue','Omsättning per kategori','Produkter','Kategori','Omsättning',[32,184,904,320]);
bar('category-margin','Bruttomarginal per kategori','Produkter','Kategori','Bruttomarginal',[960,184,928,320]);
bar('product-revenue','10 största produkter efter omsättning','Produkter','Produkt','Omsättning',[32,528,904,480],10);
const table=visual('product-table','tableEx','Produktdetaljer – omsättning och marginal',[960,528,928,480],{Values:[col('Produkter','Kategori'),col('Produkter','Produkt'),measure('Omsättning'),measure('Kostnad'),measure('Bruttovinst'),measure('Bruttomarginal')]});
table.visual.query.sortDefinition={sort:[{field:measure('Omsättning'),direction:'Descending'}],isDefaultSort:true};saveVisual(table);
write(path.join(root,'powerbi/validation/layout-and-bindings.json'),{canvas:{width:1920,height:1080},placements,themeFile:themeName});
console.log(`Generated ${placements.length} native visuals on 2 pages.`);
if(fs.existsSync(path.join(root,'assets/aubeco/aubeco-header-wordmark.png')))require('./apply-aubeco-logo.cjs');
