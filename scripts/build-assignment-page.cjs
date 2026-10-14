// Add the last analysis page to the original report. No report/model cloning.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const base=path.resolve(__dirname,'../powerbi-ledningsrapport'),report=path.join(base,'LedningsrapportUtanScroll.Report');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const write=(p,v)=>{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');};
const id=s=>crypto.createHash('sha256').update('assignment-page:'+s).digest('hex').slice(0,20);
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?`${v}D`:`'${v.replace(/'/g,"''")}'`}}});
const color=c=>({solid:{color:lit(c)}}),col=(t,p,a)=>({Column:{Expression:{SourceRef:a?{Source:a}:{Entity:t}},Property:p}}),mea=(p,a)=>({Measure:{Expression:{SourceRef:a?{Source:a}:{Entity:'Planinställning'}},Property:p}}),dynamicColor=n=>({solid:{color:{expr:mea(n)}}});
const metaFile=path.join(report,'definition/pages/pages.json'),meta=read(metaFile),pages=path.join(report,'definition/pages');
const existing=meta.pageOrder.find(p=>/^(Projekt|Uppdrag) \/ beläggning$/.test(read(path.join(pages,p,'page.json')).displayName));
const current=existing||id('page');let tab=100;const placements=[];
const source=fs.readFileSync(path.join(__dirname,'build-ledningsrapport.cjs'),'utf8'),helper=source.slice(source.indexOf('function save('),source.indexOf('function page('));
const {visual,text,button,card:baseCard,slicer,save}=eval('(function(){'+helper+';return{visual,text,button,card,slicer,save};})()');
function card(key,name,box,size=13,ink='#5B6B80',fmt){const v=baseCard(key,name,box,size,ink,false,fmt);Object.assign(v.visual.objects.value[0].properties,{bold:lit(size>=20),textWrap:lit(false)});v.visual.objects.cardCalloutArea=[{properties:{paddingUniform:lit(0),backgroundTransparency:lit(100),show:lit(false)}}];return save(v);}
if(!meta.pageOrder.includes(current))meta.pageOrder.push(current);meta.activePageName=current;write(metaFile,meta);
const page={$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json',name:current,displayName:'Uppdrag / beläggning',displayOption:'FitToPage',width:1920,height:1200,objects:{background:[{properties:{color:color('#FDF6EC'),transparency:lit(0)}}]}};
write(path.join(pages,current,'page.json'),page);
text('sidebar','',[0,0,272,1200],12,'#0F3163','#FFFFFF');button('start','Start',[16,24,240,48],meta.pageOrder[0]);
['Ledningsöversikt','Försäljningsöversikt','Kunder','Budget','Uppdrag / beläggning'].forEach((n,i)=>button('nav'+i,n,[16,156+i*68,240,56],meta.pageOrder[i+1],i===4));
text('title','Uppdrag / beläggning',[304,24,464,64],27,'#0F3163',null,true);
// Reuse the proven period selectors and their bookmark state, with new local IDs.
const old='f429b020315c602ce0ed',oldDir=path.join(pages,old,'visuals'),map={};
for(const n of fs.readdirSync(oldDir)){
 const v=read(path.join(oldDir,n,'visual.json')),q=JSON.stringify(v.visual.query||{});
 const raw=JSON.stringify(v.visual.objects||{});
 if(v.position.x<272||v.position.y>=110||(!q.match(/Periodtyp|R12val|Helårsval|Månadsval/)&&v.visual.visualType!=='actionButton'&&!raw.includes('Periodtyp')))continue;
 const newID=id('period:'+n);map[n]=newID;v.name=newID;save(v);
}
const bmDir=path.join(report,'definition/bookmarks'),bmIndex=read(path.join(bmDir,'bookmarks.json')),bookmarkMap={};
for(const n of fs.readdirSync(bmDir)){
 if(!n.endsWith('.bookmark.json'))continue;const b=read(path.join(bmDir,n));
 if(!b.displayName.startsWith('Kunder – ')||!['R12','Helår','Månad'].includes(b.displayName.split(' – ')[1]))continue;
 const newID=id('period-bookmark:'+b.name);bookmarkMap[b.name]=newID;
 let s=JSON.stringify(b).replaceAll(old,current);for(const [a,z] of Object.entries(map))s=s.replaceAll(a,z);
 const c=JSON.parse(s);c.name=newID;c.displayName=b.displayName.replace('Kunder','Uppdrag');write(path.join(bmDir,newID+'.bookmark.json'),c);
 if(!bmIndex.items.some(x=>x.name===newID))bmIndex.items.push({name:newID});
}
write(path.join(bmDir,'bookmarks.json'),bmIndex);
const datePeriods={R12val:['Januari 2025','Februari 2025','Mars 2025','April 2025','Maj 2025','Juni 2025','Juli 2025','Augusti 2025','September 2025','Oktober 2025','November 2025','December 2025','Januari 2026','Februari 2026','Mars 2026','April 2026','Maj 2026','Juni 2026','Juli 2026','Augusti 2026','September 2026','December 2024'],Helårsval:['2024','2025']};
for(const name of Object.values(map)){
 const file=path.join(pages,current,'visuals',name,'visual.json'),v=read(file);
 for(const link of v.visual.visualContainerObjects?.visualLink||[]){const val=link.properties.bookmark?.expr?.Literal;if(val){const key=val.Value.slice(1,-1);if(bookmarkMap[key])val.Value="'"+bookmarkMap[key]+"'";}}
 const fields=v.visual.query?.queryState?.Values?.projections||[],table=fields[0]?.field?.Column?.Expression?.SourceRef?.Entity;
 if(['R12val','Helårsval','Månadsval'].includes(table)){
  let values=datePeriods[table];if(table==='Månadsval'){const monthnames=['Januari','Februari','Mars','April','Maj','Juni','Juli','Augusti','September','Oktober','November','December'];values=[];for(let y=2024;y<=2026;y++)for(let m=0;m<12;m++)if(y<2026||m<9)values.push(monthnames[m]+' '+y);}
  v.filterConfig={filters:[{name:id('valid-'+table),field:col(table,'Period'),type:'Categorical',howCreated:'User',filter:{Version:2,From:[{Name:'d',Entity:table,Type:0}],Where:[{Condition:{In:{Expressions:[col(table,'Period','d')],Values:values.map(x=>[{Literal:{Value:"'"+x+"'"}}])}}}]}}]};
 }
 write(file,v);
}
function tiles(key,t,c,box,selected,columns,all=false){return visual(key,'advancedSlicerVisual',box,{Values:[col(t,c)]},{...(selected?{general:[{properties:{filter:{filter:{Version:2,From:[{Name:'s',Entity:t,Type:0}],Where:[{Condition:{In:{Expressions:[col(t,c,'s')],Values:[[{Literal:{Value:"'"+selected+"'"}}]]}}}]}}}}]}:{}),layout:[{properties:{columnCount:lit(columns),rowCount:lit(1),cellPadding:lit(3),rectangleRoundedCurve:lit(5)}}],selection:[{properties:{singleSelect:lit(!all),strictSingleSelect:lit(!all),selectAllCheckboxEnabled:lit(all)}}],value:[{selector:{id:'default'},properties:{fontFamily:lit('Segoe UI'),fontSize:lit(11),fontColor:color('#0F3163')}},{selector:{id:'selected'},properties:{fontColor:color('#FFFFFF'),bold:lit(true)}}],fillCustom:[{properties:{show:lit(true)}},{selector:{id:'default'},properties:{fillColor:color('#EEF2F7')}},{selector:{id:'selected'},properties:{fillColor:color('#0F3163')}}],outline:[{properties:{show:lit(false)}}]});}
text('area-label','Område',[1352,16,336,24],11,'#5B6B80');const area=tiles('area','Uppdragsområden','Område',[1352,48,336,48],null,3,true);
const group=slicer('group','Resursval','Resursgrupp',[1704,16,184,88],'Alla','Resursgrupp');group.visual.visualContainerObjects.background=[{properties:{show:lit(false)}}];group.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];
group.filterConfig={filters:[{name:id('valid-resource'),field:mea('Resursval tillgängligt'),type:'Advanced',howCreated:'User',filter:{Version:2,From:[{Name:'p',Entity:'Planinställning',Type:0}],Where:[{Condition:{Comparison:{ComparisonKind:0,Left:mea('Resursval tillgängligt','p'),Right:{Literal:{Value:'1L'}}}}}]}}]};save(group);
card('history-context','Utfall periodtext',[304,120,680,28],11);card('plan-context','Planperiod text',[992,120,896,28],10.5);card('resource-context','Resursurval text',[1352,98,536,20],9.5);
text('history-section','Historiskt utfall · vald period',[304,154,1040,32],15,'#0F3163',null,true);text('plan-section','Kommande beläggning · 8 veckor',[1376,154,512,32],15,'#0F3163',null,true);
const kpis=[['Utförda uppdrag','Uppdrag utförda','Uppdrag jämförelse',null],['Debiterbara timmar','Utfall timmar','Timmar jämförelse','#,##0" h"'],['Debiteringsgrad','Utfall debiteringsgrad','Grad jämförelse','0.0 %'],['Uppdragens bruttomarginal','Utfall marginal','Marginal jämförelse','0.0 %'],['Bokad beläggning','Plan beläggning','Plan jämförelse','0.0 %'],['Ledig kapacitet','Plan ledigt','Ledigt jämförelse','#,##0" h"']];
for(let i=0;i<6;i++){const x=288+i*268;const [label,m,sub,fmt]=kpis[i];text('kpi-panel'+i,'',[x,194,252,184],12,'#0F3163','#FFFFFF');text('kpi-title'+i,label,[x+16,210,224,48],i===3?12.5:14,'#0F3163',null,true);card('kpi-value'+i,m,[x+16,264,224,56],30,'#0F3163',fmt);card('kpi-sub'+i,sub,[x+16,334,224,32],10.5,i===5?'#B42318':i<2?'#007956':'#5B6B80');}
for(const [i,x,w] of [[0,288,500],[1,804,500],[2,1320,580]])text('chart-panel'+i,'',[x,396,w,428],12,'#0F3163','#FFFFFF');
card('trend-title','Uppdrag trendrubrik',[304,412,468,40],17,'#0F3163');text('plan-title','Bokningar och kapacitet',[820,416,468,36],18,'#0F3163',null,true);text('plan-subtitle','Kommande 8 veckor',[820,456,468,28],11,'#5B6B80');text('heat-title','Beläggning per resursgrupp',[1336,416,548,36],18,'#0F3163',null,true);text('heat-legend','< 80 %     80–100 %     > 100 %',[1336,464,548,28],11,'#5B6B80');
const axis={show:lit(true),fontSize:lit(10),fontColor:color('#5B6B80'),showAxisTitle:lit(false)},legend=[{properties:{show:lit(true),position:lit('TopRight'),fontSize:lit(10),labelColor:color('#5B6B80')}}];
const trend=visual('trend','lineChart',[304,472,468,332],{Category:[col('Trendaxel','Månad')],Y:[mea('Trend teknisk'),mea('Trend bemanning'),mea('Trend mål'),mea('Trend vald månad')],Tooltips:[mea('Trend timmar'),mea('Trend kapacitet')]},{categoryAxis:[{properties:axis}],valueAxis:[{properties:{...axis,start:lit(0),end:lit(1),labelDisplayUnits:lit(1)}}],legend,dataPoint:[{selector:{metadata:'Planinställning.Trend teknisk'},properties:{fill:color('#0F3163')}},{selector:{metadata:'Planinställning.Trend bemanning'},properties:{fill:color('#007956')}},{selector:{metadata:'Planinställning.Trend mål'},properties:{fill:color('#8296B4')}},{selector:{metadata:'Planinställning.Trend vald månad'},properties:{fill:color('#9B570B')}}],lineStyles:[{properties:{strokeWidth:lit(2),showMarker:lit(true),markerSize:lit(5)}},{selector:{metadata:'Planinställning.Trend mål'},properties:{lineStyle:lit('dashed'),showMarker:lit(false)}},{selector:{metadata:'Planinställning.Trend vald månad'},properties:{strokeWidth:lit(0),showMarker:lit(true),markerSize:lit(9)}}],labels:[{properties:{show:lit(false)}}]});
trend.visual.query.queryState.Y.projections.forEach((p,i)=>p.displayName=['Teknisk service','Bemanning','Mål 82 %','Vald månad'][i]);
trend.visual.query.sortDefinition={sort:[{field:col('Trendaxel','Månad'),direction:'Ascending'}],isDefaultSort:false};save(trend);
const booking=visual('bookings','lineStackedColumnComboChart',[820,496,468,308],{Category:[col('Planveckor','Vecka')],Y:[mea('Plan bokat teknisk'),mea('Plan bokat bemanning')],Y2:[mea('Plan kapacitet')],Tooltips:[mea('Plan beläggning'),mea('Plan ledigt'),mea('Plan överbeläggning')]},{categoryAxis:[{properties:axis}],valueAxis:[{properties:{...axis,start:lit(0),secShow:lit(false),labelDisplayUnits:lit(1)}}],legend,dataPoint:[{selector:{metadata:'Planinställning.Plan bokat teknisk'},properties:{fill:color('#0F3163')}},{selector:{metadata:'Planinställning.Plan bokat bemanning'},properties:{fill:color('#007956')}}],lineStyles:[{properties:{lineStyle:lit('dashed'),strokeWidth:lit(2),showMarker:lit(false)}}],labels:[{properties:{show:lit(false)}}]});
booking.visual.query.sortDefinition={sort:[{field:col('Planveckor','Vecka'),direction:'Ascending'}],isDefaultSort:false};save(booking);
booking.visual.query.queryState.Y.projections.forEach((p,i)=>p.displayName=['Teknisk service','Bemanning'][i]);booking.visual.query.queryState.Y2.projections[0].displayName='Kapacitet';booking.visual.objects.valueAxis[0].properties.sharedAxis=lit(true);booking.visual.objects.dataPoint.push({selector:{metadata:'Planinställning.Plan kapacitet'},properties:{fill:color('#8296B4')}});save(booking);
const heat=visual('heat','pivotTable',[1336,508,548,292],{Rows:[col('Resurser','Resursgrupp'),col('Resurser','Medarbetare')],Columns:[col('Planveckor','Vecka')],Values:[mea('Plan celltext')]},{rowHeaders:[{properties:{fontSize:lit(11),fontColor:color('#0F3163'),showExpandCollapseButtons:lit(true),stepped:lit(true),steppedLayoutIndentation:lit(12),wordWrap:lit(false)}}],columnHeaders:[{properties:{fontSize:lit(10),fontColor:color('#0F3163'),backColor:color('#EEF2F7'),wordWrap:lit(false),autoSizeColumnWidth:lit(false)}}],values:[{properties:{fontSize:lit(11),fontColorPrimary:color('#0F3163'),wordWrap:lit(false)}},{selector:{data:[{dataViewWildcard:{matchingOption:1}}],metadata:'Planinställning.Plan celltext'},properties:{backColor:dynamicColor('Plan cellfärg'),fontColor:dynamicColor('Plan textfärg')}}],grid:[{properties:{rowPadding:lit(14),gridVertical:lit(true),gridVerticalColor:color('#FFFFFF'),gridHorizontal:lit(true),gridHorizontalColor:color('#FFFFFF')}}],subTotals:[{properties:{rowSubtotals:lit(true),rowSubtotalsPosition:lit('Top'),columnSubtotals:lit(false)}}],rowTotal:[{properties:{show:lit(false)}}],columnTotal:[{properties:{show:lit(false)}}],columnWidth:[{selector:{metadata:'Resurser.Resursgrupp'},properties:{value:lit(150)}},{selector:{metadata:'Planinställning.Plan celltext'},properties:{value:lit(44)}}]});
heat.visual.expansionStates=[{roles:['Rows'],levels:['Resursgrupp','Medarbetare'].map(p=>({queryRefs:['Resurser.'+p],identityKeys:[col('Resurser',p)],isCollapsed:true,isPinned:true})),root:{}}];heat.visual.query.queryState.Rows.projections.forEach((p,i)=>p.active=i===0);save(heat);
// Use supported axis property names, and retain weighted heatmap totals.
for(const v of [trend,booking]){for(const object of ['categoryAxis','valueAxis'])for(const entry of v.visual.objects[object]||[]){if(entry.properties.fontColor){entry.properties.labelColor=entry.properties.fontColor;delete entry.properties.fontColor;}}save(v);}
delete heat.visual.objects.rowTotal;delete heat.visual.objects.columnTotal;save(heat);
text('table-panel','',[288,840,1612,344],12,'#0F3163','#FFFFFF');text('table-title','Uppdragsuppföljning',[304,856,664,40],22,'#0F3163',null,true);text('table-subtitle','Uppdrag aktiva under vald period · Kalkyl och slutprognos gäller hela uppdraget',[304,898,1520,28],11,'#5B6B80');
const status=tiles('status','Uppdragsstatusval','Urval',[1152,856,732,40],'Alla',4);
const fields=[mea('Uppdrag riskikon'),col('Uppdragsregister','Uppdrag'),mea('Uppdrag kund'),col('Uppdragsregister','Typ'),col('Uppdragsregister','Status'),mea('Uppdrag planerade'),mea('Uppdrag hela timmar'),mea('Uppdrag kalkyl'),mea('Uppdrag prognos')];
const table=visual('table','tableEx',[304,936,1580,182],{Values:fields},{columnHeaders:[{properties:{fontFamily:lit('Segoe UI Semibold'),fontSize:lit(11),fontColor:color('#0F3163'),backColor:color('#EEF2F7'),wordWrap:lit(false)}}],values:[{properties:{fontFamily:lit('Segoe UI'),fontSize:lit(11),fontColorPrimary:color('#405572'),backColorPrimary:color('#FFFFFF'),backColorSecondary:color('#F7F9FC'),wordWrap:lit(false)}},{selector:{data:[{dataViewWildcard:{matchingOption:1}}],metadata:'Planinställning.Uppdrag prognos'},properties:{fontColor:dynamicColor('Uppdrag marginalfärg')}},{selector:{data:[{dataViewWildcard:{matchingOption:1}}],metadata:'Planinställning.Uppdrag riskikon'},properties:{fontColor:dynamicColor('Uppdrag riskfärg')}}],grid:[{properties:{rowPadding:lit(6),gridHorizontal:lit(true),gridHorizontalColor:color('#E7ECF2'),gridVertical:lit(false)}}],total:[{properties:{totals:lit(false)}}],columnWidth:fields.map((f,i)=>({selector:{metadata:(f.Column||f.Measure).Expression.SourceRef.Entity+'.'+(f.Column||f.Measure).Property},properties:{value:lit([32,350,216,172,120,170,170,170,170][i])}}))});
table.visual.query.queryState.Values.projections.forEach((p,i)=>p.displayName=['','Uppdrag','Kund','Typ','Status','Planerade timmar','Utfört hittills','Kalkylmarginal','Prognos slutmarginal'][i]);
table.filterConfig={filters:[{name:id('active-assignment'),field:mea('Uppdrag synligt'),type:'Advanced',howCreated:'User',filter:{Version:2,From:[{Name:'p',Entity:'Planinställning',Type:0}],Where:[{Condition:{Comparison:{ComparisonKind:0,Left:mea('Uppdrag synligt','p'),Right:{Literal:{Value:'1L'}}}}}]}}]};
table.visual.query.sortDefinition={sort:[{field:mea('Uppdrag riskikon'),direction:'Descending'},{field:col('Uppdragsregister','Uppdrag'),direction:'Ascending'}],isDefaultSort:false};save(table);
const detail=card('detail','Uppdrag detaljtext',[304,1124,1580,28],10);text('capacity-note','Ledig tid och överbeläggning räknas per medarbetare och dag. Ledig kapacitet kan finnas samtidigt som andra är överbelagda.',[304,1156,1568,24],10,'#5B6B80');
page.visualInteractions=[];const future=[booking.name,heat.name,...[4,5].flatMap(i=>['kpi-value'+i,'kpi-sub'+i].map(k=>id(current+':'+k)))];
for(const target of future)page.visualInteractions.push({source:trend.name,target,type:'NoFilter'});
// Status and table selection affect only the follow-up table and detail strip.
for(const sourceID of [status.name,table.name])for(const v of placements){const target=id(current+':'+v.key);if(![table.name,detail.name,sourceID].includes(target))page.visualInteractions.push({source:sourceID,target,type:'NoFilter'});}
write(path.join(pages,current,'page.json'),page);
// Enable the existing Start tile, preserve all other homepage components.
const home=meta.pageOrder[0],homeDir=path.join(pages,home,'visuals');
for(const n of fs.readdirSync(homeDir)){const p=path.join(homeDir,n,'visual.json'),v=read(p);if(v.position.x<1500)continue;
 const t=v.visual.objects?.general?.[0]?.properties?.paragraphs?.[0]?.textRuns?.[0];
 if(t&&/Projekt \/ beläggning/.test(t.value))t.value='Uppdrag / beläggning';
 if(t&&v.position.y===668)t.value='Uppdrag, debiteringsgrad och kommande kapacitet.';
 if(v.visual.visualType==='actionButton'&&v.position.y===760){v.visual.visualContainerObjects.visualLink=[{properties:{show:lit(true),type:lit('PageNavigation'),navigationSection:lit(current)}}];for(const x of v.visual.objects.text||[])if(x.selector){x.properties.text=lit('Öppna uppdrag →');x.properties.fontColor=color('#0F3163');}}
 write(p,v);
}
require('./polish-report-sidebar.cjs')(report);
// Native report tooltip with date range and all capacity components.
const tooltip=id('plan-tooltip');
const tooltipPage={$schema:page.$schema,name:tooltip,displayName:'Kapacitetsdetaljer',displayOption:'ActualSize',width:640,height:300,visibility:'HiddenInViewMode',pageBinding:{name:'PlanTooltip',type:'Tooltip',parameters:[]},objects:{background:[{properties:{color:color('#FFFFFF'),transparency:lit(0)}}]}};
write(path.join(pages,tooltip,'page.json'),tooltipPage);
const titleTemplate=read(path.join(pages,current,'visuals',id(current+':plan-title'),'visual.json'));titleTemplate.name=id('tooltip-title');Object.assign(titleTemplate.position,{x:16,y:16,width:600,height:40});titleTemplate.visual.objects.general[0].properties.paragraphs[0].textRuns[0].value='Bokningar och kapacitet · vald vecka';write(path.join(pages,tooltip,'visuals',titleTemplate.name,'visual.json'),titleTemplate);
const tooltipTable=structuredClone(table);tooltipTable.name=id('tooltip-table');Object.assign(tooltipTable.position,{x:16,y:72,width:608,height:200});delete tooltipTable.filterConfig;delete tooltipTable.visual.query.sortDefinition;delete tooltipTable.visual.objects.columnWidth;tooltipTable.visual.query.queryState.Values.projections=[col('Planveckor','Veckostart'),col('Planveckor','Veckoslut'),mea('Plan bokat'),mea('Plan kapacitet'),mea('Plan ledigt'),mea('Plan överbeläggning')].map((field,i)=>{const f=field.Column||field.Measure;return {field,queryRef:f.Expression.SourceRef.Entity+'.'+f.Property,nativeQueryRef:f.Property,displayName:['Från','Till','Bokat, h','Kapacitet, h','Ledigt, h','Överbokat, h'][i]};});tooltipTable.visual.objects.values=tooltipTable.visual.objects.values.filter(x=>!x.selector);write(path.join(pages,tooltip,'visuals',tooltipTable.name,'visual.json'),tooltipTable);
for(const v of [heat,booking]){v.visual.visualContainerObjects.visualTooltip=[{properties:{show:lit(true),type:lit('Canvas'),section:lit(tooltip)}}];save(v);}
const latestMeta=read(metaFile);if(!latestMeta.pageOrder.includes(tooltip))latestMeta.pageOrder.push(tooltip);write(metaFile,latestMeta);
write(path.join(base,'validation/assignment-report-manifest.json'),{page:current,report,periodBookmarks:Object.values(bookmarkMap),visuals:placements.length});
require('./polish-assignment-header.cjs')(report);
console.log('Built Uppdrag / beläggning in the original report:',current);
