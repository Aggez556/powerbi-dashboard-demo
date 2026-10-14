// Export the site's real rendered wordmark, preserving its own font and color.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {chromium}=require('../.tools/powerbi/node_modules/playwright');
const root=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:4});
  await page.goto('https://www.aubeco.se/',{waitUntil:'networkidle',timeout:60000});
  await page.evaluate(()=>document.fonts.ready);
  const original=await page.request.get('https://www.aubeco.se/aubeco-google-bild.png');
  if(!original.ok())throw Error('Could not fetch official organization logo.');
  fs.writeFileSync(path.join(root,'assets/aubeco/aubeco-original.png'),await original.body());
  const evidence=await page.locator('header nav a span').first().evaluate(el=>{
   const s=getComputedStyle(el);return {text:el.textContent.trim(),fontFamily:s.fontFamily,fontWeight:s.fontWeight,fontSize:s.fontSize,lineHeight:s.lineHeight,letterSpacing:s.letterSpacing,color:s.color};
  });
  if(evidence.text.toLowerCase()!=='aubeco')throw Error('Header wordmark changed; review required.');
  await page.evaluate(e=>{
   const node=document.createElement('span');node.id='aubeco-logo-export';node.textContent=e.text;
   Object.assign(node.style,{display:'inline-block',position:'absolute',left:'0',top:'0',width:'max-content',maxWidth:'none',flex:'none',fontFamily:e.fontFamily,fontWeight:e.fontWeight,fontSize:e.fontSize,lineHeight:e.lineHeight,letterSpacing:e.letterSpacing,color:e.color,whiteSpace:'nowrap',padding:'4px 6px'});
   document.body.replaceChildren(node);document.body.style.cssText='margin:0;padding:0;background:transparent';document.documentElement.style.background='transparent';
  },evidence);
  await page.evaluate(()=>document.fonts.ready);
  const file=path.join(root,'assets/aubeco/aubeco-header-wordmark.png');
  await page.locator('#aubeco-logo-export').screenshot({path:file,omitBackground:true});
  const metadata={retrievedDate:'2026-10-07',source:'https://www.aubeco.se/',kind:'Transparent export of the actual header wordmark using the website font; not a downloaded standalone header image',css:evidence,export:{fontSize:evidence.fontSize,lineHeight:evidence.lineHeight,letterSpacing:evidence.letterSpacing,scale:4,background:'transparent'},file:'assets/aubeco/aubeco-header-wordmark.png',sha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),officialLogoImageSource:'https://www.aubeco.se/aubeco-google-bild.png'};
  fs.writeFileSync(path.join(root,'assets/aubeco/sources/header-wordmark-export.json'),JSON.stringify(metadata,null,2)+'\n');
  console.log(JSON.stringify(metadata));
 }finally{await browser.close();}
})().catch(e=>{console.error(e.message);process.exitCode=1;});
