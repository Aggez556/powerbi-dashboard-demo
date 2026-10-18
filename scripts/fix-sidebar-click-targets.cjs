// A single full-size action button above decorative labels/icons owns each click target.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
function fix(report=path.resolve(__dirname,'../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report')){
 const read=f=>JSON.parse(fs.readFileSync(f,'utf8').replace(/^\uFEFF/,''));
 const pages=path.join(report,'definition/pages');let count=0;
 const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):v+'D'}}});
 for(const page of read(path.join(pages,'pages.json')).pageOrder){
  const dir=path.join(pages,page,'visuals');
  const originals=fs.readdirSync(dir).map(k=>path.join(dir,k,'visual.json')).filter(fs.existsSync).map(read)
   .filter(v=>v.visual.visualType==='actionButton'&&v.position.x===16&&v.position.width===240&&v.position.y>=150&&v.position.y<500&&v.position.z<500);
  for(const source of originals){
   const target=source.visual.visualContainerObjects?.visualLink?.[0]?.properties;
   if(target?.type?.expr?.Literal?.Value!=="'PageNavigation'"||!target.navigationSection)throw Error('Missing sidebar page target: '+source.name);
   const v=structuredClone(source);
   v.name=crypto.createHash('sha256').update('sidebar-click-target:'+page+':'+source.name).digest('hex').slice(0,20);
   v.position.z=1000;v.position.tabOrder=source.position.tabOrder;
   v.visual.objects={
    text:[{properties:{show:lit(false)}}],icon:[{properties:{show:lit(false)}}],
    fill:[{properties:{show:lit(true),transparency:lit(100)}},...['default','hover','selected','disabled'].map(id=>({selector:{id},properties:{transparency:lit(100)}}))],
    outline:[{properties:{show:lit(false)}}]
   };
   v.visual.visualContainerObjects.background=[{properties:{show:lit(false)}}];
   v.visual.visualContainerObjects.border=[{properties:{show:lit(false)}}];
   const out=path.join(dir,v.name);fs.mkdirSync(out,{recursive:true});
   fs.writeFileSync(path.join(out,'visual.json'),JSON.stringify(v,null,2)+'\n');count++;
  }
 }
 if(count!==25)throw Error('Expected 25 full sidebar click targets; found '+count);
 console.log('Added 25 full-size sidebar click targets above decorative labels and icons.');
}
module.exports=fix;if(require.main===module)fix();
