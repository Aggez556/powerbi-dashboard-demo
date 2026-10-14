const fs=require('fs'),path=require('path');
const dir=path.resolve(__dirname,'../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report/definition/pages/b4eda99cffce7ac04192/visuals');
for(const name of fs.readdirSync(dir)){
 const file=path.join(dir,name,'visual.json');if(!fs.existsSync(file))continue;
 const v=JSON.parse(fs.readFileSync(file,'utf8'));
 if(!v.visual.query?.queryState?.Data?.projections?.some(p=>p.queryRef==='Försäljning.Sälj trend rubrik'))continue;
 const p=v.visual.objects.value[0].properties;
 p.fontFamily={expr:{Literal:{Value:"'Segoe UI Semibold'"}}};
 p.fontSize={expr:{Literal:{Value:'19D'}}};
 p.bold={expr:{Literal:{Value:'false'}}};
 v.position.y=370;
 fs.writeFileSync(file,JSON.stringify(v,null,2)+'\n');
 console.log('Matched dynamic sales trend heading to the other panel headings.');
}
