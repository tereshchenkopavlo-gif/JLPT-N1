const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
const {pathToFileURL}=require('node:url'),HTML='JLPT_N1_ukrainian_reading_v216.html',WORK='completion/v216-work';
const prepare=JSON.parse(fs.readFileSync(path.join(WORK,'prepare-results.json'),'utf8'));
const IDS=[1475,1755,1776,1795,1833,1985,2058,2116,2214,2222,3005,3006,3010,3017,3023];
const EXPECTED={
"1475":{word:"承認",reading:"しょうにん",pos:["名詞"],definition:"計画や提案などを正式に認めて受け入れること。"},
"1755":{word:"適性",reading:"てきせい",pos:["名詞"]},"1776":{word:"土台",reading:"どだい",pos:["名詞"]},
"1795":{word:"同調",reading:"どうちょう",pos:["名詞"],translations:["Слід не лише підлаштовуватися під оточення, а й чітко висловлювати власну думку."]},
"1833":{word:"燃焼",reading:"ねんしょう",pos:["名詞"]},"1985":{word:"返済",reading:"へんさい",pos:["名詞"],gloss:"повернення позиченого; погашення боргу чи позики"},
"2058":{word:"無実",reading:"むじつ",pos:["名詞"],translations:["Після повторного судового розгляду звільнили чоловіка, який відбував покарання за злочин, якого не скоював."]},
"2116":{word:"有数",reading:"ゆうすう",pos:["名詞"]},
"2214":{word:"ありのまま",reading:"ありのまま",pos:["名詞"],translations:["Оприлюднити результати дослідження такими, як вони є, — це і є чесний підхід."]},
"2222":{word:"つぼみ",reading:"つぼみ",pos:["名詞"],gloss:"молода надія",usage:"переносно — про людину чи задум із потенціалом розвитку"},
"3005":{word:"著しい",reading:"いちじるしい",pos:["イ形"]},
"3006":{word:"途方もない",reading:"とほうもない",pos:["イ形"],translations:["З’ясувалося, що сума збитків була колосальною, і керівництво притягують до відповідальності."]},
"3010":{word:"濃い",reading:"こい",pos:["イ形"]},
"3017":{word:"分厚い",reading:"ぶあつい",pos:["イ形"],translations:["Наявність численного й вагомого середнього класу слугувала основою суспільної стабільності."]},
"3023":{word:"名高い",reading:"なだかい",pos:["イ形"]}
};
(async()=>{const bytes=fs.readFileSync(HTML),sha=crypto.createHash('sha256').update(bytes).digest('hex');assert.equal(sha,prepare.candidate_sha256);assert.equal(bytes.length,prepare.candidate_bytes);
const browser=await chromium.launch({headless:true});try{
const page=await browser.newPage({viewport:{width:412,height:900}}),errors=[];page.on('pageerror',e=>errors.push(String(e)));await page.goto(pathToFileURL(path.resolve(HTML)).href);
const structural=await page.evaluate(()=>({vocab:DEFAULT_VOCAB.length,grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,pairs:VOCAB_AUDITED_PAIRS.length,uniqueIds:new Set(DEFAULT_VOCAB.map(x=>Number(x.id))).size,allIdsPresent:DEFAULT_VOCAB.every(x=>VOCAB_DETAILS_BY_ID[String(x.id)]&&VOCAB_POS_BY_ID[String(x.id)])}));
assert.deepEqual(structural,{vocab:3914,grammar:130,pairs:859,uniqueIds:3914,allIdsPresent:true});
const data=await page.evaluate(ids=>ids.map(id=>{const v=DEFAULT_VOCAB.find(x=>Number(x.id)===id),d=VOCAB_DETAILS_BY_ID[String(id)];return{id,word:d.w,reading:v.r,pos:VOCAB_POS_BY_ID[String(id)],gloss:d.t,definition:d.m,translations:d.exampleTranslations,examples:d.examples,usage:d.usage};}),IDS);
for(const c of data){const e=EXPECTED[String(c.id)];assert.equal(c.word,e.word);assert.equal(c.reading,e.reading);assert.deepEqual(c.pos,e.pos);assert.ok(c.usage&&c.usage.length>0);if(e.definition)assert.ok(c.definition.includes(e.definition));if(e.gloss)assert.ok(c.gloss.includes(e.gloss));if(e.usage)assert.ok(c.usage.includes(e.usage));if(e.translations)for(const t of e.translations)assert.ok(c.translations.includes(t));}
const norm=x=>String(x).replaceAll('\n',' ').replaceAll('\r',' ').replaceAll('\t',' ').split(' ').filter(Boolean).join(' ');
const rendered=await page.evaluate(async({ids,expected})=>{showView('cards');const out=[];const n=x=>String(x).replaceAll('\n',' ').replaceAll('\r',' ').replaceAll('\t',' ').split(' ').filter(Boolean).join(' ');for(const id of ids){await openCardDetail('v',id);await new Promise(r=>setTimeout(r,35));const body=document.getElementById('cardDetailBody'),txt=body?.innerText||'',d=VOCAB_DETAILS_BY_ID[String(id)],e=expected[String(id)],usageSample=(d.usage||'').slice(0,22);out.push({id,word:d.w,titleVisible:n(txt).includes(n(d.w)),glossVisible:!d.t||n(txt).includes(n(d.t.slice(0,18))),definitionVisible:!e.definition||n(txt).includes(n(e.definition)),usageVisible:!!d.usage&&n(txt).includes('用法・接続'),translationsVisible:d.exampleTranslations.every(x=>!x||n(txt).includes(n(x))),examplesVisible:d.examples.every(x=>!x||n(txt).includes(n(x))),textExcerpt:n(txt).slice(0,400)});}return out;},{ids:IDS,expected:EXPECTED});
fs.writeFileSync(path.join(WORK,'rendered-debug.json'),JSON.stringify(rendered,null,2)+'\n');const failures=rendered.filter(x=>!(x.titleVisible&&x.glossVisible&&x.definitionVisible&&x.usageVisible&&x.translationsVisible&&x.examplesVisible));assert.equal(rendered.length,15);if(failures.length)throw Error(JSON.stringify(failures));
const responsive=[];for(const width of [360,412,1280]){await page.setViewportSize({width,height:900});const d=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth}));responsive.push({...d,overflow:d.scrollWidth>width||d.bodyWidth>width});}assert.ok(responsive.every(x=>!x.overflow));
const storage=await page.evaluate(()=>{const key='choba_n1uk_storage_v1',old=localStorage.getItem(key),sentinel=JSON.stringify({meta:{sessionSize:10,streak:5,lastStudyDate:'2026-11-14'},vp:{'1475':{status:'S',timesShown:2}},gp:{'90':{status:'X'}}});localStorage.setItem(key,sentinel);const roundTrip=localStorage.getItem(key)===sentinel;if(old===null)localStorage.removeItem(key);else localStorage.setItem(key,old);return{roundTrip,restored:localStorage.getItem(key)===old};});assert.ok(storage.roundTrip&&storage.restored);assert.deepEqual(errors,[]);
const result={pass:true,candidate_sha256:sha,candidate_bytes:bytes.length,counts:structural,reviewed_card_count:15,fixed_rechecked_count:8,reviewed_unchanged_count:7,responsive,storage,pageErrors:errors};fs.writeFileSync(path.join(WORK,'browser-results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exit(1);});