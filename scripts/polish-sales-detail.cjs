const fs=require('fs'),path=require('path');
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?`${v}D`:"'"+v+"'"}}});
const color=v=>({solid:{color:lit(v)}});
function polish(v){
 const o=v.visual.objects;
 v.position.height=304;
 Object.assign(o.columnHeaders[0].properties,{fontFamily:lit('Segoe UI Semibold'),fontSize:lit(11.5),backColor:color('#EEF2F7'),outlineWeight:lit(0),wordWrap:lit(false)});
 Object.assign(o.rowHeaders[0].properties,{fontFamily:lit('Segoe UI'),fontSize:lit(11.5),outlineWeight:lit(0),expandCollapseButtonsColor:color('#70839A'),expandCollapseButtonsSize:lit(10)});
 Object.assign(o.values[0].properties,{fontFamily:lit('Segoe UI'),fontSize:lit(11.5),backColorPrimary:color('#FFFFFF'),backColorSecondary:color('#F7F9FC')});
 Object.assign(o.grid[0].properties,{rowPadding:lit(3),gridVertical:lit(false),gridHorizontal:lit(true),gridHorizontalColor:color('#E7ECF2'),gridHorizontalWeight:lit(1),outlineWeight:lit(0)});
 o.columnWidth.forEach((entry,i)=>entry.properties.value=lit(i<2?230:[136,112,136,114][i-2]));
 o.columnFormatting=v.visual.query.queryState.Values.projections.map(p=>({selector:{metadata:p.queryRef},properties:{alignment:lit('Right'),styleHeader:lit(true),styleValues:lit(true),styleTotal:lit(true)}}));
 Object.assign(o.rowTotal[0].properties,{fontFamily:lit('Segoe UI Semibold'),fontSize:lit(11.5),fontColor:color('#0F3163'),backColor:color('#E8EEF6'),bold:lit(true),applyToHeaders:lit(true)});
 return v;
}
module.exports=polish;
if(require.main===module){
 const dir=path.resolve(__dirname,'../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report/definition/pages/b4eda99cffce7ac04192/visuals');
 for(const name of fs.readdirSync(dir)){
  const file=path.join(dir,name,'visual.json');if(!fs.existsSync(file))continue;
  const v=JSON.parse(fs.readFileSync(file,'utf8'));if(v.visual.visualType!=='pivotTable')continue;
  fs.writeFileSync(file,JSON.stringify(polish(v),null,2)+'\n');
  console.log('Polished category matrix typography, row rhythm, column widths and totals.');
 }
}
