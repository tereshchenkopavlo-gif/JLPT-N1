const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const crypto=require('node:crypto');
const path=require('node:path');
const {pathToFileURL}=require('node:url');

const HTML='JLPT_N1_ukrainian_reading_v199.html';
const WORK='completion/v199-work';
const prepare=JSON.parse(fs.readFileSync(path.join(WORK,'prepare-results.json'),'utf8'));
const registry=JSON.parse(fs.readFileSync(path.join(WORK,'registry-results.json'),'utf8'));
const bytes=fs.readFileSync(HTML);
const sha=crypto.createHash('sha256').update(bytes).digest('hex');
assert.equal(sha,prepare.candidate_sha256);
assert.equal(prepare.pass,true);
assert.equal(prepare.exact_rollback,true);
assert.equal(registry.pass,true);

const IDS=[1042,1043,1044,1046,1048,1061,1063,1066,1067,1072,1073,1074];
const EXPECTED={
 1042:{word:'技能',gloss:'набута тренуванням або досвідом',usage:'опановує тренуванням і досвідом роботи'},
 1043:{word:'犠牲',translations:['Дедалі більше людей ставлять під сумнів спосіб життя, за якого заради роботи жертвують сімейним життям.']},
 1044:{word:'疑惑',translations:['У парламенті наполегливо вимагали пояснень щодо підозр у незаконних грошових внесках політику.']},
 1046:{word:'義理',gloss:'мачуха чи прийомна мати'},
 1048:{word:'議決',translations:['Правління мало ухвалити новий план діяльності.']},
 1061:{word:'急患',translations:['У лікарні лікарі чергують цілодобово, щоб приймати пацієнтів, які потребують невідкладної допомоги.','На щастя, стан доставленого пацієнта стабільний.']},
 1063:{word:'急募',translations:['Через нестачу персоналу компанія вирішила терміново набрати продавців на підробіток.']},
 1066:{word:'救済',usage:'виправити несправедливість'},
 1067:{word:'究極',translations:['Він прагнув до страви, яку можна було б назвати вершиною смаку.']},
 1072:{word:'拒絶',definition:'また、移植された臓器などを体が異物として受け入れないこと。',usage:'移植片の拒絶反応'},
 1073:{word:'拒否',translations:['Профспілка дала зрозуміти, що готова відхилити запропоновані компанією умови.']},
 1074:{word:'挙式',translations:['Вони оголосили, що планують провести весільну церемонію наступної весни у святилищі в рідному краї.']}
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
   if(e.translations)for(const t of e.translations)assert.ok(card.translations.includes(t),'translation mismatch '+card.id);
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
     usageVisible:norm(text).includes(norm(d.usage.slice(0,Math.min(d.usage.length,45)))),
     examplesVisible:d.exampleTranslations.every(x=>norm(text).includes(norm(x))),
     definitionVisible:id===1072?norm(text).includes(norm('また、移植された臓器などを体が異物として受け入れないこと。')):true,
     bodyTextLength:text.length
    });
   }
   return out;
  },IDS);
  assert.equal(rendered.length,12);
  const failures=rendered.filter(x=>!(x.titleVisible&&x.glossVisible&&x.usageVisible&&x.examplesVisible&&x.definitionVisible));
  if(failures.length)console.error('Rendered visibility diagnostics:',JSON.stringify(failures,null,2));
  assert.equal(failures.length,0);

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
   const sentinel=JSON.stringify({meta:{sessionSize:10,streak:4,lastStudyDate:'2026-11-13'},vp:{'1042':{status:'S',timesShown:3}},gp:{'90':{status:'X'}}});
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
