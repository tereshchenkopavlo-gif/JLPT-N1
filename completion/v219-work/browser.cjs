const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
const {pathToFileURL}=require('node:url'),HTML='JLPT_N1_ukrainian_reading_v219.html',WORK='completion/v219-work';
const prepare=JSON.parse(fs.readFileSync(path.join(WORK,'prepare-results.json'),'utf8'));
const IDS=[3277,3280,3281,3293,3296,3312,3319,3321,3323,3325,3336,3337];
const EXPECTED={
'3277':{word:'さぞや',reading:'さぞや',pos:['副詞']},
'3280':{word:'さも',reading:'さも',pos:['副詞']},
'3281':{word:'しいて',reading:'しいて',pos:['副詞'],gloss:'через силу; попри небажання; якщо вже неодмінно треба щось назвати'},
'3293':{word:'どうにか',reading:'どうにか',pos:['副詞'],gloss:'якось; більш-менш; насилу',translation:'Проблеми з обігом коштів якось вдалося подолати, але подальші перспективи неясні.'},
'3296':{word:'どうやら',reading:'どうやら',pos:['副詞'],usage:'У сучасному вживанні має й окреме значення'},
'3312':{word:'よくも',reading:'よくも',pos:['副詞'],translation:'Як він міг зрадити тих, хто стільки для нього зробив!'},
'3319':{word:'極力',reading:'きょくりょく',pos:['副詞'],translation:'Наскільки можливо, уникайте ручного введення персональних даних.'},
'3321':{word:'安静に',reading:'あんせいに',pos:['副詞'],translation:'Лікар наказав протягом тижня дотримуватися фізичного спокою.'},
'3323':{word:'案の定',reading:'あんのじょう',pos:['副詞'],example:'午後から空が暗くなり始め、案の定、夕方には雨が降り出した。',translation:'Удень небо почало темніти, і, як і очікувалося, надвечір пішов дощ.'},
'3325':{word:'依然',reading:'いぜん',pos:['副詞'],example:'事故原因の究明は依然として難航している。',translation:'З’ясування причин аварії й досі просувається важко.'},
'3336':{word:'まして',reading:'まして',pos:['副詞'],usage:'для ще виразнішого або складнішого випадку B'},
'3337':{word:'一切',reading:'いっさい',pos:['副詞'],usage:'費用の一切'}
};
(async()=>{
 const bytes=fs.readFileSync(HTML),sha=crypto.createHash('sha256').update(bytes).digest('hex');assert.equal(sha,prepare.candidate_sha256);assert.equal(bytes.length,prepare.candidate_bytes);
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:412,height:900}}),errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(pathToFileURL(path.resolve(HTML)).href);
  const structural=await page.evaluate(()=>({vocab:DEFAULT_VOCAB.length,grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,pairs:VOCAB_AUDITED_PAIRS.length,uniqueIds:new Set(DEFAULT_VOCAB.map(x=>Number(x.id))).size,allIdsPresent:DEFAULT_VOCAB.every(x=>VOCAB_DETAILS_BY_ID[String(x.id)]&&VOCAB_POS_BY_ID[String(x.id)])}));
  assert.deepEqual(structural,{vocab:3914,grammar:130,pairs:859,uniqueIds:3914,allIdsPresent:true});
  const data=await page.evaluate(ids=>ids.map(id=>{const v=DEFAULT_VOCAB.find(x=>Number(x.id)===id),d=VOCAB_DETAILS_BY_ID[String(id)];return{id,word:d.w,reading:v.r,pos:VOCAB_POS_BY_ID[String(id)],gloss:d.t,definition:d.m,translations:d.exampleTranslations,examples:d.examples,usage:d.usage};}),IDS);
  for(const c of data){const e=EXPECTED[String(c.id)];assert.equal(c.word,e.word);assert.equal(c.reading,e.reading);assert.deepEqual(c.pos,e.pos);assert.ok(c.usage&&c.usage.length>0);if(e.gloss)assert.equal(c.gloss,e.gloss);if(e.usage)assert.ok(c.usage.includes(e.usage));if(e.translation)assert.ok(c.translations.includes(e.translation));if(e.example)assert.ok(c.examples.includes(e.example));assert.equal(c.examples.length,2);assert.equal(c.translations.length,2);}
  const pairCheck=await page.evaluate(()=>({count:VOCAB_AUDITED_PAIRS.length,note:VOCAB_AUDITED_PAIRS[752].note,expectedA:VOCAB_AUDITED_PAIRS[752].a,expectedB:VOCAB_AUDITED_PAIRS[752].b}));
  assert.equal(pairCheck.expectedA,'3293');assert.equal(pairCheck.expectedB,'3296');assert.ok(pairCheck.note.includes('У сучасному вживанні'));
  const rendered=await page.evaluate(async ids=>{showView('cards');const out=[];const n=x=>String(x).replaceAll('\n',' ').replaceAll('\r',' ').replaceAll('\t',' ').split(' ').filter(Boolean).join(' ');for(const id of ids){await openCardDetail('v',id);await new Promise(r=>setTimeout(r,35));const body=document.getElementById('cardDetailBody'),txt=body?.innerText||'',d=VOCAB_DETAILS_BY_ID[String(id)];out.push({id,word:d.w,titleVisible:n(txt).includes(n(d.w)),definitionVisible:n(txt).includes(n(d.m)),usageVisible:!!d.usage&&n(txt).includes('用法・接続'),translationsVisible:d.exampleTranslations.every(x=>!x||n(txt).includes(n(x))),examplesVisible:d.examples.every(x=>!x||n(txt).includes(n(x))),textExcerpt:n(txt).slice(0,300)});}return out;},IDS);
  fs.writeFileSync(path.join(WORK,'rendered-debug.json'),JSON.stringify(rendered,null,2)+'\n');
  const failures=rendered.filter(x=>!(x.titleVisible&&x.definitionVisible&&x.usageVisible&&x.translationsVisible&&x.examplesVisible));assert.equal(rendered.length,12);if(failures.length)throw Error(JSON.stringify(failures));
  const responsive=[];for(const width of [360,412,1280]){await page.setViewportSize({width,height:900});const d=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth}));responsive.push({...d,overflow:d.scrollWidth>width||d.bodyWidth>width});}assert.ok(responsive.every(x=>!x.overflow));
  const storage=await page.evaluate(()=>{const key='choba_n1uk_storage_v1',old=localStorage.getItem(key),sentinel=JSON.stringify({meta:{sessionSize:10,streak:5,lastStudyDate:'2026-11-14'},vp:{'3277':{status:'S',timesShown:2}},gp:{'90':{status:'X'}}});localStorage.setItem(key,sentinel);const roundTrip=localStorage.getItem(key)===sentinel;if(old===null)localStorage.removeItem(key);else localStorage.setItem(key,old);return{roundTrip,restored:localStorage.getItem(key)===old};});assert.ok(storage.roundTrip&&storage.restored);assert.deepEqual(errors,[]);
  const result={pass:true,candidate_sha256:sha,candidate_bytes:bytes.length,counts:structural,reviewed_card_count:12,fixed_rechecked_count:9,reviewed_unchanged_count:2,blocked_count:1,pair_reviewed_count:7,pair_changed_count:1,responsive,storage,pageErrors:errors};
  fs.writeFileSync(path.join(WORK,'browser-results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
