const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),base=path.join(root,'powerbi-sales-finance'),report=path.join(base,'AubecoSalesFinance.Report');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,'')),id=s=>crypto.createHash('sha256').update(s).digest('hex').slice(0,20);
const write=(p,v)=>{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');};
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?`${v}D`:`'${v.replace(/'/g,"''")}'`}}}),color=c=>({solid:{color:lit(c)}});
const col=(t,p,a)=>({Column:{Expression:{SourceRef:a?{Source:a}:{Entity:t}},Property:p}}),mea=(p,a)=>({Measure:{Expression:{SourceRef:a?{Source:a}:{Entity:'Försäljning'}},Property:p}});
const pageKeys=['Hem','Executive Overview','Finance & Profitability','Sales Analytics','Transactions'];
const pages=['Hem','Ledningsöversikt','Ekonomi och lönsamhet','Försäljningsanalys','Transaktioner'],ids=pageKeys.map(x=>id('sales-finance:'+x));
const first=read(path.join(report,'definition/pages/pages.json')).pageOrder[0];ids[0]=first;
write(path.join(report,'definition/pages/pages.json'),{$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json',pageOrder:ids,activePageName:ids[0]});
const resources=path.join(report,'StaticResources/RegisteredResources');fs.mkdirSync(resources,{recursive:true});
const theme=read(path.join(root,'themes/aubeco-powerbi.json'));theme.name='AubecoSalesFinanceTheme.json';theme.dataColors=['#0F3163','#BCC8D8','#F7BA6B','#4A6BCE','#9B570B'];for(const x of ['border','padding','spacing'])delete theme.visualStyles.cardVisual['*'][x];write(path.join(resources,theme.name),theme);
const logo='AubecoWordmark202610070001.png';fs.copyFileSync(path.join(root,'assets/aubeco/aubeco-header-wordmark.png'),path.join(resources,logo));
const bg='PortalGrid202610070001.svg';fs.writeFileSync(path.join(resources,bg),`<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080"><defs><pattern id="g" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#0F3163" stroke-opacity=".035"/></pattern><radialGradient id="a"><stop stop-color="#F7BA6B" stop-opacity=".17"/><stop offset="1" stop-color="#FDF6EC" stop-opacity="0"/></radialGradient></defs><rect width="1920" height="1080" fill="#FDF6EC"/><rect width="1920" height="1080" fill="url(#g)"/><ellipse cx="1810" cy="40" rx="670" ry="420" fill="url(#a)"/></svg>`);
const iconFiles=['Overview','Profit','Growth','Ledger'].map(n=>'PortalIcon'+n+'20261007.svg');
const iconPaths=['<rect x="18" y="18" width="11" height="11" rx="2"/><rect x="35" y="18" width="11" height="11" rx="2"/><rect x="18" y="35" width="11" height="11" rx="2"/><rect x="35" y="35" width="11" height="11" rx="2"/>','<path d="M20 44V30M32 44V20M44 44V26"/>','<path d="M18 44l12-12 8 5 10-17M37 20h11v11"/>','<rect x="21" y="17" width="22" height="30" rx="3"/><path d="M27 25h10M27 32h10M27 39h6"/>'];
iconFiles.forEach((file,i)=>fs.writeFileSync(path.join(resources,file),`<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><rect x=".5" y=".5" width="63" height="63" rx="12" fill="#FDF6EC" stroke="#D5DDE7"/><g fill="none" stroke="${i===2?'#9B570B':'#4A6BCE'}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${iconPaths[i]}</g></svg>`));
const r=read(path.join(report,'definition/report.json'));r.settings.locale='sv-SE';r.themeCollection.customTheme={name:theme.name,type:'RegisteredResources',reportVersionAtImport:{visual:'2.11.0',report:'3.4.0',page:'2.3.1'}};r.resourcePackages=r.resourcePackages.filter(p=>p.name!='RegisteredResources');r.resourcePackages.push({name:'RegisteredResources',type:'RegisteredResources',items:[{name:theme.name,path:theme.name,type:'CustomTheme'},{name:logo,path:logo,type:'Image'},{name:bg,path:bg,type:'Image'},...iconFiles.map(file=>({name:file,path:file,type:'Image'})),...Array.from({length:5},(_,i)=>({name:'TransactionKpi'+i+'.svg',path:'TransactionKpi'+i+'.svg',type:'Image'}))]});write(path.join(report,'definition/report.json'),r);
let current,tab;const placements=[];
function save(v){write(path.join(report,'definition/pages',current,'visuals',v.name,'visual.json'),v);return v;}
function visual(key,type,box,query={},objects={},title='',background='#FFFFFF'){
 const v={$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json',name:id(current+':'+key),position:{x:box[0],y:box[1],width:box[2],height:box[3],z:tab,tabOrder:tab++},visual:{visualType:type,objects,visualContainerObjects:{subTitle:[{properties:{show:lit(false)}}],title:[{properties:{show:lit(!!title),text:lit(title),fontFamily:lit('Segoe UI Semibold'),fontSize:lit(13),fontColor:color('#0F3163')}}],background:[{properties:{show:lit(!!background),color:color(background||'#FFFFFF'),transparency:lit(0)}}],border:[{properties:{show:lit(!!background),color:color('#D5DDE7'),radius:lit(12)}}],padding:[{properties:{top:lit(10),bottom:lit(10),left:lit(16),right:lit(16)}}],general:[{properties:{altText:lit(title||key)}}]}}};
 if(Object.keys(query).length)v.visual.query={queryState:Object.fromEntries(Object.entries(query).map(([role,fields])=>[role,{projections:fields.map(field=>{const q=field.Column||field.Measure;return {field,queryRef:q.Expression.SourceRef.Entity+'.'+q.Property,nativeQueryRef:q.Property};})}]))};
 placements.push({page:current,key,type,box,fields:Object.values(query).flat()});return save(v);
}
function text(key,label,box,size=12,ink='#0B1B30',back=null,bold=false){const v=visual(key,'textbox',box,{}, {general:[{properties:{paragraphs:label.split('\n').map(line=>({textRuns:[{value:line,textStyle:{fontFamily:bold?'Segoe UI Semibold':'Segoe UI',fontSize:size+'pt',color:ink}}],horizontalTextAlignment:'left'}))}}]},'',back);v.visual.visualContainerObjects.padding=[{properties:{top:lit(0),bottom:lit(0),left:lit(0),right:lit(0)}}];if(!back)v.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];return save(v);}
function centerIcon(key,symbol,box,ink){text(key+'-panel','',box,12,ink,'#FDF6EC');const v=text(key,symbol,[box[0]+8,box[1]+16,48,48],20,ink,null,true);v.visual.objects.general[0].properties.paragraphs[0].horizontalTextAlignment='center';save(v);}
function image(key,file,box,back=null){const v=visual(key,'image',box,{}, {image:[{properties:{sourceType:lit('image'),sourceFile:{image:{name:lit(file),url:{expr:{ResourcePackageItem:{PackageName:'RegisteredResources',PackageType:1,ItemName:file}}},scaling:lit('Fit')}},fit:lit('Fit'),backgroundEnabled:lit(false),strokeShow:lit(false)}}]},'',back);v.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];return save(v);}
function button(key,label,box,to,selected=false){const fill=selected?'#0F3163':'#FFFFFF',ink=selected?'#FFFFFF':'#0F3163';const v=visual(key,'actionButton',box,{}, {text:[{properties:{show:lit(true)}},{selector:{id:'default'},properties:{text:lit(label),fontFamily:lit('Segoe UI Semibold'),fontSize:lit(11),fontColor:color(ink),horizontalAlignment:lit('center'),topMargin:lit(0),bottomMargin:lit(0),leftMargin:lit(8),rightMargin:lit(8)}},{selector:{id:'hover'},properties:{fontColor:color('#FFFFFF')}}],fill:[{properties:{show:lit(true)}},{selector:{id:'default'},properties:{fillColor:color(fill),transparency:lit(0)}},{selector:{id:'hover'},properties:{fillColor:color('#4A6BCE'),transparency:lit(0)}}],icon:[{properties:{show:lit(false),placement:lit('left')}}],shape:[{properties:{tileShape:lit('rectangleRounded'),roundEdge:lit(12)}}],outline:[{properties:{show:lit(false)}}]},'',null);v.visual.visualContainerObjects.visualLink=[{properties:{show:lit(true),type:lit('PageNavigation'),navigationSection:lit(to)}}];v.visual.visualContainerObjects.padding=[{properties:{top:lit(0),bottom:lit(0),left:lit(0),right:lit(0)}}];v.visual.visualContainerObjects.padding=[{properties:{top:lit(0),bottom:lit(0),left:lit(0),right:lit(0)}}];v.visual.visualContainerObjects.padding=[{properties:{top:lit(0),bottom:lit(0),left:lit(0),right:lit(0)}}];v.howCreated='InsertVisualButton';return save(v);}
function select(key,t,c,box,selected,mode='Dropdown'){
 const obj={data:[{properties:{mode:lit(mode)}}],header:[{properties:{show:lit(false)}}],selection:[{properties:{strictSingleSelect:lit(true),singleSelect:lit(true),selectAllCheckboxEnabled:lit(false)}}]};
 if(selected!==undefined)obj.general=[{properties:{filter:{filter:{Version:2,From:[{Name:'d',Entity:t,Type:0}],Where:[{Condition:{In:{Expressions:[col(t,c,'d')],Values:[[{Literal:{Value:typeof selected==='number'?selected+'L':"'"+selected+"'"}}]]}}}]}}}}];
 if(key==='year'){
  box=[box[0],box[1],box[2],80];
  obj.header=[{properties:{show:lit(true),text:lit('År'),textSize:lit(10),fontColor:color('#0F3163')}}];
 }
 const v=visual(key,'slicer',box,{Values:[col(t,c)]},obj);
 if(key==='year'){
  v.visual.visualContainerObjects.padding=[{properties:{top:lit(8),bottom:lit(8),left:lit(16),right:lit(16)}}];
  save(v);
 }
 return v;
}
function monthSelect(){
 const v=select('month','Datum','Månad',[1400,136,248,80]);
 v.visual.objects.selection=[{properties:{strictSingleSelect:lit(false),singleSelect:lit(false),selectAllCheckboxEnabled:lit(true)}}];
 v.visual.objects.header=[{properties:{show:lit(true),text:lit('Månad'),textSize:lit(10),fontColor:color('#0F3163')}}];
 v.visual.visualContainerObjects.padding=[{properties:{top:lit(8),bottom:lit(8),left:lit(16),right:lit(16)}}];
 return save(v);
}
function card(key,measure,box,size=30,fmt,ink='#0F3163'){
 const props={fontSize:lit(size),fontFamily:lit('Segoe UI Semibold'),fontColor:color(ink),horizontalAlignment:lit('left'),labelDisplayUnits:lit(1),showBlankAs:lit('–')};if(fmt)props.customFormatString=lit(fmt);
 const v=visual(key,'cardVisual',box,{Data:[mea(measure)]},{outline:[{selector:{id:'default'},properties:{show:lit(false)}}],fillCustom:[{selector:{id:'default'},properties:{show:lit(false)}}],cardCalloutArea:[{properties:{paddingUniform:lit(0),show:lit(false),backgroundTransparency:lit(100)}}],value:[{selector:{id:'default'},properties:props}],label:[{selector:{id:'default'},properties:{show:lit(false)}}]},'',null);
 v.visual.visualContainerObjects.padding=[{properties:{top:lit(0),bottom:lit(0),left:lit(0),right:lit(0)}}];v.visual.visualContainerObjects.spacing=[{selector:{id:'default'},properties:{customizeSpacing:lit(true),verticalSpacing:lit(-6)}}];return save(v);
}
function chart(key,type,title,box,table,column,measures,top){
 const v=visual(key,type,box,{Category:[col(table,column)],Y:measures.map(x=>mea(x))},{legend:[{properties:{show:lit(measures.length>1)}}],categoryAxis:[{properties:{show:lit(true),showAxisTitle:lit(false),fontSize:lit(10)}}],valueAxis:[{properties:{show:lit(true),showAxisTitle:lit(false),start:lit(0),fontSize:lit(10)}}],labels:[{properties:{show:lit(false)}}]},title);
 v.visual.query.sortDefinition={sort:[{field:top?mea(measures[0]):col(table,column),direction:top?'Descending':'Ascending'}],isDefaultSort:false};
 if(top)v.filterConfig={filters:[{name:id(key+'top'),field:col(table,column),type:'TopN',howCreated:'User',filter:{Version:2,From:[{Name:'sub',Type:2,Expression:{Subquery:{Query:{Version:2,From:[{Name:'c',Entity:table,Type:0},{Name:'f',Entity:'Försäljning',Type:0}],Select:[{...col(table,column,'c'),Name:'field'}],OrderBy:[{Direction:2,Expression:mea(measures[0],'f')}],Top:top}}}},{Name:'c',Entity:table,Type:0}],Where:[{Condition:{In:{Expressions:[col(table,column,'c')],Table:{SourceRef:{Source:'sub'}}}}}]}}]};
 return save(v);
}
function chartWithChoice(key,type,title,box,table,column,measures,choice,top){
 text(key+'-panel','',box,12,'#0F3163','#FFFFFF');
 text(key+'-heading',title,[box[0]+16,box[1]+12,box[2]-32,36],13,'#0F3163',null,true);
 const v=chart(key,type,'',[box[0],box[1]+72,box[2],box[3]-72],table,column,measures,top);
 v.visual.visualContainerObjects.background=[{properties:{show:lit(false)}}];
 v.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];
 if(measures.length===2)v.visual.query.queryState.Y.projections.forEach((projection,i)=>projection.nativeQueryRef=i?'Föregående år':'Aktuellt år');
 save(v);select(key+'-choice',choice.table,choice.column,choice.box,choice.selected);
}
function page(index){current=ids[index];tab=0;write(path.join(report,'definition/pages',current,'page.json'),{$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json',name:current,displayName:pages[index],displayOption:'FitToPage',width:1920,height:1080,objects:{background:[{properties:{color:color(index===0?'#FDF6EC':'#EEF2F7'),transparency:lit(0)}}]}});}
page(0);image('portal-grid',bg,[0,0,1920,1080]);image('logo',logo,[64,40,224,76],'#09224A');
text('title','Försäljning och ekonomi',[64,192,1200,80],34,'#0F3163',null,true);text('intro','En gemensam vy över omsättning, lönsamhet och försäljning.\nFrån ledningsöversikt till detaljerade transaktioner.',[64,280,1200,64],13,'#5B6B80');
const labels=pages.slice(1),tags=['LEDNING','LÖNSAMHET','TILLVÄXT','KONTROLL'],icons=['▦','▥','↗','≡'],descs=['Omsättning, vinst och volym\nför snabbare beslut.','Marginaler, kostnadsstruktur\noch verksamhetens drivkrafter.','Produkter, marknader och säljare\ni en gemensam analys.','Sök och granska försäljningsrader\nför kontroll och uppföljning.'];
for(let i=0;i<4;i++){const x=64+i*454;text('panel'+i,'',[x,384,430,384],12,'#0F3163','#FFFFFF');centerIcon('icon'+i,icons[i],[x+32,416,64,64],i===2?'#9B570B':'#4A6BCE');text('tag'+i,tags[i],[x+32,504,352,36],11,'#9B570B',null,true);text('area'+i,labels[i],[x+32,548,368,56],20,'#0F3163',null,true);text('description'+i,descs[i],[x+32,612,368,72],12,'#5B6B80');button('open'+i,['Öppna översikt →','Visa lönsamhet →','Analysera försäljning →','Visa transaktioner →'][i],[x+32,696,366,48],ids[i+1],true);}
text('footer-panel','',[64,928,1792,104],12,'#0F3163','#FFFFFF');const benefits=['Datadrivna beslut','Gemensamma definitioner','Insikter som leder vidare','Snabbare uppföljning'];benefits.forEach((b,i)=>{text('benefit'+i,b,[88+i*448,944,400,40],14,'#0F3163',null,true);text('benefitdesc'+i,['Från siffror till välgrundade beslut.','En bild av försäljning och ekonomi.','Identifiera trender och möjligheter.','Mindre manuellt arbete.'][i],[88+i*448,984,400,32],10,'#5B6B80');});
function shell(index){page(index);text('header-panel','',[0,0,1920,96],12,'#0F3163','#FFFFFF');image('logo',logo,[24,12,240,72],'#09224A');text('suite-title','FÖRSÄLJNING OCH EKONOMI',[320,24,1256,56],27,'#0F3163',null,true);text('side-panel','',[0,96,288,984],12,'#0F3163','#E7EDF5');['Hem',...labels].forEach((label,i)=>button('nav'+i,(i===index?'●  ':'')+label,[20,192+i*72,248,48],ids[i],i===index));text('breadcrumbs','HEM  ›  '+pages[index].toUpperCase(),[320,116,index<=3?1056:1280,32],10,'#5B6B80');text('page-title',pages[index],[320,156,index<=3?1056:1280,64],28,'#0F3163',null,true);if(index>=1&&index<=3)monthSelect();}
require('./sales-finance-overview.cjs')({shell,text,card,visual,chart,select,mea,col,lit,color,save});
for(let index=5;index<5;index++){shell(index);text('pending-panel','',[416,340,1280,392],12,'#0F3163','#FFFFFF');text('pending-title','Nästa rapportområde',[464,388,1120,64],28,'#0F3163',null,true);text('pending-copy',pages[index]+' är förberedd i navigationen.\nDen här undersidan byggs i nästa steg.\n\nLedningsöversikt är den första färdiga analyssidan.',[464,472,1120,128],16,'#5B6B80');button('pending-home','Till startsidan →',[464,648,320,48],ids[0],true);}
require('./sales-finance-analysis.cjs')({shell,text,card,visual,chart,select,mea,col,lit,color,save});
require('./sales-finance-finance.cjs')({shell,text,card,visual,chart,select,mea,col,lit,color,save});
require('./sales-finance-transactions.cjs')({shell,text,card,visual,image,select,mea,col,lit,color,save});
const retiredVisuals=[...['status-panel', 'status', 'scope-panel', 'scope-areas', 'scope-view', 'scope-description'].map(key=>[ids[0],key]),...ids.slice(1).flatMap(page=>['nav-note','data-note'].map(key=>[page,key])),[ids[0],'suite'],[ids[0],'eyebrow'],[ids[0],'scope'],[ids[1],'axis-choice'],[ids[1],'product-choice'],...ids.slice(2,5).flatMap(page=>['pending-panel','pending-title','pending-copy','pending-home'].map(key=>[page,key]))];
for(const [pageName,key] of retiredVisuals){const dir=path.join(report,'definition/pages',pageName,'visuals',id(pageName+':'+key));const file=path.join(dir,'visual.json');if(!file.startsWith(report+path.sep))throw Error('Invalid cleanup target');if(fs.existsSync(file))fs.unlinkSync(file);if(fs.existsSync(dir)&&fs.readdirSync(dir).length===0)fs.rmdirSync(dir);}
// Remove obsolete visuals only from the page being comprehensively rebuilt.
for(const rebuiltPage of [ids[1],ids[2],ids[3]]){
const overviewDir=path.join(report,'definition/pages',rebuiltPage,'visuals');
const overviewKeep=new Set(placements.filter(p=>p.page===rebuiltPage).map(p=>id(rebuiltPage+':'+p.key)));
for(const name of fs.readdirSync(overviewDir)){
 if(!/^[0-9a-f]{20}$/.test(name)||overviewKeep.has(name))continue;
 const dir=path.join(overviewDir,name),file=path.join(dir,'visual.json');
 if(fs.existsSync(file))fs.unlinkSync(file);
 if(fs.readdirSync(dir).length===0)fs.rmdirSync(dir);
}
}
write(path.join(base,'validation/layout.json'),{pages:pages.map((name,i)=>({name,id:ids[i],status:'built'})),placements,canvas:{width:1920,height:1080},intentionalOverlays:'Background panels, card labels/value/sparklines, chart metric selectors, header logo'});
console.log(`Built all five pages; ${placements.length} native visuals.`);
require('./apply-sales-finance-feedback.cjs');


