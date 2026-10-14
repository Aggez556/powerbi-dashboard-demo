// Embed the website's exported wordmark as a local registered image on all pages.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),report=path.join(root,'powerbi/AubecoHandel.Report');
const id=s=>crypto.createHash('sha256').update(s).digest('hex').slice(0,20);
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const write=(p,o)=>{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(o,null,2)+'\n');};
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?`${v}D`:`'${v.replace(/'/g,"''")}'`}}});
const color=c=>({solid:{color:lit(c)}}),name='AubecoHeaderWordmark202610070001.png';
const source=path.join(root,'assets/aubeco/aubeco-header-wordmark.png');
if(!fs.existsSync(source))throw Error('Run fetch-aubeco-logo.cjs first.');
fs.copyFileSync(source,path.join(report,'StaticResources/RegisteredResources',name));
const reportPath=path.join(report,'definition/report.json'),r=read(reportPath);
let pkg=r.resourcePackages.find(x=>x.name==='RegisteredResources');
if(!pkg){pkg={name:'RegisteredResources',type:'RegisteredResources',items:[]};r.resourcePackages.push(pkg);}
if(!pkg.items.some(x=>x.name===name))pkg.items.push({name,path:name,type:'Image'});
write(reportPath,r);
const result=[];
for(const pageId of read(path.join(report,'definition/pages/pages.json')).pageOrder){
 const dir=path.join(report,'definition/pages',pageId),page=read(path.join(dir,'page.json'));
 const paths=fs.readdirSync(path.join(dir,'visuals')).map(v=>path.join(dir,'visuals',v,'visual.json'));
 const before=Object.fromEntries(paths.filter(p=>{const t=read(p).visual.visualType;return !['textbox','image'].includes(t);}).map(p=>[p,fs.readFileSync(p,'utf8')]));
 const budget=page.displayName==='Budgetplanering';
 const titlePath=paths.find(p=>read(p).name===id(budget?pageId+':brand':pageId+':page_title'));
 if(titlePath){
  const title=read(titlePath);
  if(budget){title.position.y=148;title.position.height=180;title.visual.objects.general[0].properties.paragraphs=[{textRuns:[{value:'Budget-',textStyle:{fontFamily:'Segoe UI Semibold',fontSize:'24pt',color:'#0F3163'}}],horizontalTextAlignment:'left'},{textRuns:[{value:'planering',textStyle:{fontFamily:'Segoe UI Semibold',fontSize:'24pt',color:'#0F3163'}}],horizontalTextAlignment:'left'}];}
  else{title.position.x=240;title.position.width=976;for(const p of title.visual.objects.general[0].properties.paragraphs)for(const run of p.textRuns)run.value=run.value.replace(' · Aubeco Handel','');}
  write(titlePath,title);
 }
 const visualName=id(pageId+':official-aubeco-logo'),box=budget?[28,28,272,104]:[32,24,208,88];
 const resource={expr:{ResourcePackageItem:{PackageName:'RegisteredResources',PackageType:1,ItemName:name}}};
 const image={$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json',name:visualName,position:{x:box[0],y:box[1],width:box[2],height:box[3],z:100,tabOrder:100},visual:{visualType:'image',objects:{image:[{properties:{sourceType:lit('image'),sourceFile:{image:{name:lit('Aubeco – webbens ordmärke'),url:resource,scaling:lit('Fit')}},fit:lit('Fit'),altText:lit('Aubeco logotyp'),strokeShow:lit(false),backgroundEnabled:lit(false)}}]},visualContainerObjects:{title:[{properties:{show:lit(false)}}],background:[{properties:{show:lit(true),color:color('#09224A'),transparency:lit(0)}}],border:[{properties:{show:lit(false)}}],padding:[{properties:{top:lit(12),bottom:lit(12),left:lit(16),right:lit(16)}}],general:[{properties:{altText:lit('Aubeco – logotyp från aubeco.se')}}]}}};
 write(path.join(dir,'visuals',visualName,'visual.json'),image);
 for(const [p,content] of Object.entries(before))if(fs.readFileSync(p,'utf8')!==content)throw Error('Data visual changed: '+p);
 result.push({page:page.displayName,visual:visualName,box,dataVisualsUnchanged:true});
}
write(path.join(root,'powerbi/validation/logo-result.json'),{status:'files-updated',source:'https://www.aubeco.se/',asset:'assets/aubeco/aubeco-header-wordmark.png',resource:name,localEmbeddedResource:true,preserveAspectRatio:true,pages:result,desktopRendering:'pending'});
console.log(`Embedded Aubeco wordmark on ${result.length} pages; data visuals unchanged.`);
