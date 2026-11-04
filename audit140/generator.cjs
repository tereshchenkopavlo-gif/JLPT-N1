const {chromium}=require('playwright'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{pathToFileURL}=require('node:url');
const html=fs.readFileSync('release140/JLPT_N1_ukrainian_reading_v140.html','utf8'),sha256=require('node:crypto').createHash('sha256').update(html).digest('hex');
const old=JSON.parse(fs.readFileSync('audit139/adjudications.json','utf8')).rows,prior=JSON.parse(fs.readFileSync('audit137/targets.json','utf8')),aliases=JSON.parse(fs.readFileSync('audit140/aliases.json','utf8'));
const map=new Map();for(const row of [...old,...prior,...aliases.flatMap(a=>[0,1].map(exampleIndex=>({kind:'v',id:a.id,exampleIndex})))])map.set(`${row.kind}:${row.id}:${row.exampleIndex}`,row);
(async()=>{const browser=await chromium.launch({headless:true});try{
const page=await browser.newPage({viewport:{width:412,height:915}}),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(pathToFileURL(path.resolve('release140/JLPT_N1_ukrainian_reading_v140.html')).href);
let cases=0;const types={meaning:0,reading:0,cloze:0},results=[];
for(const row of map.values())for(const fraction of [.01,.5,.99]){
 const x=await page.evaluate(({row,fraction})=>{
  const word=(row.kind==='v'?ACTIVE_VOCAB:GRAMMAR).find(x=>x.id===row.id),it={kind:row.kind,id:row.id,word},def=SmartEngine.getDefinition(word.w,row.kind,row.id),sentence=def.examples[row.exampleIndex];
  const original=Math.random;let calls=0,p;Math.random=()=>calls++===0?(row.exampleIndex+.1)/def.examples.length:calls===2?fraction:.37;
  try{p=SmartEngine.generateOfflinePassage([it])[0]}finally{Math.random=original}
  const q=p.questions[0],marked=SmartEngine.markTarget(sentence,it.kind,word.w);
  return {p,sentence,word,spans:[...marked.s.matchAll(/\u0001([^\u0002]*)\u0002/g)].map(m=>m[1]),pool:q?.prompt.includes('読み方')?quizReadingOptions(it):[]};
 },{row,fraction});
 const q=x.p.questions[0];assert(q);assert.equal(q.choices.length,4);assert.equal(new Set(q.choices).size,4);assert(q.answer>=0&&q.answer<4);assert(!q.prompt.includes('辞書形・基本形'));
 let type='meaning';
 if(q.prompt.includes('空欄')){type='cloze';assert.equal(row.kind,'v');assert.deepEqual(x.spans,[x.word.w]);assert.equal(q.choices[q.answer],x.word.w);assert.equal(x.p.text.replace(/<span class="blank">[^<]*<\/span>/g,x.word.w).replace(/<[^>]+>/g,''),x.sentence);}
 else{assert.equal(x.p.text.replace(/<[^>]+>/g,''),x.sentence);if(q.prompt.includes('読み方')){type='reading';assert.equal(q.choices[q.answer],x.word.r);assert(q.choices.every(c=>c===x.word.r||x.pool.includes(c)));}}
 types[type]++;cases++;results.push({kind:row.kind,id:row.id,index:row.exampleIndex,fraction,type,pass:true});
}
assert.deepEqual(errors,[]);fs.writeFileSync('audit140/generator-results.json',JSON.stringify({sha256,browser:browser.version(),pass:true,contexts:map.size,cases,types,results},null,2));console.log('PASS generator contexts/cases',map.size,cases,types);
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
