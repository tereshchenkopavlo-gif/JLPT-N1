const {chromium}=require('playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const HTML='JLPT_N1_ukrainian_reading_v204.html',WORK='completion/v204-work';
const prepare=JSON.parse(fs.readFileSync(path.join(WORK,'prepare-results.json'),'utf8')),registry=JSON.parse(fs.readFileSync(path.join(WORK,'registry-results.json'),'utf8'));
const bytes=fs.readFileSync(HTML),sha=crypto.createHash('sha256').update(bytes).digest('hex');
assert.equal(sha,prepare.candidate_sha256);assert.equal(prepare.pass,true);assert.equal(prepare.exact_rollback,true);assert.equal(registry.pass,true);
const IDS=[1198,1202,1214,1218,1236,1237,1239,1241,1246,1248,1249,1251];
const EXPECTED={
 1198:{word:'現行',translations:['У чинній системі дедалі помітнішими стають аспекти, що заважають їй пристосовуватися до змін часу.']},
 1202:{word:'古来',pos:['名詞']},
 1214:{word:'誤差',translations:['Слід мати на увазі, що це дослідження має похибку в кілька пунктів.']},
 1218:{word:'公募',translations:['Кількість заявок на відкритий конкурс на посади членів комісії перевищила кількість місць більш ніж у п’ять разів.']},
 1236:{word:'考慮',gloss:'під час ухвалення рішення'},
 1237:{word:'肯定',example:'会議では、彼の提案を肯定する意見が多数を占めた。',translations:['На нараді переважали думки на підтримку його пропозиції.']},
 1239:{word:'荒廃',translations:['Ліси, за якими не доглядають, занепадають, і небезпека зсувів та селів зростає.']},
 1241:{word:'講読',gloss:'часто в навчальному контексті',translations:['На семінарі ми читаємо й докладно розбираємо класичні твори в оригіналі, вивчаючи підґрунтя відповідних ідей.']},
 1246:{word:'降参',translations:['Зрештою інша сторона поступилася його наполегливості й прийняла умови.']},
 1248:{word:'高低',gloss:'високий і низький рівні'},
 1249:{word:'合間',translations:['Проміння, що пробивалося крізь просвіти між хмарами, чітко освітлювало лінію гірського гребеня.']},
 1251:{word:'合席',translations:['Оскільки всі місця зайняті, просимо сідати за один стіл з іншими відвідувачами.']}
};
async function main(){
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:412,height:900}}),errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(pathToFileURL(path.resolve(HTML)).href);
  const structural=await page.evaluate(()=>({vocab:DEFAULT_VOCAB.length,grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,pairs:VOCAB_AUDITED_PAIRS.length,uniqueIds:new Set(DEFAULT_VOCAB.map(x=>Number(x.id))).size,allIdsPresent:DEFAULT_VOCAB.every(x=>VOCAB_DETAILS_BY_ID[String(x.id)]&&VOCAB_POS_BY_ID[String(x.id)])}));
  assert.deepEqual(structural,{vocab:3914,grammar:130,pairs:859,uniqueIds:3914,allIdsPresent:true});
  const data=await page.evaluate(ids=>ids.map(id=>{const d=VOCAB_DETAILS_BY_ID[String(id)];return{id,word:d.w,gloss:d.t,translations:d.exampleTranslations,examples:d.examples,pos:VOCAB_POS_BY_ID[String(id)]}}),IDS);
  for(const card of data){const e=EXPECTED[card.id];assert.equal(card.word,e.word);if(e.gloss)assert.ok(card.gloss.includes(e.gloss));if(e.translations)for(const t of e.translations)assert.ok(card.translations.includes(t));if(e.example)assert.equal(card.examples[1],e.example);if(e.pos)assert.deepEqual(card.pos,e.pos);else assert.deepEqual(card.pos,['名詞']);}
  const rendered=await page.evaluate(async ids=>{showView('cards');const out=[];for(const id of ids){await openCardDetail('v',id);const body=document.getElementById('cardDetailBody'),text=body.innerText,norm=x=>String(x).replace(/\s+/g,' ').trim(),d=VOCAB_DETAILS_BY_ID[String(id)];out.push({id,word:d.w,titleVisible:norm(text).includes(norm(d.w)),glossVisible:d.t.split(';').map(x=>x.trim()).filter(Boolean).every(x=>norm(text).includes(norm(x))),translationsVisible:d.exampleTranslations.every(x=>norm(text).includes(norm(x))),examplesVisible:d.examples.every(x=>norm(text).includes(norm(x)))});}return out;},IDS);
  assert.equal(rendered.length,12);assert.equal(rendered.every(x=>x.titleVisible&&x.glossVisible&&x.translationsVisible&&x.examplesVisible),true);
  const nounFilter=await page.evaluate(()=>{const ids=DEFAULT_VOCAB.filter(v=>VOCAB_POS_BY_ID[String(v.id)]?.includes('名詞')).map(v=>Number(v.id));return ids.includes(1202);});assert.equal(nounFilter,true);
  const responsive=[];for(const width of [360,412,1280]){await page.setViewportSize({width,height:900});const d=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth}));responsive.push({...d,overflow:d.scrollWidth>width||d.bodyWidth>width});}assert.equal(responsive.every(x=>!x.overflow),true);
  const storage=await page.evaluate(()=>{const key='choba_n1uk_storage_v1',old=localStorage.getItem(key),sentinel=JSON.stringify({meta:{sessionSize:10,streak:4,lastStudyDate:'2026-11-13'},vp:{'1198':{status:'S',timesShown:3}},gp:{'90':{status:'X'}}});localStorage.setItem(key,sentinel);const roundTrip=localStorage.getItem(key)===sentinel;if(old===null)localStorage.removeItem(key);else localStorage.setItem(key,old);return{roundTrip,restored:localStorage.getItem(key)===old};});
  assert.equal(storage.roundTrip,true);assert.equal(storage.restored,true);assert.deepEqual(errors,[]);
  const result={pass:true,candidate_sha256:sha,candidate_bytes:bytes.length,counts:structural,reviewed_card_count:12,reviewed_cards:rendered,noun_filter_keeps_korai:nounFilter,responsive,storage,pageErrors:errors};
  fs.writeFileSync(path.join(WORK,'browser-results.json'),JSON.stringify(result,null,2)+'\n');process.stdout.write(JSON.stringify(result,null,2)+'\n');
 }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exit(1);});
