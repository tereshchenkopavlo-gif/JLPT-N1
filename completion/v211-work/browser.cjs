const {chromium}=require('playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const HTML='JLPT_N1_ukrainian_reading_v211.html',WORK='completion/v211-work';
const prepare=JSON.parse(fs.readFileSync(path.join(WORK,'prepare-results.json'),'utf8')),registry=JSON.parse(fs.readFileSync(path.join(WORK,'registry-results.json'),'utf8'));
const bytes=fs.readFileSync(HTML),sha=crypto.createHash('sha256').update(bytes).digest('hex');
assert.equal(sha,prepare.candidate_sha256);assert.equal(prepare.pass,true);assert.equal(prepare.exact_rollback,true);assert.equal(registry.pass,true);
const IDS=[1471,1477,1479,1484,1485,1486,1487,1489,1493,1496];
const EXPECTED={
 1471:{word:'傷跡',usage:'しょうこん'},
 1477:{word:'消息',gloss:'відомості про стан або долю',translations:['Навіть через три дні після інциденту досі немає звісток про альпініста, який потрапив у біду.']},
 1479:{word:'照合',gloss:'двох або більше',usage:'для звірення потрібні дані'},
 1484:{word:'証拠',translations:['Не слід порушувати справу, якщо доказів недостатньо.']},
 1485:{word:'詳細',gloss:'докладний',translations:['Щойно завершиться розслідування, про подробиці аварії повідомлять окремо.']},
 1486:{word:'賞賛',translations:['І вітчизняні, і закордонні медіа похвалили сміливе рішення.']},
 1487:{word:'障害',gloss:'людина з інвалідністю'},
 1489:{word:'上陸',usage:'центр тайфуну досягає суші',translations:['За прогнозом, уже завтра вранці тайфун досягне узбережжя Кюсю.']},
 1493:{word:'譲歩',usage:'条件面で譲歩する',translations:['Без взаємних поступок працівників і роботодавця переговори навряд чи завершаться домовленістю.']},
 1496:{word:'触覚',translations:['Покладаючись на чутливість кінчиків пальців, майстер розрізняє ледь помітну різницю в товщині.']}
};
async function main(){
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:412,height:900}}),errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(pathToFileURL(path.resolve(HTML)).href);
  const structural=await page.evaluate(()=>({vocab:DEFAULT_VOCAB.length,grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,pairs:VOCAB_AUDITED_PAIRS.length,uniqueIds:new Set(DEFAULT_VOCAB.map(x=>Number(x.id))).size,allIdsPresent:DEFAULT_VOCAB.every(x=>VOCAB_DETAILS_BY_ID[String(x.id)]&&VOCAB_POS_BY_ID[String(x.id)])}));
  assert.deepEqual(structural,{vocab:3914,grammar:130,pairs:859,uniqueIds:3914,allIdsPresent:true});
  const data=await page.evaluate(ids=>ids.map(id=>{const d=VOCAB_DETAILS_BY_ID[String(id)];return{id,word:d.w,gloss:d.t,usage:d.usage,definition:d.m,translations:d.exampleTranslations,examples:d.examples,pos:VOCAB_POS_BY_ID[String(id)]}}),IDS);
  for(const card of data){const e=EXPECTED[card.id];assert.equal(card.word,e.word);if(e.gloss)assert.ok(card.gloss.includes(e.gloss));if(e.usage)assert.ok(card.usage.includes(e.usage));if(e.definition)assert.ok(card.definition.includes(e.definition));if(e.example)assert.ok(card.examples.some(x=>x.includes(e.example)));if(e.translations)for(const t of e.translations)assert.ok(card.translations.includes(t));assert.deepEqual(card.pos,card.id===1485?['名詞','ナ形']:['名詞']);}
  const rendered=await page.evaluate(async ids=>{showView('cards');const out=[];for(const id of ids){await openCardDetail('v',id);const body=document.getElementById('cardDetailBody'),text=body.innerText,norm=x=>String(x).replace(/\s+/g,' ').trim(),d=VOCAB_DETAILS_BY_ID[String(id)];out.push({id,word:d.w,titleVisible:norm(text).includes(norm(d.w)),glossVisible:norm(text).includes(norm(d.t)),usageVisible:norm(text).includes(norm(d.usage)),translationsVisible:d.exampleTranslations.every(x=>norm(text).includes(norm(x))),examplesVisible:d.examples.every(x=>norm(text).includes(norm(x)))});}return out;},IDS);
  assert.equal(rendered.length,10);assert.equal(rendered.every(x=>x.titleVisible&&x.glossVisible&&x.usageVisible&&x.translationsVisible&&x.examplesVisible),true);
  const responsive=[];for(const width of [360,412,1280]){await page.setViewportSize({width,height:900});const d=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth}));responsive.push({...d,overflow:d.scrollWidth>width||d.bodyWidth>width});}assert.equal(responsive.every(x=>!x.overflow),true);
  const storage=await page.evaluate(()=>{const key='choba_n1uk_storage_v1',old=localStorage.getItem(key),sentinel=JSON.stringify({meta:{sessionSize:10,streak:4,lastStudyDate:'2026-11-13'},vp:{'1471':{status:'S',timesShown:3}},gp:{'90':{status:'X'}}});localStorage.setItem(key,sentinel);const roundTrip=localStorage.getItem(key)===sentinel;if(old===null)localStorage.removeItem(key);else localStorage.setItem(key,old);return{roundTrip,restored:localStorage.getItem(key)===old};});
  assert.equal(storage.roundTrip,true);assert.equal(storage.restored,true);assert.deepEqual(errors,[]);
  const result={pass:true,candidate_sha256:sha,candidate_bytes:bytes.length,counts:structural,reviewed_card_count:10,deferred_count:2,reviewed_cards:rendered,responsive,storage,pageErrors:errors};
  fs.writeFileSync(path.join(WORK,'browser-results.json'),JSON.stringify(result,null,2)+'\n');process.stdout.write(JSON.stringify(result,null,2)+'\n');
 }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exit(1);});
