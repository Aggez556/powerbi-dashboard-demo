const { chromium } = require('../.tools/powerbi/node_modules/playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const browser = await chromium.launch({channel:'msedge', headless:true});
  const page = await browser.newPage({viewport:{width:1440,height:1000}, deviceScaleFactor:1});
  await page.goto('https://www.aubeco.se/', {waitUntil:'networkidle', timeout:60000});
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({path:'assets/aubeco/sources/home-desktop-viewport.png'});
  await page.screenshot({path:'assets/aubeco/sources/home-desktop.png', fullPage:true});
  const evidence = await page.evaluate(() => {
    const selectors = {logo:'header nav a span',heroTitle:'h1',heroBody:'#top p',heroButton:'#top a',sectionTitle:'main section:nth-child(2) h2',body:'body',section:'main section:nth-child(2)',serviceCard:'#tjanster a',footer:'footer'};
    const result = {viewport:{width:innerWidth,height:innerHeight},rootFontSize:getComputedStyle(document.documentElement).fontSize, elements:{}, fonts:[...document.fonts].map(f=>({family:f.family,weight:f.weight,status:f.status}))};
    for(const [key,selector] of Object.entries(selectors)) {
      const el=document.querySelector(selector);
      if(!el) continue;
      const style=getComputedStyle(el),rect=el.getBoundingClientRect();
      result.elements[key]={selector,text:el.textContent.trim().slice(0,100),classes:el.className,rect:{x:rect.x,y:rect.y,width:rect.width,height:rect.height}};
      for(const prop of ['fontFamily','fontSize','fontWeight','lineHeight','letterSpacing','color','backgroundColor','borderRadius','paddingTop','paddingRight','paddingBottom','paddingLeft','gap','boxShadow']) result.elements[key][prop]=style[prop];
    }
    return result;
  });
  fs.writeFileSync('assets/aubeco/sources/computed-desktop.json',JSON.stringify(evidence,null,2));
  await page.locator('header nav a span').screenshot({path:'assets/aubeco/sources/web-wordmark-reference.png'});
  const imageEvidence = await page.evaluate(async()=>{
    const img=new Image(); img.src='/aubeco-google-bild.png'; await img.decode();
    const canvas=document.createElement('canvas');canvas.width=img.width;canvas.height=img.height;
    const ctx=canvas.getContext('2d');ctx.drawImage(img,0,0);
    const data=ctx.getImageData(0,0,img.width,img.height).data,counts=new Map();
    for(let i=0;i<data.length;i+=4){const hex='#'+[data[i],data[i+1],data[i+2]].map(v=>v.toString(16).padStart(2,'0')).join('');counts.set(hex,(counts.get(hex)||0)+1);}
    return {width:img.width,height:img.height,dominantPixelColors:[...counts.entries()].sort((a,b)=>b[1]-a[1]).slice(0,5)};
  });
  fs.writeFileSync('assets/aubeco/sources/logo-image-evidence.json',JSON.stringify(imageEvidence,null,2));
  await page.setViewportSize({width:390,height:844});
  await page.waitForTimeout(350);
  const mobile = await page.evaluate(()=>{
    const result={viewport:{width:innerWidth,height:innerHeight},rootFontSize:getComputedStyle(document.documentElement).fontSize,elements:{}};
    for(const selector of ['h1','#top p','#tjanster a']){const el=document.querySelector(selector),s=getComputedStyle(el);result.elements[selector]={fontSize:s.fontSize,fontWeight:s.fontWeight,lineHeight:s.lineHeight,borderRadius:s.borderRadius,padding:s.padding};}
    return result;
  });
  fs.writeFileSync('assets/aubeco/sources/computed-mobile.json',JSON.stringify(mobile,null,2));
  await page.screenshot({path:'assets/aubeco/sources/home-mobile.png',fullPage:true});
  await browser.close();
  console.log(JSON.stringify(evidence.elements,null,2));
})().catch(error=>{console.error(error);process.exitCode=1;});
