const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const crypto=require('node:crypto');
const path=require('node:path');
const {pathToFileURL}=require('node:url');

const HTML='JLPT_N1_ukrainian_reading_v186.html';
const WORK='completion/v186-work';
const prepare=JSON.parse(fs.readFileSync(path.join(WORK,'prepare-results.json'),'utf8'));
const registry=JSON.parse(fs.readFileSync(path.join(WORK,'registry-results.json'),'utf8'));
const bytes=fs.readFileSync(HTML);
const sha=crypto.createHash('sha256').update(bytes).digest('hex');
assert.equal(sha,prepare.candidate_sha256);
assert.equal(prepare.pass,true);
assert.equal(prepare.exact_rollback,true);
assert.equal(registry.pass,true);

const IDS=[565,571,572,579,586,588,590,593,595,597,599,609];
const EXPECTED={
 565:{word:'順調',translation:'Роботи йдуть добре, і, як очікується, їх завершать наступного місяця за графіком.'},
 571:{word:'盛大',translation:'Багато хто шкодував через його відхід із роботи, тож для нього влаштували пишний прощальний захід.'},
 572:{word:'積極的',gloss:'позитивно оцінює й підтримує'},
 579:{word:'地味',translation:'Саме послідовна малопомітна праця й дає великі результати.'},
 586:{word:'典型的',translation:'У цій історії є персонаж, який утілює типовий образ героя.'},
 588:{word:'独特',pos:['ナ形']},
 590:{word:'否定的',translation:'Важливо серйозно ставитися до негативних оцінок і використовувати їх для поліпшення.'},
 593:{word:'平気',translation:'Не можна миритися з тим, що людина, попри численні зауваження, знову й знову запізнюється, наче нічого не сталося.'},
 595:{word:'未熟',translation:'Якщо відвантажувати продукцію з недостатньо відпрацьованою технологією, це може призвести до аварії з непоправними наслідками.'},
 597:{word:'無難',translation:'На нараді впадали в око учасники, які обмежувалися нейтральними висловлюваннями, що нікого не зачіпали.'},
 599:{word:'無礼',pos:['ナ形']},
 609:{word:'わりに',usage:'イ形容詞普通形／ナ形容詞な＋わりに'}
};

async function main(){
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:412,height:900}});
  const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(pathToFileURL(path.resolve(HTML)).href);
  const structural=await page.evaluate(()=>({
   vocab:DEFAULT_VOCAB.length,
   grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,
   pairs:VOCAB_AUDITED_PAIRS.length,
   uniqueIds:new Set(DEFAULT_VOCAB.map(x=>Number(x.id))).size,
   allIdsPresent:DEFAULT_VOCAB.every(x=>VOCAB_DETAILS_BY_ID[String(x.id)]&&VOCAB_POS_BY_ID[String(x.id)])
  }));
  assert.deepEqual(structural,{vocab:3914,grammar:130,pairs:859,uniqueIds:3914,allIdsPresent:true});

  const data=await page.evaluate(ids=>ids.map(id=>{
   const d=VOCAB_DETAILS_BY_ID[String(id)];
   return {id,word:d.w,pos:VOCAB_POS_BY_ID[String(id)],gloss:d.t,usage:d.usage,examples:d.examples,translations:d.exampleTranslations};
  }),IDS);
  for(const card of data){
   const expected=EXPECTED[card.id];
   assert.equal(card.word,expected.word);
   if(expected.translation)assert.ok(card.translations.includes(expected.translation),'translation mismatch '+card.id);
   if(expected.gloss)assert.ok(card.gloss.includes(expected.gloss),'gloss mismatch '+card.id);
   if(expected.usage)assert.ok(card.usage.includes(expected.usage),'usage mismatch '+card.id);
   if(expected.pos)assert.deepEqual(card.pos,expected.pos,'POS changed '+card.id);
  }
  const rendered=await page.evaluate(async ids=>{
   showView('cards');
   const out=[];
   for(const id of ids){
    await openCardDetail('v',id);
    const body=document.getElementById('cardDetailBody');
    const text=body.innerText;
    const d=VOCAB_DETAILS_BY_ID[String(id)];
    const norm=x=>String(x).replace(/\s+/g,' ').trim();
    out.push({
     id,
     word:d.w,
     titleVisible:norm(text).includes(norm(d.w)),
     glossVisible:d.t.split(';').map(x=>x.trim()).filter(Boolean).every(x=>norm(text).includes(norm(x))),
     usageVisible:norm(text).includes(norm(d.usage)),
     examplesVisible:d.exampleTranslations.every(x=>norm(text).includes(norm(x))),
     bodyTextLength:text.length
    });
   }
   return out;
  },IDS);
  assert.equal(rendered.length,12);
  assert.equal(rendered.every(x=>x.titleVisible&&x.glossVisible&&x.usageVisible&&x.examplesVisible),true);

  const responsive=[];
  for(const width of [360,412,1280]){
   await page.setViewportSize({width,height:900});
   await page.evaluate(()=>window.scrollTo(0,0));
   const d=await page.evaluate(()=>({width:window.innerWidth,scrollWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth}));
   responsive.push({...d,overflow:d.scrollWidth>width||d.bodyWidth>width});
  }
  assert.equal(responsive.every(x=>!x.overflow),true);

  const storage=await page.evaluate(()=>{
   const key='choba_n1uk_storage_v1';
   const old=localStorage.getItem(key);
   const sentinel=JSON.stringify({meta:{sessionSize:10,streak:4,lastStudyDate:'2026-11-13'},vp:{'565':{status:'S',timesShown:3}},gp:{'90':{status:'X'}}});
   localStorage.setItem(key,sentinel);
   const roundTrip=localStorage.getItem(key)===sentinel;
   if(old===null)localStorage.removeItem(key);else localStorage.setItem(key,old);
   return {roundTrip,restored:localStorage.getItem(key)===old};
  });
  assert.equal(storage.roundTrip,true);
  assert.equal(storage.restored,true);
  assert.deepEqual(errors,[]);

  const result={
   pass:true,
   candidate_sha256:sha,
   candidate_bytes:bytes.length,
   counts:structural,
   reviewed_card_count:rendered.length,
   reviewed_cards:rendered,
   c11_pos_hold:{'588':['ナ形'],'599':['ナ形']},
   responsive,
   storage,
   pageErrors:errors
  };
  fs.writeFileSync(path.join(WORK,'browser-results.json'),JSON.stringify(result,null,2)+'\n');
  process.stdout.write(JSON.stringify(result,null,2)+'\n');
 }finally{await browser.close();}
}
main().catch(error=>{console.error(error);process.exit(1);});
