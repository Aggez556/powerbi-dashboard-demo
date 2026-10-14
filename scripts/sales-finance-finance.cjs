// Reference-led finance page. Queries, filters and presentation stay native PBIR.
module.exports=function(api){
 const {shell,text,card,visual,chart,select,mea,col,lit,color,save}=api;
 const navy='#0F3163',muted='#5B6B80',pale='#E7EDF5',good='#187447',bad='#B83232';
 const qref=n=>'Försäljning.'+n,noAxis={properties:{show:lit(false)}};
 function clean(v){v.visual.visualContainerObjects.padding=[{properties:{top:lit(0),bottom:lit(0),left:lit(0),right:lit(0)}}];v.visual.visualContainerObjects.visualHeader=[{properties:{show:lit(false)}}];return save(v);}
 function flatCard(key,measure,box,size,fmt,ink=navy){
  const v=card(key,measure,box,size,fmt,ink);
  v.visual.objects.layout=[{properties:{paddingUniform:lit(0),backgroundShow:lit(false),backgroundTransparency:lit(100),cellPadding:lit(0)}}];
  v.visual.objects.padding=[{selector:{id:'default'},properties:{paddingSelection:lit('Custom'),leftMargin:lit(0),rightMargin:lit(0),topMargin:lit(0),bottomMargin:lit(0),paddingUniform:lit(0)}}];
  v.visual.objects.value[0].properties.textWrap=lit(false);v.visual.objects.value[0].properties.bold=lit(false);return clean(v);
 }
 function changeColor(name,inverse=false){return {solid:{color:{expr:{Conditional:{Cases:[
  {Condition:{Comparison:{ComparisonKind:2,Left:mea(name),Right:{Literal:{Value:'0D'}}}},Value:{Literal:{Value:"'"+(inverse?bad:good)+"'"}}},
  {Condition:{Comparison:{ComparisonKind:3,Left:mea(name),Right:{Literal:{Value:'0D'}}}},Value:{Literal:{Value:"'"+(inverse?good:bad)+"'"}}}
 ],DefaultValue:{Literal:{Value:"'"+muted+"'"}}}}}}};}
 function panel(key,title,box,subtitle){text(key+'-panel','',box,12,navy,'#FFFFFF');text(key+'-heading',title,[box[0]+24,box[1]+16,box[2]-48,32],13,navy,null,true);if(subtitle)text(key+'-subtitle',subtitle,[box[0]+24,box[1]+52,box[2]-48,24],9,muted);}
 function toggle(){
  const selected=process.env.FINANCE_PREVIEW_MODE||'Team',table='Finansaxel',column='Val';
  const v=visual('finance-choice','advancedSlicerVisual',[1060,504,188,40],{Values:[col(table,column)]},{
   general:[{properties:{filter:{filter:{Version:2,From:[{Name:'d',Entity:table,Type:0}],Where:[{Condition:{In:{Expressions:[col(table,column,'d')],Values:[[{Literal:{Value:"'"+selected+"'"}}]]}}}]}}}}],
   selection:[{properties:{strictSingleSelect:lit(true),singleSelect:lit(true),selectAllCheckboxEnabled:lit(false)}}],
   layout:[{properties:{orientation:lit(2),rowCount:lit(1),columnCount:lit(2),autoGrid:lit(true),showFixedSize:lit(false),cellPadding:lit(0),rowPadding:lit(0),columnPadding:lit(0),leftOuterMargin:lit(0),rightOuterMargin:lit(0),topOuterMargin:lit(0),bottomOuterMargin:lit(0),backgroundShow:lit(true),backgroundFillColor:color(pale),rectangleRoundedCurve:lit(28)}}],
   actionState:[{properties:{isCalloutValuesAdvanced:lit(true),IsButtonsAdvanced:lit(true)}}],
   value:['default','selected','hover'].map(state=>({selector:{id:state},properties:{show:lit(true),fontSize:lit(9),fontFamily:lit('Segoe UI'),fontColor:color(state==='selected'?'#FFFFFF':navy),horizontalAlignment:lit('center'),verticalAlignment:lit('middle'),textWrap:lit(false)}})),
   label:[{selector:{id:'default'},properties:{show:lit(false)}}],
   fillCustom:['default','selected','hover'].map(state=>({selector:{id:state},properties:{show:lit(true),fillColor:color(state==='selected'?navy:state==='hover'?'#D5DDE7':pale),transparency:lit(0)}})),
   shapeCustomRectangle:['default','selected','hover'].map(state=>({selector:{id:state},properties:{tileShape:lit('pill'),rectangleRoundedCurve:lit(28)}})),
   padding:['default','selected','hover'].map(state=>({selector:{id:state},properties:{paddingSelection:lit('Custom'),leftMargin:lit(4),rightMargin:lit(4),topMargin:lit(0),bottomMargin:lit(0)}})),
   outline:[{selector:{id:'default'},properties:{show:lit(false)}}],selectionIcon:[{selector:{id:'default'},properties:{show:lit(false)}}]
  },'',null);
  v.visual.visualContainerObjects.background=[{properties:{show:lit(true),color:color(pale),transparency:lit(0)}}];v.visual.visualContainerObjects.border=[{properties:{show:lit(true),color:color(pale),radius:lit(28)}}];
  v.visual.visualContainerObjects.padding=[{properties:{top:lit(2),bottom:lit(2),left:lit(2),right:lit(2)}}];
  v.visual.query.sortDefinition={sort:[{field:col(table,column),direction:'Ascending'}],isDefaultSort:false};save(v);
 }
 shell(2);
 text('subtitle','Bruttovinst, kostnadsstruktur och marginaler per produkt och marknad',[320,220,1040,36],12,muted);
 select('year','Datum','År',[1672,136,208,72],2025);
 const kpis=[
  ['Bruttovinst','Bruttovinst miljoner','Bruttovinst YoY','Bruttovinst','0.0" mn kr"'],
  ['Bruttomarginal','Bruttomarginal','Marginal förändring','Bruttomarginal','0.0 %'],
  ['Varukostnad','Kostnad miljoner','Kostnad årsförändring','Kostnad','0.0" mn kr"'],
  ['Omsättning per enhet','Omsättning per enhet','Omsättning per enhet årsförändring','Omsättning per enhet','#,##0.0" kr"'],
  ['Bruttovinst per enhet','Bruttovinst per enhet','Bruttovinst per enhet årsförändring','Bruttovinst per enhet','#,##0.0" kr"']
 ];
 kpis.forEach((m,i)=>{const x=320+i*312;
  text('kpi-panel'+i,'',[x,276,296,200],12,navy,'#FFFFFF');text('kpi-label'+i,m[0],[x+32,292,232,32],i>2?14:15,navy,null,true);
  flatCard('kpi-value'+i,m[1],[x+32,326,232,48],28,m[4]);text('yoy-label'+i,'Årsförändring:',[x+32,378,84,24],9,muted);
  const delta=flatCard('yoy'+i,'Finans KPI '+i+' förändring etikett',[x+116,378,148,24],10,'@');delta.visual.objects.value[0].properties.fontColor=changeColor(m[2],i===2);delta.visual.objects.value[0].properties.fontFamily=lit('Segoe UI');save(delta);
  const spark=visual('sparkline'+i,'lineChart',[x+32,412,232,56],{Category:[col('Datum','Månadsnummer')],Y:[mea(m[3])]},{legend:[noAxis],categoryAxis:[{properties:{show:lit(false),axisType:lit('Scalar'),start:lit(1),end:lit(12),roundRange:lit(false),maxMarginFactor:lit(0)}}],zoom:[{properties:{show:lit(false),showOnCategoryAxis:lit(false),showOnValueAxis:lit(false)}}],valueAxis:[noAxis],lineStyles:[{properties:{strokeWidth:lit(1.5),strokeColor:color(pale),areaShow:lit(true),areaColor:color(pale),areaMatchStrokeColor:lit(true)}}],dataPoint:[{properties:{defaultColor:color(pale)}}],labels:[noAxis]},'',null);
  spark.visual.query.sortDefinition={sort:[{field:col('Datum','Månadsnummer'),direction:'Ascending'}],isDefaultSort:false};clean(spark);
 });
 panel('finance-monthly','Månadsutveckling',[320,488,952,296],'Bruttovinst per team eller kategori');toggle();
 function panelFilter(v,index){v.filterConfig={filters:[{name:v.name+'group',field:col('Finansaxel','Panel'),type:'Categorical',howCreated:'User',filter:{Version:2,From:[{Name:'f',Entity:'Finansaxel',Type:0}],Where:[{Condition:{In:{Expressions:[col('Finansaxel','Panel','f')],Values:[[{Literal:{Value:index+'L'}}]]}}}]}}]};return clean(v);}
 for(let index=1;index<=3;index++){
  const x=[344,682,966][index-1],width=index===1?326:272,axisInset=index===1?54:0;
  const heading=flatCard('monthly-group-'+index,'Finans gruppnamn',[x+axisInset,568,width-axisInset-8,24],9,'@');heading.visual.objects.value[0].properties.horizontalAlignment=lit('center');heading.visual.objects.value[0].properties.fontFamily=lit('Segoe UI');panelFilter(heading,index);
  const v=visual('monthly-panel-'+index,'columnChart',[x,592,width,index===1?144:136],{Category:[col('Datum','M\u00e5nadsnummer')],Y:[mea('Finans vinst \u00f6ver medel'),mea('Finans vinst under medel')],Tooltips:[mea('Finans gruppvinst miljoner'),mea('Finans m\u00e5nadsmedel'),mea('Finans m\u00e5nadsaxel max')]},{
   legend:[noAxis],categoryAxis:[{properties:{show:lit(false),axisType:lit('Scalar'),start:lit(0.5),end:lit(14.5),roundRange:lit(false),innerPadding:lit(35)}}],
   valueAxis:[{properties:{show:lit(index===1),showAxisTitle:lit(false),start:lit(0),end:{expr:mea('Finans m\u00e5nadsaxel max')},roundRange:lit(false),fontSize:lit(8),labelColor:color(muted),labelDisplayUnits:lit(1),labelPrecision:lit(1),gridlineShow:lit(true),gridlineColor:color(pale),gridlineStyle:lit('dotted')}}],
   layout:[{properties:{stackedGapSize:lit(0)}}],dataPoint:[{properties:{defaultColor:color(navy),borderShow:lit(false)}},{selector:{metadata:qref('Finans vinst \u00f6ver medel')},properties:{fill:color(navy),borderShow:lit(false)}},{selector:{metadata:qref('Finans vinst under medel')},properties:{fill:color(pale),borderShow:lit(false)}}],
   labels:[noAxis],zoom:[{properties:{show:lit(false)}}],
   y1AxisReferenceLine:[{selector:{id:'0'},properties:{show:lit(true),value:{expr:mea('Finans m\u00e5nadsmedel')},displayName:lit('Medel'),position:lit('back'),width:lit(1),style:lit('dashed'),lineColor:color('#9AABBF'),shadeShow:lit(true),shadeRegion:lit('after'),shadeColor:color(pale),shadeTransparency:lit(65),dataLabelShow:lit(true),dataLabelText:lit('Name'),dataLabelColor:color(muted),dataLabelHorizontalPosition:lit('right'),dataLabelVerticalPosition:lit('above')}}]
  },'',null);
  v.visual.query.sortDefinition={sort:[{field:col('Datum','M\u00e5nadsnummer'),direction:'Ascending'}],isDefaultSort:false};panelFilter(v,index);
  // Reserve two month slots at the right for the mean label, beyond every data bar.
  Array.from('JFMAMJJASOND').forEach((letter,i)=>{const label=text('monthly-calendar-'+index+'-'+i,letter,[x+axisInset+6+i*(266/14),742,266/14,20],7,muted);label.visual.objects.general[0].properties.paragraphs[0].horizontalTextAlignment='center';save(label);});
 }

 panel('market','Vinstfördelning',[320,808,952,256],'Per marknad');flatCard('summary-heading','Finans sammanställningsrubrik',[724,824,392,32],13,'@');
 const summaryChoice=select('summary-choice','Analysaxel','Typ',[1120,816,128,48],'Land');
 summaryChoice.visual.visualContainerObjects.background=[{properties:{show:lit(false)}}];summaryChoice.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];
 summaryChoice.visual.objects.items=[{properties:{textSize:lit(9),fontColor:color(navy)}}];summaryChoice.visual.query.queryState.Values.projections[0].nativeQueryRef='Gruppering';summaryChoice.visual.query.queryState.Values.projections[0].displayName='Gruppering';clean(summaryChoice);
 const shareBars=visual('share-bars','barChart',[344,898,340,154],{Category:[col('Kunder','Land')],Y:[mea('Bruttovinst andel land'),mea('Finans andel återstående')],Tooltips:[mea('Bruttovinst'),mea('Finans andelsaxel max')]},{categoryAxis:[{properties:{show:lit(false),innerPadding:lit(58),preferredCategoryWidth:lit(1)}}],valueAxis:[{properties:{show:lit(false),start:lit(0),end:{expr:mea('Finans andelsaxel max')},roundRange:lit(false)}}],layout:[{properties:{stackedGapSize:lit(0)}}],legend:[noAxis],labels:[noAxis],dataPoint:[{properties:{defaultColor:color(navy),borderShow:lit(false)}},{selector:{metadata:qref('Bruttovinst andel land')},properties:{fill:color(navy),borderShow:lit(false)}},{selector:{metadata:qref('Finans andel återstående')},properties:{fill:color('#E4E7EC'),borderShow:lit(false)}}]},'',null);
 shareBars.visual.query.sortDefinition={sort:[{field:mea('Bruttovinst'),direction:'Descending'}],isDefaultSort:false};shareBars.position.z=2000;clean(shareBars);
 for(let rank=1;rank<=4;rank++){const y=884+(rank-1)*42;
  const caption=flatCard('share-caption'+rank,'Finans marknad '+rank+' etikett',[344,y,348,18],9,'@');caption.visual.objects.value[0].properties.fontFamily=lit('Segoe UI');save(caption);
 }
 const fields=[col('Analysaxel','Område'),mea('Finans sammanställning vinst miljoner'),mea('Finans sammanställning tillväxt etikett'),mea('Finans sammanställning marginalbild'),mea('Finans sammanställning trend')];
 const table=visual('profit-country-table','tableEx',[724,872,524,176],{Values:fields},{
  columnHeaders:[{properties:{autoSizeColumnWidth:lit(false),columnAdjustment:lit('fixedWidth'),fontSize:lit(9),fontColor:color(navy),backColor:color('#FFFFFF'),wordWrap:lit(false)}}],
  values:[{properties:{fontSize:lit(9),fontColor:color(navy),backColorPrimary:color('#FFFFFF'),backColorSecondary:color('#FFFFFF'),wordWrap:lit(false)}}],
  total:[{properties:{totals:lit(false)}}],grid:[{properties:{rowPadding:lit(5),gridVertical:lit(false),gridHorizontal:lit(true),gridHorizontalColor:color(pale),imageHeight:lit(24),imageWidth:lit(86)}}],
  columnWidth:fields.map((f,i)=>({selector:{metadata:i?'Försäljning.'+f.Measure.Property:'Analysaxel.Område'},properties:{value:lit([100,122,112,84,84][i])}})),
  columnFormatting:[{selector:{metadata:qref('Finans sammanställning vinst miljoner')},properties:{alignment:lit('Center'),styleValues:lit(true),labelDisplayUnits:lit(1),labelPrecision:lit(2),dataBars:{positiveColor:color('#BCC8D8'),negativeColor:color(bad),hideText:lit(false),axisColor:color('#FFFFFF'),reverseDirection:lit(false)}}},
   ...['Finans sammanställning tillväxt etikett','Finans sammanställning marginalbild'].map(n=>({selector:{metadata:qref(n)},properties:{alignment:lit('Center'),styleHeader:lit(true),styleValues:lit(true)}}))]
 },'',null);
 table.visual.objects.values.push({selector:{data:[{dataViewWildcard:{matchingOption:1}}],metadata:qref('Finans sammanställning tillväxt etikett')},properties:{fontColor:changeColor('Finans sammanställning tillväxt')}});
 ['Område','Bruttovinst','Årsförändring','Marginal','Trend'].forEach((n,i)=>{table.visual.query.queryState.Values.projections[i].nativeQueryRef=n;table.visual.query.queryState.Values.projections[i].displayName=n;});
 table.visual.query.sortDefinition={sort:[{field:mea('Finans sammanställning vinst miljoner'),direction:'Descending'}],isDefaultSort:false};clean(table);

 panel('right','Topp 5 produkter efter bruttovinst',[1296,488,568,576]);
 const share=flatCard('product-share','Finans topprodukter andel etikett',[1320,540,512,24],9,'@',muted);share.visual.objects.value[0].properties.fontFamily=lit('Segoe UI');save(share);
 const products=chart('finance-products','barChart','',[1312,572,536,188],'Produkter','Produkt',['Bruttovinst','Finans produktspår återstående'],5);
 products.visual.visualContainerObjects.background=[{properties:{show:lit(false)}}];products.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];
 products.visual.objects.categoryAxis=[{properties:{show:lit(true),showAxisTitle:lit(false),fontSize:lit(9),innerPadding:lit(72),maxMarginFactor:lit(38),preferredCategoryWidth:lit(1)}}];
 products.visual.objects.valueAxis=[{properties:{show:lit(false),start:lit(0),end:{expr:mea('Finans produktaxel max')},roundRange:lit(false)}}];products.visual.objects.dataPoint=[{properties:{defaultColor:color(navy),borderShow:lit(false)}},{selector:{metadata:qref('Finans produktspår återstående')},properties:{fill:color('#E4E7EC'),borderShow:lit(false)}}];products.visual.objects.layout=[{properties:{stackedGapSize:lit(0)}}];products.visual.objects.legend=[noAxis];
 products.visual.objects.labels=[noAxis];
 products.visual.query.queryState.Tooltips={projections:['Finans produktbelopp etikett','Finans produktaxel max','Bruttomarginal','Kostnad','Sålda enheter'].map(n=>({field:mea(n),queryRef:qref(n),nativeQueryRef:n}))};clean(products);
 for(let rank=1;rank<=5;rank++){
  const amount=flatCard('product-amount-'+rank,'Finans produkt '+rank+' belopp',[1780,586+(rank-1)*35.5,68,24],9,'@',muted);amount.visual.objects.value[0].properties.fontFamily=lit('Segoe UI');save(amount);
 }
 text('scatter-heading','Bruttovinst jämfört med varukostnad',[1320,776,512,32],13,navy,null,true);text('scatter-subtitle','Per produkt',[1320,812,512,24],9,muted);
 const ref=(name,driver,hpos,vpos)=>({selector:{id:'0'},properties:{show:lit(true),displayName:lit(name),value:{expr:mea(driver)},position:lit('back'),lineColor:color('#9AA8B9'),width:lit(1.5),style:lit('dashed'),dataLabelShow:lit(true),dataLabelText:lit('Name'),dataLabelColor:color(muted),dataLabelHorizontalPosition:lit(hpos),dataLabelVerticalPosition:lit(vpos)}});
 const scatter=visual('profit-cost','scatterChart',[1312,842,536,206],{Category:[col('Produkter','Produkt')],Series:[col('Produkter','Finansgrupp')],X:[mea('Kostnad miljoner')],Y:[mea('Bruttovinst miljoner')],Tooltips:[mea('Bruttomarginal'),mea('Sålda enheter'),mea('Omsättning'),mea('Finans medelkostnad produkt'),mea('Finans medelvinst produkt')]},{
  legend:[noAxis],categoryAxis:[{properties:{show:lit(true),showAxisTitle:lit(true),titleText:lit('Varukostnad (mn kr)'),titleFontSize:lit(9),fontSize:lit(8),labelDisplayUnits:lit(1),labelPrecision:lit(2),gridlineShow:lit(true),gridlineStyle:lit('dotted'),gridlineColor:color(pale)}}],
  valueAxis:[{properties:{show:lit(true),showAxisTitle:lit(true),titleText:lit('Bruttovinst (mn kr)'),titleFontSize:lit(9),fontSize:lit(8),labelDisplayUnits:lit(1),labelPrecision:lit(2),gridlineShow:lit(true),gridlineStyle:lit('dotted'),gridlineColor:color(pale)}}],
  bubbles:[{properties:{bubbleSize:lit(5),preventOverflow:lit(true)}}],fillPoint:[{properties:{style:lit('Border only')}}],
  dataPoint:[{properties:{defaultColor:color('#4A6BCE')}},...[['Elektronik','#4A6BCE'],['Hem och kök','#C6811D'],['Övrigt','#187447']].map(([name,ink])=>({selector:{data:[{scopeId:{Comparison:{ComparisonKind:0,Left:col('Produkter','Finansgrupp'),Right:{Literal:{Value:"'"+name+"'"}}}}}]},properties:{fill:color(ink)}}))],
  xAxisReferenceLine:[ref('Medelkostnad','Finans medelkostnad produkt','right','under')],y1AxisReferenceLine:[ref('Medelvinst','Finans medelvinst produkt','right','above')]
 },'',null);
 scatter.visual.query.queryState.Series.projections[0].displayName='Kategori';scatter.visual.query.queryState.Series.projections[0].nativeQueryRef='Kategori';
 ['categoryAxis','valueAxis'].forEach(axis=>{const p=scatter.visual.objects[axis][0].properties;p.titleBold=lit(false);p.titleColor=color(muted);p.labelColor=color(muted);});clean(scatter);
};
