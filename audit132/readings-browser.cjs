// A test-only route selects a specific reading inside the real generator.
// The released file has no test hooks and is separately tested without instrumentation.
const {chromium}=require('playwright');
const fs=require('node:fs');
const assert=require('node:assert/strict');
const html=fs.readFileSync('release132/JLPT_N1_ukrainian_reading_v132.html','utf8');
const bank=JSON.parse(fs.readFileSync('audit132/readings-after.json','utf8'));
const needle='const chosen = bank[Math.floor(Math.random() * bank.length)];';
assert.equal(html.split(needle).length,2);
const routed=html.replace(needle,'const chosen = bank[window.__readingIndex[level]];');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const results=[];
 try {
  for(const width of [360,412,1280]){
   const page=await browser.newPage({viewport:{width,height:920}});
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.route('http://trainer.test/trainer.html',r=>r.fulfill({contentType:'text/html',body:routed}));
   await page.goto('http://trainer.test/trainer.html');
   for(const [level,arr] of Object.entries(bank)) for(const [index,reading] of arr.entries()){
    if(reading.source!=='original_v132')continue;
    const generated=await page.evaluate(({level,index,reading})=>{
     window.__readingIndex={medium:0,long:0,[level]:index};
     const items=reading.contextNotes.map(n=>({kind:n.kind,id:Number(n.id),word:(n.kind==='v'?ACTIVE_VOCAB:GRAMMAR).find(x=>String(x.id)===n.id)}));
     // Readings with no annotated cards still render with actual session cards.
     if(!items.length)items.push({kind:'v',id:1,word:ACTIVE_VOCAB.find(x=>x.id===1)});
     const passages=SmartEngine.generateOfflinePassage(items);
     const passage=passages.find(x=>x.level===level);
     curSession={items,passages:[passage],passageIdx:0,ratings:{},plan:null};
     showView('session');
     for(const id of ['teachBody','sessDone','sessLoading','sessError'])document.getElementById(id).style.display='none';
     document.getElementById('sessBody').style.display='';
     renderPassage();
     return passage;
    },{level,index,reading});
    assert.equal(generated.title,reading.title);
    assert.equal(generated.plainText,reading.ja);
    assert.equal(generated.translation,reading.uk);
    assert.equal(generated.glossary.length,reading.contextNotes.length);
    assert.equal((await page.locator('#passageArea .reading-translation').innerText()).replace(/\s+/g,' '),reading.uk.replace(/\s+/g,' '));
    const marking=await page.locator('#passageArea .passage').evaluate(el=>({text:el.innerText,bold:[...el.querySelectorAll('b')].map(b=>b.textContent),nested:el.querySelectorAll('b b').length}));
    assert.equal(marking.nested,0);
    assert.equal(marking.text.replace(/\s+/g,''),reading.ja.replace(/\s+/g,''));
    for(const note of reading.contextNotes){
     assert(generated.glossary.some(g=>g.quote===note.quote&&g.meaning===note.meaning));
     assert(marking.bold.some(b=>b.includes(note.quote)||note.quote.includes(b)),note.quote);
    }
    const questions=page.locator('#passageArea .qcard');
    assert.equal(await questions.count(),reading.questions.length);
    for(let i=0;i<generated.questions.length;i++){
     const q=generated.questions[i],orig=reading.questions[i],card=questions.nth(i);
     assert.equal(q.choices[q.answer],orig.choices[orig.answer]);
     assert.equal(await card.locator('.qchoice').count(),4);
     const clicked=i%2?q.answer:(q.answer+1)%4;
     await card.locator('.qchoice').nth(clicked).click();
     assert.equal(await card.locator('.qchoice.correct').count(),1);
     assert.equal(await card.locator('.qchoice.wrong').count(),i%2?0:1);
     assert.equal(await card.locator('.qchoice.correct').innerText(),orig.choices[orig.answer]);
     assert.equal(await card.locator('.qexplain').innerText(),orig.explain);
     assert.equal(await card.locator('.qexplain').isVisible(),true);
    }
    const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
    assert(overflow<=2,`${reading.id}: horizontal overflow ${overflow}`);
    if(width===412&&['m132-06','l132-03','l132-07'].includes(reading.id)){
     await page.screenshot({path:`/tmp/${reading.id}.png`,fullPage:true});
    }
    results.push({width,id:reading.id,questions:reading.questions.length,glossary:generated.glossary.length,pass:true});
   }
   assert.deepEqual(errors,[]);
   await page.close();
  }
  fs.writeFileSync('audit132/readings-browser-results.json',JSON.stringify({htmlSha256:require('node:crypto').createHash('sha256').update(html).digest('hex'),browser:browser.version(),results},null,2));
  console.log('PASS all new readings at 360/412/1280px:',results.length,'renderings,',results.reduce((n,x)=>n+x.questions,0),'answers');
 } finally {await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
