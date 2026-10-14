// Rasterize the existing SVG artwork for Power BI's custom button icons.
const {chromium}=require('../.tools/powerbi/node_modules/playwright');
const fs=require('fs'),path=require('path');
(async()=>{
 const root=path.resolve(__dirname,'..'),res=path.join(root,'powerbi-sales-finance/AubecoSalesFinance.Report/StaticResources/RegisteredResources');
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try{
  const page=await browser.newPage();
  for(let i=0;i<4;i++){
   const svg=fs.readFileSync(path.join(res,`HomeArea${i}.svg`),'utf8');
   const png=await page.evaluate(async svg=>{
    const image=new Image();image.src='data:image/svg+xml;base64,'+btoa(svg);await image.decode();
    const canvas=document.createElement('canvas');canvas.width=192;canvas.height=192;
    canvas.getContext('2d').drawImage(image,0,0,192,192);return canvas.toDataURL('image/png').split(',')[1];
   },svg);
   fs.writeFileSync(path.join(root,'assets/aubeco',`HomeArea${i}.png`),Buffer.from(png,'base64'));
  }
 }finally{await browser.close();}
 console.log('Exported four existing homepage icons as 192px PNGs.');
})().catch(e=>{console.error(e.message);process.exitCode=1;});
