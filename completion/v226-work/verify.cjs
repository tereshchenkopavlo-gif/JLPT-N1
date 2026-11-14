const fs=require("node:fs"),crypto=require("node:crypto"),assert=require("node:assert/strict"),path=require("node:path");
function extractConst(s,n){
  const marker="const "+n+" =",a=s.indexOf(marker);assert.ok(a>=0,"missing "+n);
  let i=a+marker.length;while(/\s/.test(s[i]))i++;
  const open=s[i],close=open==="["?"]":"}";let depth=0,q=false,esc=false;
  for(let j=i;j<s.length;j++){const c=s[j];
    if(q){if(esc)esc=false;else if(c==="\\")esc=true;else if(c==='"')q=false;continue;}
    if(c==='"'){q=true;continue;}
    if(c===open)depth++;
    else if(c===close){depth--;if(depth===0){const literal=s.slice(i,j+1);return{start:i,end:j+1,literal,value:JSON.parse(literal)};}}
  }
  throw Error("unterminated "+n);
}
function parseCSV(s){
  const rows=[];let row=[],f="",q=false;
  for(let i=0;i<s.length;i++){const c=s[i];
    if(q){if(c==='"'&&s[i+1]==='"'){f+='"';i++;}else if(c==='"')q=false;else f+=c;}
    else if(c==='"')q=true;
    else if(c===","){row.push(f);f="";}
    else if(c==="\n"){row.push(f);rows.push(row);row=[];f="";}
    else if(c!=="\r")f+=c;
  }
  if(f.length||row.length){row.push(f);rows.push(row);}return rows;
}
const csvCell=v=>{const s=String(v??"");return /[",\r\n]/.test(s)?'"'+s.replace(/"/g,'""')+'"':s;};
const tsvCell=v=>String(v??"").replace(/\t/g," ").replace(/\r?\n/g," ");
const BASE="JLPT_N1_ukrainian_reading_v225.html",OUT="JLPT_N1_ukrainian_reading_v226.html",WORK="completion/v226-work";
const GUARD="f7af2deca13bafdd9045c9b058a77813f925edaf";
const base=fs.readFileSync(BASE,"utf8");
const baseSha=crypto.createHash("sha256").update(base).digest("hex");
assert.equal(baseSha,"53f733699fc4cf6e487c739fdd96e007e9cc27822fbeebc871da4498007d19b4","v225 base changed");
const dEntry=extractConst(base,"VOCAB_DETAILS_BY_ID"),original=JSON.parse(JSON.stringify(dEntry.value)),d=JSON.parse(JSON.stringify(dEntry.value));
const scope=[3652,3654,3657,3668,3671,3677,3679,3680,3681,3682,3685,3694];
const fixed=[3668,3671,3681,3694],reviewed=[3657,3680,3682,3685],blocked=[3652,3654,3677,3679],pairScope=[807,808,809,816];
const fieldChanges=[];
function set(id,field,value){
  const key=String(id),old=d[key][field];
  assert.notDeepEqual(old,value,"no-op field update "+id+"."+field);
  d[key][field]=value;fieldChanges.push({id,word:d[key].w,field,old,new:value});
}
function setArray(id,field,index,value){
  const key=String(id),old=d[key][field][index];
  assert.notEqual(old,value,"no-op array update "+id+"."+field+"["+index+"]");
  d[key][field][index]=value;fieldChanges.push({id,word:d[key].w,field:field+"["+index+"]",old,new:value});
}
setArray(3652,"exampleTranslations",0,"У цій крамниці багато товарів з оригінальним задумом, і вони популярні серед молоді.");
set(3668,"m","復讐・報復すること。また、競技で一度敗れた相手と再び対戦して雪辱を果たすこと。俗に、失敗したことにもう一度挑むこと。");
set(3668,"t","помста, відплата; реванш; повторна спроба після невдачі; 〜する — помститися, взяти реванш");
set(3668,"usage","リベンジする／リベンジを果たす — помститися або взяти реванш; у спорті — реванш після поразки; розмовно — повторно спробувати те, що раніше не вдалося. Конкретне значення визначає контекст; слово не завжди означає особисту помсту.");
setArray(3671,"exampleTranslations",0,"Наближався граничний строк подання заявки, тож відповідальний працівник поспішав із підготовкою.");
setArray(3671,"exampleTranslations",1,"З огляду на рентабельність, далі знижувати ціну вже неможливо.");
set(3677,"t","недбалий, неакуратний; неорганізований");
setArray(3677,"exampleTranslations",0,"Люди, які недбало ставляться до часу, легко втрачають довіру ділових партнерів.");
setArray(3679,"exampleTranslations",0,"За самовладного керівника компанії працівникам важко вільно висловлювати власну думку.");
setArray(3679,"exampleTranslations",1,"Компанія відійшла від одноосібного стилю керування засновника й запровадила колегіальне ухвалення рішень.");
set(3681,"usage","その上 додає ще одну обставину до вже сказаного. Часто підсилює попередню оцінку, але саме по собі не обмежене лише позитивними чи лише негативними фактами. На початку речення або між частинами; не фізичне 上に «зверху» в цих прикладах.");
setArray(3694,"exampleTranslations",1,"Після поширення хибного повідомлення газета наступного дня опублікувала статтю з виправленням.");
const oldTitle="<title>JLPT N1 — ウクライナ語対応学習アプリ · v225</title>",newTitle="<title>JLPT N1 — ウクライナ語対応学習アプリ · v226</title>";
assert.equal(base.split(oldTitle).length,2,"version title mismatch");
let candidate=base.replace(oldTitle,newTitle);
const dCandidate=extractConst(candidate,"VOCAB_DETAILS_BY_ID"),newLiteral=JSON.stringify(d);
candidate=candidate.slice(0,dCandidate.start)+newLiteral+candidate.slice(dCandidate.end);
const dAfter=extractConst(candidate,"VOCAB_DETAILS_BY_ID");
let rollback=candidate.slice(0,dAfter.start)+dEntry.literal+candidate.slice(dAfter.end);
rollback=rollback.replace(newTitle,oldTitle);
assert.equal(rollback,base,"exact rollback failed");
for(const n of ["DEFAULT_VOCAB","VOCAB_POS_BY_ID","GRAMMAR_DETAILS_BY_ID","VOCAB_AUDITED_PAIRS","REVIEWED_MEANING_QUIZZES","REVIEWED_READING_OPTIONS","VOCAB_KANA_EXAMPLE_TARGETS","REVIEWED_EXAMPLE_TARGETS"])
  assert.deepEqual(extractConst(candidate,n).value,extractConst(base,n).value,n+" changed");
const v=extractConst(candidate,"DEFAULT_VOCAB").value,pos=extractConst(candidate,"VOCAB_POS_BY_ID").value;
const grammar=extractConst(candidate,"GRAMMAR_DETAILS_BY_ID").value,pairs=extractConst(candidate,"VOCAB_AUDITED_PAIRS").value;
assert.equal(v.length,3914);assert.equal(Object.keys(d).length,3914);assert.equal(Object.keys(grammar).length,130);assert.equal(pairs.length,859);
assert.equal(new Set(v.map(x=>Number(x.id))).size,3914);
const expected={
3652:{word:"ユニーク",reading:"ゆにーく",pos:["名詞"]},
3654:{word:"ブロック",reading:"ぶろっく",pos:["名詞"]},
3657:{word:"プロフィール",reading:"ぷろふぃーる",pos:["名詞"]},
3668:{word:"リベンジ",reading:"りべんじ",pos:["名詞"],s:"する"},
3671:{word:"リミット",reading:"りみっと",pos:["名詞"]},
3677:{word:"ルーズ",reading:"るーず",pos:["名詞"]},
3679:{word:"ワンマン",reading:"わんまん",pos:["名詞"]},
3680:{word:"あるいは",reading:"あるいは",pos:["副詞","接続詞"]},
3681:{word:"その上",reading:"そのうえ",pos:["接続詞"]},
3682:{word:"にもかかわらず",reading:"にもかかわらず",pos:["連語"]},
3685:{word:"もしくは",reading:"もしくは",pos:["接続詞"]},
3694:{word:"誤〜",reading:"ご",pos:["接頭語"]}
};
for(const id of scope){
  const row=v.find(x=>Number(x.id)===id),z=d[String(id)],e=expected[id];
  assert.ok(row,"missing vocab row "+id);assert.equal(z.w,e.word);assert.equal(row.r,e.reading);assert.deepEqual(pos[String(id)],e.pos);
  assert.equal(z.examples.length,2);assert.equal(z.exampleTranslations.length,2);assert.ok(z.usage&&z.usage.length>0);
  if(e.s)assert.equal(row.s,e.s,"noun+する marker changed for "+id);
}
assert.ok(v.find(x=>Number(x.id)===3654).s!=="する","C11 blocker 3654 unexpectedly resolved");
assert.ok(!pos["3652"].includes("ナ形")&&!pos["3677"].includes("ナ形")&&!pos["3679"].includes("ナ形"),"C11 blockers unexpectedly resolved");
const registerPath="completion/review-register.csv",reg=parseCSV(fs.readFileSync(registerPath,"utf8"));
assert.equal(reg.length,5848,"register row count changed");
const header=reg[0],col=k=>header.indexOf(k),dec=new Map([...fixed.map(i=>[i,"fixed_rechecked"]),...reviewed.map(i=>[i,"reviewed"]),...blocked.map(i=>[i,"blocked"])]),seen=new Set();
for(const row of reg.slice(1)){
  if(row[col("kind")]==="vocab"&&dec.has(Number(row[col("key")]))){
    const id=Number(row[col("key")]);assert.equal(row[col("finalReview")],"pending","vocab row not pending "+id);assert.ok(!seen.has(id));seen.add(id);
    row[col("finalReview")]=dec.get(id);
    row[col("evidence")]="JLPT_N1_v226_audit.md; completion/v226-acceptance.tsv; completion/v226-c10-review.tsv; "+(blocked.includes(id)?"C11 POS/形動/する-marker review required; no author credit":"author review of exact v225 fields; v153 pilot does not cover IDs above 320");
  }
}
assert.equal(seen.size,12);
const pairRows=[];
for(const i of pairScope){
  const p=pairs[i],key=i+":"+p.a+":"+p.b;
  const row=reg.slice(1).find(r=>r[col("kind")]==="vocab_pair"&&r[col("key")]===key);
  assert.ok(row,"missing pair row "+key);assert.equal(row[col("finalReview")],"pending","pair row not pending "+key);
  row[col("finalReview")]="reviewed";row[col("evidence")]="completion/v226-pair-review.tsv#"+i+"; exact pair and note reviewed; no text change; author review only";
  pairRows.push({index:i,key,pair:p});
}
fs.writeFileSync(registerPath,reg.map(r=>r.map(csvCell).join(",")).join("\n")+"\n");
function counts(kind){
  const o={reviewed:0,fixed_rechecked:0,pending:0,blocked:0,total:0};
  for(const r of reg.slice(1)){if(kind&&r[col("kind")]!==kind)continue;if(Object.hasOwn(o,r[col("finalReview")]))o[r[col("finalReview")]]++;o.total++;}
  return o;
}
const after={all:counts(null),vocabulary:counts("vocab"),vocab_pair:counts("vocab_pair")};
assert.deepEqual(after,{
  all:{reviewed:4007,fixed_rechecked:465,pending:1357,blocked:18,total:5847},
  vocabulary:{reviewed:3410,fixed_rechecked:463,pending:23,blocked:18,total:3914},
  vocab_pair:{reviewed:46,fixed_rechecked:1,pending:812,blocked:0,total:859}
});
const bytes=Buffer.byteLength(candidate),sha=crypto.createHash("sha256").update(candidate).digest("hex");
const blob=crypto.createHash("sha1").update(Buffer.from("blob "+bytes+"\0")).update(Buffer.from(candidate)).digest("hex");
const fieldRows=fieldChanges.map(x=>[x.id,x.word,x.field,JSON.stringify(x.old),JSON.stringify(x.new)]);
const decisions=[
[3652,"ユニーク","blocked","exampleTranslations[0]","Translation refined; card remains blocked because な-adjective use is absent from POS-map."],
[3654,"ブロック","blocked","—","Dictionary marks 名詞(スル), and the card itself uses ブロックして; DEFAULT_VOCAB has no する marker. C11 required."],
[3657,"プロフィール","reviewed","—","Definition, profile/biographical senses, examples and translations are accurate."],
[3668,"リベンジ","fixed_rechecked","m;t;usage","Added dictionary-supported revenge/retaliation sense alongside sports rematch and colloquial retry."],
[3671,"リミット","fixed_rechecked","exampleTranslations[0..1]","Corrected the deadline collocation and made the profitability-limit translation natural."],
[3677,"ルーズ","blocked","t;exampleTranslations[0]","Gloss and translation refined; remains blocked because Kotobank classifies it as 形動 while POS-map has 名詞 only."],
[3679,"ワンマン","blocked","exampleTranslations[0..1]","Corrected 社長 as company head and clarified the founder's management style; remains blocked because the dictionary gives 名詞(形動) while POS-map has 名詞 only."],
[3680,"あるいは","reviewed","—","Conjunction and adverbial possibility uses are both represented; POS-map includes 副詞 and 接続詞."],
[3681,"その上","fixed_rechecked","usage","Removed an overly restrictive claim that additions must have the same evaluative direction."],
[3682,"にもかかわらず","reviewed","—","Concessive meaning, examples and documented attachment are consistent."],
[3685,"もしくは","reviewed","—","Formal alternative use and documentary register are represented accurately."],
[3694,"誤〜","fixed_rechecked","exampleTranslations[1]","訂正記事 means a correction article; replaced the misleading 'спростування' with 'стаття з виправленням'."]];
const acceptance=[
...fixed.map(i=>["vocab",String(i),"fixed_rechecked","updated",d[String(i)].w]),
...reviewed.map(i=>["vocab",String(i),"reviewed","unchanged",d[String(i)].w]),
...blocked.map(i=>["vocab",String(i),"blocked","held_for_C11",d[String(i)].w]),
...pairRows.map(x=>["vocab_pair",String(x.index),"reviewed","unchanged",x.pair.a+"/"+x.pair.b])
];
fs.mkdirSync(WORK,{recursive:true});fs.writeFileSync(OUT,candidate);
fs.writeFileSync(path.join(WORK,"prepare-results.json"),JSON.stringify({
 pass:true,base_version:"v225",base_main_sha:GUARD,base_html_sha256:baseSha,candidate_version:"v226",
 candidate_sha256:sha,candidate_blob_sha:blob,candidate_bytes:bytes,vocabulary_records:3914,grammar_records:130,lexical_pairs:859,unique_vocabulary_ids:3914,
 review_scope:scope,fixed_rechecked_ids:fixed,reviewed_ids:reviewed,blocked_ids:blocked,updated_fields:fieldChanges.length,
 changed_cards:[...new Set(fieldChanges.map(x=>x.id))],pair_reviewed_indices:pairScope,pair_changed_indices:[],
 pos_map_unchanged:true,reading_and_cloze_pools_unchanged:true,example_target_tables_unchanged:true,reviewed_meaning_quizzes_unchanged:true,japanese_examples_changed:[],
 author_credit_before:3865,author_credit_addition:8,author_credit_after:3873,pilot_covered_ids:[],pilot_missing_ids:scope,exact_rollback:true,register_after:after,
 author_review_only:true,independent_acceptance:"not performed",physical_device_acceptance:"not performed",provenance_legal_acceptance:"not performed",publication_guard:GUARD,publication_status:"pending"
},null,2)+"\n");
fs.writeFileSync(path.join(WORK,"registry-results.json"),JSON.stringify({pass:true,register_rows:reg.length-1,after,scope_updated:scope,pair_scope_updated:pairScope,blocked_scope:blocked,duplicate_scope_keys:0,records_deleted:0,history_rewritten:false},null,2)+"\n");
fs.writeFileSync("completion/v226-field-changes.tsv",["id\theadword\tfield\told_value_json\tnew_value_json",...fieldRows.map(r=>r.map(tsvCell).join("\t"))].join("\n")+"\n");
fs.writeFileSync("completion/v226-c10-review.tsv",["id\theadword\tdecision\tchanged_fields\treason",...decisions.map(r=>r.map(tsvCell).join("\t"))].join("\n")+"\n");
fs.writeFileSync("completion/v226-acceptance.tsv",["kind\tkey\tdecision\tchange\tnote",...acceptance.map(r=>r.map(tsvCell).join("\t"))].join("\n")+"\n");
fs.writeFileSync("completion/v226-pair-review.tsv",["index\tkey\tdecision\tchange\tnote",...pairRows.map(x=>[x.index,x.key,"reviewed","unchanged",x.pair.note].map(tsvCell).join("\t"))].join("\n")+"\n");
const checkpoint={
 version:"v226",base_version:"v225",base_main_sha:GUARD,base_html_sha256:baseSha,branch:"work/v226-c10-next-pending",
 scope_ids:scope,scope_status:"pending in main after v225; selected from current completion register",
 fixed_rechecked_ids:fixed,reviewed_ids:reviewed,blocked_ids:blocked,field_updates:fieldChanges.length,pair_reviewed:pairScope,pair_changed:[],
 pilot_covered_ids:[],pilot_missing_ids:scope,author_credit_before:3865,author_credit_after:3873,
 author_review:"completed; 8 cards credited, 4 blocked for C11 POS/形動/する-marker analysis",
 technical_verification:"pending",independent_acceptance:"not performed",physical_device_acceptance:"not performed",provenance_legal_acceptance:"not performed",
 main_guard:GUARD,publication_policy:"publish only exact verified artifacts; never merge work branch",status:"candidate and registry prepared; awaiting syntax and Chromium verification",
 candidate_sha256:sha,candidate_blob_sha:blob,candidate_bytes:bytes,exact_rollback:true,publication_status:"pending",chromium_verification:"pending",workflow_run_id:null
};
fs.writeFileSync(path.join(WORK,"checkpoint.json"),JSON.stringify(checkpoint,null,2)+"\n");
console.log(JSON.stringify({pass:true,sha,blob,bytes,fieldUpdates:fieldChanges.length,after},null,2));
