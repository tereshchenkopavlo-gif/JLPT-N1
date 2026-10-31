const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const file='release134/JLPT_N1_ukrainian_reading_v134.html';
const html=fs.readFileSync(file,'utf8'),changes=JSON.parse(fs.readFileSync('audit134/changes.json','utf8'));
const pairs=[[659,'2980','2981'],[738,'3224','3250'],[853,'3898','3900'],[857,'3909','3912']];
(async()=>{
 const browser=await chromium.launch({headless:true}),results=[];
 try{
  for(const width of [360,412,1280]){
   const page=await browser.newPage({viewport:{width,height:900}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(pathToFileURL(path.resolve(file)).href);
   for(const [index,a,b] of pairs){
    for(const id of [a,b]){
     await page.locator('.nav-tab[data-view="cards"]').click();
     await page.evaluate(id=>openCardDetail('v',id),id);
     const note=page.locator(`#cardDetailBody .lexical-pair[data-pair="${a}_${b}"] .nuance-line`);
     assert.equal(await note.innerText(),changes.pairs[String(index)]);
     assert.equal(await note.count(),1,'single reviewed note, not duplicated');
     if(changes.usage[id])assert.equal(await page.locator('#cardDetailBody .fc-trans').nth(1).innerText(),changes.usage[id]);
     if(id==='2980'||id==='2981'){
      const oppositeGroups=page.locator('#cardDetailBody .auto-relations-group').filter({has:page.locator('.auto-relations-label',{hasText:/^対義語$/})});
      if(await oppositeGroups.count())assert(!(await oppositeGroups.innerText()).includes(id==='2980'?'情け深い':'情けない'));
     }
     await page.locator('#cardDetailBody .compare-add').click();
     const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);assert(overflow<=2);
     results.push({width,index,id,card:true,usageChecked:!!changes.usage[id]});
     if(width===412&&id==='2980')await page.screenshot({path:'/tmp/v134-nasakenai.png',fullPage:true});
    }
   }
   await page.locator('.nav-tab[data-view="compare"]').click();
   assert.equal(await page.locator('.compare-entry').count(),8);
   const texts=await page.locator('.lexical-guide p').allTextContents();
   for(const [index] of pairs)assert.equal(texts.filter(t=>t===changes.pairs[String(index)]).length,1,'same note in comparison '+index);
   assert.equal(await page.evaluate(()=>getComparisonKeys().length),8);
   await page.reload();await page.locator('.nav-tab[data-view="compare"]').click();assert.equal(await page.locator('.compare-entry').count(),8);
   assert.deepEqual(errors,[]);
   results.push({width,comparison:true,reload:true,notes:4});await page.close();
  }
  fs.writeFileSync('audit134/pair-results.json',JSON.stringify({sha256:require('node:crypto').createHash('sha256').update(html).digest('hex'),browser:browser.version(),results},null,2));
  console.log('PASS v134 four notes in both card directions and comparison, usage, polarity and reload at three widths');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
