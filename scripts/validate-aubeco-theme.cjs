const fs = require('fs');
const crypto = require('crypto');
const Ajv = require('../.tools/powerbi/node_modules/ajv');
const addFormats = require('../.tools/powerbi/node_modules/ajv-formats');
const schemaPath = 'themes/schema/reportThemeSchema-2.157.json';
const themePath = 'themes/aubeco-powerbi.json';
const schemaBytes = fs.readFileSync(schemaPath);
const schema = JSON.parse(schemaBytes);
// Microsoft's published schema contains duplicate enum members. Removing
// repeated identical values preserves the accepted set and allows Draft-7
// meta-validation without changing any theme constraint. Keep original intact.
const normalizations = [];
function deduplicateEnums(value, location = '') {
  if (!value || typeof value !== 'object') return;
  if (Array.isArray(value.enum)) {
    const distinct = [...new Map(value.enum.map(item=>[JSON.stringify(item),item])).values()];
    if (distinct.length !== value.enum.length) {
      normalizations.push({path:location+'/enum',removed:value.enum.length-distinct.length});
      value.enum = distinct;
    }
  }
  for (const [key,item] of Object.entries(value)) deduplicateEnums(item, location+'/'+key);
}
deduplicateEnums(schema);
const theme = JSON.parse(fs.readFileSync(themePath,'utf8'));
const ajv = new Ajv({allErrors:true, strict:false, allowUnionTypes:true});
addFormats(ajv);
const validate = ajv.compile(schema);
const valid = validate(theme);
const luminance = hex => {
  const rgb = hex.replace('#','').match(/../g).map(v=>parseInt(v,16)/255).map(v=>v<=0.04045?v/12.92:((v+0.055)/1.055)**2.4);
  return rgb[0]*0.2126+rgb[1]*0.7152+rgb[2]*0.0722;
};
const contrast = (a,b) => {
  const [hi,lo] = [luminance(a),luminance(b)].sort((a,b)=>b-a);
  return Number(((hi+0.05)/(lo+0.05)).toFixed(2));
};
const pairs = [
 ['ink on white','#0B1B30','#FFFFFF',4.5],
 ['navy on sand-soft','#0F3163','#FDF6EC',4.5],
 ['muted on white','#5B6B80','#FFFFFF',4.5],
 ['muted on sand-soft','#5B6B80','#FDF6EC',4.5],
 ['brand orange on navy-deep','#F7BA6B','#09224A',4.5],
 ['brand orange on white','#F7BA6B','#FFFFFF',4.5],
 ['adapted orange on white','#9B570B','#FFFFFF',4.5],
 ...theme.dataColors.map((c,i)=>[`series ${i+1} on white`,c,'#FFFFFF',3]),
 ...[theme.good,theme.neutral,theme.bad].map(c=>[`status ${c} on white`,c,'#FFFFFF',4.5]),
];
const report = {
 date:'2026-10-06', theme:themePath, schema:schemaPath, schemaUrl:theme.$schema,
 schemaSha256:crypto.createHash('sha256').update(schemaBytes).digest('hex'),
 schemaDraft:schema.$schema || 'Draft-07 (Ajv default)', explorationVersion:schema.description,
 validator:`ajv ${require('../.tools/powerbi/node_modules/ajv/package.json').version}`,
 schemaNormalizations:normalizations,
 valid, errors:validate.errors||[],
 contrast:pairs.map(([name,foreground,background,threshold])=>({name,foreground,background,ratio:contrast(foreground,background),threshold,pass:contrast(foreground,background)>=threshold})),
 limitations:['Schema validation only; no Power BI Desktop import or rendered report test.','Brand orange on white is intentionally recorded as failing; use dark background or the adapted orange.'],
};
fs.writeFileSync('themes/validation-result.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
process.exitCode = valid ? 0 : 1;
