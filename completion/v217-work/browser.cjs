const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
const {pathToFileURL}=require('node:url'),HTML='JLPT_N1_ukrainian_reading_v217.html',WORK='completion/v217-work';
const prepare=JSON.parse(fs.readFileSync(path.join(WORK,'prepare-results.json'),'utf8'));
const IDS=[1740,1796,1816,1823,1824,2142,3020,3029,3034,3041,3052,3059];
const EXPECTED={
"1740":{word:"通常",reading:"つうじょう",pos:["名詞"]},"1796":{word:"同等",reading:"どうとう",pos:["名詞"]},
"1816":{word:"内緒",reading:"ないしょ",pos:["名詞"],usage:"Розмовне слово для того, що приховують від інших"},
"1823":{word:"日夜",reading:"にちや",pos:["名詞"]},"1824":{word:"任意",reading:"にんい",pos:["名詞"]},
"2142":{word:"洋風",reading:"ようふう",pos:["名詞"]},
"3020":{word:"望ましい",reading:"のぞましい",pos:["イ形"],translations:["Для запобігання повторним аваріям бажано вжити заходів, що враховують думки працівників на місцях."]},
"3029":{word:"欲深い",reading:"よくぶかい",pos:["イ形"]},"3034":{word:"ぶかぶか",reading:"ぶかぶか",pos:["ナ形"]},
"3041":{word:"画一的",reading:"かくいつてき",pos:["ナ形"],translations:["Коли освіта побудована за єдиним шаблоном, важко розвивати різноманітні здібності дітей."]},
"3052":{word:"わんぱく",reading:"わんぱく",pos:["ナ形"],definition:"子どもが元気に遊び回り、いたずらをする様子。"},
"3059":{word:"一途",reading:"いちず",pos:["ナ形"],usage:"Окреме читання いっと має значення"}
};
(async()=>{const bytes=fs.readFileSync(HTML),sha=crypto.createHash('sha256').update(bytes).digest('hex');assert.equal(sha,prepare.candidate_sha256);assert.equal(bytes.length,prepare.candidate_bytes);
const browser=await chromium.launch({headless:true});try{
const page=await browser.newPage({viewport:{width:412,height:900}}),errors=[];page.on('pageerror',e=>errors.push(String(e)));await page.goto(pathToFileURL(path.resolve(HTML)).href);
const structural=await page.evaluate(()=>({vocab:DEFAULT_VOCAB.length,grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,pairs:VOCAB_AUDITED_PAIRS.length,uniqueIds:new Set(DEFAULT_VOCAB.map(x=>Number(x.id))).size,allIdsPresent:DEFAULT_VOCAB.every(x=>VOCAB_DETAILS_BY_ID[String(x.id)]&&VOCAB_POS_BY_ID[String(x.id)])}));
assert.deepEqual(structural,{vocab:3914,grammar:130,pairs:859,uniqueIds:3914,allIdsPresent:true});
const data=await page.evaluate(ids=>ids.map(id=>{const v=DEFAULT_VOCAB.find(x=>Number(x.id)===id),d=VOCAB_DETAILS_BY_ID[String(id)];return{id,word:d.w,reading:v.r,pos:VOCAB_POS_BY_ID[String(id)],gloss:d.t,definition:d.m,translations:d.exampleTranslations,examples:d.examples,usage:d.usage};}),IDS);
for(const c of data){const e=EXPECTED[String(c.id)];assert.equal(c.word,e.word);assert.equal(c.reading,e.reading);assert.deepEqual(c.pos,e.pos);assert.ok(c.usage&&c.usage.length>0);if(e.definition)assert.ok(c.definition.includes(e.definition));if(e.usage)assert.ok(c.usage.includes(e.usage));if(e.translations)for(const t of e.translations)assert.ok(c.translations.includes(t));assert.equal(c.examples.length,2);assert.equal(c.translations.length,2);}
const norm=x=>String(x).replaceAll('\n',' ').replaceAll('\r',' ').replaceAll('\t',' ').split(' ').filter(Boolean).join(' ');
const rendered=await page.evaluate(async({ids,expected})=>{showView('cards');const out=[];const n=x=>String(x).replaceAll('\n',' ').replaceAll('\r',' ').replaceAll('\t',' ').split(' ').filter(Boolean).join(' ');for(const id of ids){await openCardDetail('v',id);await new Promise(r=>setTimeout(r,35));const body=document.getElementById('cardDetailBody'),txt=body?.innerText||'',d=VOCAB_DETAILS_BY_ID[String(id)],e=expected[String(id)];out.push({id,word:d.w,titleVisible:n(txt).includes(n(d.w)),definitionVisible:!e.definition||n(txt).includes(n(e.definition)),usageVisible:!!d.usage&&n(txt).includes('用法・接続'),translationsVisible:d.exampleTranslations.every(x=>!x||n(txt).includes(n(x))),examplesVisible:d.examples.every(x=>!x||n(txt).includes(n(x))),textExcerpt:n(txt).slice(0,360)});}return out;},{ids:IDS,expected:EXPECTED});
fs.writeFileSync(path.join(WORK,'rendered-debug.json'),JSON.stringify(rendered,null,2)+'\n');const failures=rendered.filter(x=>!(x.titleVisible&&x.definitionVisible&&x.usageVisible&&x.translationsVisible&&x.examplesVisible));assert.equal(rendered.length,12);if(failures.length)throw Error(JSON.stringify(failures));
const responsive=[];for(const width of [360,412,1280]){await page.setViewportSize({width,height:900});const d=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth}));responsive.push({...d,overflow:d.scrollWidth>width||d.bodyWidth>width});}assert.ok(responsive.every(x=>!x.overflow));
const storage=await page.evaluate(()=>{const key='choba_n1uk_storage_v1',old=localStorage.getItem(key),sentinel=JSON.stringify({meta:{sessionSize:10,streak:5,lastStudyDate:'2026-11-14'},vp:{'1740':{status:'S',timesShown:2}},gp:{'90':{status:'X'}}});localStorage.setItem(key,sentinel);const roundTrip=localStorage.getItem(key)===sentinel;if(old===null)localStorage.removeItem(key);else localStorage.setItem(key,old);return{roundTrip,restored:localStorage.getItem(key)===old};});assert.ok(storage.roundTrip&&storage.restored);assert.deepEqual(errors,[]);
const result={pass:true,candidate_sha256:sha,candidate_bytes:bytes.length,counts:structural,reviewed_card_count:12,fixed_rechecked_count:5,reviewed_unchanged_count:7,responsive,storage,pageErrors:errors};fs.writeFileSync(path.join(WORK,'browser-results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exit(1);});