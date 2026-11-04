const {chromium}=require('playwright'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{pathToFileURL}=require('node:url');
const file='release141/JLPT_N1_ukrainian_reading_v141.html',sha256=require('node:crypto').createHash('sha256').update(fs.readFileSync(file)).digest('hex'),review=JSON.parse(fs.readFileSync('audit141/editorial-review.json','utf8'));
const contexts=review.rows.flatMap(row=>row.contexts.map(x=>({...x,key:row.key,kind:'v',id:Number(row.key.slice(2))})));
(async()=>{const browser=await chromium.launch({headless:true});try{
 const page=await browser.newPage({viewport:{width:412,height:915}}),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(pathToFileURL(path.resolve(file)).href);
 const g95=await page.evaluate(()=>GRAMMAR_DETAILS_BY_ID[95].examples.map((sentence,exampleIndex)=>({key:'g_95',kind:'g',id:95,sentence,exampleIndex,...REVIEWED_MEANING_QUIZZES.g_95})));contexts.push(...g95);
 const sourceIntegrity=await page.evaluate(()=>({savedKeys:Object.keys(REVIEWED_MEANING_QUIZZES),byExample:Object.values(REVIEWED_MEANING_QUIZZES).reduce((s,q)=>s+Object.keys(q.byExample||{}).length,0)}));assert.equal(sourceIntegrity.savedKeys.length,266);assert.equal(sourceIntegrity.byExample,156);
 const generated=await page.evaluate(contexts=>{
  const results=[];
  for(const row of contexts)for(let position=0;position<4;position++){
   const word=(row.kind==='v'?ACTIVE_VOCAB:GRAMMAR).find(x=>x.id===row.id),it={kind:row.kind,id:row.id,word};
   const random=Math.random,shuffler=shuffleArray;let calls=0,p;
   Math.random=()=>calls++===0?(row.exampleIndex+.1)/2:calls===2?0:.37;
   shuffleArray=a=>{if(a.length!==4||!a.includes(row.correct))return shuffler(a);const b=a.filter(x=>x!==row.correct);b.splice(position,0,row.correct);return b};
   try{p=SmartEngine.generateOfflinePassage([it])[0]}finally{Math.random=random;shuffleArray=shuffler}
   const q=p.questions[0];
   if(!q||q.prompt.includes('読み方')||q.prompt.includes('空欄'))throw Error('not meaning '+row.key);
   if(q.choices.length!==4||new Set(q.choices).size!==4||q.answer!==position||q.choices[q.answer]!==row.correct)throw Error('key/order '+row.key);
   if(q.choices.some(c=>c!==row.correct&&!row.wrong.includes(c)))throw Error('unreviewed option '+row.key);
   if(p.text.replace(/<[^>]+>/g,'')!==row.sentence)throw Error('wrong example '+row.key);
   if(row.note&&!q.explain.includes(row.note))throw Error('missing explanation '+row.key);
   const marked=SmartEngine.markTarget(row.sentence,row.kind,word.w);
   if(!marked.found)throw Error('unmarked '+row.key);
   results.push({key:row.key,index:row.exampleIndex,position,pass:true});
  }
  return results;
 },contexts);assert.equal(generated.length,2128);
 const guard=await page.evaluate(()=>{
  const ids=[2210,2399,3707,3718,3787,3836];
  return ids.map(id=>{const word=ACTIVE_VOCAB.find(v=>v.id===id),it={kind:'v',id,word},def=SmartEngine.getDefinition(word.w,'v',id);return {id,unknownNote:quizMeaningOptions(it,def,'未知の文脈で使われた語。').note,headwordNote:quizMeaningOptions(it,def,'').note}});
 });assert(guard.every(x=>x.unknownNote===''&&x.headwordNote));
 const rendered=[];
 for(const width of [360,412,1280]){
  await page.setViewportSize({width,height:915});
  for(const row of contexts){
   const x=await page.evaluate(row=>{
    const word=(row.kind==='v'?ACTIVE_VOCAB:GRAMMAR).find(x=>x.id===row.id),it={kind:row.kind,id:row.id,word},original=Math.random;let calls=0,p;
    Math.random=()=>calls++===0?(row.exampleIndex+.1)/2:calls===2?0:.37;
    try{p=SmartEngine.generateOfflinePassage([it])[0]}finally{Math.random=original}
    curSession={items:[it],passages:[p],passageIdx:0,ratings:{},plan:null};showView('session');document.getElementById('sessBody').style.display='';renderPassage();
    const q=p.questions[0],buttons=[...document.querySelectorAll('#passageArea .qchoice')];
    if(buttons.length!==4)throw Error('choices DOM '+row.key);
    buttons[(q.answer+1)%4].click();
    const explain=document.querySelector('#passageArea .qexplain');
    return {correct:document.querySelectorAll('#passageArea .qchoice.correct').length,wrong:document.querySelectorAll('#passageArea .qchoice.wrong').length,feedback:explain?.textContent,visible:explain&&getComputedStyle(explain).display!=='none',overflow:document.documentElement.scrollWidth>innerWidth+1};
   },row);
   assert.equal(x.correct,1,row.key);assert.equal(x.wrong,1,row.key);assert(x.visible,row.key);if(row.note)assert(x.feedback.includes(row.note),row.key);assert(!x.overflow,`${width} ${row.key}`);
   rendered.push({key:row.key,index:row.exampleIndex,width,pass:true});
   if(width===412&&row.exampleIndex===1&&[2210,3718,3836].includes(row.id))await page.locator('#passageArea').screenshot({path:`/tmp/v141-${row.id}.png`});
  }
 }
 assert.equal(rendered.length,1596);assert.deepEqual(errors,[]);
 fs.writeFileSync('audit141/meaning-results.json',JSON.stringify({sha256,browser:browser.version(),pass:true,vocabularySets:265,vocabularyContexts:530,additionalGrammarContexts:2,runtimeSets:266,exampleOverrides:156,generationCases:generated.length,renderedCases:rendered.length,unknownContextGuard:guard,generated,rendered,errors},null,2)+'\n');
 console.log('PASS 265 saved sets +g95;',generated.length,'generation cases;',rendered.length,'actual DOM/wrong-answer feedback cases');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
