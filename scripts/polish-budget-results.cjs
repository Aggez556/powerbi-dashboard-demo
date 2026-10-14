// Two native matrices retain the same month/scenario columns and filters.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?`${v}D`:`'${v}'`}}});
const color=c=>({solid:{color:lit(c)}});
const id=s=>crypto.createHash('sha256').update('budget-result-layout:'+s).digest('hex').slice(0,20);
function polish(reportPath){
 const report=reportPath||path.resolve(__dirname,'../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report');
 const page='cbe967640ff6843fb323',dir=path.join(report,'definition/pages',page,'visuals');
 const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
 const save=v=>{const d=path.join(dir,v.name);fs.mkdirSync(d,{recursive:true});fs.writeFileSync(path.join(d,'visual.json'),JSON.stringify(v,null,2)+'\n');};
 const main=read(path.join(dir,'2fe3adc88d453480ae9c/visual.json')),o=main.visual.objects;
 const account={Column:{Expression:{SourceRef:{Entity:'Budgetrader'}},Property:'KontoID'}};
 const ids=fs.readFileSync(path.join(report,'../data/Budgetrader.csv'),'utf8').split(/\r?\n/).slice(1).filter(Boolean).map(line=>Number(line.split(',')[0]));
 const rowFilter=kind=>({filters:[{name:id('filter-'+kind),field:account,type:'Categorical',howCreated:'User',filter:{Version:2,From:[{Name:'r',Entity:'Budgetrader',Type:0}],Where:[{Condition:{In:{Expressions:[{Column:{Expression:{SourceRef:{Source:'r'}},Property:'KontoID'}}],Values:ids.filter(n=>kind==='accounts'?n>0:n<0).map(n=>[{Literal:{Value:n+'L'}}])}}}]}}]});
 // Positive IDs are account leaves; the four calculated rows have negative IDs.
 main.position.height=320;main.filterConfig=rowFilter('accounts');
 Object.assign(o.subTotals[0].properties,{rowSubtotals:lit(false),perRowLevel:lit(true),rowSubtotalsPosition:lit('Top')});
 o.subTotals=o.subTotals.filter(x=>!x.selector?.metadata);
 for(const name of ['Rad','Undergrupp'])o.subTotals.push({selector:{metadata:'Budgetrader.'+name},properties:{levelSubtotalEnabled:lit(true)}});
 o.rowTotal=[{properties:{fontColor:color('#FFFFFF'),backColor:color('#FFFFFF'),applyToHeaders:lit(true)}}];
 o.rowHeaders=o.rowHeaders.filter(x=>!x.selector?.data);
 Object.assign(o.rowHeaders[0].properties,{showExpandCollapseButtons:lit(true),fontFamily:lit('Segoe UI'),bold:lit(false),italic:lit(false),backColor:color('#FFFFFF')});
 o.values=o.values.filter(x=>!x.selector?.data?.some(d=>d.scopeId));
 Object.assign(o.values[0].properties,{fontFamily:lit('Segoe UI'),bold:lit(false),italic:lit(false)});
 for(const p of main.visual.query.queryState.Columns.projections)p.active=true;
 save(main);

 const results=structuredClone(main);results.name=id('calculated-results');
 Object.assign(results.position,{y:936,height:176,z:main.position.z+1,tabOrder:main.position.tabOrder+1});
 results.filterConfig=rowFilter('results');
 results.visual.query.queryState.Rows.projections=results.visual.query.queryState.Rows.projections.slice(0,1);
 results.visual.query.queryState.Rows.projections[0].active=true;
 results.visual.query.queryState.Rows.projections[0].displayName='Beräknat resultat';
 results.visual.expansionStates=results.visual.expansionStates.filter(x=>!x.roles.includes('Rows'));
 const ro=results.visual.objects;
 ro.subTotals=[{properties:{rowSubtotals:lit(false),columnSubtotals:lit(false)}}];
 Object.assign(ro.rowHeaders[0].properties,{showExpandCollapseButtons:lit(false),fontFamily:lit('Segoe UI Semibold'),fontSize:lit(12),bold:lit(true),backColor:color('#E8EEF6'),stepped:lit(false)});
 Object.assign(ro.values[0].properties,{fontFamily:lit('Segoe UI Semibold'),fontSize:lit(12),bold:lit(true),backColorPrimary:color('#E8EEF6'),backColorSecondary:color('#F3F6FA'),bandedRowHeaders:lit(true)});
 results.visual.visualContainerObjects.general=[{properties:{altText:lit('Beräknade resultat och marginaler utan underkategorier')}}];save(results);

 save({$schema:main.$schema,name:id('heading'),position:{x:624,y:892,width:1252,height:32,z:main.position.z+2,tabOrder:main.position.tabOrder+2},visual:{visualType:'textbox',objects:{general:[{properties:{paragraphs:[{textRuns:[{value:'Beräknade resultat och marginaler',textStyle:{fontFamily:'Segoe UI Semibold',fontSize:'15pt',color:'#0F3163'}}],horizontalTextAlignment:'left'}]}}]},visualContainerObjects:{background:[{properties:{show:lit(false)}}],border:[{properties:{show:lit(false)}}],padding:[{properties:{top:lit(0),bottom:lit(0),left:lit(0),right:lit(0)}}]}}});
 for(const name of fs.readdirSync(dir)){
  const p=path.join(dir,name,'visual.json');if(!fs.existsSync(p))continue;const x=read(p);
  if(x.visual.visualType!=='textbox'||x.position.x!==624||x.position.y!==1132)continue;
  x.visual.objects.general[0].properties.paragraphs[0].textRuns[0].value='Övre delen: expandera kontogrupper för detaljer · Nedre delen: beräknade resultat utan underposter.';save(x);
 }
 const pageFile=path.join(report,'definition/pages',page,'page.json'),config=read(pageFile);
 const targets=fs.readdirSync(dir).filter(name=>fs.existsSync(path.join(dir,name,'visual.json')));
 config.visualInteractions=config.visualInteractions||[];
 for(const source of [main.name,results.name])for(const target of targets){
  if(source===target)continue;const existing=config.visualInteractions.find(x=>x.source===source&&x.target===target);
  if(existing)existing.type='NoFilter';else config.visualInteractions.push({source,target,type:'NoFilter'});
 }
 fs.writeFileSync(pageFile,JSON.stringify(config,null,2)+'\n');
 console.log('Split accounts and calculated results into two native matrices; only account groups have expanders.');
}
module.exports=polish;
if(require.main===module)polish();
