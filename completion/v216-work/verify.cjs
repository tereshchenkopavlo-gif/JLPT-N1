const fs=require('node:fs'),crypto=require('node:crypto'),assert=require('node:assert/strict'),path=require('node:path');
function extractConst(source,name){
 const marker='const '+name+' =',at=source.indexOf(marker);assert.ok(at>=0,'missing '+name);
 let start=at+marker.length;while(/\s/.test(source[start]))start++;
 const open=source[start],close=open==='['?']':'}';let depth=0,inString=false,escaped=false;
 for(let i=start;i<source.length;i++){const c=source[i];
  if(inString){if(escaped)escaped=false;else if(c==='\\')escaped=true;else if(c==='"')inString=false;}
  else{if(c==='"')inString=true;else if(c===open)depth++;else if(c===close){depth--;if(depth===0)return{start,end:i+1,value:JSON.parse(source.slice(start,i+1)),literal:source.slice(start,i+1)};}}
 }
 throw new Error('unterminated '+name);
}
const basePath='JLPT_N1_ukrainian_reading_v215.html',outPath='JLPT_N1_ukrainian_reading_v216.html',work='completion/v216-work';
const base=fs.readFileSync(basePath,'utf8'),baseSha=crypto.createHash('sha256').update(base).digest('hex');
assert.equal(baseSha,'f537227849b1dd5ac31577b641e05db4d3ab5af05007cd3721aabe31df015de1');
const d=extractConst(base,'VOCAB_DETAILS_BY_ID'),v=extractConst(base,'DEFAULT_VOCAB').value,p=extractConst(base,'VOCAB_POS_BY_ID').value,g=extractConst(base,'GRAMMAR_DETAILS_BY_ID').value,pairs=extractConst(base,'VOCAB_AUDITED_PAIRS').value;
const meaning=extractConst(base,'REVIEWED_MEANING_QUIZZES').value,reading=extractConst(base,'REVIEWED_READING_OPTIONS').value,kana=extractConst(base,'VOCAB_KANA_EXAMPLE_TARGETS').value,targets=extractConst(base,'REVIEWED_EXAMPLE_TARGETS').value;
assert.equal(v.length,3914);assert.equal(Object.keys(g).length,130);assert.equal(Object.keys(d.value).length,3914);assert.equal(pairs.length,859);
const fixed=[1475,1795,1985,2058,2214,2222,3006,3017],reviewed=[1755,1776,1833,2116,3005,3010,3023],scope=[1475,1755,1776,1795,1833,1985,2058,2116,2214,2222,3005,3006,3010,3017,3023];
const expected={
"1475":["承認","しょうにん",["名詞"]],"1755":["適性","てきせい",["名詞"]],"1776":["土台","どだい",["名詞"]],
"1795":["同調","どうちょう",["名詞"]],"1833":["燃焼","ねんしょう",["名詞"]],"1985":["返済","へんさい",["名詞"]],
"2058":["無実","むじつ",["名詞"]],"2116":["有数","ゆうすう",["名詞"]],"2214":["ありのまま","ありのまま",["名詞"]],
"2222":["つぼみ","つぼみ",["名詞"]],"3005":["著しい","いちじるしい",["イ形"]],"3006":["途方もない","とほうもない",["イ形"]],
"3010":["濃い","こい",["イ形"]],"3017":["分厚い","ぶあつい",["イ形"]],"3023":["名高い","なだかい",["イ形"]]};
const baseExamples={
"1475":["新しい事業計画は、取締役会で全会一致で承認された。","国は、この新薬の製造販売を正式に承認した。"],
"1755":["採用にあたっては、個人の適性を丁寧に見極める必要がある。","適性検査の結果を踏まえて、部署の配置が決定された。"],
"1776":["建物の土台が不安定だと、地震の際に大きな被害を招く。","信頼関係こそが、長期的な取引を支える土台となる。"],
"1795":["周囲に同調するばかりでなく、自分の意見をはっきり述べるべきだ。","新たな提案に同調する議員が、与党内にも少なくなかった。"],
"1833":["エンジン内で燃料が完全に燃焼するよう、設計が改良された。","完全燃焼した試合の後、選手たちは言葉を失った。"],
"1985":["住宅ローンの返済が、家計を圧迫している。","奨学金の返済を終えるまでに、十年以上かかった。"],
"2058":["被告人は一貫して、自分は無実であると主張し続けている。","再審により、無実の罪で服役していた男性が釈放された。"],
"2116":["この地域は、全国でも有数のワインの産地として知られる。","世界有数の技術力を誇る同社は、海外でも高い評価を得ている。"],
"2214":["調査の結果は、ありのまま公表するのが誠実な態度というものだ。","彼女は自分の失敗をありのままに語り、聴衆の共感を得た。"],
"2222":["寒さが続いたため、桜のつぼみはまだ固く閉じたままである。","夕方になって、バラのつぼみがようやく開いた。"],
"3005":["新興国の著しい経済成長が、世界の貿易構造を変えつつある。","品質管理の不備により、会社の信用は著しく低下した。"],
"3006":["途方もない額の赤字が判明し、経営陣は責任を問われている。","途方もない計画だと笑われたが、彼らは粘り強く実現にこぎ着けた。"],
"3010":["濃い霧の影響で、空港では多くの便が欠航した。","このスープは味が濃いので、少しお湯を足した。"],
"3017":["会議には分厚い資料が配られ、出席者は読み込むのに苦労した。","分厚い中間層の存在が、社会の安定を支える土台となってきた。"],
"3023":["この地方は名高い温泉地として、国内外の観光客を集めている。","名高い建築家が設計した美術館が、来月一般に公開される。"]};
const updates=[
["1475","m","物事を正当または事実であると認めること。","物事を正当または事実であると認めること。また、計画や提案などを正式に認めて受け入れること。"],
["1795","exampleTranslations[0]","Слід не лише пристосовуватися до оточення, а й чітко висловлювати власну думку.","Слід не лише підлаштовуватися під оточення, а й чітко висловлювати власну думку."],
["1985","t","повернення позичених коштів за умовами позики","повернення позиченого; погашення боргу чи позики"],
["2058","exampleTranslations[1]","Після повторного судового розгляду звільнили чоловіка, який відбував покарання за невчинений ним злочин.","Після повторного судового розгляду звільнили чоловіка, який відбував покарання за злочин, якого не скоював."],
["2214","exampleTranslations[0]","Чесно — оприлюднити результати такими, як вони є.","Оприлюднити результати дослідження такими, як вони є, — це і є чесний підхід."],
["2222","t","квітковий бутон","квітковий бутон; перен. — молода надія, те, що обіцяє розвиток"],
["2222","usage","Іменник: つぼみが膨らむ／開く. Квітковий бутон. 芽 ширше про бруньку чи пагін; не кожен талант природно називати бутоном.","Іменник: つぼみが膨らむ／開く. Буквально — квітковий бутон; переносно — про людину чи задум із потенціалом розвитку. Українською залежно від контексту: «молода надія», «перспективний задум». 芽 ширше про бруньку чи пагін."],
["3006","exampleTranslations[0]","З’ясувалося, що збиток величезний, і керівництво притягають до відповідальності.","З’ясувалося, що сума збитків була колосальною, і керівництво притягують до відповідальності."],
["3017","exampleTranslations[1]","Численний середній клас був основою суспільної стабільності.","Наявність численного й вагомого середнього класу слугувала основою суспільної стабільності."]];
for(const [id,e] of Object.entries(expected)){const row=v.find(x=>String(x.id)===id);assert.ok(row);assert.equal(row.w,e[0]);assert.equal(row.r,e[1]);assert.deepEqual(p[id],e[2]);assert.deepEqual(d.value[id].examples,baseExamples[id]);}
const before=JSON.parse(JSON.stringify(d.value));
for(const [id,field,oldVal,newVal] of updates){const bracket=field.indexOf('[');if(bracket>=0){const key=field.slice(0,bracket),index=Number(field.slice(bracket+1,-1));assert.equal(d.value[id][key][index],oldVal);d.value[id][key][index]=newVal;}else{assert.equal(d.value[id][field],oldVal);d.value[id][field]=newVal;}}
const changed=Object.keys(d.value).filter(id=>JSON.stringify(d.value[id])!==JSON.stringify(before[id])).map(Number).sort((a,b)=>a-b);assert.deepEqual(changed,fixed);
let candidate=base.slice(0,d.start)+JSON.stringify(d.value)+base.slice(d.end);
const oldTitle='<title>JLPT N1 — ウクライナ語対応学習アプリ · v215</title>',newTitle='<title>JLPT N1 — ウクライナ語対応学習アプリ · v216</title>';assert.equal(candidate.split(oldTitle).length,2);candidate=candidate.replace(oldTitle,newTitle);
let rollback=candidate.replace(newTitle,oldTitle);const rd=extractConst(rollback,'VOCAB_DETAILS_BY_ID');rollback=rollback.slice(0,rd.start)+d.literal+rollback.slice(rd.end);assert.equal(rollback,base);
for(const [name,original] of Object.entries({DEFAULT_VOCAB:v,VOCAB_POS_BY_ID:p,GRAMMAR_DETAILS_BY_ID:g,VOCAB_AUDITED_PAIRS:pairs,REVIEWED_MEANING_QUIZZES:meaning,REVIEWED_READING_OPTIONS:reading,VOCAB_KANA_EXAMPLE_TARGETS:kana,REVIEWED_EXAMPLE_TARGETS:targets}))assert.deepEqual(extractConst(candidate,name).value,original);
fs.writeFileSync(outPath,candidate);
const registerPath='completion/review-register.csv',register=fs.readFileSync(registerPath,'utf8').trimEnd().split('\n'),evidence='completion/v216-acceptance.tsv; JLPT_N1_v216_audit.md',statusMap=new Map([...fixed.map(x=>[x,'fixed_rechecked']),...reviewed.map(x=>[x,'reviewed'])]),seen=new Set();
assert.equal(register.length,5848);
const updated=register.map(line=>{const a=line.split(',');if(a[0]!=='vocab'||!statusMap.has(Number(a[1])))return line;assert.equal(a.length,5);assert.equal(a[3],'pending');assert.equal(a[4],'');const id=Number(a[1]);assert.ok(!seen.has(id));seen.add(id);return [a[0],a[1],a[2],statusMap.get(id),evidence].join(',');});
assert.equal(seen.size,scope.length);fs.writeFileSync(registerPath,updated.join('\n')+'\n');
function counts(kind=null){const out={reviewed:0,fixed_rechecked:0,pending:0,total:0};for(const line of updated.slice(1)){const a=line.split(',');if(kind&&a[0]!==kind)continue;if(a[3] in out)out[a[3]]++;out.total++;}return out;}
const after={all:counts(),vocabulary:counts('vocab'),vocab_pair:counts('vocab_pair')};
assert.deepEqual(after,{all:{reviewed:3925,fixed_rechecked:419,pending:1503,total:5847},vocabulary:{reviewed:3354,fixed_rechecked:417,pending:143,total:3914},vocab_pair:{reviewed:20,fixed_rechecked:1,pending:838,total:859}});
const bytes=Buffer.byteLength(candidate),sha=crypto.createHash('sha256').update(candidate).digest('hex'),blob=crypto.createHash('sha1').update(Buffer.from('blob '+bytes+'\0')).update(Buffer.from(candidate)).digest('hex');
const prepare={pass:true,base_version:'v215',base_sha256:baseSha,candidate_version:'v216',candidate_sha256:sha,candidate_blob_sha:blob,candidate_bytes:bytes,vocabulary_records:3914,grammar_records:130,lexical_pairs:859,unique_vocabulary_ids:3914,review_scope:scope,fixed_rechecked:fixed,reviewed_ids:reviewed,updated_fields:updates.length,changed_cards:fixed,japanese_definition_changes:[1475],pos_map_unchanged:true,comparison_pairs_unchanged:true,author_credit_before:3756,author_credit_addition:15,author_credit_after:3771,pilot_covered_ids:[1475],pilot_missing_ids:scope.filter(x=>x!==1475),exact_rollback:true,register_after:after,author_review_only:true};
const registry={pass:true,register_rows:updated.length-1,after,reviewed_pair_keys:[],duplicate_keys:0,records_deleted:0,history_rewritten:false};
fs.mkdirSync(work,{recursive:true});fs.writeFileSync(path.join(work,'prepare-results.json'),JSON.stringify(prepare,null,2)+'\n');fs.writeFileSync(path.join(work,'registry-results.json'),JSON.stringify(registry,null,2)+'\n');
const cpPath=path.join(work,'checkpoint.json'),cp=JSON.parse(fs.readFileSync(cpPath,'utf8'));Object.assign(cp,{status:'candidate and registry prepared; Chromium verification pending',candidate_sha256:sha,candidate_blob_sha:blob,candidate_bytes:bytes,exact_rollback:true});fs.writeFileSync(cpPath,JSON.stringify(cp,null,2)+'\n');
const auditPath='JLPT_N1_v216_audit.md';let audit=fs.readFileSync(auditPath,'utf8');audit=audit.replace('__V216_SHA256__',sha).replace('__V216_BYTES__',String(bytes)).replace('__V216_BLOB__',blob);fs.writeFileSync(auditPath,audit);
console.log(JSON.stringify({pass:true,sha,blob,bytes,changed,after},null,2));