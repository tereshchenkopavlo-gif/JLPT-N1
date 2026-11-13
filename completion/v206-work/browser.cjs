const {chromium}=require('playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const HTML='JLPT_N1_ukrainian_reading_v206.html',WORK='completion/v206-work';
const prepare=JSON.parse(fs.readFileSync(path.join(WORK,'prepare-results.json'),'utf8')),registry=JSON.parse(fs.readFileSync(path.join(WORK,'registry-results.json'),'utf8'));
const bytes=fs.readFileSync(HTML),sha=crypto.createHash('sha256').update(bytes).digest('hex');
assert.equal(sha,prepare.candidate_sha256);assert.equal(prepare.pass,true);assert.equal(prepare.exact_rollback,true);assert.equal(registry.pass,true);
const IDS=[1322,1323,1327,1329,1331,1333,1334,1335,1339,1340,1341,1344];
const EXPECTED={
 1322:{word:'司法',gloss:'судова влада'},
 1323:{word:'始末',translations:['Договір зобов’язує відповідально прибирати або утилізувати обладнання після використання.']},
 1327:{word:'志向',translations:['Останніми роками серед молоді помітна сильна орієнтація на самореалізацію, а не на стабільність.']},
 1329:{word:'思惑',gloss:'очікування, сподівання'},
 1331:{word:'指図',gloss:'指図する — вказувати'},
 1333:{word:'指標',translations:['До показників життєздатності підприємства належать не лише фінансові параметри, а й урахування впливу на довкілля.']},
 1334:{word:'指紋',gloss:'папілярний візерунок',japanese:'皮膚隆線'},
 1335:{word:'指令',translations:['Штаб наказав підрозділу на місці негайно залишити цей район.']},
 1339:{word:'施行',gloss:'набрання чинності',usage:'Не плутати з 施工（せこう）'},
 1340:{word:'施設',gloss:'об’єкт або заклад'},
 1341:{word:'死傷',translations:['В аварії загинули або зазнали поранень близько півтора десятка пасажирів і членів екіпажу.']},
 1344:{word:'視覚',translations:['Експонати цієї виставки можна досліджувати на дотик, тож насолодитися нею зможуть і люди з порушеннями зору.']}
};
async function main(){
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:412,height:900}}),errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(pathToFileURL(path.resolve(HTML)).href);
  const structural=await page.evaluate(()=>({vocab:DEFAULT_VOCAB.length,grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,pairs:VOCAB_AUDITED_PAIRS.length,uniqueIds:new Set(DEFAULT_VOCAB.map(x=>Number(x.id))).size,allIdsPresent:DEFAULT_VOCAB.every(x=>VOCAB_DETAILS_BY_ID[String(x.id)]&&VOCAB_POS_BY_ID[String(x.id)])}));
  assert.deepEqual(structural,{vocab:3914,grammar:130,pairs:859,uniqueIds:3914,allIdsPresent:true});
  const data=await page.evaluate(ids=>ids.map(id=>{const d=VOCAB_DETAILS_BY_ID[String(id)];return{id,word:d.w,gloss:d.t,usage:d.usage,definition:d.m,translations:d.exampleTranslations,examples:d.examples,pos:VOCAB_POS_BY_ID[String(id)]}}),IDS);
  for(const card of data){const e=EXPECTED[card.id];assert.equal(card.word,e.word);if(e.gloss)assert.ok((card.gloss+' '+card.usage).includes(e.gloss));if(e.usage)assert.ok(card.usage.includes(e.usage));if(e.japanese)assert.ok(card.definition.includes(e.japanese));if(e.translations)for(const t of e.translations)assert.ok(card.translations.includes(t));assert.deepEqual(card.pos,['名詞']);}
  const rendered=await page.evaluate(async ids=>{showView('cards');const out=[];for(const id of ids){await openCardDetail('v',id);const body=document.getElementById('cardDetailBody'),text=body.innerText,norm=x=>String(x).replace(/\s+/g,' ').trim(),d=VOCAB_DETAILS_BY_ID[String(id)];out.push({id,word:d.w,titleVisible:norm(text).includes(norm(d.w)),glossVisible:norm(text).includes(norm(d.t)),usageVisible:norm(text).includes(norm(d.usage)),translationsVisible:d.exampleTranslations.every(x=>norm(text).includes(norm(x))),examplesVisible:d.examples.every(x=>norm(text).includes(norm(x)))});}return out;},IDS);
  assert.equal(rendered.length,12);assert.equal(rendered.every(x=>x.titleVisible&&x.glossVisible&&x.usageVisible&&x.translationsVisible&&x.examplesVisible),true);
  const responsive=[];for(const width of [360,412,1280]){await page.setViewportSize({width,height:900});const d=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth}));responsive.push({...d,overflow:d.scrollWidth>width||d.bodyWidth>width});}assert.equal(responsive.every(x=>!x.overflow),true);
  const storage=await page.evaluate(()=>{const key='choba_n1uk_storage_v1',old=localStorage.getItem(key),sentinel=JSON.stringify({meta:{sessionSize:10,streak:4,lastStudyDate:'2026-11-13'},vp:{'1322':{status:'S',timesShown:3}},gp:{'90':{status:'X'}}});localStorage.setItem(key,sentinel);const roundTrip=localStorage.getItem(key)===sentinel;if(old===null)localStorage.removeItem(key);else localStorage.setItem(key,old);return{roundTrip,restored:localStorage.getItem(key)===old};});
  assert.equal(storage.roundTrip,true);assert.equal(storage.restored,true);assert.deepEqual(errors,[]);
  const result={pass:true,candidate_sha256:sha,candidate_bytes:bytes.length,counts:structural,reviewed_card_count:12,reviewed_cards:rendered,responsive,storage,pageErrors:errors};
  fs.writeFileSync(path.join(WORK,'browser-results.json'),JSON.stringify(result,null,2)+'\n');process.stdout.write(JSON.stringify(result,null,2)+'\n');
 }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exit(1);});
