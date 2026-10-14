// Page chrome only; preserve statement, filters, bookmark state and sidebar.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?`${v}D`:`'${v}'`}}});
function polish(reportPath){
 const report=reportPath||path.resolve(__dirname,'../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report');
 const page='cbe967640ff6843fb323',dir=path.join(report,'definition/pages',page,'visuals');
 const update=(key,fn)=>{const id=crypto.createHash('sha256').update('budget-scenarios:'+page+':'+key).digest('hex').slice(0,20),file=path.join(dir,id,'visual.json'),v=JSON.parse(fs.readFileSync(file,'utf8').replace(/^\uFEFF/,''));fn(v);fs.writeFileSync(file,JSON.stringify(v,null,2)+'\n');};
 const box=(key,values)=>update(key,v=>Object.assign(v.position,values));
 const card=(key,values,size,bold=false)=>update(key,v=>{Object.assign(v.position,values);for(const item of v.visual.objects.value){Object.assign(item.properties,{fontSize:lit(size),bold:lit(bold),fontFamily:lit(bold?'Segoe UI Semibold':'Segoe UI'),textWrap:lit(false)});}});
 const label=(key,values,size)=>update(key,v=>{Object.assign(v.position,values);for(const p of v.visual.objects.general[0].properties.paragraphs)for(const t of p.textRuns)Object.assign(t.textStyle,{fontSize:size+'pt',fontFamily:'Segoe UI',color:'#0F3163'});});
 // Native cards add an inner inset: compensate so text aligns with headings.
 for(let i=0;i<3;i++){
  const x=288+i*542;
  box('kpi-title'+i,{x:x+24,y:180,width:478,height:32});
  card('kpi-value'+i,{x:x+8,y:218,width:494,height:64},36);
  card('kpi-budget'+i,{x:x+8,y:286,width:494,height:30},13);
  card('kpi-diff'+i,{x:x+8,y:326,width:494,height:30},15,true);
 }
 card('matrix-subtitle',{x:608,y:462,width:1268,height:36},13);
 card('matrix-unit',{x:608,y:508,width:1268,height:28},11);
 card('source-note',{x:608,y:1156,width:1268,height:24},10);
 card('period',{x:296,y:1016,width:264,height:28},11);
 // Consistent section rhythm; leave space for scenario B in comparison mode.
 label('scenario-label',{y:416,height:32},15);
 box('scenario',{y:456,height:120});
 box('scenario-help',{y:584,height:28});
 label('comparison-label',{y:628,height:32},15);
 for(let active=0;active<2;active++)for(let i=0;i<2;i++)box(`mode-${active}-${i}`,{y:668+i*48,height:44});
 box('comparison',{y:668,height:92});
 box('scenario-b',{y:766,height:64});
 label('months-label',{y:832,height:32},15);
 box('months',{y:872,height:136});
 label('view-label',{y:1052,height:30},15);
 box('view',{y:1088,height:40});
 update('reset',v=>{Object.assign(v.position,{y:1136,height:40});for(const item of v.visual.objects.text)if(item.selector){Object.assign(item.properties,{fontSize:lit(12),leftMargin:lit(0),rightMargin:lit(0)});}for(const item of v.visual.objects.fill)if(item.selector?.id==='default')item.properties.fillColor={solid:{color:lit('#EEF2F7')}};});
 update('year',v=>{Object.assign(v.position,{y:24,height:80});v.visual.objects.header[0].properties.textSize=lit(12);v.visual.objects.items[0].properties.textSize=lit(13);v.visual.objects.items[0].properties.background={solid:{color:lit('#EEF2F7')}};});
 console.log('Polished Budget page alignment, typography and control spacing; statement unchanged.');
}
module.exports=polish;
if(require.main===module)polish();
