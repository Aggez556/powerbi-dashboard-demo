// Vega table: one scrolling surface, frozen column headers and frozen row labels.
// Open/close state exists only on nodes whose Children field is 1.
module.exports=function statementSpec(open=['r6','r6_s2']){
 const text=(name,from,update)=>({name,type:'text',from:{data:from},encode:{update:{font:{value:'Segoe UI'},fontSize:{value:15},fill:{value:'#0F3163'},baseline:{value:'middle'},...update}}});
 const rect=(name,from,update)=>({name,type:'rect',...(from?{from:{data:from}}:{}),encode:{update}});
 return {$schema:'https://vega.github.io/schema/vega/v6.json',description:'Interaktiv resultaträkning. Kontogrupper kan expanderas; beräknade rader är blad utan pilar.',width:1252,height:572,padding:0,autosize:{type:'none',contains:'padding'},background:'#FFFFFF',
 signals:[
  {name:'rowHeight',value:32},{name:'headerH',value:80},{name:'labelW',value:300},
  {name:'columnW',update:"max(length(data('columns')) && indexof(data('columns')[0].Metric,' · ')>=0?168:112,(width-labelW-12)/max(1,length(data('columns'))))"},
  {name:'bodyW',update:'max(20,width-labelW-12)'},
  {name:'fullW',update:"length(data('columns'))*columnW"},
  {name:'maxX',update:'fullW>bodyW+0.5?fullW-bodyW:0'},
  {name:'bodyH',update:'height-headerH-(maxX>0?12:0)'},
  {name:'fullH',update:"length(data('rows'))?data('rows')[length(data('rows'))-1].RowTop+rowHeight:0"},
  {name:'maxY',update:'max(0,fullH-bodyH)'},
  {name:'clickedNode',value:null,on:[{events:'@nodeHit:click',update:'datum.Children===1?datum.Node:null',force:true}]},
  {name:'expandAll',value:0,on:[{events:'@expandAllButton:click',update:'now()',force:true}]},
  {name:'collapseAll',value:0,on:[{events:'@collapseAllButton:click',update:'now()',force:true}]},
  {name:'hoverNode',value:null,on:[{events:'@nodeHit:mouseover',update:'datum.Node'},{events:'@nodeHit:mouseout',update:'null'}]},
  {name:'hDrag',value:null,on:[{events:'@hthumb:mousedown',update:'{x:x(),start:scrollX}'},{events:'window:mouseup',update:'null'}]},
  {name:'vDrag',value:null,on:[{events:'@vthumb:mousedown',update:'{y:y(),start:scrollY}'},{events:'window:mouseup',update:'null'}]},
  {name:'scrollX',value:0,on:[{events:{type:'wheel',consume:true},update:'clamp(scrollX+(event.shiftKey?event.deltaY:event.deltaX),0,maxX)'},{events:'window:mousemove',update:'hDrag?clamp(hDrag.start+(x()-hDrag.x)*fullW/bodyW,0,maxX):scrollX'},{events:{signal:'maxX'},update:'clamp(scrollX,0,maxX)'}]},
  {name:'scrollY',value:0,on:[{events:{type:'wheel',consume:true},update:'clamp(scrollY+(event.shiftKey?0:event.deltaY),0,maxY)'},{events:'window:mousemove',update:'vDrag?clamp(vDrag.start+(y()-vDrag.y)*fullH/bodyH,0,maxY):scrollY'},{events:{signal:'maxY'},update:'clamp(scrollY,0,maxY)'}]}
 ],
 data:[
  {name:'dataset'},
  {name:'open',values:open.map(key=>({key})),on:[{trigger:'clickedNode',toggle:'{key:clickedNode}'},{trigger:'expandAll',remove:'true'},{trigger:'expandAll',insert:"data('expandables')"},{trigger:'collapseAll',remove:'true'}]},
  {name:'valid',source:'dataset',transform:[{type:'filter',expr:'isValid(datum.Amount) && isValid(datum.Node)'},{type:'formula',expr:'datum.GroupOrder*10+datum.Slot',as:'ColumnKey'}]},
  {name:'expandables',source:'valid',transform:[{type:'aggregate',groupby:['Node','Children']},{type:'filter',expr:'datum.Children===1'},{type:'formula',expr:'datum.Node',as:'key'}]},
  {name:'columns',source:'valid',transform:[{type:'aggregate',groupby:['Group','GroupOrder','Metric','Slot','ColumnKey']},{type:'collect',sort:{field:'ColumnKey',order:'ascending'}},{type:'window',sort:{field:'ColumnKey',order:'ascending'},ops:['row_number'],as:['ColumnNumber']},{type:'formula',expr:'datum.ColumnNumber-1',as:'ColumnIndex'}]},
  {name:'groups',source:'columns',transform:[{type:'aggregate',groupby:['Group','GroupOrder'],fields:['ColumnIndex','ColumnIndex'],ops:['min','max'],as:['First','Last']}]},
  {name:'rows',source:'valid',transform:[
   {type:'aggregate',groupby:['Node','Label','Parent','Ancestor','Depth','Kind','Order','Children','Section']},
   {type:'filter',expr:"datum.Depth===0 || (indata('open','key',datum.Parent) && (datum.Depth===1 || indata('open','key',datum.Ancestor)))"},
   {type:'collect',sort:{field:'Order',order:'ascending'}},
   {type:'formula',expr:"isValid(datum.Section) && datum.Section!==''?34:datum.Kind==='resultat'?10:0",as:'Before'},
   {type:'formula',expr:'rowHeight+datum.Before',as:'Extent'},
   {type:'window',sort:{field:'Order',order:'ascending'},ops:['sum'],fields:['Extent'],as:['RunningY'],frame:[null,0]},
   {type:'formula',expr:'datum.RunningY-rowHeight',as:'RowTop'}
  ]},
  {name:'cells',source:'valid',transform:[
   {type:'lookup',from:'rows',key:'Node',fields:['Node'],values:['RowTop'],as:['RowTop'],default:null},
   {type:'filter',expr:'isValid(datum.RowTop)'},
   {type:'lookup',from:'columns',key:'ColumnKey',fields:['ColumnKey'],values:['ColumnIndex'],as:['ColumnIndex']}
  ]}
 ],
 marks:[
  rect('header',null,{x:{value:0},y:{value:0},width:{signal:'width'},height:{signal:'headerH'},fill:{value:'#EEF2F7'}}),
  {type:'group',name:'body',clip:true,encode:{update:{x:{value:0},y:{signal:'headerH'},width:{signal:'width-12'},height:{signal:'bodyH'}}},marks:[
   rect('rowBands','rows',{x:{value:0},y:{signal:'datum.RowTop-scrollY'},width:{signal:'width-12'},height:{signal:'rowHeight'},fill:{signal:"datum.Kind==='resultat'?'#E1EAF5':datum.Kind==='marginal'?'#F3F6FA':datum.Node===hoverNode && datum.Children===1?'#F2F5F9':'#FFFFFF'"}}),
   {name:'rowLines',type:'rule',from:{data:'rows'},encode:{update:{x:{value:0},x2:{signal:'width-12'},y:{signal:'datum.RowTop+rowHeight-scrollY'},stroke:{value:'#E7ECF2'},strokeWidth:{value:.6}}}},
   {type:'group',name:'numbers',clip:true,encode:{update:{x:{signal:'labelW'},y:{value:0},width:{signal:'bodyW'},height:{signal:'bodyH'}}},marks:[
    text('cellText','cells',{x:{signal:'(datum.ColumnIndex+1)*columnW-12-scrollX'},y:{signal:'datum.RowTop+rowHeight/2-scrollY'},text:{field:'Text'},align:{value:'right'},fontSize:{signal:"datum.Kind==='konto'?15:16"},fontWeight:{signal:"datum.Kind==='resultat'?'bold':datum.Kind==='grupp'?'600':'normal'"},fontStyle:{signal:"datum.Kind==='marginal'?'italic':'normal'"},fill:{field:'Color'},limit:{signal:'columnW-12'},tooltip:{signal:"datum.Label+' · '+datum.Group+' · '+datum.Metric+': '+datum.Text"}})
   ]},
   rect('rowLabelBackground','rows',{x:{value:0},y:{signal:'datum.RowTop-scrollY'},width:{signal:'labelW'},height:{signal:'rowHeight'},fill:{signal:"datum.Kind==='resultat'?'#E1EAF5':datum.Kind==='marginal'?'#F3F6FA':datum.Node===hoverNode && datum.Children===1?'#F2F5F9':'#FFFFFF'"}}),
   text('sectionLabels','rows',{x:{value:8},y:{signal:'datum.RowTop-14-scrollY'},text:{signal:"datum.Before>0 && datum.Section?datum.Section:''"},fontSize:{value:15},fontWeight:{value:'bold'},fill:{value:'#5B6B80'}}),
   text('rowLabels','rows',{x:{signal:'datum.Depth*18+28'},y:{signal:'datum.RowTop+rowHeight/2-scrollY'},text:{field:'Label'},fontSize:{signal:"datum.Kind==='konto'?15:16"},fontWeight:{signal:"datum.Kind==='resultat'?'bold':datum.Kind==='grupp'?'600':'normal'"},fontStyle:{signal:"datum.Kind==='marginal'?'italic':'normal'"},limit:{signal:'labelW-datum.Depth*18-36'},fill:{signal:"datum.Kind==='marginal'?'#5B6B80':'#0F3163'"}}),
   text('chevrons','rows',{x:{signal:'datum.Depth*18+10'},y:{signal:'datum.RowTop+rowHeight/2-scrollY'},text:{signal:"datum.Children===1?(indata('open','key',datum.Node)?'▾':'▸'):''"},fontSize:{value:16},fontWeight:{value:'bold'}}),
   rect('nodeHit','rows',{x:{value:0},y:{signal:'datum.RowTop-scrollY'},width:{signal:'labelW'},height:{signal:'rowHeight'},fill:{value:'#FFFFFF'},fillOpacity:{value:0},cursor:{signal:"datum.Children===1?'pointer':'default'"},tooltip:{signal:"datum.Children===1?'Klicka för att visa eller dölja underkategorier':datum.Kind==='konto'?'Kontopost utan underposter':'Beräknad rad utan underposter'"}})
  ]},
  {name:'columnHeaders',type:'group',clip:true,encode:{update:{x:{signal:'labelW'},y:{value:0},width:{signal:'bodyW'},height:{signal:'headerH'}}},marks:[
   text('monthHeaders','groups',{x:{signal:'(datum.First+datum.Last+1)*columnW/2-scrollX'},y:{value:21},text:{field:'Group'},align:{value:'center'},fontSize:{value:15},fontWeight:{value:'600'}}),
   text('metricHeaders','columns',{x:{signal:'(datum.ColumnIndex+1)*columnW-12-scrollX'},y:{signal:"indexof(datum.Metric,' · ')>=0?51:58"},text:{signal:"indexof(datum.Metric,' · ')>=0?split(datum.Metric,' · '):datum.Metric"},align:{value:'right'},fontSize:{value:14},lineHeight:{value:16},limit:{signal:'columnW-12'}}),
   {type:'rule',from:{data:'groups'},encode:{update:{x:{signal:'(datum.Last+1)*columnW-scrollX'},y:{value:0},y2:{signal:'headerH'},stroke:{value:'#D7E0EB'},strokeWidth:{value:.8}}}}
  ]},
  {type:'text',encode:{update:{x:{value:10},y:{value:24},text:{value:'Post'},font:{value:'Segoe UI Semibold'},fontSize:{value:15},fill:{value:'#0F3163'}}}},
  rect('expandAllButton',null,{x:{value:8},y:{value:38},width:{value:132},height:{value:32},fill:{value:'#FFFFFF'},stroke:{value:'#D7E0EB'},cornerRadius:{value:4},cursor:{value:'pointer'}}),
  {type:'text',interactive:false,encode:{update:{x:{value:74},y:{value:54},text:{value:'Expandera alla'},font:{value:'Segoe UI'},fontSize:{value:14},fill:{value:'#0F3163'},align:{value:'center'},baseline:{value:'middle'}}}},
  rect('collapseAllButton',null,{x:{value:148},y:{value:38},width:{value:132},height:{value:32},fill:{value:'#FFFFFF'},stroke:{value:'#D7E0EB'},cornerRadius:{value:4},cursor:{value:'pointer'}}),
  {type:'text',interactive:false,encode:{update:{x:{value:214},y:{value:54},text:{value:'Fäll ihop'},font:{value:'Segoe UI'},fontSize:{value:14},fill:{value:'#0F3163'},align:{value:'center'},baseline:{value:'middle'}}}},
  rect('htrack',null,{x:{signal:'labelW'},y:{signal:'height-10'},width:{signal:'bodyW'},height:{value:8},fill:{value:'#EEF2F7'},opacity:{signal:'maxX>0?1:0'}}),
  rect('hthumb',null,{x:{signal:'labelW+(fullW?scrollX*bodyW/fullW:0)'},y:{signal:'height-10'},width:{signal:'fullW?max(24,bodyW*bodyW/fullW):bodyW'},height:{value:8},cornerRadius:{value:4},fill:{value:'#9AAAC0'},opacity:{signal:'maxX>0?1:0'},cursor:{value:'ew-resize'}}),
  rect('vtrack',null,{x:{signal:'width-10'},y:{signal:'headerH'},width:{value:8},height:{signal:'bodyH'},fill:{value:'#EEF2F7'},opacity:{signal:'maxY>0?1:0'}}),
  rect('vthumb',null,{x:{signal:'width-10'},y:{signal:'headerH+(fullH?scrollY*bodyH/fullH:0)'},width:{value:8},height:{signal:'fullH?max(24,bodyH*bodyH/fullH):bodyH'},cornerRadius:{value:4},fill:{value:'#9AAAC0'},opacity:{signal:'maxY>0?1:0'},cursor:{value:'ns-resize'}})
 ]};
};
