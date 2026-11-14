const fs=require("node:fs"),crypto=require("node:crypto"),assert=require("node:assert/strict"),path=require("node:path");
function extractConst(s,n){const m="const "+n+" =",a=s.indexOf(m);assert.ok(a>=0,"missing "+n);let i=a+m.length;while(/\s/.test(s[i]))i++;const o=s[i],c=o==="["?"]":"}";let d=0,q=false,e=false;for(let j=i;j<s.length;j++){const x=s[j];if(q){if(e)e=false;else if(x==="\\")e=true;else if(x==='"')q=false;}else if(x==='"')q=true;else if(x===o)d++;else if(x===c&&--d===0)return{start:i,end:j+1,value:JSON.parse(s.slice(i,j+1)),literal:s.slice(i,j+1)};}throw Error("unterminated "+n);}
function parseCSV(s){const rows=[];let row=[],f="",q=false;for(let i=0;i<s.length;i++){const c=s[i];if(q){if(c==='"'&&s[i+1]==='"'){f+='"';i++;}else if(c==='"')q=false;else f+=c;}else if(c==='"')q=true;else if(c===","){row.push(f);f="";}else if(c==="\n"){row.push(f);rows.push(row);row=[];f="";}else if(c!=="\r")f+=c;}if(f.length||row.length){row.push(f);rows.push(row);}return rows;}
const csvCell=v=>{const s=String(v??"");return /[",\r\n]/.test(s)?'"'+s.replace(/"/g,'""')+'"':s;};
const tsvCell=v=>String(v??"").replace(/\t/g," ").replace(/\r?\n/g," ");
const basePath="JLPT_N1_ukrainian_reading_v223.html",outPath="JLPT_N1_ukrainian_reading_v224.html",work="completion/v224-work",guard="d148859cf9760dd58b3478e5d7ac7ebaf38220f3";
const base=fs.readFileSync(basePath,"utf8"),baseSha=crypto.createHash("sha256").update(base).digest("hex");
assert.equal(baseSha,"36200574a5ff6e03386ff48b3f21d2686bd69fb335cec690db5930b37bd40955","v223 base changed");
const d=extractConst(base,"VOCAB_DETAILS_BY_ID"),v=extractConst(base,"DEFAULT_VOCAB").value,pos=extractConst(base,"VOCAB_POS_BY_ID").value,g=extractConst(base,"GRAMMAR_DETAILS_BY_ID").value,pairs=extractConst(base,"VOCAB_AUDITED_PAIRS").value,quizzes=extractConst(base,"REVIEWED_MEANING_QUIZZES").value,reading=extractConst(base,"REVIEWED_READING_OPTIONS").value,kana=extractConst(base,"VOCAB_KANA_EXAMPLE_TARGETS").value,targets=extractConst(base,"REVIEWED_EXAMPLE_TARGETS").value;
assert.equal(v.length,3914);assert.equal(Object.keys(d.value).length,3914);assert.equal(Object.keys(g).length,130);assert.equal(pairs.length,859);assert.equal(new Set(v.map(x=>Number(x.id))).size,3914);
const scope=[3522,3525,3532,3537,3548,3556,3561,3565,3568,3569,3580,3588],fixed=[3537],reviewed=[3522,3532,3548,3556,3568,3580,3588],blocked=[3525,3561,3565,3569],pairScope=[789,790],before=JSON.parse(JSON.stringify(d.value)),changes=[];
function set(id,field,oldV,newV){assert.equal(d.value[String(id)][field],oldV,"unexpected old value "+id+"."+field);d.value[String(id)][field]=newV;changes.push({id,field,oldValue:oldV,newValue:newV});}
set(3537,"t","таємний, секретний","таємниця; секрет; секретний, прихований");
assert.equal(changes.length,1);
const changed=Object.keys(d.value).filter(id=>JSON.stringify(d.value[id])!==JSON.stringify(before[id])).map(Number).sort((a,b)=>a-b);
assert.deepEqual(changed,fixed);
const expected={
3522:{word:"エントリー",reading:"えんとりー",pos:["名詞"]},
3525:{word:"オートマチック",reading:"おーとまちっく",pos:["名詞"]},
3532:{word:"キャッチ",reading:"きゃっち",pos:["名詞"]},
3537:{word:"シークレット",reading:"しーくれっと",pos:["名詞"],gloss:"таємниця; секрет; секретний, прихований"},
3548:{word:"クローズアップ",reading:"くろーずあっぷ",pos:["名詞"]},
3556:{word:"セレモニー",reading:"せれもにー",pos:["名詞"]},
3561:{word:"ジャンボ",reading:"じゃんぼ",pos:["名詞"]},
3565:{word:"タイムリー",reading:"たいむりー",pos:["名詞"]},
3568:{word:"ダメージ",reading:"だめーじ",pos:["名詞"]},
3569:{word:"コマーシャル",reading:"こまーしゃる",pos:["名詞"]},
3580:{word:"チャンピオン",reading:"ちゃんぴおん",pos:["名詞"]},
3588:{word:"ストック",reading:"すとっく",pos:["名詞"]}
};
for(const id of scope){const row=v.find(x=>Number(x.id)===id),z=d.value[String(id)],e=expected[id];assert.ok(row,"missing vocab row "+id);assert.equal(z.w,e.word);assert.equal(row.r,e.reading);assert.deepEqual(pos[String(id)],e.pos);assert.equal(z.examples.length,2);assert.equal(z.exampleTranslations.length,2);assert.ok(z.usage&&z.usage.length>0);if(e.gloss)assert.equal(z.t,e.gloss);assert.ok(!Object.hasOwn(quizzes,"v_"+id),"unexpected meaning quiz override "+id);assert.ok(!Object.hasOwn(reading,String(id)),"unexpected reading override "+id);}
for(const id of reviewed.concat(blocked))assert.equal(JSON.stringify(d.value[String(id)]),JSON.stringify(before[String(id)]),"unplanned content change "+id);
for(const id of [3522,3532,3548,3588])assert.equal(v.find(x=>Number(x.id)===id).s,"する","noun+する marker lost "+id);
let candidate=base.slice(0,d.start)+JSON.stringify(d.value)+base.slice(d.end);
const oldTitle="<title>JLPT N1 — ウクライナ語対応学習アプリ · v223</title>",newTitle="<title>JLPT N1 — ウクライナ語対応学習アプリ · v224</title>";
assert.equal(candidate.split(oldTitle).length,2,"version title mismatch");candidate=candidate.replace(oldTitle,newTitle);
let rollback=candidate.replace(newTitle,oldTitle),rd=extractConst(rollback,"VOCAB_DETAILS_BY_ID");rollback=rollback.slice(0,rd.start)+d.literal+rollback.slice(rd.end);assert.equal(rollback,base,"exact rollback failed");
for(const n of ["DEFAULT_VOCAB","VOCAB_POS_BY_ID","GRAMMAR_DETAILS_BY_ID","VOCAB_AUDITED_PAIRS","REVIEWED_MEANING_QUIZZES","REVIEWED_READING_OPTIONS","VOCAB_KANA_EXAMPLE_TARGETS","REVIEWED_EXAMPLE_TARGETS"])assert.deepEqual(extractConst(candidate,n).value,extractConst(base,n).value,n+" changed");
const rp="completion/review-register.csv",reg=parseCSV(fs.readFileSync(rp,"utf8"));assert.equal(reg.length,5848);
const h=reg[0],col=k=>h.indexOf(k),dec=new Map([...fixed.map(i=>[i,"fixed_rechecked"]),...reviewed.map(i=>[i,"reviewed"]),...blocked.map(i=>[i,"blocked"])]),seen=new Set();
for(const row of reg.slice(1)){if(row[col("kind")]==="vocab"&&dec.has(Number(row[col("key")]))){const id=Number(row[col("key")]);assert.equal(row[col("finalReview")],"pending","vocab row not pending "+id);assert.ok(!seen.has(id));seen.add(id);row[col("finalReview")]=dec.get(id);row[col("evidence")]="JLPT_N1_v224_audit.md; completion/v224-acceptance.tsv; completion/v224-c10-review.tsv; "+(blocked.includes(id)?"C11 POS-map/quiz-pool review required; not author-credited in v224":"author review only; no v153 pilot rows for IDs above 320");}}
assert.equal(seen.size,12);
const pairRows=[];
for(const i of pairScope){const p=pairs[i],key=i+":"+p.a+":"+p.b,row=reg.slice(1).find(r=>r[col("kind")]==="vocab_pair"&&r[col("key")]===key);assert.ok(row,"missing pair row "+key);assert.equal(row[col("finalReview")],"pending","pair row not pending "+key);row[col("finalReview")]="reviewed";row[col("evidence")]="completion/v224-pair-review.tsv#"+i+"; author review of exact pair and note; no text change; not independent";pairRows.push({index:i,key,pair:p});}
fs.writeFileSync(rp,reg.map(r=>r.map(csvCell).join(",")).join("\n")+"\n");
function counts(kind){const o={reviewed:0,fixed_rechecked:0,pending:0,blocked:0,total:0};for(const r of reg.slice(1)){if(kind&&r[col("kind")]!==kind)continue;if(Object.hasOwn(o,r[col("finalReview")]))o[r[col("finalReview")]]++;o.total++;}return o;}
const after={all:counts(null),vocabulary:counts("vocab"),vocab_pair:counts("vocab_pair")};
assert.deepEqual(after,{all:{reviewed:3986,fixed_rechecked:461,pending:1389,blocked:11,total:5847},vocabulary:{reviewed:3397,fixed_rechecked:459,pending:47,blocked:11,total:3914},vocab_pair:{reviewed:40,fixed_rechecked:1,pending:818,blocked:0,total:859}});
const bytes=Buffer.byteLength(candidate),sha=crypto.createHash("sha256").update(candidate).digest("hex"),blob=crypto.createHash("sha1").update(Buffer.from("blob "+bytes+"\0")).update(Buffer.from(candidate)).digest("hex");
const prep={pass:true,base_version:"v223",base_main_sha:guard,base_html_sha256:baseSha,candidate_version:"v224",candidate_sha256:sha,candidate_blob_sha:blob,candidate_bytes:bytes,vocabulary_records:3914,grammar_records:130,lexical_pairs:859,unique_vocabulary_ids:3914,review_scope:scope,fixed_rechecked_ids:fixed,reviewed_ids:reviewed,blocked_ids:blocked,updated_fields:1,changed_cards:changed,pair_reviewed_indices:pairScope,pair_changed_indices:[],pos_map_unchanged:true,reading_and_cloze_pools_unchanged:true,example_target_tables_unchanged:true,reviewed_meaning_quizzes_unchanged:true,japanese_examples_changed:[],author_credit_before:3848,author_credit_addition:8,author_credit_after:3856,pilot_covered_ids:[],pilot_missing_ids:scope,exact_rollback:true,register_after:after,author_review_only:true,independent_acceptance:"not performed",physical_device_acceptance:"not performed",provenance_legal_acceptance:"not performed",publication_guard:guard,publication_status:"pending",blocked_reason:"C11 POS-map and quiz-pool review required for IDs 3525, 3561, 3565, 3569"};
const registry={pass:true,register_rows:reg.length-1,after,scope_updated:scope,pair_scope_updated:pairScope,blocked_scope:blocked,duplicate_scope_keys:0,records_deleted:0,history_rewritten:false};
fs.mkdirSync(work,{recursive:true});fs.writeFileSync(outPath,candidate);fs.writeFileSync(path.join(work,"prepare-results.json"),JSON.stringify(prep,null,2)+"\n");fs.writeFileSync(path.join(work,"registry-results.json"),JSON.stringify(registry,null,2)+"\n");
fs.writeFileSync("completion/v224-field-changes.tsv",["id\tfield\told_value_json\tnew_value_json",...changes.map(x=>[x.id,x.field,JSON.stringify(x.oldValue),JSON.stringify(x.newValue)].map(tsvCell).join("\t"))].join("\n")+"\n");
const decisions=[
[3522,"エントリー","reviewed","—","Participation application/registration; the する marker and both examples are correct."],
[3525,"オートマチック","blocked","—","Dictionary usage includes 形動 forms (オートマチックな／に), while the app POS map has 名詞 only; C11 must assess quiz-pool impact."],
[3532,"キャッチ","reviewed","—","Noun+する; both catching information and catching a ball are natural."],
[3537,"シークレット","fixed_rechecked","t","The Japanese definition is nominal (秘密); the Ukrainian gloss now includes the noun sense as well as attributive 'secret'."],
[3548,"クローズアップ","reviewed","—","Noun+する; both close-up and highlighting a topic are represented naturally."],
[3556,"セレモニー","reviewed","—","儀式／式典; examples and Ukrainian translations are accurate."],
[3561,"ジャンボ","blocked","—","The card's own usage note has ジャンボなN, but POS map has 名詞 only; conservative C11 review required."],
[3565,"タイムリー","blocked","—","Kotobank gives 形動 for well-timed and 名詞 for a baseball hit; app POS map has 名詞 only; C11 required."],
[3568,"ダメージ","reviewed","—","Noun meaning harm/loss; brand and crop examples are accurate."],
[3569,"コマーシャル","blocked","—","Dictionary lists noun and 形動 usage, while app POS map has 名詞 only; C11 required."],
[3580,"チャンピオン","reviewed","—","Winner/titleholder; examples about defending and losing a title are accurate."],
[3588,"ストック","reviewed","—","Noun+する; stored supplies and warehouse stock are represented accurately."]
];
fs.writeFileSync("completion/v224-c10-review.tsv",["id\theadword\tdecision\tchanged_fields\treason",...decisions.map(r=>r.map(tsvCell).join("\t"))].join("\n")+"\n");
const acceptance=[
...fixed.map(i=>["vocab",String(i),"fixed_rechecked","changed",d.value[String(i)].w]),
...reviewed.map(i=>["vocab",String(i),"reviewed","unchanged",d.value[String(i)].w]),
...blocked.map(i=>["vocab",String(i),"blocked","held_for_C11",d.value[String(i)].w]),
...pairRows.map(x=>["vocab_pair",String(x.index),"reviewed","unchanged",x.pair.a+"/"+x.pair.b])
];
fs.writeFileSync("completion/v224-acceptance.tsv",["kind\tkey\tdecision\tchange\tnote",...acceptance.map(r=>r.map(tsvCell).join("\t"))].join("\n")+"\n");
fs.writeFileSync("completion/v224-pair-review.tsv",["index\tkey\tdecision\tchange\tnote",...pairRows.map(x=>[x.index,x.key,"reviewed","unchanged",x.pair.note].map(tsvCell).join("\t"))].join("\n")+"\n");
const audit=[
"# JLPT N1 v224 — C10 авторський аудит",
"",
"База: повний v223 у main, SHA-256 "+baseSha+".",
"Кандидат: повний автономний HTML v224.",
"HTML bytes: "+bytes+".",
"SHA-256: "+sha+".",
"Git blob: "+blob+".",
"",
"TECHNICAL_STATUS_PENDING",
"",
"## Авторський обсяг",
"Перевірено 12 pending-карток: "+scope.join(", ")+".",
"- 1 fixed_rechecked: 3537.",
"- 7 reviewed без змін: "+reviewed.join(", ")+".",
"- 4 blocked до C11: "+blocked.join(", ")+".",
"- Одна точна зміна у картці 3537: український gloss тепер передає іменникове значення «таємниця/секрет» поряд із прикметниковим уживанням.",
"- Дві лексичні пари reviewed без зміни тексту: індекси 789 і 790.",
"- Пілот v153 охоплює ID121–320; для цих 12 ID рядків пілота немає. Переглянуто безпосередньо за v223.",
"- POS-map, grammar data, pair notes, quiz payloads, reading/cloze pools і target tables не змінювалися.",
"- Noun+する для エントリー, キャッチ, クローズアップ, ストック збережено як 名詞 із вихідним marker する.",
"",
"## C11 blockers",
"- 3525 オートマチック: у словнику є 形動 уживання オートマチックな／に; POS-map містить лише 名詞.",
"- 3561 ジャンボ: власна usage-нотатка містить ジャンボなN; POS-map містить лише 名詞. Залишено blocked консервативно до словникової/POS-звірки.",
"- 3565 タイムリー: словник класифікує загальне значення як 形動, а бейсбольне як 名詞; POS-map містить лише 名詞.",
"- 3569 コマーシャル: словник засвідчує і 名詞, і 形動 уживання; POS-map містить лише 名詞.",
"- Жоден POS-map чи quiz pool не змінювався без окремого C11 аналізу.",
"",
"## Реєстр",
"Після v224: словник — 3397 reviewed /459 fixed_rechecked /47 pending /11 blocked; лексичні пари — 40 reviewed /1 fixed_rechecked /818 pending. Увесь реєстр — 3986 reviewed /461 fixed_rechecked /1389 pending /11 blocked із 5847. Авторський credit — 3856/3914; це не загальна готовність 1.0.",
"",
"## Межі",
"Це авторський мовний перегляд і технічний пакет, не незалежне лінгвістичне приймання. Незалежне лінгвістичне, фізичне Android/Windows та правове/походження приймання залишаються відкритими."
].join("\n");
fs.writeFileSync("JLPT_N1_v224_audit.md",audit+"\n");
const cp={version:"v224",base_version:"v223",base_main_sha:guard,base_html_sha256:baseSha,base_html_blob:"2ca9191848ecd598aaede1693f8fbf35c772f7ae",base_html_bytes:6952219,branch:"work/v224-c10-next-pending",scope_ids:scope,scope_status:"pending in main after v223; selected after older follow-ups",fixed_rechecked_ids:fixed,reviewed_ids:reviewed,blocked_ids:blocked,field_updates:changes.map(x=>({id:x.id,field:x.field})),pair_reviewed:pairScope,pilot_covered_ids:[],pilot_missing_ids:scope,author_credit_before:3848,author_credit_after:3856,author_review:"completed; 8 cards credited, 4 blocked for C11 POS/quiz analysis",technical_verification:"pending",independent_acceptance:"not performed",physical_device_acceptance:"not performed",provenance_legal_acceptance:"not performed",main_guard:guard,publication_policy:"publish only exact verified artifacts; never merge work branch",status:"candidate and registry prepared; syntax and Chromium verification pending",candidate_sha256:sha,candidate_blob_sha:blob,candidate_bytes:bytes,pair_changed:[],exact_rollback:true,publication_status:"pending",chromium_verification:"pending",workflow_run_id:null};
fs.writeFileSync(path.join(work,"checkpoint.json"),JSON.stringify(cp,null,2)+"\n");
console.log(JSON.stringify({pass:true,candidate_sha256:sha,candidate_blob_sha:blob,candidate_bytes:bytes,changed_cards:changed,field_updates:changes.length,registry_after:after},null,2));
