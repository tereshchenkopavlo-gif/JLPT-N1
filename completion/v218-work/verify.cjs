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
const basePath='JLPT_N1_ukrainian_reading_v217.html',outPath='JLPT_N1_ukrainian_reading_v218.html',work='completion/v218-work';
const base=fs.readFileSync(basePath,'utf8'),baseSha=crypto.createHash('sha256').update(base).digest('hex');
assert.equal(baseSha,'58d01e555bdf84810bd16237d8fcf755cbdcf756fb1a8784046eca144e58f79b','base HTML changed; stop and rebase');
const d=extractConst(base,'VOCAB_DETAILS_BY_ID'),v=extractConst(base,'DEFAULT_VOCAB').value,p=extractConst(base,'VOCAB_POS_BY_ID').value,g=extractConst(base,'GRAMMAR_DETAILS_BY_ID').value,pairs=extractConst(base,'VOCAB_AUDITED_PAIRS').value;
const stable=['REVIEWED_MEANING_QUIZZES','REVIEWED_READING_OPTIONS','VOCAB_KANA_EXAMPLE_TARGETS','REVIEWED_EXAMPLE_TARGETS'].map(n=>[n,extractConst(base,n).value]);
assert.equal(v.length,3914);assert.equal(Object.keys(g).length,130);assert.equal(Object.keys(d.value).length,3914);assert.equal(pairs.length,859);
const fixed=[3119,3127,3131,3164,3168,3169,3176,3234,3269],reviewed=[3208,3266,3272],scope=[3119,3127,3131,3164,3168,3169,3176,3208,3234,3266,3269,3272];
const before=JSON.parse(JSON.stringify(d.value)),fieldChanges=[];
function set(id,field,oldValue,newValue){assert.equal(d.value[String(id)][field],oldValue,'unexpected old value '+id+'.'+field);d.value[String(id)][field]=newValue;fieldChanges.push({id,field,oldValue,newValue});}
function setArray(id,field,index,oldValue,newValue){assert.equal(d.value[String(id)][field][index],oldValue,'unexpected old array value '+id+'.'+field+'['+index+']');d.value[String(id)][field][index]=newValue;fieldChanges.push({id,field:field+'['+index+']',oldValue,newValue});}
set(3119,'m','運がよく、都合がよい様子。','その人にとって望ましく、ありがたいこと。また、運がよく、都合がよいさま。');
set(3119,'t','щасливий, вдалий','щастя; сприятливий, вдалий; на щастя');
set(3119,'usage','な-прикметник та іменник: 幸いなことに／幸いだった. Сприятливий збіг обставин, «на щастя». 不幸中の幸い — усталене іменникове сполучення, його не варто механічно змішувати з 幸いなことに.','Іменник і な-прикметник; також прислівник: 幸いなことに／幸いだった／幸い、命だけは助かった. Сприятливий збіг обставин або щасливий результат; у прислівниковому вживанні — «на щастя». 不幸中の幸い — усталене іменникове сполучення.');
set(3127,'t','жахливий, прикрий, катастрофічний','вкрай поганий, жахливий; дуже, украй (прислівникове)');
setArray(3131,'exampleTranslations',1,'За млявої переговорної позиції не вдасться домогтися вигідних умов.','За надто нерішучої позиції на переговорах не вдасться домогтися вигідних умов.');
set(3164,'m','数量や程度がかなり大きい様子。また、つり合ってふさわしい様子。','価値や働きなどが、他のものとほぼ等しいこと。また、程度がかなり大きいさま。');
set(3164,'t','чималий, значний, відповідний','еквівалентний, відповідний; чималий, значний');
set(3168,'t','недбалий, лінивий, нерадивий','недбалість; недбалий, нерадивий');
setArray(3168,'exampleTranslations',1,'Начальник неодноразово вимагав від недбалого працівника виправити ставлення до роботи.','Керівник неодноразово вказував працівникові з недбалим ставленням до роботи на потребу виправитися.');
set(3169,'t','нудний, одноманітний, безбарвний','нудьга; нудний, нецікавий');
set(3176,'m','字を上手に書く様子。','文字や文章を巧みに書くこと。また、そのさまや書かれたもの。');
set(3176,'t','каліграфічний, красивий (про почерк)','майстерний почерк; вправне письмо');
set(3176,'usage','な-прикметник та іменник: 達筆な人／達筆だ. Майстерно пише від руки; не просто створює добрий літературний текст. 能筆 — близьке іменникове позначення.','Іменник і な-прикметник: 達筆な人／達筆だ. Майстерне письмо; може стосуватися і вправного почерку, і майстерного написання тексту. У цих прикладах ідеться саме про почерк. 能筆 — близьке іменникове позначення.');
set(3234,'t','клопітний, обтяжливий, важкий','клопіт; клопітний, обтяжливий; бути на чиємусь утриманні (お厄介になる)');
set(3269,'m','典型的な特徴がよく表れている様子、または強い同意を示す副詞。','程度や状態の強さを示す。また、典型的な特徴がよく表れていることや、相手の考えを強く肯定することを表す。');
set(3269,'t','справді; саме так; аж надто характерно (сильне враження або згода)','справді; цілком; саме так; цілком типовий (про характерну рису)');
assert.equal(fieldChanges.length,16);
const changed=Object.keys(d.value).filter(id=>JSON.stringify(d.value[id])!==JSON.stringify(before[id])).map(Number).sort((a,b)=>a-b);
assert.deepEqual(changed,fixed);
for(const id of scope){const row=v.find(x=>Number(x.id)===id);assert.ok(row,'missing id '+id);assert.ok(d.value[String(id)].w);assert.equal(d.value[String(id)].examples.length,2);assert.equal(d.value[String(id)].exampleTranslations.length,2);assert.ok(p[String(id)]);}
let candidate=base.slice(0,d.start)+JSON.stringify(d.value)+base.slice(d.end);
const oldTitle='<title>JLPT N1 — ウクライナ語対応学習アプリ · v217</title>',newTitle='<title>JLPT N1 — ウクライナ語対応学習アプリ · v218</title>';
assert.equal(candidate.split(oldTitle).length,2);candidate=candidate.replace(oldTitle,newTitle);
let rollback=candidate.replace(newTitle,oldTitle);const rd=extractConst(rollback,'VOCAB_DETAILS_BY_ID');rollback=rollback.slice(0,rd.start)+d.literal+rollback.slice(rd.end);assert.equal(rollback,base,'exact rollback failed');
for(const [name,original] of stable)assert.deepEqual(extractConst(candidate,name).value,original,name+' changed');
assert.deepEqual(extractConst(candidate,'DEFAULT_VOCAB').value,v);
assert.deepEqual(extractConst(candidate,'VOCAB_POS_BY_ID').value,p);
assert.deepEqual(extractConst(candidate,'GRAMMAR_DETAILS_BY_ID').value,g);
assert.deepEqual(extractConst(candidate,'VOCAB_AUDITED_PAIRS').value,pairs);
fs.writeFileSync(outPath,candidate);
const registerPath='completion/review-register.csv',register=parseCSV(fs.readFileSync(registerPath,'utf8'));
assert.equal(register.length,5848,'unexpected registry row count');
const header=register[0],col=k=>header.indexOf(k),fixedSet=new Set(fixed),reviewedSet=new Set(reviewed),seen=new Set();
const evidence='JLPT_N1_v218_audit.md; completion/v218-acceptance.tsv; completion/v218-c10-review.tsv; author review, not independent; provenance/physical excluded';
for(const row of register.slice(1)){if(row[col('kind')]==='vocab'&&(fixedSet.has(Number(row[col('key')]))||reviewedSet.has(Number(row[col('key')])))){const id=Number(row[col('key')]);assert.equal(row[col('finalReview')],'pending','record not pending: '+id);assert.ok(!seen.has(id),'duplicate registry key '+id);seen.add(id);row[col('finalReview')]=fixedSet.has(id)?'fixed_rechecked':'reviewed';row[col('evidence')]=evidence;}}
assert.equal(seen.size,12,'not all scoped rows updated');
fs.writeFileSync(registerPath,register.map(row=>row.map(csvCell).join(',')).join('\n')+'\n');
function counts(kind){const out={reviewed:0,fixed_rechecked:0,pending:0,total:0};for(const row of register.slice(1)){if(kind&&row[col('kind')]!==kind)continue;if(Object.prototype.hasOwnProperty.call(out,row[col('finalReview')]))out[row[col('finalReview')]]++;out.total++;}return out;}
const after={all:counts(null),vocabulary:counts('vocab'),vocab_pair:counts('vocab_pair')};
assert.deepEqual(after,{all:{reviewed:3935,fixed_rechecked:433,pending:1479,total:5847},vocabulary:{reviewed:3364,fixed_rechecked:431,pending:119,total:3914},vocab_pair:{reviewed:20,fixed_rechecked:1,pending:838,total:859}});
const bytes=Buffer.byteLength(candidate),sha=crypto.createHash('sha256').update(candidate).digest('hex'),blob=crypto.createHash('sha1').update(Buffer.from('blob '+bytes+'\0')).update(Buffer.from(candidate)).digest('hex');
const prepare={pass:true,base_version:'v217',base_main_sha:'f8a54df76e6187f3f87b4f4f9977c0612235228c',base_sha256:baseSha,candidate_version:'v218',candidate_sha256:sha,candidate_blob_sha:blob,candidate_bytes:bytes,vocabulary_records:3914,grammar_records:130,lexical_pairs:859,unique_vocabulary_ids:3914,review_scope:scope,fixed_rechecked:fixed,reviewed_ids:reviewed,updated_fields:16,changed_cards:fixed,pos_map_unchanged:true,examples_unchanged:true,comparison_pairs_unchanged:true,author_credit_before:3783,author_credit_addition:12,author_credit_after:3795,pilot_covered_ids:[],pilot_missing_ids:scope,exact_rollback:true,register_after:after,author_review_only:true};
const registry={pass:true,register_rows:register.length-1,after,scope_updated:[...scope],duplicate_scope_keys:0,records_deleted:0,history_rewritten:false};
fs.mkdirSync(work,{recursive:true});fs.writeFileSync(path.join(work,'prepare-results.json'),JSON.stringify(prepare,null,2)+'\n');fs.writeFileSync(path.join(work,'registry-results.json'),JSON.stringify(registry,null,2)+'\n');
const cpPath=path.join(work,'checkpoint.json'),cp=JSON.parse(fs.readFileSync(cpPath,'utf8'));Object.assign(cp,{status:'candidate and registry prepared; syntax and Chromium verification pending',candidate_sha256:sha,candidate_blob_sha:blob,candidate_bytes:bytes,exact_rollback:true});fs.writeFileSync(cpPath,JSON.stringify(cp,null,2)+'\n');
const auditPath='JLPT_N1_v218_audit.md';let audit=fs.readFileSync(auditPath,'utf8');audit=audit.replace('__V218_SHA256__',sha).replace('__V218_BYTES__',String(bytes)).replace('__V218_BLOB__',blob);fs.writeFileSync(auditPath,audit);
console.log(JSON.stringify({pass:true,sha,blob,bytes,changed_cards:changed,field_changes:fieldChanges.length,registry:after},null,2));
