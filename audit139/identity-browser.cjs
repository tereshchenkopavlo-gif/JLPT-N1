const {chromium}=require('playwright'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
(async()=>{const browser=await chromium.launch({headless:true});try{
 const page=await browser.newPage({viewport:{width:412,height:915},acceptDownloads:true}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.resolve('JLPT_N1_ukrainian_reading_v138.html')).href);
 await page.evaluate(()=>{state.vp['716']={status:'S',timesShown:4,lastSeen:1793426400000,firstSeen:1793340000000};saveStorage();saveComparisonKeys(['v_716','v_782']);showView('settings')});
 const [download]=await Promise.all([page.waitForEvent('download'),page.locator('#btnExportProgress').click()]);
 const backup=fs.readFileSync(await download.path());const old=JSON.parse(backup);assert(old.vp['716']);assert(old.comparisonKeys.includes('v_716'));
 // A different file:// can have independent storage: use the supported backup handoff.
 await page.goto(pathToFileURL(path.resolve('release139/JLPT_N1_ukrainian_reading_v139.html')).href);
 await page.locator('.nav-tab[data-view="settings"]').click();page.on('dialog',d=>d.accept());
 await page.locator('#importProgressInput').setInputFiles({name:'v138-progress.json',mimeType:'application/json',buffer:backup});
 await page.waitForFunction(()=>state.vp['716']?.timesShown===4);
 await page.reload();
 assert.deepEqual(await page.evaluate(()=>state.vp['716']),old.vp['716']);
 await page.evaluate(async()=>{showView('cards');await openCardDetail('v','716')});
 const title=await page.locator('#cardDetailBody .fc-word').innerText();assert(title.includes('恵み'));assert((await page.locator('#cardDetailBody .fc-word').innerText()).includes('名詞'));
 assert((await page.locator('#cardDetailBody').innerText()).includes('自然の恵み'));
 assert.equal(await page.evaluate(()=>ACTIVE_VOCAB.find(x=>x.id===716).w),'恵み');
 await page.locator('.nav-tab[data-view="compare"]').click();const compare=await page.locator('#view-compare').innerText();assert(compare.includes('恵み'));assert(compare.includes('並'));
 assert.deepEqual(await page.evaluate(()=>state.vp['716']),old.vp['716']);assert.deepEqual(errors,[]);
 fs.writeFileSync('audit139/identity-results.json',JSON.stringify({sha256:require('node:crypto').createHash('sha256').update(fs.readFileSync('release139/JLPT_N1_ukrainian_reading_v139.html')).digest('hex'),browser:browser.version(),pass:true,stableId:716,oldLabel:'恵',newLabel:'恵み',importedProgress:old.vp['716'],comparisonKeys:old.comparisonKeys,scope:'Built-in vocabulary, actual v138 backup export → v139 import/reload/card/comparison; custom vocabulary not migrated.'},null,2));console.log('PASS ID716 v138 → v139 actual backup/import/reload/card/comparison');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
