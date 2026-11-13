const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const crypto=require('node:crypto');
const path=require('node:path');
const {pathToFileURL}=require('node:url');

const HTML='JLPT_N1_ukrainian_reading_v194.html';
const WORK='completion/v194-work';
const prepare=JSON.parse(fs.readFileSync(path.join(WORK,'prepare-results.json'),'utf8'));
const registry=JSON.parse(fs.readFileSync(path.join(WORK,'registry-results.json'),'utf8'));
const bytes=fs.readFileSync(HTML);
const sha=crypto.createHash('sha256').update(bytes).digest('hex');
assert.equal(sha,prepare.candidate_sha256);
assert.equal(prepare.pass,true);
assert.equal(prepare.exact_rollback,true);
assert.equal(registry.pass,true);

const IDS=[883,884,885,888,890,893,894,900,901,903,905,906];
const EXPECTED={
 883:{word:'加減',translations:['','Від того, скільки солі додати, смак страви може істотно змінитися.']},
 884:{word:'加味',gloss:'додавання смаку; перенесено — врахування додаткового чинника'},
 885:{word:'可決',translations:['','Перш ніж законопроєкт ухвалять, імовірно, ще виникнуть складнощі й непередбачені повороти подій.']},
 888:{word:'家来',translations:['','Він покірно слухається начальника, наче васал, і навіть не хоче висловлювати власної думки.']},
 890:{word:'架空',definition:'想像によって作り上げること。また、そのように作られたもの。',gloss:'вигадування неіснуючого; вигадка'},
 893:{word:'火災',translations:['','Пожежний сповіщувач перевіряють щороку.']},
 894:{word:'稼働',translations:['Новий завод має повноцінно запрацювати наступного місяця.']},
 900:{word:'過剰',translations:['Надмірні запаси ускладнили фінансування поточних витрат.']},
 901:{word:'過疎',gloss:'стан малонаселеної території, де через розріджене населення важко підтримувати звичне життя й послуги'},
 903:{word:'我々'},
 905:{word:'介護',translations:['Він працює, водночас доглядаючи за своїм літнім батьком або матір’ю.','Нестача фахівців із догляду виразно постала як проблема всього суспільства.']},
 906:{word:'介入',translations:['Уряд ретельно зважує, чи втручатися у валютний ринок.']}
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
   if(e.translations)for(const t of e.translations.filter(Boolean))assert.ok(card.translations.includes(t),'translation mismatch '+card.id);
   const expectedPos=card.id===903?['代名詞']:card.id===900?['名詞','ナ形']:['名詞'];
   assert.deepEqual(card.pos,expectedPos,'POS mismatch '+card.id);
  }

  const filterResult=await page.evaluate(()=>{
   showView('cards');
   const select=document.getElementById('cardPos');
   const hasPronounOption=Array.from(select.options).some(o=>o.value==='代名詞');
   select.value='代名詞';
   select.dispatchEvent(new Event('change',{bubbles:true}));
   const pronounIds=getCardPool().map(x=>String(x.id));
   select.value='名詞';
   select.dispatchEvent(new Event('change',{bubbles:true}));
   const nounIds=getCardPool().map(x=>String(x.id));
   return {hasPronounOption,pronounContains903:pronounIds.includes('903'),nounContains903:nounIds.includes('903')};
  });
  assert.deepEqual(filterResult,{hasPronounOption:true,pronounContains903:true,nounContains903:false});

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
     examplesVisible:d.exampleTranslations.every(x=>norm(text).includes(norm(x))),
     bodyTextLength:text.length
    });
   }
   return out;
  },IDS);
  assert.equal(rendered.length,12);
  const visibilityFailures=rendered.filter(x=>!(x.titleVisible&&x.glossVisible&&x.examplesVisible));
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
   const sentinel=JSON.stringify({meta:{sessionSize:10,streak:4,lastStudyDate:'2026-11-13'},vp:{'903':{status:'S',timesShown:3}},gp:{'90':{status:'X'}}});
   localStorage.setItem(key,sentinel);
   const roundTrip=localStorage.getItem(key)===sentinel;
   if(old===null)localStorage.removeItem(key);else localStorage.setItem(key,old);
   return {roundTrip,restored:localStorage.getItem(key)===old};
  });
  assert.equal(storage.roundTrip,true);
  assert.equal(storage.restored,true);
  assert.deepEqual(errors,[]);

  const result={pass:true,candidate_sha256:sha,candidate_bytes:bytes.length,counts:structural,reviewed_card_count:rendered.length,reviewed_cards:rendered,pos_filter:filterResult,responsive,storage,pageErrors:errors};
  fs.writeFileSync(path.join(WORK,'browser-results.json'),JSON.stringify(result,null,2)+'\n');
  process.stdout.write(JSON.stringify(result,null,2)+'\n');
 }finally{await browser.close();}
}
main().catch(error=>{console.error(error);process.exit(1);});
