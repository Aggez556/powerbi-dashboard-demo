// One surface colors the entire row, including the hierarchy label.
module.exports=function(){
 const txt=(name,data,x,y,text,extra={})=>({name,type:'text',...(data?{from:{data}}:{}),encode:{update:{x:typeof x==='number'?{value:x}:{signal:x},y:typeof y==='number'?{value:y}:{signal:y},text,fill:{value:'#0F3163'},font:{value:'Segoe UI'},fontSize:{value:16},baseline:{value:'middle'},...extra}}});
 const financial=[['Revenue',388],['Growth',490],['GrossProfit',620],['Margin',736]];
 const values=(data,y)=>financial.map(([field,x])=>{
  const formatted=field==='Revenue'||field==='GrossProfit'?`replace(format(datum.${field},'${field==='Revenue'?'.1f':'.2f'}'),'.',',')+' Mkr'`:`isValid(datum.${field})?replace(replace(format(datum.${field},'${field==='Growth'?'+.1%':'.1%'}'),'.',','),'%',' %'):'—'`;
  const name={Revenue:'Omsättning',Growth:'Förändring mot föregående år',GrossProfit:'Bruttovinst',Margin:'Bruttomarginal'}[field];
  return txt(data+field,data,x,y,{signal:formatted},{align:{value:'right'},fontWeight:{value:data==='total'?'600':'normal'},tooltip:{signal:`{'Post':datum.Label||'Totalt','Nyckeltal':'${name}','Värde':(${formatted})}`},...(field==='Growth'?{fill:{signal:"datum.Growth>0?'#007956':datum.Growth<0?'#B42318':'#5B6B80'"}}:{})});
 });
 return {$schema:'https://vega.github.io/schema/vega/v6.json',width:750,height:304,padding:0,autosize:'none',background:'#FFFFFF',
 signals:[{name:'rowH',value:30},{name:'bodyH',value:242},{name:'clicked',value:null,on:[{events:'@rowHit:click, @rowLabel:click, @expander:click',update:'datum.Depth===0?datum.Category:null',force:true}]},{name:'scrollY',value:0,on:[{events:{type:'wheel',consume:true},update:'clamp(scrollY+event.deltaY,0,maxY)'},{events:{signal:'maxY'},update:'clamp(scrollY,0,maxY)'}]},{name:'maxY',update:"max(0,length(data('rows'))*rowH-bodyH)"}],
 data:[{name:'dataset'},{name:'facts',source:'dataset',transform:[{type:'formula',expr:'datum.RevenueKrona/1000000',as:'Revenue'},{type:'formula',expr:'datum.PreviousRevenueKrona/1000000',as:'PreviousRevenue'},{type:'formula',expr:'datum.GrossProfitKrona/1000000',as:'GrossProfit'}]},
 {name:'open',values:[],on:[{trigger:'clicked',toggle:'{key:clicked}'}]},
 {name:'categories',source:'facts',transform:[{type:'aggregate',groupby:['Category','Area','Order'],fields:['Revenue','PreviousRevenue','GrossProfit'],ops:['sum','sum','sum'],as:['Revenue','PreviousRevenue','GrossProfit']},{type:'formula',expr:'datum.Category',as:'Label'},{type:'formula',expr:'0',as:'Depth'},{type:'formula',expr:'datum.Order*100',as:'Sort'}]},
 {name:'articles',source:'facts',transform:[{type:'filter',expr:"indata('open','key',datum.Category)"},{type:'collect',sort:{field:['Order','Article'],order:['ascending','ascending']}},{type:'window',groupby:['Category'],sort:{field:'Article',order:'ascending'},ops:['row_number'],as:['ArticleOrder']},{type:'formula',expr:'datum.Article',as:'Label'},{type:'formula',expr:'1',as:'Depth'},{type:'formula',expr:'datum.Order*100+datum.ArticleOrder',as:'Sort'}]},
 {name:'rows',source:['categories','articles'],transform:[{type:'collect',sort:{field:'Sort',order:'ascending'}},{type:'window',sort:{field:'Sort',order:'ascending'},ops:['row_number'],as:['Row']},{type:'formula',expr:'datum.PreviousRevenue?datum.Revenue/datum.PreviousRevenue-1:null',as:'Growth'},{type:'formula',expr:'datum.Revenue?datum.GrossProfit/datum.Revenue:null',as:'Margin'},{type:'formula',expr:"datum.Depth===1?'#FFFFFF':datum.Area===1?'#E3EBF5':datum.Area===2?'#E4F1E9':'#FAEBD7'",as:'Background'}]},
 {name:'total',source:'facts',transform:[{type:'aggregate',fields:['Revenue','PreviousRevenue','GrossProfit'],ops:['sum','sum','sum'],as:['Revenue','PreviousRevenue','GrossProfit']},{type:'formula',expr:'datum.PreviousRevenue?datum.Revenue/datum.PreviousRevenue-1:null',as:'Growth'},{type:'formula',expr:'datum.Revenue?datum.GrossProfit/datum.Revenue:null',as:'Margin'},{type:'formula',expr:'0',as:'Depth'}]}],
 marks:[{type:'rect',encode:{update:{width:{signal:'width'},height:{value:34},fill:{value:'#EEF2F7'}}}},
 ...[['Kategori',8,'left'],['Omsättning',388,'right'],['Tillväxt',490,'right'],['Bruttovinst',620,'right'],['Marginal',736,'right']].map(([label,x,align])=>txt('header'+x,null,x,17,{value:label},{align:{value:align},fontSize:{value:15},fontWeight:{value:'600'}})),
 {type:'group',clip:true,encode:{update:{y:{value:34},width:{signal:'width'},height:{signal:'bodyH'}}},marks:[
 {name:'rowHit',type:'rect',from:{data:'rows'},encode:{update:{x:{value:0},y:{signal:'(datum.Row-1)*rowH-scrollY'},width:{signal:'width'},height:{signal:'rowH-1'},fill:{field:'Background'},cursor:{signal:"datum.Depth===0?'pointer':'default'"},tooltip:{signal:"{'Post':datum.Label,'Verksamhet':datum.Area===1?'Produktförsäljning':datum.Area===2?'Teknisk service':'Bemanning','Föregående år':replace(format(datum.PreviousRevenue,'.2f'),'.',',')+' Mkr'}"}}}},
 txt('expander','rows',9,'(datum.Row-.5)*rowH-scrollY',{signal:"datum.Depth===0?(indata('open','key',datum.Category)?'▾':'▸'):''"}),
 txt('rowLabel','rows','datum.Depth===0?26:42','(datum.Row-.5)*rowH-scrollY',{field:'Label'},{limit:{value:240},fontWeight:{value:'normal'}}),
 ...values('rows','(datum.Row-.5)*rowH-scrollY'),
 {type:'rect',encode:{update:{x:{value:744},y:{value:0},width:{value:6},height:{signal:'bodyH'},fill:{value:'#EEF2F7'},opacity:{signal:'maxY>0?1:0'}}}},
 {type:'rect',encode:{update:{x:{value:744},y:{signal:'maxY>0?scrollY/maxY*(bodyH-bodyH*bodyH/(maxY+bodyH)):0'},width:{value:6},height:{signal:'bodyH*bodyH/(maxY+bodyH)'},fill:{value:'#9AAAC0'},opacity:{signal:'maxY>0?1:0'},cornerRadius:{value:3}}}}]},
 {type:'rect',encode:{update:{y:{value:276},width:{signal:'width'},height:{value:28},fill:{value:'#FFFFFF'}}}},
 {type:'rule',encode:{update:{x:{value:0},x2:{signal:'width'},y:{value:276},stroke:{value:'#D5DDE7'},strokeWidth:{value:1}}}},
 txt('totalLabel',null,8,290,{value:'Totalt'},{fontWeight:{value:'600'}}),...values('total',290)]};
};
