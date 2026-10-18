const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert/strict');
const report=path.resolve(__dirname,'../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report'),page='f429b020315c602ce0ed';
const hash=s=>crypto.createHash('sha256').update(s).digest('hex').slice(0,20);
const id=k=>hash('customer-page:'+page+':'+k);
const read=f=>JSON.parse(fs.readFileSync(f,'utf8').replace(/^\uFEFF/,''));
const dir=path.join(report,'definition/pages',page,'visuals');
const visual=name=>read(path.join(dir,name,'visual.json'));
const groups=['base','revenue'].map(p=>['title','bridge','summary'].map(k=>id(p+'-'+k)));
for(let mode=0;mode<2;mode++){
 const b=read(path.join(report,'definition/bookmarks',hash('customer-bridge-view:'+mode)+'.bookmark.json'));
 assert.equal(b.options.suppressData,true);assert.equal(b.options.suppressActiveSection,true);
 assert.equal(b.options.applyOnlyToTargetVisuals,true,'Bridge bookmarks must affect selected visuals only.');
 const state=b.explorationState.sections[page].visualContainers;
 assert.equal(Object.keys(state).length,10);
 for(let group=0;group<2;group++)for(const name of groups[group])assert.equal(state[name].singleVisual.display?.mode==='hidden',group!==mode);
 const visibleButtons=[];
 for(let active=0;active<2;active++)for(let choice=0;choice<2;choice++){
  const name=hash('customer-bridge-button:'+active+':'+choice),v=visual(name);
  assert.equal(state[name].singleVisual.display?.mode==='hidden',active!==mode);
  assert.equal(v.visual.visualContainerObjects.visualLink[0].properties.bookmark.expr.Literal.Value,"'"+hash('customer-bridge-view:'+choice)+"'");
  if(active===mode)visibleButtons.push(name);
 }
 assert.equal(visibleButtons.length,2);
 assert.deepEqual(new Set(b.options.targetVisualNames),new Set(Object.keys(state)));
}
const charts=groups.map(g=>visual(g[1]));
for(const v of charts)assert.equal(v.visual.visualType,'waterfallChart');
for(const prop of ['x','y','width','height'])assert.equal(charts[0].position[prop],charts[1].position[prop]);
assert.equal(!!charts[0].isHidden,false);assert.equal(!!charts[1].isHidden,true);
assert.equal(charts[0].visual.query.queryState.Y.projections[0].field.Measure.Property,'Kundbas bryggsteg');
assert.equal(charts[1].visual.query.queryState.Y.projections[0].field.Measure.Property,'Kundintäkt bryggsteg');
assert(!fs.existsSync(path.join(dir,id('revenue-panel'),'visual.json')));
for(const entry of fs.readdirSync(dir)){
 const file=path.join(dir,entry,'visual.json');if(!fs.existsSync(file))continue;const v=read(file),p=v.position;
 if(v.visual.visualType==='waterfallChart')assert(!(p.x>=288&&p.x<1086&&p.y>=792&&p.y<1176),'Standalone lower-left waterfall must be removed: '+entry);
}
const result={status:'passed',views:2,displayOnly:true,periodAndIndustryFiltersPreserved:true,bothTransitionsCovered:true,standaloneLowerLeftBridgeRemoved:true};
fs.writeFileSync(path.join(report,'../validation/customer-bridge-toggle-check.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result));
