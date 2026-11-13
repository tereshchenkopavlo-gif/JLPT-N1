const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const crypto=require('node:crypto');
const path=require('node:path');
const {pathToFileURL}=require('node:url');

const HTML='JLPT_N1_ukrainian_reading_v188.html';
const WORK='completion/v188-work';
const prepare=JSON.parse(fs.readFileSync(path.join(WORK,'prepare-results.json'),'utf8'));
const registry=JSON.parse(fs.readFileSync(path.join(WORK,'registry-results.json'),'utf8'));
const bytes=fs.readFileSync(HTML);
const sha=crypto.createHash('sha256').update(bytes).digest('hex');
assert.equal(sha,prepare.candidate_sha256);
assert.equal(prepare.pass,true);
assert.equal(prepare.exact_rollback,true);
assert.equal(registry.pass,true);

const IDS=[677,683,685,687,691,692,697,701,703,706,707,708];
const EXPECTED={
 677:{word:'ホール',definition:'また、ゴルフでボールを入れる穴。',translations:['Урочиста церемонія відбулася з великим розмахом у великій залі міста.']},
 683:{word:'マッサージ',translations:['','Йому помасажували затерплу спину.']},
 685:{word:'デザイン',translations:['','Магазин, дизайн якого розробив молодий дизайнер, привернув увагу галузі.']},
 687:{word:'サポート',translations:['Фахівець, спеціально закріплений за цим завданням, забезпечуватиме постійний супровід після впровадження.']},
 691:{word:'ネックレス',translations:['Вона дуже дорожить намистом, що дісталося їй від бабусі, й носить його.','На виставці популярністю користувалися намиста, виготовлені майстрами вручну.']},
 692:{word:'メロディー',translations:['Мелодія головної пісні до фільму глибоко запам’яталася слухачам.','Люди в залі тихо вслухалися в прекрасну мелодію.']},
 697:{word:'闇',gloss:'темрява, морок; тіньовий світ',translations:['','Щоб припинити незаконну приховану торгівлю, органи влади посилюють розслідування.']},
 701:{word:'沖',gloss:'водний простір на віддалі від берега (у морі чи озері)'},
 703:{word:'核',definition:'原子の中心部や、細胞内で遺伝情報を含む構造。'},
 706:{word:'幹',definition:'木の中心にある太い部分で、枝を支える。',usage:'幹が太い, 幹に触れる'},
 707:{word:'管',usage:'単独の管はくだと読む。複合語ではかんとなることが多い: 水道管（すいどうかん）。'},
 708:{word:'癌',gloss:'руйнівна вада, що підточує організацію'}
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
    const d=VOCAB_DETAILS_BY_ID[String(id)];
    const norm=x=>String(x).replace(/\s+/g,' ').trim();
    out.push({
     id,word:d.w,
     titleVisible:norm(text).includes(norm(d.w)),
     glossVisible:d.t.split(';').map(x=>x.trim()).filter(Boolean).every(x=>norm(text).includes(norm(x))),
     usageVisible:d.usage.split(/[.!?。]/).map(x=>norm(x)).filter(x=>x.length>8).every(x=>norm(text).includes(x)),
     examplesVisible:d.exampleTranslations.every(x=>norm(text).includes(norm(x))),
     bodyTextLength:text.length,bodyText:text
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
   const sentinel=JSON.stringify({meta:{sessionSize:10,streak:4,lastStudyDate:'2026-11-13'},vp:{'677':{status:'S',timesShown:3}},gp:{'90':{status:'X'}}});
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
