const {chromium}=require("playwright"),assert=require("node:assert/strict"),fs=require("node:fs"),crypto=require("node:crypto"),path=require("node:path");
const {pathToFileURL}=require("node:url"),HTML="JLPT_N1_ukrainian_reading_v224.html",BASE="JLPT_N1_ukrainian_reading_v223.html",WORK="completion/v224-work";
const prep=JSON.parse(fs.readFileSync(path.join(WORK,"prepare-results.json"),"utf8"));
const IDS=[3522,3525,3532,3537,3548,3556,3561,3565,3568,3569,3580,3588];
const EXPECTED={
"3522":{word:"エントリー",reading:"えんとりー",pos:["名詞"]},
"3525":{word:"オートマチック",reading:"おーとまちっく",pos:["名詞"]},
"3532":{word:"キャッチ",reading:"きゃっち",pos:["名詞"]},
"3537":{word:"シークレット",reading:"しーくれっと",pos:["名詞"],gloss:"таємниця; секрет; секретний, прихований"},
"3548":{word:"クローズアップ",reading:"くろーずあっぷ",pos:["名詞"]},
"3556":{word:"セレモニー",reading:"せれもにー",pos:["名詞"]},
"3561":{word:"ジャンボ",reading:"じゃんぼ",pos:["名詞"]},
"3565":{word:"タイムリー",reading:"たいむりー",pos:["名詞"]},
"3568":{word:"ダメージ",reading:"だめーじ",pos:["名詞"]},
"3569":{word:"コマーシャル",reading:"こまーしゃる",pos:["名詞"]},
"3580":{word:"チャンピオン",reading:"ちゃんぴおん",pos:["名詞"]},
"3588":{word:"ストック",reading:"すとっく",pos:["名詞"]}
};
(async()=>{
 const bytes=fs.readFileSync(HTML),sha=crypto.createHash("sha256").update(bytes).digest("hex");
 assert.equal(sha,prep.candidate_sha256);assert.equal(bytes.length,prep.candidate_bytes);
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:412,height:900}}),errors=[];
  page.on("pageerror",e=>errors.push(String(e)));
  await page.goto(pathToFileURL(path.resolve(HTML)).href);
  const structural=await page.evaluate(()=>({vocab:DEFAULT_VOCAB.length,grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,pairs:VOCAB_AUDITED_PAIRS.length,uniqueIds:new Set(DEFAULT_VOCAB.map(x=>Number(x.id))).size,allIdsPresent:DEFAULT_VOCAB.every(x=>VOCAB_DETAILS_BY_ID[String(x.id)]&&VOCAB_POS_BY_ID[String(x.id)])}));
  assert.deepEqual(structural,{vocab:3914,grammar:130,pairs:859,uniqueIds:3914,allIdsPresent:true});
  const data=await page.evaluate(ids=>ids.map(id=>{const v=DEFAULT_VOCAB.find(x=>Number(x.id)===id),d=VOCAB_DETAILS_BY_ID[String(id)];return{id,word:d.w,reading:v.r,pos:VOCAB_POS_BY_ID[String(id)],gloss:d.t,meaning:d.m,usage:d.usage,examples:d.examples,translations:d.exampleTranslations};}),IDS);
  for(const c of data){const e=EXPECTED[String(c.id)];assert.equal(c.word,e.word);assert.equal(c.reading,e.reading);assert.deepEqual(c.pos,e.pos);assert.ok(c.usage&&c.usage.length>0);if(e.gloss)assert.equal(c.gloss,e.gloss);assert.equal(c.examples.length,2);assert.equal(c.translations.length,2);}
  const pairData=await page.evaluate(()=>[789,790].map(i=>({index:i,...VOCAB_AUDITED_PAIRS[i]})));
  const expectedPairs=[["3526","3529"],["3534","3535"]];
  pairData.forEach((p,i)=>{assert.equal(p.a,expectedPairs[i][0]);assert.equal(p.b,expectedPairs[i][1]);assert.ok(p.note);});
  const rendered=await page.evaluate(async ids=>{showView("cards");const out=[],norm=x=>String(x).replaceAll("\n"," ").replaceAll("\r"," ").replaceAll("\t"," ").split(" ").filter(Boolean).join(" ");for(const id of ids){await openCardDetail("v",id);await new Promise(r=>setTimeout(r,35));const body=document.getElementById("cardDetailBody"),txt=body?.innerText||"",d=VOCAB_DETAILS_BY_ID[String(id)];out.push({id,word:d.w,titleVisible:norm(txt).includes(norm(d.w)),definitionVisible:norm(txt).includes(norm(d.m)),usageVisible:norm(txt).includes("用法・接続"),examplesVisible:d.examples.every(x=>norm(txt).includes(norm(x))),translationsVisible:d.exampleTranslations.every(x=>norm(txt).includes(norm(x)))});}return out;},IDS);
  fs.writeFileSync(path.join(WORK,"rendered-debug.json"),JSON.stringify(rendered,null,2)+"\n");
  assert.ok(rendered.every(x=>x.titleVisible&&x.definitionVisible&&x.usageVisible&&x.examplesVisible&&x.translationsVisible));
  const basePage=await browser.newPage();await basePage.goto(pathToFileURL(path.resolve(BASE)).href);
  const stableBase=await basePage.evaluate(()=>({vocab:JSON.stringify(DEFAULT_VOCAB),pos:JSON.stringify(VOCAB_POS_BY_ID),grammar:JSON.stringify(GRAMMAR_DETAILS_BY_ID),pairs:JSON.stringify(VOCAB_AUDITED_PAIRS),meaning:JSON.stringify(REVIEWED_MEANING_QUIZZES),reading:JSON.stringify(REVIEWED_READING_OPTIONS),kana:JSON.stringify(VOCAB_KANA_EXAMPLE_TARGETS),targets:JSON.stringify(REVIEWED_EXAMPLE_TARGETS)}));
  const stableCandidate=await page.evaluate(()=>({vocab:JSON.stringify(DEFAULT_VOCAB),pos:JSON.stringify(VOCAB_POS_BY_ID),grammar:JSON.stringify(GRAMMAR_DETAILS_BY_ID),pairs:JSON.stringify(VOCAB_AUDITED_PAIRS),meaning:JSON.stringify(REVIEWED_MEANING_QUIZZES),reading:JSON.stringify(REVIEWED_READING_OPTIONS),kana:JSON.stringify(VOCAB_KANA_EXAMPLE_TARGETS),targets:JSON.stringify(REVIEWED_EXAMPLE_TARGETS)}));
  assert.deepEqual(stableCandidate,stableBase);
  const responsive=[];for(const width of [360,412,1280]){await page.setViewportSize({width,height:900});const d=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth}));responsive.push({...d,overflow:d.scrollWidth>width||d.bodyWidth>width});}
  assert.ok(responsive.every(x=>!x.overflow));
  const storage=await page.evaluate(()=>{const key="choba_n1uk_storage_v1",old=localStorage.getItem(key),sentinel=JSON.stringify({meta:{sessionSize:10,streak:5,lastStudyDate:"2026-11-14"},vp:{"3522":{status:"S",timesShown:2}},gp:{"90":{status:"X"}}});localStorage.setItem(key,sentinel);const roundTrip=localStorage.getItem(key)===sentinel;if(old===null)localStorage.removeItem(key);else localStorage.setItem(key,old);return{roundTrip,restored:localStorage.getItem(key)===old};});
  assert.ok(storage.roundTrip&&storage.restored);assert.deepEqual(errors,[]);
  const result={pass:true,candidate_sha256:sha,candidate_bytes:bytes.length,counts:structural,reviewed_card_count:12,fixed_rechecked_count:1,reviewed_unchanged_count:7,blocked_count:4,pair_reviewed_count:2,pair_changed_count:0,responsive,storage,stablePoolsUnchanged:true,pageErrors:errors};
  fs.writeFileSync(path.join(WORK,"browser-results.json"),JSON.stringify(result,null,2)+"\n");console.log(JSON.stringify(result,null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
