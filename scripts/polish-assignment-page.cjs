// Polish existing visuals without resetting the user's period/filter selections.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?`${v}D`:`'${v}'`}}});
const color=c=>({solid:{color:lit(c)}});
function polish(reportPath){
 const report=reportPath||path.resolve(__dirname,'../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report'),page='30e52cac0a5174639318';
 const dir=path.join(report,'definition/pages',page,'visuals');
 const id=k=>crypto.createHash('sha256').update('assignment-page:'+page+':'+k).digest('hex').slice(0,20);
 const file=k=>path.join(dir,id(k),'visual.json');
 const update=(k,fn)=>{const p=file(k),v=JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));fn(v);fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');};
 const box=(k,x,y,w,h)=>update(k,v=>Object.assign(v.position,{x,y,width:w,height:h}));
 update('kpi-title3',v=>{for(const p of v.visual.objects.general[0].properties.paragraphs)for(const r of p.textRuns)r.textStyle.fontSize='14pt';});
 box('chart-panel0',288,396,460,428);box('chart-panel1',764,396,460,428);box('chart-panel2',1240,396,660,428);
 box('trend-title',288,412,460,40);
 update('trend-title',v=>{for(const e of v.visual.objects.value)Object.assign(e.properties,{fontSize:lit(18),fontFamily:lit('Segoe UI Semibold'),bold:lit(true),textWrap:lit(true)});});
 box('plan-title',780,416,428,36);box('plan-subtitle',780,456,428,28);
 const subtitle=JSON.parse(fs.readFileSync(file('plan-subtitle'),'utf8').replace(/^\uFEFF/,''));subtitle.name=id('trend-subtitle');Object.assign(subtitle.position,{x:304,y:456,width:428,height:28});subtitle.visual.objects.general[0].properties.paragraphs[0].textRuns[0].value='12 månaders historik';fs.mkdirSync(path.dirname(file('trend-subtitle')),{recursive:true});fs.writeFileSync(file('trend-subtitle'),JSON.stringify(subtitle,null,2)+'\n');
 box('heat-title',1256,416,628,36);box('heat-legend',1256,464,628,28);
 update('heat-legend',v=>{v.visual.objects.general[0].properties.paragraphs=[{horizontalTextAlignment:'left',textRuns:[['● ', '#8FB9E1'],['< 80 %     ','#5B6B80'],['● ','#77BFA7'],['80–100 %     ','#5B6B80'],['● ','#DF8980'],['> 100 %','#5B6B80']].map(([value,color])=>({value,textStyle:{fontFamily:'Segoe UI',fontSize:'11pt',color}}))}];});
 box('trend',304,496,428,308);box('bookings',780,496,428,308);box('heat',1256,508,628,292);
 update('trend',v=>{const p=v.visual.objects.valueAxis[0].properties;for(const [key,name] of [['start','Trend axel min'],['end','Trend axel max']])p[key]={expr:{Measure:{Expression:{SourceRef:{Entity:'Planinställning'}},Property:name}}};p.labelPrecision=lit(0);});
 update('heat',v=>{
  v.visual.objects.columnWidth=[{selector:{metadata:'Resurser.Resursgrupp'},properties:{value:lit(136)}},{selector:{metadata:'Planinställning.Plan celltext'},properties:{value:lit(58)}}];
  v.visual.objects.grid[0].properties.rowPadding=lit(10);
  v.visual.objects.columnFormatting=[{selector:{metadata:'Planinställning.Plan celltext'},properties:{alignment:lit('Center'),styleHeader:lit(true),styleValues:lit(true),styleSubtotals:lit(true),styleTotal:lit(true)}}];
  v.visual.objects.columnHeaders[0].properties.alignment=lit('Center');
  v.visual.objects.rowHeaders[0].properties.backColor=color('#FFFFFF');
 });
 update('table',v=>{
  v.visual.query.queryState.Values.projections[0].displayName='Risk';
  v.visual.query.queryState.Values.projections[5].displayName='Planerade timmar, h';v.visual.query.queryState.Values.projections[6].displayName='Utfört hittills, h';
  const forecast=v.visual.query.queryState.Values.projections.at(-1);forecast.field.Measure.Property='Uppdrag prognostext';forecast.queryRef='Planinställning.Uppdrag prognostext';forecast.nativeQueryRef='Prognos slutmarginal';
  for(const e of v.visual.objects.values)if(e.selector?.metadata==='Planinställning.Uppdrag prognos')e.selector.metadata='Planinställning.Uppdrag prognostext';
  v.visual.objects.columnHeaders[0].properties.fontSize=lit(11.5);
  v.visual.objects.values[0].properties.fontSize=lit(11.5);
  for(const e of v.visual.objects.columnWidth){const name=e.selector.metadata;if(name.endsWith('Uppdrag prognos')||name.endsWith('Uppdrag prognostext')){e.selector.metadata='Planinställning.Uppdrag prognostext';e.properties.value=lit(192);}if(name.endsWith('.Uppdrag'))e.properties.value=lit(310);if(name.endsWith('Uppdrag riskikon'))e.properties.value=lit(50);}
  v.visual.objects.columnFormatting=['Uppdrag planerade','Uppdrag hela timmar','Uppdrag kalkyl','Uppdrag prognostext'].map(name=>({selector:{metadata:'Planinställning.'+name},properties:{alignment:lit('Right'),styleHeader:lit(true),styleValues:lit(true)}}));
  v.visual.query.sortDefinition={sort:[{field:{Measure:{Expression:{SourceRef:{Entity:'Planinställning'}},Property:'Uppdrag riskikon'}},direction:'Descending'},{field:{Column:{Expression:{SourceRef:{Entity:'Uppdragsregister'}},Property:'Uppdrag'}},direction:'Ascending'}],isDefaultSort:false};
 });
 console.log('Polished chart headings, panel proportions, heatmap legibility, legend and follow-up table.');
}
module.exports=polish;
if(require.main===module)polish();
