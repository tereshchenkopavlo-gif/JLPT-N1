const {chromium}=require('playwright'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const html=fs.readFileSync('release137/JLPT_N1_ukrainian_reading_v137.html','utf8');
(async()=>{const browser=await chromium.launch({headless:true});const results=[];try{
for(const width of [360,412,1280]){
 const page=await browser.newPage({viewport:{width,height:915}}),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(pathToFileURL(path.resolve('release137/JLPT_N1_ukrainian_reading_v137.html')).href);
 const conservation=await page.evaluate(()=>{
  const canonical=s=>localizeStudyHeadings(s).replace(/Форма:/g,'形：').replace(/【[^】]+】/gu,'').replace(/(?:接続|形|共通点|違い|例文|置き換え|用法|制約|文体)：/gu,'').replace(/\s+/gu,'');
  const rendered=s=>{const el=document.createElement('div');el.innerHTML=studyTextHtml(s);el.querySelectorAll('.study-subheading').forEach(x=>x.remove());return canonical(el.textContent)};
  const failures=[];let checked=0;
  for(const [kind,db] of [['v',VOCAB_DETAILS_BY_ID],['g',GRAMMAR_DETAILS_BY_ID]])for(const [id,d] of Object.entries(db)){
   const data={translation:d.t,usage:d.usage||''},model=cardStudyModel(kind,data);
   for(const [field,original] of [['translation',model.translation],['usage',model.usage]]){
    if(rendered(original)!==canonical(original))failures.push({kind,id,field,expected:canonical(original),actual:rendered(original)});checked++;
   }
   if(kind==='g'&&canonical(model.translation+model.usage)!==canonical(d.t+(d.usage||'')))failures.push({kind,id,error:'grammar content moved incorrectly'});
  }
  for(const [i,p] of VOCAB_AUDITED_PAIRS.entries())if(!LEXICAL_PRESENTATION[[Number(p.a),Number(p.b)].sort((a,b)=>a-b).join('_')]){if(rendered(p.note)!==canonical(p.note))failures.push({pair:i});checked++}
  for(const [i,p] of GRAMMAR_AUDITED_PAIRS.entries()){if(rendered(p[2])!==canonical(p[2]))failures.push({grammarPair:i});checked++}
  const covered=new Set([...VOCAB_AUDITED_PAIRS.map(x=>x.note),...GRAMMAR_AUDITED_PAIRS.map(x=>x[2])]);
  const legacy=new Set([...Object.values(AUTO_VOCAB_COMPARISONS),...Object.values(AUTO_GRAMMAR_COMPARISONS)].flat().map(x=>x.note).filter(Boolean));
  for(const note of legacy)if(!covered.has(note)){if(rendered(note)!==canonical(note))failures.push({legacyNote:note.slice(0,80)});checked++}
  return {checked,failures};
 });assert.deepEqual(conservation.failures,[],JSON.stringify(conservation.failures.slice(0,5)));
 await page.locator('.nav-tab[data-view="cards"]').click();
 const allCount=await page.evaluate(()=>getCardPool().length);assert.equal(allCount,3914);
 const options=await page.locator('#cardPos option').evaluateAll(xs=>xs.map(x=>x.value));
 const counts={};
 for(const label of options.filter(x=>x!=='all')){
  await page.locator('#cardPos').selectOption(label);
  const ids=await page.evaluate(()=>getCardPool().map(x=>x.id));assert(ids.length>0);counts[label]=ids.length;
  assert(await page.evaluate(({ids,label})=>ids.every(id=>vocabPartOfSpeech(id).includes(label)),{ids,label}));
  const listed=await page.locator('#cardsList .cardrow').evaluateAll(xs=>xs.map(x=>x.dataset.id));assert.deepEqual(listed,ids.slice(0,100));
 }
 await page.locator('#cardPos').selectOption('イ形');
 const expected=await page.evaluate(()=>getCardPool().map(x=>x.id));assert.equal(expected.length,119);
 await page.evaluate(ids=>{state.vp[ids[0]]={status:'S'};state.vp[ids[1]]={status:'X'};renderCardsList()},expected);
 await page.locator('#cardHideMastered').check();assert.equal(await page.evaluate(()=>getCardPool().length),118);
 await page.locator('#cardWeakOnly').check();assert.deepEqual(await page.evaluate(()=>getCardPool().map(x=>x.id)),[expected[1]]);
 await page.locator('#cardWeakOnly').uncheck();await page.locator('#cardHideMastered').uncheck();
 await page.evaluate(ids=>{delete state.vp[ids[0]];delete state.vp[ids[1]];renderCardsList()},expected);
 const tag=await page.evaluate(()=>THEME_CATEGORIES.find(c=>c.id!=='all'&&getCardPool().some(x=>x.tags.includes(c.id))).id);
 await page.locator(`#categoryChips [data-cat="${tag}"]`).click();assert(await page.evaluate(tag=>getCardPool().length>0&&getCardPool().every(x=>x.tags.includes(tag)),tag));await page.locator('#categoryChips [data-cat="all"]').click();
 await page.locator('#cardsList .cardrow').first().click();await page.waitForSelector('#cardDetailBody .word-pos');
 assert.match(await page.locator('#cardDetailBody .word-pos').innerText(),/イ形/);
 await page.locator('#btnCardNext').click();await page.waitForFunction(id=>document.getElementById('cardDetailBody').dataset.currentKey==='v_'+id,expected[1]);
 const peer=await page.locator('#cardDetailBody .chip.link[data-kind="v"]').evaluateAll(nodes=>nodes.map(x=>({id:x.dataset.id}))).then(xs=>xs.find(x=>!expected.includes(x.id)));
 if(peer){await page.locator(`#cardDetailBody .chip.link[data-kind="v"][data-id="${peer.id}"]`).first().click();await page.waitForFunction(id=>document.getElementById('cardDetailBody').dataset.currentKey==='v_'+id,peer.id);assert.equal(await page.locator('#cardNavScope').innerText(),'全語彙')}
 await page.locator('#btnCardBack').click();assert.equal(await page.locator('#cardPos').inputValue(),'イ形');

 await page.locator('#cardSearch').fill('い');assert((await page.evaluate(()=>getCardPool())).every(x=>x.label.includes('い')||x.reading.includes('い')));
 await page.locator('#cardSearch').fill('');await page.locator('#btnNextPage').click();
 await page.locator('#cardsList .cardrow').first().click();await page.waitForFunction(id=>document.getElementById('cardDetailBody').dataset.currentKey==='v_'+id,expected[100]);await page.locator('#btnCardBack').click();assert.match(await page.locator('#pageInfo').innerText(),/^2\s*\//);
 await page.locator('#cardFilterToggle [data-f="g"]').click();assert.equal(await page.locator('#cardPosFilter').isVisible(),false);assert.equal(await page.evaluate(()=>getCardPool().length),130);
 await page.locator('#cardFilterToggle [data-f="v"]').click();assert.equal(await page.locator('#cardPosFilter').isVisible(),true);assert.equal(await page.locator('#cardPos').inputValue(),'イ形');
 await page.locator('#cardPos').selectOption('all');
 await page.evaluate(()=>openCardDetail('v','58'));await page.waitForSelector('#cardDetailBody .lexical-pair[data-pair="58_75"] .study-example');
 const pair=page.locator('#cardDetailBody .lexical-pair[data-pair="58_75"]');assert.equal(await pair.locator('.study-example').count(),2);assert.equal(await pair.locator('.study-subheading').count(),4);
 assert.match(await page.locator('#cardDetailBody .word-pos').innerText(),/名詞/);
 const legacy=page.locator('#cardDetailBody .nuance-group');assert(await legacy.locator('.study-paragraph').count()>=2);assert.match(await legacy.innerText(),/制限/);assert.match(await legacy.innerText(),/規制/);
 const usage=await page.locator('#cardDetailBody .fc-trans').nth(1).innerText();assert.doesNotMatch(usage,/^Іменник/);assert.match(usage,/行動／排出を規制する/);
 if(width===412){await pair.screenshot({path:'/tmp/v137-regulation.png'});await page.locator('#cardDetailBody .fc-word').screenshot({path:'/tmp/v137-title.png'});}
 await page.evaluate(()=>{saveComparisonKeys(['v_58','v_75','g_1','g_2']);renderComparison();showView('compare')});
 const guide=await page.locator('#compareGuides .lexical-guide').innerText();assert.match(guide,/Місто обмежило рух/);assert.equal(await page.locator('#compareGuides .lexical-guide .study-example').count(),2);
 assert.equal(await page.locator('.compare-entry .word-pos').count(),2);assert(await page.locator('#compareGuides .study-subheading').count()>3);
 await page.reload();await page.locator('.nav-tab[data-view="compare"]').click();assert.equal(await page.locator('.compare-entry').count(),4);assert.equal(await page.locator('.compare-entry .word-pos').count(),2);
 await page.locator('.nav-tab[data-view="cards"]').click();await page.evaluate(()=>openCardDetail('g','1'));await page.waitForSelector('#cardDetailBody .study-subheading');
 assert.equal(await page.locator('#cardDetailBody .word-pos').count(),0);
 if(width===412){await page.locator('#cardDetailBody').screenshot({path:'/tmp/v137-grammar.png'});await page.locator('#btnCardBack').click();await page.locator('#cardPos').selectOption('ナ形');await page.screenshot({path:'/tmp/v137-list.png',fullPage:false});}
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);assert(overflow<=2,`overflow ${overflow}`);assert.deepEqual(errors,[]);
 results.push({width,contentChecks:conservation.checked,posOptions:options.length-1,posCounts:counts,filter:true,combinedFilters:true,navigation:true,comparison:true,progressUnaffected:true,pass:true});await page.close();
}
fs.writeFileSync('audit137/presentation-results.json',JSON.stringify({sha256:require('node:crypto').createHash('sha256').update(html).digest('hex'),browser:browser.version(),results},null,2));console.log('PASS presentation conservation, POS, filters and comparisons at 360/412/1280px');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
