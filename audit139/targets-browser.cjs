const {chromium}=require('playwright'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const html=fs.readFileSync('release139/JLPT_N1_ukrainian_reading_v139.html','utf8');
const exact=JSON.parse(html.match(/const REVIEWED_EXAMPLE_TARGETS = (.*?);\n/)[1]);
const reviewed=JSON.parse(fs.readFileSync('audit139/adjudications.json','utf8')).rows;
const key=r=>`${r.kind}_${r.id}_${r.exampleIndex}`;
const rows=[...exact,...reviewed.filter(r=>!exact.some(e=>key(r)===key(e))).map(r=>({...r,sentence:r.sentenceNow||r.sentence}))];
assert.equal(rows.length,556);
(async()=>{const browser=await chromium.launch({headless:true});const results=[];let renders=0;try{
for(const width of [360,412,1280]){
 const page=await browser.newPage({viewport:{width,height:920}}),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(pathToFileURL(path.resolve('release139/JLPT_N1_ukrainian_reading_v139.html')).href);
 for(const row of rows){
  const render=width===412||exact.some(e=>key(row)===key(e));
  for(const fraction of [.01,.5,.99]){
   const generated=await page.evaluate(({row,fraction,render})=>{
    const word=(row.kind==='v'?ACTIVE_VOCAB:GRAMMAR).find(x=>x.id===row.id),it={kind:row.kind,id:row.id,word};
    const def=SmartEngine.getDefinition(word.w,row.kind,row.id),usable=def.examples.filter(s=>SmartEngine.markTarget(s,row.kind,word.w).found),index=usable.indexOf(row.sentence);
    if(index<0)throw Error('Example unavailable '+row.word);
    const original=Math.random;let calls=0,passage;
    Math.random=()=>calls++===0?(index+.1)/usable.length:calls===2?fraction:.37;
    try{passage=SmartEngine.generateOfflinePassage([it]).find(x=>x.level==='short')}finally{Math.random=original}
    if(fraction===.01&&render){
     curSession={items:[it],passages:[passage],passageIdx:0,ratings:{},plan:null};showView('session');
     for(const id of ['teachBody','sessDone','sessLoading','sessError'])document.getElementById(id).style.display='none';document.getElementById('sessBody').style.display='';renderPassage();
    }
    return {passage,label:word.w,reading:word.r};
   },{row,fraction,render});
   const {passage,label,reading}=generated;
   assert.equal(passage.questions.length,1);const q=passage.questions[0];assert.equal(q.choices.length,4);assert.equal(new Set(q.choices).size,4);assert(q.explain.length>label.length+2);
   const isExact=exact.some(e=>key(row)===key(e));
   if(isExact)assert(!passage.text.includes('class="blank"'),'no inflected surface presented as dictionary-form cloze');
   if(!passage.text.includes('class="blank"'))assert.equal(passage.text.replace(/<[^>]*>/g,''),row.sentence);
   if(q.prompt.includes('読み方')){assert.equal(q.choices[q.answer],reading);assert(q.prompt.includes('見出し語'));}
   else if(q.prompt.includes('空欄'))assert.equal(q.choices[q.answer],label);
   else if(row.quiz){assert.equal(q.choices[q.answer],row.quiz.correct);assert(q.explain.includes(row.quiz.note));}
   if(fraction===.01&&render){
    const bold=await page.locator('#passageArea .psent b').allTextContents();assert.deepEqual(bold,row.forms);
    const card=page.locator('#passageArea .qcard');assert.equal(await card.count(),1);
    await card.locator('.qchoice').nth((q.answer+1)%4).click();assert.equal(await card.locator('.qchoice.correct').count(),1);assert.equal(await card.locator('.qchoice.wrong').count(),1);assert(await card.locator('.qexplain').isVisible());
    if(row.quiz)assert((await card.locator('.qexplain').innerText()).includes(row.quiz.note));
    assert(await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth)<=2);
    if(width===412&&((row.kind==='g'&&row.id===125)||(row.kind==='v'&&[519,716,790].includes(row.id))))await page.locator('#passageArea').screenshot({path:`/tmp/v139-${row.kind}-${row.id}-${row.exampleIndex}.png`});
    renders++;
   }
   results.push({width,kind:row.kind,id:row.id,exampleIndex:row.exampleIndex,fraction,type:q.prompt.includes('読み方')?'reading':q.prompt.includes('空欄')?'cloze':'meaning',correct:q.choices[q.answer],pass:true});
  }
 }
 assert.deepEqual(errors,[]);await page.close();console.log('Completed width '+width);
}
fs.writeFileSync('audit139/targets-browser-results.json',JSON.stringify({sha256:require('node:crypto').createHash('sha256').update(html).digest('hex'),browser:browser.version(),renderings:renders,generatorCases:results.length,results},null,2));console.log(`PASS ${results.length} generator cases, ${renders} renderings`);
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
