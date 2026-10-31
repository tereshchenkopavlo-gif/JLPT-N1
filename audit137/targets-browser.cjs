const {chromium}=require('playwright'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const html=fs.readFileSync('release137/JLPT_N1_ukrainian_reading_v137.html','utf8'),rows=JSON.parse(fs.readFileSync('audit137/targets.json','utf8'));
(async()=>{const browser=await chromium.launch({headless:true});const results=[];try{
for(const width of [360,412,1280]){
 const page=await browser.newPage({viewport:{width,height:920}}),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(pathToFileURL(path.resolve('release137/JLPT_N1_ukrainian_reading_v137.html')).href);
 for(const row of rows){
  for(const fraction of [.01,.5,.99]){
   const generated=await page.evaluate(({row,fraction})=>{
    const word=(row.kind==='v'?ACTIVE_VOCAB:GRAMMAR).find(x=>x.id===row.id),it={kind:row.kind,id:row.id,word};
    const def=SmartEngine.getDefinition(word.w,row.kind,row.id),usable=def.examples.filter(s=>SmartEngine.markTarget(s,row.kind,word.w).found),index=usable.indexOf(row.sentence);
    if(index<0)throw Error('Example unavailable '+row.word);
    const original=Math.random;let calls=0,passage;
    Math.random=()=>calls++===0?(index+.1)/usable.length:calls===2?fraction:.37;
    try{passage=SmartEngine.generateOfflinePassage([it]).find(x=>x.level==='short')}finally{Math.random=original}
    if(fraction===.01){
     curSession={items:[it],passages:[passage],passageIdx:0,ratings:{},plan:null};showView('session');
     for(const id of ['teachBody','sessDone','sessLoading','sessError'])document.getElementById(id).style.display='none';document.getElementById('sessBody').style.display='';renderPassage();
    }
    return passage;
   },{row,fraction});
   assert.equal(generated.questions.length,1);const q=generated.questions[0];assert.equal(q.choices.length,4);assert.equal(new Set(q.choices).size,4);
   assert(!generated.text.includes('class="blank"'),'no inflected form presented as literal dictionary-form cloze');
   assert.equal(generated.text.replace(/<[^>]*>/g,''),row.sentence);
   if(row.kind==='g'||row.id===447||fraction===.01){assert.equal(q.choices[q.answer],row.quiz.correct);assert(q.explain.includes(row.quiz.note));}
   else{assert.equal(q.choices[q.answer],'しんぽ');assert(q.prompt.includes('読み方'));}
   if(fraction===.01){
    const bold=await page.locator('#passageArea .psent b').allTextContents();assert.deepEqual(bold,row.forms);
    const card=page.locator('#passageArea .qcard');assert.equal(await card.count(),1);
    await card.locator('.qchoice').nth((q.answer+1)%4).click();assert.equal(await card.locator('.qchoice.correct').count(),1);assert.equal(await card.locator('.qchoice.wrong').count(),1);assert((await card.locator('.qexplain').innerText()).includes(row.quiz.note));
    assert(await card.locator('.qexplain').isVisible());
    const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);assert(overflow<=2);
    if(width===412&&((row.kind==='g'&&row.id===18)||(row.kind==='v'&&row.id===447&&row.exampleIndex===1)))await page.locator('#passageArea').screenshot({path:`/tmp/v137-${row.kind}-${row.id}-${row.exampleIndex}.png`});
   }
   results.push({width,kind:row.kind,id:row.id,exampleIndex:row.exampleIndex,fraction,correct:q.choices[q.answer],pass:true});
  }
 }
 assert.deepEqual(errors,[]);await page.close();
}
fs.writeFileSync('audit137/targets-browser-results.json',JSON.stringify({sha256:require('node:crypto').createHash('sha256').update(html).digest('hex'),browser:browser.version(),renderings:90,generatorCases:results.length,results},null,2));console.log('PASS 30 exact examples at 3 widths: 90 rendered questions and 270 generator cases');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
