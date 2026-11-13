const {chromium}=require('playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const HTML='JLPT_N1_ukrainian_reading_v205.html',WORK='completion/v205-work';
const prepare=JSON.parse(fs.readFileSync(path.join(WORK,'prepare-results.json'),'utf8')),registry=JSON.parse(fs.readFileSync(path.join(WORK,'registry-results.json'),'utf8'));
const bytes=fs.readFileSync(HTML),sha=crypto.createHash('sha256').update(bytes).digest('hex');
assert.equal(sha,prepare.candidate_sha256);assert.equal(prepare.pass,true);assert.equal(prepare.exact_rollback,true);assert.equal(registry.pass,true);
const IDS=[1297,1300,1301,1303,1306,1309,1311,1312,1313,1315,1316,1319];
const EXPECTED={
 1297:{word:'在籍',translations:['Нині в нашому навчальному закладі навчається близько тисячі студентів, які щодня займаються дослідженнями.','Під час тимчасової перерви в роботі він залишається в штаті компанії й чекає на повернення.']},
 1300:{word:'搾取',translations:['У колоніальну добу місцеві ресурси експлуатували, а жителі потерпали від злиднів.']},
 1301:{word:'昨今',translations:['Останнім часом, із поширенням різних форм роботи, істотно змінюються й кадрові системи підприємств.']},
 1303:{word:'察知',gloss:'виявлення сигналу приладом'},
 1306:{word:'参観',translations:['Студентів, які побували на заводі, вразив високий технологічний рівень виробництва.']},
 1309:{word:'山岳',translations:['У гірській місцевості погода може різко змінитися, тому тим, хто вирушає в гори, потрібно ретельно підготуватися.']},
 1311:{word:'山脈',translations:['Гірський хребет, яким проходить кордон, здавна був природною перепоною для зв’язків між двома країнами.']},
 1312:{word:'惨事',translations:['Було пообіцяно забезпечити повне виконання заходів безпеки, щоб така трагедія більше не повторилася.']},
 1313:{word:'惨敗',translations:['Правляча партія зазнала нищівної поразки від опозиції на місцевих виборах, і посилилися заклики притягнути її лідера до відповідальності.','Новий товар зазнав нищівної поразки в конкуренції з іншими виробниками, і компанія була змушена згорнути цей напрям бізнесу.']},
 1315:{word:'産物',translations:['Це відома страва місцевої кухні, у якій майстерно використано продукти регіону.']},
 1316:{word:'酸化',gloss:'сполучення речовини з киснем'},
 1319:{word:'仕業',gloss:'це справа його рук'}
};
async function main(){
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:412,height:900}}),errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(pathToFileURL(path.resolve(HTML)).href);
  const structural=await page.evaluate(()=>({vocab:DEFAULT_VOCAB.length,grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,pairs:VOCAB_AUDITED_PAIRS.length,uniqueIds:new Set(DEFAULT_VOCAB.map(x=>Number(x.id))).size,allIdsPresent:DEFAULT_VOCAB.every(x=>VOCAB_DETAILS_BY_ID[String(x.id)]&&VOCAB_POS_BY_ID[String(x.id)])}));
  assert.deepEqual(structural,{vocab:3914,grammar:130,pairs:859,uniqueIds:3914,allIdsPresent:true});
  const data=await page.evaluate(ids=>ids.map(id=>{const d=VOCAB_DETAILS_BY_ID[String(id)];return{id,word:d.w,gloss:d.t,usage:d.usage,translations:d.exampleTranslations,examples:d.examples,pos:VOCAB_POS_BY_ID[String(id)]}}),IDS);
  for(const card of data){const e=EXPECTED[card.id];assert.equal(card.word,e.word);if(e.gloss)assert.ok((card.gloss+' '+card.usage).includes(e.gloss));if(e.translations)for(const t of e.translations)assert.ok(card.translations.includes(t));assert.deepEqual(card.pos,['名詞']);}
  const rendered=await page.evaluate(async ids=>{showView('cards');const out=[];for(const id of ids){await openCardDetail('v',id);const body=document.getElementById('cardDetailBody'),text=body.innerText,norm=x=>String(x).replace(/\s+/g,' ').trim(),d=VOCAB_DETAILS_BY_ID[String(id)];out.push({id,word:d.w,titleVisible:norm(text).includes(norm(d.w)),glossVisible:d.t.split(';').map(x=>x.trim()).filter(Boolean).every(x=>norm(text).includes(norm(x))),translationsVisible:d.exampleTranslations.every(x=>norm(text).includes(norm(x))),examplesVisible:d.examples.every(x=>norm(text).includes(norm(x)))});}return out;},IDS);
  assert.equal(rendered.length,12);assert.equal(rendered.every(x=>x.titleVisible&&x.glossVisible&&x.translationsVisible&&x.examplesVisible),true);
  const responsive=[];for(const width of [360,412,1280]){await page.setViewportSize({width,height:900});const d=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth}));responsive.push({...d,overflow:d.scrollWidth>width||d.bodyWidth>width});}assert.equal(responsive.every(x=>!x.overflow),true);
  const storage=await page.evaluate(()=>{const key='choba_n1uk_storage_v1',old=localStorage.getItem(key),sentinel=JSON.stringify({meta:{sessionSize:10,streak:4,lastStudyDate:'2026-11-13'},vp:{'1297':{status:'S',timesShown:3}},gp:{'90':{status:'X'}}});localStorage.setItem(key,sentinel);const roundTrip=localStorage.getItem(key)===sentinel;if(old===null)localStorage.removeItem(key);else localStorage.setItem(key,old);return{roundTrip,restored:localStorage.getItem(key)===old};});
  assert.equal(storage.roundTrip,true);assert.equal(storage.restored,true);assert.deepEqual(errors,[]);
  const result={pass:true,candidate_sha256:sha,candidate_bytes:bytes.length,counts:structural,reviewed_card_count:12,reviewed_cards:rendered,responsive,storage,pageErrors:errors};
  fs.writeFileSync(path.join(WORK,'browser-results.json'),JSON.stringify(result,null,2)+'\n');process.stdout.write(JSON.stringify(result,null,2)+'\n');
 }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exit(1);});
