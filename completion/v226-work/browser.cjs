const {chromium}=require("playwright"),assert=require("node:assert/strict"),fs=require("node:fs"),crypto=require("node:crypto"),path=require("node:path");
const {pathToFileURL}=require("node:url");
const HTML="JLPT_N1_ukrainian_reading_v226.html",BASE="JLPT_N1_ukrainian_reading_v225.html",WORK="completion/v226-work";
const prep=JSON.parse(fs.readFileSync(path.join(WORK,"prepare-results.json"),"utf8"));
const IDS=[3652,3654,3657,3668,3671,3677,3679,3680,3681,3682,3685,3694];
const EXPECTED={
"3652":{word:"ユニーク",reading:"ゆにーく",pos:["名詞"]},"3654":{word:"ブロック",reading:"ぶろっく",pos:["名詞"]},
"3657":{word:"プロフィール",reading:"ぷろふぃーる",pos:["名詞"]},"3668":{word:"リベンジ",reading:"りべんじ",pos:["名詞"],short:"する"},
"3671":{word:"リミット",reading:"りみっと",pos:["名詞"]},"3677":{word:"ルーズ",reading:"るーず",pos:["名詞"]},
"3679":{word:"ワンマン",reading:"わんまん",pos:["名詞"]},"3680":{word:"あるいは",reading:"あるいは",pos:["副詞","接続詞"]},
"3681":{word:"その上",reading:"そのうえ",pos:["接続詞"]},"3682":{word:"にもかかわらず",reading:"にもかかわらず",pos:["連語"]},
"3685":{word:"もしくは",reading:"もしくは",pos:["接続詞"]},"3694":{word:"誤〜",reading:"ご",pos:["接頭語"]}
};
const UPDATES={
"3652":{"exampleTranslations[0]":"У цій крамниці багато товарів з оригінальним задумом, і вони популярні серед молоді."},
"3668":{"m":"復讐・報復すること。また、競技で一度敗れた相手と再び対戦して雪辱を果たすこと。俗に、失敗したことにもう一度挑むこと。","t":"помста, відплата; реванш; повторна спроба після невдачі; 〜する — помститися, взяти реванш","usage":"リベンジする／リベンジを果たす — помститися або взяти реванш; у спорті — реванш після поразки; розмовно — повторно спробувати те, що раніше не вдалося. Конкретне значення визначає контекст; слово не завжди означає особисту помсту."},
"3671":{"exampleTranslations[0]":"Наближався граничний строк подання заявки, тож відповідальний працівник поспішав із підготовкою.","exampleTranslations[1]":"З огляду на рентабельність, далі знижувати ціну вже неможливо."},
"3677":{"t":"недбалий, неакуратний; неорганізований","exampleTranslations[0]":"Люди, які недбало ставляться до часу, легко втрачають довіру ділових партнерів."},
"3679":{"exampleTranslations[0]":"За самовладного керівника компанії працівникам важко вільно висловлювати власну думку.","exampleTranslations[1]":"Компанія відійшла від одноосібного стилю керування засновника й запровадила колегіальне ухвалення рішень."},
"3681":{"usage":"その上 додає ще одну обставину до вже сказаного. Часто підсилює попередню оцінку, але саме по собі не обмежене лише позитивними чи лише негативними фактами. На початку речення або між частинами; не фізичне 上に «зверху» в цих прикладах."},
"3694":{"exampleTranslations[1]":"Після поширення хибного повідомлення газета наступного дня опублікувала статтю з виправленням."}
};
function extractConst(s,n){
 const marker="const "+n+" =",a=s.indexOf(marker);assert.ok(a>=0,"missing "+n);
 let i=a+marker.length;while(/\s/.test(s[i]))i++;
 const open=s[i],close=open==="["?"]":"}";let depth=0,q=false,esc=false;
 for(let j=i;j<s.length;j++){const c=s[j];if(q){if(esc)esc=false;else if(c==="\\")esc=true;else if(c==='"')q=false;continue;}if(c==='"'){q=true;continue;}if(c===open)depth++;else if(c===close){depth--;if(depth===0)return JSON.parse(s.slice(i,j+1));}}
 throw Error("unterminated "+n);
}
(async()=>{
 const bytes=fs.readFileSync(HTML),sha=crypto.createHash("sha256").update(bytes).digest("hex");
 assert.equal(sha,prep.candidate_sha256);assert.equal(bytes.length,prep.candidate_bytes);
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:412,height:900}}),errors=[];
  page.on("pageerror",e=>errors.push(String(e)));await page.goto(pathToFileURL(path.resolve(HTML)).href);
  const structural=await page.evaluate(()=>({vocab:DEFAULT_VOCAB.length,grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,pairs:VOCAB_AUDITED_PAIRS.length,uniqueIds:new Set(DEFAULT_VOCAB.map(x=>Number(x.id))).size,allIdsPresent:DEFAULT_VOCAB.every(x=>VOCAB_DETAILS_BY_ID[String(x.id)]&&VOCAB_POS_BY_ID[String(x.id)])}));
  assert.deepEqual(structural,{vocab:3914,grammar:130,pairs:859,uniqueIds:3914,allIdsPresent:true});
  const data=await page.evaluate(ids=>ids.map(id=>{const v=DEFAULT_VOCAB.find(x=>Number(x.id)===id),d=VOCAB_DETAILS_BY_ID[String(id)];return{id,word:d.w,reading:v.r,pos:VOCAB_POS_BY_ID[String(id)],short:v.s,meaning:d.m,gloss:d.t,usage:d.usage,examples:d.examples,translations:d.exampleTranslations};}),IDS);
  for(const c of data){const e=EXPECTED[String(c.id)];assert.equal(c.word,e.word);assert.equal(c.reading,e.reading);assert.deepEqual(c.pos,e.pos);if(e.short)assert.equal(c.short,e.short);assert.ok(c.usage&&c.usage.length>0);assert.equal(c.examples.length,2);assert.equal(c.translations.length,2);}
  const basePage=await browser.newPage();await basePage.goto(pathToFileURL(path.resolve(BASE)).href);
  const stable=async p=>p.evaluate(()=>({vocab:JSON.stringify(DEFAULT_VOCAB),pos:JSON.stringify(VOCAB_POS_BY_ID),grammar:JSON.stringify(GRAMMAR_DETAILS_BY_ID),pairs:JSON.stringify(VOCAB_AUDITED_PAIRS),meaning:JSON.stringify(REVIEWED_MEANING_QUIZZES),reading:JSON.stringify(REVIEWED_READING_OPTIONS),kana:JSON.stringify(VOCAB_KANA_EXAMPLE_TARGETS),targets:JSON.stringify(REVIEWED_EXAMPLE_TARGETS)}));
  assert.deepEqual(await stable(page),await stable(basePage));
  const baseDetails=await basePage.evaluate(()=>VOCAB_DETAILS_BY_ID),candidateDetails=await page.evaluate(()=>VOCAB_DETAILS_BY_ID);
  const expectedDetails=JSON.parse(JSON.stringify(baseDetails));
  for(const [id,fields] of Object.entries(UPDATES))for(const [field,value] of Object.entries(fields)){
   if(field.startsWith("exampleTranslations[")){const ix=Number(field.match(/\[(\d+)\]/)[1]);expectedDetails[id].exampleTranslations[ix]=value;}
   else expectedDetails[id][field]=value;
  }
  assert.deepEqual(candidateDetails,expectedDetails,"unexpected detail field changes");
  const pairData=await page.evaluate(()=>[807,808,809,816].map(i=>({index:i,...VOCAB_AUDITED_PAIRS[i]})));
  const pairKeys=[["3680","3685"],["3680","3684"],["3681","3683"],["3693","3694"]];
  pairData.forEach((p,i)=>{assert.equal(p.a,pairKeys[i][0]);assert.equal(p.b,pairKeys[i][1]);assert.ok(p.note);});
  const rendered=await page.evaluate(async ids=>{
   showView("cards");const out=[],norm=x=>String(x).replaceAll("\n"," ").replaceAll("\r"," ").replaceAll("\t"," ").split(" ").filter(Boolean).join(" ");
   for(const id of ids){await openCardDetail("v",id);await new Promise(r=>setTimeout(r,35));const body=document.getElementById("cardDetailBody"),txt=body?.innerText||"",d=VOCAB_DETAILS_BY_ID[String(id)];
    out.push({id,word:d.w,titleVisible:norm(txt).includes(norm(d.w)),definitionVisible:norm(txt).includes(norm(d.m)),usageVisible:norm(txt).includes("用法・接続"),examplesVisible:d.examples.every(x=>norm(txt).includes(norm(x))),translationsVisible:d.exampleTranslations.every(x=>norm(txt).includes(norm(x)))});
   }return out;
  },IDS);
  fs.writeFileSync(path.join(WORK,"rendered-debug.json"),JSON.stringify(rendered,null,2)+"\n");
  assert.ok(rendered.every(x=>x.titleVisible&&x.definitionVisible&&x.usageVisible&&x.examplesVisible&&x.translationsVisible));
  const responsive=[];for(const width of [360,412,1280]){await page.setViewportSize({width,height:900});const x=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth}));responsive.push({...x,overflow:x.scrollWidth>width||x.bodyWidth>width});}
  assert.ok(responsive.every(x=>!x.overflow));
  const storage=await page.evaluate(()=>{const key="choba_n1uk_storage_v1",old=localStorage.getItem(key),sentinel=JSON.stringify({meta:{sessionSize:10,streak:5,lastStudyDate:"2026-11-14"},vp:{"3652":{status:"S",timesShown:2}},gp:{"90":{status:"X"}}});localStorage.setItem(key,sentinel);const roundTrip=localStorage.getItem(key)===sentinel;if(old===null)localStorage.removeItem(key);else localStorage.setItem(key,old);return{roundTrip,restored:localStorage.getItem(key)===old};});
  assert.ok(storage.roundTrip&&storage.restored);assert.deepEqual(errors,[]);
  const result={pass:true,candidate_sha256:sha,candidate_bytes:bytes.length,counts:structural,reviewed_card_count:12,credited_count:8,blocked_count:4,pair_reviewed_count:4,pair_changed_count:0,responsive,storage,stablePoolsUnchanged:true,exactDetailChanges:true,pageErrors:errors};
  fs.writeFileSync(path.join(WORK,"browser-results.json"),JSON.stringify(result,null,2)+"\n");console.log(JSON.stringify(result,null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
