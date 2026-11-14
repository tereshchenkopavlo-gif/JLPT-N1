const {chromium}=require("playwright"),assert=require("node:assert/strict"),fs=require("node:fs"),crypto=require("node:crypto"),path=require("node:path");
const {pathToFileURL}=require("node:url"),HTML="JLPT_N1_ukrainian_reading_v225.html",BASE="JLPT_N1_ukrainian_reading_v224.html",WORK="completion/v225-work";
const prep=JSON.parse(fs.readFileSync(path.join(WORK,"prepare-results.json"),"utf8"));
const IDS=[3589,3594,3599,3601,3607,3614,3635,3636,3637,3642,3644,3646];
const EXPECTED={
"3589":{word:"データベース",reading:"でーたべーす",pos:["名詞"]},
"3594":{word:"ストレート",reading:"すとれーと",pos:["名詞"]},
"3599":{word:"デビュー",reading:"でびゅー",pos:["名詞"]},
"3601":{word:"ペア",reading:"ぺあ",pos:["名詞"]},
"3607":{word:"ボイコット",reading:"ぼいこっと",pos:["名詞"]},
"3614":{word:"トリック",reading:"とりっく",pos:["名詞"]},
"3635":{word:"ノルマ",reading:"のるま",pos:["名詞"]},
"3636":{word:"プライベート",reading:"ぷらいべーと",pos:["名詞"]},
"3637":{word:"ムード",reading:"むーど",pos:["名詞"]},
"3642":{word:"ブランク",reading:"ぶらんく",pos:["名詞"]},
"3644":{word:"ハーモニー",reading:"はーもにー",pos:["名詞"]},
"3646":{word:"モダン",reading:"もだん",pos:["名詞"]}
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
  for(const c of data){const e=EXPECTED[String(c.id)];assert.equal(c.word,e.word);assert.equal(c.reading,e.reading);assert.deepEqual(c.pos,e.pos);assert.ok(c.usage&&c.usage.length>0);assert.equal(c.examples.length,2);assert.equal(c.translations.length,2);}
  const pairData=await page.evaluate(()=>[791,792].map(i=>({index:i,...VOCAB_AUDITED_PAIRS[i]})));
  const expectedPairs=[["3530","3577"],["3554","3557"]];
  pairData.forEach((p,i)=>{assert.equal(p.a,expectedPairs[i][0]);assert.equal(p.b,expectedPairs[i][1]);assert.ok(p.note);});
  const rendered=await page.evaluate(async ids=>{showView("cards");const out=[],norm=x=>String(x).replaceAll("\n"," ").replaceAll("\r"," ").replaceAll("\t"," ").split(" ").filter(Boolean).join(" ");for(const id of ids){await openCardDetail("v",id);await new Promise(r=>setTimeout(r,35));const body=document.getElementById("cardDetailBody"),txt=body?.innerText||"",d=VOCAB_DETAILS_BY_ID[String(id)];out.push({id,word:d.w,titleVisible:norm(txt).includes(norm(d.w)),definitionVisible:norm(txt).includes(norm(d.m)),usageVisible:norm(txt).includes("用法・接続"),examplesVisible:d.examples.every(x=>norm(txt).includes(norm(x))),translationsVisible:d.exampleTranslations.every(x=>norm(txt).includes(norm(x)))});}return out;},IDS);
  fs.writeFileSync(path.join(WORK,"rendered-debug.json"),JSON.stringify(rendered,null,2)+"\n");
  assert.ok(rendered.every(x=>x.titleVisible&&x.definitionVisible&&x.usageVisible&&x.examplesVisible&&x.translationsVisible));
  const basePage=await browser.newPage();await basePage.goto(pathToFileURL(path.resolve(BASE)).href);
  const stableBase=await basePage.evaluate(()=>({vocab:JSON.stringify(DEFAULT_VOCAB),details:JSON.stringify(VOCAB_DETAILS_BY_ID),pos:JSON.stringify(VOCAB_POS_BY_ID),grammar:JSON.stringify(GRAMMAR_DETAILS_BY_ID),pairs:JSON.stringify(VOCAB_AUDITED_PAIRS),meaning:JSON.stringify(REVIEWED_MEANING_QUIZZES),reading:JSON.stringify(REVIEWED_READING_OPTIONS),kana:JSON.stringify(VOCAB_KANA_EXAMPLE_TARGETS),targets:JSON.stringify(REVIEWED_EXAMPLE_TARGETS)}));
  const stableCandidate=await page.evaluate(()=>({vocab:JSON.stringify(DEFAULT_VOCAB),details:JSON.stringify(VOCAB_DETAILS_BY_ID),pos:JSON.stringify(VOCAB_POS_BY_ID),grammar:JSON.stringify(GRAMMAR_DETAILS_BY_ID),pairs:JSON.stringify(VOCAB_AUDITED_PAIRS),meaning:JSON.stringify(REVIEWED_MEANING_QUIZZES),reading:JSON.stringify(REVIEWED_READING_OPTIONS),kana:JSON.stringify(VOCAB_KANA_EXAMPLE_TARGETS),targets:JSON.stringify(REVIEWED_EXAMPLE_TARGETS)}));
  assert.deepEqual(stableCandidate,stableBase);
  const responsive=[];for(const width of [360,412,1280]){await page.setViewportSize({width,height:900});const d=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth}));responsive.push({...d,overflow:d.scrollWidth>width||d.bodyWidth>width});}
  assert.ok(responsive.every(x=>!x.overflow));
  const storage=await page.evaluate(()=>{const key="choba_n1uk_storage_v1",old=localStorage.getItem(key),sentinel=JSON.stringify({meta:{sessionSize:10,streak:5,lastStudyDate:"2026-11-14"},vp:{"3589":{status:"S",timesShown:2}},gp:{"90":{status:"X"}}});localStorage.setItem(key,sentinel);const roundTrip=localStorage.getItem(key)===sentinel;if(old===null)localStorage.removeItem(key);else localStorage.setItem(key,old);return{roundTrip,restored:localStorage.getItem(key)===old};});
  assert.ok(storage.roundTrip&&storage.restored);assert.deepEqual(errors,[]);
  const result={pass:true,candidate_sha256:sha,candidate_bytes:bytes.length,counts:structural,reviewed_card_count:12,credited_count:9,blocked_count:3,pair_reviewed_count:2,pair_changed_count:0,responsive,storage,stablePoolsUnchanged:true,pageErrors:errors};
  fs.writeFileSync(path.join(WORK,"browser-results.json"),JSON.stringify(result,null,2)+"\n");console.log(JSON.stringify(result,null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
