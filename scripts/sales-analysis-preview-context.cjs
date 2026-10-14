// Explicit preview context when Desktop click automation cannot confirm a choice.
const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..');
const file=path.join(root,'powerbi-sales-finance/AubecoSalesFinance.Report/definition/pages/64292d897630eb848ace/visuals/5436c533f8c1f426d247/visual.json');
const backup=path.join(root,'.tools/sales-analysis-month-backup.json');
const choice=process.argv[2];
if(choice==='restore'){if(!fs.existsSync(backup))throw Error('No saved month definition');fs.copyFileSync(backup,file);process.exit(0);}
if(!fs.existsSync(backup))fs.copyFileSync(file,backup);
const v=JSON.parse(fs.readFileSync(backup,'utf8').replace(/^\uFEFF/,''));
const names=choice==='q1'?['januari','februari','mars']:choice==='october'?['oktober']:choice==='september-october'?['september','oktober']:choice==='empty'?['okänd']:null;
if(!names)throw Error('Unsupported preview context');
v.visual.objects.general=[{properties:{filter:{filter:{Version:2,From:[{Name:'d',Entity:'Datum',Type:0}],Where:[{Condition:{In:{Expressions:[{Column:{Expression:{SourceRef:{Source:'d'}},Property:'Månad'}}],Values:names.map(name=>[{Literal:{Value:"'"+name+"'"}}])}}}]}}}}];
fs.writeFileSync(file,JSON.stringify(v,null,2)+'\n');
