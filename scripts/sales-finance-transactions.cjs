// Reference-led transaction detail page; fact key preserves individual rows.
module.exports=function({preserveChrome,shell,text,card,visual,image,select,mea,col,lit,color,save}){
 const navy='#0F3163',muted='#5B6B80',good='#187447',bad='#B83232';
 shell(4);
 const interval=visual('date-range','slicer',[1536,164,328,96],{Values:[col('Datum','Datum')]},{
  data:[{properties:{mode:lit('Between'),startDate:{expr:{Literal:{Value:"datetime'2025-01-01T00:00:00'"}}},endDate:{expr:{Literal:{Value:"datetime'2025-12-31T00:00:00'"}}}}}],slider:[{properties:{show:lit(false)}}],
  header:[{properties:{show:lit(true),text:lit('Datumintervall'),textSize:lit(14.4),fontColor:color(muted)}}],
  date:[{properties:{textSize:lit(14.4),fontColor:color(navy),background:color('#EEF2F7'),hideDatePickerButton:lit(false)}}],
  calendarButton:[{properties:{iconColor:color(muted),backgroundShow:lit(false),strokeShow:lit(false),iconSize:lit(19.2)}}],
  general:[{properties:{filter:{filter:{Version:2,From:[{Name:'d',Entity:'Datum',Type:0}],Where:[{Condition:{And:{Left:{Comparison:{ComparisonKind:2,Left:col('Datum','Datum','d'),Right:{Literal:{Value:"datetime'2025-01-01T00:00:00'"}}}},Right:{Comparison:{ComparisonKind:4,Left:col('Datum','Datum','d'),Right:{Literal:{Value:"datetime'2025-12-31T00:00:00'"}}}}}}}]}}}}]
 },'',null);
 text('subtitle','Orderrader med försäljning, varukostnad och bruttomarginal',[320,220,1040,36],12,muted);
 text('transaction-kpi-panel','',[320,276,1544,132],12,navy,'#FFFFFF');
 const metrics=[['Omsättning','Omsättning miljoner','0.0" mn kr"','↗'],['Sålda enheter','Sålda enheter','#,##0','◇'],['Bruttovinst','Bruttovinst miljoner','0.0" mn kr"','kr'],['Bruttomarginal','Bruttomarginal','0.0 %','%'],['Leveranser','Leveranser','#,##0','▱']];
 metrics.forEach((m,i)=>{const x=332+i*304;
  if(i>0){const accent=text('kpi-accent'+i,'',[x,292,5,100],12,navy,navy);accent.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];save(accent);}
  text('kpi-label'+i,m[0],[x+24,294,200,32],15,navy,null,true);
  const value=card('kpi-value'+i,m[1],[x+24,338,200,56],28,m[2]);value.visual.objects.value[0].properties.fontFamily=lit('Segoe UI Semibold');save(value);
  if(image)image('kpi-icon'+i,'TransactionKpi'+i+'.svg',[x+232,318,48,48]);
 });
 text('records-panel','',[320,432,1544,632],12,navy,'#FFFFFF');
 text('records-heading','Transaktionsdetaljer',[344,452,800,36],13,navy,null,true);
 visual('product-search','textSlicer',[1496,448,344,56],{Values:[col('Produkter','Produkt')]},{inputTextBox:[{properties:{placeholder:lit('Sök produkt…'),placeholderFontSize:lit(9),placeholderFontColor:color(muted),borderShow:lit(true),borderColor:color('#D5DDE7'),containerCornerRadius:lit(6),paddingTop:lit(4),paddingBottom:lit(4),paddingLeft:lit(8),paddingRight:lit(8)}}],filterOperator:[{properties:{backShow:lit(true),backColor:color('#F5F7FA'),iconColor:color(muted),borderShow:lit(false),cornerRadius:lit(4)}}],inputText:[{properties:{fontSize:lit(9),fontColor:color(navy)}}],slicerSettings:[{properties:{multiselect:lit(false),numericInputOnly:lit(false)}}],applyButton:[{properties:{iconColor:color(navy)}}]},'',null);
 const fields=[col('Datum','Datum'),col('Säljare','Säljare'),col('Säljare','Team'),col('Kunder','Land'),col('Produkter','Kategori'),col('Produkter','Produkt'),mea('Omsättning per enhet'),mea('Sålda enheter'),mea('Kostnad'),mea('Omsättning'),mea('Bruttovinst'),mea('Transaktion marginalspår'),mea('Bruttomarginal'),col('Försäljning','Radnyckel')];
 const labels=['Datum','Säljare','Team','Marknad','Kategori','Produkt','Enhetspris','Antal','Varukostnad','Omsättning','Bruttovinst','Marginal','%','Rad-ID'];
 const widths=[100,116,68,84,128,238,102,66,104,104,104,140,60,60];
 const objects={
  columnHeaders:[{properties:{autoSizeColumnWidth:lit(false),columnAdjustment:lit('fixedWidth'),fontSize:lit(9),wordWrap:lit(false),backColor:color('#F5F7FA'),fontColor:color(navy)}}],
  values:[{properties:{fontSize:lit(9),wordWrap:lit(false),backColorPrimary:color('#FFFFFF'),backColorSecondary:color('#FFFFFF'),fontColorPrimary:color(navy),fontColorSecondary:color(navy)}}],
  total:[{properties:{totals:lit(false)}}],grid:[{properties:{rowPadding:lit(14),imageHeight:lit(24),imageWidth:lit(120),gridVertical:lit(false),gridHorizontal:lit(true),gridHorizontalColor:color('#E7EDF5')}}],
  columnFormatting:fields.map((f,i)=>{const spec=f.Column||f.Measure;return {selector:{metadata:spec.Expression.SourceRef.Entity+'.'+spec.Property},properties:{alignment:lit(f.Measure||i===13?'Right':'Left'),styleValues:lit(true),styleHeader:lit(true),labelDisplayUnits:lit(1),...(f.Measure?{labelPrecision:lit(i===7?0:i===12?1:2)}:{})}};})
 };
 for(const i of [10,12])objects.values.push({selector:{data:[{dataViewWildcard:{matchingOption:1}}],metadata:'Försäljning.'+(i===10?'Bruttovinst':'Bruttomarginal')},properties:{fontColor:{solid:{color:{expr:{Conditional:{Cases:[{Condition:{Comparison:{ComparisonKind:3,Left:mea(i===10?'Bruttovinst':'Bruttomarginal'),Right:{Literal:{Value:'0D'}}}},Value:{Literal:{Value:"'"+bad+"'"}}}],DefaultValue:{Literal:{Value:"'"+(i===10?navy:good)+"'"}}}}}}}}});
 const table=visual('records','tableEx',[344,512,1496,528],{Values:fields},objects,'',null);
 table.visual.visualContainerObjects.stylePreset=[{properties:{name:lit('None')}}];
 table.visual.query.queryState.Values.projections.forEach((p,i)=>{p.nativeQueryRef=labels[i];p.displayName=labels[i];});
 table.visual.objects.columnWidth=table.visual.query.queryState.Values.projections.map((p,i)=>({selector:{metadata:p.queryRef},properties:{value:lit(widths[i])}}));
 table.visual.query.sortDefinition={sort:[{field:col('Datum','Datum'),direction:'Ascending'},{field:col('Försäljning','Radnyckel'),direction:'Ascending'}],isDefaultSort:false};
 save(table);
};





