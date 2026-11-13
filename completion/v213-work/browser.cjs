const {chromium}=require('playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const HTML='JLPT_N1_ukrainian_reading_v213.html',WORK='completion/v213-work';
const prepare=JSON.parse(fs.readFileSync(path.join(WORK,'prepare-results.json'),'utf8')),registry=JSON.parse(fs.readFileSync(path.join(WORK,'registry-results.json'),'utf8'));
const diag=JSON.parse(fs.readFileSync(path.join(WORK,'pos-diagnostic.json'),'utf8'));
const bytes=fs.readFileSync(HTML),sha=crypto.createHash('sha256').update(bytes).digest('hex');
assert.equal(sha,prepare.candidate_sha256);assert.equal(prepare.pass,true);assert.equal(prepare.exact_rollback,true);assert.equal(registry.pass,true);
assert.deepEqual(diag,{id:1631,current:['名詞'],proposed:['名詞','ナ形'],reading_candidates_before:60,reading_candidates_after:2,cloze_candidates_before:2269,cloze_candidates_after:65});
const IDS=[1528,1529,1539,1541,1542,1548,1551,1554,1558,1625,1628];
const EXPECTED={
 1528:{word:'親善',gloss:'взаємна приязнь'},
 1529:{word:'診療',translations:['У цій клініці пацієнтів терапевтичного профілю оглядають і лікують навіть без попереднього запису.','Нагальним завданням стало забезпечити лікарів, які надаватимуть медичну допомогу в малолюдних районах.']},
 1539:{word:'人柄',translations:['Багато хто, приваблений його порядністю, хоче мати з ним ділові стосунки.']},
 1541:{word:'図星',usage:'зауваження влучне',translations:['Коли йому влучно вказали на болюче місце, він відвів погляд, намагаючись приховати хвилювання.']},
 1542:{word:'吹雪',definition:'風が積もった雪を巻き上げて吹き荒れること'},
 1548:{word:'水気',translations:['Якщо перед смаженням добре дати воді стекти з овочів, готова страва не буде липкою.']},
 1551:{word:'衰退',definition:'勢いが弱まり、力や活気を失っていくこと'},
 1554:{word:'世論',definition:'公共の問題についての意見や見方'},
 1558:{word:'制定',gloss:'ухвалення, установлення нового закону'},
 1625:{word:'捜査',translations:['Поліція продовжує розслідування, оскільки підозрює, що причетність до справи мала організований характер.']},
 1628:{word:'操作',translations:['Через неправомірні маніпуляції система автоматично зупинилася.']}
};
async function main(){
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:412,height:900}}),errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(pathToFileURL(path.resolve(HTML)).href);
  const structural=await page.evaluate(()=>({vocab:DEFAULT_VOCAB.length,grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,pairs:VOCAB_AUDITED_PAIRS.length,uniqueIds:new Set(DEFAULT_VOCAB.map(x=>Number(x.id))).size,allIdsPresent:DEFAULT_VOCAB.every(x=>VOCAB_DETAILS_BY_ID[String(x.id)]&&VOCAB_POS_BY_ID[String(x.id)])}));
  assert.deepEqual(structural,{vocab:3914,grammar:130,pairs:859,uniqueIds:3914,allIdsPresent:true});
  const data=await page.evaluate(ids=>ids.map(id=>{const d=VOCAB_DETAILS_BY_ID[String(id)];return{id,word:d.w,gloss:d.t,usage:d.usage,definition:d.m,translations:d.exampleTranslations,examples:d.examples,pos:VOCAB_POS_BY_ID[String(id)]}}),IDS);
  for(const card of data){const e=EXPECTED[card.id];assert.equal(card.word,e.word);if(e.gloss)assert.ok(card.gloss.includes(e.gloss));if(e.usage)assert.ok(card.usage.includes(e.usage));if(e.definition)assert.ok(card.definition.includes(e.definition));if(e.translations)for(const t of e.translations)assert.ok(card.translations.includes(t));assert.ok(card.pos.length>=1);}
  const deferred=await page.evaluate(()=>({pos:VOCAB_POS_BY_ID['1631']}));
  assert.deepEqual(deferred.pos,['名詞']);
  const rendered=await page.evaluate(async ids=>{showView('cards');const out=[];for(const id of ids){await openCardDetail('v',id);await new Promise(resolve=>setTimeout(resolve,40));const body=document.getElementById('cardDetailBody'),text=body?.innerText||'',norm=x=>String(x).replace(/\\s+/g,' ').trim(),d=VOCAB_DETAILS_BY_ID[String(id)];out.push({id,word:d.w,titleVisible:norm(text).includes(norm(d.w)),glossVisible:norm(text).includes(norm(d.t)),usageVisible:!d.usage||norm(text).includes(norm(d.usage)),translationsVisible:d.exampleTranslations.every(x=>!x||norm(text).includes(norm(x))),examplesVisible:d.examples.every(x=>!x||norm(text).includes(norm(x))),textExcerpt:norm(text).slice(0,900)});}return out;},IDS);
  fs.writeFileSync(path.join(WORK,'rendered-debug.json'),JSON.stringify(rendered,null,2)+'\\n');
  const renderFailures=rendered.filter(x=>!(x.titleVisible&&x.glossVisible&&x.usageVisible&&x.translationsVisible&&x.examplesVisible));
  assert.equal(rendered.length,11);if(renderFailures.length)throw new Error('Card detail visibility mismatches: '+JSON.stringify(renderFailures));
  const responsive=[];for(const width of [360,412,1280]){await page.setViewportSize({width,height:900});const d=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth}));responsive.push({...d,overflow:d.scrollWidth>width||d.bodyWidth>width});}assert.equal(responsive.every(x=>!x.overflow),true);
  const storage=await page.evaluate(()=>{const key='choba_n1uk_storage_v1',old=localStorage.getItem(key),sentinel=JSON.stringify({meta:{sessionSize:10,streak:4,lastStudyDate:'2026-11-13'},vp:{'1528':{status:'S',timesShown:3}},gp:{'90':{status:'X'}}});localStorage.setItem(key,sentinel);const roundTrip=localStorage.getItem(key)===sentinel;if(old===null)localStorage.removeItem(key);else localStorage.setItem(key,old);return{roundTrip,restored:localStorage.getItem(key)===old};});
  assert.equal(storage.roundTrip,true);assert.equal(storage.restored,true);assert.deepEqual(errors,[]);
  const result={pass:true,candidate_sha256:sha,candidate_bytes:bytes.length,counts:structural,reviewed_card_count:11,pending_card_count:1,responsive,storage,pageErrors:errors,deferred_pos_diagnostic:diag};
  fs.writeFileSync(path.join(WORK,'browser-results.json'),JSON.stringify(result,null,2)+'\n');process.stdout.write(JSON.stringify(result,null,2)+'\n');
 }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exit(1);});
