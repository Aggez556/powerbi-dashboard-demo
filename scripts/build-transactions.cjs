// Rebuild only Sales Analytics; preserve Desktop-authored pages and shared chrome.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),report=path.join(root,'powerbi-sales-finance/AubecoSalesFinance.Report');
const pageId='c29a05a83c27e1d92518',pageDir=path.join(report,'definition/pages',pageId),visualDir=path.join(pageDir,'visuals');
const id=s=>crypto.createHash('sha256').update(s).digest('hex').slice(0,20);
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?`${v}D`:`'${v.replace(/'/g,"''")}'`}}}),color=c=>({solid:{color:lit(c)}});
const col=(t,p,a)=>({Column:{Expression:{SourceRef:a?{Source:a}:{Entity:t}},Property:p}}),mea=(p,a)=>({Measure:{Expression:{SourceRef:a?{Source:a}:{Entity:'Försäljning'}},Property:p}});
let tab=100;const keep=new Set(['header-panel','logo','suite-title','side-panel','breadcrumbs','page-title',...Array.from({length:5},(_,i)=>'nav'+i)].map(key=>id(pageId+':'+key)));
function save(v){const dir=path.join(visualDir,v.name);fs.mkdirSync(dir,{recursive:true});fs.writeFileSync(path.join(dir,'visual.json'),JSON.stringify(v,null,2)+'\n');keep.add(v.name);return v;}
function visual(key,type,box,query={},objects={},title='',background='#FFFFFF'){
 const v={$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json',name:id(pageId+':'+key),position:{x:box[0],y:box[1],width:box[2],height:box[3],z:tab,tabOrder:tab++},visual:{visualType:type,objects,visualContainerObjects:{title:[{properties:{show:lit(!!title),text:lit(title),fontSize:lit(13),fontColor:color('#0F3163')}}],subTitle:[{properties:{show:lit(false)}}],background:[{properties:{show:lit(!!background),color:color(background||'#FFFFFF'),transparency:lit(0)}}],border:[{properties:{show:lit(!!background),color:color('#D5DDE7'),radius:lit(12)}}],padding:[{properties:{top:lit(0),bottom:lit(0),left:lit(0),right:lit(0)}}],visualHeader:[{properties:{show:lit(false)}}],general:[{properties:{altText:lit(title||key)}}]}}};
 if(Object.keys(query).length)v.visual.query={queryState:Object.fromEntries(Object.entries(query).map(([role,fields])=>[role,{projections:fields.map(field=>{const q=field.Column||field.Measure;return {field,queryRef:q.Expression.SourceRef.Entity+'.'+q.Property,nativeQueryRef:q.Property};})}]))};
 return save(v);
}
function text(key,label,box,size=12,ink='#0F3163',back=null,bold=false){return visual(key,'textbox',box,{}, {general:[{properties:{paragraphs:label.split('\n').map(line=>({textRuns:[{value:line,textStyle:{fontFamily:bold?'Segoe UI Semibold':'Segoe UI',fontSize:size+'pt',color:ink}}],horizontalTextAlignment:'left'}))}}]},'',back);}
function card(key,measure,box,size=28,fmt='@',ink='#0F3163'){
 return visual(key,'cardVisual',box,{Data:[mea(measure)]},{outline:[{selector:{id:'default'},properties:{show:lit(false)}}],fillCustom:[{selector:{id:'default'},properties:{show:lit(false)}}],cardCalloutArea:[{properties:{paddingUniform:lit(0),show:lit(false),backgroundTransparency:lit(100)}}],layout:[{properties:{paddingUniform:lit(0),backgroundShow:lit(false),backgroundTransparency:lit(100),cellPadding:lit(0)}}],padding:[{selector:{id:'default'},properties:{paddingSelection:lit('Custom'),leftMargin:lit(0),rightMargin:lit(0),topMargin:lit(0),bottomMargin:lit(0),paddingUniform:lit(0)}}],value:[{selector:{id:'default'},properties:{fontSize:lit(size),fontFamily:lit('Segoe UI'),bold:lit(false),fontColor:color(ink),horizontalAlignment:lit('left'),labelDisplayUnits:lit(1),customFormatString:lit(fmt),textWrap:lit(false),showBlankAs:lit('–')}}],label:[{selector:{id:'default'},properties:{show:lit(false)}}]},'',null);
}
function select(key,t,c,box,selected){const obj={data:[{properties:{mode:lit('Dropdown')}}],selection:[{properties:{strictSingleSelect:lit(true),singleSelect:lit(true),selectAllCheckboxEnabled:lit(false)}}],header:[{properties:{show:lit(false)}}],items:[{properties:{textSize:lit(9),fontColor:color('#0F3163')}}]};if(selected!==undefined)obj.general=[{properties:{filter:{filter:{Version:2,From:[{Name:'d',Entity:t,Type:0}],Where:[{Condition:{In:{Expressions:[col(t,c,'d')],Values:[[{Literal:{Value:"'"+selected+"'"}}]]}}}]}}}}];return visual(key,'slicer',box,{Values:[col(t,c)]},obj,'',null);}
const register=JSON.parse(fs.readFileSync(path.join(report,'definition/report.json'),'utf8'));
const pack=register.resourcePackages.find(p=>p.name==='RegisteredResources');
const iconPaths=[
 '<path d="M13 31l9-10 7 5 10-14M30 12h9v9"/>',
 '<path d="M13 18l13-7 13 7v16l-13 7-13-7zM13 18l13 8 13-8M26 26v15"/>',
 '<path d="M13 13v26M13 29l12-12M13 29l12 10M31 39V23M31 29c0-5 4-7 9-6"/>',
 '<path d="M15 38l22-24"/><circle cx="17" cy="17" r="5"/><circle cx="35" cy="35" r="5"/>',
 '<path d="M10 16h22v19H10zM32 23h7l5 7v5H32"/><circle cx="18" cy="36" r="4"/><circle cx="38" cy="36" r="4"/>'
];
iconPaths.forEach((drawing,i)=>{
 const name='TransactionKpi'+i+'.svg';
 fs.writeFileSync(path.join(report,'StaticResources/RegisteredResources',name),`<svg xmlns="http://www.w3.org/2000/svg" width="52" height="52" viewBox="0 0 52 52"><circle cx="26" cy="26" r="26" fill="#0F3163"/><g fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${drawing}</g></svg>`);
 if(!pack.items.some(x=>x.name===name))pack.items.push({name,path:name,type:'Image'});
});
fs.writeFileSync(path.join(report,'definition/report.json'),JSON.stringify(register,null,2)+'\n');
function image(key,file,box){return visual(key,'image',box,{}, {image:[{properties:{sourceType:lit('image'),sourceFile:{image:{name:lit(file),url:{expr:{ResourcePackageItem:{PackageName:'RegisteredResources',PackageType:1,ItemName:file}}},scaling:lit('Fit')}},fit:lit('Fit'),backgroundEnabled:lit(false),strokeShow:lit(false)}}]},'',null);}
require('./sales-finance-transactions.cjs')({preserveChrome:true,shell:()=>{},text,card,visual,image,select,mea,col,lit,color,save});
if(process.env.SALES_ANALYSIS_STAGE!=='header'){
 for(let i=0;i<5;i++)for(const key of ['yoy-label','yoy','sparkline']){
  const dir=path.join(visualDir,id(pageId+':'+key+i)),file=path.join(dir,'visual.json');
  if(fs.existsSync(file))fs.unlinkSync(file);
  if(fs.existsSync(dir)&&fs.readdirSync(dir).length===0)fs.rmdirSync(dir);
 }
}
if(!process.env.SALES_ANALYSIS_STAGE){
 for(const name of fs.readdirSync(visualDir)){
  if(!/^[0-9a-f]{20}$/.test(name)||keep.has(name))continue;
  const dir=path.join(visualDir,name),file=path.join(dir,'visual.json');
  if(!file.startsWith(pageDir+path.sep))throw Error('Unexpected cleanup path');
  if(fs.existsSync(file))fs.unlinkSync(file);
  if(fs.readdirSync(dir).length===0)fs.rmdirSync(dir);
 }
}
console.log(`Built Transactions only; ${keep.size} native visuals retained.`);

