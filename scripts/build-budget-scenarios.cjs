// Additive native Budget page. Other report content is preserved.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),report=path.join(root,'powerbi-ledningsrapport',process.env.PBI_BUDGET_REPORT||'LedningsrapportUtanScroll.Report');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const write=(p,v)=>{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');};
const id=s=>crypto.createHash('sha256').update('budget-scenarios:'+s).digest('hex').slice(0,20);
const budget=id('page'),metaFile=path.join(report,'definition/pages/pages.json'),meta=read(metaFile);
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?`${v}D`:`'${v.replace(/'/g,"''")}'`}}});
const color=c=>({solid:{color:lit(c)}}),col=(t,p,a)=>({Column:{Expression:{SourceRef:a?{Source:a}:{Entity:t}},Property:p}}),mea=(p,a)=>({Measure:{Expression:{SourceRef:a?{Source:a}:{Entity:'Budgetscenarier'}},Property:p}}),dynamicColor=n=>({solid:{color:{expr:mea(n)}}});
let current=budget,tab=100;const placements=[];
const source=fs.readFileSync(path.join(__dirname,'build-ledningsrapport.cjs'),'utf8'),helper=source.slice(source.indexOf('function save('),source.indexOf('function page('));
const {visual,text,button,card,slicer,save}=eval('(function(){'+helper+';return{visual,text,button,card,slicer,save};})()');
if(!meta.pageOrder.includes(budget))meta.pageOrder.push(budget);meta.activePageName=budget;write(metaFile,meta);
const page={$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json',name:budget,displayName:'Budget',displayOption:'FitToPage',width:1920,height:1200,objects:{background:[{properties:{color:color('#FDF6EC'),transparency:lit(0)}}]}};
write(path.join(report,'definition/pages',budget,'page.json'),page);
// Seed six navigation controls so the shared sidebar grammar can style them.
text('sidebar','',[0,0,272,1200],12,'#0F3163','#FFFFFF');button('start','Start',[16,24,240,48],meta.pageOrder[0]);
['Ledningsöversikt','Försäljningsöversikt','Kunder','Budget','Projekt / beläggning'].forEach((n,i)=>button('nav'+i,n,[16,156+i*68,240,56],meta.pageOrder[i+1]||null,i===3));
text('title','Budget',[304,24,1100,64],32,'#0F3163',null,true);
text('subtitle','Budgetscenarier och utfall',[304,88,1100,40],18,'#5B6B80');
function selectValues(t,c,values){return [{properties:{filter:{filter:{Version:2,From:[{Name:'s',Entity:t,Type:0}],Where:[{Condition:{In:{Expressions:[col(t,c,'s')],Values:values.map(v=>[{Literal:{Value:typeof v==='number'?v+'L':"'"+v+"'"}}])}}}]}}}}];}
function measureFilter(v,name){v.filterConfig={filters:[{name:id('filter:'+name),field:mea(name),type:'Advanced',howCreated:'User',filter:{Version:2,From:[{Name:'b',Entity:'Budgetscenarier',Type:0}],Where:[{Condition:{Comparison:{ComparisonKind:0,Left:mea(name,'b'),Right:{Literal:{Value:'1L'}}}}}]}}]};return save(v);}
const controls=[];
function tiles(key,t,c,box,selected,columns,rows,filter){
 const v=visual(key,'advancedSlicerVisual',box,{Values:[col(t,c)]},{general:selectValues(t,c,selected),layout:[{properties:{columnCount:lit(columns),rowCount:lit(rows),cellPadding:lit(3),rectangleRoundedCurve:lit(5),leftOuterMargin:lit(0),rightOuterMargin:lit(0),topOuterMargin:lit(0),bottomOuterMargin:lit(0)}}],selection:[{properties:{singleSelect:lit(key!=='months'),strictSingleSelect:lit(key!=='months')}}],value:[{selector:{id:'default'},properties:{fontFamily:lit('Segoe UI'),fontSize:lit(12),fontColor:color('#0F3163'),textWrap:lit(false)}},{selector:{id:'selected'},properties:{fontColor:color('#FFFFFF'),bold:lit(true)}}],fillCustom:[{properties:{show:lit(true)}},{selector:{id:'default'},properties:{fillColor:color('#EEF2F7')}},{selector:{id:'selected'},properties:{fillColor:color('#0F3163')}}],outline:[{properties:{show:lit(false)}}]});
 controls.push(v);if(filter)measureFilter(v,filter);return v;
}
const year=slicer('year','Budgetår','År',[1712,16,176,88],'2026','År');year.visual.objects.general=selectValues('Budgetår','År',[2026]);year.visual.visualContainerObjects.background=[{properties:{show:lit(false)}}];year.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];save(year);controls.push(year);
card('kpi-prefix','Budget KPI prefix',[304,120,1584,28],11,'#5B6B80');
for(const [i,label,title] of [[0,'omsättning','Omsättning'],[1,'resultat','Rörelseresultat'],[2,'marginal','Bruttomarginal']]){
 const x=288+i*542;
 text('kpi-panel'+i,'',[x,160,526,208],12,'#0F3163','#FFFFFF');
 text('kpi-title'+i,title,[x+24,176,478,32],16,'#0F3163',null,true);
 card('kpi-value'+i,'Budget '+label+' värde',[x+24,216,478,64],36,'#0F3163');
 card('kpi-budget'+i,'Budget '+label+' jämförelse',[x+24,286,478,30],13,'#5B6B80');
 card('kpi-diff'+i,'Budget '+label+' avvikelse',[x+24,326,478,30],15,'Budget '+label+' färg',true);
}
text('filters-panel','',[288,392,296,792],12,'#0F3163','#FFFFFF');text('matrix-panel','',[600,392,1300,792],12,'#0F3163','#FFFFFF');
text('scenario-label','Budgetscenario',[312,412,248,32],15,'#0F3163',null,true);
tiles('scenario','Budgetscenarion','Scenario',[312,452,248,120],['Huvudscenario'],1,3,'Budget scenario tillgängligt');
text('scenario-help','Förberedda versioner från Excel',[312,580,248,28],10.5,'#5B6B80');
text('comparison-label','Jämförelse',[312,620,248,32],15,'#0F3163',null,true);
const modeState=tiles('comparison','Budgetjämförelse','Läge',[312,660,248,80],['Scenario mot utfall'],1,2,'Budget jämförelse tillgänglig');
modeState.isHidden=true;save(modeState);
const modeVariants=[];
for(let active=0;active<2;active++)for(let i=0;i<2;i++){
 const v=button(`mode-${active}-${i}`,['Scenario mot utfall','Jämför scenarier'][i],[312,660+i*46,248,44],id('mode-'+i),active===i,true);
 for(const t of v.visual.objects.text)if(t.selector){t.properties.fontSize=lit(11.5);t.properties.horizontalAlignment=lit('center');}
 v.visual.objects.icon=[{properties:{show:lit(false)}},{selector:{id:'default'},properties:{placement:lit('left')}}];
 if(active)v.isHidden=true;save(v);modeVariants.push({v,active});
}
// Empty in actual mode, populated only for valid comparison scenarios.
const b=slicer('scenario-b','Budgetjämförelsescenario','Scenario',[312,752,248,80],'Försiktigt scenario','Jämförelsescenario');
b.visual.visualContainerObjects.background=[{properties:{show:lit(false)}}];b.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];measureFilter(b,'Budget B tillgängligt');controls.push(b);
b.isHidden=true;save(b);
text('months-label','Period',[312,840,248,32],15,'#0F3163',null,true);
tiles('months','Budgetmånader','Kortnamn',[312,878,248,136],['Jul','Aug','Sep'],3,4,'Budget månad tillgänglig');
card('period','Budget periodetikett',[312,1018,248,28],10.5,'#5B6B80');
text('view-label','Visning',[312,1052,248,30],14,'#0F3163',null,true);
tiles('view','Budgetvisning','Visning',[312,1088,248,40],['Månad'],2,1);
const reset=button('reset','Återställ filter',[312,1136,248,44],id('reset'),false,true);
for(const o of reset.visual.objects.text)if(o.selector){o.properties.fontSize=lit(11);o.properties.horizontalAlignment=lit('center');}
reset.visual.objects.icon=[{properties:{show:lit(false)}},{selector:{id:'default'},properties:{placement:lit('left')}}];save(reset);
text('matrix-title','Resultaträkning',[624,412,680,42],23,'#0F3163',null,true);
card('matrix-subtitle','Budget matrisrubrik',[624,462,1252,36],13,'#5B6B80');
card('matrix-unit','Budget visningsetikett',[624,508,1252,28],11,'#5B6B80');
for(const [key,label,x,w] of [['expand','Expandera alla',1536,168],['collapse','Fäll ihop',1716,160]]){
 const v=button(key,label,[x,412,w,44],id(key),false,true);for(const t of v.visual.objects.text)if(t.selector){t.properties.fontSize=lit(11);t.properties.horizontalAlignment=lit('center');}
 v.visual.objects.icon=[{properties:{show:lit(false)}},{selector:{id:'default'},properties:{placement:lit('left')}}];save(v);
}
const rows=['Rad','Undergrupp','Post'].map(p=>col('Budgetrader',p));
const matrix=visual('matrix','pivotTable',[624,548,1252,572],{Rows:rows,Columns:[col('Budgetkolumner','Grupp'),col('Budgetkolumner','Kolumn')],Values:[mea('Budget matrisvärde')]},{
 columnHeaders:[{properties:{fontFamily:lit('Segoe UI Semibold'),fontSize:lit(11.5),fontColor:color('#0F3163'),backColor:color('#EEF2F7'),alignment:lit('Right'),autoSizeColumnWidth:lit(false),wordWrap:lit(true),outlineWeight:lit(0)}}],
 rowHeaders:[{properties:{fontFamily:lit('Segoe UI'),fontSize:lit(11.5),fontColor:color('#0F3163'),backColor:color('#FFFFFF'),stepped:lit(true),steppedLayoutIndentation:lit(18),showExpandCollapseButtons:lit(true),expandCollapseButtonsSize:lit(11),expandCollapseButtonsColor:color('#0F3163'),wordWrap:lit(false),outlineWeight:lit(0)}}],
 values:[{properties:{fontFamily:lit('Segoe UI'),fontSize:lit(11.5),fontColorPrimary:color('#405572'),fontColorSecondary:color('#405572'),backColorPrimary:color('#FFFFFF'),backColorSecondary:color('#F8FAFC'),wordWrap:lit(false),outlineWeight:lit(0)}},{selector:{data:[{dataViewWildcard:{matchingOption:1}}],metadata:'Budgetscenarier.Budget matrisvärde'},properties:{fontColor:dynamicColor('Budget matrisfärg'),backColor:dynamicColor('Budget radbakgrund')}}],
 grid:[{properties:{rowPadding:lit(5),gridVertical:lit(true),gridVerticalColor:color('#E7ECF2'),gridVerticalWeight:lit(.5),gridHorizontal:lit(true),gridHorizontalColor:color('#E7ECF2'),gridHorizontalWeight:lit(.5),outlineWeight:lit(0)}}],
 subTotals:[{properties:{rowSubtotals:lit(true),rowSubtotalsPosition:lit('Top'),columnSubtotals:lit(false),fontFamily:lit('Segoe UI Semibold'),fontSize:lit(11.5),fontColor:color('#0F3163'),backColor:color('#F0F4F9'),applyToHeaders:lit(true)}}],
 rowTotal:[{properties:{fontSize:lit(11.5)}}],columnTotal:[{properties:{fontSize:lit(11.5)}}],
 columnFormatting:[{selector:{metadata:'Budgetscenarier.Budget matrisvärde'},properties:{alignment:lit('Right'),styleHeader:lit(true),styleValues:lit(true),styleTotal:lit(true)}}],
 columnWidth:[{selector:{metadata:'Budgetrader.Rad'},properties:{value:lit(260)}},{selector:{metadata:'Budgetscenarier.Budget matrisvärde'},properties:{value:lit(108)}}]
});
// Ragged leaf levels return BLANK in DAX, preventing blank pseudo-children.
function expansion(mode){return [{roles:['Rows'],levels:rows.map((field,i)=>({queryRefs:['Budgetrader.'+['Rad','Undergrupp','Post'][i]],identityKeys:[field],isCollapsed:mode!=='expand',isPinned:true})),root:mode==='default'?{children:[{identityValues:[{Literal:{Value:"'Övriga rörelsekostnader'"}}],isToggled:true,children:[{identityValues:[{Literal:{Value:"'IT'"}}],isToggled:true}]}]}:{}}];}
const rowExpansion=expansion;expansion=mode=>[...rowExpansion(mode),{roles:['Columns'],levels:['Grupp','Kolumn'].map(p=>({queryRefs:['Budgetkolumner.'+p],identityKeys:[col('Budgetkolumner',p)],isCollapsed:false,isPinned:true})),root:{}}];
matrix.visual.expansionStates=expansion('default');
matrix.visual.query.queryState.Rows.projections[0].displayName='Rad';matrix.visual.query.queryState.Values.projections[0].displayName='';
// Desktop otherwise activates only the month level. Both column levels must be
// active, because the value measure selects Budget/Utfall via the leaf slot.
for(const projection of matrix.visual.query.queryState.Columns.projections)projection.active=true;
matrix.visual.query.queryState.Rows.projections.forEach((projection,i)=>projection.active=i===0);
matrix.visual.query.sortDefinition={sort:[{field:col('Budgetrader','Rad'),direction:'Ascending'},{field:col('Budgetkolumner','Grupp'),direction:'Ascending'},{field:col('Budgetkolumner','Kolumn'),direction:'Ascending'}],isDefaultSort:false};
save(matrix);
text('matrix-help','Klicka på pilen vid en post för att visa underkategorier.',[624,1132,1252,28],11,'#5B6B80');
card('source-note','Budget utfallsnot',[624,1156,1252,24],10,'#5B6B80');
const bmDir=path.join(report,'definition/bookmarks'),bmIndex=read(path.join(bmDir,'bookmarks.json'));
for(let mode=0;mode<2;mode++){
 const name=id('mode-'+mode),containers={};
 containers[modeState.name]={singleVisual:{display:{mode:'hidden'},objects:{merge:{general:selectValues('Budgetjämförelse','Läge',[['Scenario mot utfall','Jämför scenarier'][mode]])}}}};
 containers[b.name]={singleVisual:mode?{}:{display:{mode:'hidden'}}};
 for(const {v,active} of modeVariants)containers[v.name]={singleVisual:active===mode?{}:{display:{mode:'hidden'}}};
 // Comparison is only defined for 2026, so entering it chooses that populated year.
 if(mode)containers[year.name]={singleVisual:{objects:{merge:{general:selectValues('Budgetår','År',[2026])}}}};
 write(path.join(bmDir,name+'.bookmark.json'),{$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/bookmark/2.1.0/schema.json',name,displayName:'Budget – '+['Scenario mot utfall','Jämför scenarier'][mode],options:{targetVisualNames:Object.keys(containers),suppressData:false,suppressDisplay:false,suppressActiveSection:true,applyOnlyToTargetVisuals:true},explorationState:{version:'1.3',activeSection:budget,sections:{[budget]:{visualContainers:containers}}}});
 if(!bmIndex.items.some(b=>b.name===name))bmIndex.items.push({name});
}
for(const kind of ['expand','collapse','reset']){
 const name=id(kind),containers={};
 containers[matrix.name]={singleVisual:{expansionStates:expansion(kind==='reset'?'default':kind)}};
 if(kind==='reset'){
  for(const v of controls)containers[v.name]={singleVisual:{...(v.isHidden?{display:{mode:'hidden'}}:{}),objects:{merge:{general:v.visual.objects.general}}}};
  for(const {v,active} of modeVariants)containers[v.name]={singleVisual:active===0?{}:{display:{mode:'hidden'}}};
 }
 write(path.join(bmDir,name+'.bookmark.json'),{$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/bookmark/2.1.0/schema.json',name,displayName:'Budget – '+{expand:'Expandera alla',collapse:'Fäll ihop',reset:'Återställ filter'}[kind],options:{targetVisualNames:Object.keys(containers),suppressData:false,suppressDisplay:kind!=='reset',suppressActiveSection:true,applyOnlyToTargetVisuals:true},explorationState:{version:'1.3',activeSection:budget,sections:{[budget]:{visualContainers:containers}}}});
 if(!bmIndex.items.some(b=>b.name===name))bmIndex.items.push({name});
}
write(path.join(bmDir,'bookmarks.json'),bmIndex);
// Detail selections must not silently change KPI scope. Slicers still filter all data visuals.
page.visualInteractions=[];for(const v of placements.filter(v=>v.key!=='matrix'))page.visualInteractions.push({source:matrix.name,target:id(budget+':'+v.key),type:'NoFilter'});
write(path.join(report,'definition/pages',budget,'page.json'),page);
require('./polish-report-sidebar.cjs')(report);
// Activate Budget on the Start portal, keeping the established card geometry.
for(const name of fs.readdirSync(path.join(report,'definition/pages',meta.pageOrder[0],'visuals'))){
 const file=path.join(report,'definition/pages',meta.pageOrder[0],'visuals',name,'visual.json');if(!fs.existsSync(file))continue;const v=read(file);
 if(v.position.x!==1174 && v.position.x!==1150)continue;
 if(v.visual.visualType==='actionButton'&&v.position.y===760){v.visual.visualContainerObjects.visualLink=[{properties:{show:lit(true),type:lit('PageNavigation'),navigationSection:lit(budget)}}];for(const t of v.visual.objects.text||[])if(t.selector)t.properties.text=lit('Öppna budget →');write(file,v);}
 if(v.visual.visualType==='textbox'&&[524,668].includes(v.position.y)){v.visual.objects.general[0].properties.paragraphs[0].textRuns[0].value=v.position.y===524?'BUDGET':'Scenarier, utfall och resultaträkning.';write(file,v);}
}
write(path.join(root,'powerbi-ledningsrapport/validation/budget-page-manifest.json'),{page:budget,visuals:placements,default:{year:2026,scenario:'Huvudscenario',mode:'Scenario mot utfall',months:[7,8,9],view:'Månad'},nativeMatrix:true,screenshotsVerified:false});
require('./polish-budget-header.cjs')(report);
require('./polish-budget-page.cjs')(report);
require('./install-budget-statement.cjs')(report);
console.log('Built native Budget page with Excel scenarios, dynamic RR hierarchy and navigation.');
