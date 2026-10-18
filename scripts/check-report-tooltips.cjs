const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert/strict');
const root=path.resolve(__dirname,'../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report/definition/pages');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8').replace(/^\uFEFF/,''));
const hash=s=>crypto.createHash('sha256').update(s).digest('hex').slice(0,20);
const tooltip=hash('report-tooltip:sales-month'),p=read(path.join(root,tooltip,'page.json'));
assert.equal(p.type,'Tooltip');assert.equal(p.visibility,'HiddenInViewMode');assert.equal(p.pageBinding.acceptsFilterContext,'Default');
const table=read(path.join(root,tooltip,'visuals',hash('report-tooltip:sales-table'),'visual.json'));
const fields=table.visual.query.queryState.Values.projections;
assert.equal(fields.length,3);assert.equal(fields[1].field.Measure.Property,'Sälj trend');assert.equal(fields[2].field.Measure.Property,'Sälj trend föregående år');
assert(!table.filterConfig);assert.equal(table.visual.objects.total[0].properties.totals.expr.Literal.Value,'false');
assert(table.position.y+table.position.height<=p.height);
assert(table.visual.objects.columnWidth.reduce((sum,c)=>sum+parseFloat(c.properties.value.expr.Literal.Value),0)+24<=table.position.width);
const chart=read(path.join(root,'b4eda99cffce7ac04192/visuals/bd40a85062bdd0a42a40/visual.json'));
assert.equal(chart.visual.visualContainerObjects.visualTooltip[0].properties.section.expr.Literal.Value,"'"+tooltip+"'");
assert(!chart.visual.query.queryState.Tooltips.projections.some(p=>p.field.Measure.Property==='Sälj trend vald månad'));
let checked=0;
for(const page of ['e2f0addc480f40543797','b4eda99cffce7ac04192','cbe967640ff6843fb323','30e52cac0a5174639318']){
 const dir=path.join(root,page,'visuals');
 for(const name of fs.readdirSync(dir)){
  const file=path.join(dir,name,'visual.json');if(!fs.existsSync(file))continue;
  const v=read(file);if(!v.visual.query||v.visual.visualType.toLowerCase().includes('slicer'))continue;
  const props=v.visual.visualContainerObjects.visualTooltip[0].properties;
  if(v.visual.visualType==='cardVisual')assert.equal(props.show.expr.Literal.Value,'false');
  else{assert.equal(props.fontSize.expr.Literal.Value,'11D');assert.equal(props.transparency.expr.Literal.Value,'0D');}
  checked++;
 }
}
console.log('PASS: '+checked+' data visuals checked across four pages; sales tooltip wiring, units, bounds, total suppression and hidden page type verified.');
