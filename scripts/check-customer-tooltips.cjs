const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert/strict');
const root=path.resolve(__dirname,'../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report/definition/pages');
const hash=s=>crypto.createHash('sha256').update(s).digest('hex').slice(0,20);
const read=f=>JSON.parse(fs.readFileSync(f,'utf8').replace(/^\uFEFF/,''));
const id=hash('customer-tooltip:industry-page'),p=read(path.join(root,id,'page.json'));
assert.equal(p.pageBinding.type,'Tooltip');assert.equal(p.visibility,'HiddenInViewMode');
assert.equal(p.type,'Tooltip','A tooltip binding alone does not mark the page as a tooltip.');
assert.equal(p.pageBinding.acceptsFilterContext,'Default');
for(let i=0;i<2;i++){
 const v=read(path.join(root,'f429b020315c602ce0ed/visuals',hash('customer-industry-change:chart-'+i),'visual.json'));
 assert.equal(v.visual.visualContainerObjects.visualTooltip[0].properties.section.expr.Literal.Value,"'"+id+"'");
}
const table=read(path.join(root,id,'visuals',hash('customer-tooltip:table'),'visual.json'));
assert.equal(table.visual.query.queryState.Values.projections.length,4);
assert.equal(table.visual.objects.total[0].properties.totals.expr.Literal.Value,'false');
assert(!table.filterConfig,'Tooltip must inherit hovered month and industry context.');
assert(table.position.y+table.position.height<=p.height);
assert.equal(table.visual.visualContainerObjects.visualTooltip[0].properties.show.expr.Literal.Value,'false');
console.log('Tooltip pilot checks passed: hidden report tooltip, both views connected, four columns, no misleading totals, inherited filter context.');
