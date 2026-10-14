// Native Power BI visuals for the two requested analytical pages.
module.exports=function(api){
 const {shell,text,card,visual,chart,select,mea,col,lit,color,save}=api;
 const noAxis={properties:{show:lit(false)}},axis={properties:{show:lit(true),showAxisTitle:lit(false),fontSize:lit(9),labelDisplayUnits:lit(1)}};
 function subtitle(label){text('subtitle',label,[320,220,1280,36],12,'#5B6B80');select('year','Datum','År',[1672,136,208,72],2025);}
 function kpis(items,sparks=true){items.forEach((m,i)=>{const x=320+i*312;
  text('kpi-panel'+i,'',[x,276,296,232],12,'#0F3163','#FFFFFF');
  text('kpi-label'+i,m[0],[x+16,288,264,36],14,'#0B1B30',null,true);
  card('kpi-value'+i,m[1],[x+16,328,264,64],28,m[4]);
  text('yoy-label'+i,'Årsförändring',[x+16,396,128,32],10,'#5B6B80');
  card('yoy'+i,m[2],[x+152,396,128,32],11,m[5]||'+0.0 %;-0.0 %;0.0 %');
  if(sparks){const v=visual('sparkline'+i,'lineChart',[x+20,428,256,64],{Category:[col('Datum','Månad')],Y:[mea(m[3])]},{legend:[{properties:{show:lit(false)}}],categoryAxis:[noAxis],valueAxis:[noAxis],lineStyles:[{properties:{strokeWidth:lit(1.5),areaShow:lit(true)}}],labels:[{properties:{show:lit(false)}}]},'',null);v.visual.visualContainerObjects.padding=[{properties:{top:lit(0),bottom:lit(0),left:lit(0),right:lit(0)}}];save(v);}
 });}
 function panelPlot(key,title,box,type,query,objects={},choice){
  text(key+'-panel','',box,12,'#0F3163','#FFFFFF');text(key+'-heading',title,[box[0]+16,box[1]+12,box[2]-32,36],13,'#0F3163',null,true);
  const band=choice?72:48;
  const v=visual(key,type,[box[0],box[1]+band,box[2],box[3]-band],query,{legend:[{properties:{show:lit(false)}}],categoryAxis:[axis],valueAxis:[axis],labels:[{properties:{show:lit(false)}}],...objects},'',null);
  if(type==='scatterChart')delete v.visual.objects.labels;
  if(query.Category)v.visual.query.sortDefinition={sort:[{field:query.Category[0],direction:'Ascending'}],isDefaultSort:false};save(v);
  if(choice)select(key+'-choice',choice.table,choice.column,choice.box,choice.selected);
  return v;
 }
 function table(key,title,box,fields,names,sortMeasure){
  const v=visual(key,'tableEx',box,{Values:fields},{columnHeaders:[{properties:{autoSizeColumnWidth:lit(true),columnAdjustment:lit('growToFit'),fontSize:lit(10),wordWrap:lit(true)}}],values:[{properties:{fontSize:lit(11),wordWrap:lit(false)}}],total:[{properties:{totals:lit(false)}}],grid:[{properties:{rowPadding:lit(9)}}]},title);
  v.visual.query.queryState.Values.projections.forEach((p,i)=>p.nativeQueryRef=names[i]);
  v.visual.query.sortDefinition={sort:[{field:mea(sortMeasure),direction:'Descending'}],isDefaultSort:false};save(v);return v;
 }
 function tooltip(v,fields){v.visual.query.queryState.Tooltips={projections:fields.map(p=>({field:mea(p),queryRef:'Försäljning.'+p,nativeQueryRef:p}))};save(v);}
 const pct='+0.0 %;-0.0 %;0.0 %',pp='+0.0" pp";-0.0" pp";0.0" pp"';
 shell(3);subtitle('Säljarresultat, ordervärden och försäljningens fördelning mellan marknader');
 kpis([
  ['Aktiva säljare','Aktiva säljare','Aktiva säljare årsförändring','Aktiva säljare','#,##0'],
  ['Omsättning per säljare','Omsättning per säljare miljoner','Omsättning per säljare årsförändring','Omsättning per säljare','0.0" mn kr"'],
  ['Leveranser','Leveranser','Leveranser YoY','Leveranser','#,##0'],
  ['Genomsnittlig order','Genomsnittlig order','Genomsnittlig order årsförändring','Genomsnittlig order','#,##0" kr"'],
  ['Topp 5 · andel','Topp 5 säljare andel','Topp 5 andel förändring','Topp 5 säljare andel','0.0 %',pp]
 ]);
 const trend=panelPlot('sales-trend','Omsättning och bruttovinst per månad',[320,532,952,228],'lineClusteredColumnComboChart',{Category:[col('Datum','Månad')],Y:[mea('Omsättning miljoner')],Y2:[mea('Bruttovinst miljoner')]},{legend:[{properties:{show:lit(true)}}],lineStyles:[{properties:{strokeWidth:lit(2)}}]});
 trend.visual.query.queryState.Y.projections[0].nativeQueryRef='Omsättning';trend.visual.query.queryState.Y2.projections[0].nativeQueryRef='Bruttovinst';save(trend);
 tooltip(chart('sales-leaderboard','clusteredBarChart','Säljarresultat · topp 10 efter omsättning',[1296,532,568,500],'Säljare','Säljare',['Omsättning miljoner'],10),['Tillväxt mot föregående år','Bruttovinst','Bruttomarginal','Leveranser']);
 table('sales-country-table','Försäljning per land',[320,784,472,248],[col('Kunder','Land'),mea('Omsättning miljoner'),mea('Tillväxt mot föregående år'),mea('Omsättning andel land')],['Land','Omsättning','År %','Andel'],'Omsättning miljoner');
 panelPlot('country-trends','Omsättning · trend per land',[816,784,456,248],'lineChart',{Category:[col('Datum','Månad')],Rows:[col('Kunder','Land')],Y:[mea('Omsättning miljoner')]},{categoryAxis:[noAxis],valueAxis:[noAxis],smallMultiplesLayout:[{properties:{layoutType:lit('custom'),rowCount:lit(4),columnCount:lit(1),gridPadding:lit(2),gridLineShow:lit(false)}}],lineStyles:[{properties:{strokeWidth:lit(1.5)}}]});
};
