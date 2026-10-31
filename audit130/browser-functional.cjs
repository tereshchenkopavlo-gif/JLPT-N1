// Actual navigation and persistence smoke, separate from static HTML inspection.
const { chromium }=require('playwright');
const { pathToFileURL }=require('node:url');
const path=require('node:path');
const assert=require('node:assert/strict');
const fs=require('node:fs/promises');
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
  if(name!=='session') assert.equal(await view.isVisible(),true,'visible view '+name);
  // Session contains sub-states that can be hidden until the user begins an exercise.
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
 const exportBytes=await fs.readFile(await download.path(),'utf8');
 const backup=JSON.parse(exportBytes);
 assert.ok(backup && typeof backup==='object' && !Array.isArray(backup),'export contains a JSON object');
 assert.ok(exportBytes.length>20,'export contains usable payload');
 assert.ok(Object.keys(backup).length>0,'export JSON has top-level fields');
 assert.ok(backup.meta && typeof backup.meta==='object','export metadata present');
 assert.ok(backup.vp && typeof backup.vp==='object','vocabulary progress is an object');
 assert.ok(backup.gp && typeof backup.gp==='object','grammar progress is an object');
 assert.ok(Number.isInteger(backup.backupVersion),'export has integer backup version');
 assert.ok(Array.isArray(backup.comparisonKeys),'comparison list is an array');
 console.log('PASS v130 export JSON',JSON.stringify({width,bytes:exportBytes.length,keys:Object.keys(backup).slice(0,15)}));
 console.log('PASS v130 progress export',JSON.stringify({width,filename:download.suggestedFilename()}));
 // Synthetic but nonempty learning progress, using the app's own exported schema.
 // This tests whether the import accepts and retains meaningful records; it does not fabricate user progress.
 const seeded=structuredClone(backup);
 seeded.vp['1']={s:3,n:2,last:20261031};
 seeded.gp['1']={s:2,n:1,last:20261031};
 seeded.comparisonKeys=[]; // separate regression needed for UI-produced comparison keys
 const seededBytes=JSON.stringify(seeded);
 // Import the exported backup through the real file input, if one is provided by the app.
 const fileInputs=page.locator('input[type="file"]');
 assert.ok(await fileInputs.count()>=1,'progress import input exists');
 const importInput=page.locator('input[type="file"][accept*="json"]').first();
 const uploadInput=(await importInput.count())?importInput:fileInputs.first();
 const dialogs=[];page.on('dialog',async d=>{dialogs.push(d.message());await d.accept()});
 await uploadInput.setInputFiles({name:download.suggestedFilename(),mimeType:'application/json',buffer:Buffer.from(seededBytes,'utf8')});
 await page.waitForTimeout(300);
 assert.equal(errors.length,0,'import does not throw JavaScript errors');
 console.log('PASS v130 progress import attempt',JSON.stringify({width,dialogs:dialogs.length,inputId:await uploadInput.getAttribute('id')}));
 // A successful import should preserve the same exported data when exported again.
 await page.locator('.nav-tab[data-view="settings"]').click();
 const [roundtrip]=await Promise.all([
   page.waitForEvent('download',{timeout:10000}),
   page.locator('#btnExportProgress').click()
 ]);
 const second=JSON.parse(await fs.readFile(await roundtrip.path(),'utf8'));
 assert.deepEqual(second.vp,seeded.vp,'vocabulary progress survives import/export');
 assert.ok(Object.keys(second.vp).length>0,'nonempty vocabulary progress restored');
 assert.deepEqual(second.gp,seeded.gp,'grammar progress survives import/export');
 assert.ok(Object.keys(second.gp).length>0,'nonempty grammar progress restored');
 assert.deepEqual(second.comparisonKeys,seeded.comparisonKeys,'comparison list survives import/export');
 console.log('PASS v130 progress export/import roundtrip',JSON.stringify({width,vocab:Object.keys(second.vp).length,grammar:Object.keys(second.gp).length}));


 // Reload should keep the session functional and app accessible, irrespective of which keys exist.
 await page.reload({waitUntil:'load'});
 assert.equal(await page.locator('.nav-tab').count(),5,'all tabs survive reload');
 assert.equal(await page.locator('#btnStartSession').count(),1,'session action survives reload');
 const [reloadedExport]=await Promise.all([
   page.waitForEvent('download',{timeout:10000}),
   page.locator('.nav-tab[data-view="settings"]').click().then(()=>page.locator('#btnExportProgress').click())
 ]);
 const afterReload=JSON.parse(await fs.readFile(await reloadedExport.path(),'utf8'));
 assert.deepEqual(afterReload.vp,seeded.vp,'vocab backup remains intact after reload');
 assert.deepEqual(afterReload.gp,seeded.gp,'grammar backup remains intact after reload');
 assert.deepEqual(afterReload.comparisonKeys,seeded.comparisonKeys,'comparison list remains intact after reload');
 console.log('PASS v130 progress after reload',JSON.stringify({width,vocabCount:Object.keys(afterReload.vp).length,grammarCount:Object.keys(afterReload.gp).length,compareCount:afterReload.comparisonKeys.length}));
 const savedKeys=await page.evaluate(()=>Object.keys(localStorage));
 assert.ok(savedKeys.includes('choba_n1uk_storage_v1'),'imported progress storage survives reload');
 assert.ok(savedKeys.includes('jlptN1CompareListUA_v1'),'imported comparison storage survives reload');
 if(errors.length)throw new Error('runtime errors: '+errors.join(' | '));
 console.log('PASS v130 functional navigation',JSON.stringify({width,viewsChecked:6,progressKeys:savedKeys.length,errors:0}));
 await page.close();
}
}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
