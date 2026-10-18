import * as vega from '../.tools/vega-validation/node_modules/vega/build/vega.module.js';
import fs from 'node:fs';
import assert from 'node:assert/strict';
import buildSpec from './budget-statement-spec.cjs';
const base='powerbi-ledningsrapport/validation/';
const dataset=JSON.parse(fs.readFileSync(base+'budget-statement-fixture.json','utf8'));
const spec=buildSpec();
assert(spec.marks.findIndex(m=>m.name==='header')>spec.marks.findIndex(m=>m.name==='body'));
assert(spec.marks.findIndex(m=>m.name==='columnHeaders')>spec.marks.findIndex(m=>m.name==='header'));
assert.equal(spec.marks.find(m=>m.name==='header').encode.update.fillOpacity.value,1);
const view=new vega.View(vega.parse(buildSpec()),{renderer:'none'});
await view.change('dataset',vega.changeset().insert(dataset)).runAsync();
assert.equal(view.data('columns').length,8);
assert.equal(view.data('rows').length,16);
const calculated=new Set(['Bruttovinst','Bruttomarginal','Rörelseresultat','Rörelsemarginal']);
assert.equal(view.data('rows').filter(r=>calculated.has(r.Label)).length,4);
assert(view.data('rows').filter(r=>calculated.has(r.Label)).every(r=>r.Children===0));
assert.equal(view.data('expandables').length,6);
await view.signal('clickedNode','r6').runAsync();
assert.equal(view.data('rows').length,9);
await view.signal('clickedNode','r1').runAsync();
assert.equal(view.data('rows').length,12);
await view.signal('expandAll',1).runAsync();
assert.equal(view.data('rows').length,26);
assert.equal(view.data('varianceCells').length,104);
assert(view.data('varianceCells').every(r=>r.Slot===2));
for(const row of view.data('varianceCells').filter(r=>r.GroupOrder===13)){
 const expected=dataset.find(r=>r.Node===row.Node && r.GroupOrder===13 && r.Slot===3);
 assert.equal(row.VarianceText,expected.Text);
 assert.equal(row.VarianceColor,expected.Color);
}
assert(view.signal('maxY')>0);
await view.signal('clickedNode','r6').runAsync();
assert.equal(view.data('rows').length,19);
await view.signal('clickedNode',null).runAsync();
await view.signal('clickedNode','r6').runAsync();
assert.equal(view.data('rows').length,26);
await view.signal('scrollY',50).runAsync();
assert.equal(view.signal('scrollY'),50);
await view.signal('collapseAll',1).runAsync();
assert.equal(view.data('rows').length,9);
assert(view.signal('scrollY')<=view.signal('maxY'));
// Calculated and leaf rows have no child relationship, so no fake expanders.
assert(view.data('rows').filter(r=>r.Children).every(r=>r.Kind==='grupp'));
const svg=await view.toSVG();assert(svg.includes('Nettoomsättning'));assert(svg.includes('Rörelseresultat'));
fs.writeFileSync(base+'budget-statement-component.svg',svg);
const wide=JSON.parse(fs.readFileSync(base+'budget-statement-wide-fixture.json','utf8'));
await view.change('dataset',vega.changeset().remove(()=>true).insert(wide)).runAsync();
assert.equal(view.data('columns').length,20);assert(view.signal('maxX')>0);
await view.signal('scrollX',250).runAsync();assert.equal(view.signal('scrollX'),250);
const scenarios=JSON.parse(fs.readFileSync(base+'budget-statement-scenarios-fixture.json','utf8'));
await view.change('dataset',vega.changeset().remove(()=>true).insert(scenarios)).runAsync();
assert.equal(view.data('columns').length,26);
assert(view.data('columns').some(c=>c.Metric==='A · Försiktigt scenario'));
assert(view.data('columns').some(c=>c.Metric==='B · Huvudscenario'));
assert((await view.toSVG()).includes('Försiktigt'));
for(const row of view.data('varianceCells').filter(r=>r.GroupOrder===13)){
 const expected=scenarios.find(r=>r.Node===row.Node && r.GroupOrder===13 && r.Slot===3);
 assert.equal(row.VarianceText,expected.Text);
 assert.equal(row.VarianceColor,expected.Color);
}
const seed=dataset.find(r=>r.Slot===1);
const cases=[[-100,-90,'+10,0 %','#007956'],[-100,-110,'−10,0 %','#B42318'],[0,10,'—','#5B6B80'],[100,100.01,'0,0 %','#5B6B80']];
for(const [budget,actual,label,color] of cases){
 const clean=JSON.parse(JSON.stringify(seed));
 const pair=[{...clean,Amount:budget,Slot:1},{...clean,Amount:actual,Slot:2,Metric:'Utfall'}];
 await view.change('dataset',vega.changeset().remove(()=>true).insert(pair)).runAsync();
 assert.equal(view.data('varianceCells')[0].VarianceText,label);
 assert.equal(view.data('varianceCells')[0].VarianceColor,color);
}
const prior=dataset.map(row=>({...row,Metric:row.Slot===1?'Föregående år':row.Metric}));
await view.change('dataset',vega.changeset().remove(()=>true).insert(prior)).runAsync();
assert.equal(view.signal('budgetW'),120);
await view.signal('scrollX',0).runAsync();
const priorSvg=await view.toSVG();
assert(priorSvg.includes('>Föreg. år<'));
const report={status:'passed',engine:'Local Vega dataflow, not Power BI Desktop rendering',priorYearHeader:true,defaultVisibleRows:16,collapsedRows:9,expandedRows:26,defaultColumns:8,wideColumns:20,inlineMonthlyVariance:true,zeroBudgetAndCostSigns:true,onlyRealGroupsExpand:true,calculatedRowsHaveNoChildren:true,expandCollapseSignals:true,horizontalAndVerticalScrollSignals:true,rootAmountsMatchPreviousLiveDAX:true};
fs.writeFileSync(base+'budget-statement-component-check.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));view.finalize();
