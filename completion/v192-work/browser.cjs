const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const crypto=require('node:crypto');
const path=require('node:path');
const {pathToFileURL}=require('node:url');

const HTML='JLPT_N1_ukrainian_reading_v192.html';
const WORK='completion/v192-work';
const prepare=JSON.parse(fs.readFileSync(path.join(WORK,'prepare-results.json'),'utf8'));
const registry=JSON.parse(fs.readFileSync(path.join(WORK,'registry-results.json'),'utf8'));
const bytes=fs.readFileSync(HTML);
const sha=crypto.createHash('sha256').update(bytes).digest('hex');
assert.equal(sha,prepare.candidate_sha256);
assert.equal(prepare.pass,true);
assert.equal(prepare.exact_rollback,true);
assert.equal(registry.pass,true);

const IDS=[815,818,819,822,825,828,831,839,844,845,855,856];
const EXPECTED={
 815:{word:'圧倒',translations:['Найбільша перевага цієї компанії — технологічний рівень, що значно випереджає конкурентів.']},
 818:{word:'暗殺',gloss:'зазвичай політично або ідеологічно мотивоване',translations:['','Цей роман розповідає про події навколо таємного вбивства одного політика.']},
 819:{word:'暗算',gloss:'обчислення подумки; рахунок у голові'},
 822:{word:'委託',translations:['','Проведення дослідження планують доручити сторонній організації.']},
 825:{word:'意義',translations:['','Усі учасники ще раз разом підтвердили значущість цієї діяльності.']},
 828:{word:'異動',usage:'移動 — загальне переміщення; 異動 — кадрова зміна в межах організації.'},
 831:{word:'遺言',translations:['У заповіті дідусь висловив вдячність родині.']},
 839:{word:'一息',translations:['Коли завершився черговий етап важливої справи, команда перепочила.']},
 844:{word:'一連',definition:'互いに関連し、ひと続きとして捉えられる物事。',translations:['','Усі ці процедури планують перевести в електронну форму.']},
 845:{word:'逸品',translations:['','Винятковий виріб, який майстер виготовив із великою ретельністю, став головною принадою виставки.']},
 855:{word:'閲覧',translations:['У бібліотеці обмежено перегляд цінних давніх документів.']},
 856:{word:'援助',usage:'人を援助する／人に援助を行う／援助を受ける'}
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
   return {id,word:d.w,definition:d.m,gloss:d.t,usage:d.usage,examples:d.examples,translations:d.exampleTranslations,pos:VOCAB_POS_BY_ID[String(id)]};
  }),IDS);
  for(const card of data){
   const e=EXPECTED[card.id];
   assert.equal(card.word,e.word);
   if(e.definition)assert.ok(card.definition.includes(e.definition),'definition mismatch '+card.id);
   if(e.gloss)assert.ok(card.gloss.includes(e.gloss),'gloss mismatch '+card.id);
   if(e.usage)assert.ok(card.usage.includes(e.usage),'usage mismatch '+card.id);
   if(e.translations)for(const t of e.translations.filter(Boolean))assert.ok(card.translations.includes(t),'translation mismatch '+card.id);
   assert.deepEqual(card.pos,['名詞'],'POS changed '+card.id);
  }

  const rendered=await page.evaluate(async ids=>{
   showView('cards');
   const out=[];
   for(const id of ids){
    await openCardDetail('v',id);
    const body=document.getElementById('cardDetailBody');
    const text=body.innerText;
    const norm=x=>String(x).replace(/\s+/g,' ').replace(/\s*([—–])\s*/g,'$1').trim();
    const d=VOCAB_DETAILS_BY_ID[String(id)];
    out.push({
     id,word:d.w,
     titleVisible:norm(text).includes(norm(d.w)),
     glossVisible:d.t.split(';').map(x=>x.trim()).filter(Boolean).every(x=>norm(text).includes(norm(x))),
     usageVisible:[828,856].includes(id)?norm(text).includes(norm(id===828?'移動 — загальне переміщення':'人を援助する')):true,
     examplesVisible:d.exampleTranslations.every(x=>norm(text).includes(norm(x))),
     bodyTextLength:text.length
    });
   }
   return out;
  },IDS);
  assert.equal(rendered.length,12);
  const visibilityFailures=rendered.filter(x=>!(x.titleVisible&&x.glossVisible&&x.usageVisible&&x.examplesVisible));
  if(visibilityFailures.length)console.error('Rendered visibility diagnostics:',JSON.stringify(visibilityFailures,null,2));
  assert.equal(visibilityFailures.length,0);

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
   const sentinel=JSON.stringify({meta:{sessionSize:10,streak:4,lastStudyDate:'2026-11-13'},vp:{'815':{status:'S',timesShown:3}},gp:{'90':{status:'X'}}});
   localStorage.setItem(key,sentinel);
   const roundTrip=localStorage.getItem(key)===sentinel;
   if(old===null)localStorage.removeItem(key);else localStorage.setItem(key,old);
   return {roundTrip,restored:localStorage.getItem(key)===old};
  });
  assert.equal(storage.roundTrip,true);
  assert.equal(storage.restored,true);
  assert.deepEqual(errors,[]);

  const result={pass:true,candidate_sha256:sha,candidate_bytes:bytes.length,counts:structural,reviewed_card_count:rendered.length,reviewed_cards:rendered,responsive,storage,pageErrors:errors};
  fs.writeFileSync(path.join(WORK,'browser-results.json'),JSON.stringify(result,null,2)+'\n');
  process.stdout.write(JSON.stringify(result,null,2)+'\n');
 }finally{await browser.close();}
}
main().catch(error=>{console.error(error);process.exit(1);});
