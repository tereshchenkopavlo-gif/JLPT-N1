const {chromium}=require('playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const HTML='JLPT_N1_ukrainian_reading_v214.html',WORK='completion/v214-work';
const prepare=JSON.parse(fs.readFileSync(path.join(WORK,'prepare-results.json'),'utf8'));
const registry=JSON.parse(fs.readFileSync(path.join(WORK,'registry-results.json'),'utf8'));
const bytes=fs.readFileSync(HTML),sha=crypto.createHash('sha256').update(bytes).digest('hex');
assert.equal(sha,prepare.candidate_sha256); assert.equal(bytes.length,prepare.candidate_bytes);
assert.equal(prepare.pass,true); assert.equal(prepare.exact_rollback,true); assert.equal(registry.pass,true);
const IDS=[1632,1635,1637,1651,1654,1666,1675,1676,1679,1682,1688,1690];
const EXPECTED={
 1632:{word:'相互',gloss:'взаємність'},
 1635:{word:'総会',gloss:'загальні збори організації'},
 1637:{word:'草花',gloss:'квіткові трав’янисті рослини'},
 1651:{word:'損害',gloss:'шкода, збитки'},
 1654:{word:'妥協',definition:'自分の要求や基準を譲ること'},
 1666:{word:'滞納',translations:['Через тривалу заборгованість з орендної плати орендареві висунули вимогу звільнити помешкання.']},
 1675:{word:'大筋',translations:['З’ясувавши загальний напрям переговорів, домовилися перейти до узгодження деталей.']},
 1676:{word:'大口',gloss:'великий рот'},
 1679:{word:'大物',definition:'大きな物や獲物',translations:['Він привертає увагу як новачок, що вже має поставу впливової постаті.']},
 1682:{word:'脱税',translations:['На керівника компанії подали заяву до правоохоронних органів за підозрою у масштабному ухиленні від сплати податків.']},
 1688:{word:'鍛錬',definition:'金属を打ち鍛えること'},
 1690:{word:'弾力',gloss:'гнучкість'}
};
async function main(){
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:412,height:900}}),errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(pathToFileURL(path.resolve(HTML)).href);
  const structural=await page.evaluate(()=>({vocab:DEFAULT_VOCAB.length,grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,pairs:VOCAB_AUDITED_PAIRS.length,uniqueIds:new Set(DEFAULT_VOCAB.map(x=>Number(x.id))).size,allIdsPresent:DEFAULT_VOCAB.every(x=>VOCAB_DETAILS_BY_ID[String(x.id)]&&VOCAB_POS_BY_ID[String(x.id)])}));
  assert.deepEqual(structural,{vocab:3914,grammar:130,pairs:859,uniqueIds:3914,allIdsPresent:true});
  const data=await page.evaluate(ids=>ids.map(id=>{const d=VOCAB_DETAILS_BY_ID[String(id)];return{id,word:d.w,gloss:d.t,definition:d.m,translations:d.exampleTranslations,examples:d.examples,pos:VOCAB_POS_BY_ID[String(id)]}}),IDS);
  for(const card of data){
   const e=EXPECTED[card.id];
   assert.equal(card.word,e.word);
   if(e.gloss) assert.ok(card.gloss.includes(e.gloss));
   if(e.definition) assert.ok(card.definition.includes(e.definition));
   if(e.translations) for(const t of e.translations) assert.ok(card.translations.includes(t));
   assert.deepEqual(card.pos,['名詞']);
  }
  const pairData=await page.evaluate(()=>({
   p417:VOCAB_AUDITED_PAIRS.find(p=>p.a==='1651'&&p.b==='1652'),
   p421:VOCAB_AUDITED_PAIRS.find(p=>p.a==='1666'&&p.b==='1682')
  }));
  assert.ok(pairData.p417); assert.ok(pairData.p421);
  const rendered=await page.evaluate(async ids=>{
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
     definitionVisible:!EXPECTED[id].definition||norm(text).includes(norm(EXPECTED[id].definition)),
     usageVisible:!usageSample||norm(text).includes(norm(usageSample)),
     translationsVisible:d.exampleTranslations.every(x=>!x||norm(text).includes(norm(x))),
     examplesVisible:d.examples.every(x=>!x||norm(text).includes(norm(x))),
     textExcerpt:norm(text).slice(0,800)
    });
   }
   return out;
  },IDS);
  fs.writeFileSync(path.join(WORK,'rendered-debug.json'),JSON.stringify(rendered,null,2)+'\n');
  const failures=rendered.filter(x=>!(x.titleVisible&&x.glossVisible&&x.definitionVisible&&x.usageVisible&&x.translationsVisible&&x.examplesVisible));
  assert.equal(rendered.length,12);
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
  const result={pass:true,candidate_sha256:sha,candidate_bytes:bytes.length,counts:structural,reviewed_card_count:12,pending_card_count:0,reviewed_pair_indices:[417,421],responsive,storage,pageErrors:errors};
  fs.writeFileSync(path.join(WORK,'browser-results.json'),JSON.stringify(result,null,2)+'\n');
  process.stdout.write(JSON.stringify(result,null,2)+'\n');
 }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exit(1);});
