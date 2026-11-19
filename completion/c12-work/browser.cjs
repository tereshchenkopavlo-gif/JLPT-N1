const fs=require('fs'),assert=require('assert/strict'),{chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const page=await browser.newPage();
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const html=fs.readFileSync('completion/c12-work/JLPT_N1_C12_candidate_UNACCEPTED.html','utf8');
 const rows=JSON.parse(fs.readFileSync('completion/c12-work/reading-candidates.json'));
 await page.route('http://c12.test/',r=>r.fulfill({contentType:'text/html',body:html}));
 await page.goto('http://c12.test/');
 const cases=[];
 for(const width of [360,412,1280]){
  await page.setViewportSize({width,height:900});
  for(const row of rows){
   await page.evaluate(row=>{
    curSession={items:[],passageIdx:0,passages:[{integrated:true,level:'medium',text:row.ja,translation:row.uk,questions:row.questions,targetIds:[],targetKeys:[],glossary:[]}]};
    showView('session');renderPassage();
   },row);
   assert.equal(await page.locator('.qchoice').count(),8);
   for(let i=0;i<2;i++){
    await page.locator('.qchoice[data-qi="'+i+'"][data-ci="'+row.questions[i].answer+'"]').click();
    assert.ok((await page.locator('#exp-'+i).innerText()).includes(row.questions[i].evidence));
   }
   assert.ok((await page.locator('body').innerText()).includes(row.ja.slice(0,20)));
   const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);
   assert.equal(overflow,false);
   cases.push({id:row.id,width,questions:2,choices:8,overflow});
  }
 }
 assert.deepEqual(errors,[]);
 fs.writeFileSync('completion/c12-work/browser-results.json',JSON.stringify({pass:true,cases,pageErrors:errors},null,2));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
