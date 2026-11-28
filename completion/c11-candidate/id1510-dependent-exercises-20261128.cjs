const {chromium}=require("playwright");
const fs=require("node:fs");
(async()=>{
const b=await chromium.launch({executablePath:process.env.CHROMIUM_PATH || undefined});
try {
 const p=await b.newPage(); const errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.route('http://jlpt.test/',r=>r.fulfill({contentType:'text/html',body:fs.readFileSync('current.html')}));
 await p.goto('http://jlpt.test/');
 const result=await p.evaluate(()=>{
   const word=DEFAULT_VOCAB.find(x=>x.id===1510);
   const item={kind:'v',id:'1510',word};
   const def=SmartEngine.getDefinition(word.w,item.kind,item.id);
   const reading=quizReadingOptions(item);
   const cloze=clozeWordCandidates(item);
   return {reading,cloze,contexts:def.examples.map(ex=>({ex,eligible:literalClozeAvailable(ex,item,SmartEngine),meaning:quizMeaningOptions(item,def,ex)}))};
 });
 console.log(JSON.stringify({result,errors}));
}finally{await b.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
