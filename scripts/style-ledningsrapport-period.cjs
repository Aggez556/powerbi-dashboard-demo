const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..'),base=path.join(root,'powerbi-ledningsrapport');
const mapping=JSON.parse(fs.readFileSync(path.join(base,'validation/header-visuals.json'),'utf8'));
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?v+'D':"'"+v+"'"}}});
const fill=c=>({solid:{color:lit(c)}}),entry=p=>[{properties:p}];
function patch(key,change){
 const pages=path.join(base,'LedningsrapportUtanScroll.Report/definition/pages'),target={'period-label':'Periodtext','r12-end':'R12val',year:'Helårsval',month:'Månadsval'}[key],matches=[];
 for(const p of fs.readdirSync(pages)){const dir=path.join(pages,p,'visuals');if(!fs.existsSync(dir))continue;for(const name of fs.readdirSync(dir)){const file=path.join(dir,name,'visual.json');const v=JSON.parse(fs.readFileSync(file,'utf8').replace(/^\uFEFF/,''));const query=JSON.stringify(v.visual?.query||{});if(query.includes(target))matches.push({file,v});}}
 if(matches.length!==1)throw Error(`Expected one ${key} visual, found ${matches.length}`);
 const {file,v}=matches[0];change(v);fs.writeFileSync(file,JSON.stringify(v,null,2)+'\n');
}
patch('period-label',v=>{
 Object.assign(v.position,{x:840,y:112,width:1048,height:32});
 const vc=v.visual.visualContainerObjects;
 vc.background=entry({show:lit(false),transparency:lit(100)});vc.border=entry({show:lit(false)});
 vc.padding=entry({top:lit(0),bottom:lit(0),left:lit(0),right:lit(0)});
 v.visual.objects.cardCalloutArea=entry({show:lit(false),backgroundTransparency:lit(100),paddingUniform:lit(0)});
 for(const key of ['fillCustom','outline','shadowCustom'])v.visual.objects[key]=[{properties:{show:lit(false)}},{selector:{id:'default'},properties:{show:lit(false)}}];
 for(const item of v.visual.objects.value)item.properties.horizontalAlignment=lit('right');
});
for(const key of ['r12-end','year','month'])patch(key,v=>{
 Object.assign(v.position,{x:1496,y:28,width:392,height:80});
 const vc=v.visual.visualContainerObjects;
 vc.background=entry({show:lit(false)});vc.border=entry({show:lit(false)});
 vc.padding=entry({top:lit(0),bottom:lit(0),left:lit(0),right:lit(0)});
 v.visual.objects.items=entry({fontFamily:lit('Segoe UI Semibold'),textSize:lit(12),fontColor:fill('#0F3163'),background:fill('#FAEBD7'),padding:lit(8)});
 v.visual.objects.header[0].properties.fontColor=fill('#5B6B80');
});
const pagesDir=path.join(base,'LedningsrapportUtanScroll.Report/definition/pages');
for(const page of fs.readdirSync(pagesDir)){
 const dir=path.join(pagesDir,page,'visuals');if(!fs.existsSync(dir))continue;
 for(const name of fs.readdirSync(dir)){
  const file=path.join(dir,name,'visual.json'),v=JSON.parse(fs.readFileSync(file,'utf8').replace(/^\uFEFF/,''));
  const paragraphs=v.visual?.objects?.general?.[0]?.properties?.paragraphs;
  const text=paragraphs?.flatMap(p=>p.textRuns.map(r=>r.value)).join('');
  let changed=false;
  if(text==='Ledningsöversikt'){Object.assign(v.position,{x:304,y:40,width:744,height:56});changed=true;}
  if(text==='Periodtyp'){Object.assign(v.position,{x:1080,y:28,width:376,height:24});changed=true;}
  if(v.visual?.visualType==='actionButton' && v.position.x>=1080 && v.position.y<120){
   v.position.y=56;v.position.height=40;
   for(const item of v.visual.objects.shape||[])if(item.properties.roundEdge)item.properties.roundEdge=lit(4);
   changed=true;
  }
  if(changed)fs.writeFileSync(file,JSON.stringify(v,null,2)+'\n');
 }
}
console.log('Period context is transparent and right aligned; all date selectors match the period control palette.');
