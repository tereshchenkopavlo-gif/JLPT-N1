const {chromium}=require('playwright'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{pathToFileURL}=require('node:url');
const html=fs.readFileSync('release140/JLPT_N1_ukrainian_reading_v140.html','utf8');
function data(name){const start=html.indexOf('const '+name+' = ')+('const '+name+' = ').length;return JSON.parse(html.slice(start,html.indexOf(';\n',start)));}
const bank=data('readingBank'),aliases=JSON.parse(fs.readFileSync('audit140/aliases.json','utf8')),sha256=require('node:crypto').createHash('sha256').update(html).digest('hex');
(async()=>{const browser=await chromium.launch({headless:true});try{
 const page=await browser.newPage({viewport:{width:412,height:915},acceptDownloads:true}),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(pathToFileURL(path.resolve('release140/JLPT_N1_ukrainian_reading_v140.html')).href);
 const pool=await page.evaluate(()=>{
  const result={eligible:0,guarded:0,canonicalAliases:0};
  for(const v of ACTIVE_VOCAB){const wrong=quizReadingOptions({kind:'v',id:v.id,word:v});if(wrong.length<3){result.guarded++;continue;}result.eligible++;
   if(new Set([v.r,...wrong]).size!==wrong.length+1)throw Error('duplicate '+v.id);
   const prefix=(v.w.match(/^[ぁ-ゟー]+/)||[''])[0],tail=(v.w.match(/[ぁ-ゟー]+$/)||[''])[0];
   for(const r of wrong)if(prefix&&!r.startsWith(prefix)||tail&&!r.endsWith(tail))throw Error('visible kana mismatch '+v.id);
  }
  for(const a of VOCAB_HEADWORD_ALIASES){const old={id:a.id,w:a.oldWord,r:a.oldReading,c:'legacy'},n=normalizeLegacyVocabRow(old);if(n.w!==a.word||n.r!==a.reading||n.id!==old.id)throw Error('alias '+a.id);result.canonicalAliases++;
   const modified={...old,r:'custom'};if(normalizeLegacyVocabRow(modified)!==modified)throw Error('custom modified');
  }
  if(normalizeLegacyVocabRow({id:999999,w:'顕著な',r:'けんちょな'}).w!=='顕著な')throw Error('foreign custom id altered');
  return result;
 });assert.equal(pool.eligible+pool.guarded,3914);assert.equal(pool.canonicalAliases,286);
 // Card data and actual DOM for every normalized header, including lexical な in 頑な/粉々.
 let cards=0;
 for(const a of aliases){
  const x=await page.evaluate(async id=>{showView('cards');await openCardDetail('v',String(id));return {title:document.querySelector('#cardDetailBody .fc-word').innerText,reading:document.querySelector('#cardDetailBody .fc-reading')?.innerText,text:document.getElementById('cardDetailBody').innerText,word:ACTIVE_VOCAB.find(x=>x.id===id).w,def:SmartEngine.getDefinition(ACTIVE_VOCAB.find(x=>x.id===id).w,'v',id)}},a.id);
  assert.equal(x.word,a.word);assert(x.title.includes(a.word));assert(!x.title.includes(a.oldWord));assert(x.text.includes(a.reading));assert(x.def.examples.length>=2);cards++;
 }
 // Import a real-format old customized built-in list; stable IDs retain current progress.
 const migration=await page.evaluate(aliases=>{
  state.vp['3112']={status:'X',lastSeen:1793790000000,timesShown:3,firstSeen:1793700000000};saveStorage();saveComparisonKeys(['v_3112','v_3005']);
  localStorage.setItem(VOCAB_DATA_KEY,JSON.stringify(aliases.map(a=>({...DEFAULT_VOCAB.find(v=>v.id===a.id),w:a.oldWord,r:a.oldReading}))));return state.vp['3112'];
 },aliases);
 await page.reload();assert.deepEqual(await page.evaluate(()=>state.vp['3112']),migration);assert.equal(await page.evaluate(()=>ACTIVE_VOCAB.find(x=>x.id===3112).w),'顕著');
 await page.evaluate(async()=>{showView('cards');await openCardDetail('v','3112')});assert((await page.locator('#cardDetailBody').innerText()).includes('けんちょ'));assert((await page.locator('#cardDetailBody').innerText()).includes('顕著な傾向'));
 await page.locator('.nav-tab[data-view="compare"]').click();assert((await page.locator('#view-compare').innerText()).includes('顕著'));
 await page.evaluate(()=>localStorage.removeItem(VOCAB_DATA_KEY));await page.reload();
 // Original screenshot regression: all choices preserve しい, exact spelling options, actual answer feedback.
 for(const width of [360,412,1280]){
  await page.setViewportSize({width,height:915});
  const p=await page.evaluate(()=>{
   const word=ACTIVE_VOCAB.find(x=>x.id===3005),it={kind:'v',id:3005,word},original=Math.random;let calls=0,p;
   Math.random=()=>calls++===0?0:calls===2?.99:.37;
   try{p=SmartEngine.generateOfflinePassage([it])[0]}finally{Math.random=original}
   curSession={items:[it],passages:[p],passageIdx:0,ratings:{},plan:null};showView('session');document.getElementById('sessBody').style.display='';renderPassage();return p;
  });const q=p.questions[0];assert(q.prompt.includes('読み方'));assert.equal(q.choices[q.answer],'いちじるしい');assert(q.choices.every(x=>x.endsWith('しい')));assert(!q.choices.includes('あらっぽい'));assert(!q.choices.includes('やっかいな'));
  await page.locator('#passageArea .qchoice').nth((q.answer+1)%4).click();assert.equal(await page.locator('#passageArea .qchoice.correct').count(),1);assert(await page.locator('#passageArea .qexplain').isVisible());
  if(width===412)await page.locator('#passageArea').screenshot({path:'/tmp/v140-reading.png'});
 }
 // Every authored reading and all 400 lexical notes use separate lexical/context fields.
 let readings=0,lexical=0,duplicateQuotes=0;
 await page.setViewportSize({width:412,height:915});
 for(const [level,items]of Object.entries(bank))for(const [index,r]of items.entries()){
  const mediumIndex=level==='medium'?index:0,longIndex=level==='long'?index:0,mediumQuestions=bank.medium[mediumIndex].questions.length;
  const out=await page.evaluate(({level,mediumIndex,longIndex,mediumQuestions,mediumLength,longLength})=>{
   const original=Math.random;let calls=0,ps;
   Math.random=()=>{const c=calls++;return c===0?(mediumIndex+.1)/mediumLength:c===1+mediumQuestions*3?(longIndex+.1)/longLength:.37};
   try{ps=SmartEngine.generateOfflinePassage([])}finally{Math.random=original}
   const p=ps.find(x=>x.level===level);curSession={items:[],passages:[p],passageIdx:0,ratings:{},plan:null};showView('session');document.getElementById('sessBody').style.display='';renderPassage();
   const gloss=[...document.querySelectorAll('.reading-glossary>div')].map(el=>({label:el.querySelector('b').textContent,quote:el.querySelector('[lang="ja"]')?.textContent||'',meaning:el.querySelector('span').textContent}));
   document.querySelectorAll('#passageArea .qcard').forEach(el=>el.querySelector('.qchoice').click());return {p,gloss,overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth};
  },{level,mediumIndex,longIndex,mediumQuestions,mediumLength:bank.medium.length,longLength:bank.long.length});
  assert.equal(out.p.plainText,r.ja);assert.equal(out.p.questions.length,r.questions.length);assert(out.overflow<=2);
  if(r.contextNotes){assert.equal(out.gloss.length,r.contextNotes.length);
   for(const n of r.contextNotes){const g=out.gloss.find(g=>g.label===n.label);assert(g);assert(g.quote!==g.label);if(n.quote===n.label){assert.equal(g.quote,'');duplicateQuotes++;}
    if(n.kind==='v'){lexical++;assert(g.meaning.startsWith(n.translation));if((n.context||n.meaning)!==n.translation)assert(g.meaning.includes('(тут — '+(n.context||n.meaning)+')'));}
   }
  }
  if(r.id==='m130-11'){const g=out.p.glossary.find(g=>g.label==='〜ばこそ');assert.equal(g.quote,'扱いがあればこそ');assert(out.p.plainText.includes(g.quote));await page.locator('#passageArea .reading-glossary').screenshot({path:'/tmp/v140-koso-glossary.png'});}
  if(r.id==='l131-06'){const g=out.gloss.find(g=>g.label==='判断');assert.equal(g.meaning,'висновок (тут — про походження висловлених почуттів)');await page.locator('#passageArea .reading-glossary').screenshot({path:'/tmp/v140-meaning-glossary.png'});}
  readings++;
 }
 assert.equal(readings,160);assert.equal(lexical,400);assert.deepEqual(errors,[]);
 fs.writeFileSync('audit140/browser-results.json',JSON.stringify({sha256,browser:browser.version(),pass:true,pool,normalizedCards:cards,readings,lexicalGlosses:lexical,hiddenDuplicateQuotes:duplicateQuotes,screenshotWidths:[360,412,1280],stableProgress:migration},null,2));console.log('PASS reading choices, 286 cards, legacy progress and all 160 readings / 400 lexical notes',pool);
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
