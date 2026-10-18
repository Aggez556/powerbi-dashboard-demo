// Final, idempotent formatting pass. Never modifies queries, interactions or model data.
const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'../powerbi-ledningsrapport');
const pages=path.join(root,'LedningsrapportUtanScroll.Report/definition/pages');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8').replace(/^\uFEFF/,''));
const write=(f,v)=>fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n');
const palette={'#405572':'#5B6B80','#70839A':'#708198'};
const audit={rules:{pageTitle:30,panelTitle:18,kpiLabel:13,legend:11,font:'Segoe UI',primary:'#0F3163',secondary:'#5B6B80',positive:'#007956',negative:'#B42318'},pages:[]};
for(const id of read(path.join(pages,'pages.json')).pageOrder){
 const folder=path.join(pages,id),page=read(path.join(folder,'page.json'));
 const home=page.displayName==='Start',changes=[];
 for(const key of fs.readdirSync(path.join(folder,'visuals'))){
  const f=path.join(folder,'visuals',key,'visual.json');if(!fs.existsSync(f))continue;
  const v=read(f),before=JSON.stringify(v),notes=new Set();
  const runs=(v.visual.objects?.general?.[0]?.properties?.paragraphs||[]).flatMap(p=>p.textRuns||[]);
  const label=runs.map(r=>r.value).join('');
  if(label){
   for(const run of runs){
    const s=run.textStyle;if(!s)continue;const n=parseFloat(s.fontSize);
    let next=n;
    if(!home&&v.position.x>=272){
     if(n===29)next=30;
     if([19,23].includes(n))next=18;
     if(n===13.5||(page.displayName==='Budget'&&n===16))next=13;
     if(n===13.75||label.includes('●')||/^— Mål/.test(label))next=11;
    }
    if(home&&label==='Omsättning, lönsamhet,uppdrag och kunder.')run.value='Omsättning, lönsamhet, uppdrag och kunder.';
    if(next!==n){s.fontSize=next+'pt';notes.add('text hierarchy');}
    if(!home&&next===18&&v.position.x>=272)s.fontFamily='Segoe UI Semibold';
   }
  }
  // Match native chart titles and six-card KPI values to textbox counterparts.
  for(const [object,entries] of Object.entries(v.visual.objects||{})){
   for(const entry of Array.isArray(entries)?entries:[]){
    const p=entry.properties||{},size=p.fontSize?.expr?.Literal;
    if(object==='legend'&&size&&!home){size.Value='11D';notes.add('legend size');}
    if(object==='title'&&size&&!home&&['19D','18D'].includes(size.Value)){size.Value='18D';notes.add('panel title');}
    if(v.visual.visualType==='cardVisual'&&object==='value'&&size&&!home&&page.displayName!=='Budget'&&['29D','32D'].includes(size.Value)){size.Value='30D';notes.add('KPI size');}
   }
  }
  // Only equivalent neutral text shades; semantic, heatmap and series colors stay distinct.
  function colors(o){if(!o||typeof o!=='object')return;for(const [k,value] of Object.entries(o)){if(typeof value==='string'){let next=value;for(const [a,b]of Object.entries(palette))next=next.replaceAll(a,b);if(next!==value){o[k]=next;notes.add('secondary text color');}}else colors(value);}}
  colors(v.visual);
  if(JSON.stringify(v)!==before){write(f,v);changes.push({visual:key,label:label.slice(0,100),changes:[...notes]});}
 }
 audit.pages.push({page:page.displayName,changedVisuals:changes.length,changes});
}
write(path.join(root,'validation/design-consistency.json'),audit);
console.log(JSON.stringify(audit.pages.map(({page,changedVisuals})=>({page,changedVisuals}))));
