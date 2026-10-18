// Focused finishing pass; existing page, data and navigation remain in place.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const report=path.resolve(__dirname,'../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report');
const page='30e52cac0a5174639318',dir=path.join(report,'definition/pages',page,'visuals');
const id=k=>crypto.createHash('sha256').update('assignment-page:'+page+':'+k).digest('hex').slice(0,20);
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?v+'D':"'"+v.replace(/'/g,"''")+"'"}}});
const color=c=>({solid:{color:lit(c)}});
const file=k=>path.join(dir,id(k),'visual.json');
const write=v=>{const p=path.join(dir,v.name,'visual.json');fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');};
const update=(k,fn)=>{const v=read(file(k));fn(v);write(v);};
update('table-title',v=>{
 for(const paragraph of v.visual.objects.general[0].properties.paragraphs)
  for(const run of paragraph.textRuns)run.textStyle.fontSize='18pt';
});
function legend(key,runs,box){
 const v=read(file('heat-legend'));v.name=id(key);Object.assign(v.position,{x:box[0],y:box[1],width:box[2],height:box[3],z:310});
 v.visual.objects.general[0].properties.paragraphs=[{horizontalTextAlignment:'left',textRuns:runs.map(([value,ink])=>({value,textStyle:{fontFamily:'Segoe UI',fontSize:'10.5pt',color:ink}}))}];write(v);
}
const dateField={Column:{Expression:{SourceRef:{Entity:'Trendaxel'}},Property:'Månadsstart'}};
const monthProjection={field:dateField,queryRef:'Trendaxel.Månadsstart',nativeQueryRef:'Månad',displayName:'Månad'};
for(const key of ['trend','bookings'])update(key,v=>{
 v.visual.query.queryState.Category.projections=[monthProjection];
 v.visual.query.sortDefinition={sort:[{field:dateField,direction:'Ascending'}],isDefaultSort:false};
 v.visual.objects.categoryAxis[0].properties.axisType=lit('Categorical');
 v.visual.objects.categoryAxis[0].properties.fontSize=lit(10);
 v.visual.objects.legend=[{properties:{show:lit(false)}}];
 if(key==='bookings')Object.assign(v.visual.objects.valueAxis[0].properties,{showAxisTitle:lit(false)});
 if(key==='trend'){
  v.visual.query.queryState.Y.projections=v.visual.query.queryState.Y.projections.filter(p=>p.field.Measure.Property!=='Trend vald månad');
  for(const object of ['dataPoint','lineStyles'])v.visual.objects[object]=v.visual.objects[object].filter(e=>e.selector?.metadata!=='Planinställning.Trend vald månad');
  Object.assign(v.position,{x:304,y:536,width:388,height:268});
 }else Object.assign(v.position,{x:740,y:536,width:428,height:248});
});
legend('trend-subtitle',[['12 månaders historik','#5B6B80']],[304,456,388,24]);
legend('trend-legend',[['● ','#0F3163'],['Teknisk service   ','#5B6B80'],['● ','#007956'],['Bemanning','#5B6B80']],[304,488,388,24]);
legend('trend-legend-target',[['— ','#8296B4'],['Mål 82 %','#5B6B80']],[304,510,388,24]);
legend('time-legend0',[['● ','#0F3163'],['Debiterbart   ','#5B6B80'],['● ','#65BBA6'],['Kundarbete, ej deb.','#5B6B80']],[740,488,428,24]);
legend('time-legend2',[['● ','#6D8FBE'],['Internt arbete   ','#5B6B80'],['● ','#B8CBDD'],['Ej rapporterat','#5B6B80']],[740,510,428,24]);
legend('plan-subtitle',[['Timmar per månad','#5B6B80']],[740,456,428,24]);
legend('heat-subtitle',[['Andel debiterbar tid per månad','#5B6B80']],[1216,456,668,24]);
legend('heat-legend',[['● ','#DF8980'],['Under 75 %   ','#5B6B80'],['● ','#8FB9E1'],['75–82 %   ','#5B6B80'],['● ','#65BBA6'],['Minst 82 %','#5B6B80']],[1216,488,668,24]);
// Remove obsolete separate legend textboxes after merging their text runs.
for(const key of ['trend-legend-service','time-legend1','time-legend3','heat-legend-mid','heat-legend-high']){
 const target=file(key);if(fs.existsSync(target))fs.unlinkSync(target);
 const folder=path.dirname(target);if(fs.existsSync(folder)&&fs.readdirSync(folder).length===0)fs.rmdirSync(folder);
}
update('heat',v=>{
 v.visual.query.queryState.Columns.projections=[monthProjection];
 v.visual.query.sortDefinition={sort:[{field:dateField,direction:'Ascending'}],isDefaultSort:false};
 v.visual.objects.columnHeaders[0].properties.wordWrap=lit(true);
});
// Generate a code-native calendar icon for the previously missing active state.
const name='navigation-projects-FFFFFF.svg',resources=path.join(report,'StaticResources/RegisteredResources');
fs.writeFileSync(path.join(resources,name),'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 11h18M7 15h3M14 15h3M7 18h3"/></svg>\n');
const reportFile=path.join(report,'definition/report.json'),r=read(reportFile),pkg=r.resourcePackages.find(p=>p.name==='RegisteredResources');
if(!pkg.items.some(x=>x.name===name))pkg.items.push({name,path:name,type:'Image'});
fs.writeFileSync(reportFile,JSON.stringify(r,null,2)+'\n');
const changed=new Set([page]);
for(const p of fs.readdirSync(path.join(report,'definition/pages'))){
 const visuals=path.join(report,'definition/pages',p,'visuals');if(!fs.existsSync(visuals))continue;
 for(const key of fs.readdirSync(visuals)){
  const f=path.join(visuals,key,'visual.json');if(!fs.existsSync(f))continue;const old=fs.readFileSync(f,'utf8');
  if(old.includes('navigation-projects-FFFFFF.png')){fs.writeFileSync(f,old.replaceAll('navigation-projects-FFFFFF.png',name));changed.add(p);}
 }
}
fs.writeFileSync(path.join(report,'../validation/historical-details-pages.json'),JSON.stringify({changedPages:[...changed],activeIcon:name,shortDateFormat:'MMM',staticLegends:true},null,2)+'\n');
console.log('Raised captions above panels, shortened month labels, fitted legends and repaired active navigation icon.');
