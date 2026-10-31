// Actual navigation and persistence smoke, separate from static HTML inspection.
const { chromium }=require('playwright');
const { pathToFileURL }=require('node:url');
const path=require('node:path');
const assert=require('node:assert/strict');
const url=pathToFileURL(path.resolve('release130/JLPT_N1_ukrainian_reading_v130.html')).href;
(async()=>{
const browser=await chromium.launch({headless:true});
try{
for(const width of [360,412,1280]){
 const page=await browser.newPage({viewport:{width,height:900},acceptDownloads:true});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(url,{waitUntil:'load'});
 for(const name of ['home','cards','compare','settings','session','home']){
  const tab=page.locator('.nav-tab[data-view="'+name+'"]');
  await tab.click();
  assert.equal(await tab.evaluate(el=>el.classList.contains('active')),true,'active tab '+name);
  const view=page.locator('#view-'+name);
  assert.equal(await view.evaluate(el=>el.classList.contains('active')),true,'active view '+name);
  assert.equal(await view.isVisible(),true,'visible view '+name);
 }
 await page.locator('.nav-tab[data-view="cards"]').click();
 const cards=page.locator('#view-cards button');
 assert.ok(await cards.count()>3,'cards controls present');
 await page.locator('.nav-tab[data-view="settings"]').click();
 assert.equal(await page.locator('#btnExportProgress').isVisible(),true,'export available');
 const progressKeys=await page.evaluate(()=>Object.keys(localStorage));
 // The export button must produce an actual file, not merely be visible.
 const [download]=await Promise.all([
   page.waitForEvent('download',{timeout:10000}),
   page.locator('#btnExportProgress').click()
 ]);
 assert.ok(download.suggestedFilename().length>3,'export file has a name');
 const failure=await download.failure();
 assert.equal(failure,null,'export downloaded without error');
 console.log('PASS v130 progress export',JSON.stringify({width,filename:download.suggestedFilename()}));
 // Reload should keep the session functional and app accessible, irrespective of which keys exist.
 await page.reload({waitUntil:'load'});
 assert.equal(await page.locator('.nav-tab').count(),5,'all tabs survive reload');
 assert.equal(await page.locator('#btnStartSession').count(),1,'session action survives reload');
 assert.deepEqual(await page.evaluate(()=>Object.keys(localStorage)),progressKeys,'reload does not discard saved keys');
 if(errors.length)throw new Error('runtime errors: '+errors.join(' | '));
 console.log('PASS v130 functional navigation',JSON.stringify({width,viewsChecked:6,progressKeys:progressKeys.length,errors:0}));
 await page.close();
}
}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
