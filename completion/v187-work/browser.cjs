const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const crypto=require('node:crypto');
const path=require('node:path');
const {pathToFileURL}=require('node:url');

const HTML='JLPT_N1_ukrainian_reading_v187.html';
const WORK='completion/v187-work';
const prepare=JSON.parse(fs.readFileSync(path.join(WORK,'prepare-results.json'),'utf8'));
const registry=JSON.parse(fs.readFileSync(path.join(WORK,'registry-results.json'),'utf8'));
const bytes=fs.readFileSync(HTML);
const sha=crypto.createHash('sha256').update(bytes).digest('hex');
assert.equal(sha,prepare.candidate_sha256);
assert.equal(prepare.pass,true);
assert.equal(prepare.exact_rollback,true);
assert.equal(registry.pass,true);

const IDS=[615,616,618,624,629,644,651,654,663,664,672,674];
const EXPECTED={
 615:{word:'仮に',translations:['Навіть якщо попит знизиться сильніше, ніж передбачалося спочатку, це не завадить продовженню діяльності.','Якщо припустити, що цю пропозицію ухвалять, яким буде фінансове навантаження?']},
 616:{word:'いくらか',translations:['Хоча певне поліпшення помітне, докорінного розв’язання проблеми ще не досягнуто.']},
 618:{word:'改めて',translations:['Після цього випадку ми маємо намір посилити виконання заходів, щоб подібне не повторилося.']},
 624:{word:'間もなく'},
 629:{word:'わざと',usage:'навмисно припуститися помилки',translations:['','Працівника покарали, вважаючи, що він навмисно приховував важливу інформацію.']},
 644:{word:'当然',pos:['副詞'],translations:['Дотримуватися законів — само собою зрозумілий обов’язок компанії.']},
 651:{word:'インフルエンザ',definition:'インフルエンザウイルスによって起こる急性の感染症。'},
 654:{word:'ウイルス',definition:'生きた細胞に入り込み、その細胞の仕組みを利用して増殖する感染性の病原体。'},
 663:{word:'オーバー',pos:['名詞']},
 664:{word:'スペース',gloss:'пробіл (у тексті)'},
 672:{word:'カウンター',gloss:'контратака, контрудар',translations:['','Особливість цього закладу — уважне обслуговування покупців біля прилавка.']},
 674:{word:'ベース',gloss:'база (у бейсболі); бас-гітара, басова партія'}
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
   if(e.pos)assert.deepEqual(card.pos,e.pos,'POS changed '+card.id);
  }

  const rendered=await page.evaluate(async ids=>{
   showView('cards');
   const out=[];
   for(const id of ids){
    await openCardDetail('v',id);
    const body=document.getElementById('cardDetailBody');
    const text=body.innerText;
    const d=VOCAB_DETAILS_BY_ID[String(id)];
    const norm=x=>String(x).replace(/\\s+/g,' ').trim();
    out.push({
     id,word:d.w,
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
   const sentinel=JSON.stringify({meta:{sessionSize:10,streak:4,lastStudyDate:'2026-11-13'},vp:{'615':{status:'S',timesShown:3}},gp:{'90':{status:'X'}}});
   localStorage.setItem(key,sentinel);
   const roundTrip=localStorage.getItem(key)===sentinel;
   if(old===null)localStorage.removeItem(key);else localStorage.setItem(key,old);
   return {roundTrip,restored:localStorage.getItem(key)===old};
  });
  assert.equal(storage.roundTrip,true);
  assert.equal(storage.restored,true);
  assert.deepEqual(errors,[]);

  const result={pass:true,candidate_sha256:sha,candidate_bytes:bytes.length,counts:structural,reviewed_card_count:rendered.length,reviewed_cards:rendered,c11_pos_hold:{'644':['副詞'],'663':['名詞']},responsive,storage,pageErrors:errors};
  fs.writeFileSync(path.join(WORK,'browser-results.json'),JSON.stringify(result,null,2)+'\\n');
  process.stdout.write(JSON.stringify(result,null,2)+'\\n');
 }finally{await browser.close();}
}
main().catch(error=>{console.error(error);process.exit(1);});
