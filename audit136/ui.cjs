const {chromium}=require('playwright');
const {pathToFileURL}=require('node:url');
const path=require('node:path'),fs=require('node:fs'),assert=require('node:assert/strict');
const html=fs.readFileSync('release136/JLPT_N1_ukrainian_reading_v136.html','utf8');
const url=pathToFileURL(path.resolve('release136/JLPT_N1_ukrainian_reading_v136.html')).href;
const checks=[];
const key=page=>page.locator('#cardDetailBody').getAttribute('data-current-key');
async function expectCard(page,k){
 await page.waitForFunction(k=>document.getElementById('cardDetailBody').dataset.currentKey===k&&document.querySelector('#cardDetailBody .fc-trans'),k);
 assert.equal(await key(page),k);
}
async function swipe(page,dx,dy=0,selector='#cardDetailBody'){
 await page.locator(selector).evaluate((el,{dx,dy})=>{
  const emit=(name,field,value)=>{const e=new Event(name,{bubbles:true});Object.defineProperty(e,field,{value});el.dispatchEvent(e)};
  emit('touchstart','touches',[{clientX:240,clientY:300}]);
  emit('touchend','changedTouches',[{clientX:240+dx,clientY:300+dy}]);
 },{dx,dy});
}
(async()=>{
 const browser=await chromium.launch({headless:true});
 try {
  for(const width of [360,412,1280]){
   const page=await browser.newPage({viewport:{width,height:900}});const errors=[];
   page.on('pageerror',e=>errors.push(e.message));await page.goto(url);
   await page.locator('.nav-tab[data-view="cards"]').click();
   await page.locator('#cardsList .cardrow').first().click();await expectCard(page,'v_1');
   const saved=await page.evaluate(()=>JSON.stringify(state));
   assert.equal(await page.locator('#btnCardPrev').isDisabled(),true);
   assert.equal(await page.locator('#btnCardNext').innerText(),'次のカード →');
   assert.equal(await page.locator('#cardDetailBody .fc-section-label').first().innerText(),'ウクライナ語訳');
   assert((await page.locator('#cardDetailBody .fc-section-label').allTextContents()).includes('例文'));
   assert.equal(await page.locator('#cardDetailBody .compare-add').innerText(),'＋ 比較リストに追加');
   assert.match(await page.locator('#cardDetailBody .fc-trans').first().innerText(),/погіршення/);
   await page.locator('#btnCardNext').click();await expectCard(page,'v_2');
   await page.locator('#btnCardPrevBottom').click();await expectCard(page,'v_1');
   await page.keyboard.press('ArrowRight');await expectCard(page,'v_2');
   await page.keyboard.press('ArrowLeft');await expectCard(page,'v_1');
   await swipe(page,-130);await expectCard(page,'v_2');
   await swipe(page,130);await expectCard(page,'v_1');
   await swipe(page,20,180);assert.equal(await key(page),'v_1','vertical gesture does not navigate');
   await swipe(page,-130,0,'#cardDetailBody .compare-add');assert.equal(await key(page),'v_1','button gesture does not navigate');
   assert.equal(await page.evaluate(()=>JSON.stringify(state)),saved,'browsing does not grade cards');
   await page.locator('#cardDetailBody .compare-add').click();
   assert.equal(await page.locator('#cardDetailBody .compare-add').innerText(),'✓ 比較リストから削除');
   await page.locator('.nav-tab[data-view="compare"]').click();
   assert.equal(await page.locator('#view-compare h2').innerText(),'比較リスト');
   assert.equal(await page.locator('.remove-compare').first().innerText(),'リストから削除');
   assert.match(await page.locator('.compare-ua').first().innerText(),/погіршення/);
   await page.locator('.nav-tab[data-view="cards"]').click();
   await page.locator('#cardSearch').fill('悪化');await page.locator('#cardsList .cardrow').click();await expectCard(page,'v_1');
   assert.equal(await page.locator('#btnCardPrev').isDisabled(),true);assert.equal(await page.locator('#btnCardNext').isDisabled(),true);
   assert.equal(await page.locator('.card-position').first().innerText(),'1 / 1');
   const peer=page.locator('#cardDetailBody .chip.link[data-kind="v"]').first();
   assert(await peer.count());const peerId=await peer.getAttribute('data-id');await peer.click();await expectCard(page,'v_'+peerId);
   assert.equal(await page.locator('#cardNavScope').innerText(),'全語彙','related card outside filter gets an explicit full-vocabulary scope');
   await page.locator('#btnCardBack').click();assert.equal(await page.locator('#cardSearch').inputValue(),'悪化');
   await page.locator('#cardSearch').fill('');
   await page.locator('#cardsList .cardrow[data-id="100"]').click();await expectCard(page,'v_100');
   await page.locator('#btnCardNext').click();await expectCard(page,'v_101');await page.locator('#btnCardBack').click();
   assert.match(await page.locator('#pageInfo').innerText(),/^2\s*\//);
   assert.equal(await page.locator('#cardsList .cardrow').first().getAttribute('data-id'),'101');
   await page.locator('#cardFilterToggle [data-f="g"]').click();
   await page.locator('#cardsList .cardrow').first().click();await expectCard(page,'g_1');
   assert.equal(await page.locator('.card-position').first().innerText(),'1 / 130');
   assert((await page.locator('.auto-relations-label').allTextContents()).includes('類似・比較表現'));
   assert.match(await page.locator('#cardDetailBody').innerText(),/接続/);
   assert.doesNotMatch(await page.locator('#cardDetailBody').innerText(),/【Приєднання】/);
   await page.locator('#btnCardNext').click();await expectCard(page,'g_2');
   await page.evaluate(()=>openCardDetail('g','130'));await expectCard(page,'g_130');
   assert.equal(await page.locator('#btnCardNext').isDisabled(),true);
   await page.locator('#btnCardPrev').click();await expectCard(page,'g_129');
   await page.locator('#btnCardBack').click();
   await page.locator('#categoryChips .cat-chip').nth(1).click();
   const ids=await page.locator('#cardsList .cardrow').evaluateAll(rows=>rows.map(r=>r.dataset.id));
   assert(ids.length>=2);await page.locator('#cardsList .cardrow').first().click();await expectCard(page,'g_'+ids[0]);
   await page.locator('#btnCardNext').click();await expectCard(page,'g_'+ids[1]);
   assert.equal(await page.locator('.card-position').first().innerText(),`2 / ${ids.length}`);
   // Delayed data from a previous card must never replace the newest card.
   await page.evaluate(async()=>{
    const original=getCardData;
    getCardData=async(kind,id)=>{if(String(id)==='1')await new Promise(r=>setTimeout(r,120));return original(kind,id)};
    try{await Promise.all([openCardDetail('g','1'),openCardDetail('g','2')]);}finally{getCardData=original}
   });
   await expectCard(page,'g_2');
   const expected=await page.evaluate(async()=>localizeStudyHeadings(cardStudyModel('g',await getCardData('g','2')).translation));
   assert.equal((await page.locator('#cardDetailBody .fc-trans').first().innerText()).replace(/\s+/g,''),expected.replace(/\s+/g,''));
   await page.locator('#cardDetailBody .act-master').click();
   await page.waitForFunction(()=>document.getElementById('cardDetailBody').dataset.currentKey!=='g_2');
   assert.equal(await page.evaluate(()=>state.gp['2'].status),'S','grading still advances and saves');
   const weakKey=await key(page),canAdvance=await page.locator('#btnCardNext').isEnabled();
   await page.locator('#cardDetailBody .act-weak').click();
   if(canAdvance)await page.waitForFunction(old=>document.getElementById('cardDetailBody').dataset.currentKey!==old,weakKey);
   assert.equal(await page.evaluate(k=>state.gp[k.split('_')[1]].status,weakKey),'X','weak grading still saves the intended card');
   const labels=await page.locator('.fc-section-label,.auto-relations-label,#view-compare h2,.compare-type,.remove-compare,.compare-add,.card-nav button').allTextContents();
   for(const text of labels)assert.doesNotMatch(text,/[А-Яа-яІіЇїЄєҐґ]/,'service label is Japanese: '+text);
   const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
   assert(overflow<=2,'no horizontal overflow');assert.deepEqual(errors,[]);
   if(width===412){await page.locator('#btnCardPrev').click();await page.screenshot({path:'/tmp/v136-card.png',fullPage:true});}
   checks.push({width,navigation:true,search:true,category:true,pagination:true,keyboard:true,syntheticSwipe:true,race:true,grading:true,labels:true});
   await page.close();
  }
  fs.writeFileSync('audit136/ui-results.json',JSON.stringify({sha256:require('node:crypto').createHash('sha256').update(html).digest('hex'),browser:browser.version(),checks},null,2));
  console.log('PASS v136 navigation and Japanese UI at all three widths');
 } finally {await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
