// Adjust only the two requested visuals, retaining all other Desktop edits.
const fs=require('fs'),path=require('path');
const report=path.resolve(__dirname,'../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report');
const dir=path.join(report,'definition/pages/b4eda99cffce7ac04192/visuals');
const lit=value=>({expr:{Literal:{Value:typeof value==='boolean'?String(value):`${value}D`}}});
let changed=0;
for(const entry of fs.readdirSync(dir)){
 const file=path.join(dir,entry,'visual.json');if(!fs.existsSync(file))continue;
 const v=JSON.parse(fs.readFileSync(file,'utf8').replace(/^\uFEFF/,''));let update=false;
 if(v.visual.visualType==='pivotTable'){
  v.position.height=304;
  v.visual.objects.grid[0].properties.rowPadding=lit(2);
  update=true;
 }
 if(v.visual.query?.queryState?.Data?.projections?.some(p=>p.queryRef==='Försäljning.Periodtext')){
  v.visual.visualContainerObjects.background=[{properties:{show:lit(false),transparency:lit(100)}}];
  v.visual.objects.fillCustom=[{selector:{id:'default'},properties:{show:lit(true),transparency:lit(100)}}];
  update=true;
 }
 if(update){fs.writeFileSync(file,JSON.stringify(v,null,2)+'\n');changed++;}
}
if(changed!==2)throw Error(`Expected exactly two updated visuals, found ${changed}`);
console.log('Updated matrix height/row spacing and removed period-card background.');
