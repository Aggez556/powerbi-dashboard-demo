// Embed the supplied original logo and preserve existing navigation and aspect ratio.
const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..');
const report=path.join(root,'powerbi-ledningsrapport/LedningsrapportUtanScroll.Report');
const name='DemobolagetBlue.png',old='AubecoLogoBlue202610140002.svg';
const asset=path.join(root,'assets/demobolaget',name);
fs.mkdirSync(path.dirname(asset),{recursive:true});
if(process.argv[2])fs.copyFileSync(process.argv[2],asset);
fs.copyFileSync(asset,path.join(report,'StaticResources/RegisteredResources',name));
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const write=(p,v)=>fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');
const f=path.join(report,'definition/report.json'),r=read(f);
const pkg=r.resourcePackages.find(x=>x.name==='RegisteredResources');
if(!pkg.items.some(x=>x.name===name))pkg.items.push({name,path:name,type:'Image'});
write(f,r);
let count=0;
for(const page of fs.readdirSync(path.join(report,'definition/pages'))){
 const dir=path.join(report,'definition/pages',page,'visuals');if(!fs.existsSync(dir))continue;
 for(const key of fs.readdirSync(dir)){
  const file=path.join(dir,key,'visual.json');if(!fs.existsSync(file))continue;
  const source=fs.readFileSync(file,'utf8');
  if(!source.includes(old)&&!source.includes(name))continue;
  const v=JSON.parse(source.replaceAll(old,name).replaceAll('Aubeco','Demobolaget'));
  const home=page==='6ff94a05bddfe7036ec7';
  Object.assign(v.position,home?{x:1536,y:40,width:320,height:112}:{x:20,y:14,width:232,height:90});
  for(const entry of v.visual.visualContainerObjects.padding||[])
   for(const property of Object.values(entry.properties))property.expr.Literal.Value='0D';
  write(file,v);count++;
 }
}
console.log(`Updated ${count} logo visuals with the original PNG.`);
