// Focused patch: preserve all Desktop-saved visuals and data outside the header.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),report=path.join(root,'powerbi-ledningsrapport/LedningsrapportUtanScroll.Report');
const mapping=JSON.parse(fs.readFileSync(path.join(root,'powerbi-ledningsrapport/validation/header-visuals.json'),'utf8')),page=mapping.page;
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?v+'D':"'"+v+"'"}}});
function edit(key,box,fn){
 const p=path.join(report,'definition/pages',page,'visuals',mapping.visuals[key],'visual.json');
 const v=JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
 Object.assign(v.position,{x:box[0],y:box[1],width:box[2],height:box[3]});fn?.(v);
 fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');
}
edit('page-title',[304,24,744,56],v=>v.visual.objects.general[0].properties.paragraphs.forEach(p=>p.textRuns.forEach(t=>t.textStyle.fontSize='32pt')));
edit('period-heading',[1080,24,372,24]);
for(let active=0;active<3;active++)for(let i=0;i<3;i++)edit(`mode-${active}-${i}`,[1080+i*128,56,120,56],v=>v.visual.objects.text.filter(x=>x.selector).forEach(x=>{x.properties.horizontalAlignment=lit('center');x.properties.leftMargin=lit(0);x.properties.rightMargin=lit(0);}));
for(const key of ['r12-end','year','month'])edit(key,[1496,24,392,88],v=>{
 v.visual.visualContainerObjects.background=[{properties:{show:lit(false)}}];
 v.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];
 v.visual.visualContainerObjects.padding=[{properties:{top:lit(0),bottom:lit(0),left:lit(0),right:lit(0)}}];
});
edit('period-label',[304,120,1584,32],v=>{
 const vc=v.visual.visualContainerObjects;
 vc.background=[{properties:{show:lit(false)}}];vc.border=[{properties:{show:lit(false)}}];
 vc.padding=[{properties:{top:lit(0),bottom:lit(0),left:lit(0),right:lit(0)}}];
 for(const key of ['fillCustom','outline'])v.visual.objects[key]=[{selector:{id:'default'},properties:{show:lit(false)}}];
 for(const item of v.visual.objects.value){item.properties.bold=lit(false);item.properties.fontSize=lit(11);item.properties.textWrap=lit(false);}
});
console.log('Updated only header title, filter positions, mode alignment and period context.');
