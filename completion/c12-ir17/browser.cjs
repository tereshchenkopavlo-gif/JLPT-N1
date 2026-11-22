const fs=require('fs'),assert=require('assert/strict'),{chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const page=await browser.newPage();
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const html=fs.readFileSync('completion/c12-ir17/JLPT_N1_C12_candidate_UNACCEPTED.html','utf8');
 const rows=JSON.parse(fs.readFileSync('completion/c12-ir17/drafts.json'));
 await page.route('http://c12.test/',r=>r.fulfill({contentType:'text/html',body:html}));
 await page.goto('http://c12.test/');
 const cases=[];
 for(const width of [360,412,1280]){
  await page.setViewportSize({width,height:900});
  for(const row of rows){
   const generated=await page.evaluate(row=>{
    const originalRandom=Math.random;
    let passages;
    try {
     const index=70;
     Math.random=()=>(index+0.5)/71;
     passages=SmartEngine.generateOfflinePassage([]);
    } finally { Math.random=originalRandom; }
    const passage=passages.find(p=>p.level==='long');
    curSession={items:[],passageIdx:0,passages:[passage]};
    showView('session');document.getElementById('sessBody').style.display='';renderPassage();
    return passage;
   },row);
   assert.equal(generated.title,row.title);
   assert.equal(generated.plainText,row.ja);
   assert.equal(generated.translation,row.uk);
   assert.equal(generated.glossary.length,row.contextNotes.length);
   for(let i=0;i<3;i++) assert.equal(generated.questions[i].choices[generated.questions[i].answer],row.questions[i].choices[row.questions[i].answer]);
   assert.equal(await page.locator('.qchoice').count(),12);
   for(let i=0;i<3;i++){
    await page.locator('.qchoice[data-qi="'+i+'"][data-ci="'+generated.questions[i].answer+'"]').click();
    assert.equal(await page.locator('#exp-'+i).innerText(),row.questions[i].explain);
   }
   assert.ok((await page.locator('body').innerText()).includes(row.ja.slice(0,20)));
   const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);
   assert.equal(overflow,false);
   cases.push({id:row.id,width,questions:3,choices:12,overflow});
  }
 }
 assert.deepEqual(errors,[]);
 fs.writeFileSync('completion/c12-ir17/browser-results.json',JSON.stringify({pass:true,cases,pageErrors:errors},null,2));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
