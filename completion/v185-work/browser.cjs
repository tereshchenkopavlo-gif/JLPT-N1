const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const crypto=require('node:crypto');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const HTML='JLPT_N1_ukrainian_reading_v185.html';
const prepare=JSON.parse(fs.readFileSync('completion/v185-work/prepare-results.json','utf8'));
const bytes=fs.readFileSync(HTML);
const sha=crypto.createHash('sha256').update(bytes).digest('hex');
assert.equal(sha,prepare.candidate_sha256);
assert.equal(prepare.pass,true); assert.equal(prepare.exact_rollback,true);
const IDS=[525,530,533,540,541,544,547,549,550,552,557,563];
const EXPECTED={
525:{word:'抜ける',head:'помітно вирізнятися серед інших',usage:'бути на голову вище'},
530:{word:'埋める',meaning:'うめる：穴や隙間に物を入れて満たす。不足分を補う。うずめる：物を土や灰などの中に入れて外から見えなくする。また、物や人で場所をいっぱいにする。'},
533:{word:'誘う',meaning:'さそう：一緒に行動するように相手に呼びかける。また、ある気持ちや行動を引き起こす。いざなう：相手をある場所へ導くように誘い、連れて行く。',usage:'Обидва наведені приклади — читання さそう.'},
540:{word:'冷やす',head:'охолодити голову, заспокоїтися'},
541:{word:'励ます',example:'Одна фраза старшого колеги, який підбадьорив його, стала для нього поворотним моментом.'},
544:{word:'いい加減'},547:{word:'気楽',example:'Є велика різниця між тим, щоб висловлювати думку без особливого тягаря відповідальності, і тим, щоб ухвалювати рішення, за які відповідаєш.'},
549:{word:'気軽',head:'без вагань і зайвих церемоній'},550:{word:'わがまま'},
552:{word:'確か',example:'Його безсумнівну майстерність широко визнають у галузі.'},557:{word:'結構'},
563:{word:'手軽',meaning:'手間や費用をあまりかけずに行える様子。'}
};
async function main(){
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:412,height:900}});
  const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(pathToFileURL(path.resolve(HTML)).href);
  const structural=await page.evaluate(()=>{const ids=DEFAULT_VOCAB.map(x=>Number(x.id));return {vocab:DEFAULT_VOCAB.length,grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,pairs:VOCAB_AUDITED_PAIRS.length,uniqueIds:new Set(ids).size,allIdsPresent:ids.every(id=>VOCAB_DETAILS_BY_ID[String(id)]&&VOCAB_POS_BY_ID[String(id)])};});
  assert.deepEqual(structural,{vocab:3914,grammar:130,pairs:859,uniqueIds:3914,allIdsPresent:true});
  const data=await page.evaluate(ids=>ids.map(id=>{const d=VOCAB_DETAILS_BY_ID[String(id)];return {id,word:d.w,pos:VOCAB_POS_BY_ID[String(id)],m:d.m,t:d.t,usage:d.usage,examples:d.examples,translations:d.exampleTranslations};}),IDS);
  for(const card of data){const e=EXPECTED[card.id];assert.equal(card.word,e.word);if(e.head)assert.ok(card.t.includes(e.head));if(e.meaning)assert.ok(card.m.includes(e.meaning));if(e.usage)assert.ok(card.usage.includes(e.usage));if(e.example)assert.ok(card.translations.includes(e.example));}
  for(const id of [544,550,552,557])assert.deepEqual(data.find(x=>x.id===id).pos,['ナ形'],'C11-dependent POS remains unchanged');
  const rendered=await page.evaluate(async ids=>{showView('cards');const out=[];for(const id of ids){await openCardDetail('v',id);const body=document.getElementById('cardDetailBody');const text=body.innerText;const d=VOCAB_DETAILS_BY_ID[String(id)];const norm=x=>String(x).replace(/\s+/g,' ').trim();out.push({id,word:d.w,titleVisible:norm(text).includes(norm(d.w)),translationVisible:d.t.split(';').every(part=>norm(text).includes(norm(part))),examplesVisible:d.exampleTranslations.every(t=>norm(text).includes(norm(t))),bodyTextLength:text.length});}return out;},IDS);
  assert.equal(rendered.length,12);assert.equal(rendered.every(x=>x.titleVisible&&x.translationVisible&&x.examplesVisible),true);
  const responsive=[];for(const width of [360,412,1280]){await page.setViewportSize({width,height:900});await page.evaluate(()=>window.scrollTo(0,0));const d=await page.evaluate(()=>({width:window.innerWidth,scrollWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth}));responsive.push({...d,overflow:d.scrollWidth>width||d.bodyWidth>width});}
  assert.equal(responsive.every(x=>!x.overflow),true);
  const storage=await page.evaluate(()=>{const key='choba_n1uk_storage_v1';const old=localStorage.getItem(key);const sentinel=JSON.stringify({meta:{sessionSize:10,streak:4,lastStudyDate:'2026-11-13'},vp:{'525':{status:'S',timesShown:3}},gp:{'90':{status:'X'}}});localStorage.setItem(key,sentinel);const roundTrip=localStorage.getItem(key)===sentinel;if(old===null)localStorage.removeItem(key);else localStorage.setItem(key,old);return {roundTrip,restored:localStorage.getItem(key)===old};});
  assert.equal(storage.roundTrip,true);assert.equal(storage.restored,true);assert.deepEqual(errors,[]);
  const result={pass:true,candidate_sha256:sha,candidate_bytes:bytes.length,counts:structural,reviewed_card_count:rendered.length,reviewed_cards:rendered,responsive,storage,pageErrors:errors};
  fs.writeFileSync('completion/v185-work/browser-results.json',JSON.stringify(result,null,2)+'\n');process.stdout.write(JSON.stringify(result,null,2)+'\n');
 }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exit(1);});
