const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict'),{chromium}=require('playwright'),{pathToFileURL}=require('node:url');
const file='release147/JLPT_N1_ukrainian_reading_v147.html',sha256=crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),catalog=JSON.parse(fs.readFileSync('audit147/grammar-coverage.json'));assert.equal(catalog.sha256,sha256);
(async()=>{const b=await chromium.launch();try{const p=await b.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(pathToFileURL(path.resolve(file)).href);
const actual=await p.evaluate(()=>GRAMMAR.flatMap(word=>GRAMMAR_DETAILS_BY_ID[word.id].examples.map((sentence,exampleIndex)=>{
 const exact=reviewedExampleTarget(sentence,'g',word.w)?.quiz,entry=REVIEWED_MEANING_QUIZZES['g_'+word.id],payload=exact||entry?.byExample?.[sentence]||entry;if(!payload)throw Error('automatic context '+word.id+':'+exampleIndex);
 const it={kind:'g',id:word.id,word},def=SmartEngine.getDefinition(word.w,'g',word.id),q=quizMeaningOptions(it,def,sentence);
 if(q.correct!==payload.correct||JSON.stringify(q.wrong)!==JSON.stringify(payload.wrong)||q.note!==payload.note)throw Error('route payload mismatch '+word.id);
 return{id:word.id,exampleIndex,sentence,route:exact?'exact_reviewed':'saved_set',payload:{correct:q.correct,note:q.note,wrong:q.wrong}};
})));
const hash=s=>crypto.createHash('sha256').update(s).digest('hex'),results=[];assert.equal(actual.length,261);
for(const row of actual){const e=catalog.rows.find(x=>x.id===row.id&&x.exampleIndex===row.exampleIndex);assert(e);assert.equal(e.route,row.route);assert.equal(e.sentenceSha256,hash(row.sentence));assert.equal(e.payloadSha256,hash(JSON.stringify(row.payload)));results.push({id:row.id,exampleIndex:row.exampleIndex,route:row.route,pass:true})}
assert.equal(new Set(actual.map(x=>x.id)).size,130);assert.equal(results.filter(x=>x.route==='exact_reviewed').length,37);assert.deepEqual(errors,[]);
fs.writeFileSync('audit147/coverage-results.json',JSON.stringify({sha256,browser:b.version(),pass:true,grammarCards:130,grammarContexts:261,savedContexts:224,exactContexts:37,exactOrigins:{C04:27,C05:10},automaticCurrentContexts:0,scope:'Technical hash/route match to consolidated author decisions, not independent language acceptance.',results,errors},null,2)+'\n');console.log('PASS consolidated author evidence matches all 261 actual grammar contexts; 0 automatic /37 exact /224 saved');
}finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
