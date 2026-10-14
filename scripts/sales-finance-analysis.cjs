// Reference-led Sales Analytics components, shared with the full-project builder.
module.exports=function(api){
 const {shell,text,card,visual,select,mea,col,lit,color,save}=api;
 const navy='#0F3163',muted='#5B6B80',pale='#E7EDF5',good='#187447',bad='#B83232';
 const ref=n=>'Försäljning.'+n,noAxis={properties:{show:lit(false)}};
 const stage=process.env.SALES_ANALYSIS_STAGE||'all';
 function panel(key,title,box,subtitle){text(key+'-panel','',box,12,navy,'#FFFFFF');text(key+'-heading',title,[box[0]+24,box[1]+16,box[2]-48,32],13,navy,null,true);if(subtitle)text(key+'-subtitle',subtitle,[box[0]+24,box[1]+52,box[2]-48,24],9,muted);}
 function clean(v){v.visual.visualContainerObjects.padding=[{properties:{top:lit(0),bottom:lit(0),left:lit(0),right:lit(0)}}];v.visual.visualContainerObjects.background=[{properties:{show:lit(false)}}];v.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];v.visual.visualContainerObjects.visualHeader=[{properties:{show:lit(false)}}];return save(v);}
 function flatCard(...args){const v=card(...args);v.visual.objects.layout=[{properties:{paddingUniform:lit(0),backgroundShow:lit(false),backgroundTransparency:lit(100),cellPadding:lit(0)}}];v.visual.objects.padding=[{selector:{id:'default'},properties:{paddingSelection:lit('Custom'),leftMargin:lit(0),rightMargin:lit(0),topMargin:lit(0),bottomMargin:lit(0),paddingUniform:lit(0)}}];v.visual.objects.cardCalloutArea=[{properties:{paddingUniform:lit(0),show:lit(false),backgroundTransparency:lit(100)}},{selector:{id:'default'},properties:{paddingUniform:lit(0),show:lit(false),backgroundTransparency:lit(100)}}];v.visual.objects.fillCustom=[{properties:{show:lit(false)}},{selector:{id:'default'},properties:{show:lit(false),transparency:lit(100)}}];v.visual.objects.value[0].properties.bold=lit(false);v.visual.objects.value[0].properties.textWrap=lit(false);return clean(v);}
 function colorMeasure(name){return {solid:{color:{expr:mea(name)}}};}
 function growthColor(name){return {solid:{color:{expr:{Conditional:{Cases:[{Condition:{Comparison:{ComparisonKind:3,Left:mea(name),Right:{Literal:{Value:'0D'}}}},Value:{Literal:{Value:"'"+bad+"'"}}}],DefaultValue:{Literal:{Value:"'"+good+"'"}}}}}}};}
 shell(3);
 if(!api.preserveChrome)select('year','Datum','År',[1672,136,208,72],2025);
 text('subtitle','Säljarresultat, ordervärden och omsättningens fördelning mellan marknader',[320,220,1280,36],12,muted);
 // Existing period slicers are preserved by the page-only builder.
 if(stage==='header')return;
 const metrics=[['Aktiva säljare','Aktiva säljare','#,##0'],['Omsättning per säljare','Omsättning per säljare miljoner','0.0" mn kr"'],['Leveranser','Leveranser','#,##0'],['Genomsnittligt ordervärde','Genomsnittlig order','#,##0" kr"'],['Topp 5 · andel','Topp 5 säljare andel','0.0 %']];
 metrics.forEach((m,i)=>{
  const x=320+i*312;
  text('kpi-panel'+i,'',[x,276,296,200],12,navy,'#FFFFFF');text('kpi-label'+i,m[0],[x+32,294,252,36],15,navy,null,true);
  const value=flatCard('kpi-value'+i,m[1],[x+32,336,244,56],28,m[2]);value.visual.objects.value[0].properties.fontFamily=lit('Segoe UI Semibold');save(value);
  const pill=text('kpi-change-panel'+i,'',[x+32,412,196,40],10,navy,pale);
  pill.visual.visualContainerObjects.border=[{properties:{show:lit(true),color:colorMeasure('Säljanalys KPI '+i+' färg'),radius:lit(20)}}];
  pill.visual.visualContainerObjects.background=[{properties:{show:lit(true),color:colorMeasure('Säljanalys KPI '+i+' färg'),transparency:lit(94)}}];save(pill);
  const delta=flatCard('kpi-change'+i,'Säljanalys KPI '+i+' förändring',[x+40,420,180,24],10,'@');delta.visual.objects.value[0].properties.horizontalAlignment=lit('center');delta.visual.objects.value[0].properties.fontColor=colorMeasure('Säljanalys KPI '+i+' färg');save(delta);
 });
 if(stage==='kpi')return;

 panel('sales-trend','Omsättning och bruttovinst',[320,500,952,284],'Per månad');
 const trend=visual('sales-trend','lineStackedColumnComboChart',[336,578,920,166],{Category:[col('Datum','Månad kort')],Y:[mea('Säljanalys omsättning övriga månader'),mea('Säljanalys omsättning toppmånad')],Y2:[mea('Bruttovinst miljoner'),mea('Säljanalys bruttovinst max punkt'),mea('Säljanalys bruttovinst min punkt')],Tooltips:[mea('Omsättning'),mea('Bruttovinst'),mea('Bruttomarginal')]},{
  legend:[noAxis],categoryAxis:[{properties:{show:lit(true),axisType:lit('Categorical'),concatenateLabels:lit(false),fontSize:lit(9),labelColor:color(muted),showAxisTitle:lit(false),innerPadding:lit(48)}}],
  valueAxis:[{properties:{show:lit(true),showAxisTitle:lit(false),start:lit(0),fontSize:lit(9),labelColor:color(muted),labelDisplayUnits:lit(1),labelPrecision:lit(1),secShow:lit(true),secShowAxisTitle:lit(false),secStart:lit(0),secLabelDisplayUnits:lit(1),secLabelPrecision:lit(1),secFontSize:lit(9),secLabelColor:color(muted),gridlineShow:lit(true),gridlineColor:color(pale),gridlineStyle:lit('dotted')}}],
  dataPoint:[{properties:{defaultColor:color('#E4E7EC'),borderShow:lit(false)}},{selector:{metadata:ref('Säljanalys omsättning toppmånad')},properties:{fill:color(navy),borderShow:lit(false)}},{selector:{metadata:ref('Bruttovinst miljoner')},properties:{fill:color('#BCC8D8')}},...['max','min'].map(ext=>({selector:{metadata:ref('Säljanalys bruttovinst '+ext+' punkt')},properties:{fill:color('#BCC8D8')}}))],
  lineStyles:[{properties:{strokeWidth:lit(2),lineChartType:lit('smooth'),showMarker:lit(false)}},...['max','min'].map(ext=>({selector:{metadata:ref('Säljanalys bruttovinst '+ext+' punkt')},properties:{strokeShow:lit(false),showMarker:lit(true),markerShape:lit('circle'),markerSize:lit(4),markerColor:color(navy)}}))],labels:[noAxis],zoom:[{properties:{show:lit(false)}}]
 },'',null);
 trend.visual.query.sortDefinition={sort:[{field:col('Datum','Månadsnummer'),direction:'Ascending'}],isDefaultSort:false};clean(trend);
 for(let q=1;q<=4;q++){const v=flatCard('sales-quarter-'+q,'Säljanalys kvartal '+q,[408+((q-1)*3+1)*(768/12),744,768/12,24],9,'@',muted);v.visual.objects.value[0].properties.showBlankAs=lit('');v.visual.objects.value[0].properties.horizontalAlignment=lit('center');save(v);}
 const legend=text('sales-legend','',[980,760,264,24],9,muted);
 legend.visual.objects.general[0].properties.paragraphs[0].textRuns=[{value:'● Omsättning    ',textStyle:{fontFamily:'Segoe UI',fontSize:'9pt',color:navy}},{value:'─ Bruttovinst',textStyle:{fontFamily:'Segoe UI',fontSize:'9pt',color:'#BCC8D8'}}];save(legend);
 if(stage==='trend')return;

 panel('sales-markets','Försäljning per marknad',[320,808,952,256],'Omsättning');
 const table=visual('sales-country-table','tableEx',[344,884,464,172],{Values:[col('Kunder','Land'),mea('Omsättning miljoner'),mea('Säljanalys marknad tillväxt etikett'),mea('Säljanalys marknad andelsbild')]},{
  columnHeaders:[{properties:{autoSizeColumnWidth:lit(false),fontSize:lit(9),wordWrap:lit(false),fontColor:color(navy),backColor:color('#FFFFFF')}}],values:[{properties:{fontSize:lit(9),wordWrap:lit(false),fontColor:color(navy),backColor:color('#FFFFFF'),backColorSecondary:color('#FFFFFF')}}],total:[{properties:{totals:lit(false)}}],grid:[{properties:{rowPadding:lit(4),imageHeight:lit(22),imageWidth:lit(88),gridVertical:lit(false),gridHorizontal:lit(true),gridHorizontalColor:color(pale)}}],
  columnFormatting:[
   {selector:{metadata:ref('Omsättning miljoner')},properties:{alignment:lit('Right'),styleHeader:lit(true),styleValues:lit(true),dataBars:{positiveColor:color('#BCC8D8'),negativeColor:color(bad),axisColor:color('#FFFFFF'),hideText:lit(false),reverseDirection:lit(false)}}},
   {selector:{metadata:ref('Säljanalys marknad tillväxt etikett')},properties:{alignment:lit('Center'),styleHeader:lit(true),styleValues:lit(true),fontColor:colorMeasure('Säljanalys marknad tillväxt färg')}},
   {selector:{metadata:ref('Säljanalys marknad andelsbild')},properties:{alignment:lit('Center'),styleHeader:lit(true),styleValues:lit(true)}}]
 },'',null);
 ['Marknad','Omsättning','Årsförändring','Andel'].forEach((name,i)=>{table.visual.query.queryState.Values.projections[i].nativeQueryRef=name;table.visual.query.queryState.Values.projections[i].displayName=name;});
 const widths=[100,112,112,104];table.visual.objects.columnWidth=table.visual.query.queryState.Values.projections.map((p,i)=>({selector:{metadata:p.queryRef},properties:{value:lit(widths[i])}}));
 table.visual.query.sortDefinition={sort:[{field:mea('Omsättning miljoner'),direction:'Descending'}],isDefaultSort:false};clean(table);
 if(stage==='market')return;

 const trendHeading=flatCard('sales-market-trend-heading','Säljanalys trendrubrik',[824,824,300,32],13,'@');trendHeading.visual.objects.value[0].properties.fontFamily=lit('Segoe UI Semibold');save(trendHeading);
 const choice=select('sales-market-choice','Analysaxel','Typ',[1128,816,120,48],process.env.SALES_PREVIEW_GROUP||'Land');choice.visual.query.queryState.Values.projections[0].nativeQueryRef='Gruppering';choice.visual.query.queryState.Values.projections[0].displayName='Gruppering';clean(choice);
 for(let rank=1;rank<=4;rank++){
  const y=880+(rank-1)*42;
  const name=flatCard('sales-market-name-'+rank,'Säljanalys trend '+rank+' namn etikett',[816,y+8,92,24],9,'@');name.visual.objects.value[0].properties.horizontalAlignment=lit('right');name.visual.objects.value[0].properties.showBlankAs=lit('');save(name);
  const v=visual('sales-market-line-'+rank,'tableEx',[920,y,328,42],{Values:[mea('Säljanalys trend '+rank+' bild')]},{columnHeaders:[{properties:{fontSize:lit(1),fontColor:color('#FFFFFF'),backColor:color('#FFFFFF'),wordWrap:lit(false),autoSizeColumnWidth:lit(false)}}],values:[{properties:{fontSize:lit(8),backColor:color('#FFFFFF'),backColorSecondary:color('#FFFFFF')}}],total:[{properties:{totals:lit(false)}}],grid:[{properties:{outlineStyle:lit(0),outlineColor:color('#FFFFFF'),rowPadding:lit(0),imageHeight:lit(28),imageWidth:lit(318),gridVertical:lit(false),gridHorizontal:lit(false)}}],columnWidth:[{selector:{metadata:ref('Säljanalys trend '+rank+' bild')},properties:{value:lit(324)}}]},'',null);v.visual.query.queryState.Values.projections[0].nativeQueryRef=' ';v.visual.query.queryState.Values.projections[0].displayName=' ';clean(v);
 }
 if(stage==='trends')return;

 panel('sales-leaderboard','Säljare · högst omsättning',[1296,500,568,564],'Rangordnade efter omsättning · vald period');
 for(let rank=1;rank<=7;rank++){
  const y=584+(rank-1)*68,prefix='Säljanalys säljare '+rank+' ';
  const row=text('sales-seller-row-'+rank,'',[1320,y,520,58],9,navy,pale);row.visual.visualContainerObjects.border=[{properties:{show:lit(true),color:color(pale),radius:lit(16)}}];save(row);
  const badge=text('sales-seller-badge-'+rank,'',[1332,y+7,44,44],9,navy,navy);badge.visual.visualContainerObjects.border=[{properties:{show:lit(true),color:color(navy),radius:lit(22)}}];save(badge);
  const initials=flatCard('sales-seller-initials-'+rank,prefix+'initialer',[1332,y+7,44,44],12,'@','#FFFFFF');initials.visual.objects.value[0].properties.horizontalAlignment=lit('center');save(initials);
  flatCard('sales-seller-name-'+rank,prefix+'namn',[1392,y+4,424,28],12,'@',navy);
  flatCard('sales-seller-segments-'+rank,prefix+'segment',[1392,y+30,192,24],8,'@',navy);
  flatCard('sales-seller-amount-'+rank,prefix+'belopp etikett',[1588,y+30,88,24],9,'@',navy);
  text('sales-seller-divider-'+rank,'|',[1676,y+30,10,24],9,muted);
  const growth=flatCard('sales-seller-growth-'+rank,prefix+'tillväxt etikett',[1690,y+30,144,24],9,'@');growth.visual.objects.value[0].properties.fontColor=growthColor(prefix+'tillväxt');save(growth);
 }
};











