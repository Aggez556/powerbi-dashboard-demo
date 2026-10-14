// User-supplied Aubeco SVGs and October branding refinement.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),report=path.join(root,'powerbi-sales-finance/AubecoSalesFinance.Report');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,'')),write=(p,v)=>fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):`'${v}'`}}}),color=c=>({solid:{color:lit(c)}});
const id=s=>crypto.createHash('sha256').update(s).digest('hex').slice(0,20);
const rfile=path.join(report,'definition/report.json'),r=read(rfile),pack=r.resourcePackages.find(p=>p.name==='RegisteredResources'),res=path.join(report,'StaticResources/RegisteredResources');
for(let i=0;i<4;i++){
 const name=`HomeArea${i}.png`;fs.copyFileSync(path.join(root,'assets/aubeco',name),path.join(res,name));
 if(!pack.items.some(x=>x.name===name))pack.items.push({name,path:name,type:'Image'});
}
for(const variant of ['blue','orange']){const name=`AubecoLogo-${variant}.svg`;fs.copyFileSync(path.join(root,'assets/aubeco',name),path.join(res,name));if(!pack.items.some(x=>x.name===name))pack.items.push({name,path:name,type:'Image'});}
const replacements={'#BD610A':'#FF8A24','#F7BA6B':'#FFB65B','#9B570B':'#BE5100','#FDF6EC':'#F5F8FC'};
function recolor(s){for(const [a,b]of Object.entries(replacements))s=s.replaceAll(a,b);return s;}
for(const item of pack.items){const p=path.join(res,item.path);if(fs.existsSync(p)&&item.name!=='AubecoLogo-orange.svg'&&item.name!=='AubecoLogo-blue.svg'&&/\.(svg|json)$/.test(p))fs.writeFileSync(p,recolor(fs.readFileSync(p,'utf8')));}
fs.writeFileSync(path.join(res,'PortalGrid202610070001.svg'),'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080"><rect width="1920" height="1080" fill="#003267"/></svg>');
for(let i=0;i<5;i++){const f=path.join(res,`Nav${i}-hover.svg`);if(fs.existsSync(f))fs.writeFileSync(f,fs.readFileSync(f,'utf8').replaceAll('#FFFFFF','#0F3163'));}
const pages=read(path.join(report,'definition/pages/pages.json')).pageOrder;
for(let i=0;i<5;i++){
 const name=`NavArtwork${i}.svg`;
 const svg=i===0?'<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><rect width="64" height="64" rx="16" fill="#E7EDF5"/><g fill="none" stroke="#003267" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M16 31L32 17l16 14M21 28v20h22V28M28 48V35h8v13"/></g></svg>':fs.readFileSync(path.join(res,`HomeArea${i-1}.svg`),'utf8').replace(/stroke="#[0-9a-fA-F]{6}"/g,'stroke="#003267"').replace(/(<rect width="64" height="64" rx="16" fill=")#[0-9a-fA-F]{6}/,'$1#E7EDF5');
 // Only the glyph remains; the navigation button supplies the background.
 fs.writeFileSync(path.join(res,name),svg.replace(/<rect width="64" height="64" rx="16" fill="#[0-9a-fA-F]{6}"\/>/,''));
 if(!pack.items.some(x=>x.name===name))pack.items.push({name,path:name,type:'Image'});
}
pages.forEach((page,pi)=>{
 const dir=path.join(report,'definition/pages',page),pf=path.join(dir,'page.json'),p=read(pf);if(pi===0)p.objects.background[0].properties.color=color('#003267');if(pi===2)p.displayName='Lönsamhet';write(pf,p);
 for(const entry of fs.readdirSync(path.join(dir,'visuals'))){
  const f=path.join(dir,'visuals',entry,'visual.json');if(!fs.existsSync(f))continue;
  if(entry===id(page+':suite-title')){
   fs.unlinkSync(f);const visualDir=path.dirname(f);
   if(fs.readdirSync(visualDir).length===0)fs.rmdirSync(visualDir);
   continue;
  }
  let v=JSON.parse(recolor(fs.readFileSync(f,'utf8')));const o=v.visual.objects,c=v.visual.visualContainerObjects;
  for(const paragraph of o.general?.[0]?.properties.paragraphs||[])for(const run of paragraph.textRuns||[])if(typeof run.value==='string')run.value=run.value.replaceAll('Ekonomi och lönsamhet','Lönsamhet').replaceAll('EKONOMI OCH LÖNSAMHET','LÖNSAMHET');
  if(v.visual.visualType==='actionButton'){
   // Reuse the actual homepage SVG, including its color and rounded tile.
   const navIndex=[0,1,2,3,4].find(n=>entry===id(page+':nav'+n));
   if(navIndex!==undefined){
    const name=`NavArtwork${navIndex}.svg`;
    const image={name:lit(name),url:{expr:{ResourcePackageItem:{PackageName:'RegisteredResources',PackageType:1,ItemName:name}}},scaling:lit('Fit')};
    const num=n=>({expr:{Literal:{Value:n+'D'}}});
    o.icon=[{properties:{show:lit(true)}},...['default','hover','selected','disabled'].map(state=>({selector:{id:state},properties:{shapeType:lit('custom'),image,placement:lit('left'),iconSize:num(28),leftMargin:num(8),rightMargin:num(6)}}))];
    // Some Desktop builds ignore custom button icons. Use an image visual
    // with the same navigation action, so clicking the artwork also navigates.
    o.icon=[{properties:{show:lit(false)}}];
    const homeIconFile=path.join(report,'definition/pages',pages[0],'visuals',id(pages[0]+':icon'+Math.max(0,navIndex-1)),'visual.json');
    const icon=read(homeIconFile);
    icon.visual.objects.image[0].properties.sourceFile={image};
    icon.name=id(page+':nav-artwork'+navIndex);
    icon.position={x:v.position.x+16,y:v.position.y+(v.position.height-32)/2,width:32,height:32,z:v.position.z+1,tabOrder:v.position.tabOrder+1000};
    for(const state of o.text||[])if(state.selector?.id==='default')state.properties.leftMargin=num(52);
    icon.visual.visualContainerObjects.background=[{properties:{show:lit(false)}}];
    icon.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];
    icon.visual.visualContainerObjects.padding=[{properties:{top:num(0),bottom:num(0),left:num(0),right:num(0)}}];
    icon.visual.visualContainerObjects.visualLink=JSON.parse(JSON.stringify(c.visualLink));
    for(const link of icon.visual.visualContainerObjects.visualLink||[])Object.assign(link.properties,{suppressDefaultTooltip:lit(true),showDefaultTooltip:lit(false)});
    icon.visual.visualContainerObjects.visualTooltip=[{properties:{show:lit(false)}}];
    icon.visual.visualContainerObjects.general=[{properties:{altText:lit('Öppna '+['Hem','Ledningsöversikt','Lönsamhet','Försäljningsanalys','Transaktioner'][navIndex])}}];
    const iconDir=path.join(dir,'visuals',icon.name);fs.mkdirSync(iconDir,{recursive:true});write(path.join(iconDir,'visual.json'),icon);
   }
   for(const state of o.text||[])if(state.selector?.id==='hover')state.properties.fontColor=color('#0F3163');
   for(const state of o.text||[])if(state.properties.text?.expr?.Literal)state.properties.text.expr.Literal.Value=state.properties.text.expr.Literal.Value.replaceAll('Ekonomi och lönsamhet','Lönsamhet');
   for(const link of c.visualLink||[])Object.assign(link.properties,{suppressDefaultTooltip:lit(true),showDefaultTooltip:lit(false),enabledTooltip:lit(''),tooltip:lit('')});
   c.visualTooltip=[{properties:{show:lit(false)}}];
  }
  if(entry===id(page+':logo')){
   const name=`AubecoLogo-${pi===0?'orange':'blue'}.svg`;
   o.image[0].properties.sourceFile={image:{name:lit(name),url:{expr:{ResourcePackageItem:{PackageName:'RegisteredResources',PackageType:1,ItemName:name}}},scaling:lit('Fit')}};
   c.background=[{properties:{show:lit(false)}}];c.general=[{properties:{altText:lit('Aubeco')}}];
  }
  if(entry===id(page+':title')&&pi===0){const run=o.general[0].properties.paragraphs[0].textRuns[0];run.value='Verksamhetsöversikt';run.textStyle.color='#FFFFFF';}
  if(pi===0){
   const homeIconIndex=[0,1,2,3].find(n=>entry===id(page+':icon'+n));
   if(homeIconIndex!==undefined){
    const label=read(path.join(dir,'visuals',id(page+':tag'+homeIconIndex),'visual.json'));
    Object.assign(v.position,{x:label.position.x,y:416,width:56,height:56});
    const zero={expr:{Literal:{Value:'0D'}}};
    c.padding=[{properties:{top:zero,bottom:zero,left:zero,right:zero}}];
   }
  }
  if(pi===0&&entry===id(page+':intro'))for(const paragraph of o.general[0].properties.paragraphs)for(const run of paragraph.textRuns)run.textStyle.color='#DCE8F5';
  if(pi===0&&entry===id(page+':refresh')){
   const num=n=>({expr:{Literal:{Value:n+'D'}}});
   for(const state of o.value||[])Object.assign(state.properties,{fontColor:color('#DCE8F5'),fontFamily:lit('Segoe UI'),bold:lit(false),textWrap:lit(false),horizontalAlignment:lit('right')});
   c.background=[{properties:{show:lit(false)}}];
   c.border=[{properties:{show:lit(false)}}];
   c.visualHeader=[{properties:{show:lit(false)}}];
   for(const object of ['fillCustom','outline'])o[object]=[{properties:{show:lit(false)}},{selector:{id:'default'},properties:{show:lit(false)}}];
   o.layout=[{properties:{backgroundShow:lit(false),backgroundTransparency:num(100),cellPadding:num(0)}},{selector:{id:'default'},properties:{backgroundShow:lit(false),backgroundTransparency:num(100)}}];
   o.cardCalloutArea=[{properties:{show:lit(false),backgroundTransparency:num(100)}}];
   c.padding=[{properties:{top:num(0),bottom:num(0),left:num(0),right:num(0)}}];
  }
  if(pi===0){
   // Absolute coordinates make repeated application safe.
   const contentY={title:192,intro:280};
   for(let n=0;n<4;n++)Object.assign(contentY,{['panel'+n]:384,['icon'+n]:416,['tag'+n]:504,['area'+n]:548,['description'+n]:612,['open'+n]:696});
   const contentKey=Object.keys(contentY).find(key=>entry===id(page+':'+key));
   if(contentKey!==undefined)v.position.y=contentY[contentKey]+80;
  }
  write(f,v);
 }
});
// The user removed the homepage benefit strip; keep it removed on regeneration.
for(const key of ['footer-panel',...[0,1,2,3].flatMap(n=>['benefit'+n,'benefitdesc'+n,'benefit-icon'+n])]){
 const target=path.join(report,'definition/pages',pages[0],'visuals',id(pages[0]+':'+key));
 const f=path.join(target,'visual.json');if(fs.existsSync(f))fs.unlinkSync(f);
 if(fs.existsSync(target)&&fs.readdirSync(target).length===0)fs.rmdirSync(target);
}
write(rfile,r);
console.log('Applied supplied SVG logos, blue homepage, brighter accents and suppressed navigation tooltips.');
