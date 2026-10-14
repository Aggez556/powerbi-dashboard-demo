const fs=require('fs'),path=require('path');
const dir=path.resolve(__dirname,'../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report/definition/pages/b4eda99cffce7ac04192/visuals');
for(const name of fs.readdirSync(dir)){
 const file=path.join(dir,name,'visual.json');if(!fs.existsSync(file))continue;
 const v=JSON.parse(fs.readFileSync(file,'utf8'));
 if(!['scatterChart','columnChart'].includes(v.visual.visualType))continue;
 // Retain the native, area-filtered legend and the existing bottom edge.
 v.position.y=376;v.position.height=376;
 if(v.visual.visualType==='scatterChart')v.visual.objects.valueAxis[0].properties.end={expr:{Literal:{Value:'45D'}}};
 fs.writeFileSync(file,JSON.stringify(v,null,2)+'\n');
 console.log('Aligned '+v.visual.visualType+' native legend with its heading at the top right.');
}
