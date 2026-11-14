const fs=require("node:fs"),crypto=require("node:crypto"),assert=require("node:assert/strict"),path=require("node:path");
function extractConst(s,n){const m="const "+n+" =",a=s.indexOf(m);assert.ok(a>=0,"missing "+n);let i=a+m.length;while(/\s/.test(s[i]))i++;const o=s[i],c=o==="["?"]":"}";let d=0,q=false,e=false;for(let j=i;j<s.length;j++){const x=s[j];if(q){if(e)e=false;else if(x==="\\")e=true;else if(x==='"')q=false;}else if(x==='"')q=true;else if(x===o)d++;else if(x===c&&--d===0)return{start:i,end:j+1,value:JSON.parse(s.slice(i,j+1)),literal:s.slice(i,j+1)};}throw Error("unterminated "+n);}
function parseCSV(s){const rows=[];let row=[],f="",q=false;for(let i=0;i<s.length;i++){const c=s[i];if(q){if(c==='"'&&s[i+1]==='"'){f+='"';i++;}else if(c==='"')q=false;else f+=c;}else if(c==='"')q=true;else if(c===","){row.push(f);f="";}else if(c==="\n"){row.push(f);rows.push(row);row=[];f="";}else if(c!=="\r")f+=c;}if(f.length||row.length){row.push(f);rows.push(row);}return rows;}
const csvCell=v=>{const s=String(v??"");return /[",\r\n]/.test(s)?'"'+s.replace(/"/g,'""')+'"':s;};
const tsvCell=v=>String(v??"").replace(/\t/g," ").replace(/\r?\n/g," ");
const basePath="JLPT_N1_ukrainian_reading_v224.html",outPath="JLPT_N1_ukrainian_reading_v225.html",work="completion/v225-work",guard="fc471671622b10aac6053a5bd74903bdc34b9eef";
const base=fs.readFileSync(basePath,"utf8"),baseSha=crypto.createHash("sha256").update(base).digest("hex");
assert.equal(baseSha,"19a9d8ca2e9f52a33c977674eb199ae7a132024adedd741681a4193f51a30cf6","v224 base changed");
const d=extractConst(base,"VOCAB_DETAILS_BY_ID"),v=extractConst(base,"DEFAULT_VOCAB").value,pos=extractConst(base,"VOCAB_POS_BY_ID").value,g=extractConst(base,"GRAMMAR_DETAILS_BY_ID").value,pairs=extractConst(base,"VOCAB_AUDITED_PAIRS").value,quizzes=extractConst(base,"REVIEWED_MEANING_QUIZZES").value,reading=extractConst(base,"REVIEWED_READING_OPTIONS").value,kana=extractConst(base,"VOCAB_KANA_EXAMPLE_TARGETS").value,targets=extractConst(base,"REVIEWED_EXAMPLE_TARGETS").value;
assert.equal(v.length,3914);assert.equal(Object.keys(d.value).length,3914);assert.equal(Object.keys(g).length,130);assert.equal(pairs.length,859);assert.equal(new Set(v.map(x=>Number(x.id))).size,3914);
const scope=[3589,3594,3599,3601,3607,3614,3635,3636,3637,3642,3644,3646],fixed=[],reviewed=[3589,3599,3601,3607,3614,3635,3637,3642,3644],blocked=[3594,3636,3646],pairScope=[791,792];
const expected={
3589:{word:"データベース",reading:"でーたべーす",pos:["名詞"]},
3594:{word:"ストレート",reading:"すとれーと",pos:["名詞"],usage:"ストレートな"},
3599:{word:"デビュー",reading:"でびゅー",pos:["名詞"]},
3601:{word:"ペア",reading:"ぺあ",pos:["名詞"]},
3607:{word:"ボイコット",reading:"ぼいこっと",pos:["名詞"]},
3614:{word:"トリック",reading:"とりっく",pos:["名詞"]},
3635:{word:"ノルマ",reading:"のるま",pos:["名詞"]},
3636:{word:"プライベート",reading:"ぷらいべーと",pos:["名詞"],usage:"プライベートな"},
3637:{word:"ムード",reading:"むーど",pos:["名詞"]},
3642:{word:"ブランク",reading:"ぶらんく",pos:["名詞"]},
3644:{word:"ハーモニー",reading:"はーもにー",pos:["名詞"]},
3646:{word:"モダン",reading:"もだん",pos:["名詞"],usage:"モダンな"}
};
for(const id of scope){const row=v.find(x=>Number(x.id)===id),z=d.value[String(id)],e=expected[id];assert.ok(row,"missing vocab row "+id);assert.equal(z.w,e.word);assert.equal(row.r,e.reading);assert.deepEqual(pos[String(id)],e.pos);assert.equal(z.examples.length,2);assert.equal(z.exampleTranslations.length,2);assert.ok(z.usage&&z.usage.length>0);if(e.usage)assert.ok(z.usage.includes(e.usage),"missing adjectival usage marker "+id);assert.ok(!Object.hasOwn(quizzes,"v_"+id),"unexpected meaning quiz override "+id);assert.ok(!Object.hasOwn(reading,String(id)),"unexpected reading override "+id);}
for(const id of [3599,3607])assert.equal(v.find(x=>Number(x.id)===id).s,"する","noun+する marker lost "+id);
const oldTitle="<title>JLPT N1 — ウクライナ語対応学習アプリ · v224</title>",newTitle="<title>JLPT N1 — ウクライナ語対応学習アプリ · v225</title>";
assert.equal(base.split(oldTitle).length,2,"version title mismatch");
const candidate=base.replace(oldTitle,newTitle);
assert.equal(candidate.replace(newTitle,oldTitle),base,"exact rollback failed");
for(const n of ["DEFAULT_VOCAB","VOCAB_DETAILS_BY_ID","VOCAB_POS_BY_ID","GRAMMAR_DETAILS_BY_ID","VOCAB_AUDITED_PAIRS","REVIEWED_MEANING_QUIZZES","REVIEWED_READING_OPTIONS","VOCAB_KANA_EXAMPLE_TARGETS","REVIEWED_EXAMPLE_TARGETS"])assert.deepEqual(extractConst(candidate,n).value,extractConst(base,n).value,n+" changed");
const rp="completion/review-register.csv",reg=parseCSV(fs.readFileSync(rp,"utf8"));assert.equal(reg.length,5848);
const h=reg[0],col=k=>h.indexOf(k),dec=new Map([...fixed.map(i=>[i,"fixed_rechecked"]),...reviewed.map(i=>[i,"reviewed"]),...blocked.map(i=>[i,"blocked"])]),seen=new Set();
for(const row of reg.slice(1)){if(row[col("kind")]==="vocab"&&dec.has(Number(row[col("key")]))){const id=Number(row[col("key")]);assert.equal(row[col("finalReview")],"pending","vocab row not pending "+id);assert.ok(!seen.has(id));seen.add(id);row[col("finalReview")]=dec.get(id);row[col("evidence")]="JLPT_N1_v225_audit.md; completion/v225-acceptance.tsv; completion/v225-c10-review.tsv; "+(blocked.includes(id)?"C11 POS-map/quiz-pool review required; not author-credited in v225":"author review only; no v153 pilot rows for IDs above 320");}}
assert.equal(seen.size,12);
const pairRows=[];
for(const i of pairScope){const p=pairs[i],key=i+":"+p.a+":"+p.b,row=reg.slice(1).find(r=>r[col("kind")]==="vocab_pair"&&r[col("key")]===key);assert.ok(row,"missing pair row "+key);assert.equal(row[col("finalReview")],"pending","pair row not pending "+key);row[col("finalReview")]="reviewed";row[col("evidence")]="completion/v225-pair-review.tsv#"+i+"; author review of exact pair and note; no text change; not independent";pairRows.push({index:i,key,pair:p});}
fs.writeFileSync(rp,reg.map(r=>r.map(csvCell).join(",")).join("\n")+"\n");
function counts(kind){const o={reviewed:0,fixed_rechecked:0,pending:0,blocked:0,total:0};for(const r of reg.slice(1)){if(kind&&r[col("kind")]!==kind)continue;if(Object.hasOwn(o,r[col("finalReview")]))o[r[col("finalReview")]]++;o.total++;}return o;}
const after={all:counts(null),vocabulary:counts("vocab"),vocab_pair:counts("vocab_pair")};
assert.deepEqual(after,{all:{reviewed:3999,fixed_rechecked:461,pending:1373,blocked:14,total:5847},vocabulary:{reviewed:3406,fixed_rechecked:459,pending:35,blocked:14,total:3914},vocab_pair:{reviewed:42,fixed_rechecked:1,pending:816,blocked:0,total:859}});
const bytes=Buffer.byteLength(candidate),sha=crypto.createHash("sha256").update(candidate).digest("hex"),blob=crypto.createHash("sha1").update(Buffer.from("blob "+bytes+"\0")).update(Buffer.from(candidate)).digest("hex");
const prep={pass:true,base_version:"v224",base_main_sha:guard,base_html_sha256:baseSha,candidate_version:"v225",candidate_sha256:sha,candidate_blob_sha:blob,candidate_bytes:bytes,vocabulary_records:3914,grammar_records:130,lexical_pairs:859,unique_vocabulary_ids:3914,review_scope:scope,fixed_rechecked_ids:fixed,reviewed_ids:reviewed,blocked_ids:blocked,updated_fields:0,changed_cards:[],pair_reviewed_indices:pairScope,pair_changed_indices:[],pos_map_unchanged:true,reading_and_cloze_pools_unchanged:true,example_target_tables_unchanged:true,reviewed_meaning_quizzes_unchanged:true,japanese_examples_changed:[],author_credit_before:3856,author_credit_addition:9,author_credit_after:3865,pilot_covered_ids:[],pilot_missing_ids:scope,exact_rollback:true,register_after:after,author_review_only:true,independent_acceptance:"not performed",physical_device_acceptance:"not performed",provenance_legal_acceptance:"not performed",publication_guard:guard,publication_status:"pending",blocked_reason:"C11 POS-map and quiz-pool review required for IDs 3594, 3636, 3646"};
const registry={pass:true,register_rows:reg.length-1,after,scope_updated:scope,pair_scope_updated:pairScope,blocked_scope:blocked,duplicate_scope_keys:0,records_deleted:0,history_rewritten:false};
fs.mkdirSync(work,{recursive:true});fs.writeFileSync(outPath,candidate);fs.writeFileSync(path.join(work,"prepare-results.json"),JSON.stringify(prep,null,2)+"\n");fs.writeFileSync(path.join(work,"registry-results.json"),JSON.stringify(registry,null,2)+"\n");
fs.writeFileSync("completion/v225-field-changes.tsv","id\tfield\told_value_json\tnew_value_json\n");
const decisions=[
[3589,"データベース","reviewed","—","Definition and examples correctly describe an organized, searchable database; データベース化して is translated adequately."],
[3594,"ストレート","blocked","—","Kotobank classifies it as 名・形動; app POS-map has 名詞 only, while examples use ストレートに／な. C11 required."],
[3599,"デビュー","reviewed","—","Noun+する marker is correct; debut as singer and first-team pitcher are natural."],
[3601,"ペア","reviewed","—","Pair of people or objects; note correctly prevents an exclusively romantic reading."],
[3607,"ボイコット","reviewed","—","Noun+する marker and collective refusal/participation senses are correct."],
[3614,"トリック","reviewed","—","Deceptive device/trick; mystery and advertising examples are natural."],
[3635,"ノルマ","reviewed","—","Assigned work quantity within a period; sales target and failure examples fit."],
[3636,"プライベート","blocked","—","Card usage includes プライベートなN and nominal プライベート; POS-map has 名詞 only. C11 required."],
[3637,"ムード","reviewed","—","Mood/atmosphere and wider social trend are both represented by examples."],
[3642,"ブランク","reviewed","—","Blank and period away from a job/activity are accurately distinguished."],
[3644,"ハーモニー","reviewed","—","General harmony and musical 和声 are correctly distinguished from a single 和音."],
[3646,"モダン","blocked","—","JMDict-based source and card examples show adjectival モダンな usage; POS-map has 名詞 only. C11 required."]
];
fs.writeFileSync("completion/v225-c10-review.tsv",["id\theadword\tdecision\tchanged_fields\treason",...decisions.map(r=>r.map(tsvCell).join("\t"))].join("\n")+"\n");
const acceptance=[
...reviewed.map(i=>["vocab",String(i),"reviewed","unchanged",d.value[String(i)].w]),
...blocked.map(i=>["vocab",String(i),"blocked","held_for_C11",d.value[String(i)].w]),
...pairRows.map(x=>["vocab_pair",String(x.index),"reviewed","unchanged",x.pair.a+"/"+x.pair.b])
];
fs.writeFileSync("completion/v225-acceptance.tsv",["kind\tkey\tdecision\tchange\tnote",...acceptance.map(r=>r.map(tsvCell).join("\t"))].join("\n")+"\n");
fs.writeFileSync("completion/v225-pair-review.tsv",["index\tkey\tdecision\tchange\tnote",...pairRows.map(x=>[x.index,x.key,"reviewed","unchanged",x.pair.note].map(tsvCell).join("\t"))].join("\n")+"\n");
const audit=[
"# JLPT N1 v225 — C10 авторський аудит",
"",
"База: повний v224 у main, SHA-256 "+baseSha+".",
"Кандидат: повний автономний HTML v225.",
"HTML bytes: "+bytes+".",
"SHA-256: "+sha+".",
"Git blob: "+blob+".",
"",
"TECHNICAL_STATUS_PENDING",
"",
"## Авторський обсяг",
"Перевірено 12 pending-карток: "+scope.join(", ")+".",
"- 9 reviewed без змін: "+reviewed.join(", ")+".",
"- 3 blocked до C11: "+blocked.join(", ")+".",
"- Реальних мовних помилок, що вимагали зміни полів у 9 прийнятих картках, не виявлено; не додавав змін заради кількості.",
"- Дві лексичні пари reviewed без зміни тексту: індекси 791 і 792.",
"- Пілот v153 охоплює ID121–320; для цих 12 ID рядків пілота немає. Переглянуто безпосередньо за v224.",
"- POS-map, grammar data, pair notes, quiz payloads, reading/cloze pools і target tables не змінювалися.",
"- Noun+する markers для デビュー та ボイコット збережено.",
"",
"## C11 blockers",
"- 3594 ストレート: Kotobank позначає 名・形動; POS-map містить лише 名詞.",
"- 3636 プライベート: картка використовує プライベートなN та іменникове プライベート; POS-map містить лише 名詞.",
"- 3646 モダン: картка використовує モダンなN, а JMDict-орієнтоване джерело підтверджує прикметникове вживання; POS-map містить лише 名詞.",
"- Жоден POS-map чи quiz pool не змінювався без окремого C11 аналізу.",
"",
"## Реєстр",
"Після v225: словник — 3406 reviewed /459 fixed_rechecked /35 pending /14 blocked; лексичні пари — 42 reviewed /1 fixed_rechecked /816 pending. Увесь реєстр — 3999 reviewed /461 fixed_rechecked /1373 pending /14 blocked із 5847. Авторський credit — 3865/3914; це не загальна готовність 1.0.",
"",
"## Межі",
"Це авторський мовний перегляд і технічний пакет, не незалежне лінгвістичне приймання. Незалежне лінгвістичне, фізичне Android/Windows та правове/походження приймання залишаються відкритими."
].join("\n");
fs.writeFileSync("JLPT_N1_v225_audit.md",audit+"\n");
const cp={version:"v225",base_version:"v224",base_main_sha:guard,base_html_sha256:baseSha,base_html_blob:"e125da7bc2d404409c3d9f8bbfb2666eeee43b99",base_html_bytes:6952257,branch:"work/v225-c10-next-pending",scope_ids:scope,scope_status:"pending in main after v224; selected after older follow-ups",fixed_rechecked_ids:fixed,reviewed_ids:reviewed,blocked_ids:blocked,field_updates:[],pair_reviewed:pairScope,pilot_covered_ids:[],pilot_missing_ids:scope,author_credit_before:3856,author_credit_after:3865,author_review:"completed; 9 cards credited, 3 blocked for C11 POS/quiz analysis",technical_verification:"pending",independent_acceptance:"not performed",physical_device_acceptance:"not performed",provenance_legal_acceptance:"not performed",main_guard:guard,publication_policy:"publish only exact verified artifacts; never merge work branch",status:"candidate and registry prepared; syntax and Chromium verification pending",candidate_sha256:sha,candidate_blob_sha:blob,candidate_bytes:bytes,pair_changed:[],exact_rollback:true,publication_status:"pending",chromium_verification:"pending",workflow_run_id:null};
fs.writeFileSync(path.join(work,"checkpoint.json"),JSON.stringify(cp,null,2)+"\n");
console.log(JSON.stringify({pass:true,candidate_sha256:sha,candidate_blob_sha:blob,candidate_bytes:bytes,reviewed:reviewed,blocked:blocked,pair_reviewed:pairScope,registry_after:after},null,2));
