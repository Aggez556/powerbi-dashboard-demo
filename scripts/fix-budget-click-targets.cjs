// Keep native button/slicer hit areas above decorative report elements.
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const report=path.resolve(__dirname,'../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report');
const dir=path.join(report,'definition/pages/cbe967640ff6843fb323/visuals');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8').replace(/^\uFEFF/,''));
const visuals=fs.readdirSync(dir).map(n=>path.join(dir,n,'visual.json')).filter(fs.existsSync).map(file=>({file,v:read(file)}));
const controls=visuals.filter(({v})=>v.position.x===312&&v.position.y>=450&&['actionButton','advancedSlicerVisual','slicer'].includes(v.visual.visualType));
for(const {v,file} of controls){
 v.position.z=2000+v.position.tabOrder;
 if(v.visual.visualType==='actionButton')assert(v.visual.visualContainerObjects.visualLink[0].properties.bookmark,'Native button requires a bookmark action.');
 fs.writeFileSync(file,JSON.stringify(v,null,2)+'\n');
}
// An obsolete, empty help textbox intersects the fourth scenario tile.
const help=visuals.find(({v})=>v.name==='02ab4eacb4cbda1f85b7');
if(help){help.v.isHidden=true;fs.writeFileSync(help.file,JSON.stringify(help.v,null,2)+'\n');}
for(const {v} of controls.filter(({v})=>!v.isHidden))for(const {v:other} of visuals){
 if(other.name===v.name||other.isHidden)continue;
 const a=v.position,b=other.position;
 const intersects=a.x<b.x+b.width&&a.x+a.width>b.x&&a.y<b.y+b.height&&a.y+a.height>b.y;
 assert(!intersects||b.z<a.z,'A visible layer covers control '+v.name+': '+other.name);
}
assert.equal(controls.length,10);
console.log('Checked 10 native Budget controls: full button text and tile areas are above decorative layers; no visible overlay intercepts clicks.');
