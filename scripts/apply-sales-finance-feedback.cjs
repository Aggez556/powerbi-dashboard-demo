// Applied after the main builder, so feedback survives report regeneration.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const base=path.resolve(__dirname,'../powerbi-sales-finance'),report=path.join(base,'AubecoSalesFinance.Report');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const write=(p,v)=>fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?`${v}D`:`'${v}'`}}});
const color=c=>({solid:{color:lit(c)}}),id=s=>crypto.createHash('sha256').update(s).digest('hex').slice(0,20);
const pages=read(path.join(report,'definition/pages/pages.json')).pageOrder;
const res=path.join(report,'StaticResources/RegisteredResources'),rfile=path.join(report,'definition/report.json'),r=read(rfile);
const pack=r.resourcePackages.find(p=>p.name==='RegisteredResources');
const strokes=['<path d="M16 32L32 18l16 14v16H21V32M28 48V36h8v12"/>','<rect x="18" y="18" width="11" height="11" rx="2"/><rect x="35" y="18" width="11" height="11" rx="2"/><rect x="18" y="35" width="11" height="11" rx="2"/><rect x="35" y="35" width="11" height="11" rx="2"/>','<path d="M20 44V30M32 44V20M44 44V26"/>','<path d="M18 44l12-12 8 5 10-17M37 20h11v11"/>','<rect x="21" y="17" width="22" height="30" rx="3"/><path d="M27 25h10M27 32h10M27 39h6"/>'];
const inks=['#6755C8','#008A83','#BD610A','#3275CD'],tints=['#EFEBFF','#E2F6F2','#FFF0E2','#E8F1FF'];
function svg(name,body,ink,back){fs.writeFileSync(path.join(res,name),`<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">${back?`<rect width="64" height="64" rx="16" fill="${back}"/>`:''}<g fill="none" stroke="${ink}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">${body}</g></svg>`);if(!pack.items.some(x=>x.name===name))pack.items.push({name,path:name,type:'Image'});}
function img(name){return {name:lit(name),url:{expr:{ResourcePackageItem:{PackageName:'RegisteredResources',PackageType:1,ItemName:name}}},scaling:lit('Fit')};}
for(let i=0;i<5;i++)for(const state of ['default','selected','hover'])svg(`Nav${i}-${state}.svg`,strokes[i],state==='selected'?'#0F3163':state==='hover'?'#FFFFFF':'#0F3163');
for(let i=0;i<4;i++)svg(`HomeArea${i}.svg`,strokes[i+1],inks[i],tints[i]);
const benefitPaths=['<circle cx="32" cy="32" r="14"/><circle cx="32" cy="32" r="6"/><path d="M32 14v6M46 32h6"/>','<path d="M32 16l14 6v12c0 8-14 15-14 15S18 42 18 34V22zM25 32l5 5 10-11"/>',strokes[3],'<circle cx="32" cy="32" r="16"/><path d="M32 22v11l8 5"/>'];
benefitPaths.forEach((s,i)=>svg(`Benefit${i}.svg`,s,inks[0],tints[0]));
for(let pi=0;pi<pages.length;pi++){
 const page=pages[pi],dir=path.join(report,'definition/pages',page,'visuals');
 const file=key=>path.join(dir,id(page+':'+key),'visual.json');
 function get(key){return read(file(key));}function put(key,v){const p=file(key);fs.mkdirSync(path.dirname(p),{recursive:true});write(p,v);}
 function image(key,name,box){const v=get(pi===0?'logo':'logo');v.name=id(page+':'+key);v.position={x:box[0],y:box[1],width:box[2],height:box[3],z:900,tabOrder:900};v.visual.objects.image[0].properties.sourceFile={image:img(name)};v.visual.visualContainerObjects.background=[{properties:{show:lit(false)}}];put(key,v);}
 if(pi>0)for(let n=0;n<5;n++){
  const key='nav'+n,v=get(key),o=v.visual.objects;
  v.position.x=12;v.position.width=264;v.position.height=56;
  const selected=pi===n;
  o.text[1].properties.text=lit(['Hem','Ledningsöversikt','Ekonomi och lönsamhet','Försäljningsanalys','Transaktioner'][n]);
  Object.assign(o.text[1].properties,{fontSize:lit(13),fontFamily:lit('Segoe UI Semibold'),horizontalAlignment:lit('left'),leftMargin:lit(42),rightMargin:lit(6),fontColor:color('#0F3163')});
  o.shape=[{properties:{tileShape:lit('pill')}},{selector:{id:'default'},properties:{tileShape:lit('pill')}}];
  o.fill[1].properties.fillColor=color(selected?'#F7BA6B':'#FFFFFF');o.fill[2].properties.fillColor=color('#BD610A');
  o.icon=[{properties:{show:lit(true),placement:lit('left')}},...['default','hover'].map(state=>({selector:{id:state},properties:{shapeType:lit('custom'),image:img(`Nav${n}-${state==='default'&&selected?'selected':state}.svg`),iconSize:lit(28),placement:lit('left'),leftMargin:lit(8),rightMargin:lit(6)}}))];put(key,v);
 }
 for(const entry of fs.readdirSync(dir)){
  const p=path.join(dir,entry,'visual.json');if(!fs.existsSync(p))continue;let v=read(p);
  // Stronger semantic colors, preserving the existing comparison rules.
  v=JSON.parse(JSON.stringify(v).replaceAll('#187447','#078A36').replaceAll('#B83232','#D92D20'));
  const o=v.visual.objects||{};
  if(pi===1&&entry===id(page+':trend'))o.dataPoint=[
   {selector:{metadata:'Försäljning.Trendvärde'},properties:{fill:color('#BD610A')}},
   {selector:{metadata:'Försäljning.Trend föregående år'},properties:{fill:color('#D7DFEA')}}
  ];
  if(entry===id(page+':trend-legend')||entry===id(page+':sales-legend')){
   for(const paragraph of o.general?.[0]?.properties.paragraphs||[])for(const run of paragraph.textRuns||[])
    if(run.value.includes('● Aktuellt år')||run.value.includes('● Omsättning'))run.textStyle.color='#BD610A';
  }
  if(entry===id(page+':trend-legend-prior'))for(const paragraph of o.general[0].properties.paragraphs)for(const run of paragraph.textRuns)run.textStyle.color='#D7DFEA';
  for(const dp of o.dataPoint||[])for(const prop of ['fill','defaultColor']){
   const value=dp.properties[prop]?.solid?.color?.expr?.Literal;
   if(value?.Value==="'#0F3163'")value.Value="'#BD610A'";
  }
  if(v.visual.visualType==='scatterChart')o.fillPoint=[{properties:{style:lit('Fill only')}}];
  for(let n=0;n<5;n++){
   if(entry===id(page+':yoy-label'+n)){v.position.width=112;v.position.height=28;o.general[0].properties.paragraphs[0].textRuns[0].textStyle.fontSize='11pt';}
   if(entry===id(page+':yoy'+n)){v.position.x=320+n*312+146;v.position.width=118;v.position.height=28;o.value[0].properties.fontSize=lit(12);}
   if(entry===id(page+':kpi-change'+n)){o.value[0].properties.fontSize=lit(12);v.position.height=28;}
  }
  write(p,v);
 }
 // Refresh metadata uses a disconnected Import table, unaffected by slicers.
 const v=get(pi===0?'title':'suite-title');v.name=id(page+':refresh');v.position={x:1480,y:30,width:400,height:48,z:950,tabOrder:950};
 v.visual.visualType='cardVisual';v.visual.query={queryState:{Data:{projections:[{field:{Measure:{Expression:{SourceRef:{Entity:'Rapportstatus'}},Property:'Senast uppdaterad'}},queryRef:'Rapportstatus.Senast uppdaterad',nativeQueryRef:'Senast uppdaterad'}]}}};
 v.visual.objects={value:[{selector:{id:'default'},properties:{fontSize:lit(11),fontFamily:lit('Segoe UI'),fontColor:color('#5B6B80'),horizontalAlignment:lit('right'),showBlankAs:lit('Uppdatera data för tidsstämpel')}}],label:[{selector:{id:'default'},properties:{show:lit(false)}}],outline:[{selector:{id:'default'},properties:{show:lit(false)}}],fillCustom:[{selector:{id:'default'},properties:{show:lit(false)}}],padding:[{selector:{id:'default'},properties:{paddingUniform:lit(0)}}]};put('refresh',v);
 if(pi===0){
  for(let n=0;n<4;n++){
   image('icon'+n,`HomeArea${n}.svg`,[96+n*454,416,64,64]);
   const old=file('icon'+n+'-panel');if(fs.existsSync(old))fs.unlinkSync(old);if(fs.existsSync(path.dirname(old))&&fs.readdirSync(path.dirname(old)).length===0)fs.rmdirSync(path.dirname(old));
   const heading=get('area'+n);Object.assign(heading.visual.objects.general[0].properties.paragraphs[0].textRuns[0].textStyle,{fontFamily:'Segoe UI',fontWeight:'bold'});put('area'+n,heading);
   const tag=get('tag'+n);tag.visual.objects.general[0].properties.paragraphs[0].textRuns[0].textStyle.color=inks[n];put('tag'+n,tag);
   const b=get('open'+n);b.visual.objects.shape=[{properties:{tileShape:lit('pill')}}];b.visual.objects.fill[2].properties.fillColor=color('#BD610A');put('open'+n,b);
   image('benefit-icon'+n,`Benefit${n}.svg`,[88+n*448,950,56,56]);
   for(const [key,size,y] of [['benefit',13,946],['benefitdesc',10,986]]){const t=get(key+n);t.position.x=160+n*448;t.position.width=336;t.position.y=y;t.visual.objects.general[0].properties.paragraphs[0].textRuns[0].textStyle.fontSize=size+'pt';put(key+n,t);}
  }
 }
}
write(rfile,r);
require('./apply-sales-finance-brand.cjs');
const layoutFile=path.join(base,'validation/layout.json'),layout=read(layoutFile);
layout.placements=pages.flatMap(page=>{const dir=path.join(report,'definition/pages',page,'visuals');return fs.readdirSync(dir).flatMap(name=>{const p=path.join(dir,name,'visual.json');if(!fs.existsSync(p))return [];const v=read(p),old=layout.placements.find(x=>x.page===page&&id(page+':'+x.key)===v.name);return [{page,key:old?.key||v.name,type:v.visual.visualType,box:[v.position.x,v.position.y,v.position.width,v.position.height],fields:Object.values(v.visual.query?.queryState||{}).flatMap(x=>x.projections.map(p=>p.field))}];});});write(layoutFile,layout);
console.log('Applied navigation, icons, accents, readable changes and refresh status to five pages.');
