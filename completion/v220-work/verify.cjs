const fs=require('node:fs'),crypto=require('node:crypto'),assert=require('node:assert/strict'),path=require('node:path');
function extractConst(source,name){
 const marker='const '+name+' =',at=source.indexOf(marker);assert.ok(at>=0,'missing '+name);
 let start=at+marker.length;while(/\s/.test(source[start]))start++;
 const open=source[start],close=open==='['?']':'}';let depth=0,inString=false,escaped=false;
 for(let i=start;i<source.length;i++){const c=source[i];
  if(inString){if(escaped)escaped=false;else if(c==='\\')escaped=true;else if(c==='"')inString=false;}
  else{if(c==='"')inString=true;else if(c===open)depth++;else if(c===close){depth--;if(depth===0)return{start,end:i+1,value:JSON.parse(source.slice(start,i+1)),literal:source.slice(start,i+1)};}}
 }throw new Error('unterminated '+name);
}
function parseCSV(s){const rows=[];let row=[],f='',q=false;for(let i=0;i<s.length;i++){const c=s[i];if(q){if(c==='"'&&s[i+1]==='"'){f+='"';i++;}else if(c==='"')q=false;else f+=c;}else if(c==='"')q=true;else if(c===','){row.push(f);f='';}else if(c==='\n'){row.push(f);rows.push(row);row=[];f='';}else if(c!=='\r')f+=c;}if(f.length||row.length){row.push(f);rows.push(row);}return rows;}
function csvCell(v){const s=String(v??'');return /[",\r\n]/.test(s)?'"'+s.replace(/"/g,'""')+'"':s;}
function tsvCell(v){return String(v??'').replace(/\t/g,' ').replace(/\r?\n/g,' ');}
const basePath='JLPT_N1_ukrainian_reading_v219.html',outPath='JLPT_N1_ukrainian_reading_v220.html',work='completion/v220-work';
const base=fs.readFileSync(basePath,'utf8'),baseSha=crypto.createHash('sha256').update(base).digest('hex');
assert.equal(baseSha,'abfaf537a365d5389138f1f0e514c20f2f181cf51ac33ea7b34fb7de48f22481','base HTML changed; stop and rebase');
const d=extractConst(base,'VOCAB_DETAILS_BY_ID'),v=extractConst(base,'DEFAULT_VOCAB').value,pos=extractConst(base,'VOCAB_POS_BY_ID').value,g=extractConst(base,'GRAMMAR_DETAILS_BY_ID').value,pairs=extractConst(base,'VOCAB_AUDITED_PAIRS').value,quizzes=extractConst(base,'REVIEWED_MEANING_QUIZZES').value;
assert.equal(v.length,3914);assert.equal(Object.keys(g).length,130);assert.equal(Object.keys(d.value).length,3914);assert.equal(pairs.length,859);
const fixed=[3344,3349,3364,3369,3370],reviewed=[3352,3357,3360,3368,3373],blocked=[3345,3363],scope=[3344,3345,3349,3352,3357,3360,3363,3364,3368,3369,3370,3373],pairScope=[413,760];
const before=JSON.parse(JSON.stringify(d.value)),fieldChanges=[];
function set(id,field,oldValue,newValue){assert.equal(d.value[String(id)][field],oldValue,'unexpected old value '+id+'.'+field);d.value[String(id)][field]=newValue;fieldChanges.push({id,field,oldValue,newValue});}
function setArray(id,field,index,oldValue,newValue){assert.equal(d.value[String(id)][field][index],oldValue,'unexpected old array value '+id+'.'+field+'['+index+']');d.value[String(id)][field][index]=newValue;fieldChanges.push({id,field:field+'['+index+']',oldValue,newValue});}
set(3344,'t','тепер, нині, у цей момент','нині, тепер уже; на цьому етапі');
setArray(3344,'exampleTranslations',1,'Нині настав час суворо питати з компаній за їхню суспільну відповідальність.','Нині суспільство суворо вимагає від компаній соціальної відповідальності.');
setArray(3349,'examples',0,'計画には若干の修正が必要になるかもしれない。','計画には若干修正が必要になるかもしれない。');
setArray(3349,'exampleTranslations',0,'Можливо, план потребуватиме деяких змін.','Можливо, план доведеться трохи скоригувати.');
setArray(3349,'examples',1,'昨年に比べ、売上は若干の増加にとどまった。','昨年に比べ、売上は若干増加した。');
setArray(3349,'exampleTranslations',1,'Порівняно з минулим роком продажі зросли лише трохи.','Порівняно з минулим роком продажі трохи зросли.');
setArray(3364,'examples',0,'海外市場の需要は、相変わらず低迷が続いている。','海外市場の需要は、相変わらず低迷している。');
setArray(3369,'examples',0,'彼の頼みなら、大概のことは引き受けるつもりだ。','彼は大概、約束の時間に遅れてくる。');
setArray(3369,'exampleTranslations',0,'Якщо попросить він, я готовий узятися майже за будь-яку справу.','Він зазвичай запізнюється на домовлений час.');
setArray(3370,'examples',1,'大方の予想に反して、新人が優勝を果たした。','この問題の原因は、大方解明された。');
setArray(3370,'exampleTranslations',1,'Усупереч очікуванням більшості, переміг новачок.','Причини цієї проблеми здебільшого з’ясовано.');
assert.equal(fieldChanges.length,11);
const changed=Object.keys(d.value).filter(id=>JSON.stringify(d.value[id])!==JSON.stringify(before[id])).map(Number).sort((a,b)=>a-b);
assert.deepEqual(changed,fixed);
for(const id of scope){const row=v.find(x=>Number(x.id)===id);assert.ok(row,'missing id '+id);assert.ok(d.value[String(id)].w);assert.equal(d.value[String(id)].examples.length,2);assert.equal(d.value[String(id)].exampleTranslations.length,2);assert.ok(pos[String(id)]);}
for(const id of reviewed)assert.equal(JSON.stringify(d.value[String(id)]),JSON.stringify(before[String(id)]));
for(const id of blocked)assert.equal(JSON.stringify(d.value[String(id)]),JSON.stringify(before[String(id)]));
assert.ok(pos['3345'].includes('副詞')&&!pos['3345'].includes('ナ形'));
assert.ok(pos['3363'].includes('副詞')&&!pos['3363'].includes('ナ形'));
assert.ok(quizzes['v_3345']?.byExample?.['天候に恵まれず、散々な結果に終わった遠征だった。']);
assert.ok(quizzes['v_3363']?.note);
const targetNames=['VOCAB_KANA_EXAMPLE_TARGETS','REVIEWED_EXAMPLE_TARGETS','REVIEWED_READING_OPTIONS'];
for(const n of targetNames)assert.deepEqual(extractConst(base,n).value,extractConst(base,n).value);
const changedExampleIds=[3349,3364,3369,3370];
for(const n of ['VOCAB_KANA_EXAMPLE_TARGETS','REVIEWED_EXAMPLE_TARGETS']){
 const json=JSON.stringify(extractConst(base,n).value);
 for(const id of changedExampleIds)assert.ok(!new RegExp('(^|[^0-9])'+id+'([^0-9]|$)').test(json),'unexpected target row for '+n+' id '+id);
}
let candidate=base.slice(0,d.start)+JSON.stringify(d.value)+base.slice(d.end);
const oldTitle='<title>JLPT N1 — ウクライナ語対応学習アプリ · v219</title>',newTitle='<title>JLPT N1 — ウクライナ語対応学習アプリ · v220</title>';
assert.equal(candidate.split(oldTitle).length,2);candidate=candidate.replace(oldTitle,newTitle);
let rollback=candidate.replace(newTitle,oldTitle);const rd=extractConst(rollback,'VOCAB_DETAILS_BY_ID');
rollback=rollback.slice(0,rd.start)+d.literal+rollback.slice(rd.end);assert.equal(rollback,base,'exact rollback failed');
const stable=['DEFAULT_VOCAB','VOCAB_POS_BY_ID','GRAMMAR_DETAILS_BY_ID','VOCAB_AUDITED_PAIRS','REVIEWED_MEANING_QUIZZES','REVIEWED_READING_OPTIONS','VOCAB_KANA_EXAMPLE_TARGETS','REVIEWED_EXAMPLE_TARGETS'];
for(const n of stable)assert.deepEqual(extractConst(candidate,n).value,extractConst(base,n).value,n+' changed');
const registerPath='completion/review-register.csv',register=parseCSV(fs.readFileSync(registerPath,'utf8'));
assert.equal(register.length,5848,'unexpected registry row count');
const header=register[0],col=k=>header.indexOf(k);assert.ok(col('kind')>=0&&col('key')>=0&&col('finalReview')>=0&&col('evidence')>=0);
const decisionById=new Map([...fixed.map(id=>[id,'fixed_rechecked']),...reviewed.map(id=>[id,'reviewed']),...blocked.map(id=>[id,'blocked'])]),seenVocab=new Set(),seenPairs=new Set();
for(const row of register.slice(1)){
 if(row[col('kind')]==='vocab'&&decisionById.has(Number(row[col('key')]))){
  const id=Number(row[col('key')]);assert.equal(row[col('finalReview')],'pending','record not pending: '+id);assert.ok(!seenVocab.has(id),'duplicate vocab key '+id);seenVocab.add(id);row[col('finalReview')]=decisionById.get(id);
  row[col('evidence')]=id===3345?'completion/v220-c10-review.tsv#3345; mixed adverb and な-adjective example plus byExample payload; POS-map remains 副詞; C11 required; no data changed':id===3363?'completion/v220-c10-review.tsv#3363; adjectival 相当な時間 example conflicts with adverbial POS and quiz scope; C11 required; no data changed':'JLPT_N1_v220_audit.md; completion/v220-acceptance.tsv; completion/v220-c10-review.tsv; author review, not independent; no v153 pilot rows for IDs above 320';
 }
}
assert.equal(seenVocab.size,12);
for(const index of pairScope){
 const pair=pairs[index],key=index+':'+pair.a+':'+pair.b;
 const row=register.slice(1).find(r=>r[col('kind')]==='vocab_pair'&&r[col('key')]===key);
 assert.ok(row,'missing pair register row '+key);assert.equal(row[col('finalReview')],'pending','pair not pending '+key);assert.ok(!seenPairs.has(key));seenPairs.add(key);row[col('finalReview')]='reviewed';row[col('evidence')]='completion/v220-pair-review.tsv#'+index+'; author review of the exact pair and stated senses; not independent'+(index===413?'; ID3363 card remains blocked for separate C11 POS/quiz analysis':'');
}
assert.equal(seenPairs.size,2);
fs.writeFileSync(registerPath,register.map(row=>row.map(csvCell).join(',')).join('\n')+'\n');
function counts(kind){const out={reviewed:0,fixed_rechecked:0,pending:0,blocked:0,total:0};for(const row of register.slice(1)){if(kind&&row[col('kind')]!==kind)continue;if(Object.prototype.hasOwnProperty.call(out,row[col('finalReview')]))out[row[col('finalReview')]]++;out.total++;}return out;}
const after={all:counts(null),vocabulary:counts('vocab'),vocab_pair:counts('vocab_pair')};
assert.deepEqual(after,{all:{reviewed:3951,fixed_rechecked:447,pending:1446,blocked:3,total:5847},vocabulary:{reviewed:3371,fixed_rechecked:445,pending:95,blocked:3,total:3914},vocab_pair:{reviewed:29,fixed_rechecked:1,pending:829,blocked:0,total:859}});
const bytes=Buffer.byteLength(candidate),sha=crypto.createHash('sha256').update(candidate).digest('hex'),blob=crypto.createHash('sha1').update(Buffer.from('blob '+bytes+'\0')).update(Buffer.from(candidate)).digest('hex');
const prepare={pass:true,base_version:'v219',base_main_sha:'cb5fc9661df6abf8ea914d560ae2fc743f701948',main_status_commit:'919cc7dd73c27b6cb526e5323b16f10ef0339bcf',base_sha256:baseSha,candidate_version:'v220',candidate_sha256:sha,candidate_blob_sha:blob,candidate_bytes:bytes,vocabulary_records:3914,grammar_records:130,lexical_pairs:859,unique_vocabulary_ids:3914,review_scope:scope,fixed_rechecked_ids:fixed,reviewed_ids:reviewed,blocked_ids:blocked,updated_fields:fieldChanges.length,changed_cards:fixed,pair_reviewed_indices:pairScope,pair_changed_indices:[],pair_updates:0,pos_map_unchanged:true,reading_and_cloze_pools_unchanged:true,example_target_tables_unchanged:true,reviewed_meaning_quizzes_unchanged:true,japanese_examples_changed:changedExampleIds,example_target_rows_found_for_changed_examples:0,author_credit_before:3806,author_credit_addition:10,author_credit_after:3816,pilot_covered_ids:[],pilot_missing_ids:scope,exact_rollback:true,register_after:after,author_review_only:true,independent_acceptance:'not performed',physical_device_acceptance:'not performed',provenance_legal_acceptance:'not performed'};
const registry={pass:true,register_rows:register.length-1,after,scope_updated:scope,pair_scope_updated:pairScope,blocked_scope:blocked,duplicate_scope_keys:0,records_deleted:0,history_rewritten:false};
fs.mkdirSync(work,{recursive:true});fs.writeFileSync(outPath,candidate);
fs.writeFileSync(path.join(work,'prepare-results.json'),JSON.stringify(prepare,null,2)+'\n');
fs.writeFileSync(path.join(work,'registry-results.json'),JSON.stringify(registry,null,2)+'\n');
const fieldRows=['id\tfield\told_value_json\tnew_value_json',...fieldChanges.map(x=>[x.id,x.field,JSON.stringify(x.oldValue),JSON.stringify(x.newValue)].map(tsvCell).join('\t'))];
fs.writeFileSync('completion/v220-field-changes.tsv',fieldRows.join('\n')+'\n');
const decisionRows=[
 ['3344','今や','fixed_rechecked','t; exampleTranslations[1]','Narrow “у цей момент” to current-era/state change; naturalize social-responsibility translation'],
 ['3345','散々','blocked','—','The card includes adverbial and な-adjective uses while POS-map is only 副詞; byExample quiz depends on the adjective example; defer to C11'],
 ['3349','若干','fixed_rechecked','examples[0]; exampleTranslations[0]; examples[1]; exampleTranslations[1]','Make both examples consistently adverbial, matching the current POS-map'],
 ['3352','所詮','reviewed','—','Resigned/limiting conclusion sense and both examples checked; no change'],
 ['3357','真っ二つに','reviewed','—','Literal and figurative two-way split checked; no change'],
 ['3360','先立って','reviewed','—','Reading さきだって and pre-event use checked; no change'],
 ['3363','相当','blocked','—','Adverbial quiz and POS conflict with adjectival 相当な時間 example/usage; defer to C11'],
 ['3364','相変わらず','fixed_rechecked','examples[0]','Remove redundant 低迷が続いている while preserving unchanged-state meaning'],
 ['3368','大して','reviewed','—','Negative-polarity examples and limited-degree meaning checked; no change'],
 ['3369','大概','fixed_rechecked','examples[0]; exampleTranslations[0]','Use an adverbial example instead of 大概のこと, aligning the card POS'],
 ['3370','大方','fixed_rechecked','examples[1]; exampleTranslations[1]','Use an adverbial “mostly” example instead of nominal 大方の予想'],
 ['3373','中途半端に','reviewed','—','Incomplete/half-hearted action and both examples checked; no change']
];
fs.writeFileSync('completion/v220-c10-review.tsv',['id\theadword\tdecision\tchanged_fields\treason',...decisionRows.map(r=>r.map(tsvCell).join('\t'))].join('\n')+'\n');
const acceptance=[
 ...fixed.map(id=>['vocab',String(id),'fixed_rechecked','changed',String(d.value[String(id)].w)]),
 ...reviewed.map(id=>['vocab',String(id),'reviewed','unchanged',String(d.value[String(id)].w)]),
 ...blocked.map(id=>['vocab',String(id),'blocked','unchanged',String(d.value[String(id)].w)+' — C11 POS/quiz']),
 ...pairScope.map(i=>['vocab_pair',String(i),'reviewed','unchanged',String(pairs[i].a)+'/'+String(pairs[i].b)])
];
fs.writeFileSync('completion/v220-acceptance.tsv',['kind\tkey\tdecision\tchange\tnote',...acceptance.map(r=>r.map(tsvCell).join('\t'))].join('\n')+'\n');
fs.writeFileSync('completion/v220-pair-review.tsv',['index\tkey\tdecision\tchange\tnote',...pairScope.map(i=>{const p=pairs[i];return[i,i+':'+p.a+':'+p.b,'reviewed','unchanged',p.note].map(tsvCell).join('\t');})].join('\n')+'\n');
let audit=fs.readFileSync('JLPT_N1_v220_audit.md','utf8').replace('__V220_SHA256__',sha).replace('__V220_BYTES__',String(bytes)).replace('__V220_BLOB__',blob);
fs.writeFileSync('JLPT_N1_v220_audit.md',audit);
const cpPath=path.join(work,'checkpoint.json'),cp=JSON.parse(fs.readFileSync(cpPath,'utf8'));
Object.assign(cp,{status:'candidate and registry prepared; syntax and Chromium verification pending',candidate_sha256:sha,candidate_blob_sha:blob,candidate_bytes:bytes,fixed_rechecked_ids:fixed,reviewed_ids:reviewed,blocked_ids:blocked,field_updates:fieldChanges.map(x=>({id:x.id,field:x.field})),pair_reviewed:pairScope,pair_changed:[],pilot_covered_ids:[],pilot_missing_ids:scope,author_credit_after:3816,author_review:'completed; 10 cards credited, two C11 POS/quiz blocks',technical_verification:'pending',exact_rollback:true});
fs.writeFileSync(cpPath,JSON.stringify(cp,null,2)+'\n');
console.log(JSON.stringify({pass:true,sha,blob,bytes,changed_cards:changed,field_changes:fieldChanges.length,registry:after},null,2));
