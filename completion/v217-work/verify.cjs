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
const basePath='JLPT_N1_ukrainian_reading_v216.html',outPath='JLPT_N1_ukrainian_reading_v217.html',work='completion/v217-work';
const base=fs.readFileSync(basePath,'utf8'),baseSha=crypto.createHash('sha256').update(base).digest('hex');assert.equal(baseSha,'9166c9c55fac5478dda8768da705986ce9ba42d7f8fb43ae259848d17df156ec');
const d=extractConst(base,'VOCAB_DETAILS_BY_ID'),v=extractConst(base,'DEFAULT_VOCAB').value,p=extractConst(base,'VOCAB_POS_BY_ID').value,g=extractConst(base,'GRAMMAR_DETAILS_BY_ID').value,pairs=extractConst(base,'VOCAB_AUDITED_PAIRS').value,meaning=extractConst(base,'REVIEWED_MEANING_QUIZZES').value,reading=extractConst(base,'REVIEWED_READING_OPTIONS').value,kana=extractConst(base,'VOCAB_KANA_EXAMPLE_TARGETS').value,targets=extractConst(base,'REVIEWED_EXAMPLE_TARGETS').value;
assert.equal(v.length,3914);assert.equal(Object.keys(g).length,130);assert.equal(Object.keys(d.value).length,3914);assert.equal(pairs.length,859);
const fixed=[1816,3020,3041,3052,3059],reviewed=[1740,1796,1823,1824,2142,3029,3034],scope=[1740,1796,1816,1823,1824,2142,3020,3029,3034,3041,3052,3059];
const expected={
"1740":["通常","つうじょう",["名詞"]],"1796":["同等","どうとう",["名詞"]],"1816":["内緒","ないしょ",["名詞"]],
"1823":["日夜","にちや",["名詞"]],"1824":["任意","にんい",["名詞"]],"2142":["洋風","ようふう",["名詞"]],
"3020":["望ましい","のぞましい",["イ形"]],"3029":["欲深い","よくぶかい",["イ形"]],"3034":["ぶかぶか","ぶかぶか",["ナ形"]],
"3041":["画一的","かくいつてき",["ナ形"]],"3052":["わんぱく","わんぱく",["ナ形"]],"3059":["一途","いちず",["ナ形"]]};
const baseExamples={
"1740":["通常、申請から許可が下りるまでには、約一か月を要する。","通常の営業時間を変更して、夜間も対応することにした。"],
"1796":["この製品は、従来品と同等の品質を備えている。","この資格は、大学卒業と同等の学力を認めるものだ。"],
"1816":["この計画は、正式発表まで内緒にしておいてほしい。","彼が内緒で副業を始めていたことが発覚した。"],
"1823":["技術者たちは、日夜開発に励んで新製品を完成させた。","被災地では、日夜を問わず復旧作業が続けられている。"],
"1824":["この調査への参加はあくまで任意であり、強制ではない。","任意の数を代入して、式が成り立つか確かめなさい。"],
"2142":["和風の庭園の一角に、洋風の建築が調和して建てられている。","会合のために、洋風のドレッシングを使ったサラダを作った。"],
"3020":["経営の透明性を高めることが、株主に対する望ましい対応だ。","事故の再発防止には、現場の意見を反映した対策が望ましい。"],
"3029":["欲深い経営は短期的な利益を生んでも、長期的な信用を損なう。","欲深い業者に付け込まれ、高額な契約を結ばされる被害が相次ぐ。"],
"3034":["新入社員はぶかぶかなスーツを着て、緊張した面持ちで挨拶した。","ぶかぶかな靴で長時間歩いたため、彼は靴ずれした。"],
"3041":["画一的な教育では、子どもの多様な才能を伸ばすことが難しい。","画一的な対応を改め、顧客ごとの事情に合わせた提案を行う。"],
"3052":["わんぱくな子どもたちが、自然の中で思い切り体を動かしている。","わんぱくな少年時代を過ごした彼は、後に冒険家として名を成した。"],
"3059":["一途な思いで研究に打ち込み、彼はついに新発見をなし遂げた。","一途な情熱が周囲の人々の心を動かし、協力の輪が広がった。"]};
const updates=[
["1816","usage","Іменник і な-вживання: 内緒にする、人に内緒で. Приховувати від певної людини; розмовніше за 内密. 秘密 ширше означає приховану інформацію або таємницю.","Іменник: 内緒にする、人に内緒で. Розмовне слово для того, що приховують від інших; менш офіційне за 内密. 秘密 ширше й нейтральніше позначає приховану інформацію."],
["3020","exampleTranslations[1]","Щоб запобігти повторенню аварій, бажано врахувати думки працівників на місцях.","Для запобігання повторним аваріям бажано вжити заходів, що враховують думки працівників на місцях."],
["3041","exampleTranslations[0]","Освіті за одним шаблоном важко розвивати різноманітні дитячі здібності.","Коли освіта побудована за єдиним шаблоном, важко розвивати різноманітні здібності дітей."],
["3052","m","子どもが元気がよすぎて、いたずらをする様子。","子どもが元気に遊び回り、いたずらをする様子。"],
["3059","usage","な-прикметник: 一途な思い／一途に打ち込む. Уся відданість спрямована на одне; не обов’язково патологічна одержимість. Іменникове 一途をたどる — інше вживання.","Іменник і な-прикметник: 一途な思い／一途に打ち込む. Уся відданість спрямована на одне; не обов’язково патологічна одержимість. Окреме читання いっと має значення «один напрям, тенденція»: 増加の一途をたどる — «неухильно зростати»."]
];
for(const [id,e] of Object.entries(expected)){const row=v.find(x=>String(x.id)===id);assert.ok(row);assert.equal(row.w,e[0]);assert.equal(row.r,e[1]);assert.deepEqual(p[id],e[2]);assert.deepEqual(d.value[id].examples,baseExamples[id]);}
const before=JSON.parse(JSON.stringify(d.value));
for(const [id,field,oldVal,newVal] of updates){const bracket=field.indexOf('[');if(bracket>=0){const key=field.slice(0,bracket),index=Number(field.slice(bracket+1,-1));assert.equal(d.value[id][key][index],oldVal);d.value[id][key][index]=newVal;}else{assert.equal(d.value[id][field],oldVal);d.value[id][field]=newVal;}}
const changed=Object.keys(d.value).filter(id=>JSON.stringify(d.value[id])!==JSON.stringify(before[id])).map(Number).sort((a,b)=>a-b);assert.deepEqual(changed,fixed);
let candidate=base.slice(0,d.start)+JSON.stringify(d.value)+base.slice(d.end);
const oldTitle='<title>JLPT N1 — ウクライナ語対応学習アプリ · v216</title>',newTitle='<title>JLPT N1 — ウクライナ語対応学習アプリ · v217</title>';assert.equal(candidate.split(oldTitle).length,2);candidate=candidate.replace(oldTitle,newTitle);
let rollback=candidate.replace(newTitle,oldTitle);const rd=extractConst(rollback,'VOCAB_DETAILS_BY_ID');rollback=rollback.slice(0,rd.start)+d.literal+rollback.slice(rd.end);assert.equal(rollback,base);
for(const [name,original] of Object.entries({DEFAULT_VOCAB:v,VOCAB_POS_BY_ID:p,GRAMMAR_DETAILS_BY_ID:g,VOCAB_AUDITED_PAIRS:pairs,REVIEWED_MEANING_QUIZZES:meaning,REVIEWED_READING_OPTIONS:reading,VOCAB_KANA_EXAMPLE_TARGETS:kana,REVIEWED_EXAMPLE_TARGETS:targets}))assert.deepEqual(extractConst(candidate,name).value,original);
fs.writeFileSync(outPath,candidate);
const registerPath='completion/review-register.csv',register=parseCSV(fs.readFileSync(registerPath,'utf8')),evidence='completion/v217-acceptance.tsv; JLPT_N1_v217_audit.md; author review, not independent',statusMap=new Map([...fixed.map(x=>[x,'fixed_rechecked']),...reviewed.map(x=>[x,'reviewed'])]),seen=new Set();
assert.equal(register.length,5848);
for(const row of register.slice(1)){if(row[0]!=='vocab'||!statusMap.has(Number(row[1])))continue;const id=Number(row[1]);assert.equal(row[3],'pending');assert.ok(!seen.has(id));seen.add(id);row[3]=statusMap.get(id);row[4]=evidence;}
assert.equal(seen.size,scope.length);
fs.writeFileSync(registerPath,register.map(row=>row.map(csvCell).join(',')).join('\n')+'\n');
function counts(kind=null){const out={reviewed:0,fixed_rechecked:0,pending:0,total:0};for(const r of register.slice(1)){if(kind&&r[0]!==kind)continue;if(r[3] in out)out[r[3]]++;out.total++;}return out;}
const after={all:counts(),vocabulary:counts('vocab'),vocab_pair:counts('vocab_pair')};
assert.deepEqual(after,{all:{reviewed:3932,fixed_rechecked:424,pending:1491,total:5847},vocabulary:{reviewed:3361,fixed_rechecked:422,pending:131,total:3914},vocab_pair:{reviewed:20,fixed_rechecked:1,pending:838,total:859}});
const bytes=Buffer.byteLength(candidate),sha=crypto.createHash('sha256').update(candidate).digest('hex'),blob=crypto.createHash('sha1').update(Buffer.from('blob '+bytes+'\0')).update(Buffer.from(candidate)).digest('hex');
const prepare={pass:true,base_version:'v216',base_sha256:baseSha,candidate_version:'v217',candidate_sha256:sha,candidate_blob_sha:blob,candidate_bytes:bytes,vocabulary_records:3914,grammar_records:130,lexical_pairs:859,unique_vocabulary_ids:3914,review_scope:scope,fixed_rechecked:fixed,reviewed_ids:reviewed,updated_fields:updates.length,changed_cards:fixed,japanese_definition_changes:[3052],pos_map_unchanged:true,comparison_pairs_unchanged:true,author_credit_before:3771,author_credit_addition:12,author_credit_after:3783,pilot_covered_ids:[],pilot_missing_ids:scope,exact_rollback:true,register_after:after,author_review_only:true};
const registry={pass:true,register_rows:register.length-1,after,reviewed_pair_keys:[],duplicate_keys:0,records_deleted:0,history_rewritten:false};
fs.mkdirSync(work,{recursive:true});fs.writeFileSync(path.join(work,'prepare-results.json'),JSON.stringify(prepare,null,2)+'\n');fs.writeFileSync(path.join(work,'registry-results.json'),JSON.stringify(registry,null,2)+'\n');
const cpPath=path.join(work,'checkpoint.json'),cp=JSON.parse(fs.readFileSync(cpPath,'utf8'));Object.assign(cp,{status:'candidate and registry prepared; Chromium verification pending',candidate_sha256:sha,candidate_blob_sha:blob,candidate_bytes:bytes,exact_rollback:true});fs.writeFileSync(cpPath,JSON.stringify(cp,null,2)+'\n');
const auditPath='JLPT_N1_v217_audit.md';let audit=fs.readFileSync(auditPath,'utf8');audit=audit.replace('__V217_SHA256__',sha).replace('__V217_BYTES__',String(bytes)).replace('__V217_BLOB__',blob);fs.writeFileSync(auditPath,audit);
console.log(JSON.stringify({pass:true,sha,blob,bytes,changed,after},null,2));
