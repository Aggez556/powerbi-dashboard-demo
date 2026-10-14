// Additive budget-planning demo; never regenerate or rewrite existing pages/theme.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),pbi=path.join(root,'powerbi'),report=path.join(pbi,'AubecoHandel.Report'),model=path.join(pbi,'AubecoHandel.SemanticModel/definition');
const reportOnly=process.argv.includes('--report-only');
const id=s=>crypto.createHash('sha256').update(s).digest('hex').slice(0,20),pageId=id('aubeco-budget-planning');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const write=(p,o)=>{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(o,null,2)+'\n');};
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
function files(dir){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?files(path.join(dir,e.name)):[path.join(dir,e.name)]);}
const oldFiles=files(path.join(report,'definition/pages')).filter(p=>!p.includes(pageId)&&!p.endsWith('pages.json')).concat(files(path.join(report,'StaticResources')),[path.join(report,'definition/report.json')]);
const oldHashes=Object.fromEntries(oldFiles.map(p=>[p,hash(p)]));
const rows=[['Intäkter',0],['\u00a0 Nettoomsättning',1],['\u00a0 Övriga rörelseintäkter',2],['Summa intäkter',3],[' ',0],['Kostnader',0],['\u00a0 Varu- och underkonsultkostnader',4],['\u00a0 Övriga externa kostnader',5],['\u00a0 Personalkostnader',6],['Summa kostnader',7],['  ',0],['Resultat före avskrivningar',8],['   ',0],['Avskrivningar',0],['\u00a0 Avskrivningar enligt plan',9],['Summa avskrivningar',9],['    ',0],['Rörelseresultat',10]];
const tableDefs=[
 ['Resultatrader',[['Rad','string'],['Ordning','int64'],['Beräkning','int64']],rows.map((r,i)=>[r[0],i+1,r[1]])],
 ['Budgetscenario',[['Scenario','string'],['Faktor','decimal']],[['BU 5',1.05],['BU 6',1.08]]],
 ['Budgetversion',[['Version','string'],['Ordning','int64']],[['Actuals',1],['Actuals PY',2],['Max YTD PY',3],['Budget',4]]],
 ['Budgetjustering',[['Procent','int64']],Array.from({length:26},(_,i)=>[i-10])],
 ['Budgetbelopp',[['Belopp','int64']],Array.from({length:81},(_,i)=>[i*250000])],
 ['Budgetfördelning',[['Fördelning','string']],[['Fördela över hela året'],['Följ säsongsvariation']]],
 ['Budgetkommentarer',[['Kommentar','string'],['Status','string']],[['Budget baserad på föregående år','Klar'],['Granska kostnadsantaganden','Pågår'],['Säsongsvariation är simulerad','Klar']]],
 ];
const q=s=>`'${s.replace(/'/g,"''")}'`;
for(const [name,columns,data] of tableDefs){
 const csv=[columns.map(x=>x[0]),...data].map(r=>r.map(v=>'"'+String(v).replace(/"/g,'""')+'"').join(',')).join('\r\n')+'\r\n';
 if(!reportOnly)fs.writeFileSync(path.join(pbi,'data',name+'.csv'),'\uFEFF'+csv);
 let t=`/// Fristående tabell för lokal budgetsimulering.\ntable ${name}\n`;
 for(const [c,type] of columns){t+=`\n\tcolumn ${q(c)}\n\t\tdataType: ${type}\n\t\tsourceColumn: ${c}\n\t\tsummarizeBy: none\n`;
  if(['Ordning','Beräkning','Faktor'].includes(c))t+='\t\tisHidden\n';
  if(c==='Rad'||c==='Version')t+="\t\tsortByColumn: 'Ordning'\n";
  if(c==='Belopp')t+='\t\tformatString: #,##0 " kr"\n';
 }
 t+=`\n\tpartition ${name} = m\n\t\tmode: import\n\t\tsource =\n\t\t\tlet\n\t\t\t\tSource = Csv.Document(File.Contents(DataFolder & "/${name}.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n\t\t\t\tHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n\t\t\t\tTyped = Table.TransformColumnTypes(Headers, {${columns.map(([c,type])=>`{"${c}", ${type==='int64'?'Int64.Type':type==='decimal'?'type number':'type text'}}`).join(', ')}}, "en-US")\n\t\t\tin\n\t\t\t\tTyped\n`;
 if(!reportOnly)fs.writeFileSync(path.join(model,'tables',name+'.tmdl'),t);
}
let m=fs.readFileSync(path.join(model,'model.tmdl'),'utf8');
for(const [name] of tableDefs)if(!m.includes('ref table '+name+'\n'))m+='\nref table '+name+'\n';
if(!reportOnly)fs.writeFileSync(path.join(model,'model.tmdl'),m);
const measures={
 'Planering bas':`VAR PY = [Omsättning föregående år]\nRETURN COALESCE(PY, [Omsättning])`,
 'Planering justerad':`[Planering bas] * (1 + DIVIDE(SELECTEDVALUE('Budgetjustering'[Procent], 3), 100))`,
 'Planerad omsättning':`VAR Bas = [Planering bas]\nVAR Helår = CALCULATE([Planering bas], ALLEXCEPT('Datum', 'Datum'[År]))\nVAR Månader = COUNTROWS(VALUES('Datum'[Månadsnummer]))\nVAR Jämnt = SELECTEDVALUE('Budgetfördelning'[Fördelning], "Fördela över hela året") = "Fördela över hela året"\nVAR Vikt = IF(Jämnt, DIVIDE(Månader, 12), DIVIDE(Bas, Helår))\nVAR Årsbelopp = SELECTEDVALUE('Budgetbelopp'[Belopp], 0)\nRETURN (IF(Jämnt, Helår * DIVIDE(Månader, 12), Bas) * SELECTEDVALUE('Budgetscenario'[Faktor], 1.05) * (1 + DIVIDE(SELECTEDVALUE('Budgetjustering'[Procent], 3), 100))) + Årsbelopp * Vikt`,
 'Resultat utfall':`VAR Kod = SELECTEDVALUE('Resultatrader'[Beräkning])\nVAR Version = SELECTEDVALUE('Budgetversion'[Version], "Actuals")\nVAR Intäkt = SWITCH(Version, "Actuals PY", [Omsättning föregående år], "Max YTD PY", CALCULATE([Omsättning föregående år], DATESYTD('Datum'[Datum])), "Budget", [Planerad omsättning], [Omsättning])\nVAR Varukostnad = SWITCH(Version, "Actuals PY", CALCULATE([Kostnad], SAMEPERIODLASTYEAR('Datum'[Datum])), "Max YTD PY", CALCULATE([Kostnad], SAMEPERIODLASTYEAR(DATESYTD('Datum'[Datum]))), "Budget", Intäkt * 0.73, [Kostnad])\nRETURN SWITCH(Kod, 0, 0, 1, Intäkt, 2, Intäkt * 0.04, 3, Intäkt * 1.04, 4, -Varukostnad, 5, -Intäkt * 0.08, 6, -Intäkt * 0.12, 7, -Varukostnad - Intäkt * 0.20, 8, Intäkt * 0.84 - Varukostnad, 9, -Intäkt * 0.03, 10, Intäkt * 0.81 - Varukostnad)`,
 'Resultat budget':`VAR Kod = SELECTEDVALUE('Resultatrader'[Beräkning])\nVAR Intäkt = [Planerad omsättning]\nRETURN SWITCH(Kod, 0, 0, 1, Intäkt, 2, Intäkt * 0.04, 3, Intäkt * 1.04, 4, -Intäkt * 0.73, 5, -Intäkt * 0.08, 6, -Intäkt * 0.12, 7, -Intäkt * 0.93, 8, Intäkt * 0.11, 9, -Intäkt * 0.03, 10, Intäkt * 0.08)`,
 'Resultatrad bakgrund':`VAR Rad = SELECTEDVALUE('Resultatrader'[Rad])\nRETURN IF(LEFT(Rad, 5) = "Summa" || Rad IN {"Resultat före avskrivningar", "Rörelseresultat"}, "#E1E8F2", "#FFFFFF")`,
};
let measureText='';
const variableNames={Helår:'AnnualBase',Månader:'MonthCount',Jämnt:'EvenSpread',Årsbelopp:'AnnualAmount',Intäkt:'RevenueValue',Version:'SelectedVersion'};
for(const name of Object.keys(measures))measures[name]=measures[name].replace(/('[^']*'|"(?:[^"]|"")*"|\[[^\]]+\])|(?<![\p{L}\p{N}_])(Helår|Månader|Jämnt|Årsbelopp|Intäkt|Version)(?![\p{L}\p{N}_])/gu,(match,protectedText,variable)=>protectedText||variableNames[variable]);
for(const [name,dax] of Object.entries(measures))measureText+=`\n\t/// Fiktiv budgetsimulering; inget skrivs tillbaka.\n\tmeasure ${q(name)} =\n${dax.split('\n').map(x=>'\t\t\t'+x).join('\n')}\n\t\tformatString: ${name==='Resultatrad bakgrund'?'@':'#,##0;-#,##0;" "'}\n\t\tdisplayFolder: Budgetplanering\n`;
const factPath=path.join(model,'tables/Försäljning.tmdl');let fact=fs.readFileSync(factPath,'utf8');
if(!fact.includes("measure 'Planering bas'"))fact=fact.replace(/(\n\t\/\/\/ Nettoomsättning)/,measureText+'$1');
else for(const [name,dax] of Object.entries(measures))fact=fact.replace(new RegExp('\\n\\tmeasure '+q(name)+' =\\r?\\n[\\s\\S]*?(?=\\n\\t\\tformatString:)'),`\n\tmeasure ${q(name)} =\n${dax.split('\n').map(x=>'\t\t\t'+x).join('\n')}`);
// A table's properties must precede its child measures in TMDL.
const tableLineage=fact.match(/\n\tlineageTag: [^\r\n]+/);
if(tableLineage){fact=fact.replace(tableLineage[0],'');fact=fact.replace(/(table Försäljning\r?\n)/,'$1'+tableLineage[0]+'\n');}
if(!reportOnly)fs.writeFileSync(factPath,fact);
// PBIR expression helpers, all visuals native.
const lit=v=>({expr:{Literal:{Value:typeof v==='boolean'?String(v):typeof v==='number'?`${v}D`:q(v)}}});
const color=c=>({solid:{color:lit(c)}});
const col=(t,p,source)=>({Column:{Expression:{SourceRef:source?{Source:source}:{Entity:t}},Property:p}});
const mea=p=>({Measure:{Expression:{SourceRef:{Entity:'Försäljning'}},Property:p}});
const proj=(f,display)=>{const e=f.Column||f.Measure;return {field:f,queryRef:`${e.Expression.SourceRef.Entity}.${e.Property}`,nativeQueryRef:display||e.Property};};
const pageDir=path.join(report,'definition/pages',pageId);let tab=0;const placements=[];
function visual(key,type,box,query={},objects={},background='#FFFFFF',title=''){
 const name=id(pageId+':'+key),v={$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json',name,position:{x:box[0],y:box[1],width:box[2],height:box[3],z:tab,tabOrder:tab++},visual:{visualType:type,objects,visualContainerObjects:{background:[{properties:{show:lit(true),color:color(background),transparency:lit(0)}}],border:[{properties:{show:lit(false)}}],padding:[{properties:{top:lit(8),bottom:lit(8),left:lit(10),right:lit(10)}}],title:[{properties:{show:lit(!!title),text:lit(title),fontFamily:lit('Segoe UI Semibold'),fontSize:lit(12),fontColor:color('#0F3163')}}],general:[{properties:{altText:lit(title||key)}}]}}};
 if(Object.keys(query).length)v.visual.query={queryState:Object.fromEntries(Object.entries(query).map(([role,fields])=>[role,{projections:fields.map(f=>proj(f))}]))};
 placements.push({key,type,box,fields:Object.values(query).flat()});save(v);return v;
}
function save(v){write(path.join(pageDir,'visuals',v.name,'visual.json'),v);}
function text(key,label,box,size=11,ink='#0B1B30',bg='#FFFFFF',bold=false){
 const v=visual(key,'textbox',box,{}, {general:[{properties:{paragraphs:label.split('\n').map(line=>({textRuns:[{value:line,textStyle:{fontFamily:bold?'Segoe UI Semibold':'Segoe UI',fontSize:size+'pt',color:ink}}],horizontalTextAlignment:key.includes('action')?'center':'left'}))}}]},bg);
 v.visual.visualContainerObjects.padding=[{properties:{top:lit(4),bottom:lit(4),left:lit(10),right:lit(10)}}];save(v);return v;
}
function slicer(key,t,c,box,label,mode='Dropdown',selected){
 const objects={data:[{properties:{mode:lit(mode)}}],header:[{properties:{show:lit(!!label),text:lit(label||''),fontColor:color('#0F3163')}}],selection:[{properties:{strictSingleSelect:lit(c!=='Månad'),singleSelect:lit(true),selectAllCheckboxEnabled:lit(false)}}]};
 if(selected!==undefined){const val=typeof selected==='number'?`${selected}L`:q(selected);objects.general=[{properties:{filter:{filter:{Version:2,From:[{Name:'d',Entity:t,Type:0}],Where:[{Condition:{In:{Expressions:[col(t,c,'d')],Values:[[{Literal:{Value:val}}]]}}}]}}}}];}
 if(mode==='Single'&&typeof selected==='number')objects.data[0].properties.numericStart=lit(selected);
 return visual(key,'slicer',box,{Values:[col(t,c)]},objects);
}
function card(key,measure,box){const v=visual(key,'cardVisual',box,{Data:[mea(measure)]},{value:[{selector:{id:'default'},properties:{fontSize:lit(11),fontColor:color('#0F3163'),fontFamily:lit('Segoe UI Semibold'),labelDisplayUnits:lit(1),labelPrecision:lit(0),customFormatString:lit('#,##0'),showBlankAs:lit('–')}}],label:[{selector:{id:'default'},properties:{show:lit(false)}}]},'#E1E8F2');v.visual.visualContainerObjects.padding=[{properties:{top:lit(0),bottom:lit(0),left:lit(0),right:lit(0)}}];v.visual.visualContainerObjects.spacing=[{selector:{id:'default'},properties:{customizeSpacing:lit(true),verticalSpacing:lit(-6)}}];save(v);return v;}
function tiles(key,t,c,box,columns,rowCount,selected,single=true){
 const objects={layout:[{properties:{orientation:lit(2),rowCount:lit(rowCount),columnCount:lit(columns),maxTiles:lit(columns*rowCount),autoGrid:lit(false),cellPadding:lit(4),style:lit('Cards')}}],selection:[{properties:{strictSingleSelect:lit(single),singleSelect:lit(single),selectAllCheckboxEnabled:lit(false)}}],value:[{selector:{id:'default'},properties:{show:lit(true),fontSize:lit(11),fontFamily:lit('Segoe UI'),fontColor:color('#0F3163'),horizontalAlignment:lit('center'),verticalAlignment:lit('middle'),textWrap:lit(false)}},{selector:{id:'selected'},properties:{fontColor:color('#FFFFFF'),bold:lit(true)}}],fillCustom:[{selector:{id:'default'},properties:{show:lit(true),fillColor:color('#FFFFFF'),transparency:lit(0)}},{selector:{id:'selected'},properties:{show:lit(true),fillColor:color('#0F3163'),transparency:lit(0)}}],outline:[{selector:{id:'default'},properties:{show:lit(true),lineColor:color('#D5DDE7'),weight:lit(1)}}],selectionIcon:[{selector:{id:'default'},properties:{show:lit(false)}}]};
 if(selected!==undefined){objects.general=[{properties:{filter:{filter:{Version:2,From:[{Name:'d',Entity:t,Type:0}],Where:[{Condition:{In:{Expressions:[col(t,c,'d')],Values:[[{Literal:{Value:typeof selected==='number'?`${selected}L`:q(selected)}}]]}}}]}}}}];}
 return visual(key,'advancedSlicerVisual',box,{Values:[col(t,c)]},objects);
}
write(path.join(pageDir,'page.json'),{$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json',name:pageId,displayName:'Budgetplanering',displayOption:'FitToPage',height:1080,width:1920,objects:{background:[{properties:{color:color('#FDF6EC'),transparency:lit(0)}}]}});
// Fixed geometry scaled from the supplied reference: sidebar, four top panels, P&L.
for(const [key,box] of [['panel-distribution',[324,24,240,308]],['panel-py',[580,24,248,308]],['panel-month',[844,24,308,308]],['panel-comments',[1168,24,704,308]]])text(key,'',box);
text('brand','AUBECO\n\nBudget-\nplanering',[28,28,272,300],24,'#0F3163','#FDF6EC',true);
text('distribution-title','Jämn fördelning',[324,24,240,44],12,'#0F3163','#FFFFFF',true);
slicer('distribution','Budgetfördelning','Fördelning',[324,72,240,56],'','Dropdown','Fördela över hela året');
slicer('amount','Budgetbelopp','Belopp',[324,138,240,104],'Fördela belopp','Dropdown',0);
text('distribution-action','×',[324,280,240,44],18,'#9B570B','#FDF6EC',true);
text('py-title','Förändring mot föregående år',[580,24,248,44],11,'#0F3163','#FFFFFF',true);
slicer('percent','Budgetjustering','Procent',[580,74,248,94],'Justering (%)','Single',3);
text('base-label','Bas',[580,180,120,36],10,'#0F3163','#E1E8F2',true);
text('adjusted-label','Justerad',[708,180,120,36],10,'#0F3163','#E1E8F2',true);
card('base','Planering bas',[580,216,120,56]);card('adjusted','Planering justerad',[708,216,120,56]);
text('py-action','✓',[580,280,248,44],18,'#0F3163','#FDF6EC',true);
text('month-title','Månadsuppdatering',[844,24,308,44],12,'#0F3163','#FFFFFF',true);
text('month-label','Uppdaterat belopp',[844,74,308,40],11,'#5B6B80');
const input=text('month-input','Ex. 70 000 kr',[854,118,288,104],12,'#5B6B80','#FFFFFF');input.visual.visualContainerObjects.border=[{properties:{show:lit(true),color:color('#D5DDE7'),radius:lit(0)}}];save(input);
text('month-demo','Exempel – välj månad till vänster',[844,228,308,44],10,'#5B6B80','#E1E8F2');
text('month-action','×',[844,280,308,44],18,'#9B570B','#FDF6EC',true);
text('comments-title','Kommentarer',[1168,24,364,44],12,'#0F3163','#FFFFFF',true);
const comments=visual('comments','tableEx',[1168,72,364,156],{Values:[col('Budgetkommentarer','Kommentar'),col('Budgetkommentarer','Status')]},{columnHeaders:[{properties:{autoSizeColumnWidth:lit(false),columnAdjustment:lit('fixedWidth'),fontSize:lit(10),backColor:color('#E1E8F2')}}],columnWidth:[{selector:{metadata:'Budgetkommentarer.Kommentar'},properties:{value:lit(255)}},{selector:{metadata:'Budgetkommentarer.Status'},properties:{value:lit(72)}}],values:[{properties:{fontSize:lit(10),wordWrap:lit(true),backColorPrimary:color('#FFFFFF'),backColorSecondary:color('#FFFFFF')}}],grid:[{properties:{rowPadding:lit(5)}}]});comments.visual.visualContainerObjects.stylePreset=[{properties:{name:lit('None')}}];save(comments);
slicer('status','Budgetkommentarer','Status',[1168,236,364,88],'Status','Dropdown');
text('new-comment-title','Ny kommentar',[1548,24,324,44],12,'#0F3163','#FFFFFF',true);
const commentInput=text('new-comment','Skriv kommentar här\n\n\n\nFörhandsvisning – sparas inte',[1558,72,304,196],11,'#5B6B80');commentInput.visual.visualContainerObjects.border=[{properties:{show:lit(true),color:color('#D5DDE7'),radius:lit(0)}}];save(commentInput);
text('comment-action','×',[1548,280,324,44],18,'#9B570B','#FDF6EC',true);
slicer('scenario','Budgetscenario','Scenario',[28,352,272,128],'Scenario','Dropdown','BU 5');
text('scenario-tools','▣                                      ⚒',[28,482,272,40],15,'#9B570B','#FFFFFF');
slicer('version','Budgetversion','Version',[28,538,272,224],'','VerticalList','Actuals');
tiles('year','Datum','År',[28,778,272,72],2,1,2025);
tiles('month','Datum','Månad',[28,866,272,166],3,4,undefined,false);
const matrix=visual('income-statement','pivotTable',[324,352,1548,680],{Rows:[col('Resultatrader','Rad')],Columns:[col('Datum','Månad')],Values:[mea('Resultat budget'),mea('Resultat utfall')]},{
 rowHeaders:[{properties:{fontFamily:lit('Segoe UI'),fontSize:lit(11),fontColor:color('#0B1B30'),wordWrap:lit(false),showExpandCollapseButtons:lit(false),stepped:lit(false),backColor:color('#FFFFFF')}}],
 columnHeaders:[{properties:{fontFamily:lit('Segoe UI Semibold'),fontSize:lit(10),fontColor:color('#0F3163'),backColor:color('#E1E8F2'),autoSizeColumnWidth:lit(false),columnAdjustment:lit('fixedWidth'),defaultColumnWidth:lit(112),customColumnWidth:lit(true),wordWrap:lit(false)}}],
 grid:[{properties:{rowPadding:lit(14),gridVertical:lit(false),gridHorizontal:lit(false),outlineWeight:lit(0)}}],
 values:[{properties:{fontFamily:lit('Segoe UI'),fontSize:lit(11),fontColorPrimary:color('#0B1B30'),fontColorSecondary:color('#0B1B30'),backColorPrimary:color('#FFFFFF'),backColorSecondary:color('#FFFFFF'),wordWrap:lit(false)}}],
 subTotals:[{properties:{rowSubtotals:lit(false),columnSubtotals:lit(false)}}],
 columnWidth:[{selector:{metadata:'Resultatrader.Rad'},properties:{value:lit(340)}},{selector:{metadata:'Försäljning.Resultat budget'},properties:{value:lit(112)}},{selector:{metadata:'Försäljning.Resultat utfall'},properties:{value:lit(112)}}],
},'#FFFFFF','Resultatrapport · månadsvis (SEK)');
matrix.visual.visualContainerObjects.stylePreset=[{properties:{name:lit('None')}}];
for(const measure of ['Resultat budget','Resultat utfall'])matrix.visual.objects.values.push({selector:{data:[{dataViewWildcard:{matchingOption:1}}],metadata:'Försäljning.'+measure},properties:{backColor:{solid:{color:{expr:mea('Resultatrad bakgrund')}}}}});
matrix.filterConfig={filters:[{name:id('budget-visible-rows'),field:col('Resultatrader','Ordning'),type:'Categorical',howCreated:'User',filter:{Version:2,From:[{Name:'r',Entity:'Resultatrader',Type:0}],Where:[{Condition:{In:{Expressions:[col('Resultatrader','Ordning','r')],Values:[1,2,3,4,6,7,8,9,10,12,14,15,16,18].map(n=>[{Literal:{Value:n+'L'}}])}}}]}}]};
matrix.visual.query.queryState.Values.projections[0].nativeQueryRef='Budget';
matrix.visual.query.queryState.Values.projections[1].nativeQueryRef='Actuals';
matrix.visual.query.sortDefinition={sort:[{field:col('Resultatrader','Rad'),direction:'Ascending'}],isDefaultSort:true};
save(matrix);
text('disclaimer','Lokal simulering · SEK · Budget och omkostnader är fiktiva · Inga ändringar sparas',[324,1040,1548,28],10,'#5B6B80','#FDF6EC');
const pagesPath=path.join(report,'definition/pages/pages.json'),pages=read(pagesPath);if(!pages.pageOrder.includes(pageId))pages.pageOrder.push(pageId);pages.activePageName=pageId;write(pagesPath,pages);
for(const [file,digest] of Object.entries(oldHashes))if(hash(file)!==digest)throw Error('Existing page or theme changed: '+file);
write(path.join(pbi,'validation/budget-page.json'),{status:'files-created',pageId,displayName:'Budgetplanering',nativeVisuals:placements.length,placements,existingPagesAndThemeUnchanged:true,source:'User-supplied screenshot; geometry adapted to 1920x1080',limitations:['No writeback, comment entry or save/reset actions.','Budget and operating expenses are simulated; original sales data unchanged.','DAX and rendering require Desktop refresh.']});
console.log(`Added Budgetplanering: ${placements.length} visuals, ${tableDefs.length} disconnected Import tables; previous pages and theme unchanged.`);
if(fs.existsSync(path.join(root,'assets/aubeco/aubeco-header-wordmark.png')))require('./apply-aubeco-logo.cjs');
