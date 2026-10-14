// Reference-led executive overview. Native, data-bound visuals only.
module.exports=function(api){
 const {shell,text,card,visual,chart,select,mea,col,lit,color,save}=api;
 const navy='#0F3163',muted='#5B6B80',pale='#E7EDF5',good='#187447',bad='#B83232';
 const noAxis={properties:{show:lit(false)}};
 const qref=name=>'Försäljning.'+name;
 const changeColor=name=>({solid:{color:{expr:{Conditional:{Cases:[
  {Condition:{Comparison:{ComparisonKind:2,Left:mea(name),Right:{Literal:{Value:'0D'}}}},Value:{Literal:{Value:"'"+good+"'"}}},
  {Condition:{Comparison:{ComparisonKind:3,Left:mea(name),Right:{Literal:{Value:'0D'}}}},Value:{Literal:{Value:"'"+bad+"'"}}}
 ],DefaultValue:{Literal:{Value:"'"+muted+"'"}}}}}}});
 function chrome(v){v.visual.visualContainerObjects.padding=[{properties:{top:lit(4),bottom:lit(4),left:lit(8),right:lit(8)}}];return save(v);}
 function kpiCard(v){
  v.visual.objects.layout=[{properties:{paddingUniform:lit(0),backgroundShow:lit(false),backgroundTransparency:lit(100),cellPadding:lit(0)}}];
  v.visual.objects.padding=[{selector:{id:'default'},properties:{paddingSelection:lit('Custom'),leftMargin:lit(0),rightMargin:lit(0),topMargin:lit(0),bottomMargin:lit(0),paddingUniform:lit(0)}}];
  v.visual.objects.value[0].properties.textWrap=lit(false);
  return save(v);
 }
 function panel(key,title,box,subtitle){text(key+'-panel','',box,12,navy,'#FFFFFF');text(key+'-heading',title,[box[0]+24,box[1]+16,box[2]-48,32],13,navy,null,true);if(subtitle)text(key+'-subtitle',subtitle,[box[0]+24,box[1]+52,box[2]-48,28],9,muted);}
 function toggle(key,table,column,box,selected){
  // Reference proportions: compact rail, allowing for the longer Swedish labels.
  const width={'trend-choice':200,'country-choice':176,'products-choice':224}[key];
  box=[box[0]+box[2]-width,box[1]+(box[3]-40)/2,width,40];
  const general=[{properties:{filter:{filter:{Version:2,From:[{Name:'d',Entity:table,Type:0}],Where:[{Condition:{In:{Expressions:[col(table,column,'d')],Values:[[{Literal:{Value:"'"+selected+"'"}}]]}}}]}}}}];
  const v=visual(key,'advancedSlicerVisual',box,{Values:[col(table,column)]},{
   general,
   selection:[{properties:{strictSingleSelect:lit(true),singleSelect:lit(true),selectAllCheckboxEnabled:lit(false)}}],
   layout:[{properties:{orientation:lit(2),rowCount:lit(1),columnCount:lit(2),autoGrid:lit(true),showFixedSize:lit(false),cellPadding:lit(0),rowPadding:lit(0),columnPadding:lit(0),leftOuterMargin:lit(0),rightOuterMargin:lit(0),topOuterMargin:lit(0),bottomOuterMargin:lit(0),backgroundShow:lit(true),backgroundFillColor:color(pale),rectangleRoundedCurve:lit(28)}}],
   actionState:[{properties:{isCalloutValuesAdvanced:lit(true),IsButtonsAdvanced:lit(true)}}],
   value:['default','selected','hover'].map(state=>({selector:{id:state},properties:{show:lit(true),fontSize:lit(9),fontFamily:lit('Segoe UI'),fontColor:color(state==='selected'?'#FFFFFF':navy),horizontalAlignment:lit('center'),verticalAlignment:lit('middle'),textWrap:lit(false)}})),
   label:[{selector:{id:'default'},properties:{show:lit(false)}}],
   fillCustom:['default','selected','hover'].map(state=>({selector:{id:state},properties:{show:lit(true),fillColor:color(state==='selected'?navy:state==='hover'?'#D5DDE7':pale),transparency:lit(0)}})),
   shapeCustomRectangle:['default','selected','hover'].map(state=>({selector:{id:state},properties:{tileShape:lit('pill'),rectangleRoundedCurve:lit(28)}})),
   padding:['default','selected','hover'].map(state=>({selector:{id:state},properties:{paddingSelection:lit('Custom'),leftMargin:lit(4),rightMargin:lit(4),topMargin:lit(0),bottomMargin:lit(0)}})),
   outline:[{selector:{id:'default'},properties:{show:lit(false)}}],
   selectionIcon:[{selector:{id:'default'},properties:{show:lit(false)}}]
  },'',null);
  // One continuous capsule is the shared track; only the selected segment is filled.
  v.visual.visualContainerObjects.background=[{properties:{show:lit(true),color:color(pale),transparency:lit(0)}}];
  v.visual.visualContainerObjects.border=[{properties:{show:lit(true),color:color(pale),radius:lit(28)}}];
  v.visual.visualContainerObjects.padding=[{properties:{top:lit(2),bottom:lit(2),left:lit(2),right:lit(2)}}];
  v.visual.visualContainerObjects.visualHeader=[{properties:{show:lit(false)}}];
  v.visual.query.sortDefinition={sort:[{field:col(table,column),direction:table==='Produktval'?'Ascending':'Descending'}],isDefaultSort:false};save(v);
 }
 function pairedBars(key,box,table,column,actual,prior,change){
  const v=chart(key,'clusteredBarChart','',box,table,column,[actual,prior]);
  v.visual.visualContainerObjects.background=[{properties:{show:lit(false)}}];v.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];
  v.visual.objects.legend=[{properties:{show:lit(false)}}];v.visual.objects.valueAxis=[{properties:{show:lit(false),...(key==='team'?{end:lit(6800000)}:{})}}];
  v.visual.objects.categoryAxis=[{properties:{show:lit(true),showAxisTitle:lit(false),fontSize:lit(9),innerPadding:lit(35),gridlineShow:lit(false),maxMarginFactor:lit(24)}}];
  v.visual.objects.dataPoint=[{properties:{defaultColor:color(navy)}},{selector:{metadata:qref(prior)},properties:{fill:color('#D7DFEA')}}];
  v.visual.objects.labels=[{properties:{show:lit(true)}},{selector:{metadata:qref(prior)},properties:{show:lit(false)}},{selector:{metadata:qref(actual)},properties:{show:lit(true),labelPosition:lit('OutsideEnd'),fontSize:lit(9),showDynamicLabels:lit(true),enableValueDataLabel:lit(true),labelDisplayUnits:lit(1),valueFormatString:lit('0.00,," mn kr"'),valueCustomFormatString:lit('0.00,," mn kr"'),labelPrecision:lit(2),labelContentLayout:lit('MultiLine'),enableDetailDataLabel:lit(!!change),detailContentType:lit('Custom'),detailFontSize:lit(9),detailCustomFormatString:lit('+0.0 %;-0.0 %;0.0 %'),detailFormatString:lit('+0.0 %;-0.0 %;0.0 %'),detailLabelDisplayUnits:lit(1),detailLabelPrecision:lit(1)}}];
  if(change){const caption=actual==='Analysvärde'?'Marknadsbelopp etikett':'Omsättning etikett';v.visual.objects.labels.push({selector:{data:[{dataViewWildcard:{matchingOption:1}}],metadata:qref(actual),highlightMatching:1},properties:{dynamicLabelValue:{expr:mea(caption)},dynamicLabelDetail:{expr:mea(change)},detailColor:changeColor(change)}});v.visual.query.queryState.Tooltips={projections:[{field:mea(change),queryRef:qref(change),nativeQueryRef:'Årsförändring'},{field:mea(caption),queryRef:qref(caption),nativeQueryRef:caption}]};}
  v.visual.query.queryState.Y.projections[0].nativeQueryRef='Aktuellt år';v.visual.query.queryState.Y.projections[1].nativeQueryRef='Föregående år';
  v.visual.query.sortDefinition={sort:[{field:mea(actual),direction:'Descending'}],isDefaultSort:false};chrome(v);
 }
 function ranking(key,title,box,table,column,value,change,top){
  const v=chart(key,'clusteredBarChart','',box,table,column,[value],top);
  v.visual.visualContainerObjects.background=[{properties:{show:lit(false)}}];v.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];
  v.visual.objects.categoryAxis=[{properties:{show:lit(true),showAxisTitle:lit(false),fontSize:lit(10),innerPadding:lit(40),maxMarginFactor:lit(35)}}];v.visual.objects.valueAxis=[noAxis];
  v.visual.objects.labels=[{properties:{show:lit(true),labelPosition:lit('OutsideEnd'),fontSize:lit(10),labelDisplayUnits:lit(value==='Produktvärde'?0:1000000),labelPrecision:lit(2),labelContentLayout:lit('MultiLine'),enableDetailDataLabel:lit(!!change),detailContentType:lit('Custom'),detailCustomFormatString:lit('+0.0 %;-0.0 %;0.0 %'),detailFormatString:lit('+0.0 %;-0.0 %;0.0 %'),detailLabelDisplayUnits:lit(1),detailLabelPrecision:lit(1),detailFontSize:lit(9)}}];
  if(change){v.visual.objects.labels.push({selector:{data:[{dataViewWildcard:{matchingOption:1}}],highlightMatching:1},properties:{dynamicLabelDetail:{expr:mea(change)}}});v.visual.query.queryState.Tooltips={projections:[{field:mea(change),queryRef:qref(change),nativeQueryRef:'Årsförändring'}]};}
  if(value==='Produktvärde'){v.visual.objects.labels[0].properties.labelOverflow=lit(true);v.visual.objects.labels[0].properties.labelContainerMaxWidth=lit(100);v.visual.objects.labels[0].properties.showDynamicLabels=lit(true);v.visual.objects.labels[0].properties.enableValueDataLabel=lit(true);v.visual.objects.labels.push({selector:{data:[{dataViewWildcard:{matchingOption:1}}],highlightMatching:1},properties:{dynamicLabelValue:{expr:mea('Produktvärde etikett')}}});v.visual.query.queryState.Tooltips={projections:[{field:mea('Produktvärde etikett'),queryRef:qref('Produktvärde etikett'),nativeQueryRef:'Belopp eller antal'}]};}
  if(value==='Produktvärde'){
   v.visual.objects.valueAxis=[{properties:{show:lit(false),start:lit(0),end:{expr:mea('Produktaxel max')}}}];
   v.visual.query.queryState.Tooltips.projections.push({field:mea('Produktaxel max'),queryRef:qref('Produktaxel max'),nativeQueryRef:'Skalgräns'});
  }
  chrome(v);
 }
 function sellerList(){
  function sellerCard(...args){
   const v=card(...args);
   v.visual.objects.layout=[{properties:{paddingUniform:lit(0),backgroundShow:lit(false),backgroundTransparency:lit(100),cellPadding:lit(0)}}];
   v.visual.objects.padding=[{selector:{id:'default'},properties:{paddingSelection:lit('Custom'),leftMargin:lit(0),rightMargin:lit(0),topMargin:lit(0),bottomMargin:lit(0),paddingUniform:lit(0)}}];
   v.visual.objects.cardCalloutArea=[{properties:{paddingUniform:lit(0),show:lit(false),backgroundTransparency:lit(100)}},{selector:{id:'default'},properties:{paddingUniform:lit(0),show:lit(false),backgroundTransparency:lit(100)}}];
   v.visual.objects.fillCustom=[{properties:{show:lit(false)}},{selector:{id:'default'},properties:{show:lit(false),transparency:lit(100)}}];
   v.visual.objects.value[0].properties.bold=lit(false);v.visual.objects.value[0].properties.textWrap=lit(false);
   return save(v);
  }
  const intro=sellerCard('seller-share','Säljartopp andel etikett',[1320,536,512,24],9,'@',muted);
  intro.visual.objects.value[0].properties.fontFamily=lit('Segoe UI');save(intro);
  for(let rank=1;rank<=3;rank++){
   const y=568+(rank-1)*68,prefix='Säljartopp '+rank+' ';
   const row=text('seller-row-'+rank,'',[1320,y,520,56],9,navy,pale);
   row.visual.visualContainerObjects.border=[{properties:{show:lit(true),color:color(pale),radius:lit(16)}}];save(row);
   const badge=text('seller-badge-'+rank,'',[1332,y+6,44,44],9,navy,navy);
   badge.visual.visualContainerObjects.border=[{properties:{show:lit(true),color:color(navy),radius:lit(22)}}];save(badge);
   const initials=sellerCard('seller-initials-'+rank,prefix+'initialer',[1332,y+6,44,44],12,'@','#FFFFFF');
   initials.visual.objects.value[0].properties.horizontalAlignment=lit('center');save(initials);
   const name=sellerCard('seller-name-'+rank,prefix+'namn',[1392,y+3,424,26],12,'@',navy);
   name.visual.objects.value[0].properties.fontFamily=lit('Segoe UI');save(name);
   const bar=sellerCard('seller-segments-'+rank,prefix+'segment',[1392,y+26,192,24],8,'@',navy);
   bar.visual.objects.value[0].properties.fontFamily=lit('Segoe UI');save(bar);
   const amount=sellerCard('seller-amount-'+rank,prefix+'etikett',[1588,y+26,88,24],9,'@',navy);
   amount.visual.objects.value[0].properties.fontFamily=lit('Segoe UI');save(amount);
   text('seller-separator-'+rank,'|',[1676,y+26,10,24],9,muted);
   const growth=sellerCard('seller-growth-'+rank,prefix+'förändring etikett',[1690,y+26,144,24],9,'@');
   growth.visual.objects.value[0].properties.fontFamily=lit('Segoe UI');
   growth.visual.objects.value[0].properties.fontColor=changeColor(prefix+'förändring');save(growth);
  }
 }
 shell(1);text('subtitle','Omsättning, bruttovinst, volym och leveranser i en gemensam ledningsvy',[320,220,1280,36],12,muted);select('year','Datum','År',[1672,136,208,80],2025);
 const metrics=[
  ['Omsättning','Omsättning miljoner','Tillväxt mot föregående år','Omsättning','0.0" mn kr"'],
  ['Sålda enheter','Sålda enheter','Enheter YoY','Sålda enheter','#,##0'],
  ['Bruttovinst','Bruttovinst miljoner','Bruttovinst YoY','Bruttovinst','0.0" mn kr"'],
  ['Bruttomarginal','Bruttomarginal','Marginal förändring','Bruttomarginal','0.0 %'],
  ['Leveranser','Leveranser','Leveranser YoY','Leveranser','#,##0']
 ];
 metrics.forEach((m,i)=>{const x=320+i*312;
  text('kpi-panel'+i,'',[x,276,296,200],12,navy,'#FFFFFF');text('kpi-label'+i,m[0],[x+32,292,232,32],15,navy,null,true);
  kpiCard(card('kpi-value'+i,m[1],[x+32,326,232,48],28,m[4]));
  const comparison=text('yoy-label'+i,'Årsförändring:',[x+32,378,84,24],9,muted);
  comparison.visual.visualContainerObjects.general=[{properties:{altText:lit('Förändring mot samma period föregående år')}}];save(comparison);
  const delta=kpiCard(card('yoy'+i,'KPI förändring '+i+' etikett',[x+116,378,148,24],10,'@'));
  delta.visual.objects.value[0].properties.fontColor=changeColor(m[2]);delta.visual.objects.value[0].properties.bold=lit(false);save(delta);
  const spark=visual('sparkline'+i,'lineChart',[x+32,412,232,56],{Category:[col('Datum','Månadsnummer')],Y:[mea(m[3])]},{legend:[{properties:{show:lit(false)}}],categoryAxis:[{properties:{show:lit(false),axisType:lit('Scalar'),start:lit(1),end:lit(12),roundRange:lit(false),maxMarginFactor:lit(0)}}],zoom:[{properties:{show:lit(false),showOnCategoryAxis:lit(false),showOnValueAxis:lit(false)}}],valueAxis:[noAxis],lineStyles:[{properties:{strokeWidth:lit(1.5),strokeColor:color(pale),areaShow:lit(true),areaColor:color(pale),areaMatchStrokeColor:lit(true)}}],dataPoint:[{properties:{defaultColor:color(pale)}}],labels:[{properties:{show:lit(false)}}]},'',null);spark.visual.visualContainerObjects.padding=[{properties:{top:lit(0),bottom:lit(0),left:lit(0),right:lit(0)}}];spark.visual.query.sortDefinition={sort:[{field:col('Datum','Månadsnummer'),direction:'Ascending'}],isDefaultSort:false};save(spark);
 });
 panel('trend','Månadsutveckling',[320,488,952,272],'Aktuellt år jämfört med föregående år');
 toggle('trend-choice','Trendval','Mått',[912,496,336,56],'Omsättning');
 const trend=chart('trend','clusteredColumnChart','',[336,568,920,160],'Datum','Månad',['Trendvärde','Trend föregående år']);
 trend.visual.visualContainerObjects.background=[{properties:{show:lit(false)}}];trend.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];
 trend.visual.query.queryState.Y.projections[0].nativeQueryRef='Aktuellt år';trend.visual.query.queryState.Y.projections[1].nativeQueryRef='Föregående år';
 trend.visual.objects.categoryAxis=[{properties:{show:lit(true),showAxisTitle:lit(false),fontSize:lit(9)}}];trend.visual.objects.valueAxis=[{properties:{show:lit(true),showAxisTitle:lit(false),fontSize:lit(9),labelDisplayUnits:lit(1000000),gridlineShow:lit(true),gridlineColor:color('#E7EDF5'),gridlineStyle:lit('dotted')}}];
 trend.visual.objects.legend=[{properties:{show:lit(false)}}];chrome(trend);
 text('trend-legend','● Aktuellt år',[1076,736,80,24],9,navy);text('trend-legend-prior','● Föregående år',[1156,736,100,24],9,muted);
 panel('market','Omsättning per marknad',[320,784,952,280],'Aktuellt år jämfört med föregående år');
 text('team-heading','Omsättning per säljteam',[880,800,368,32],13,navy,null,true);text('team-subtitle','Aktuellt år jämfört med föregående år',[880,836,368,28],9,muted);
 toggle('country-choice','Analysaxel','Typ',[584,792,264,56],'Land');
 pairedBars('country',[336,868,512,180],'Analysaxel','Namn','Analysvärde','Analys föregående år','Analys årsförändring');
 pairedBars('team',[872,868,384,180],'Säljare','Team','Omsättning','Omsättning föregående år','Tillväxt mot föregående år');
 panel('right','Topp 3 säljare',[1296,488,568,576]);
 sellerList();
 text('products-heading','Topp 5 produkter',[1320,784,208,32],13,navy,null,true);text('products-subtitle','Efter valt mått',[1320,820,160,24],9,muted);
 toggle('products-choice','Produktval','Mått',[1504,780,336,56],'Omsättning');
 ranking('products','',[1312,856,536,184],'Produkter','Produkt','Produktvärde',null,5);
};
