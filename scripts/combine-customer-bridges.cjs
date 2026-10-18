// Move both existing bridges into one card; bookmarks change display only.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const report=path.resolve(__dirname,'../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report');
const page='f429b020315c602ce0ed',dir=path.join(report,'definition/pages',page,'visuals');
const hash=s=>crypto.createHash('sha256').update(s).digest('hex').slice(0,20);
const id=k=>hash('customer-page:'+page+':'+k),bookmark=i=>hash('customer-bridge-view:'+i);
const read=f=>JSON.parse(fs.readFileSync(f,'utf8').replace(/^\uFEFF/,''));
const write=(f,v)=>fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n');
const file=k=>path.join(dir,id(k),'visual.json');
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?v+'D':"'"+v.replace(/'/g,"''")+"'"}}});
const color=c=>({solid:{color:lit(c)}});
const groups=[];
for(const [index,prefix]of ['base','revenue'].entries()){
 const keys=[prefix+'-title',prefix+'-bridge',prefix+'-summary'];groups.push(keys.map(id));
 for(const key of keys){
  const v=read(file(key));v.isHidden=index===1;
  if(key.endsWith('-title')){
   Object.assign(v.position,{x:1126,y:376,width:380,height:40});
   const p=v.visual.objects.general[0].properties.paragraphs;
   p[0].textRuns[0].value=index===0?'Kundbasens förändring':'Försäljningens förändring';
   for(const para of p)for(const run of para.textRuns)run.textStyle.fontSize='18pt';
  }else if(key.endsWith('-bridge'))Object.assign(v.position,{x:1126,y:432,width:750,height:280});
  else Object.assign(v.position,{x:1126,y:728,width:750,height:32});
  write(file(key),v);
 }
}
const template=read(file('mode-0-0')),buttons=[];
for(let active=0;active<2;active++)for(let choice=0;choice<2;choice++){
 const v=structuredClone(template),selected=active===choice;
 v.name=hash('customer-bridge-button:'+active+':'+choice);buttons.push({name:v.name,active});
 v.isHidden=active!==0;delete v.filterConfig;
 Object.assign(v.position,{x:1516+choice*182,y:376,width:178,height:40,z:500,tabOrder:500+choice});
 v.visual.objects={text:[{properties:{show:lit(true)}},...['default','hover','selected'].map(state=>({selector:{id:state},properties:{text:lit(choice===0?'Antal kunder':'Försäljning'),fontFamily:lit(selected?'Segoe UI Semibold':'Segoe UI'),fontSize:lit(11),fontColor:color(selected?'#FFFFFF':'#0F3163'),horizontalAlignment:lit('center'),verticalAlignment:lit('middle')}}))],fill:[{properties:{show:lit(true)}},...['default','hover','selected'].map(state=>({selector:{id:state},properties:{fillColor:color(selected?'#0F3163':state==='hover'?'#E6EDF6':'#EEF2F7'),transparency:lit(0)}}))],outline:[{properties:{show:lit(false)}}],icon:[{properties:{show:lit(false)}}],shape:[{properties:{tileShape:lit('rectangleRounded'),roundEdge:{expr:{Literal:{Value:'4L'}}}}}]};
 v.visual.visualContainerObjects.visualLink=[{properties:{show:lit(true),type:lit('Bookmark'),bookmark:lit(bookmark(choice))}}];
 v.visual.visualContainerObjects.general=[{properties:{altText:lit(choice===0?'Visa kundbasens förändring i antal kunder':'Visa försäljningsförändringen i miljoner kronor')}}];
 const out=path.join(dir,v.name);fs.mkdirSync(out,{recursive:true});write(path.join(out,'visual.json'),v);
}
const bookmarks=path.join(report,'definition/bookmarks');
const targetVisualNames=[...groups.flat(),...buttons.map(b=>b.name)];
for(let active=0;active<2;active++){
 const containers={};
 groups.forEach((names,index)=>names.forEach(name=>containers[name]={singleVisual:index===active?{}:{display:{mode:'hidden'}}}));
 buttons.forEach(b=>containers[b.name]={singleVisual:b.active===active?{}:{display:{mode:'hidden'}}});
 write(path.join(bookmarks,bookmark(active)+'.bookmark.json'),{$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/bookmark/2.1.0/schema.json',name:bookmark(active),displayName:'Kunder – '+(active===0?'Antal kunder':'Försäljning'),options:{targetVisualNames,suppressData:true,suppressDisplay:false,suppressActiveSection:true,applyOnlyToTargetVisuals:true},explorationState:{version:'1.3',activeSection:page,sections:{[page]:{visualContainers:containers}}}});
}
const indexFile=path.join(bookmarks,'bookmarks.json'),index=read(indexFile);
index.items=index.items.filter(b=>![bookmark(0),bookmark(1)].includes(b.name));index.items.push({name:bookmark(0)},{name:bookmark(1)});write(indexFile,index);
// The former lower-left card is genuinely free, without an invented replacement.
const panel=file('revenue-panel');if(fs.existsSync(panel))fs.unlinkSync(panel);
const panelDir=path.dirname(panel);if(fs.existsSync(panelDir)&&fs.readdirSync(panelDir).length===0)fs.rmdirSync(panelDir);
const pageFile=path.join(report,'definition/pages',page,'page.json'),p=read(pageFile);
p.visualInteractions=(p.visualInteractions||[]).filter(x=>x.source!==id('revenue-panel')&&x.target!==id('revenue-panel'));write(pageFile,p);
console.log('Combined both customer bridges with display-only bookmarks; lower-left area is free.');
