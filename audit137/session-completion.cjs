// End-to-end completion of one actual learning session, including persistence.
const {chromium}=require('playwright');
const {pathToFileURL}=require('node:url');
const path=require('node:path');
const assert=require('node:assert/strict');
const url=pathToFileURL(path.resolve('release137/JLPT_N1_ukrainian_reading_v137.html')).href;
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:412,height:915}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(url);
  await page.locator('#btnStartSession').click();
  await page.waitForFunction(()=>['teachBody','sessBody','sessError'].some(id=>document.getElementById(id).getClientRects().length>0));
  if(await page.locator('#teachBody').isVisible())await page.locator('#btnSkipTeach').click();
  let pages=0,answers=0,graded=0;
  for(;pages<40;pages++){
   await page.waitForFunction(()=>['sessBody','sessDone','sessError','teachBody'].some(id=>document.getElementById(id).getClientRects().length>0));
   if(await page.locator('#sessDone').isVisible())break;
   if(await page.locator('#sessError').isVisible())throw Error('session entered error state');
   if(await page.locator('#teachBody').isVisible()){await page.locator('#btnSkipTeach').click();continue;}
   const qs=page.locator('#passageArea .qcard');
   for(let i=0,n=await qs.count();i<n;i++){
    await qs.nth(i).locator('.qchoice').first().click();
    assert.equal(await qs.nth(i).locator('.qexplain').isVisible(),true,'explanation shown');
    answers++;
   }
   const rows=page.locator('#passageArea .raterow');
   for(let i=0,n=await rows.count();i<n;i++){
    await rows.nth(i).locator('.ratebtn[data-g="S"]').click();graded++;
   }
   assert.equal(await page.locator('#btnPassageNext').isEnabled(),true,'next enabled');
   await page.locator('#btnPassageNext').click();
  }
  assert.ok(await page.locator('#sessDone').isVisible(),'session finishes within 40 passages');
  const summary=await page.locator('#sessSummary').innerText();
  assert.ok(summary.length>5,'completion summary present');
  await page.locator('#btnSessFinish').click();
  assert.equal(await page.locator('#view-home').isVisible(),true,'return home after completion');
  const saved=await page.evaluate(()=>localStorage.getItem('choba_n1uk_storage_v1'));
  assert.ok(saved&&saved.length>20,'session data stored');
  await page.reload();
  assert.ok(await page.evaluate(()=>localStorage.getItem('choba_n1uk_storage_v1')),'session progress persists after reload');
  assert.deepEqual(errors,[],'no uncaught browser errors');
  console.log('PASS v137 complete learning session '+JSON.stringify({pages,answers,graded,summary:summary.slice(0,150),storedBytes:saved.length}));
  const fs=require('node:fs');
  const sha256=require('node:crypto').createHash('sha256').update(fs.readFileSync(path.resolve('release137/JLPT_N1_ukrainian_reading_v137.html'))).digest('hex');
  fs.writeFileSync('audit137/session-results.json',JSON.stringify({sha256,browser:browser.version(),pass:true,pages,answers,graded,summary,storedBytes:saved.length},null,2));
  await page.close();
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
