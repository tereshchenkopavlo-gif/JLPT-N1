const {chromium}=require('playwright');
const {pathToFileURL}=require('node:url');
const path=require('node:path'),fs=require('node:fs'),assert=require('node:assert/strict');
const file='release133/JLPT_N1_ukrainian_reading_v133.html';
(async()=>{
 const browser=await chromium.launch({headless:true}),results=[];
 try{
  for(const width of [360,412,1280]){
   const page=await browser.newPage({viewport:{width,height:900}}),errors=[],dialogs=[];
   page.on('pageerror',e=>errors.push(e.message));page.on('dialog',async d=>{dialogs.push(d.message());await d.accept()});
   await page.goto(pathToFileURL(path.resolve(file)).href);
   async function add(kind,id){
    await page.locator('.nav-tab[data-view="cards"]').click();
    await page.evaluate(({kind,id})=>openCardDetail(kind,String(id)),{kind,id});
    await page.locator('#cardDetailBody .compare-add').click();
   }
   await add('g',1);await add('g',2);
   await page.locator('.nav-tab[data-view="compare"]').click();
   assert.equal(await page.locator('.compare-entry').count(),2);
   assert((await page.locator('#compareGuides').innerText()).includes('【接続】'));
   assert(!(await page.locator('#compareGuides').innerText()).includes('【Приєднання】'));
   await add('g',3);await page.locator('.nav-tab[data-view="compare"]').click();
   assert.equal(await page.locator('.compare-entry').count(),3);
   assert((await page.locator('#compareGuides').innerText()).includes('確認済みの比較解説がない組合せ'));
   for(let id=1;id<=27;id++)await add('v',id);
   assert.equal(await page.evaluate(()=>getComparisonKeys().length),30);
   await add('v',28);
   assert.equal(await page.evaluate(()=>getComparisonKeys().length),30);
   assert.equal(await page.locator('#cardDetailBody .compare-add').innerText(),'＋ 比較リストに追加');
   assert((await page.locator('#toastBox').innerText()).includes('比較リストは30件までです'));
   await page.locator('.nav-tab[data-view="compare"]').click();
   assert.equal(await page.locator('.compare-entry').count(),30);
   assert.equal(await page.evaluate(()=>new Set(getComparisonKeys()).size),30);
   const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
   assert(overflow<=2,'comparison layout fits '+width);
   const headers=await page.locator('#view-compare h2,#view-compare h3,#view-compare button,.compare-type').allTextContents();
   for(const label of headers)assert.doesNotMatch(label,/[А-Яа-яІіЇїЄєҐґ]/);
   await page.locator('.remove-compare').first().click();assert.equal(await page.locator('.compare-entry').count(),29);
   await page.locator('#btnClearCompare').click();assert.deepEqual(dialogs,['比較リストをすべて削除しますか？']);
   assert.equal(await page.locator('.compare-entry').count(),0);
   assert((await page.locator('.compare-empty').innerText()).includes('比較リストは空です'));
   assert.deepEqual(errors,[]);
   results.push({width,two:true,three:true,mixed:true,limit30:true,noDuplicates:true,remove:true,clear:true,japanese:true});
   await page.close();
  }
  fs.writeFileSync('audit133/comparison-results.json',JSON.stringify({sha256:require('node:crypto').createHash('sha256').update(fs.readFileSync(file)).digest('hex'),results},null,2));
  console.log('PASS v133 two/three/mixed/30-item comparison, Japanese labels, removal and clearing');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
