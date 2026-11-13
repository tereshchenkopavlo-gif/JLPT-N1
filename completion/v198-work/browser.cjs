const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const crypto=require('node:crypto');
const path=require('node:path');
const {pathToFileURL}=require('node:url');

const HTML='JLPT_N1_ukrainian_reading_v198.html';
const WORK='completion/v198-work';
const prepare=JSON.parse(fs.readFileSync(path.join(WORK,'prepare-results.json'),'utf8'));
const registry=JSON.parse(fs.readFileSync(path.join(WORK,'registry-results.json'),'utf8'));
const bytes=fs.readFileSync(HTML);
const sha=crypto.createHash('sha256').update(bytes).digest('hex');
assert.equal(sha,prepare.candidate_sha256);
assert.equal(prepare.pass,true);
assert.equal(prepare.exact_rollback,true);
assert.equal(registry.pass,true);

const IDS=[1015,1016,1018,1021,1023,1024,1025,1026,1027,1030,1031,1034];
const EXPECTED={
 1015:{word:'機材'},
 1016:{word:'帰省'},
 1018:{word:'気質',translations:['Він, як справжній майстер, ніколи не відвантажував вироби, доки не був цілком задоволений результатом.']},
 1021:{word:'気配'},
 1023:{word:'気品'},
 1024:{word:'気風',translations:['','Ініціативний дух, притаманний цьому краю, сприяв появі багатьох підприємців.']},
 1025:{word:'気流'},
 1026:{word:'祈願',translations:['','На будівельному майданчику провели традиційний обряд перед початком робіт, просячи про їхню безпеку.']},
 1027:{word:'規定'},
 1030:{word:'記述'},
 1031:{word:'貴族'},
 1034:{word:'起動',translations:['','Нове обладнання для виробництва електроенергії запустили, і почалося її постачання в регіон.']}
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
   const sentinel=JSON.stringify({meta:{sessionSize:10,streak:4,lastStudyDate:'2026-11-13'},vp:{'1015':{status:'S',timesShown:3}},gp:{'90':{status:'X'}}});
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
