// Adds one page to the current report; never rebuilds the established overview.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),base=path.join(root,'powerbi-ledningsrapport'),report=path.join(base,'LedningsrapportUtanScroll.Report');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const id=s=>crypto.createHash('sha256').update('sales-overview:'+s).digest('hex').slice(0,20);
const write=(p,v)=>{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');};
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?`${v}D`:`'${v.replace(/'/g,"''")}'`}}});
const color=c=>({solid:{color:lit(c)}}),dynamicColor=n=>({solid:{color:{expr:mea(n)}}});
const col=(t,p,a)=>({Column:{Expression:{SourceRef:a?{Source:a}:{Entity:t}},Property:p}});
const mea=(p,a)=>({Measure:{Expression:{SourceRef:a?{Source:a}:{Entity:'Försäljning'}},Property:p}});
const pagesMeta=path.join(report,'definition/pages/pages.json'),meta=read(pagesMeta),overview=meta.pageOrder[1],home=meta.pageOrder[0],sales=id('page');
let current=sales,tab=100;const placements=[];
// Established native component functions; load definitions without running the old builder.
const source=fs.readFileSync(path.join(__dirname,'build-ledningsrapport.cjs'),'utf8');
const helper=source.slice(source.indexOf('function save('),source.indexOf('function page('));
const {visual,text,button,card:baseCard,slicer,save,selection}=eval('(function(){'+helper+'; return {visual,text,button,card,slicer,save,selection};})()');
function card(...args){const v=baseCard(...args);const p=v.visual.objects.value[0].properties;p.textWrap=lit(false);p.bold=lit(args[3]>=20);v.visual.objects.padding[0].properties={paddingUniform:lit(0)};return save(v);}
write(path.join(report,'definition/pages',sales,'page.json'),{$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json',name:sales,displayName:'Försäljningsöversikt',displayOption:'FitToPage',width:1920,height:1200,objects:{background:[{properties:{color:color('#FDF6EC'),transparency:lit(0)}}]}});
if(!meta.pageOrder.includes(sales))meta.pageOrder.push(sales);write(pagesMeta,meta);
text('sidebar','',[0,0,272,1200],12,'#0F3163','#FFFFFF');
button('start','←  Start',[16,16,240,48],home);
const areas=['Ledningsöversikt','Försäljningsöversikt','Kunder','Budget','Projekt / beläggning'];
areas.forEach((n,i)=>button('nav'+i,n,[16,104+i*72,240,56],i===0?overview:i===1?sales:null,i===1));
text('page-title','Försäljningsöversikt',[304,24,464,64],29,'#0F3163',null,true);
text('period-label-heading','Periodtyp',[784,16,288,24],11,'#5B6B80');
const modes=['R12','Helår','Månad'],variants=[];
for(let active=0;active<3;active++)for(let i=0;i<3;i++){
 const v=button(`mode-${active}-${i}`,modes[i],[784+i*96,48,92,48],id('bookmark:'+modes[i]),active===i,true);
 for(const t of v.visual.objects.text)if(t.selector){t.properties.horizontalAlignment=lit('center');t.properties.leftMargin=lit(0);t.properties.rightMargin=lit(0);t.properties.fontSize=lit(11);}
 if(active)v.isHidden=true;save(v);variants.push({v,active});
}
const state=slicer('mode-state','Periodtyp','Periodtyp',[288,16,160,80],'R12','Periodtyp',true);
const dateSels=[slicer('r12-end','R12val','Period',[1088,16,248,88],'September 2026','Slutmånad'),slicer('year','Helårsval','Period',[1088,16,248,88],'2025','År',true),slicer('month','Månadsval','Period',[1088,16,248,88],'September 2026','Månad och år',true)];
dateSels.forEach(v=>{v.visual.visualContainerObjects.background=[{properties:{show:lit(false)}}];v.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];v.visual.objects.items=[{properties:{fontFamily:lit('Segoe UI'),textSize:lit(11),fontColor:color('#0F3163'),background:color('#FAEBD7')}}];save(v);});
text('area-heading','Verksamhetsområde',[1352,16,536,24],11,'#5B6B80');
const area=visual('area-selector','advancedSlicerVisual',[1352,48,536,56],{Values:[col('Områdesval','Verksamhetsområde')]},{general:selection('Områdesval','Verksamhetsområde','Alla områden'),layout:[{properties:{columnCount:lit(4),rowCount:lit(1),cellPadding:lit(2),leftOuterMargin:lit(0),rightOuterMargin:lit(0),topOuterMargin:lit(0),bottomOuterMargin:lit(0)}}],selection:[{properties:{singleSelect:lit(true),strictSingleSelect:lit(true)}}],value:[{selector:{id:'default'},properties:{fontSize:lit(10),fontFamily:lit('Segoe UI'),fontColor:color('#0F3163')}}]});
const periodCard=card('period-text','Periodtext',[784,112,1104,32],11,'#5B6B80');periodCard.visual.objects.value[0].properties.horizontalAlignment=lit('right');save(periodCard);
periodCard.visual.visualContainerObjects.background=[{properties:{show:lit(false),transparency:lit(100)}}];
periodCard.visual.objects.fillCustom=[{selector:{id:'default'},properties:{show:lit(true),transparency:lit(100)}}];save(periodCard);
area.visual.objects.fillCustom=[{properties:{show:lit(true)}},{selector:{id:'default'},properties:{fillColor:color('#FAEBD7'),transparency:lit(0)}},{selector:{id:'selected'},properties:{fillColor:color('#0F3163'),transparency:lit(0)}}];
area.visual.objects.value[0].properties.textWrap=lit(false);
area.visual.objects.value.push({selector:{id:'selected'},properties:{fontColor:color('#FFFFFF'),fontSize:lit(10),textWrap:lit(false)}});
area.visual.objects.outline=[{selector:{id:'default'},properties:{show:lit(false)}}];save(area);
const kpis=[['Nettoomsättning','Sälj omsättning Mkr','Sälj netto undertext'],['Försäljningstillväxt','Sälj tillväxt','Sälj tillväxt undertext'],['Bruttovinst','Sälj bruttovinst Mkr','Sälj brutto undertext'],['Bruttomarginal','Sälj bruttomarginal','Sälj marginal undertext'],['Sälj kort 5 rubrik','Sälj kort 5 värde','Sälj kort 5 undertext'],['Sälj kort 6 rubrik','Sälj kort 6 värde','Sälj kort 6 undertext']];
for(let i=0;i<6;i++){
 const x=288+i*270;text('kpi-panel'+i,'',[x,160,254,184],12,'#0F3163','#FFFFFF');
 if(i<4)text('kpi-title'+i,kpis[i][0],[x+16,176,222,40],13,'#0F3163',null,true);
 else card('kpi-title'+i,kpis[i][0],[x+8,168,238,48],12,'#0F3163');
 card('kpi-value'+i,kpis[i][1],[x+16,220,222,60],i===1?30:29,i===1?'Sälj tillväxt färg':'#0F3163',i===1);
 card('kpi-context'+i,kpis[i][2],[x+16,284,230,48],10.5,i===1?'Sälj tillväxt färg':i===3?'Sälj marginal färg':i===4?'#007956':'#5B6B80',i===1||i===3);
}
const panels=[['trend',[288,360,798,416]],['scatter',[1102,360,798,416]],['industry',[288,792,798,384]],['detail',[1102,792,798,384]]];
for(const [key,box] of panels)text(key+'-panel','',box,12,'#0F3163','#FFFFFF');
const trendTitle=card('trend-title','Sälj trend rubrik',[296,370,766,48],19);
trendTitle.visual.objects.value[0].properties.fontFamily=lit('Segoe UI Semibold');save(trendTitle);
text('scatter-title','Omsättning och bruttomarginal',[1126,376,750,48],19,'#0F3163',null,true);
text('industry-title','Försäljning per kundbransch',[312,808,750,48],19,'#0F3163',null,true);
text('detail-title','Produkt- och tjänsteanalys',[1126,808,750,48],19,'#0F3163',null,true);
const axis={show:lit(true),showAxisTitle:lit(false),fontFamily:lit('Segoe UI'),fontSize:lit(11),labelColor:color('#5B6B80')};
const val={...axis,start:lit(0),showAxisTitle:lit(true),titleText:lit('Omsättning, Mkr'),titleFontSize:lit(11),labelDisplayUnits:lit(1),labelPrecision:lit(1),gridlineShow:lit(true),gridlineColor:color('#D5DDE7')};
const legend={show:lit(true),position:lit('TopRight'),fontFamily:lit('Segoe UI'),fontSize:lit(10.5),labelColor:color('#5B6B80'),showTitle:lit(false)};
const trend=visual('trend','columnChart',[312,432,750,320],{Category:[col('Trendaxel','Månad')],Series:[col('Försäljningsserie','Serie')],Y:[mea('Sälj trend')],Tooltips:[mea('Sälj trend föregående år')]},{legend:[{properties:legend}],categoryAxis:[{properties:axis}],valueAxis:[{properties:val}],dataPoint:[{properties:{defaultColor:dynamicColor('Sälj trend färg')}}],labels:[{properties:{show:lit(true),fontSize:lit(10),labelDisplayUnits:lit(1),labelPrecision:lit(1)}}]});
trend.visual.query.sortDefinition={sort:[{field:col('Trendaxel','Månad'),direction:'Ascending'}],isDefaultSort:false};trend.visual.visualContainerObjects.visualTooltip=[{properties:{show:lit(true)}}];save(trend);
const scatter=visual('scatter','scatterChart',[1126,432,750,320],{Category:[col('Artiklar','Kategori')],Series:[col('Artiklar','Område')],X:[mea('Sälj omsättning Mkr')],Y:[mea('Sälj marginal procent')],Tooltips:[mea('Sälj bruttovinst Mkr'),mea('Sälj tillväxt')]},{legend:[{properties:legend}],categoryAxis:[{properties:{...val,titleText:lit('Omsättning, Mkr')}}],valueAxis:[{properties:{...val,titleText:lit('Bruttomarginal, %'),labelPrecision:lit(0)}}],categoryLabels:[{properties:{show:lit(true),fontSize:lit(10),color:color('#0F3163')}}]});scatter.visual.visualContainerObjects.visualTooltip=[{properties:{show:lit(true)}}];save(scatter);
const industry=visual('industry','clusteredBarChart',[312,864,750,288],{Category:[col('Kunder','Kundbransch')],Y:[mea('Sälj omsättning Mkr'),mea('Sälj omsättning föregående år Mkr')]},{legend:[{properties:legend}],categoryAxis:[{properties:axis}],valueAxis:[{properties:val}],dataPoint:[{selector:{metadata:'Försäljning.Sälj omsättning Mkr'},properties:{fill:color('#0F3163')}},{selector:{metadata:'Försäljning.Sälj omsättning föregående år Mkr'},properties:{fill:color('#BCC8D8')}}],labels:[{properties:{show:lit(true),fontSize:lit(11),labelDisplayUnits:lit(1),labelPrecision:lit(1)}}]});
industry.visual.query.queryState.Y.projections.forEach((p,i)=>{p.displayName=i?'Föregående år':'Vald period';p.nativeQueryRef=p.displayName;});industry.visual.query.sortDefinition={sort:[{field:mea('Sälj omsättning Mkr'),direction:'Descending'}],isDefaultSort:false};
scatter.position.y=376;scatter.position.height=376;
scatter.visual.objects.valueAxis[0].properties.end=lit(45);save(scatter);
industry.visual.objects.legend[0].properties.show=lit(false);
industry.visual.objects.categoryAxis[0].properties.innerPadding=lit(40);save(industry);
const industryLegend=text('industry-legend','',[780,816,282,32],10.5);
industryLegend.visual.objects.general[0].properties.paragraphs=[{horizontalTextAlignment:'right',textRuns:[{value:'● ',textStyle:{fontFamily:'Segoe UI',fontSize:'10.5pt',color:'#0F3163'}},{value:'Vald period  ',textStyle:{fontFamily:'Segoe UI',fontSize:'10.5pt',color:'#5B6B80'}},{value:'● ',textStyle:{fontFamily:'Segoe UI',fontSize:'10.5pt',color:'#BCC8D8'}},{value:'Föregående år',textStyle:{fontFamily:'Segoe UI',fontSize:'10.5pt',color:'#5B6B80'}}]}];save(industryLegend);
const detail=visual('detail','pivotTable',[1126,864,750,288],{Rows:[col('Artiklar','Kategori'),col('Artiklar','Artikel')],Values:[mea('Sälj omsättning Mkr'),mea('Sälj tillväxt'),mea('Sälj bruttovinst Mkr'),mea('Sälj bruttomarginal')]},{columnHeaders:[{properties:{fontSize:lit(11),fontColor:color('#0F3163'),backColor:color('#EEF2F7'),autoSizeColumnWidth:lit(false),columnAdjustment:lit('fixedWidth'),wordWrap:lit(false)}}],rowHeaders:[{properties:{fontSize:lit(11),fontColor:color('#5B6B80'),stepped:lit(true),steppedLayoutIndentation:lit(8),showExpandCollapseButtons:lit(true),autoExpand:lit(false),wordWrap:lit(false)}}],values:[{properties:{fontSize:lit(11),fontColorPrimary:color('#5B6B80'),fontColorSecondary:color('#5B6B80'),backColorPrimary:color('#FFFFFF'),backColorSecondary:color('#FFFFFF')}}],grid:[{properties:{rowPadding:lit(4),gridHorizontal:lit(true),gridHorizontalColor:color('#D5DDE7')}}],subTotals:[{properties:{rowSubtotals:lit(false),rowSubtotalsLabel:lit('Totalt'),rowSubtotalsPosition:lit('Bottom'),fontColor:color('#0F3163'),backColor:color('#EEF2F7'),bold:lit(true)}}]});
const labels=['Omsättning','Tillväxt','Bruttovinst','Marginal'];detail.visual.query.queryState.Values.projections.forEach((p,i)=>{p.displayName=labels[i];p.nativeQueryRef=labels[i];});
detail.visual.objects.columnWidth=[...detail.visual.query.queryState.Rows.projections.map(p=>({selector:{metadata:p.queryRef},properties:{value:lit(244)}})),...detail.visual.query.queryState.Values.projections.map((p,i)=>({selector:{metadata:p.queryRef},properties:{value:lit([128,110,138,130][i])}}))];
detail.visual.visualContainerObjects.stylePreset=[{properties:{name:lit('None')}}];
detail.visual.objects.subTotals[0].properties.rowSubtotals=lit(true);
detail.visual.objects.rowTotal=[{properties:{fontColor:color('#0F3163'),backColor:color('#EEF2F7'),bold:lit(true),applyToHeaders:lit(true)}}];
detail.position.height=304;
detail.visual.objects.grid[0].properties.rowPadding=lit(2);
detail.visual.objects.columnWidth.forEach((entry,i)=>entry.properties.value=lit(i<2?220:[120,100,128,110][i-2]));
detail.visual.objects.values.push({selector:{data:[{dataViewWildcard:{matchingOption:1}}],metadata:'Försäljning.Sälj tillväxt'},properties:{fontColor:dynamicColor('Sälj tillväxt färg')}});
require('./polish-sales-detail.cjs')(detail);
save(detail);
trend.position.y=376;trend.position.height=376;
trend.visual.objects.dataPoint=require('./fix-sales-trend-colors.cjs');
trend.visual.objects.labels[0].properties.show=lit(false);
trend.visual.objects.totals=[{properties:{show:lit(true),fontSize:lit(10.5),labelDisplayUnits:lit(1),labelPrecision:lit(1),color:color('#0F3163')}}];
trend.visual.query.queryState.Tooltips.projections.push({field:mea('Sälj trend vald månad'),queryRef:'Försäljning.Sälj trend vald månad',nativeQueryRef:'Vald månad'});
save(trend);
// Mode bookmarks have independent IDs from the overview, sharing the same model tables.
const targetNames=[state.name,...dateSels.map(v=>v.name),...variants.map(x=>x.v.name)];
const bookmarkItems=[];
for(let i=0;i<3;i++){
 const name=id('bookmark:'+modes[i]),containers={};
 containers[state.name]={singleVisual:{display:{mode:'hidden'},objects:{merge:{general:selection('Periodtyp','Periodtyp',modes[i])}}}};
 dateSels.forEach((v,j)=>containers[v.name]={singleVisual:{...(i===j?{}:{display:{mode:'hidden'}}),objects:{merge:{general:selection(['R12val','Helårsval','Månadsval'][j],'Period',j===1?'2025':'September 2026')}}}});
 variants.forEach(({v,active})=>containers[v.name]={singleVisual:active===i?{}:{display:{mode:'hidden'}}});
 write(path.join(report,'definition/bookmarks',name+'.bookmark.json'),{$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/bookmark/2.1.0/schema.json',name,displayName:'Försäljning – '+modes[i],options:{targetVisualNames:targetNames,suppressData:false,suppressDisplay:false,suppressActiveSection:true,applyOnlyToTargetVisuals:false},explorationState:{version:'1.3',activeSection:sales,sections:{[sales]:{visualContainers:containers}}}});bookmarkItems.push({name});
}
const bmPath=path.join(report,'definition/bookmarks/bookmarks.json'),bm=read(bmPath);bm.items=bm.items.filter(x=>!bookmarkItems.some(b=>b.name===x.name));bm.items.push(...bookmarkItems);write(bmPath,bm);
// Mode changes affect only the named controls, retaining area choices and static overview row filters.
for(const item of bm.items){const p=path.join(report,'definition/bookmarks',item.name+'.bookmark.json');if(fs.existsSync(p)){const b=read(p);if(b.options?.targetVisualNames?.length){b.options.applyOnlyToTargetVisuals=true;write(p,b);}}}
// Activate existing links and clear former organisation/branding text.
for(const page of meta.pageOrder){
 const dir=path.join(report,'definition/pages',page,'visuals');
 const files=fs.readdirSync(dir).map(n=>path.join(dir,n,'visual.json')).filter(f=>fs.existsSync(f));
 const values=files.map(file=>({file,v:read(file)}));
 const startHeading=values.find(({v})=>JSON.stringify(v.visual?.objects?.general||{}).includes('Försäljningsöversikt')&&v.position.y>400);
 for(const {file,v} of values){
  let changed=false;const para=v.visual?.objects?.general?.[0]?.properties?.paragraphs;
  if(para)for(const p of para)for(const run of p.textRuns||[])if(typeof run.value==='string'&&/Hygiengruppen|Aubeco/i.test(run.value)){run.value='';changed=true;}
  if(v.visual?.visualType==='actionButton'){
   const labels=v.visual.objects.text||[];const all=labels.map(x=>x.properties?.text?.expr?.Literal?.Value||'').join(' ');
   const side=all.includes('Försäljningsöversikt');const start=page===home&&startHeading&&Math.abs(v.position.x-startHeading.v.position.x)<1&&v.position.y>700&&v.position.y<850;
   if(side||start){
    v.visual.visualContainerObjects.visualLink=[{properties:{show:lit(true),type:lit('PageNavigation'),navigationSection:lit(sales)}}];
    labels.filter(x=>x.selector).forEach(x=>{if(start)x.properties.text=lit('Öppna försäljning →');x.properties.fontColor=color(page===sales||start?'#FFFFFF':'#0F3163');});
    for(const entry of v.visual.objects.fill||[])if(entry.selector)entry.properties.fillColor=color(page===sales||start?'#0F3163':'#FFFFFF');
    changed=true;
   }
  }
  if(page===home&&startHeading&&para&&Math.abs(v.position.x-startHeading.v.position.x)<1){
   if(v.position.y===524){para[0].textRuns[0].value='FÖRSÄLJNING';changed=true;}
   if(v.position.y===668){para[0].textRuns[0].value='Försäljning, kunder och\nlönsamhet per kategori.';changed=true;}
  }
  if(changed)write(file,v);
 }
}
const theme=path.join(report,'StaticResources/RegisteredResources/LedningsrapportTheme.json');if(fs.existsSync(theme)){const t=read(theme);t.dataColors=['#0F3163','#007956','#4A6BCE','#9B570B','#5B6B80'];write(theme,t);}
write(path.join(base,'validation/sales-layout.json'),{page:sales,displayName:'Försäljningsöversikt',canvas:{width:1920,height:1200},standard:'R12 september 2026, alla områden',placements,overviewPreserved:overview});
console.log('Added Försäljningsöversikt, six responsive KPIs, four native visuals, period controls, area filter and navigation.');
require('./polish-report-sidebar.cjs')();
