const fs=require('fs'),path=require('path'),crypto=require('crypto');
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?`${v}D`:`'${v}'`}}});
function polish(reportPath){
 const report=reportPath||path.resolve(__dirname,'../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report');
 const page='30e52cac0a5174639318',dir=path.join(report,'definition/pages',page,'visuals');
 const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
 const file=k=>path.join(dir,crypto.createHash('sha256').update('assignment-page:'+page+':'+k).digest('hex').slice(0,20),'visual.json');
 const update=(k,fn)=>{const p=file(k),v=read(p);fn(v);fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');};
 const customer=path.join(report,'definition/pages/f429b020315c602ce0ed/visuals');
 const established=read(path.join(customer,'f20bbd6190796433338e/visual.json'));
 const title=read(path.join(customer,'2959a3126b1062dede29/visual.json'));
 update('title',v=>{v.visual.objects.general[0].properties.paragraphs[0].textRuns[0].textStyle=structuredClone(title.visual.objects.general[0].properties.paragraphs[0].textRuns[0].textStyle);});
 update('group',v=>{Object.assign(v.position,{x:1624,y:16,width:264,height:88});});
 const group=read(file('group'));
 update('area',v=>{
  const query=v.visual.query;v.visual=structuredClone(group.visual);v.visual.query=query;
  delete v.filterConfig;
  v.visual.objects.header[0].properties.text=lit('Område');
  v.visual.objects.general=[];
  v.visual.objects.selection=[{properties:{singleSelect:lit(false),strictSingleSelect:lit(false),selectAllCheckboxEnabled:lit(true)}}];
  Object.assign(v.position,{x:1352,y:16,width:256,height:88});
 });
 update('area-label',v=>{v.isHidden=true;});
 for(const [key,box,align,size] of [['history-context',[304,112,640,32],'left',11],['plan-context',[960,112,928,32],'right',10.5],['resource-context',[1352,94,536,20],'right',9]])update(key,v=>{
  Object.assign(v.position,{x:box[0],y:box[1],width:box[2],height:box[3]});
  v.visual.objects=structuredClone(established.visual.objects);
  for(const entry of v.visual.objects.value||[])Object.assign(entry.properties,{horizontalAlignment:lit(align),fontSize:lit(size),bold:lit(false),textWrap:lit(false)});
  for(const name of ['fillCustom','outline','shadowCustom'])v.visual.objects[name]=[{properties:{show:lit(false)}},{selector:{id:'default'},properties:{show:lit(false),transparency:lit(100)}}];
  v.visual.objects.cardCalloutArea=[{properties:{show:lit(false),backgroundTransparency:lit(100),paddingUniform:lit(0)}}];
  v.visual.visualContainerObjects.background=[{properties:{show:lit(false),transparency:lit(100)}}];
  v.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];
 });
 console.log('Aligned header with established pages; two full-width dropdowns and transparent period context.');
}
module.exports=polish;
if(require.main===module)polish();
