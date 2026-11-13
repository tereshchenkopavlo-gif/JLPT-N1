const {chromium}=require('playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const HTML='JLPT_N1_ukrainian_reading_v215.html',WORK='completion/v215-work';
const prepare=JSON.parse(fs.readFileSync(path.join(WORK,'prepare-results.json'),'utf8'));
const registry=JSON.parse(fs.readFileSync(path.join(WORK,'registry-results.json'),'utf8'));
const bytes=fs.readFileSync(HTML),sha=crypto.createHash('sha256').update(bytes).digest('hex');
assert.equal(sha,prepare.candidate_sha256); assert.equal(bytes.length,prepare.candidate_bytes);
assert.equal(prepare.pass,true); assert.equal(prepare.exact_rollback,true); assert.equal(registry.pass,true);
const IDS=[1019,1028,1078,1082,1089,1093,1191,1255,1258,1260,1270,1272,1276,1280,1285,1290,1292,1293,1296];
const EXPECTED={
  "1019": {
    "word": "気心",
    "translations": [
      "Коли працюєш із товаришами, чию вдачу добре знаєш, порозумітися значно легше."
    ]
  },
  "1028": {
    "word": "規範",
    "translations": [
      "Від державних службовців вимагають високих етичних норм, що слугують взірцем для суспільства."
    ]
  },
  "1078": {
    "word": "漁村",
    "translations": [
      "У цьому маленькому рибальському селі людно через туристів, які приїздять сюди за свіжими морепродуктами.",
      "У рибальських селах, де населення скорочується, гостро стоїть проблема залучення людей, які продовжать рибальську справу."
    ]
  },
  "1082": {
    "word": "凶作",
    "translations": [
      "Через затяжні дощі цього року був неврожай рису."
    ]
  },
  "1089": {
    "word": "強行",
    "translations": [
      "Будівельні роботи провели попри негоду, що викликало занепокоєння щодо безпеки працівників."
    ]
  },
  "1093": {
    "word": "恐慌",
    "glosses": [
      "паніка",
      "世界恐慌／世界大恐慌"
    ]
  },
  "1191": {
    "word": "厳禁",
    "translations": [
      "У цій зоні суворо заборонено користуватися будь-якими джерелами займання, тому куріння категорично не допускається."
    ]
  },
  "1255": {
    "word": "合併",
    "glosses": [
      "у медицині — поєднання з іншим захворюванням"
    ]
  },
  "1258": {
    "word": "告訴",
    "translations": [
      "Потерпілий подав кримінальну скаргу проти недобросовісного суб’єкта господарювання за підозрою в шахрайстві."
    ]
  },
  "1260": {
    "word": "国防",
    "translations": [
      "У парламенті розгорнулися дебати щодо того, яким має бути бюджет на національну оборону."
    ]
  },
  "1270": {
    "word": "混沌",
    "translations": [
      "За хаотичної ситуації, коли інформація надходила безладно, працівники на місцях ледве встигали реагувати."
    ]
  },
  "1272": {
    "word": "差額",
    "translations": [
      "Різницю між кошторисом і фактичними витратами остаточно розрахують пізніше."
    ]
  },

  "1276": {"word":"挫折","translations":["Він не здався після першої невдачі й наполегливо продовжив спроби — саме це допомогло йому зрости."]},
  "1280": {"word":"再三","usage":"часто вживають прислівниково"},
  "1285": {"word":"採算","translations":["Ця лінія не окупається, тож лунають думки, що її, можливо, доведеться скасувати."]},
  "1290": {"word":"歳月","translations":["Минуло багато років, і місцеві жителі відродили традиційне свято, яке вже перестали проводити."]},
  "1292": {"word":"細菌","glosses":["представник групи прокаріотів"],"definition":"古細菌とは別の生物群に属し"},
  "1293": {"word":"細工","definition":"そのようにして作った物"},
  "1296": {"word":"在職","translations":["У цій компанії розмір виплати після завершення роботи визначають залежно від стажу."]}
};
async function main(){
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:412,height:900}}),errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(pathToFileURL(path.resolve(HTML)).href);
  const structural=await page.evaluate(()=>({vocab:DEFAULT_VOCAB.length,grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,pairs:VOCAB_AUDITED_PAIRS.length,uniqueIds:new Set(DEFAULT_VOCAB.map(x=>Number(x.id))).size,allIdsPresent:DEFAULT_VOCAB.every(x=>VOCAB_DETAILS_BY_ID[String(x.id)]&&VOCAB_POS_BY_ID[String(x.id)])}));
  assert.deepEqual(structural,{vocab:3914,grammar:130,pairs:859,uniqueIds:3914,allIdsPresent:true});
  const data=await page.evaluate(ids=>ids.map(id=>{const d=VOCAB_DETAILS_BY_ID[String(id)];return{id,word:d.w,gloss:d.t,definition:d.m,translations:d.exampleTranslations,examples:d.examples,usage:d.usage,pos:VOCAB_POS_BY_ID[String(id)]}}),IDS);
  for(const card of data){
   const e=EXPECTED[card.id];
   assert.equal(card.word,e.word);
   if(e.gloss) assert.ok(card.gloss.includes(e.gloss));
   if(e.glosses) for(const g of e.glosses) assert.ok(card.gloss.includes(g));
   if(e.definition) assert.ok(card.definition.includes(e.definition));
   if(e.usage) assert.ok(card.usage.includes(e.usage));
   if(e.translations) for(const t of e.translations) assert.ok(card.translations.includes(t));
   assert.deepEqual(card.pos,['名詞']);
  }
  const rendered=await page.evaluate(async ({ids,expected})=>{
   showView('cards'); const out=[];
   const norm=x=>String(x).replace(/\s+/g,' ').trim();
   for(const id of ids){
    await openCardDetail('v',id); await new Promise(resolve=>setTimeout(resolve,40));
    const body=document.getElementById('cardDetailBody'),text=body?.innerText||'',d=VOCAB_DETAILS_BY_ID[String(id)];
    const usageSample=(d.usage||'').match(/[一-龯々〆〇ぁ-んァ-ヶー・、。／（）「」]+/u)?.[0]||'';
    out.push({
     id,word:d.w,
     titleVisible:norm(text).includes(norm(d.w)),
     glossVisible:!d.t||norm(text).includes(norm(d.t.split(/[;\n]/)[0])),
     definitionVisible:!expected[id].definition||norm(text).includes(norm(expected[id].definition)),
     usageVisible:!usageSample||norm(text).includes(norm(usageSample)),
     translationsVisible:d.exampleTranslations.every(x=>!x||norm(text).includes(norm(x))),
     examplesVisible:d.examples.every(x=>!x||norm(text).includes(norm(x))),
     textExcerpt:norm(text).slice(0,800)
    });
   }
   return out;
  },{ids:IDS,expected:EXPECTED});
  fs.writeFileSync(path.join(WORK,'rendered-debug.json'),JSON.stringify(rendered,null,2)+'\n');
  const failures=rendered.filter(x=>!(x.titleVisible&&x.glossVisible&&x.definitionVisible&&x.usageVisible&&x.translationsVisible&&x.examplesVisible));
  assert.equal(rendered.length,19);
  if(failures.length) throw new Error('Card detail visibility mismatches: '+JSON.stringify(failures));
  const responsive=[];
  for(const width of [360,412,1280]){
   await page.setViewportSize({width,height:900});
   const d=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth}));
   responsive.push({...d,overflow:d.scrollWidth>width||d.bodyWidth>width});
  }
  assert.equal(responsive.every(x=>!x.overflow),true);
  const storage=await page.evaluate(()=>{
   const key='choba_n1uk_storage_v1',old=localStorage.getItem(key);
   const sentinel=JSON.stringify({meta:{sessionSize:10,streak:4,lastStudyDate:'2026-11-14'},vp:{'1632':{status:'S',timesShown:3}},gp:{'90':{status:'X'}}});
   localStorage.setItem(key,sentinel);
   const roundTrip=localStorage.getItem(key)===sentinel;
   if(old===null)localStorage.removeItem(key);else localStorage.setItem(key,old);
   return{roundTrip,restored:localStorage.getItem(key)===old};
  });
  assert.equal(storage.roundTrip,true); assert.equal(storage.restored,true); assert.deepEqual(errors,[]);
  const result={pass:true,candidate_sha256:sha,candidate_bytes:bytes.length,counts:structural,reviewed_card_count:19,pending_card_count:0,reviewed_pair_indices:[],responsive,storage,pageErrors:errors};
  fs.writeFileSync(path.join(WORK,'browser-results.json'),JSON.stringify(result,null,2)+'\n');
  process.stdout.write(JSON.stringify(result,null,2)+'\n');
 }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exit(1);});
