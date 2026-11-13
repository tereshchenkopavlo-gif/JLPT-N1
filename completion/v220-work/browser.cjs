const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
const {pathToFileURL}=require('node:url'),HTML='JLPT_N1_ukrainian_reading_v220.html',WORK='completion/v220-work';
const prepare=JSON.parse(fs.readFileSync(path.join(WORK,'prepare-results.json'),'utf8'));
const IDS=[3344,3345,3349,3352,3357,3360,3363,3364,3368,3369,3370,3373];
const EXPECTED={
'3344':{word:'今や',reading:'いまや',pos:['副詞'],gloss:'нині, тепер уже; на цьому етапі',translation:'Нині суспільство суворо вимагає від компаній соціальної відповідальності.'},
'3345':{word:'散々',reading:'さんざん',pos:['副詞'],blocked:true,example:'天候に恵まれず、散々な結果に終わった遠征だった。'},
'3349':{word:'若干',reading:'じゃっかん',pos:['副詞'],example:'計画には若干修正が必要になるかもしれない。',translation:'Можливо, план доведеться трохи скоригувати.'},
'3352':{word:'所詮',reading:'しょせん',pos:['副詞']},
'3357':{word:'真っ二つに',reading:'まっぷたつに',pos:['副詞']},
'3360':{word:'先立って',reading:'さきだって',pos:['副詞']},
'3363':{word:'相当',reading:'そうとう',pos:['副詞'],blocked:true,example:'この計画の実現には、相当な時間を要するだろう。'},
'3364':{word:'相変わらず',reading:'あいかわらず',pos:['副詞'],example:'海外市場の需要は、相変わらず低迷している。'},
'3368':{word:'大して',reading:'たいして',pos:['副詞']},
'3369':{word:'大概',reading:'たいがい',pos:['副詞'],example:'彼は大概、約束の時間に遅れてくる。',translation:'Він зазвичай запізнюється на домовлений час.'},
'3370':{word:'大方',reading:'おおかた',pos:['副詞'],example:'この問題の原因は、大方解明された。',translation:'Причини цієї проблеми здебільшого з’ясовано.'},
'3373':{word:'中途半端に',reading:'ちゅうとはんぱに',pos:['副詞']}
};
(async()=>{
 const bytes=fs.readFileSync(HTML),sha=crypto.createHash('sha256').update(bytes).digest('hex');assert.equal(sha,prepare.candidate_sha256);assert.equal(bytes.length,prepare.candidate_bytes);
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:412,height:900}}),errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(pathToFileURL(path.resolve(HTML)).href);
  const structural=await page.evaluate(()=>({vocab:DEFAULT_VOCAB.length,grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,pairs:VOCAB_AUDITED_PAIRS.length,uniqueIds:new Set(DEFAULT_VOCAB.map(x=>Number(x.id))).size,allIdsPresent:DEFAULT_VOCAB.every(x=>VOCAB_DETAILS_BY_ID[String(x.id)]&&VOCAB_POS_BY_ID[String(x.id)])}));
  assert.deepEqual(structural,{vocab:3914,grammar:130,pairs:859,uniqueIds:3914,allIdsPresent:true});
  const data=await page.evaluate(ids=>ids.map(id=>{const v=DEFAULT_VOCAB.find(x=>Number(x.id)===id),d=VOCAB_DETAILS_BY_ID[String(id)];return{id,word:d.w,reading:v.r,pos:VOCAB_POS_BY_ID[String(id)],gloss:d.t,usage:d.usage,examples:d.examples,translations:d.exampleTranslations};}),IDS);
  for(const c of data){const e=EXPECTED[String(c.id)];assert.equal(c.word,e.word);assert.equal(c.reading,e.reading);assert.deepEqual(c.pos,e.pos);assert.ok(c.usage&&c.usage.length>0);if(e.gloss)assert.equal(c.gloss,e.gloss);if(e.translation)assert.ok(c.translations.includes(e.translation));if(e.example)assert.ok(c.examples.includes(e.example));assert.equal(c.examples.length,2);assert.equal(c.translations.length,2);}
  const pairData=await page.evaluate(()=>({p413:VOCAB_AUDITED_PAIRS[413],p760:VOCAB_AUDITED_PAIRS[760]}));assert.equal(pairData.p413.a,'1634');assert.equal(pairData.p413.b,'3363');assert.equal(pairData.p760.a,'3318');assert.equal(pairData.p760.b,'3368');
  const quiz=await page.evaluate(()=>({v3345:!!REVIEWED_MEANING_QUIZZES.v_3345?.byExample?.['天候に恵まれず、散々な結果に終わった遠征だった。'],v3363:!!REVIEWED_MEANING_QUIZZES.v_3363}));
  assert.deepEqual(quiz,{v3345:true,v3363:true});
  const rendered=await page.evaluate(async ids=>{showView('cards');const out=[];const n=x=>String(x).replaceAll('\n',' ').replaceAll('\r',' ').replaceAll('\t',' ').split(' ').filter(Boolean).join(' ');for(const id of ids){await openCardDetail('v',id);await new Promise(r=>setTimeout(r,35));const body=document.getElementById('cardDetailBody'),txt=body?.innerText||'',d=VOCAB_DETAILS_BY_ID[String(id)];out.push({id,word:d.w,titleVisible:n(txt).includes(n(d.w)),definitionVisible:n(txt).includes(n(d.m)),usageVisible:!!d.usage&&n(txt).includes('用法・接続'),translationsVisible:d.exampleTranslations.every(x=>!x||n(txt).includes(n(x))),examplesVisible:d.examples.every(x=>!x||n(txt).includes(n(x)))});}return out;},IDS);
  fs.writeFileSync(path.join(WORK,'rendered-debug.json'),JSON.stringify(rendered,null,2)+'\n');
  assert.ok(rendered.every(x=>x.titleVisible&&x.definitionVisible&&x.usageVisible&&x.translationsVisible&&x.examplesVisible));
  const responsive=[];for(const width of [360,412,1280]){await page.setViewportSize({width,height:900});const d=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth}));responsive.push({...d,overflow:d.scrollWidth>width||d.bodyWidth>width});}assert.ok(responsive.every(x=>!x.overflow));
  const storage=await page.evaluate(()=>{const key='choba_n1uk_storage_v1',old=localStorage.getItem(key),sentinel=JSON.stringify({meta:{sessionSize:10,streak:5,lastStudyDate:'2026-11-14'},vp:{'3344':{status:'S',timesShown:2}},gp:{'90':{status:'X'}}});localStorage.setItem(key,sentinel);const roundTrip=localStorage.getItem(key)===sentinel;if(old===null)localStorage.removeItem(key);else localStorage.setItem(key,old);return{roundTrip,restored:localStorage.getItem(key)===old};});assert.ok(storage.roundTrip&&storage.restored);assert.deepEqual(errors,[]);
  const result={pass:true,candidate_sha256:sha,candidate_bytes:bytes.length,counts:structural,reviewed_card_count:12,fixed_rechecked_count:5,reviewed_unchanged_count:5,blocked_count:2,pair_reviewed_count:2,pair_changed_count:0,responsive,storage,pageErrors:errors,quizPayloadsPreserved:quiz};
  fs.writeFileSync(path.join(WORK,'browser-results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
