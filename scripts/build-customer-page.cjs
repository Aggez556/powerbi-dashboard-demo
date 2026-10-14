// Add customer analysis without rebuilding any established page.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),base=path.join(root,'powerbi-ledningsrapport'),report=path.join(base,'LedningsrapportUtanScroll.Report');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const id=s=>crypto.createHash('sha256').update('customer-page:'+s).digest('hex').slice(0,20);
const write=(p,v)=>{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');};
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?`${v}D`:"'"+v.replace(/'/g,"''")+"'"}}});
const color=c=>({solid:{color:lit(c)}}),dynamicColor=n=>({solid:{color:{expr:mea(n)}}});
const col=(t,p,a)=>({Column:{Expression:{SourceRef:a?{Source:a}:{Entity:t}},Property:p}}),mea=(p,a)=>({Measure:{Expression:{SourceRef:a?{Source:a}:{Entity:'Försäljning'}},Property:p}});
const pagesPath=path.join(report,'definition/pages/pages.json'),meta=read(pagesPath),home=meta.pageOrder[0],overview=meta.pageOrder[1],sales=meta.pageOrder[2],customers=id('page');
let current=customers,tab=100;const placements=[];
const source=fs.readFileSync(path.join(__dirname,'build-ledningsrapport.cjs'),'utf8'),helper=source.slice(source.indexOf('function save('),source.indexOf('function page('));
const {visual,text,button,card:baseCard,slicer,save,selection}=eval('(function(){'+helper+';return{visual,text,button,card,slicer,save,selection};})()');
function card(...args){const v=baseCard(...args),p=v.visual.objects.value[0].properties;p.textWrap=lit(false);p.bold=lit(args[3]>=20);v.visual.visualContainerObjects.background=[{properties:{show:lit(false),transparency:lit(100)}}];v.visual.objects.fillCustom=[{selector:{id:'default'},properties:{show:lit(true),transparency:lit(100)}}];return save(v);}
const page={$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json',name:customers,displayName:'Kunder',displayOption:'FitToPage',width:1920,height:1200,objects:{background:[{properties:{color:color('#FDF6EC'),transparency:lit(0)}}]}};
if(!meta.pageOrder.includes(customers))meta.pageOrder.push(customers);write(pagesPath,meta);
text('sidebar','',[0,0,272,1200],12,'#0F3163','#FFFFFF');button('start','←  Start',[16,16,240,48],home);
['Ledningsöversikt','Försäljningsöversikt','Kunder','Budget','Projekt / beläggning'].forEach((n,i)=>button('nav'+i,n,[16,104+i*72,240,56],[overview,sales,customers,null,null][i],i===2));
text('title','Kunder',[304,24,464,64],29,'#0F3163',null,true);
text('period-heading','Periodtyp',[784,16,288,24],11,'#5B6B80');
const modes=['R12','Helår','Månad'],variants=[];
for(let active=0;active<3;active++)for(let i=0;i<3;i++){
 const v=button(`mode-${active}-${i}`,modes[i],[784+i*96,48,92,48],id('bookmark:'+modes[i]),active===i,true);
 for(const t of v.visual.objects.text)if(t.selector){t.properties.horizontalAlignment=lit('center');t.properties.leftMargin=lit(0);t.properties.rightMargin=lit(0);t.properties.fontSize=lit(11);}
 if(active)v.isHidden=true;save(v);variants.push({v,active});
}
const state=slicer('mode-state','Periodtyp','Periodtyp',[288,16,160,80],'R12','Periodtyp',true);
const dates=[slicer('r12','R12val','Period',[1088,16,248,88],'September 2026','Slutmånad'),slicer('year','Helårsval','Period',[1088,16,248,88],'2025','År',true),slicer('month','Månadsval','Period',[1088,16,248,88],'September 2026','Månad och år',true)];
for(const v of dates){v.visual.visualContainerObjects.background=[{properties:{show:lit(false)}}];v.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];v.visual.objects.items=[{properties:{textSize:lit(11),fontColor:color('#0F3163'),background:color('#FAEBD7')}}];save(v);}
const completeMonths=[];for(let year=2024;year<=2026;year++)for(let month=1;month<=12;month++){const value=year*100+month;if(value>=202412&&value<=202610)completeMonths.push([{Literal:{Value:value+'L'}}]);}
dates[2].filterConfig={filters:[{name:id('complete-month-comparison'),field:col('Månadsval','Ordning'),type:'Categorical',howCreated:'User',filter:{Version:2,From:[{Name:'s',Entity:'Månadsval',Type:0}],Where:[{Condition:{In:{Expressions:[col('Månadsval','Ordning','s')],Values:completeMonths}}}]}}]};save(dates[2]);
const industry=visual('industry','slicer',[1352,16,536,88],{Values:[col('Kunder','Kundbransch')]},{data:[{properties:{mode:lit('Dropdown')}}],header:[{properties:{show:lit(true),text:lit('Kundbransch'),textSize:lit(11),fontColor:color('#5B6B80')}}],selection:[{properties:{singleSelect:lit(false),selectAllCheckboxEnabled:lit(true)}}],items:[{properties:{textSize:lit(11),fontColor:color('#0F3163'),background:color('#FAEBD7')}}]});
industry.filterConfig={filters:[{name:id('customer-industries'),field:col('Kunder','Kundbransch'),type:'Categorical',howCreated:'User',filter:{Version:2,From:[{Name:'k',Entity:'Kunder',Type:0}],Where:[{Condition:{In:{Expressions:[col('Kunder','Kundbransch','k')],Values:['Restaurang','Hotell','Catering','Kontor','Livsmedel'].map(n=>[{Literal:{Value:"'"+n+"'"}}])}}}]}}]};save(industry);
const period=card('period-text','Kundperiod text',[784,112,1104,32],11,'#5B6B80');period.visual.objects.value[0].properties.horizontalAlignment=lit('right');save(period);
const kpis=[['Aktiva kunder','Kunder aktiva','Kunder aktiva undertext'],['Nya kunder','Kunder nya','Kunder nya undertext'],['Förlorade kunder','Kunder förlorade','Kunder förlorade undertext'],['Logo churn','Kunder logo churn','Kunder logo undertext'],['Revenue churn netto','Kunder revenue churn','Kunder churn undertext'],['Försäljning nya och\nåteraktiverade','Kunder nyförsäljningsandel','Kunder andel undertext']];
for(let i=0;i<6;i++){
 const x=288+i*270;text('kpi-panel'+i,'',[x,160,254,184],12,'#0F3163','#FFFFFF');text('kpi-title'+i,kpis[i][0],[x+16,176,230,48],13,'#0F3163',null,true);
 card('kpi-value'+i,kpis[i][1],[x+16,228,222,56],30,i===4?'Kunder churn färg':'#0F3163',i===4);
 card('kpi-context'+i,kpis[i][2],[x+16,288,230,44],10,i===4?'Kunder churn färg':i===0?'#007956':'#5B6B80',i===4);
}
for(const [key,box] of [['trend',[288,360,798,416]],['base',[1102,360,798,416]],['revenue',[288,792,798,384]],['detail',[1102,792,798,384]]])text(key+'-panel','',box,12,'#0F3163','#FFFFFF');
text('trend-title','Försäljning per kundgrupp',[312,376,750,40],19,'#0F3163',null,true);
text('base-title','Kundbasens förändring',[1126,376,750,40],19,'#0F3163',null,true);
text('revenue-title','Vad driver försäljningsförändringen?',[312,808,750,40],19,'#0F3163',null,true);
text('detail-title','Kunder att följa upp',[1126,808,750,40],19,'#0F3163',null,true);
const axis={show:lit(true),showAxisTitle:lit(false),fontFamily:lit('Segoe UI'),fontSize:lit(10.5),labelColor:color('#5B6B80')};
const valueAxis={...axis,start:lit(0),showAxisTitle:lit(true),titleFontSize:lit(11),labelDisplayUnits:lit(1),gridlineShow:lit(true),gridlineColor:color('#D5DDE7'),labelPrecision:lit(1)};
const legend={show:lit(true),position:lit('TopRight'),fontSize:lit(10),labelColor:color('#5B6B80'),showTitle:lit(false)};
const seriesNames=['Befintliga','Helt nya','Återaktiverade'],palette=['#0F3163','#007956','#4A6BCE'];
const trend=visual('trend','columnChart',[312,408,750,304],{Category:[col('Trendaxel','Månad')],Series:[col('Kundgrupper','Kundgrupp')],Y:[mea('Kundgrupp månadsintäkt')],Tooltips:[mea('Kundgrupp andel')]},{legend:[{properties:legend}],categoryAxis:[{properties:axis}],valueAxis:[{properties:{...valueAxis,titleText:lit('Omsättning, Mkr')}}],dataPoint:seriesNames.map((name,i)=>({selector:{data:[{scopeId:{Comparison:{ComparisonKind:0,Left:col('Kundgrupper','Kundgrupp'),Right:{Literal:{Value:"'"+name+"'"}}}}}]},properties:{fill:color(palette[i])}})),labels:[{properties:{show:lit(false)}}],totals:[{properties:{show:lit(true),fontSize:lit(10),labelDisplayUnits:lit(1),labelPrecision:lit(1),color:color('#0F3163')}}]});
trend.visual.query.sortDefinition={sort:[{field:col('Trendaxel','Månad'),direction:'Ascending'}],isDefaultSort:false};save(trend);
trend.position.y=376;trend.position.height=336;save(trend);
card('group-summary','Kundgrupp summering',[312,728,750,32],11,'#5B6B80');
function bridge(key,table,measure,box,maximum,title,precision){
 const v=visual(key,'waterfallChart',box,{Category:[col(table,'Steg')],Y:[mea(measure)],Tooltips:[mea('Kunder retention')]},{legend:[{properties:{show:lit(false)}}],categoryAxis:[{properties:{...axis,fontSize:lit(10)}}],valueAxis:[{properties:{...valueAxis,titleText:lit(title),labelPrecision:lit(precision),end:{expr:mea(maximum)}}}],sentimentColors:[{properties:{increaseFill:color('#007956'),decreaseFill:color('#B42318'),totalFill:color('#0F3163')}}],labels:[{properties:{show:lit(true),fontSize:lit(11),color:color('#0F3163'),labelDisplayUnits:lit(1),labelPrecision:lit(precision),labelPosition:lit('Auto')}}]});
 v.visual.query.sortDefinition={sort:[{field:col(table,'Steg'),direction:'Ascending'}],isDefaultSort:false};return save(v);
}
const baseBridge=bridge('base-bridge','Kundbassteg','Kundbas bryggsteg',[1126,424,750,288],'Kundbas bryggtak','Antal kunder',0);
card('base-summary','Kundbas ekvation',[1126,728,750,32],11,'#0F3163');
const revenueBridge=bridge('revenue-bridge','Kundintäktssteg','Kundintäkt bryggsteg',[312,864,750,248],'Kundintäkt bryggtak','Omsättning, Mkr',1);
card('revenue-summary','Kundintäkt ekvation',[312,1128,750,32],11,'Kunder churn färg',true);
const statuses=visual('status-selector','advancedSlicerVisual',[1126,856,750,44],{Values:[col('Kundstatusval','Status')]},{general:selection('Kundstatusval','Status','Alla'),layout:[{properties:{columnCount:lit(5),rowCount:lit(1),cellPadding:lit(1),leftOuterMargin:lit(0),rightOuterMargin:lit(0),topOuterMargin:lit(0),bottomOuterMargin:lit(0)}}],selection:[{properties:{singleSelect:lit(true),strictSingleSelect:lit(true)}}],value:[{selector:{id:'default'},properties:{fontSize:lit(10),fontColor:color('#0F3163'),textWrap:lit(false)}},{selector:{id:'selected'},properties:{fontColor:color('#FFFFFF')}}],fillCustom:[{properties:{show:lit(true)}},{selector:{id:'default'},properties:{fillColor:color('#EEF2F7')}},{selector:{id:'selected'},properties:{fillColor:color('#0F3163')}}]});
const detail=visual('detail','tableEx',[1126,912,750,208],{Values:[col('Kunder','Kund'),mea('Kundstatus text'),mea('Kund omsättning Mkr'),mea('Kund förändring procent'),mea('Kund marginal'),mea('Kund senaste köp text')]},{columnHeaders:[{properties:{fontFamily:lit('Segoe UI Semibold'),fontSize:lit(10),fontColor:color('#0F3163'),backColor:color('#EEF2F7'),autoSizeColumnWidth:lit(false),wordWrap:lit(false),outlineWeight:lit(0)}}],values:[{properties:{fontSize:lit(10),fontColorPrimary:color('#5B6B80'),fontColorSecondary:color('#5B6B80'),backColorPrimary:color('#FFFFFF'),backColorSecondary:color('#F7F9FC'),wordWrap:lit(false),outlineWeight:lit(0)}},{selector:{data:[{dataViewWildcard:{matchingOption:1}}],metadata:'Försäljning.Kundstatus text'},properties:{fontColor:dynamicColor('Kund radfärg')}}],grid:[{properties:{rowPadding:lit(3),gridVertical:lit(false),gridHorizontal:lit(true),gridHorizontalColor:color('#E7ECF2'),outlineWeight:lit(0)}}],total:[{properties:{totals:lit(false)}}]});
const labels=['Kund','Status','Omsättning','Förändring','Marginal','Senaste köp'],widths=[174,116,108,106,92,134];
detail.visual.query.queryState.Values.projections.forEach((p,i)=>{p.displayName=labels[i];p.nativeQueryRef=labels[i];});
detail.visual.objects.columnWidth=detail.visual.query.queryState.Values.projections.map((p,i)=>({selector:{metadata:p.queryRef},properties:{value:lit(widths[i])}}));
detail.visual.visualContainerObjects.stylePreset=[{properties:{name:lit('None')}}];
detail.filterConfig={filters:[{name:id('visible-customers'),field:mea('Kund tabell synlig'),type:'Advanced',howCreated:'User',filter:{Version:2,From:[{Name:'f',Entity:'Försäljning',Type:0}],Where:[{Condition:{Comparison:{ComparisonKind:0,Left:mea('Kund tabell synlig','f'),Right:{Literal:{Value:'1L'}}}}}]}}]};
detail.visual.query.sortDefinition={sort:[{field:mea('Kund omsättning Mkr'),direction:'Descending'}],isDefaultSort:false};save(detail);
const detail1=card('detail-extra1','Kund detaljrad 1',[1126,1120,750,24],9.5,'#5B6B80'),detail2=card('detail-extra2','Kund detaljrad 2',[1126,1144,750,24],9.5,'#5B6B80');
text('footer','Återaktiverad: köp historiskt, men inte under hela föregående jämförelseperiod. Negativ nettochurn betyder tillväxt i befintlig kundstock.',[304,1180,1584,20],10,'#5B6B80');
// Status selectors and chart clicks must never silently redefine headline churn.
const names=placements.map(p=>id(customers+':'+p.key)),onlyDetails=new Set([detail.name,detail1.name,detail2.name]);
page.visualInteractions=[];
for(const source of [trend.name,baseBridge.name,revenueBridge.name,detail.name,statuses.name])for(const target of names){
 if(source===target)continue;
 if(source===detail.name&&[detail1.name,detail2.name].includes(target))continue;
 if(source===statuses.name&&onlyDetails.has(target))continue;
 page.visualInteractions.push({source,target,type:'NoFilter'});
}
write(path.join(report,'definition/pages',customers,'page.json'),page);
const controls=[state.name,...dates.map(v=>v.name),...variants.map(x=>x.v.name)],items=[];
for(let i=0;i<3;i++){
 const name=id('bookmark:'+modes[i]),containers={};
 containers[state.name]={singleVisual:{display:{mode:'hidden'},objects:{merge:{general:selection('Periodtyp','Periodtyp',modes[i])}}}};
 dates.forEach((v,j)=>containers[v.name]={singleVisual:{...(i===j?{}:{display:{mode:'hidden'}}),objects:{merge:{general:selection(['R12val','Helårsval','Månadsval'][j],'Period',j===1?'2025':'September 2026')}}}});
 variants.forEach(({v,active})=>containers[v.name]={singleVisual:active===i?{}:{display:{mode:'hidden'}}});
 write(path.join(report,'definition/bookmarks',name+'.bookmark.json'),{$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/bookmark/2.1.0/schema.json',name,displayName:'Kunder – '+modes[i],options:{targetVisualNames:controls,suppressData:false,suppressDisplay:false,suppressActiveSection:true,applyOnlyToTargetVisuals:true},explorationState:{version:'1.3',activeSection:customers,sections:{[customers]:{visualContainers:containers}}}});items.push({name});
}
const bmPath=path.join(report,'definition/bookmarks/bookmarks.json'),bm=read(bmPath);bm.items=bm.items.filter(x=>!items.some(b=>b.name===x.name));bm.items.push(...items);write(bmPath,bm);
// Activate customer navigation on the portal and every existing sidebar.
for(const pageId of meta.pageOrder){
 const dir=path.join(report,'definition/pages',pageId,'visuals');
 for(const entry of fs.readdirSync(dir)){
  const file=path.join(dir,entry,'visual.json');if(!fs.existsSync(file))continue;
  const v=read(file);let changed=false;
  if(v.visual.visualType==='actionButton'){
   const label=JSON.stringify(v.visual.objects.text),isHomeCard=pageId===home&&v.position.x===812&&v.position.y===760;
   if(label.includes('Kunder')||isHomeCard){
    v.visual.visualContainerObjects.visualLink=[{properties:{show:lit(true),type:lit('PageNavigation'),navigationSection:lit(customers)}}];
    for(const item of v.visual.objects.text)if(item.selector){if(isHomeCard)item.properties.text=lit('Öppna kunder →');item.properties.fontColor=color(pageId===customers||isHomeCard?'#FFFFFF':'#0F3163');}
    for(const item of v.visual.objects.fill||[])if(item.selector)item.properties.fillColor=color(pageId===customers||isHomeCard?'#0F3163':'#FFFFFF');changed=true;
   }
  }
  if(pageId===home&&v.position.x===812){const p=v.visual.objects.general?.[0]?.properties?.paragraphs;if(p&&v.position.y===524){p[0].textRuns[0].value='KUNDER';changed=true;}if(p&&v.position.y===668){p[0].textRuns[0].value='Kundbas, lojalitet och\nförsäljningens drivkrafter.';changed=true;}}
  if(changed)write(file,v);
 }
}
write(path.join(base,'validation/customer-layout.json'),{page:customers,canvas:{width:1920,height:1200},standard:'R12 september 2026, alla branscher',table:'Seven priority customers; status filters only table; selecting row reveals industry, purchased areas and absolute financial details',placements});
console.log('Built customer page with six dynamic KPIs, cohort trend, two bridges, customer follow-up and protected churn context.');
require('./polish-report-sidebar.cjs')();

require('./polish-customer-followup.cjs')();
