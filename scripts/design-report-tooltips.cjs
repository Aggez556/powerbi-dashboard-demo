// Apply the approved tooltip grammar to the remaining report pages.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
function design(){
 const report=path.resolve(__dirname,'../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report'),pages=path.join(report,'definition/pages');
 const hash=s=>crypto.createHash('sha256').update(s).digest('hex').slice(0,20);
 const read=f=>JSON.parse(fs.readFileSync(f,'utf8').replace(/^\uFEFF/,''));
 const write=(f,v)=>{fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n');};
 const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?v+'D':"'"+v.replace(/'/g,"''")+"'"}}});
 const color=c=>({solid:{color:lit(c)}});
 const style={show:lit(true),type:lit('Default'),fontFamily:lit('Segoe UI'),fontSize:lit(11),titleFontColor:color('#5B6B80'),valueFontColor:color('#0F3163'),background:color('#FFFFFF'),transparency:lit(0)};
 const labels={
  'Sälj trend':'Försäljning, Mkr','Sälj trend föregående år':'Föregående år, Mkr','Serie':'Verksamhet',
  'Sälj omsättning Mkr':'Försäljning, Mkr','Sälj omsättning föregående år Mkr':'Föregående år, Mkr','Sälj bruttovinst Mkr':'Bruttovinst, Mkr','Sälj tillväxt':'Förändring mot föregående år','Sälj marginal procent':'Bruttomarginal',
  'Trendomsättning föregående år':'Föregående år','Trendomsättning förändring':'Förändring mot föregående år','Rörelsemarginal trend':'Rörelsemarginal','Bryggsteg':'Förändring, Mkr',
  'Trend teknisk':'Teknisk service','Trend bemanning':'Bemanning','Trend mål':'Mål',
  'Tid debiterbar trend':'Debiterbart','Tid kundarbete trend':'Kundarbete, ej debiterat','Tid internt trend':'Internt arbete','Tid ej rapporterat trend':'Ej rapporterat','Tid tillgänglig trend':'Tillgänglig tid','Tid kapacitetsavvikelse trend':'Tid över kapacitet',
  'Historisk cellgrad':'Debiteringsgrad','Uppdrag timmar periodslut':'Utfört till periodslut','Uppdrag planerade':'Planerade timmar','Uppdrag kalkyl':'Kalkylmarginal','Uppdrag faktisk marginaltext':'Faktisk bruttomarginal','Uppdrag kund':'Kund','Uppdrag status historisk':'Status',
  'Steg':'Förändring','Kundbransch':'Bransch','Månadsstart':'Månad'
 };
 const audit=[];let salesTrend;
 for(const name of read(path.join(pages,'pages.json')).pageOrder){
  const p=read(path.join(pages,name,'page.json'));if(p.type==='Tooltip'||p.displayName==='Kunder')continue;
  const row={page:p.displayName,standardTooltips:0,disabledDuplicateCards:0,customTables:0};
  const dir=path.join(pages,name,'visuals');
  for(const entry of fs.readdirSync(dir)){
   const file=path.join(dir,entry,'visual.json');if(!fs.existsSync(file))continue;
   const v=read(file),q=v.visual.query?.queryState;if(!q)continue;
   const type=v.visual.visualType;
   if(type.toLowerCase().includes('slicer'))continue;
   const c=v.visual.visualContainerObjects||={};
   if(type==='cardVisual'){c.visualTooltip=[{properties:{show:lit(false)}}];row.disabledDuplicateCards++;}
   else if(type.startsWith('deneb')){c.visualTooltip=[{properties:structuredClone(style)}];row.customTables++;}
   else{
    c.visualTooltip=[{properties:structuredClone(style)}];row.standardTooltips++;
    // A helper highlighting the selected month is not additional hover information.
    if(q.Tooltips)q.Tooltips.projections=q.Tooltips.projections.filter(p=>(p.field.Measure||{}).Property!=='Sälj trend vald månad');
    // Combined hours/capacity do not explain the two individual utilisation lines.
    if(type==='lineChart'&&q.Y?.projections.some(p=>p.field.Measure?.Property==='Trend teknisk'))delete q.Tooltips;
    for(const role of Object.values(q))for(const projection of role.projections||[]){
     const property=(projection.field.Column||projection.field.Measure)?.Property;
     if(labels[property])projection.nativeQueryRef=projection.displayName=labels[property];
    }
   }
   if(entry==='bd40a85062bdd0a42a40')salesTrend={v,file};
   write(file,v);
  }
  audit.push(row);
 }
 // A shared-month tooltip: three areas, or the selected area's categories.
 const id=hash('report-tooltip:sales-month'),customerPage=hash('customer-tooltip:industry-page');
 const page=read(path.join(pages,customerPage,'page.json'));
 Object.assign(page,{name:id,displayName:'Tooltip · Månadsförsäljning',type:'Tooltip',width:560,height:300});
 page.pageBinding.name=hash('report-tooltip:sales-binding');write(path.join(pages,id,'page.json'),page);
 const save=v=>write(path.join(pages,id,'visuals',v.name,'visual.json'),v);
 for(const [key,label] of [['title','Försäljning per verksamhet'],['subtitle','Pekad månad · jämförelse med samma månad föregående år']]){
  const v=read(path.join(pages,customerPage,'visuals',hash('customer-tooltip:'+key),'visual.json'));
  v.name=hash('report-tooltip:sales-'+key);v.visual.objects.general[0].properties.paragraphs[0].textRuns[0].value=label;save(v);
 }
 const table=read(path.join(pages,customerPage,'visuals',hash('customer-tooltip:table'),'visual.json'));
 table.name=hash('report-tooltip:sales-table');table.position.height=226;
 const q=salesTrend.v.visual.query.queryState;
 const fields=[q.Series.projections[0],q.Y.projections[0],q.Tooltips.projections.find(p=>p.field.Measure.Property==='Sälj trend föregående år')].map(p=>structuredClone(p));
 for(const [i,label] of ['Verksamhet','Försäljning, Mkr','Föregående år, Mkr'].entries())fields[i].displayName=fields[i].nativeQueryRef=label;
 table.visual.query={queryState:{Values:{projections:fields}}};
 table.visual.objects.columnWidth=fields.map((p,i)=>({selector:{metadata:p.queryRef},properties:{value:lit([204,146,154][i])}}));save(table);
 salesTrend.v.visual.visualContainerObjects.visualTooltip=[{properties:{...structuredClone(style),type:lit('Canvas'),section:lit(id)}}];write(salesTrend.file,salesTrend.v);
 const indexFile=path.join(pages,'pages.json'),index=read(indexFile);if(!index.pageOrder.includes(id))index.pageOrder.push(id);write(indexFile,index);
 write(path.join(report,'../validation/report-tooltip-inventory.json'),{pages:audit,salesMonthTooltip:id,modelAndFactDataChanged:false});
 console.log(JSON.stringify(audit));
}
module.exports=design;if(require.main===module)design();
