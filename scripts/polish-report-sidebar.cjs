// Shared navigation treatment for the three analysis pages. No model/data edits.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const report=path.resolve(__dirname,'../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?`${v}D`:"'"+v.replace(/'/g,"''")+"'"}}});
const color=c=>({solid:{color:lit(c)}});
const resource=name=>({expr:{ResourcePackageItem:{PackageName:'RegisteredResources',PackageType:1,ItemName:name}}});
function icon(kind,ink){const name=`navigation-${kind}-${ink.slice(1)}.png`;return{image:{name:lit(name),url:resource(name),scaling:lit('Fit')}};}
function decorate(page,key,label,box,ink='#708198',size=10.5,back=null){
 const name=crypto.createHash('sha256').update('report-sidebar:'+page+':'+key).digest('hex').slice(0,20);
 const v={$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json',name,position:{x:box[0],y:box[1],width:box[2],height:box[3],z:180,tabOrder:180},visual:{visualType:'textbox',objects:{general:[{properties:{paragraphs:[{textRuns:[{value:label,textStyle:{fontFamily:'Segoe UI Semibold',fontSize:size+'pt',color:ink}}],horizontalTextAlignment:'left'}]}}]},visualContainerObjects:{background:[{properties:{show:lit(!!back),color:color(back||'#FFFFFF'),transparency:lit(0)}}],border:[{properties:{show:lit(false)}}],padding:[{properties:{top:lit(0),bottom:lit(0),left:lit(0),right:lit(0)}}],general:[{properties:{altText:lit(label||'Avdelare')}}]}}};
 const dir=path.join(report,'definition/pages',page,'visuals',name);fs.mkdirSync(dir,{recursive:true});fs.writeFileSync(path.join(dir,'visual.json'),JSON.stringify(v,null,2)+'\n');
}
function polish(){
 const reportFile=path.join(report,'definition/report.json'), definition=read(reportFile);
 const resources=definition.resourcePackages.find(p=>p.name==='RegisteredResources');
 const logo='AubecoLogoBlue202610140002.svg';
 fs.copyFileSync(path.resolve(__dirname,'../assets/aubeco/AubecoLogo-blue.svg'),path.join(report,'StaticResources/RegisteredResources',logo));
 if(!resources.items.some(r=>r.name===logo))resources.items.push({name:logo,path:logo,type:'Image'});
 for(const name of fs.readdirSync(path.join(report,'StaticResources/RegisteredResources')).filter(n=>n.startsWith('navigation-')&&n.endsWith('.png'))){if(!resources.items.some(r=>r.name===name))resources.items.push({name,path:name,type:'Image'});}
 fs.writeFileSync(reportFile,JSON.stringify(definition,null,2)+'\n');
 const meta=read(path.join(report,'definition/pages/pages.json')),home=meta.pageOrder[0];
 const targets=[meta.pageOrder[1],meta.pageOrder[2],meta.pageOrder[3]];
 const rows=[{label:'Start',kind:'home',y:24,h:48,target:home},{label:'Ledningsöversikt',kind:'overview',y:156,h:56,target:targets[0]},{label:'Försäljningsöversikt',kind:'sales',y:224,h:56,target:targets[1]},{label:'Kunder',kind:'customers',y:292,h:56,target:targets[2]},{label:'Budget',kind:'budget',y:360,h:56},{label:'Projekt / beläggning',kind:'projects',y:428,h:56}];
 let count=0;
 for(const page of targets.filter(Boolean)){
  const dir=path.join(report,'definition/pages',page,'visuals');let updated=0;
  for(const name of fs.readdirSync(dir)){
   const file=path.join(dir,name,'visual.json');if(!fs.existsSync(file))continue;
   const v=read(file);
   if(v.visual.visualType==='textbox'&&v.position.x===0&&v.position.width===272&&v.position.height===1200){
    v.visual.visualContainerObjects.background=[{properties:{show:lit(true),color:color('#FFFFFF'),transparency:lit(0)}}];
    v.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];v.visual.visualContainerObjects.dropShadow=[{properties:{show:lit(false)}}];
    fs.writeFileSync(file,JSON.stringify(v,null,2)+'\n');continue;
   }
   if(!['actionButton','image'].includes(v.visual.visualType)||v.position.x>=50)continue;
   const raw=(v.visual.objects.text||[]).map(x=>x.properties?.text?.expr?.Literal?.Value||'').join(' ');
   const row=v.visual.visualType==='image'&&v.position.y===24?rows[0]:rows.find(r=>r.label==='Start'?raw.includes('Start'):raw.includes(r.label));if(!row)continue;
   const active=row.target===page,disabled=!row.target,isHome=row.kind==='home';
   Object.assign(v.position,{x:16,y:row.y,width:240,height:row.h,z:200+rows.indexOf(row),tabOrder:200+rows.indexOf(row)});
   if(isHome){
    Object.assign(v.position,{x:32,width:208,height:64});
    v.visual={visualType:'image',objects:{image:[{properties:{sourceType:lit('image'),sourceFile:{image:{name:lit(logo),url:resource(logo),scaling:lit('Fit')}},fit:lit('Fit'),altText:lit('Aubeco – till startsidan'),strokeShow:lit(false),backgroundEnabled:lit(false)}}]},visualContainerObjects:{background:[{properties:{show:lit(false)}}],border:[{properties:{show:lit(false)}}],padding:[{properties:{top:lit(10),bottom:lit(10),left:lit(20),right:lit(20)}}],general:[{properties:{altText:lit('Aubeco – till startsidan')}}],visualLink:[{properties:{show:lit(true),type:lit('PageNavigation'),navigationSection:lit(home)}}]}};
    fs.writeFileSync(file,JSON.stringify(v,null,2)+'\n');updated++;count++;continue;
   }
   const states=['default','hover','selected','disabled'];
   const ink=state=>active?'#FFFFFF':'#0F3163';
   const fill=state=>active?(state==='hover'?'#173F76':'#0F3163'):state==='hover'&&!disabled?'#E6EDF6':isHome?'#FFFFFF':'#F2F5F9';
   v.visual.objects.text=[{properties:{show:lit(false)}},...states.map(state=>({selector:{id:state},properties:{text:lit(row.label),fontFamily:lit(active?'Segoe UI Semibold':'Segoe UI'),fontSize:lit(12),bold:lit(false),fontColor:color(ink(state)),horizontalAlignment:lit('left'),leftMargin:lit(52),rightMargin:lit(8),topMargin:lit(0),bottomMargin:lit(0)}}))];
   v.visual.objects.fill=[{properties:{show:lit(true)}},...states.map(state=>({selector:{id:state},properties:{fillColor:color(fill(state)),transparency:lit(0)}}))];
   v.visual.objects.icon=[{properties:{show:lit(false)}},...states.map(state=>({selector:{id:state},properties:{shapeType:lit('custom'),image:icon(row.kind,ink(state)),placement:lit('left'),horizontalAlignment:lit('left'),verticalAlignment:lit('middle'),leftMargin:lit(16),rightMargin:lit(0),topMargin:lit(0),bottomMargin:lit(0),iconSize:lit(22)}}))];
   v.visual.objects.shape=[{properties:{tileShape:lit('rectangleRounded'),roundEdge:{expr:{Literal:{Value:'6L'}}}}},{selector:{id:'default'},properties:{tileShape:lit('rectangleRounded')}}];
   v.visual.objects.outline=[{properties:{show:lit(false)}}];
   v.visual.visualContainerObjects.background=[{properties:{show:lit(false)}}];
   v.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];
   v.visual.visualContainerObjects.general=[{properties:{altText:lit(row.label+(active?' – aktiv sida':'')),keepLayerOrder:lit(true)}}];
   v.visual.visualContainerObjects.visualLink=[{properties:row.target?{show:lit(true),type:lit('PageNavigation'),navigationSection:lit(row.target)}:{show:lit(false)}}];
   fs.writeFileSync(file,JSON.stringify(v,null,2)+'\n');updated++;count++;
   // Explicit columns keep icon and text aligned independently of button auto-layout.
   const labelKey='label-'+row.kind;
   decorate(page,labelKey,row.label,[76,row.y+14,172,32],ink('default'),12);
   const labelName=crypto.createHash('sha256').update('report-sidebar:'+page+':'+labelKey).digest('hex').slice(0,20);
   const labelFile=path.join(dir,labelName,'visual.json'), labelVisual=read(labelFile);
   labelVisual.position.z=400;labelVisual.visual.visualContainerObjects.visualLink=v.visual.visualContainerObjects.visualLink;
   labelVisual.visual.objects.general[0].properties.paragraphs[0].textRuns[0].textStyle.fontFamily=active?'Segoe UI Semibold':'Segoe UI';
   fs.writeFileSync(labelFile,JSON.stringify(labelVisual,null,2)+'\n');
   const imageName=crypto.createHash('sha256').update('report-sidebar:'+page+':icon-'+row.kind).digest('hex').slice(0,20);
   const imageDir=path.join(dir,imageName);fs.mkdirSync(imageDir,{recursive:true});
   const imageVisual={$schema:v.$schema,name:imageName,position:{x:36,y:row.y+16,width:24,height:24,z:400,tabOrder:400},visual:{visualType:'image',objects:{image:[{properties:{sourceType:lit('image'),sourceFile:icon(row.kind,ink('default')),fit:lit('Fit'),strokeShow:lit(false),backgroundEnabled:lit(false)}}]},visualContainerObjects:{background:[{properties:{show:lit(false)}}],border:[{properties:{show:lit(false)}}],padding:[{properties:{top:lit(0),bottom:lit(0),left:lit(0),right:lit(0)}}],visualLink:v.visual.visualContainerObjects.visualLink,general:[{properties:{altText:lit(row.label)}}]}}};
   fs.writeFileSync(path.join(imageDir,'visual.json'),JSON.stringify(imageVisual,null,2)+'\n');
  }
  if(updated!==6)throw Error(`Expected six sidebar buttons on ${page}; found ${updated}`);
  decorate(page,'reports','RAPPORTER',[32,112,224,26]);
  for(const key of ['divider','upcoming','footer-divider']){
   const name=crypto.createHash('sha256').update('report-sidebar:'+page+':'+key).digest('hex').slice(0,20);
   const file=path.join(dir,name,'visual.json');
   if(fs.existsSync(file))fs.unlinkSync(file);
   if(fs.existsSync(path.join(dir,name)))fs.rmdirSync(path.join(dir,name));
  }
  decorate(page,'footer-title','Verksamhet & ekonomi',[32,1100,224,30],'#0F3163',11.5);
  decorate(page,'footer-detail','Rapportöversikt',[32,1136,224,24]);
 }
 console.log(`Polished ${count} sidebar buttons across ${targets.filter(Boolean).length} analysis pages.`);
}
module.exports=polish;
if(require.main===module)polish();
