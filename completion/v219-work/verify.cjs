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
const basePath='JLPT_N1_ukrainian_reading_v218.html',outPath='JLPT_N1_ukrainian_reading_v219.html',work='completion/v219-work';
const base=fs.readFileSync(basePath,'utf8'),baseSha=crypto.createHash('sha256').update(base).digest('hex');
assert.equal(baseSha,'adc7376d13a74d6d2f9ed00a5d35a9695f4728066aa66659b1ab01218433e425','base HTML changed; stop and rebase');
const d=extractConst(base,'VOCAB_DETAILS_BY_ID'),v=extractConst(base,'DEFAULT_VOCAB').value,pos=extractConst(base,'VOCAB_POS_BY_ID').value,g=extractConst(base,'GRAMMAR_DETAILS_BY_ID').value,pairs=extractConst(base,'VOCAB_AUDITED_PAIRS');
const stable=['DEFAULT_VOCAB','VOCAB_POS_BY_ID','GRAMMAR_DETAILS_BY_ID','REVIEWED_MEANING_QUIZZES','REVIEWED_READING_OPTIONS','VOCAB_KANA_EXAMPLE_TARGETS','REVIEWED_EXAMPLE_TARGETS'].map(n=>[n,extractConst(base,n).value]);
assert.equal(v.length,3914);assert.equal(Object.keys(g).length,130);assert.equal(Object.keys(d.value).length,3914);assert.equal(pairs.value.length,859);
const fixed=[3281,3293,3296,3312,3319,3321,3323,3325,3336],reviewed=[3277,3280],blocked=[3337],scope=[3277,3280,3281,3293,3296,3312,3319,3321,3323,3325,3336,3337],pairScope=[747,749,751,752,757,761,764];
const before=JSON.parse(JSON.stringify(d.value)),pairBefore=JSON.parse(JSON.stringify(pairs.value)),fieldChanges=[],pairChanges=[];
function set(id,field,oldValue,newValue){assert.equal(d.value[String(id)][field],oldValue,'unexpected old value '+id+'.'+field);d.value[String(id)][field]=newValue;fieldChanges.push({id,field,oldValue,newValue});}
function setArray(id,field,index,oldValue,newValue){assert.equal(d.value[String(id)][field][index],oldValue,'unexpected old array value '+id+'.'+field+'['+index+']');d.value[String(id)][field][index]=newValue;fieldChanges.push({id,field:field+'['+index+']',oldValue,newValue});}
set(3281,'t','якщо вже наполягати; через силу; навмисне всупереч природному перебігу','через силу; попри небажання; якщо вже неодмінно треба щось назвати');
set(3293,'t','якось, ледве, насилу вдаючись','якось; більш-менш; насилу');
setArray(3293,'exampleTranslations',1,'Із браком обігових коштів якось упоралися, але подальші перспективи неясні.','Проблеми з обігом коштів якось вдалося подолати, але подальші перспективи неясні.');
set(3296,'usage','どうやら〜ようだ／らしい — висновок за наявними ознаками, ще не повна впевненість. Історично має й значення «якось», але в цих прикладах не замінюється на どうにか.','どうやら〜ようだ／らしい — висновок за наявними ознаками, хоча впевненість не повна. У сучасному вживанні має й окреме значення «якось, більш-менш упоратися»; у цих прикладах ужито саме значення припущення, тому не замінюється на どうにか.');
setArray(3312,'exampleTranslations',1,'Як він міг зрадити після стількох отриманих послуг!','Як він міг зрадити тих, хто стільки для нього зробив!');
setArray(3319,'exampleTranslations',1,'Ручного введення персональних даних просимо за можливості уникати.','Наскільки можливо, уникайте ручного введення персональних даних.');
setArray(3321,'exampleTranslations',0,'Лікар наказав тиждень дотримуватися спокою.','Лікар наказав протягом тижня дотримуватися фізичного спокою.');
setArray(3323,'examples',1,'天気予報どおり、案の定、夕方から雨が降り出した。','午後から空が暗くなり始め、案の定、夕方には雨が降り出した。');
setArray(3323,'exampleTranslations',1,'Як і очікували за прогнозом, надвечір почався дощ.','Удень небо почало темніти, і, як і очікувалося, надвечір пішов дощ.');
setArray(3325,'examples',1,'事故原因の究明は依然、難航している状態が続く。','事故原因の究明は依然として難航している。');
setArray(3325,'exampleTranslations',1,'З’ясування причин аварії, як і раніше, просувається важко.','З’ясування причин аварії й досі просувається важко.');
set(3336,'usage','Aでさえ…、ましてB… — від сильнішої підстави робиться висновок «тим більше». У запереченні переклад може бути «не кажучи вже про».','Aでさえ…、ましてB… — якщо твердження справджується вже для випадку A, то для ще виразнішого або складнішого випадку B воно тим більше слушне. У запереченні природний відповідник може бути «не кажучи вже про».');
assert.equal(fieldChanges.length,11);
const pairOld=pairs.value[752].note,pairNew='どうにか間に合った — якось удалося; どうやら間に合ったようだ — схоже, встигли. どうにか仕事を終えた。— Насилу завершили роботу. どうやら雨になりそうだ。— Схоже, піде дощ. Обидва прислівники, але тут перший оцінює подолання труднощів, другий — упевненість висновку. У сучасному вживанні どうやら також має окреме значення «якось, більш-менш упоратися»; у наведеному прикладі йдеться про припущення за ознаками.';
assert.equal(pairOld,'どうにか間に合った — якось удалося; どうやら間に合ったようだ — схоже, встигли. どうにか仕事を終えた。— Насилу завершили роботу. どうやら雨になりそうだ。— Схоже, піде дощ. Обидва прислівники, але тут перший оцінює подолання труднощів, другий — упевненість висновку. У старішому значенні どうやら теж може означати «якось»; це не значення поточних прикладів.');
pairs.value[752].note=pairNew;pairChanges.push({index:752,key:'752:3293:3296',oldValue:pairOld,newValue:pairNew});
const changed=Object.keys(d.value).filter(id=>JSON.stringify(d.value[id])!==JSON.stringify(before[id])).map(Number).sort((a,b)=>a-b);
assert.deepEqual(changed,fixed);
const pairChanged=pairs.value.map((x,i)=>JSON.stringify(x)!==JSON.stringify(pairBefore[i])?i:null).filter(x=>x!==null);
assert.deepEqual(pairChanged,[752]);
for(const id of scope){const row=v.find(x=>Number(x.id)===id);assert.ok(row,'missing id '+id);assert.ok(d.value[String(id)].w);assert.equal(d.value[String(id)].examples.length,2);assert.equal(d.value[String(id)].exampleTranslations.length,2);assert.ok(pos[String(id)]);}
for(const id of reviewed)assert.equal(JSON.stringify(d.value[String(id)]),JSON.stringify(before[String(id)]));
for(const id of blocked)assert.equal(JSON.stringify(d.value[String(id)]),JSON.stringify(before[String(id)]));
let candidate=base;
const replacements=[{start:d.start,end:d.end,text:JSON.stringify(d.value)},{start:pairs.start,end:pairs.end,text:JSON.stringify(pairs.value)}].sort((a,b)=>b.start-a.start);
for(const x of replacements)candidate=candidate.slice(0,x.start)+x.text+candidate.slice(x.end);
const oldTitle='<title>JLPT N1 — ウクライナ語対応学習アプリ · v218</title>',newTitle='<title>JLPT N1 — ウクライナ語対応学習アプリ · v219</title>';
assert.equal(candidate.split(oldTitle).length,2);candidate=candidate.replace(oldTitle,newTitle);
let rollback=candidate.replace(newTitle,oldTitle);
const rd=extractConst(rollback,'VOCAB_DETAILS_BY_ID'),rp=extractConst(rollback,'VOCAB_AUDITED_PAIRS');
const restore=[{start:rd.start,end:rd.end,text:d.literal},{start:rp.start,end:rp.end,text:pairs.literal}].sort((a,b)=>b.start-a.start);
for(const x of restore)rollback=rollback.slice(0,x.start)+x.text+rollback.slice(x.end);
assert.equal(rollback,base,'exact rollback failed');
for(const [name,original] of stable)assert.deepEqual(extractConst(candidate,name).value,original,name+' changed');
assert.equal(extractConst(candidate,'VOCAB_AUDITED_PAIRS').value.length,859);
const registerPath='completion/review-register.csv',register=parseCSV(fs.readFileSync(registerPath,'utf8'));
assert.equal(register.length,5848,'unexpected registry row count');
const header=register[0],col=k=>header.indexOf(k);assert.ok(col('kind')>=0&&col('key')>=0&&col('finalReview')>=0&&col('evidence')>=0);
const decisionById=new Map([...fixed.map(id=>[id,'fixed_rechecked']),...reviewed.map(id=>[id,'reviewed']),...blocked.map(id=>[id,'blocked'])]),seenVocab=new Set(),seenPairs=new Set();
for(const row of register.slice(1)){
 if(row[col('kind')]==='vocab'&&decisionById.has(Number(row[col('key')]))){
  const id=Number(row[col('key')]);assert.equal(row[col('finalReview')],'pending','record not pending: '+id);assert.ok(!seenVocab.has(id),'duplicate vocab key '+id);seenVocab.add(id);row[col('finalReview')]=decisionById.get(id);
  row[col('evidence')]=id===3337?'completion/v219-c10-review.tsv#3337; content checked; noun use in 一切 requires separate C11 POS/pool-impact review; POS-map unchanged; author review, not independent':'JLPT_N1_v219_audit.md; completion/v219-acceptance.tsv; completion/v219-c10-review.tsv; author review, not independent; no v153 pilot rows for IDs above 320';
 }
}
assert.equal(seenVocab.size,12);
for(const index of pairScope){
 const pair=pairs.value[index],key=index+':'+pair.a+':'+pair.b;
 const row=register.slice(1).find(r=>r[col('kind')]==='vocab_pair'&&r[col('key')]===key);
 assert.ok(row,'missing pair register row '+key);assert.equal(row[col('finalReview')],'pending','pair not pending '+key);assert.ok(!seenPairs.has(key));seenPairs.add(key);row[col('finalReview')]='reviewed';row[col('evidence')]='completion/v219-pair-review.tsv#'+index+'; author review of the exact pair and stated senses; not independent'+(index===752?'; note corrected to remove unsupported historical restriction':'');
}
assert.equal(seenPairs.size,7);
fs.writeFileSync(registerPath,register.map(row=>row.map(csvCell).join(',')).join('\n')+'\n');
function counts(kind){const out={reviewed:0,fixed_rechecked:0,pending:0,blocked:0,total:0};for(const row of register.slice(1)){if(kind&&row[col('kind')]!==kind)continue;if(Object.prototype.hasOwnProperty.call(out,row[col('finalReview')]))out[row[col('finalReview')]]++;out.total++;}return out;}
const after={all:counts(null),vocabulary:counts('vocab'),vocab_pair:counts('vocab_pair')};
assert.deepEqual(after,{all:{reviewed:3944,fixed_rechecked:442,pending:1460,blocked:1,total:5847},vocabulary:{reviewed:3366,fixed_rechecked:440,pending:107,blocked:1,total:3914},vocab_pair:{reviewed:27,fixed_rechecked:1,pending:831,blocked:0,total:859}});
const bytes=Buffer.byteLength(candidate),sha=crypto.createHash('sha256').update(candidate).digest('hex'),blob=crypto.createHash('sha1').update(Buffer.from('blob '+bytes+'\0')).update(Buffer.from(candidate)).digest('hex');
const prepare={pass:true,base_version:'v218',base_main_sha:'845f5c9c114a436016a9242fbb0fc0235eeb7f3c',main_status_commit:'c5e13bbe3a2845f3821ce8cd3aaa4289a3ee7116',base_sha256:baseSha,candidate_version:'v219',candidate_sha256:sha,candidate_blob_sha:blob,candidate_bytes:bytes,vocabulary_records:3914,grammar_records:130,lexical_pairs:859,unique_vocabulary_ids:3914,review_scope:scope,fixed_rechecked_ids:fixed,reviewed_ids:reviewed,blocked_ids:blocked,updated_fields:fieldChanges.length,changed_cards:fixed,pair_reviewed_indices:pairScope,pair_changed_indices:pairChanged,pair_updates:pairChanges.length,pos_map_unchanged:true,reading_and_cloze_pools_unchanged:true,example_target_tables_unchanged:true,japanese_examples_changed:[3323,3325],example_target_rows_found_for_changed_examples:0,author_credit_before:3795,author_credit_addition:11,author_credit_after:3806,pilot_covered_ids:[],pilot_missing_ids:scope,exact_rollback:true,register_after:after,author_review_only:true,independent_acceptance:'not performed',physical_device_acceptance:'not performed',provenance_legal_acceptance:'not performed'};
const registry={pass:true,register_rows:register.length-1,after,scope_updated:scope,pair_scope_updated:pairScope,blocked_scope:[3337],duplicate_scope_keys:0,records_deleted:0,history_rewritten:false};
fs.mkdirSync(work,{recursive:true});
fs.writeFileSync(outPath,candidate);
fs.writeFileSync(path.join(work,'prepare-results.json'),JSON.stringify(prepare,null,2)+'\n');
fs.writeFileSync(path.join(work,'registry-results.json'),JSON.stringify(registry,null,2)+'\n');
const fieldRows=['id\tfield\told_value_json\tnew_value_json',...fieldChanges.map(x=>[x.id,x.field,JSON.stringify(x.oldValue),JSON.stringify(x.newValue)].map(tsvCell).join('\t'))];
fs.writeFileSync('completion/v219-field-changes.tsv',fieldRows.join('\n')+'\n');
const decisionRows=[
 ['3277','さぞや','reviewed','—','Both examples, definition and empathic conjecture usage checked; no change'],
 ['3280','さも','reviewed','—','As-if use, examples and caveat against assuming deception checked; no change'],
 ['3281','しいて','fixed_rechecked','t','Remove misleading deliberate-against-natural-course gloss; retain forced/pressed and forced-choice senses'],
 ['3293','どうにか','fixed_rechecked','t; exampleTranslations[1]','Naturalize gloss and avoid over-specific cash-shortage translation for 資金繰り'],
 ['3296','どうやら','fixed_rechecked','usage','Correct claim that the “somehow” sense is merely historical; distinguish two current senses'],
 ['3312','よくも','fixed_rechecked','exampleTranslations[1]','Replace calque of 世話になる with natural Ukrainian'],
 ['3319','極力','fixed_rechecked','exampleTranslations[1]','Preserve the maximum-effort force of 極力避ける'],
 ['3321','安静に','fixed_rechecked','exampleTranslations[0]','Specify physical rest without asserting mandatory bed rest'],
 ['3323','案の定','fixed_rechecked','examples[1]; exampleTranslations[1]','Remove redundant forecast/as-expected cue and keep a clear prior sign'],
 ['3325','依然','fixed_rechecked','examples[1]; exampleTranslations[1]','Remove redundant continuation wording and retain unchanged-state meaning'],
 ['3336','まして','fixed_rechecked','usage','Explain the logical direction from A to the more obvious/stronger B case'],
 ['3337','一切','blocked','—','Content checked; noun use is documented but app POS map/pool impact requires C11']
];
fs.writeFileSync('completion/v219-c10-review.tsv',['id\theadword\tdecision\tchanged_fields\treason',...decisionRows.map(r=>r.map(tsvCell).join('\t'))].join('\n')+'\n');
const acceptance=[
 ['vocab','3277','reviewed','unchanged','さぞや'],
 ['vocab','3280','reviewed','unchanged','さも'],
 ...fixed.map(id=>['vocab',String(id),'fixed_rechecked','changed',String(d.value[String(id)].w)]),
 ['vocab','3337','blocked','unchanged','一切 — C11 POS/pool impact'],
 ...pairScope.map(i=>['vocab_pair',String(i),'reviewed',i===752?'note corrected':'unchanged',String(pairs.value[i].a)+'/'+String(pairs.value[i].b)])
];
fs.writeFileSync('completion/v219-acceptance.tsv',['kind\tkey\tdecision\tchange\tnote',...acceptance.map(r=>r.map(tsvCell).join('\t'))].join('\n')+'\n');
const pairRows=['index\tkey\tdecision\tchange\tnote',...pairScope.map(i=>{const p=pairs.value[i];return[i,i+':'+p.a+':'+p.b,'reviewed',i===752?'note corrected':'unchanged',p.note].map(tsvCell).join('\t');})];
fs.writeFileSync('completion/v219-pair-review.tsv',pairRows.join('\n')+'\n');
const auditPath='JLPT_N1_v219_audit.md';let audit=fs.readFileSync(auditPath,'utf8');
audit=audit.replace('__V219_SHA256__',sha).replace('__V219_BYTES__',String(bytes)).replace('__V219_BLOB__',blob).replace('TECHNICAL_STATUS_PENDING','TECHNICAL_STATUS_PENDING');
fs.writeFileSync(auditPath,audit);
const cpPath=path.join(work,'checkpoint.json'),cp=JSON.parse(fs.readFileSync(cpPath,'utf8'));
Object.assign(cp,{status:'candidate and registry prepared; syntax and Chromium verification pending',candidate_sha256:sha,candidate_blob_sha:blob,candidate_bytes:bytes,fixed_rechecked_ids:fixed,reviewed_ids:reviewed,blocked_ids:blocked,field_updates:fieldChanges.map(x=>({id:x.id,field:x.field})),pair_reviewed:pairScope,pair_changed:pairChanged,pilot_covered_ids:[],pilot_missing_ids:scope,author_credit_after:3806,author_review:'completed; 11 cards credited, one C11 POS block',technical_verification:'pending',exact_rollback:true});
fs.writeFileSync(cpPath,JSON.stringify(cp,null,2)+'\n');
console.log(JSON.stringify({pass:true,sha,blob,bytes,changed_cards:changed,field_changes:fieldChanges.length,pair_changed:pairChanged,registry:after},null,2));
