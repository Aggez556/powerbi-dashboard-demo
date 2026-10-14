// Local PBIR authoring. Reuses the established Sales Finance component grammar.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),base=path.join(root,'powerbi-ledningsrapport'),report=path.join(base,'LedningsrapportUtanScroll.Report');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const id=s=>crypto.createHash('sha256').update('Ledningsrapport:'+s).digest('hex').slice(0,20);
const write=(p,v)=>{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');};
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?`${v}D`:`'${v.replace(/'/g,"''")}'`}}});
const color=c=>({solid:{color:lit(c)}}),dynamicColor=n=>({solid:{color:{expr:mea(n)}}});
const col=(t,p,a)=>({Column:{Expression:{SourceRef:a?{Source:a}:{Entity:t}},Property:p}});
const mea=(p,a)=>({Measure:{Expression:{SourceRef:a?{Source:a}:{Entity:'Försäljning'}},Property:p}});
const pages=['Start','Ledningsöversikt'],ids=pages.map(id),placements=[];
let current,tab;
function save(v){write(path.join(report,'definition/pages',current,'visuals',v.name,'visual.json'),v);return v;}
function visual(key,type,box,query={},objects={},title='',background=null){
 const v={$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json',name:id(current+':'+key),position:{x:box[0],y:box[1],width:box[2],height:box[3],z:tab,tabOrder:tab++},visual:{visualType:type,objects,visualContainerObjects:{subTitle:[{properties:{show:lit(false)}}],title:[{properties:{show:lit(!!title),text:lit(title),fontFamily:lit('Segoe UI Semibold'),fontSize:lit(15),fontColor:color('#0F3163')}}],background:[{properties:{show:lit(!!background),color:color(background||'#FFFFFF'),transparency:lit(0)}}],border:[{properties:{show:lit(!!background),color:color('#D5DDE7'),radius:lit(8)}}],padding:[{properties:{top:lit(0),bottom:lit(0),left:lit(0),right:lit(0)}}],general:[{properties:{altText:lit(title||key),keepLayerOrder:lit(true)}}]}}};
 if(Object.keys(query).length)v.visual.query={queryState:Object.fromEntries(Object.entries(query).map(([role,fields])=>[role,{projections:fields.map(field=>{const q=field.Column||field.Measure;return {field,queryRef:q.Expression.SourceRef.Entity+'.'+q.Property,nativeQueryRef:q.Property};})}]))};
 placements.push({page:current,key,type,box});return save(v);
}
function text(key,label,box,size=12,ink='#0B1B30',back=null,bold=false){return visual(key,'textbox',box,{}, {general:[{properties:{paragraphs:label.split('\n').map(line=>({textRuns:[{value:line,textStyle:{fontFamily:bold?'Segoe UI Semibold':'Segoe UI',fontSize:size+'pt',color:ink}}],horizontalTextAlignment:'left'}))}}]},'',back);}
function button(key,label,box,to,selected=false,bookmark=false){
 const ink=selected?'#FFFFFF':to?'#0F3163':'#5B6B80',fill=selected?'#0F3163':to?'#FFFFFF':'#EEF2F7';
 const v=visual(key,'actionButton',box,{}, {text:[{properties:{show:lit(true)}},{selector:{id:'default'},properties:{text:lit(label),fontFamily:lit('Segoe UI Semibold'),fontSize:lit(12),fontColor:color(ink),horizontalAlignment:lit('left'),leftMargin:lit(16),rightMargin:lit(8)}},{selector:{id:'hover'},properties:{fontColor:color(to?'#0F3163':'#5B6B80')}}],fill:[{properties:{show:lit(true)}},{selector:{id:'default'},properties:{fillColor:color(fill),transparency:lit(0)}},{selector:{id:'hover'},properties:{fillColor:color(to?'#FAEBD7':fill),transparency:lit(0)}}],icon:[{properties:{show:lit(false)}}],shape:[{properties:{tileShape:lit('rectangleRounded'),roundEdge:lit(8)}}],outline:[{properties:{show:lit(false)}}]});
 if(to)v.visual.visualContainerObjects.visualLink=[{properties:{show:lit(true),type:lit(bookmark?'Bookmark':'PageNavigation'),[bookmark?'bookmark':'navigationSection']:lit(to)}}];
 v.howCreated='InsertVisualButton';return save(v);
}
function card(key,n,box,size=28,ink='#0F3163',dynamic=false,fmt){
 const props={fontSize:lit(size),fontFamily:lit(size>=20?'Segoe UI Semibold':'Segoe UI'),fontColor:dynamic?dynamicColor(ink):color(ink),horizontalAlignment:lit('left'),textWrap:lit(true),labelDisplayUnits:lit(1),showBlankAs:lit('—')};
 if(fmt)props.customFormatString=lit(fmt);
 return visual(key,'cardVisual',box,{Data:[mea(n)]},{outline:[{selector:{id:'default'},properties:{show:lit(false)}}],fillCustom:[{selector:{id:'default'},properties:{show:lit(false)}}],padding:[{selector:{id:'default'},properties:{paddingUniform:lit(0)}}],layout:[{selector:{id:'default'},properties:{paddingUniform:lit(0)}}],value:[{selector:{id:'default'},properties:props}],label:[{selector:{id:'default'},properties:{show:lit(false)}}]});
}
function selection(t,c,value){return [{properties:{filter:{filter:{Version:2,From:[{Name:'s',Entity:t,Type:0}],Where:[{Condition:{In:{Expressions:[col(t,c,'s')],Values:[[{Literal:{Value:"'"+value+"'"}}]]}}}]}}}}];}
function slicer(key,t,c,box,value,label,hidden=false){
 const v=visual(key,'slicer',box,{Values:[col(t,c)]},{data:[{properties:{mode:lit('Dropdown')}}],header:[{properties:{show:lit(true),text:lit(label),textSize:lit(11),fontColor:color('#5B6B80')}}],selection:[{properties:{strictSingleSelect:lit(true),singleSelect:lit(true),selectAllCheckboxEnabled:lit(false)}}],general:selection(t,c,value)},'','#FFFFFF');
 v.visual.query.sortDefinition={sort:[{field:col(t,c),direction:'Ascending'}],isDefaultSort:false};
 if(hidden)v.isHidden=true;return save(v);
}
function page(i){current=ids[i];tab=0;write(path.join(report,'definition/pages',current,'page.json'),{$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json',name:current,displayName:pages[i],displayOption:'FitToPage',width:1920,height:1200,objects:{background:[{properties:{color:color('#FDF6EC'),transparency:lit(0)}}]}});}
const resources=path.join(report,'StaticResources/RegisteredResources');fs.mkdirSync(resources,{recursive:true});
const theme=read(path.join(root,'themes/aubeco-powerbi.json'));theme.name='LedningsrapportTheme.json';theme.dataColors=['#0F3163','#007956','#9B570B','#4A6BCE','#5B6B80'];
for(const key of ['border','padding','spacing'])delete theme.visualStyles.cardVisual['*'][key];
write(path.join(resources,'LedningsrapportTheme.json'),theme);
const r=read(path.join(report,'definition/report.json'));r.settings.locale='sv-SE';r.themeCollection.customTheme={name:'LedningsrapportTheme.json',type:'RegisteredResources',reportVersionAtImport:{visual:'2.11.0',report:'3.4.0',page:'2.3.1'}};r.resourcePackages=r.resourcePackages.filter(p=>p.name!=='RegisteredResources');r.resourcePackages.push({name:'RegisteredResources',type:'RegisteredResources',items:[{name:'LedningsrapportTheme.json',path:'LedningsrapportTheme.json',type:'CustomTheme'}]});r.objects={outspacePane:[{properties:{expanded:lit(false)}}]};write(path.join(report,'definition/report.json'),r);
const oldPages=read(path.join(report,'definition/pages/pages.json')).pageOrder;
write(path.join(report,'definition/pages/pages.json'),{$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json',pageOrder:ids,activePageName:ids[0]});
// Remove only the empty scaffold page; never touch other projects.
for(const p of oldPages){if(ids.includes(p))continue;const dir=path.resolve(report,'definition/pages',p);if(!dir.startsWith(path.resolve(report)+path.sep))throw Error('Invalid scaffold path');if(fs.readdirSync(dir).length===1&&fs.existsSync(path.join(dir,'page.json'))){fs.unlinkSync(path.join(dir,'page.json'));fs.rmdirSync(dir);}}

page(0);
text('brand','Verksamhet och ekonomi',[64,56,700,64],30,'#0F3163',null,true);
text('eyebrow','VERKSAMHET OCH EKONOMI',[64,148,1200,32],12,'#9B570B',null,true);
text('page-title','En gemensam bild av verksamheten',[64,196,1700,80],34,'#0F3163',null,true);
text('intro','Välj rapportområde för att följa utvecklingen och förstå resultatet.',[64,292,1500,48],15,'#5B6B80');
const areas=['Ledningsöversikt','Försäljningsöversikt','Kunder','Budget','Projekt / beläggning'];
const symbols=['▥','↗','◉','≡','▦'];
for(let i=0;i<5;i++){
 const x=64+i*362;
 text('panel'+i,'',[x,408,338,436],12,'#0F3163','#FFFFFF');
 text('icon'+i,symbols[i],[x+24,432,100,64],32,i===0?'#0F3163':'#5B6B80');
 text('status'+i,i===0?'LEDNING':'PLANERAT RAPPORTOMRÅDE',[x+24,524,290,32],10,i===0?'#9B570B':'#5B6B80',null,true);
 text('area'+i,areas[i],[x+24,572,290,80],i===1?20:22,'#0F3163',null,true);
 if(i===0)text('description'+i,'Omsättning, lönsamhet,\nuppdrag och kunder.',[x+24,668,290,64],13,'#5B6B80');
 else text('description'+i,'Förberett för framtida utbyggnad.',[x+24,668,290,64],12,'#5B6B80');
 button('open'+i,i===0?'Öppna ledningsöversikt →':'Kommer senare',[x+24,760,290,56],i===0?ids[1]:null,i===0);
}
text('footer-panel','',[64,972,1792,136],12,'#0F3163','#FFFFFF');
['Datadrivna beslut','Gemensamma definitioner','Snabbare uppföljning'].forEach((n,i)=>{
 text('benefit'+i,n,[88+i*596,992,552,40],17,'#0F3163',null,true);
 text('benefit-desc'+i,['Från siffror till välgrundade beslut.','Samma period och samma grund för alla nyckeltal.','Från överblick till verksamhetens drivkrafter.'][i],[88+i*596,1044,552,40],12,'#5B6B80');
});
page(1);
text('side-panel','',[0,0,272,1200],12,'#0F3163','#FFFFFF');
button('home','←  Start',[16,16,240,48],ids[0]);
areas.forEach((n,i)=>button('nav'+i,symbols[i]+'  '+n,[16,104+i*72,240,56],i===0?ids[1]:null,i===0));
text('page-title','Ledningsöversikt',[304,24,744,56],32,'#0F3163',null,true);
text('organisation','',[304,80,440,36],16,'#5B6B80');
text('period-heading','Periodtyp',[1080,24,372,24],11,'#5B6B80');
const modes=['R12','Helår','Månad'];
const variants=[];
for(let active=0;active<3;active++)for(let i=0;i<3;i++){
 const v=button(`mode-${active}-${i}`,modes[i],[1080+i*128,56,120,56],id('bookmark:'+modes[i]),active===i,true);
 v.visual.objects.text.filter(x=>x.selector).forEach(x=>{x.properties.horizontalAlignment=lit('center');x.properties.leftMargin=lit(0);x.properties.rightMargin=lit(0);});save(v);
 if(active!==0)v.isHidden=true;save(v);variants.push({v,active});
}
const selector=slicer('periodtyp-state','Periodtyp','Periodtyp',[288,16,200,80],'R12','Periodtyp',true);
const sels=[
 slicer('r12-end','R12val','Period',[1496,24,392,88],'September 2026','Slutmånad'),
 slicer('year','Helårsval','Period',[1496,24,392,88],'2025','År',true),
 slicer('month','Månadsval','Period',[1496,24,392,88],'September 2026','Månad och år',true)];
const periodLabel=card('period-label','Periodtext',[304,120,1584,32],11,'#5B6B80');
periodLabel.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];
periodLabel.visual.objects.value[0].properties.bold=lit(false);save(periodLabel);
const kpis=[['Nettoomsättning','Nettoomsättning Mkr','Nettoomsättning jämförelsetext','Nettoomsättning statusfärg'],['Bruttovinst','Bruttovinst Mkr','Bruttovinst undertext'],['Rörelseresultat','Rörelseresultat Mkr','Rörelseresultat undertext'],['Resultat mot budget','Resultat mot budget Mkr','Budget undertext','Budgetfärg'],['Utförda uppdrag','Utförda uppdrag','Utförda uppdrag jämförelsetext','Utförda uppdrag statusfärg'],['Aktiva kunder','Aktiva kunder','Kunder undertext']];
for(let i=0;i<6;i++){
 const x=288+i*270;
 text('kpi-panel'+i,'',[x,160,254,184],12,'#0F3163','#FFFFFF');
 text('kpi-heading'+i,kpis[i][0],[x+16,176,222,32],13,'#0B1B30',null,true);
 card('kpi-value'+i,kpis[i][1],[x+16,216,222,64],i<4?29:32,i===3?'Budgetfärg':'#0F3163',i===3);
 card('kpi-context'+i,kpis[i][2],[x+16,280,222,56],11,kpis[i][3]||'#5B6B80',!!kpis[i][3]);
}
text('trend-panel','',[288,360,798,416],12,'#0F3163','#FFFFFF');
text('jobs-panel','',[1102,360,798,416],12,'#0F3163','#FFFFFF');
card('trend-heading','Trendrubrik',[312,376,750,48],16);
card('jobs-heading','Uppdragsrubrik',[1126,376,750,48],16);
const axis={show:lit(true),showAxisTitle:lit(false),fontSize:lit(11),fontFamily:lit('Segoe UI'),labelColor:color('#5B6B80')};
const yaxis={...axis,start:lit(0),showAxisTitle:lit(true),titleText:lit('Omsättning, Mkr'),titleFontSize:lit(11),gridlineColor:color('#D5DDE7'),gridlineShow:lit(true),labelDisplayUnits:lit(1),labelPrecision:lit(1)};
const legend={show:lit(true),position:lit('TopRight'),fontSize:lit(10),labelColor:color('#5B6B80'),showTitle:lit(false)};
const combo=visual('revenue-margin','lineStackedColumnComboChart',[312,432,750,320],{Category:[col('Trendaxel','Månad')],Y:[mea('Omsättning')],Y2:[mea('Rörelsemarginal trend')],Tooltips:[mea('Trendomsättning föregående år'),mea('Trendomsättning förändring')]},{legend:[{properties:legend}],categoryAxis:[{properties:axis}],valueAxis:[{properties:{...yaxis,secShow:lit(true),secShowAxisTitle:lit(true),secTitleText:lit('Rörelsemarginal, %'),secTitleFontSize:lit(11),secStart:lit(0),secLabelPrecision:lit(1),secLabelDisplayUnits:lit(1)}}],dataPoint:[{selector:{metadata:'Försäljning.Omsättning'},properties:{fill:dynamicColor('Trendfärg')}},{selector:{metadata:'Försäljning.Rörelsemarginal trend'},properties:{fill:color('#007956')}}],lineStyles:[{properties:{strokeWidth:lit(2.5),showMarker:lit(true),markerSize:lit(6),markerColor:color('#007956')}}],labels:[{properties:{show:lit(false)}}]});
combo.visual.query.queryState.Y2.projections[0].nativeQueryRef='Rörelsemarginal';combo.visual.visualContainerObjects.visualTooltip=[{properties:{show:lit(true)}}];combo.visual.query.sortDefinition={sort:[{field:col('Trendaxel','Månad'),direction:'Ascending'}],isDefaultSort:false};save(combo);
const jobs=visual('jobs','columnChart',[1126,432,750,320],{Category:[col('Trendaxel','Månad')],Y:[mea('Teknisk service'),mea('Bemanning')]},{legend:[{properties:legend}],categoryAxis:[{properties:axis}],valueAxis:[{properties:{...yaxis,titleText:lit('Antal'),labelPrecision:lit(0)}}],dataPoint:[{selector:{metadata:'Försäljning.Teknisk service'},properties:{fill:dynamicColor('Trendfärg')}},{selector:{metadata:'Försäljning.Bemanning'},properties:{fill:color('#007956')}}],labels:[{properties:{show:lit(false)}}]});jobs.visual.query.sortDefinition={sort:[{field:col('Trendaxel','Månad'),direction:'Ascending'}],isDefaultSort:false};save(jobs);
text('areas-panel','',[288,792,798,384],12,'#0F3163','#FFFFFF');
text('areas-heading','Verksamhetsområden',[312,808,750,48],19,'#0F3163',null,true);
const matrix=visual('areas','pivotTable',[312,872,750,220],{Rows:[col('Områden','Område')],Values:[mea('Nettoomsättning Mkr'),mea('Bruttovinst Mkr'),mea('Bruttomarginal'),mea('Utförda uppdrag'),mea('Aktiva kunder')]},{columnHeaders:[{properties:{autoSizeColumnWidth:lit(true),columnAdjustment:lit('growToFit'),fontSize:lit(11),fontColor:color('#0F3163'),backColor:color('#EEF2F7'),wordWrap:lit(true)}}],rowHeaders:[{properties:{fontSize:lit(11),fontColor:color('#5B6B80'),stepped:lit(false),showExpandCollapseButtons:lit(false),wordWrap:lit(true)}}],values:[{properties:{fontSize:lit(11),fontColorPrimary:color('#5B6B80'),backColorPrimary:color('#FFFFFF'),backColorSecondary:color('#FDF6EC')}}],grid:[{properties:{rowPadding:lit(12)}}],subTotals:[{properties:{rowSubtotals:lit(true),rowSubtotalsLabel:lit('Totalt'),rowSubtotalsPosition:lit('Bottom'),fontColor:color('#0F3163'),backColor:color('#EEF2F7'),bold:lit(true)}}]});
matrix.visual.visualContainerObjects.stylePreset=[{properties:{name:lit('None')}}];matrix.visual.query.queryState.Values.projections.forEach((p,i)=>p.nativeQueryRef=['Omsättning','Bruttovinst','Bruttomarginal','Uppdrag','Kunder'][i]);save(matrix);
text('customer-note','Kunder totalt räknas unikt. Samma kund kan köpa inom flera områden.',[312,1128,750,32],10,'#5B6B80');
text('bridge-panel','',[1102,792,798,384],12,'#0F3163','#FFFFFF');
text('bridge-heading','Vad förklarar resultatförändringen?',[1126,808,750,48],19,'#0F3163',null,true);
text('bridge-subtitle','Förändrad bruttovinst och gemensamma kostnader',[1126,856,750,32],12,'#5B6B80');
const bridge=visual('bridge','waterfallChart',[1126,904,750,244],{Category:[col('Bryggaxel','Steg')],Y:[mea('Bryggsteg')]},{legend:[{properties:{show:lit(false)}}],categoryAxis:[{properties:{...axis,fontSize:lit(10)}}],valueAxis:[{properties:{...yaxis,titleText:lit('Mkr'),labelPrecision:lit(1)}}],sentimentColors:[{properties:{increaseFill:color('#007956'),decreaseFill:color('#B42318'),totalFill:color('#0F3163')}}],labels:[{properties:{show:lit(true),fontSize:lit(11),labelDisplayUnits:lit(1),labelPrecision:lit(2),color:color('#0F3163')}}]});bridge.visual.query.sortDefinition={sort:[{field:col('Bryggaxel','Steg'),direction:'Ascending'}],isDefaultSort:false};save(bridge);
bridge.visual.objects.labels[0].properties.labelPosition=lit('Auto');
bridge.visual.objects.valueAxis[0].properties.end={expr:mea('Bryggans övre axelgräns')};save(bridge);
// Native waterfall's final total is calculated by the visual. A dynamic card names that endpoint.
text('bridge-end-mask','',[1760,1100,114,64],12,'#0F3163','#FFFFFF');
card('bridge-end-label','Bryggans slutetikett',[1760,1100,114,64],10,'#5B6B80');

const targets=[selector.name,...sels.map(v=>v.name),...variants.map(v=>v.v.name)];
for(let i=0;i<3;i++){
 const name=id('bookmark:'+modes[i]),containers={};
 containers[selector.name]={singleVisual:{display:{mode:'hidden'},objects:{merge:{general:selection('Periodtyp','Periodtyp',modes[i])}}}};
 sels.forEach((v,j)=>containers[v.name]={singleVisual:{...(i===j?{}:{display:{mode:'hidden'}}),objects:{merge:{general:selection(['R12val','Helårsval','Månadsval'][j],'Period',j===1?'2025':'September 2026')}}}});
 variants.forEach(({v,active})=>containers[v.name]={singleVisual:active===i?{}:{display:{mode:'hidden'}}});
 write(path.join(report,'definition/bookmarks',name+'.bookmark.json'),{$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/bookmark/2.1.0/schema.json',name,displayName:modes[i],options:{targetVisualNames:targets,suppressData:false,suppressDisplay:false,suppressActiveSection:true,applyOnlyToTargetVisuals:false},explorationState:{version:'1.3',activeSection:ids[1],sections:{[ids[1]]:{visualContainers:containers}}}});
}
write(path.join(report,'definition/bookmarks/bookmarks.json'),{$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/bookmarksMetadata/1.0.0/schema.json',items:modes.map(m=>({name:id('bookmark:'+m)}))});
write(path.join(base,'validation/layout.json'),{canvas:{width:1920,height:1200},pages:pages.map((n,i)=>({name:n,id:ids[i]})),placements,intentionalOverlays:'KPI labels/values/context within panels; mode variants and relevant period dropdown selected by bookmarks; native waterfall total endpoint label.'});
console.log(`Built two pages, ${placements.length} native Power BI visuals.`);
require('./style-ledningsrapport-period.cjs');
require('child_process').execFileSync('python',[path.join(__dirname,'fix-ledningsrapport-detail-panels.py')],{stdio:'inherit'});
require('child_process').execFileSync('python',[path.join(__dirname,'fixed-area-table.py')],{stdio:'inherit'});
require('child_process').execFileSync('python',[path.join(__dirname,'fit-ledningsrapport-kpi-text.py')],{stdio:'inherit'});
require('child_process').execFileSync('python',[path.join(__dirname,'kpi-single-line.py')],{stdio:'inherit'});
require('child_process').execFileSync('python',[path.join(__dirname,'match-chart-headings.py')],{stdio:'inherit'});
