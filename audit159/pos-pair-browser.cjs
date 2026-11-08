const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const file='JLPT_N1_v159_working.html',sha256=require('node:crypto').createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const expected={"2277": ["名詞", "副詞"], "2283": ["名詞", "副詞"], "2335": ["名詞", "ナ形"], "2343": ["名詞", "ナ形"], "2351": ["名詞", "ナ形"], "2357": ["名詞", "副詞"]};
(async()=>{const browser=await chromium.launch({headless:true});const results=[];try{
 for(const width of [360,412,1280]){
  const page=await browser.newPage({viewport:{width,height:915}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(path.resolve(file)).href);
  await page.evaluate(()=>{showView('cards');cardFilter='v';selectedCategory='all';document.getElementById('cardSearch').value='';document.getElementById('cardWeakOnly').checked=false;document.getElementById('cardHideMastered').checked=false;});
  for(const [id,parts] of Object.entries(expected))for(const part of ['名詞','ナ形','副詞','動詞']){
   await page.locator('#cardPos').selectOption(part);
   const included=await page.evaluate(id=>getCardPool().some(x=>String(x.id)===id),id);
   assert.equal(included,parts.includes(part),`${id}/${part}/${width}`);
  }
  for(const id of ['1953','1954','2310','2318']){
   await page.evaluate(id=>openCardDetail('v',id),id);
   await page.waitForFunction(id=>document.getElementById('cardDetailBody').dataset.currentKey==='v_'+id,id);
   const text=await page.locator('#cardDetailBody').innerText();
   if(['2310','2318'].includes(id)){assert(text.includes('Він невпевнено взяв ніж у руки.'));assert(!text.includes('Він незвично для себе взявся за ніж.'));}else{assert(text.includes('розподіляти прибуток між отримувачами'));assert(!text.includes('отримувати частки прибутку'));}
  }
  assert.deepEqual(errors,[]);results.push({width,posMembershipChecks:24,bothDirectionsOfChangedPair:true,previousPairRegression:true,pass:true});await page.close();
 }
 fs.writeFileSync('completion/v159-work/pos-pair-results.json',JSON.stringify({sha256,browser:browser.version(),results},null,2)+'\n');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
