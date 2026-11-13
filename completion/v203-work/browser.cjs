const {chromium}=require('playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const HTML='JLPT_N1_ukrainian_reading_v203.html',WORK='completion/v203-work';
const prepare=JSON.parse(fs.readFileSync(path.join(WORK,'prepare-results.json'),'utf8')),registry=JSON.parse(fs.readFileSync(path.join(WORK,'registry-results.json'),'utf8'));
const bytes=fs.readFileSync(HTML),sha=crypto.createHash('sha256').update(bytes).digest('hex');
assert.equal(sha,prepare.candidate_sha256);assert.equal(prepare.pass,true);assert.equal(prepare.exact_rollback,true);assert.equal(registry.pass,true);
const IDS=[1153,1157,1158,1169,1173,1175,1178,1182,1194,1195,1196];
const EXPECTED={
 1153:{word:'欠乏',translations:['Нестача ресурсів суттєво ускладнює життя людей.']},
 1157:{word:'決裂',gloss:'зрив переговорів; розходження сторін без досягнення згоди'},
 1158:{word:'結核',translations:['У місці спільного проживання виявили випадок туберкульозу, після чого орган охорони здоров’я провів обстеження.']},
 1169:{word:'兼業',gloss:'поєднання основної роботи з іншою професійною діяльністю'},
 1173:{word:'建前',translations:['Необхідність залежно від обставин по-різному висловлювати офіційну позицію та справжні почуття ускладнює стосунки в організації.','Згідно з формальними положеннями правил, допустити виняток неможливо.']},
 1175:{word:'検挙',translations:['У матеріалах, оприлюднених поліцією, зазначено кількість справ, у яких поліція ідентифікувала підозрюваних.','Кількість осіб, яких поліція ідентифікувала як підозрюваних, значно зросла порівняно з минулим роком.']},
 1178:{word:'検事',example:'検事は、法廷で被告人の責任を厳しく追及した。',translations:['Після складання японського кваліфікаційного іспиту для юридичних професій він обрав кар’єру прокурора.']},
 1182:{word:'献立',translations:['Вечірнє меню в традиційному готелі переважно складалося з місцевих сезонних продуктів.']},
 1194:{word:'幻想',translations:['Вона й досі береже мрії, які виникли в неї ще в дівоцтві.']},
 1195:{word:'減点',translations:['За неправильно написані або пропущені знаки у відповіді можуть зняти бали.']},
 1196:{word:'源泉',translations:['Часто кажуть, що джерело конкурентоспроможності компанії — її кадри.']}
};
async function main(){
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:412,height:900}}),errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(pathToFileURL(path.resolve(HTML)).href);
  const structural=await page.evaluate(()=>({vocab:DEFAULT_VOCAB.length,grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,pairs:VOCAB_AUDITED_PAIRS.length,uniqueIds:new Set(DEFAULT_VOCAB.map(x=>Number(x.id))).size,allIdsPresent:DEFAULT_VOCAB.every(x=>VOCAB_DETAILS_BY_ID[String(x.id)]&&VOCAB_POS_BY_ID[String(x.id)])}));
  assert.deepEqual(structural,{vocab:3914,grammar:130,pairs:859,uniqueIds:3914,allIdsPresent:true});
  const data=await page.evaluate(ids=>ids.map(id=>{const d=VOCAB_DETAILS_BY_ID[String(id)];return{id,word:d.w,gloss:d.t,translations:d.exampleTranslations,examples:d.examples,pos:VOCAB_POS_BY_ID[String(id)]}}),IDS);
  for(const card of data){const e=EXPECTED[card.id];assert.equal(card.word,e.word);if(e.gloss)assert.ok(card.gloss.includes(e.gloss));if(e.translations)for(const t of e.translations)assert.ok(card.translations.includes(t));if(e.example)assert.equal(card.examples[0],e.example);assert.deepEqual(card.pos,['名詞']);}
  const rendered=await page.evaluate(async ids=>{showView('cards');const out=[];for(const id of ids){await openCardDetail('v',id);const body=document.getElementById('cardDetailBody'),text=body.innerText,norm=x=>String(x).replace(/\s+/g,' ').trim(),d=VOCAB_DETAILS_BY_ID[String(id)];out.push({id,word:d.w,titleVisible:norm(text).includes(norm(d.w)),glossVisible:d.t.split(';').map(x=>x.trim()).filter(Boolean).every(x=>norm(text).includes(norm(x))),translationsVisible:d.exampleTranslations.every(x=>norm(text).includes(norm(x))),examplesVisible:d.examples.every(x=>norm(text).includes(norm(x)))});}return out;},IDS);
  assert.equal(rendered.length,11);assert.equal(rendered.every(x=>x.titleVisible&&x.glossVisible&&x.translationsVisible&&x.examplesVisible),true);
  const responsive=[];for(const width of [360,412,1280]){await page.setViewportSize({width,height:900});const d=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth}));responsive.push({...d,overflow:d.scrollWidth>width||d.bodyWidth>width});}assert.equal(responsive.every(x=>!x.overflow),true);
  const storage=await page.evaluate(()=>{const key='choba_n1uk_storage_v1',old=localStorage.getItem(key),sentinel=JSON.stringify({meta:{sessionSize:10,streak:4,lastStudyDate:'2026-11-13'},vp:{'1153':{status:'S',timesShown:3}},gp:{'90':{status:'X'}}});localStorage.setItem(key,sentinel);const roundTrip=localStorage.getItem(key)===sentinel;if(old===null)localStorage.removeItem(key);else localStorage.setItem(key,old);return{roundTrip,restored:localStorage.getItem(key)===old};});
  assert.equal(storage.roundTrip,true);assert.equal(storage.restored,true);assert.deepEqual(errors,[]);
  const result={pass:true,candidate_sha256:sha,candidate_bytes:bytes.length,counts:structural,reviewed_card_count:11,reviewed_cards:rendered,responsive,storage,pageErrors:errors};
  fs.writeFileSync(path.join(WORK,'browser-results.json'),JSON.stringify(result,null,2)+'\n');process.stdout.write(JSON.stringify(result,null,2)+'\n');
 }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exit(1);});
