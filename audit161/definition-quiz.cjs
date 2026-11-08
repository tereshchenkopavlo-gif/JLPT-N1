const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const file='JLPT_N1_v161_working.html',sha256=require('node:crypto').createHash('sha256').update(fs.readFileSync(file)).digest('hex');
(async()=>{const browser=await chromium.launch({headless:true});const results=[];try{
for(const width of [360,412,1280]){
 const page=await browser.newPage({viewport:{width,height:915}});const errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(pathToFileURL(path.resolve(file)).href);
 const samples=await page.evaluate(()=>{
 const rows=[];for(const id of [2576,2635]){const word=DEFAULT_VOCAB.find(x=>Number(x.id)===id),def=VOCAB_DETAILS_BY_ID[String(id)];for(const example of def.examples){let first;for(let n=0;n<10;n++){const q=quizMeaningOptions({kind:'v',id,word},def,example);if(!q.correct||q.wrong.length!==3||new Set([q.correct,...q.wrong]).size!==4)throw Error('Invalid meaning payload '+id);first??=q;}rows.push({id,example,sample:first});}}return rows;});
 assert.deepEqual(errors,[]);results.push({width,generatedPayloads:40,pass:true,samples});await page.close();
}
fs.writeFileSync('completion/v161-work/definition-quiz-results.json',JSON.stringify({sha256,scope:'technical payload checks for two changed definitions; not semantic acceptance of all generated alternatives',results},null,2)+'\n');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
