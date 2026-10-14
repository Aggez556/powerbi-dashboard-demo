const fs=require('fs'),path=require('path');
const dir=path.resolve(__dirname,'../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report/definition/pages/e2f0addc480f40543797/visuals');
for(const name of fs.readdirSync(dir)){
 const file=path.join(dir,name,'visual.json');if(!fs.existsSync(file))continue;
 const v=JSON.parse(fs.readFileSync(file,'utf8'));
 if(v.visual.visualType!=='waterfallChart')continue;
 for(const item of v.visual.objects.labels)item.properties.labelPosition={expr:{Literal:{Value:"'Auto'"}}};
 v.visual.objects.valueAxis[0].properties.end={expr:{Measure:{Expression:{SourceRef:{Entity:'Försäljning'}},Property:'Bryggans övre axelgräns'}}};
 fs.writeFileSync(file,JSON.stringify(v,null,2)+'\n');
 console.log('Waterfall labels use Auto with dynamic headroom above the highest bar.');
}
