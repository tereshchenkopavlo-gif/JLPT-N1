const {chromium}=require('playwright'),fs=require('node:fs'),assert=require('node:assert/strict'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const html=fs.readFileSync('release138/JLPT_N1_ukrainian_reading_v138.html','utf8');
(async()=>{const browser=await chromium.launch({headless:true}),results=[];try{
for(const width of [360,412,1280])for(const [scheme,scale,forced] of [['light',1,false],['light',1.25,false],['dark',1,false],['dark',1,true]]){
 const page=await browser.newPage({viewport:{width,height:920},colorScheme:scheme}),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(pathToFileURL(path.resolve('release138/JLPT_N1_ukrainian_reading_v138.html')).href);
 await page.evaluate(({scale,forced})=>{document.documentElement.style.setProperty('--fs',String(scale));if(forced)document.documentElement.dataset.theme='light';saveComparisonKeys(['v_58','v_75','g_1','g_2']);renderComparison();showView('compare')},{scale,forced});
 const stats=await page.evaluate(()=>{
  const style=el=>{const s=getComputedStyle(el);return {color:s.color,size:parseFloat(s.fontSize),weight:s.fontWeight}};
  return {body:[...document.querySelectorAll('#compareList .compare-ua .study-paragraph,#compareList .compare-jp,#compareList .grammar-example-ua,#compareGuides .study-paragraph,#compareGuides .study-example-translation')].map(style),emphasis:[...document.querySelectorAll('#compareList h3,#compareList b,#compareGuides strong')].map(style),headings:[...document.querySelectorAll('#compareList .compare-jp b')].map(x=>x.textContent),overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth};
 });
 const color=scheme==='dark'&&!forced?'rgb(255, 255, 255)':'rgb(0, 0, 0)';assert(stats.body.length>20);
 for(const x of stats.body){assert.equal(x.color,color);assert.equal(x.weight,'400');assert.equal(x.size,16*scale)}
 for(const x of stats.emphasis){assert.equal(x.color,color);assert(Number(x.weight)>=600)}
 assert(stats.headings.includes('類似・関連表現：'));assert(stats.headings.includes('例文：'));assert(stats.overflow<=2);assert.deepEqual(errors,[]);
 if(width===412&&scheme==='light'&&scale===1){await page.locator('.compare-entry').first().screenshot({path:'/tmp/v138-comparison.png'});}
 await page.reload();await page.locator('.nav-tab[data-view="compare"]').click();assert.equal(await page.locator('.compare-entry').count(),4);
 await page.locator('.remove-compare').first().click();assert.equal(await page.locator('.compare-entry').count(),3);
 results.push({width,scheme,scale,forcedLight:forced,bodyChecks:stats.body.length,blackOrWhiteNeutralText:true,normalBodyWeight:true,equalBodySizes:true,meaningfulEmphasis:true,persistence:true,pass:true});await page.close();
}
fs.writeFileSync('audit138/browser-results.json',JSON.stringify({sha256:require('node:crypto').createHash('sha256').update(html).digest('hex'),browser:browser.version(),results},null,2));console.log('PASS comparison typography, scaling, light/dark themes, persistence:',results.length,'scenarios');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
