const {chromium}=require('playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const HTML='JLPT_N1_ukrainian_reading_v202.html',WORK='completion/v202-work';
const prepare=JSON.parse(fs.readFileSync(path.join(WORK,'prepare-results.json'),'utf8')),registry=JSON.parse(fs.readFileSync(path.join(WORK,'registry-results.json'),'utf8'));
const bytes=fs.readFileSync(HTML),sha=crypto.createHash('sha256').update(bytes).digest('hex');
assert.equal(sha,prepare.candidate_sha256);assert.equal(prepare.pass,true);assert.equal(prepare.exact_rollback,true);assert.equal(registry.pass,true);
const IDS=[1119,1123,1124,1127,1128,1129,1132,1135,1139,1140,1147,1148];
const EXPECTED={
 1119:{word:'近接',gloss:'безпосередня близькість у просторі або часі; 近接する — розташовуватися зовсім поруч'},
 1123:{word:'苦戦',translations:['Новий продукт від самого початку мав труднощі на ринку, а продажі не зростали, як очікувалося.']},
 1124:{word:'駆使',translations:['Завдяки вмілому використанню кількох мов він успішно завершив переговори на міжнародній конференції.']},
 1127:{word:'屈指',translations:['Її вважають однією з наймайстерніших піаністок країни.']},
 1128:{word:'屈折',gloss:'згинання; заломлення світла або хвиль'},
 1129:{word:'群衆',translations:['Іноді досить однієї людини, щоб підбурити натовп.']},
 1132:{word:'刑罰',translations:['За законом за такі порушення передбачене суворе кримінальне покарання.']},
 1135:{word:'形態',translations:['Компанії, створені на основі спільних капіталовкладень, привертають увагу як нова форма ведення бізнесу.']},
 1139:{word:'継続',translations:['Постійні сумлінні зусилля приводять до відчутних результатів.']},
 1140:{word:'警戒',translations:['Готуючись до наближення тайфуну, мешканці узбережжя пильніше стежать за загрозою штормового нагону води.']},
 1147:{word:'激減',translations:['Через зниження народжуваності кількість учнів початкових шкіл у регіонах різко скорочується.','Різке скорочення кількості туристів завдало тяжкого удару галузі туристичного розміщення.']},
 1148:{word:'激怒',translations:['Клієнт страшенно розлютився через несправедливе ставлення й наказав відповідальному працівникові підійти.']}
};
async function main(){
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:412,height:900}}),errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(pathToFileURL(path.resolve(HTML)).href);
  const structural=await page.evaluate(()=>({vocab:DEFAULT_VOCAB.length,grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,pairs:VOCAB_AUDITED_PAIRS.length,uniqueIds:new Set(DEFAULT_VOCAB.map(x=>Number(x.id))).size,allIdsPresent:DEFAULT_VOCAB.every(x=>VOCAB_DETAILS_BY_ID[String(x.id)]&&VOCAB_POS_BY_ID[String(x.id)])}));
  assert.deepEqual(structural,{vocab:3914,grammar:130,pairs:859,uniqueIds:3914,allIdsPresent:true});
  const data=await page.evaluate(ids=>ids.map(id=>{const d=VOCAB_DETAILS_BY_ID[String(id)];return{id,word:d.w,definition:d.m,gloss:d.t,translations:d.exampleTranslations,examples:d.examples,pos:VOCAB_POS_BY_ID[String(id)]}}),IDS);
  for(const card of data){const e=EXPECTED[card.id];assert.equal(card.word,e.word);if(e.gloss)assert.ok(card.gloss.includes(e.gloss));if(e.translations)for(const t of e.translations)assert.ok(card.translations.includes(t));assert.deepEqual(card.pos,['名詞']);}
  const rendered=await page.evaluate(async ids=>{showView('cards');const out=[];for(const id of ids){await openCardDetail('v',id);const body=document.getElementById('cardDetailBody'),text=body.innerText,norm=x=>String(x).replace(/\s+/g,' ').trim(),d=VOCAB_DETAILS_BY_ID[String(id)];out.push({id,word:d.w,titleVisible:norm(text).includes(norm(d.w)),glossVisible:d.t.split(';').map(x=>x.trim()).filter(Boolean).every(x=>norm(text).includes(norm(x))),translationsVisible:d.exampleTranslations.every(x=>norm(text).includes(norm(x)))});}return out;},IDS);
  assert.equal(rendered.length,12);assert.equal(rendered.every(x=>x.titleVisible&&x.glossVisible&&x.translationsVisible),true);
  const responsive=[];for(const width of [360,412,1280]){await page.setViewportSize({width,height:900});const d=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth}));responsive.push({...d,overflow:d.scrollWidth>width||d.bodyWidth>width});}assert.equal(responsive.every(x=>!x.overflow),true);
  const storage=await page.evaluate(()=>{const key='choba_n1uk_storage_v1',old=localStorage.getItem(key),sentinel=JSON.stringify({meta:{sessionSize:10,streak:4,lastStudyDate:'2026-11-13'},vp:{'1119':{status:'S',timesShown:3}},gp:{'90':{status:'X'}}});localStorage.setItem(key,sentinel);const roundTrip=localStorage.getItem(key)===sentinel;if(old===null)localStorage.removeItem(key);else localStorage.setItem(key,old);return{roundTrip,restored:localStorage.getItem(key)===old};});
  assert.equal(storage.roundTrip,true);assert.equal(storage.restored,true);assert.deepEqual(errors,[]);
  const result={pass:true,candidate_sha256:sha,candidate_bytes:bytes.length,counts:structural,reviewed_card_count:12,reviewed_cards:rendered,responsive,storage,pageErrors:errors};
  fs.writeFileSync(path.join(WORK,'browser-results.json'),JSON.stringify(result,null,2)+'\n');process.stdout.write(JSON.stringify(result,null,2)+'\n');
 }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exit(1);});
