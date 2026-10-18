// Update the existing page in place; retain navigation and selected periods.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const base=path.resolve(__dirname,'../powerbi-ledningsrapport'),report=path.join(base,'LedningsrapportUtanScroll.Report');
const page='30e52cac0a5174639318',dir=path.join(report,'definition/pages',page,'visuals');
const id=k=>crypto.createHash('sha256').update('assignment-page:'+page+':'+k).digest('hex').slice(0,20);
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const file=k=>path.join(dir,id(k),'visual.json');
const write=v=>{const p=path.join(dir,v.name,'visual.json');fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');};
const get=k=>read(file(k));
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?`${v}D`:`'${v.replace(/'/g,"''")}'`}}});
const color=c=>({solid:{color:lit(c)}});
const mea=n=>({Measure:{Expression:{SourceRef:{Entity:'Planinställning'}},Property:n}});
const col=(t,n)=>({Column:{Expression:{SourceRef:{Entity:t}},Property:n}});
const dynamic=n=>({solid:{color:{expr:mea(n)}}});
const projection=(field,displayName)=>{const f=field.Measure||field.Column;return {field,queryRef:f.Expression.SourceRef.Entity+'.'+f.Property,nativeQueryRef:f.Property,displayName:displayName||f.Property};};
const modify=(k,fn)=>{const v=get(k);fn(v);write(v);return v;};
const box=(v,x,y,width,height)=>Object.assign(v.position,{x,y,width,height});
function text(k,label,coords){return modify(k,v=>{const run=v.visual.objects.general[0].properties.paragraphs[0].textRuns[0];v.visual.objects.general[0].properties.paragraphs=[{horizontalTextAlignment:'left',textRuns:[{...run,value:label}]}];if(coords)box(v,...coords);});}
function card(k,measure,coords,size=11,ink='#5B6B80'){
 const v=get('kpi-sub0');v.name=id(k);if(coords)box(v,...coords);
 v.position.z=300;
 v.visual.query={queryState:{Data:{projections:[projection(mea(measure))]}}};
 for(const e of v.visual.objects.value){Object.assign(e.properties,{fontSize:lit(size),fontFamily:lit(size>=17?'Segoe UI Semibold':'Segoe UI'),bold:lit(size>=17),textWrap:lit(true),fontColor:color(ink)});delete e.properties.customFormatString;}
 for(const e of v.visual.objects.layout||[])Object.assign(e.properties,{backgroundShow:lit(false),backgroundTransparency:lit(100)});
 for(const e of v.visual.objects.fillCustom||[])Object.assign(e.properties,{show:lit(false),transparency:lit(100)});
 v.visual.visualContainerObjects.general=[{properties:{altText:lit(measure),keepLayerOrder:lit(true)}}];
 write(v);return v;
}
const removed=[];
for(const k of ['plan-context','plan-section']){
 const p=file(k);if(fs.existsSync(p)){fs.unlinkSync(p);fs.rmdirSync(path.dirname(p));removed.push(id(k));}
}
card('history-context','Utfall periodtext',[1088,120,796,28],11,'#0F3163');
modify('history-context',v=>{for(const e of v.visual.objects.value)e.properties.horizontalAlignment=lit('right');});
text('history-section','Historiskt utfall · vald period',[304,154,1580,32]);
text('kpi-title4','Ej debiterbara timmar');text('kpi-title5','Uppdrag över tidskalkyl');
for(let i=0;i<6;i++)modify('kpi-title'+i,v=>{v.position.y=208;v.position.height=52;for(const p of v.visual.objects.general[0].properties.paragraphs)for(const r of p.textRuns)r.textStyle.fontSize='13.5pt';});
for(const [k,n,fmt] of [['kpi-value4','Utfall ej debiterbara timmar','#,##0" h"'],['kpi-value5','Uppdrag över tidskalkyl','#,##0']]){
 modify(k,v=>{v.visual.query={queryState:{Data:{projections:[projection(mea(n))]}}};for(const e of v.visual.objects.value)e.properties.customFormatString=lit(fmt);});
}
card('kpi-sub4','Ej debiterbart jämförelse',[1376,334,224,32],10.5);
card('kpi-sub5','Tidskalkyl jämförelse',[1644,334,224,32],10.5,'#B42318');
for(const [key,name] of [['kpi-sub2','Grad jämförelsefärg'],['kpi-sub3','Marginal jämförelsefärg']])modify(key,v=>{for(const e of v.visual.objects.value)e.properties.fontColor=dynamic(name);});

// Three historical panels; the matrix gets room for twelve monthly columns.
for(const [i,x,w] of [[0,288,420],[1,724,460],[2,1200,700]])modify('chart-panel'+i,v=>box(v,x,396,w,428));
modify('trend-title',v=>box(v,288,412,420,40));
card('trend-subtitle','Historisk trendtext',[304,456,388,28]);
modify('trend',v=>box(v,304,496,388,308));
text('plan-title','Tidsanvändning över tid',[740,416,428,36]);
card('plan-subtitle','Historisk tidsrubrik',[740,456,428,28]);
const booking=modify('bookings',v=>{
 box(v,740,496,428,288);v.visual.visualType='columnChart';
 v.visual.query={queryState:{Category:{projections:[projection(col('Trendaxel','Månad'))]},Y:{projections:[['Tid debiterbar trend','Debiterbart'],['Tid kundarbete trend','Ej debiterbart kundarbete'],['Tid internt trend','Internt arbete'],['Tid ej rapporterat trend','Ej tidrapporterat']].map(([n,l])=>projection(mea(n),l))},Tooltips:{projections:[projection(mea('Tid tillgänglig trend'),'Tillgängliga timmar')]}},sortDefinition:{sort:[{field:col('Trendaxel','Månad'),direction:'Ascending'}],isDefaultSort:false}};
 delete v.visual.objects.lineStyles;
 for(const e of v.visual.objects.valueAxis||[]){delete e.properties.secShow;delete e.properties.sharedAxis;delete e.properties.end;}
 v.visual.objects.legend=[{properties:{show:lit(true),position:lit('Top'),fontSize:lit(10.5),labelColor:color('#405572')}}];
 v.visual.objects.dataPoint=['#0F3163','#65BBA6','#6D8FBE','#B8CBDD'].map((c,i)=>({selector:{metadata:'Planinställning.'+['Tid debiterbar trend','Tid kundarbete trend','Tid internt trend','Tid ej rapporterat trend'][i]},properties:{fill:color(c)}}));
 v.visual.objects.totals=[{properties:{show:lit(false)}}];
 delete v.visual.visualContainerObjects.visualTooltip;
 v.visual.query.queryState.Tooltips.projections.push(projection(mea('Tid kapacitetsavvikelse trend'),'Rapporterat över kapacitet, h'));
});
card('time-summary','Tid summering',[740,788,428,32],11,'#0F3163');
text('heat-title','Debiteringsgrad per resursgrupp',[1216,416,668,36]);
card('heat-subtitle','Historisk heatrubrik',[1216,456,668,28]);
text('heat-legend','● < 75 %      ● 75–82 %      ● ≥ 82 %',[1216,488,668,24]);
modify('heat-legend',v=>{v.visual.objects.general[0].properties.paragraphs[0].textRuns=[['● ','#DF8980'],['< 75 %     ','#5B6B80'],['● ','#8FB9E1'],['75–82 %     ','#5B6B80'],['● ','#65BBA6'],['≥ 82 %','#5B6B80']].map(([value,c])=>({value,textStyle:{fontFamily:'Segoe UI',fontSize:'11pt',color:c}}));});
const heat=modify('heat',v=>{
 box(v,1216,528,668,276);
 v.visual.query.queryState.Columns.projections=[projection(col('Trendaxel','Månad'))];
 v.visual.query.queryState.Values.projections=[projection(mea('Historisk cellgrad'),'Debiteringsgrad')];
 delete v.visual.query.sortDefinition;
 v.visual.objects.values=[{properties:{fontSize:lit(11),fontColorPrimary:color('#0F3163'),wordWrap:lit(false)}},{selector:{data:[{dataViewWildcard:{matchingOption:1}}],metadata:'Planinställning.Historisk cellgrad'},properties:{backColor:dynamic('Historisk cellfärg'),fontColor:color('#0F3163')}}];
 Object.assign(v.visual.objects.columnHeaders[0].properties,{fontSize:lit(10),autoSizeColumnWidth:lit(true),columnAdjustment:lit('growToFit'),alignment:lit('Center')});
 v.visual.objects.columnWidth=[{selector:{metadata:'Resurser.Resursgrupp'},properties:{value:lit(128)}},{selector:{metadata:'Planinställning.Historisk cellgrad'},properties:{value:lit(44)}}];
 v.visual.objects.columnFormatting=[{selector:{metadata:'Planinställning.Historisk cellgrad'},properties:{alignment:lit('Center'),styleHeader:lit(true),styleValues:lit(true),styleSubtotals:lit(true)}}];
 v.visual.objects.subTotals=[{properties:{rowSubtotals:lit(false),columnSubtotals:lit(false)}}];
 v.visual.objects.grid[0].properties.rowPadding=lit(16);
 v.visual.visualContainerObjects.stylePreset=[{properties:{name:lit('None')}}];
 delete v.visual.visualContainerObjects.visualTooltip;
});
card('table-subtitle','Historisk tabellrubrik',[304,898,1520,28]);
const table=modify('table',v=>{
 const fields=[mea('Uppdrag riskikon'),col('Uppdragsregister','Uppdrag'),mea('Uppdrag kund'),col('Uppdragsregister','Typ'),mea('Uppdrag status historisk'),mea('Uppdrag planerade'),mea('Uppdrag timmar periodslut'),mea('Uppdrag kalkyl'),mea('Uppdrag faktisk marginaltext')];
 const labels=['Risk','Uppdrag','Kund','Typ','Status','Planerade timmar','Utfört t.o.m. periodslut','Kalkylmarginal','Faktisk bruttomarginal'];
 v.visual.query.queryState.Values.projections=fields.map((f,i)=>projection(f,labels[i]));
 v.visual.objects.values=v.visual.objects.values.filter(x=>!x.selector||x.selector.metadata!=='Planinställning.Uppdrag prognostext');
 v.visual.objects.values.push({selector:{data:[{dataViewWildcard:{matchingOption:1}}],metadata:'Planinställning.Uppdrag faktisk marginaltext'},properties:{fontColor:dynamic('Uppdrag marginalfärg'),backColor:dynamic('Uppdrag marginalbakgrund')}});
 const widths=[44,300,224,160,120,170,200,160,190];
 v.visual.objects.columnWidth=fields.map((f,i)=>({selector:{metadata:projection(f).queryRef},properties:{value:lit(widths[i])}}));
 v.visual.objects.columnFormatting=fields.slice(5).map(f=>({selector:{metadata:projection(f).queryRef},properties:{alignment:lit('Right'),styleHeader:lit(true),styleValues:lit(true)}}));
 Object.assign(v.visual.objects.columnHeaders[0].properties,{wordWrap:lit(true),autoSizeColumnWidth:lit(true),columnAdjustment:lit('growToFit')});
 v.visual.objects.values[0].properties.fontSize=lit(12);
 v.visual.visualContainerObjects.stylePreset=[{properties:{name:lit('None')}}];
});
text('capacity-note','Tidskalkyl gäller hela uppdraget. Utfall visas till periodslut. — = ingen registrerad intäkt. Ej debiterbara timmar inkluderar internt arbete och ej rapporterad tid.');
const pageFile=path.join(report,'definition/pages',page,'page.json'),p=read(pageFile);
p.visualInteractions=(p.visualInteractions||[]).filter(x=>!removed.includes(x.source)&&!removed.includes(x.target)&&!(x.source===id('trend')&&[heat.name,booking.name].includes(x.target)));
// New historical subtitles/summary must not be filtered by follow-up row/status.
for(const source of [id('status'),table.name])for(const target of [id('heat-subtitle'),id('time-summary')])if(!p.visualInteractions.some(x=>x.source===source&&x.target===target))p.visualInteractions.push({source,target,type:'NoFilter'});
fs.writeFileSync(pageFile,JSON.stringify(p,null,2)+'\n');
// Remove the obsolete future-capacity tooltip, never any other page.
const tooltip='9b71739249a33de0815d',tooltipDir=path.resolve(report,'definition/pages',tooltip);
if(!tooltipDir.startsWith(path.resolve(report,'definition/pages')+path.sep))throw Error('Unsafe tooltip path');
if(fs.existsSync(tooltipDir))fs.rmSync(tooltipDir,{recursive:true});
const metaFile=path.join(report,'definition/pages/pages.json'),meta=read(metaFile);meta.pageOrder=meta.pageOrder.filter(x=>x!==tooltip);if(meta.activePageName===tooltip)meta.activePageName=page;fs.writeFileSync(metaFile,JSON.stringify(meta,null,2)+'\n');
const home=path.join(report,'definition/pages/6ff94a05bddfe7036ec7/visuals/4523c14f425e64cf8df3/visual.json');
if(fs.existsSync(home)){const v=read(home);v.visual.objects.general[0].properties.paragraphs[0].textRuns[0].value='Utförda uppdrag, tidsanvändning och faktisk lönsamhet.';fs.writeFileSync(home,JSON.stringify(v,null,2)+'\n');}
fs.writeFileSync(path.join(base,'validation/historical-assignment-report.json'),JSON.stringify({page,status:'prepared',removedFutureTooltip:tooltip,historicalTimeChart:booking.name,historicalResourceMatrix:heat.name,followupTable:table.name,changedPages:[page,'6ff94a05bddfe7036ec7']},null,2)+'\n');
console.log('Replaced forward-looking page content with historical time, resource utilization and period-end actuals.');
require('./polish-historical-details.cjs');
