const fs=require('fs'),base='powerbi-ledningsrapport/validation/';
const x=JSON.parse(fs.readFileSync(base+'assignment-measure-result.json','utf8').replace(/^\uFEFF/,''));
let expression=x.resultSets[0][0]['[Expression]'];
for(const [name,value] of Object.entries({'Uppdrag hela timmar':'0','Uppdrag planerade':'1','Uppdrag prognos':'.28','Uppdrag kalkyl':'.30'}))expression=expression.replaceAll('['+name+']',value);
fs.writeFileSync(base+'assignment-risk-boundary.dax',`DEFINE MEASURE 'Planinställning'[Risk boundary] = ${expression}
EVALUATE UNION(
CALCULATETABLE(ROW("Case","Ongoing","Risk",[Risk boundary]),TREATAS({"Pågående"},'Uppdragsregister'[Status])),
CALCULATETABLE(ROW("Case","Completed","Risk",[Risk boundary]),TREATAS({"Avslutat"},'Uppdragsregister'[Status])))
ORDER BY [Case]`);
