const {chromium}=require('playwright'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{pathToFileURL}=require('node:url');
const file='release149/JLPT_N1_ukrainian_reading_v149.html',sha256=require('node:crypto').createHash('sha256').update(fs.readFileSync(file)).digest('hex'),review=JSON.parse(fs.readFileSync('audit149/editorial-review.json'));
(async()=>{const browser=await chromium.launch({headless:true});try{const results=[],pairResults=[];
for(const width of [360,412,1280]){
 const page=await browser.newPage({viewport:{width,height:915}}),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(pathToFileURL(path.resolve(file)).href);
 for(const row of review.rows){const id=Number(row.key);
  await page.evaluate(id=>{showView('cards');openCardDetail('g',String(id))},id);
  await page.waitForFunction(id=>document.getElementById('cardDetailBody').dataset.currentKey==='g_'+id&&!!document.querySelector('#cardDetailBody .fc-trans'),id);
  const x=await page.evaluate(id=>{const el=document.getElementById('cardDetailBody'),s=el.textContent,d=GRAMMAR_DETAILS_BY_ID[id],norm=s=>s.replace(/\s/g,'');return {definition:s.includes(d.m),examples:d.examples.every(x=>norm(s).includes(norm(x))),translations:d.exampleTranslations.every(x=>norm(s).includes(norm(x))),meaning:norm(s).includes(norm(d.t.split('\n')[0])),headings:[...el.querySelectorAll('.study-subheading')].map(x=>x.textContent),noUkrainianServiceHeading:!s.includes('Приєднання:'),overflow:document.documentElement.scrollWidth>innerWidth+1}},id);
  assert(x.definition&&x.examples&&x.translations&&x.meaning&&x.noUkrainianServiceHeading,JSON.stringify({id,width,x}));assert(x.headings.includes('接続')&&x.headings.includes('用法'));assert(!x.overflow,`overflow ${id}`);results.push({id,width,pass:true,...x});
 }
 for(const row of review.pairs){
  await page.evaluate(index=>{const [a,b]=GRAMMAR_AUDITED_PAIRS[index];saveComparisonKeys([a,b].map(w=>'g_'+GRAMMAR.find(x=>x.w===w).id));renderComparison();showView('compare')},row.index);
  const x=await page.evaluate(row=>{const el=[...document.querySelectorAll('#compareGuides .compare-guide')].find(x=>x.querySelector('h3')?.textContent.includes(row.labels.join(' / '))),norm=s=>s.replace(/\s/g,'');if(!el)return{found:false};return {found:true,headings:[...el.querySelectorAll('.study-subheading')].map(x=>x.textContent),content:[row.common,row.connection,row.difference,row.substitution,...row.examples.flatMap(x=>[x.japanese,x.ukrainian])].every(x=>norm(el.textContent).includes(norm(x))),separateUkrainianExamples:el.querySelectorAll('.study-example-translation').length===2,overflow:document.documentElement.scrollWidth>innerWidth+1}},row);
  assert(x.found&&x.content&&x.separateUkrainianExamples&&!x.overflow,JSON.stringify({index:row.index,width,x}));assert.deepEqual(x.headings,['共通点','接続','違い','例文','置き換え']);pairResults.push({index:row.index,width,pass:true,...x});
 }
 if(width===412){await page.locator('#compareGuides').screenshot({path:'/tmp/v149-pair89.png'});await page.evaluate(()=>{showView('cards');openCardDetail('g','57')});await page.locator('#cardDetailBody').screenshot({path:'/tmp/v149-card57.png'});}
 assert.deepEqual(errors,[]);await page.close();
}
fs.writeFileSync('audit149/grammar-results.json',JSON.stringify({sha256,browser:browser.version(),pass:true,reviewType:'Technical rendering and content conservation; author linguistic decisions in editorial-review.json',results,pairResults},null,2)+'\n');console.log('PASS 27 cards and 9 actual selected comparison guides at three widths');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
