// Technical route/eligibility ledger. This does not accept the semantics of automatic alternatives.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict'),{chromium}=require('playwright'),{pathToFileURL}=require('node:url');
const file='release148/JLPT_N1_ukrainian_reading_v148.html',sha256=crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
(async()=>{const b=await chromium.launch();try{const p=await b.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(pathToFileURL(path.resolve(file)).href);
const data=await p.evaluate(()=>{
 const reading=ACTIVE_VOCAB.map(word=>({id:word.id,candidateCount:quizReadingOptions({kind:'v',id:word.id,word}).length}));
 const grammar=GRAMMAR.map(word=>{
  const def=SmartEngine.getDefinition(word.w,'g',word.id),sentence=def.examples[0],original=Math.random;let calls=0,seed=20261105,passage;
  Math.random=()=>{if(++calls<=2)return 0;seed=(1664525*seed+1013904223)>>>0;return seed/4294967296};
  try{passage=SmartEngine.generateOfflinePassage([{kind:'g',id:word.id,word}])[0]}finally{Math.random=original}
  const q=passage.questions[0],exact=reviewedExampleTarget(sentence,'g',word.w)?.quiz,entry=REVIEWED_MEANING_QUIZZES['g_'+word.id],expected=exact||entry?.byExample?.[sentence]||entry;
  if(q.choices.length!==4||new Set(q.choices).size!==4||!q.prompt.includes('意味')||passage.text.replace(/<[^>]+>/g,'')!==sentence)throw Error('Malformed '+word.id);
  if(expected&&(q.choices[q.answer]!==expected.correct||q.choices.some(x=>x!==expected.correct&&!expected.wrong.includes(x))))throw Error('Wrong source '+word.id);
  return{id:word.id,route:exact?'exact_reviewed':entry?'saved_set':'automatic',targetFound:SmartEngine.markTarget(sentence,'g',word.w).found,choices:q.choices,correct:q.choices[q.answer]};
 });return{reading,grammar};
});
const guarded=data.reading.filter(x=>x.candidateCount<3),csv=fs.readFileSync('review20261105/reading-guarded.csv','utf8').trim().split(/\r?\n/).slice(1).map(x=>{const p=x.split(',');return{id:+p[0],candidateCount:+p[3]}});assert.deepEqual(guarded,csv);assert.equal(data.reading.length,3914);assert.equal(guarded.length,1482);
const automatic=data.grammar.filter(x=>x.route==='automatic').map(x=>x.id),exact=data.grammar.filter(x=>x.route==='exact_reviewed').map(x=>x.id),saved=data.grammar.filter(x=>x.route==='saved_set').map(x=>x.id);assert.equal(automatic.length,0);assert.equal(exact.length,16);assert.equal(saved.length,114);assert(data.grammar.every(x=>x.targetFound));assert.deepEqual(errors,[]);
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
fs.writeFileSync('audit148/scope-results.json',JSON.stringify({sha256,browser:b.version(),pass:true,scope:'Technical route and reading eligibility only; not independent semantic acceptance.',firstGrammarCases:130,automaticGrammarIds:automatic,exactReviewedFirstIds:exact,savedFirstIds:saved,exactFirstOrigins:{C04:11,C05:5},readingPools:3914,eligibleReadingPools:2432,guardedReadingPools:1482,guardedIdsAndCandidateCountsUnchanged:true,cases:data.grammar.map(({choices,correct,...x})=>({...x,choiceSha256:choices.map(hash),correctSha256:hash(correct)})),errors},null,2)+'\n');console.log('PASS 130 first-example routes: 114 saved /16 exact reviewed /0 automatic; unchanged 1482 reading guards');
}finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
