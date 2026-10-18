import fs from 'node:fs';
import assert from 'node:assert/strict';
import * as vega from '../.tools/vega-validation/node_modules/vega/build/vega.module.js';
import build from './sales-colored-rows-spec.cjs';
const base='powerbi-ledningsrapport/validation/';
const live=JSON.parse(fs.readFileSync(base+'sales-colored-rows-live.json','utf8').replace(/^\uFEFF/,'')).resultSets[0];
const data=live.map(r=>({Category:r['Artiklar[Kategori]'],Article:r['Artiklar[Artikel]'],Area:r['Artiklar[Områdesordning]'],Order:r['Artiklar[Kategoriordning]'],RevenueKrona:r['[Revenue]'],PreviousRevenueKrona:r['[PreviousRevenue]'],GrossProfitKrona:r['[GrossProfit]']}));
const view=new vega.View(vega.parse(build()),{renderer:'none'});
await view.change('dataset',vega.changeset().insert(data)).runAsync();
assert.equal(view.data('rows').length,8);assert.equal(view.signal('maxY'),0);
assert.equal(new Set(view.data('rows').map(r=>r.Background)).size,3);
const total=view.data('total')[0];assert(Math.abs(total.Revenue-139.5)<1e-8);assert(Math.abs(total.GrossProfit-36.04)<1e-8);assert(Math.abs(total.PreviousRevenue-120)<1e-8);
function assertHierarchy(){
 const rows=[...view.data('rows')].sort((a,b)=>a.Row-b.Row);
 for(let i=0;i<rows.length;i++){
  assert.equal(rows[i].Row,i+1);
  if(i)assert(rows[i].Sort>rows[i-1].Sort,'Displayed rows must follow hierarchy order.');
  if(rows[i].Depth===1){let parent=i-1;while(parent>=0&&rows[parent].Depth===1)parent--;assert(parent>=0);assert.equal(rows[i].Category,rows[parent].Category,'Articles must appear directly below their own category.');}
 }
}
const middle=view.data('categories')[1].Category;
await view.signal('clicked',middle).runAsync();assertHierarchy();
await view.signal('clicked',null).runAsync();
await view.signal('clicked',middle).runAsync();assertHierarchy();assert.equal(view.data('rows').length,8);
for(const category of view.data('categories')){
 const parts=data.filter(r=>r.Category===category.Category);
 assert(Math.abs(parts.reduce((s,r)=>s+r.RevenueKrona/1000000,0)-category.Revenue)<1e-8);
 await view.signal('clicked',category.Category).runAsync();
 assertHierarchy();
}
assert.equal(view.data('rows').length,24);assert(view.signal('maxY')>0);
for(const r of view.data('rows'))assert.equal(r.Background,r.Depth===1?'#FFFFFF':['#E3EBF5','#E4F1E9','#FAEBD7'][r.Area-1]);
await view.signal('scrollY',50).runAsync();assert.equal(view.signal('scrollY'),50);
const svg=await view.toSVG();assert(svg.includes('Totalt'));assert(svg.includes('Maskiner'));
assert.equal(build().marks.find(m=>m.type==='rect'&&m.encode.update.y?.value===276).encode.update.fill.value,'#FFFFFF');
fs.writeFileSync(base+'sales-colored-rows.svg',svg);
console.log('PASS: live DAX totals, 8 categories, 16 articles, three distinct business-area row colors, expansion, scrolling and weighted margins.');view.finalize();
