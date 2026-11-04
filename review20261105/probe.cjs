// Read-only snapshot: execute the published app, never rewrite its data or storage.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const {chromium}=require('playwright'),{pathToFileURL}=require('node:url');
const file='JLPT_N1_ukrainian_reading_v141.html',sha256=crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
assert.equal(sha256,'08e016a95f1786f243c29f54289edf5dd65aac4c43c9ff863b25c9f0422f75a3');
(async()=>{const browser=await chromium.launch({headless:true});try{
 const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(pathToFileURL(path.resolve(file)).href);
 const readings=await page.evaluate(()=>ACTIVE_VOCAB.map(v=>{
  const candidates=quizReadingOptions({kind:'v',id:v.id,word:v});
  let reason='eligible';
  if(candidates.length<3){
   if(!v.r||!/^[ぁ-ゟー]+$/.test(v.r))reason='reading_not_single_hiragana';
   else if(!/[一-鿿]/.test(v.w))reason='no_hidden_kanji';
   else if(/[〜～・／/]/.test(v.w))reason='marked_or_multiple_headword';
   else{
    const prefix=(v.w.match(/^[ぁ-ゟー]+/)||[''])[0],tail=(v.w.match(/[ぁ-ゟー]+$/)||[''])[0];
    reason=(prefix&&!v.r.startsWith(prefix)||tail&&!v.r.endsWith(tail))?'visible_kana_mismatch':'fewer_than_three_filtered_candidates';
   }
  }
  return {id:v.id,word:v.w,reading:v.r,pos:vocabPartOfSpeech(v.id),candidateCount:candidates.length,reason};
 }));
 assert.equal(readings.length,3914);assert.equal(readings.filter(x=>x.reason!=='eligible').length,1482);
 const grammar=await page.evaluate(()=>GRAMMAR.map(word=>{
  const it={kind:'g',id:word.id,word},def=SmartEngine.getDefinition(word.w,'g',word.id),sentence=def.examples[0],random=Math.random;let calls=0,seed=20261105,p;
  Math.random=()=>{calls++;if(calls<=2)return 0;seed=(1664525*seed+1013904223)>>>0;return seed/4294967296};
  try{p=SmartEngine.generateOfflinePassage([it])[0]}finally{Math.random=random}
  const q=p.questions[0];if(!q||q.choices.length!==4||new Set(q.choices).size!==4||!q.prompt.includes('意味'))throw Error('malformed '+word.id);
  const exact=reviewedExampleTarget(sentence,'g',word.w)?.quiz,saved=REVIEWED_MEANING_QUIZZES['g_'+word.id];
  return {id:word.id,word:word.w,exampleIndex:0,sentence,prompt:q.prompt,choices:q.choices,answer:q.answer,correct:q.choices[q.answer],explain:q.explain,route:exact?'exact_example':saved?'saved_set':'automatic',targetFound:SmartEngine.markTarget(sentence,'g',word.w).found};
 }));assert.equal(grammar.length,130);assert.deepEqual(errors,[]);
 const out={date:'2026-11-05',baseCommit:'571aa092d256e682ad16873b7462dcc263cf62d8',sha256,browser:browser.version(),seed:20261105,scope:'Read-only technical snapshot. Semantic decisions are separate; no runtime or learning mechanism changed.',readingEligibility:{eligible:2432,guarded:1482,rows:readings},grammarCases:grammar,errors};
 fs.writeFileSync('review20261105/probe.json',JSON.stringify(out,null,2)+'\n');console.log('Snapshot: 3914 reading pools /1482 guarded; 130 fixed grammar meaning cases; no runtime writes');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
