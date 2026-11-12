const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {pathToFileURL}=require('node:url');
const file='JLPT_N1_ukrainian_reading_v178.html';
const specs=[
 {id:'255',label:'直接',proposed:[['名詞','ナ形'],['名詞','副詞'],['名詞','ナ形','副詞']],knownAlternativeReadings:[]},
 {id:'327',label:'浮気',proposed:[['名詞','ナ形']],knownAlternativeReadings:['ふき']}
];
function uniquePool(item){
 const v=item.word,frame=readingFrame(v.w),pos=vocabPartOfSpeech(v.id).join('|');
 const prefix=(v.w.match(/^[ぁ-ゟー]+/)||[''])[0],tail=(v.w.match(/[ぁ-ゟー]+$/)||[''])[0];
 const core=v.r.slice(prefix.length,tail.length?-tail.length:undefined);
 const raw=ACTIVE_VOCAB.filter(x=>x.id!==v.id&&x.r!==v.r&&/^[ぁ-ゟー]+$/.test(x.r||'')&&readingFrame(x.w)===frame&&vocabPartOfSpeech(x.id).join('|')===pos&&Math.abs(x.r.length-v.r.length)<=1&&(!prefix||x.r.startsWith(prefix))&&(!tail||x.r.endsWith(tail)))
  .map(x=>({id:String(x.id),word:x.w,reading:x.r,d:readingDistance(core,x.r.slice(prefix.length,tail.length?-tail.length:undefined))}))
  .filter(x=>x.d>0&&x.d<=2).sort((a,b)=>a.d-b.d||a.reading.localeCompare(b.reading));
 const seen=new Set(),out=[];
 for(const x of raw){if(!seen.has(x.reading)){seen.add(x.reading);out.push(x);}}
 return out.slice(0,6);
}
async function main(){
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1280,height:900}}),errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(pathToFileURL(path.resolve(file)).href);
  const result=await page.evaluate(specs=>{
   const normPos=x=>Array.from(x);
   const out=[];
   for(const spec of specs){
    const item=ACTIVE_VOCAB.find(x=>String(x.id)===spec.id);
    if(!item)throw new Error('missing active vocab '+spec.id);
    const currentPos=VOCAB_POS_BY_ID[spec.id].slice();
    const currentOptions=quizReadingOptions({kind:'v',id:Number(spec.id),word:item});
    const currentPool=uniquePool({kind:'v',id:Number(spec.id),word:item});
    const reviewedOverride=Object.prototype.hasOwnProperty.call(REVIEWED_READING_OPTIONS,spec.id);
    const proposed=[];
    for(const tags of spec.proposed){
     const saved=VOCAB_POS_BY_ID[spec.id];
     VOCAB_POS_BY_ID[spec.id]=tags.slice();
     const options=quizReadingOptions({kind:'v',id:Number(spec.id),word:item});
     const pool=uniquePool({kind:'v',id:Number(spec.id),word:item});
     VOCAB_POS_BY_ID[spec.id]=saved;
     proposed.push({pos:tags,options,poolCount:options.length,pool,reviewedOverride});
    }
    out.push({id:spec.id,headword:item.w,correctReading:item.r,currentPos,currentOptions,currentPool,currentPoolCount:currentOptions.length,reviewedOverride,proposed,knownAlternativeReadings:spec.knownAlternativeReadings});
   }
   return {vocabularyCount:DEFAULT_VOCAB.length,grammarCount:Object.keys(GRAMMAR_DETAILS_BY_ID).length,pairCount:VOCAB_AUDITED_PAIRS.length,results:out};
  },specs);
  if(errors.length)throw new Error('page errors: '+errors.join('; '));
  const hash=crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
  const output={pass:true,baseVersion:'v178',baseSha256:hash,scope:result,applicationErrors:errors,mutatedPersistedData:false,mechanismChanged:false,reviewedReadingOptionsChanged:false};
  fs.writeFileSync('completion/v179-work/diagnostics.json',JSON.stringify(output,null,2)+'\n');
  const rows=['id\theadword\tcurrent_pos\tcurrent_options\tproposed_pos\tproposed_options\tcandidate_readings\tcandidate_words\tmanual_review'];
  for(const r of result.results){
   for(const p of r.proposed){
    rows.push([r.id,r.headword,r.currentPos.join('|'),r.currentOptions.join(';'),p.pos.join('|'),p.options.join(';'),p.pool.map(x=>x.reading).join(';'),p.pool.map(x=>x.word+'['+x.id+']').join(';'),'not accepted; inspect homographs and alternate readings'].join('\t'));
   }
  }
  fs.writeFileSync('completion/v179-work/proposals.tsv',rows.join('\n')+'\n');
  let md='# v179 — C11 reading-pool diagnostics\n\n**Base:** v178, SHA-256 '+hash+'. **Scope:** ID255 直接; ID327 浮気. No HTML/data/learning logic was changed.\n\n';
  md+='| ID | Word | Current POS | Current wrong readings | Proposed POS | Proposed pool |\n|---:|---|---|---|---|---:|\n';
  for(const r of result.results){for(const p of r.proposed){md+='| '+r.id+' | '+r.headword+' | '+r.currentPos.join(' / ')+' | '+r.currentOptions.join(', ')+' | '+p.pos.join(' / ')+' | '+p.poolCount+' |\n';}}
  md+='\n## Candidate words\n\n';
  for(const r of result.results){md+='### '+r.id+' '+r.headword+' — '+r.correctReading+'\n\nCurrent POS pool:\n\n';for(const x of r.currentPool){md+='- '+x.reading+' — '+x.word+' (ID '+x.id+', edit distance '+x.d+')\n';}for(const p of r.proposed){md+='\nProposed POS '+p.pos.join(' / ')+': '+p.poolCount+' options\n\n';for(const x of p.pool){md+='- '+x.reading+' — '+x.word+' (ID '+x.id+', edit distance '+x.d+')\n';}}if(r.knownAlternativeReadings.length)md+='\nKnown alternate reading(s) requiring exclusion from distractors: '+r.knownAlternativeReadings.join(', ')+'.\n';md+='\n';}
  md+='## Decision boundary\n\nA four-choice reading question needs three wrong options. Current automatic options are reported as diagnostics only. POS changes and curated overrides are not applied here. Any proposed override must be checked against dictionary readings, same-form homographs, and the exact question context; no learning-mechanism change is authorized.\n';
  fs.writeFileSync('completion/v179-work/diagnostics.md',md);
  console.log(JSON.stringify(output,null,2));
 }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
