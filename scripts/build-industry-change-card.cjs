const fs=require('fs'),path=require('path'),crypto=require('crypto');
const report=path.resolve(__dirname,'../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report');
const page='f429b020315c602ce0ed',dir=path.join(report,'definition/pages',page,'visuals');
const hash=s=>crypto.createHash('sha256').update(s).digest('hex').slice(0,20);
const old=k=>hash('customer-page:'+page+':'+k),id=k=>hash('customer-industry-change:'+k),bm=i=>id('bookmark-'+i);
const read=f=>JSON.parse(fs.readFileSync(f,'utf8').replace(/^\uFEFF/,''));
const load=name=>read(path.join(dir,name,'visual.json'));
const write=(f,v)=>fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n');
const save=v=>{const d=path.join(dir,v.name);fs.mkdirSync(d,{recursive:true});write(path.join(d,'visual.json'),v);};
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?v+'D':"'"+v.replace(/'/g,"''")+"'"}}});
const color=c=>({solid:{color:lit(c)}});
const column=(t,p)=>({Column:{Expression:{SourceRef:{Entity:t}},Property:p}}),measure=p=>({Measure:{Expression:{SourceRef:{Entity:'Kunder'}},Property:p}});
const proj=(field,name)=>{const f=field.Column||field.Measure;return{field,queryRef:f.Expression.SourceRef.Entity+'.'+f.Property,nativeQueryRef:name||f.Property,displayName:name||f.Property};};
const panel=load(old('base-panel'));panel.name=id('panel');Object.assign(panel.position,{x:288,y:792,width:798,height:384});save(panel);
function text(key,label,box,size=11){const v=load(old('base-title'));v.name=id(key);v.isHidden=false;Object.assign(v.position,{x:box[0],y:box[1],width:box[2],height:box[3],z:400});v.visual.objects.general[0].properties.paragraphs=[{horizontalTextAlignment:'left',textRuns:[{value:label,textStyle:{fontFamily:size===18?'Segoe UI Semibold':'Segoe UI',fontSize:size+'pt',color:size===18?'#0F3163':'#5B6B80'}}]}];save(v);}
text('title','Försäljning per bransch',[312,808,490,40],18);
text('subtitle','Förändring mot samma månad föregående år',[312,852,750,24]);
const footerFile=path.join(dir,id('footer'),'visual.json');
if(fs.existsSync(footerFile))fs.unlinkSync(footerFile);
if(fs.existsSync(path.dirname(footerFile)))fs.rmdirSync(path.dirname(footerFile));
const palette=[['Restaurang','#0F3163'],['Hotell','#007956'],['Catering','#4A6BCE'],['Kontor','#9B570B'],['Livsmedel','#708198']];
const dataPoint=palette.map(([name,ink])=>({selector:{data:[{scopeId:{Comparison:{ComparisonKind:0,Left:column('Kunder','Kundbransch'),Right:{Literal:{Value:"'"+name+"'"}}}}}]},properties:{fill:color(ink)}}));
const charts=[];
for(let mode=0;mode<2;mode++){
 const v=load(old('trend'));v.name=id('chart-'+mode);charts.push(v.name);v.isHidden=mode!==0;
 Object.assign(v.position,{x:312,y:878,width:750,height:282,z:300});
 v.visual.visualType=mode===0?'lineChart':'clusteredColumnChart';
 const y=mode===0?'Bransch månadsförändring procent':'Bransch månadsförändring Mkr',unit=mode===0?'procent':'Mkr';
 v.visual.query={queryState:{Category:{projections:[proj(column('Trendaxel','Månadsstart'),'Månad')]},Series:{projections:[proj(column('Kunder','Kundbransch'),'Bransch')]},Y:{projections:[proj(measure(y),mode===0?'Förändring i procent':'Förändring i Mkr')]},Tooltips:{projections:[proj(measure('Bransch månadsförsäljning'),'Försäljning'),proj(measure('Bransch månadsförsäljning föregående år'),'Samma månad föregående år'),proj(measure(mode===0?'Bransch månadsförändring kronor':'Bransch månadsförändring procent'),'Förändring')]}},sortDefinition:{sort:[{field:column('Trendaxel','Månadsstart'),direction:'Ascending'}],isDefaultSort:false}};
 v.filterConfig=structuredClone(load(old('industry')).filterConfig);
 const axis={show:lit(true),fontFamily:lit('Segoe UI'),fontSize:lit(10),labelColor:color('#5B6B80')};
 v.visual.objects={categoryAxis:[{properties:{...axis,axisType:lit('Categorical'),showAxisTitle:lit(false)}}],valueAxis:[{properties:{...axis,start:{expr:measure('Bransch axelgolv '+unit)},end:{expr:measure('Bransch axeltak '+unit)},roundRange:lit(false),showAxisTitle:lit(true),titleText:lit(mode===0?'Förändring, %':'Förändring, Mkr'),titleFontSize:lit(10.5),labelDisplayUnits:lit(1),labelPrecision:lit(mode===0?0:1),gridlineShow:lit(true),gridlineColor:color('#D5DDE7'),gridlineStyle:lit('dotted')}}],legend:[{properties:{show:lit(true),position:lit('Top'),fontFamily:lit('Segoe UI'),fontSize:lit(10.5),labelColor:color('#5B6B80'),showTitle:lit(false)}}],dataPoint,labels:[{properties:{show:lit(false)}}],y1AxisReferenceLine:[{selector:{id:'zero'},properties:{show:lit(true),value:lit(0),position:lit('front'),lineColor:color('#8296B4'),width:lit(1.2),transparency:lit(0),style:lit('solid'),dataLabelShow:lit(false)}}]};
 if(mode===0)v.visual.objects.lineStyles=[{properties:{strokeWidth:lit(2),showMarker:lit(true),markerSize:lit(3),lineChartType:lit('linear')}},...palette.map(([name,ink],i)=>({selector:dataPoint[i].selector,properties:{strokeColor:color(ink),markerColor:color(ink)}}))];
 v.visual.visualContainerObjects.general=[{properties:{altText:lit('Månadsvis försäljningsförändring mot samma månad året före, per kundbransch. Symmetrisk skala med noll i mitten.')}}];save(v);
}
const template=load(old('mode-0-0')),buttons=[];
for(let active=0;active<2;active++)for(let choice=0;choice<2;choice++){
 const v=structuredClone(template);v.name=id('button-'+active+'-'+choice);buttons.push({name:v.name,active});v.isHidden=active!==0;delete v.filterConfig;
 Object.assign(v.position,{x:814+choice*126,y:808,width:122,height:40,z:500,tabOrder:600+choice});
 const selected=active===choice;
 v.visual.objects={text:[{properties:{show:lit(true)}},...['default','hover','selected'].map(state=>({selector:{id:state},properties:{text:lit(choice===0?'Procent':'Kronor'),fontFamily:lit(selected?'Segoe UI Semibold':'Segoe UI'),fontSize:lit(11),fontColor:color(selected?'#FFFFFF':'#0F3163'),horizontalAlignment:lit('center')}}))],fill:[{properties:{show:lit(true)}},...['default','hover','selected'].map(state=>({selector:{id:state},properties:{fillColor:color(selected?'#0F3163':state==='hover'?'#E6EDF6':'#EEF2F7'),transparency:lit(0)}}))],outline:[{properties:{show:lit(false)}}],icon:[{properties:{show:lit(false)}}],shape:[{properties:{tileShape:lit('rectangleRounded'),roundEdge:{expr:{Literal:{Value:'4L'}}}}}]};
 v.visual.visualContainerObjects.visualLink=[{properties:{show:lit(true),type:lit('Bookmark'),bookmark:lit(bm(choice))}}];save(v);
}
const targets=[...charts,...buttons.map(b=>b.name)],bookmarks=path.join(report,'definition/bookmarks');
for(let active=0;active<2;active++){
 const containers={};charts.forEach((name,i)=>containers[name]={singleVisual:i===active?{}:{display:{mode:'hidden'}}});buttons.forEach(b=>containers[b.name]={singleVisual:b.active===active?{}:{display:{mode:'hidden'}}});
 write(path.join(bookmarks,bm(active)+'.bookmark.json'),{$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/bookmark/2.1.0/schema.json',name:bm(active),displayName:'Branschutveckling – '+(active===0?'Procent':'Kronor'),options:{targetVisualNames:targets,suppressData:true,suppressDisplay:false,suppressActiveSection:true,applyOnlyToTargetVisuals:true},explorationState:{version:'1.3',activeSection:page,sections:{[page]:{visualContainers:containers}}}});
}
const indexFile=path.join(bookmarks,'bookmarks.json'),index=read(indexFile);index.items=index.items.filter(b=>![bm(0),bm(1)].includes(b.name));index.items.push({name:bm(0)},{name:bm(1)});write(indexFile,index);
const pageFile=path.join(report,'definition/pages',page,'page.json'),p=read(pageFile);
p.visualInteractions=p.visualInteractions.filter(i=>i.source!==id('footer')&&i.target!==id('footer'));
const visuals=fs.readdirSync(dir).map(name=>path.join(dir,name,'visual.json')).filter(fs.existsSync).map(read);
const interactors=visuals.filter(v=>['columnChart','waterfallChart','tableEx'].includes(v.visual.visualType)).map(v=>v.name);
for(const source of [...interactors,...charts])for(const target of charts.includes(source)?visuals.map(v=>v.name):charts){if(source!==target&&!p.visualInteractions.some(i=>i.source===source&&i.target===target))p.visualInteractions.push({source,target,type:'NoFilter'});}
write(pageFile,p);
console.log('Added monthly industry trend with percentage lines, grouped money columns, fixed series colors and independent display-only toggle.');
require('./design-customer-tooltips.cjs')();
