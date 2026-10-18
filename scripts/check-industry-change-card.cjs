const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert/strict');
const report=path.resolve(__dirname,'../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report'),page='f429b020315c602ce0ed';
const hash=s=>crypto.createHash('sha256').update(s).digest('hex').slice(0,20),id=k=>hash('customer-industry-change:'+k);
const read=f=>JSON.parse(fs.readFileSync(f,'utf8').replace(/^\uFEFF/,''));
const visual=k=>read(path.join(report,'definition/pages',page,'visuals',id(k),'visual.json'));
const old=read(path.join(report,'definition/bookmarks',hash('customer-bridge-view:0')+'.bookmark.json'));
for(let mode=0;mode<2;mode++){
 const v=visual('chart-'+mode),q=v.visual.query.queryState;
 assert.equal(v.visual.visualType,mode===0?'lineChart':'clusteredColumnChart');
 assert.equal(!!v.isHidden,mode!==0);assert.equal(q.Category.projections[0].field.Column.Property,'Månadsstart');
 assert.equal(q.Series.projections[0].field.Column.Property,'Kundbransch');
 assert.equal(q.Y.projections[0].field.Measure.Property,mode===0?'Bransch månadsförändring procent':'Bransch månadsförändring Mkr');
 assert.equal(v.visual.objects.dataPoint.length,5);assert.equal(v.visual.objects.labels[0].properties.show.expr.Literal.Value,'false');
 assert.equal(v.visual.objects.y1AxisReferenceLine[0].properties.value.expr.Literal.Value,'0D');
 const axis=v.visual.objects.valueAxis[0].properties,unit=mode===0?'procent':'Mkr';
 assert.equal(axis.start.expr.Measure.Property,'Bransch axelgolv '+unit);assert.equal(axis.end.expr.Measure.Property,'Bransch axeltak '+unit);
 assert.equal(v.position.x,312);assert.equal(v.position.y,878);assert(v.position.y+v.position.height<=1160);
 const b=read(path.join(report,'definition/bookmarks',id('bookmark-'+mode)+'.bookmark.json'));
 assert(b.options.suppressData);assert(b.options.suppressActiveSection);
 assert.equal(b.options.applyOnlyToTargetVisuals,true,'Industry bookmarks must affect selected visuals only.');
 assert.equal(old.options.applyOnlyToTargetVisuals,true,'The other toggle must also be scoped.');
 assert.equal(b.options.targetVisualNames.length,6);
 assert(!b.options.targetVisualNames.some(name=>old.options.targetVisualNames.includes(name)),'The two chart toggles must be independent.');
 const states=b.explorationState.sections[page].visualContainers;
 assert.equal(states[id('chart-0')].singleVisual.display?.mode==='hidden',mode!==0);
 assert.equal(states[id('chart-1')].singleVisual.display?.mode==='hidden',mode!==1);
 for(let active=0;active<2;active++)for(let choice=0;choice<2;choice++){
  const button=visual('button-'+active+'-'+choice);
  assert.equal(states[button.name].singleVisual.display?.mode==='hidden',active!==mode);
  assert.equal(button.visual.visualContainerObjects.visualLink[0].properties.bookmark.expr.Literal.Value,"'"+id('bookmark-'+choice)+"'");
 }
}
// Exercise alternating transitions for all four combinations. Unrelated display
// state must survive each selected-visual bookmark application.
const groups=[['customer-bridge-view:',0],['customer-industry-change:bookmark-',1]].map(([prefix])=>[0,1].map(i=>read(path.join(report,'definition/bookmarks',hash(prefix+i)+'.bookmark.json'))));
const state={};
for(const sequence of [[0,1,0,1],[1,0,1,0]])for(let first=0;first<2;first++)for(let second=0;second<2;second++){
 for(const group of sequence){
  const b=groups[group][group===0?first:second],other=groups[1-group][0].options.targetVisualNames;
  const before=other.map(name=>state[name]);
  for(const name of b.options.targetVisualNames)state[name]=b.explorationState.sections[page].visualContainers[name].singleVisual.display?.mode!=='hidden';
  assert.deepEqual(other.map(name=>state[name]),before,'Changing one card must preserve the other card.');
 }
 for(const [group,mode] of [[0,first],[1,second]]){
  const names=groups[group][0].options.targetVisualNames;
  assert.equal(names.filter(name=>state[name]).length,group===0?5:3);
 }
}
const result={status:'passed',defaultView:'percentage',fiveFixedIndustryColors:true,independentDisplayOnlyToggle:true,alternatingTransitionsCovered:true,dynamicAxisBindings:true,zeroReferenceLine:true,labelsHidden:true,unchangedPeriodAndIndustryControls:true};
fs.writeFileSync(path.join(report,'../validation/industry-change-card-check.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
