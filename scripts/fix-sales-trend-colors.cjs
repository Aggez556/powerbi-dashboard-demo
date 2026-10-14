const fs=require('fs'),path=require('path');
const palette=['#0F3163','#007956','#4A6BCE'];
const groups=[['Produktförsäljning','Teknisk service','Bemanning'],['Maskiner','Rengöringsprodukter','Förbrukningsmaterial'],['Service','Reparationer','Installationer'],['Diskpersonal','Städpersonal']];
const dataPoint=groups.flatMap(names=>names.map((name,i)=>({selector:{data:[{scopeId:{Comparison:{ComparisonKind:0,Left:{Column:{Expression:{SourceRef:{Entity:'Försäljningsserie'}},Property:'Serie'}},Right:{Literal:{Value:"'"+name+"'"}}}}}]},properties:{fill:{solid:{color:{expr:{Literal:{Value:"'"+palette[i]+"'"}}}}}}})));
module.exports=dataPoint;
if(require.main===module){
 const dir=path.resolve(__dirname,'../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report/definition/pages/b4eda99cffce7ac04192/visuals');
 let count=0;
 for(const name of fs.readdirSync(dir)){
  const file=path.join(dir,name,'visual.json');if(!fs.existsSync(file))continue;
  const v=JSON.parse(fs.readFileSync(file,'utf8'));
  if(v.visual.visualType!=='columnChart')continue;
  v.visual.objects.dataPoint=dataPoint;
  fs.writeFileSync(file,JSON.stringify(v,null,2)+'\n');count++;
 }
 if(count!==1)throw Error(`Expected one sales trend, got ${count}`);
 console.log('Fixed all area/category series to the existing navy, green and blue palette.');
}
