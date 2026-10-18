// Tooltip pilot: customer page only. Existing measures and filter context reused.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
function design(){
 const report=path.resolve(__dirname,'../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report');
 const hash=s=>crypto.createHash('sha256').update(s).digest('hex').slice(0,20);
 const sourcePage='f429b020315c602ce0ed',tooltipPage=hash('customer-tooltip:industry-page');
 const pageDir=path.join(report,'definition/pages'),dir=path.join(pageDir,sourcePage,'visuals');
 const read=f=>JSON.parse(fs.readFileSync(f,'utf8').replace(/^\uFEFF/,''));
 const write=(f,v)=>{fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n');};
 const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?v+'D':"'"+v.replace(/'/g,"''")+"'"}}});
 const color=c=>({solid:{color:lit(c)}});
 const native={show:lit(true),type:lit('Default'),fontFamily:lit('Segoe UI'),fontSize:lit(11),titleFontColor:color('#5B6B80'),valueFontColor:color('#0F3163'),background:color('#FFFFFF'),transparency:lit(0)};
 const labels={'Kundgrupp månadsintäkt':'Försäljning','Kundgrupp andel':'Andel av månadens försäljning','Kundgrupp':'Kundgrupp','Kundbas bryggsteg':'Antal kunder','Kundintäkt bryggsteg':'Försäljning','Steg':'Förändring'};
 let chartCount=0;
 for(const name of fs.readdirSync(dir)){
  const file=path.join(dir,name,'visual.json');if(!fs.existsSync(file))continue;
  const v=read(file),type=v.visual.visualType;
  if(!['lineChart','clusteredColumnChart','columnChart','waterfallChart','tableEx','cardVisual'].includes(type))continue;
  const containers=v.visual.visualContainerObjects||={};
  // KPI explanatory lines already contain their full information.
  if(type==='cardVisual'){containers.visualTooltip=[{properties:{show:lit(false)}}];write(file,v);continue;}
  containers.visualTooltip=[{properties:structuredClone(native)}];
  const q=v.visual.query?.queryState;
  if(type==='waterfallChart')delete q.Tooltips; // Retention does not describe an individual bridge step.
  if(q)for(const role of Object.values(q))for(const p of role.projections||[]){
   const prop=(p.field.Measure||p.field.Column)?.Property;
   if(labels[prop])p.displayName=p.nativeQueryRef=labels[prop];
  }
  if(['lineChart','clusteredColumnChart'].includes(type)&&q?.Series?.projections[0]?.field.Column.Property==='Kundbransch'){
   containers.visualTooltip=[{properties:{...structuredClone(native),type:lit('Canvas'),section:lit(tooltipPage)}}];
  }
  if(type!=='tableEx')chartCount++;
  write(file,v);
 }
 const page={
  $schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json',
  name:tooltipPage,displayName:'Tooltip · Branschutveckling',type:'Tooltip',displayOption:'ActualSize',width:560,height:270,visibility:'HiddenInViewMode',
  pageBinding:{name:hash('customer-tooltip:binding'),type:'Tooltip',acceptsFilterContext:'Default'},
  objects:{background:[{properties:{color:color('#FFFFFF'),transparency:lit(0)}}]}
 };
 write(path.join(pageDir,tooltipPage,'page.json'),page);
 const indexFile=path.join(pageDir,'pages.json'),index=read(indexFile);
 if(!index.pageOrder.includes(tooltipPage))index.pageOrder.push(tooltipPage);
 write(indexFile,index);
 const visualsDir=path.join(pageDir,tooltipPage,'visuals');
 const save=v=>write(path.join(visualsDir,v.name,'visual.json'),v);
 const textTemplate=read(path.join(dir,hash('customer-industry-change:title'),'visual.json'));
 for(const [key,label,y,size] of [['title','Försäljning per bransch',8,13],['subtitle','Jämfört med samma månad föregående år',34,9]]){
  const v=structuredClone(textTemplate);v.name=hash('customer-tooltip:'+key);delete v.isHidden;
  Object.assign(v.position,{x:12,y,width:536,height:key==='title'?26:22,z:1});
  v.visual.objects.general[0].properties.paragraphs=[{textRuns:[{value:label,textStyle:{fontFamily:'Segoe UI',fontSize:size+'pt',color:key==='title'?'#0F3163':'#5B6B80'}}]}];
  v.visual.visualContainerObjects.visualTooltip=[{properties:{show:lit(false)}}];save(v);
 }
 const table=read(path.join(dir,'d5cf6cd421060b6d9ad3','visual.json'));
 table.name=hash('customer-tooltip:table');delete table.filterConfig;delete table.isHidden;
 Object.assign(table.position,{x:12,y:62,width:536,height:196,z:2});
 const fields=[['Column','Kundbransch','Bransch'],['Measure','Bransch månadsförsäljning','Försäljning'],['Measure','Bransch månadsförändring procent','Ändring, %'],['Measure','Bransch månadsförändring kronor','Ändring, kr']];
 table.visual.query={queryState:{Values:{projections:fields.map(([kind,prop,label])=>({field:{[kind]:{Expression:{SourceRef:{Entity:'Kunder'}},Property:prop}},queryRef:'Kunder.'+prop,nativeQueryRef:label,displayName:label}))}},sortDefinition:{sort:[{field:{Column:{Expression:{SourceRef:{Entity:'Kunder'}},Property:'Kundbransch'}},direction:'Ascending'}],isDefaultSort:false}};
 table.visual.objects={
  columnHeaders:[{properties:{fontFamily:lit('Segoe UI Semibold'),fontSize:lit(10),fontColor:color('#0F3163'),backColor:color('#EEF2F7'),autoSizeColumnWidth:lit(false),columnAdjustment:lit('fixedWidth'),customColumnWidth:lit(true),wordWrap:lit(false)}}],
  values:[{properties:{fontFamily:lit('Segoe UI'),fontSize:lit(10),fontColorPrimary:color('#0F3163'),fontColorSecondary:color('#0F3163'),backColorPrimary:color('#FFFFFF'),backColorSecondary:color('#F5F7FA'),wordWrap:lit(false)}}],
  grid:[{properties:{rowPadding:lit(3),gridVertical:lit(false),gridHorizontal:lit(false),outlineWeight:lit(0)}}],
  total:[{properties:{totals:lit(false)}}],
  columnWidth:fields.map(([,prop],i)=>({selector:{metadata:'Kunder.'+prop},properties:{value:lit([104,146,108,146][i])}}))
 };
 table.visual.visualContainerObjects={background:[{properties:{show:lit(false)}}],border:[{properties:{show:lit(false)}}],title:[{properties:{show:lit(false)}}],visualTooltip:[{properties:{show:lit(false)}}],visualHeader:[{properties:{show:lit(false)}}]};
 save(table);
 console.log('Customer tooltip pilot: '+chartCount+' chart views, one compact industry tooltip page, native tooltip style and Swedish labels.');
}
module.exports=design;if(require.main===module)design();
