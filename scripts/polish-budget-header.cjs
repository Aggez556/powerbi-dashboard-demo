const fs=require('fs'),path=require('path'),crypto=require('crypto');
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?`${v}D`:`'${v}'`}}});
function polish(reportPath){
 const report=reportPath||path.resolve(__dirname,'../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report');
 const pages=path.join(report,'definition/pages'),page='cbe967640ff6843fb323';
 const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
 const file=key=>path.join(pages,page,'visuals',crypto.createHash('sha256').update('budget-scenarios:'+page+':'+key).digest('hex').slice(0,20),'visual.json');
 const update=(key,fn)=>{const p=file(key),v=read(p);fn(v);fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');};
 const customer=path.join(pages,'f429b020315c602ce0ed','visuals');
 const title=read(path.join(customer,'2959a3126b1062dede29','visual.json'));
 const period=read(path.join(customer,'f20bbd6190796433338e','visual.json'));
 const year=read(path.join(customer,'9862681395862b77aaf7','visual.json'));
 update('title',v=>{Object.assign(v.position,{x:304,y:24,width:464,height:64});v.visual.objects.general[0].properties.paragraphs[0].textRuns[0].textStyle=title.visual.objects.general[0].properties.paragraphs[0].textRuns[0].textStyle;});
 update('subtitle',v=>{Object.assign(v.position,{x:304,y:88,width:464,height:32});const style=v.visual.objects.general[0].properties.paragraphs[0].textRuns[0].textStyle;Object.assign(style,{fontFamily:'Segoe UI',fontSize:'13pt',color:'#5B6B80'});});
 update('year',v=>{Object.assign(v.position,{x:1640,y:16,width:248,height:88});for(const name of ['items','header','data'])if(year.visual.objects[name])v.visual.objects[name]=structuredClone(year.visual.objects[name]);v.visual.objects.header[0].properties.text=lit('År');v.visual.visualContainerObjects.background=[{properties:{show:lit(false)}}];v.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];});
 update('kpi-prefix',v=>{Object.assign(v.position,{x:784,y:112,width:1104,height:32});v.visual.objects=structuredClone(period.visual.objects);v.visual.visualContainerObjects.background=[{properties:{show:lit(false)}}];v.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];});
 console.log('Matched Budget header to the established report header.');
}
module.exports=polish;
if(require.main===module)polish();
