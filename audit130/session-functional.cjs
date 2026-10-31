// Launch a real learning session and verify live exercise content is rendered.
const {chromium}=require('playwright');
const {pathToFileURL}=require('node:url');
const path=require('node:path');
const assert=require('node:assert/strict');
const url=pathToFileURL(path.resolve('release130/JLPT_N1_ukrainian_reading_v130.html')).href;
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  for(const width of [360,412,1280]){
   const page=await browser.newPage({viewport:{width,height:900}});
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(url,{waitUntil:'load'});
   assert.equal(await page.locator('#btnStartSession').isVisible(),true,'session start button visible');
   await page.locator('#btnStartSession').click();
   await page.waitForFunction(()=>['teachBody','sessBody','sessError','sessDone'].some(id=>{const e=document.getElementById(id);return e&&e.getClientRects().length>0}),{timeout:20000});
   const state=await page.evaluate(()=>['teachBody','sessBody','sessError','sessDone'].filter(id=>document.getElementById(id).getClientRects().length>0));
   assert.equal(state.length,1,'exactly one session state visible');
   assert.notEqual(state[0],'sessError','session generation succeeds');
   assert.notEqual(state[0],'sessDone','session is not immediately finished');
   const txt=await page.locator('#'+state[0]).innerText();
   assert.ok(txt.trim().length>25,'session contains real content');
   if(state[0]==='teachBody'){
    assert.equal(await page.locator('#btnSkipTeach').isVisible(),true,'skip teaching is available');
    await page.locator('#btnSkipTeach').click();
    await page.waitForFunction(()=>document.getElementById('sessBody').getClientRects().length>0);
   }
   const passage=await page.locator('#passageArea').innerText();
   assert.ok(passage.trim().length>50,'exercise contains reading/questions');
   const controls=await page.locator('#passageArea').evaluate(el=>({
    markup:el.innerHTML.slice(0,4500),
    buttons:[...el.querySelectorAll('button')].map(b=>({text:b.textContent.trim().slice(0,60),className:b.className,id:b.id})).slice(0,24),
    radios:el.querySelectorAll('input[type="radio"]').length
   }));
   console.log('SESSION-CONTROLS '+JSON.stringify({width,...controls}));
   const questions=page.locator('#passageArea .qcard');
   const questionCount=await questions.count();
   assert.ok(questionCount>=1,'exercise has answerable questions');
   for(let i=0;i<questionCount;i++){
    const q=questions.nth(i);
    assert.equal(await q.locator('.qchoice').count(),4,'four choices per question');
    await q.locator('.qchoice').first().click();
    const choiceClasses=await q.locator('.qchoice').evaluateAll(items=>items.map(el=>el.className));
    console.log('ANSWER-CLASSES '+JSON.stringify({width,i,choiceClasses}));
    assert.equal(await q.locator('.qexplain').isVisible(),true,'answer reveals explanation '+i);
    assert.ok((await q.locator('.qexplain').innerText()).trim().length>4,'nonempty explanation '+i);
   }
   const rows=page.locator('#passageArea .raterow');
   const ratingCount=await rows.count();
   assert.ok(ratingCount>=1,'session has progress grading controls');
   for(let i=0;i<ratingCount;i++) await rows.nth(i).locator('.ratebtn[data-g="S"]').click();
   assert.equal(await page.locator('#btnPassageNext').isEnabled(),true,'next passage enabled after answers and ratings');
   console.log('PASS v130 question explanations and progress ratings',JSON.stringify({width,questionCount,ratingCount}));
   await page.locator('#btnPassageNext').click();
   await page.waitForFunction(()=>['teachBody','sessBody','sessDone'].some(id=>{const e=document.getElementById(id);return e&&e.getClientRects().length>0}),{timeout:15000});
   assert.equal(await page.locator('#sessError').isVisible(),false,'advancing exercise does not cause session error');
   const postNext=await page.evaluate(()=>({session:document.getElementById('sessBody').getClientRects().length>0,done:document.getElementById('sessDone').getClientRects().length>0,teaching:document.getElementById('teachBody').getClientRects().length>0}));
   assert.ok(postNext.session||postNext.done||postNext.teaching,'next exercise changes to supported session state');
   console.log('PASS v130 next passage transition',JSON.stringify({width,postNext}));
   assert.equal(errors.length,0,'no browser runtime errors');
   console.log('PASS v130 learning session',JSON.stringify({width,state,passageChars:passage.length}));
   await page.close();
  }
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
