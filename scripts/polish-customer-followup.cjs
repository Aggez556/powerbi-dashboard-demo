const fs=require('fs'),path=require('path'),crypto=require('crypto');
const page='f429b020315c602ce0ed';
const dir=path.resolve(__dirname,'../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report/definition/pages',page,'visuals');
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?`${v}D`:`'${v}'`}}});
const color=v=>({solid:{color:lit(v)}});
function edit(key,fn){const name=crypto.createHash('sha256').update('customer-page:'+page+':'+key).digest('hex').slice(0,20),file=path.join(dir,name,'visual.json');const v=JSON.parse(fs.readFileSync(file,'utf8').replace(/^\uFEFF/,''));fn(v);fs.writeFileSync(file,JSON.stringify(v,null,2)+'\n');}
function polish(){
 edit('detail',v=>{
  Object.assign(v.position,{y:910,height:214});
  const o=v.visual.objects;
  Object.assign(o.columnHeaders[0].properties,{fontFamily:lit('Segoe UI Semibold'),fontSize:lit(11),backColor:color('#EEF2F7'),fontColor:color('#0F3163'),wordWrap:lit(false)});
  Object.assign(o.values[0].properties,{fontFamily:lit('Segoe UI'),fontSize:lit(11),fontColorPrimary:color('#405572'),fontColorSecondary:color('#405572'),backColorPrimary:color('#FFFFFF'),backColorSecondary:color('#F7F9FC'),wordWrap:lit(false)});
  Object.assign(o.grid[0].properties,{rowPadding:lit(4),gridVertical:lit(false),gridHorizontal:lit(true),gridHorizontalColor:color('#E7ECF2'),gridHorizontalWeight:lit(1),outlineWeight:lit(0)});
  const widths=[180,118,112,106,86,140];
  o.columnWidth.forEach((entry,i)=>entry.properties.value=lit(widths[i]));
  o.columnFormatting=v.visual.query.queryState.Values.projections.map((p,i)=>({selector:{metadata:p.queryRef},properties:{alignment:lit(i<2||i===5?'Left':'Right'),styleHeader:lit(true),styleValues:lit(true),styleTotal:lit(true)}}));
 });
 edit('status-selector',v=>{
  v.position.height=42;
  for(const entry of v.visual.objects.value){Object.assign(entry.properties,{fontFamily:lit('Segoe UI'),fontSize:lit(11),textWrap:lit(false)});if(entry.selector?.id==='selected')entry.properties.bold=lit(true);}
  v.visual.objects.layout[0].properties.cellPadding=lit(3);
  v.visual.objects.outline=[{properties:{show:lit(false)}}];
  for(const entry of v.visual.objects.fillCustom||[])if(entry.selector?.id==='default')entry.properties.fillColor=color('#F0F3F8');else if(entry.selector?.id==='selected')entry.properties.fillColor=color('#0F3163');
 });
 for(const [key,y] of [['detail-extra1',1128],['detail-extra2',1152]])edit(key,v=>{Object.assign(v.position,{x:1126,y,width:750,height:24});for(const obj of Object.values(v.visual.objects))for(const entry of obj)if(entry.properties?.fontSize)entry.properties.fontSize=lit(10);});
 console.log('Polished customer follow-up table and status filter.');
}
module.exports=polish;
if(require.main===module)polish();
