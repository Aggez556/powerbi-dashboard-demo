const fs=require('fs'),path=require('path');
const base=path.resolve(__dirname,'../powerbi-sales-finance/AubecoSalesFinance.Report/definition/pages/c29a05a83c27e1d92518'),file=path.join(base,'page.json'),backup=path.resolve(__dirname,'../.tools/transactions-page-backup.json');
const mode=process.argv[2];
if(mode==='Restore'){fs.copyFileSync(backup,file);process.exit();}
if(!fs.existsSync(backup))fs.copyFileSync(file,backup);
const p=JSON.parse(fs.readFileSync(backup,'utf8'));
const fields=mode==='October'?[['Datum','Månadsnummer',[10]]]:mode==='Multi'?[['Datum','Månadsnummer',[1,2,3]]]:mode==='Market'?[['Datum','Månadsnummer',[10]],['Kunder','Land',['Norge']]]:mode==='Empty'?[['Produkter','Produkt',['Finns inte']]]:[];
p.filterConfig={filters:fields.map(([table,column,values],i)=>({name:'tx-review-'+i,field:{Column:{Expression:{SourceRef:{Entity:table}},Property:column}},type:'Categorical',howCreated:'User',filter:{Version:2,From:[{Name:'t',Entity:table,Type:0}],Where:[{Condition:{In:{Expressions:[{Column:{Expression:{SourceRef:{Source:'t'}},Property:column}}],Values:values.map(v=>[{Literal:{Value:typeof v==='number'?v+'L':"'"+v+"'"}}])}}}]}}))};
fs.writeFileSync(file,JSON.stringify(p,null,2)+'\n');
