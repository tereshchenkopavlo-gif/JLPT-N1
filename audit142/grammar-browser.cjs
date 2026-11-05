const {chromium}=require('playwright'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{pathToFileURL}=require('node:url');
const file='release142/JLPT_N1_ukrainian_reading_v142.html',sha256=require('node:crypto').createHash('sha256').update(fs.readFileSync(file)).digest('hex');
(async()=>{const browser=await chromium.launch({headless:true});try{const results=[];
for(const width of [360,412,1280]){
 const page=await browser.newPage({viewport:{width,height:915}}),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(pathToFileURL(path.resolve(file)).href);
 for(const id of [28,72,89,130]){
  await page.evaluate(id=>{showView('cards');openCardDetail('g',String(id))},id);
  await page.waitForFunction(id=>document.getElementById('cardDetailBody').dataset.currentKey==='g_'+id&&!!document.querySelector('#cardDetailBody .fc-trans'),id);
  const x=await page.evaluate(id=>{const el=document.getElementById('cardDetailBody'),s=el.textContent,d=GRAMMAR_DETAILS_BY_ID[id];return {definition:s.includes(d.m),translation:localizeStudyHeadings(d.t).split('Приєднання:')[0].trim().split('。')[0],text:s,overflow:document.documentElement.scrollWidth>innerWidth+1}},id);
  assert(x.definition,`definition ${id}`);assert(!x.overflow,`overflow ${id}`);
  if(id===130)assert(x.text.includes('майбутньої нагоди'));
  if(width===412&&id===130)await page.locator('#cardDetailBody').screenshot({path:'/tmp/v142-card130.png'});
  results.push({id,width,pass:true});
 }
 assert.deepEqual(errors,[]);await page.close();
}
fs.writeFileSync('audit142/grammar-results.json',JSON.stringify({sha256,browser:browser.version(),pass:true,results},null,2)+'\n');console.log('PASS four revised grammar cards at three widths');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
