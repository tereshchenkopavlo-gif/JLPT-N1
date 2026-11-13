const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const base='JLPT_N1_ukrainian_reading_v178.html',file='JLPT_N1_ukrainian_reading_v179.html';
const updates=JSON.parse(fs.readFileSync('completion/v179-work/updates.json','utf8'));
async function open(browser,name,width=1280){
 const page=await browser.newPage({viewport:{width,height:915}}),errors=[];
 page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(pathToFileURL(path.resolve(name)).href);
 return {page,errors};
}
async function main(){
 const browser=await chromium.launch({headless:true});
 const result={pass:false,sha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),cardsChecked:[2433,2468],contextPayloadsChecked:2,widths:[]};
 try{
  const a=await open(browser,base),b=await open(browser,file);
  assert.deepEqual(a.errors,[]);assert.deepEqual(b.errors,[]);
  const snapshot=page=>page.evaluate(()=>({vocab:DEFAULT_VOCAB.length,details:Object.keys(VOCAB_DETAILS_BY_ID).length,grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,pairs:VOCAB_AUDITED_PAIRS.length,ids:DEFAULT_VOCAB.map(x=>x.id),pos:JSON.parse(JSON.stringify(VOCAB_POS_BY_ID)),reading:JSON.parse(JSON.stringify(REVIEWED_READING_OPTIONS)),meaning:JSON.parse(JSON.stringify(REVIEWED_MEANING_QUIZZES)),targets:JSON.parse(JSON.stringify(REVIEWED_EXAMPLE_TARGETS))}));
  const before=await snapshot(a.page),after=await snapshot(b.page);
  assert.equal(before.vocab,3914);assert.equal(after.vocab,3914);assert.equal(after.details,3914);assert.equal(after.grammar,130);assert.equal(after.pairs,859);
  assert.deepEqual(after.ids,before.ids);assert.deepEqual(after.pos,before.pos);assert.deepEqual(after.reading,before.reading);assert.deepEqual(after.meaning,before.meaning);
  const strip=rows=>rows.map(r=>{const x={...r};if(x.id===2468&&x.word==='下す'&&updates.some(u=>u.sentence===x.sentence))delete x.quiz;return x;});
  assert.deepEqual(strip(after.targets),strip(before.targets));
  const tested=await b.page.evaluate(updates=>{
   const getQuiz=(id,sentence,rv=0)=>{const old=Math.random;Math.random=()=>rv;try{const word=DEFAULT_VOCAB.find(x=>x.id===id),item={kind:'v',id,word},def=SmartEngine.getDefinition(word.w,'v',id);return quizMeaningOptions(item,def,sentence);}finally{Math.random=old;}};
   const rows=updates.map(u=>{const q=getQuiz(u.id,u.sentence,0.25),marked=SmartEngine.markTarget(u.sentence,'v',u.word),spans=[...marked.s.matchAll(/\u0001([^\u0002]*)\u0002/g)].map(m=>m[1]);return {id:u.id,exampleIndex:u.exampleIndex,sentence:u.sentence,quiz:q,marked:marked.found,spans};});
   const auto2433=VOCAB_DETAILS_BY_ID['2433'].examples.map(sentence=>getQuiz(2433,sentence,0));
   const metrics=[2433,2468].map(id=>{const word=DEFAULT_VOCAB.find(x=>x.id===id),item={kind:'v',id,word};return {id,readingOptions:quizReadingOptions(item),clozeCount:clozeWordCandidates(item).length,clozeExamples:VOCAB_DETAILS_BY_ID[id].examples.map(sentence=>literalClozeAvailable(sentence,item,SmartEngine)),rendered:renderCardShell('v',id,VOCAB_DETAILS_BY_ID[id]).length>0};});
   localStorage.setItem('choba_n1uk_storage_v1','v179-progress-sentinel');
   return {rows,auto2433,metrics,progressStorageUnchanged:localStorage.getItem('choba_n1uk_storage_v1')==='v179-progress-sentinel'};
  },updates);
  assert.equal(tested.rows.length,2);
  for(const row of tested.rows){assert.equal(row.marked,true);assert.deepEqual(row.spans,['下した']);assert.equal(row.quiz.wrong.length,3);assert.equal(new Set([row.quiz.correct,...row.quiz.wrong]).size,4);}
  const autoBefore=await a.page.evaluate(()=>{
   const old=Math.random;Math.random=()=>0;
   try{return VOCAB_DETAILS_BY_ID['2433'].examples.map(sentence=>{const word=DEFAULT_VOCAB.find(x=>x.id===2433),item={kind:'v',id:2433,word},def=SmartEngine.getDefinition(word.w,'v',2433);return quizMeaningOptions(item,def,sentence);});}
   finally{Math.random=old;}
  });
  assert.deepEqual(tested.auto2433,autoBefore);
  for(const width of [360,412,1280]){
   const p=await open(browser,file,width);
   const check=await p.page.evaluate(()=>[2433,2468].map(id=>{const d=VOCAB_DETAILS_BY_ID[id],shell=renderCardShell('v',id,d),wrap=document.createElement('div');wrap.innerHTML=shell;const ex=vocabExamplesHtml(id,d.examples);return {id,cardRendered:wrap.textContent.includes(d.w),examplesRendered:d.exampleTranslations.every(t=>ex.includes(t))};}));
   assert.deepEqual(p.errors,[]);assert(check.every(x=>x.cardRendered&&x.examplesRendered),JSON.stringify(check));
   result.widths.push({width,pass:true,cards:check});await p.page.close();
  }
  result.contextResults=tested.rows;result.automatic2433=tested.auto2433;result.cards=tested.metrics;result.progressStorageUnchanged=tested.progressStorageUnchanged;
  result.counts={vocabulary:3914,grammar:130,lexicalPairs:859};result.pass=true;
  fs.writeFileSync('completion/v179-work/browser-results.json',JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify(result,null,2));
 }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
