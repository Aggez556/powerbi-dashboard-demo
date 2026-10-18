// Register the official Deneb package and bind the editable Vega statement.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const buildSpec=require('./budget-statement-spec.cjs');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?`${v}D`:`'${v.replace(/'/g,"''")}'`}}});
const id=s=>crypto.createHash('sha256').update(s).digest('hex').slice(0,20);
const guid='deneb7E15AEF80B9E4D4F8E12924291ECE89A'; // Read from downloaded official package.json.
function install(reportPath){
 const report=reportPath||path.resolve(__dirname,'../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report');
 const page='cbe967640ff6843fb323',dir=path.join(report,'definition/pages',page,'visuals');
 const packageFile=path.join(report,'CustomVisuals',guid,'package.json');
 if(!fs.existsSync(packageFile))throw Error('Unpack the official Deneb package before installing the statement.');
 if(read(packageFile).visual.guid!==guid)throw Error('Unexpected Deneb GUID.');
 const reportFile=path.join(report,'definition/report.json'),definition=read(reportFile);
 definition.resourcePackages=definition.resourcePackages.filter(p=>p.name!==guid);
 definition.resourcePackages.push({name:guid,type:'CustomVisual',items:[{name:guid+'.pbiviz.json',path:guid+'.pbiviz.json',type:'CustomVisualMetadata'}]});
 fs.writeFileSync(reportFile,JSON.stringify(definition,null,2)+'\n');
 const file=path.join(dir,'2fe3adc88d453480ae9c/visual.json'),visual=read(file);
 Object.assign(visual.position,{x:624,y:548,width:1252,height:572});
 const column=(t,p)=>({Column:{Expression:{SourceRef:{Entity:t}},Property:p}});
 const measure=p=>({Measure:{Expression:{SourceRef:{Entity:'Budgetrapportnoder'}},Property:p}});
 const bindings=[['Node','NodID'],['Label','Etikett'],['Parent','Förälder'],['Ancestor','Överförälder'],['Depth','Nivå'],['Kind','Typ'],['Order','Ordning'],['Children','HarBarn'],['Section','Avsnitt']].map(([name,p])=>({name,field:column('Budgetrapportnoder',p)}));
 bindings.push(...[['Group','Grupp'],['GroupOrder','MånadID'],['Metric','Kolumn'],['Slot','Position']].map(([name,p])=>({name,field:column('Budgetkolumner',p)})),...['Amount','Text','Color'].map((name,i)=>({name,field:measure(['Rapportvärde','Rapporttext','Rapportfärg'][i])})));
 const spec=buildSpec();
 visual.visual={visualType:guid,query:{queryState:{dataset:{projections:bindings.map(({name,field})=>{const f=field.Column||field.Measure;return{field,queryRef:f.Expression.SourceRef.Entity+'.'+f.Property,nativeQueryRef:name,displayName:name};})}}},objects:{vega:[{properties:{provider:lit('vega'),jsonSpec:lit(JSON.stringify(spec)),jsonConfig:lit('{}'),renderMode:lit('svg'),enableSelection:lit(false),enableTooltips:lit(true),enableContextMenu:lit(false)}}],dataLimit:[{properties:{override:lit(false),showCustomVisualNotes:lit(false)}}]},visualContainerObjects:{title:[{properties:{show:lit(false)}}],background:[{properties:{show:lit(false)}}],border:[{properties:{show:lit(false)}}],padding:[{properties:{top:lit(0),bottom:lit(0),left:lit(0),right:lit(0)}}],general:[{properties:{altText:lit('Sammanhängande resultaträkning. Klickpilar finns bara på kontogrupper. Resultat och marginaler är beräknade rader utan underposter.')}}]}};
 delete visual.filterConfig;fs.writeFileSync(file,JSON.stringify(visual,null,2)+'\n');
 // Remove only the superseded split-result block and obsolete external buttons.
 const remove=[id('budget-result-layout:calculated-results'),id('budget-result-layout:heading'),...['expand','collapse'].map(key=>id('budget-scenarios:'+page+':'+key))];
 for(const name of remove){const p=path.join(dir,name,'visual.json');if(fs.existsSync(p))fs.unlinkSync(p);if(fs.existsSync(path.join(dir,name)))fs.rmdirSync(path.join(dir,name));}
 for(const name of fs.readdirSync(dir)){
  const p=path.join(dir,name,'visual.json');if(!fs.existsSync(p))continue;const v=read(p);
  if(v.visual.visualType==='textbox'&&v.position.x===624&&v.position.y===1132){v.visual.objects.general[0].properties.paragraphs[0].textRuns[0].value='Avvikelse: + bättre / − sämre · Marginaler i pp · Nollreferens: — · Klickpilar öppnar underkategorier.';fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');}
 }
 const manifest=read(path.join(report,'../validation/budget-statement-model.json'));
 for(const kind of ['expand','collapse','reset']){
  const p=path.join(report,'definition/bookmarks',id('budget-scenarios:'+kind)+'.bookmark.json');if(!fs.existsSync(p))continue;const b=read(p);
  const containers=b.explorationState.sections[page].visualContainers;
  containers[visual.name]={singleVisual:{objects:{merge:{vega:[{properties:{provider:lit('vega'),jsonSpec:lit(JSON.stringify(buildSpec(kind==='expand'?manifest.expandableNodes:kind==='collapse'?[]:undefined))),jsonConfig:lit('{}')}}]}}}};
  b.options.targetVisualNames=b.options.targetVisualNames.filter(n=>!remove.includes(n));fs.writeFileSync(p,JSON.stringify(b,null,2)+'\n');
 }
 const pageFile=path.join(report,'definition/pages',page,'page.json'),p=read(pageFile);
 const exists=new Set(fs.readdirSync(dir));p.visualInteractions=(p.visualInteractions||[]).filter(x=>exists.has(x.source)&&exists.has(x.target));
 fs.writeFileSync(pageFile,JSON.stringify(p,null,2)+'\n');
 fs.writeFileSync(path.join(report,'../validation/budget-statement-spec.json'),JSON.stringify(spec,null,2)+'\n');
 console.log('Installed one integrated, editable Power BI statement with real group expanders and shared scrolling.');
}
module.exports=install;
if(require.main===module)install();
