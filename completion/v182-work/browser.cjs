const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const crypto=require('node:crypto');
const path=require('node:path');
const {pathToFileURL}=require('node:url');

const HTML='JLPT_N1_ukrainian_reading_v182.html';
const prepare=JSON.parse(fs.readFileSync('completion/v182-work/prepare-results.json','utf8'));
const diagnostic=JSON.parse(fs.readFileSync('completion/v180-c11-diagnostics.json','utf8'));
const bytes=fs.readFileSync(HTML);
const sha=crypto.createHash('sha256').update(bytes).digest('hex');
assert.equal(sha,prepare.candidate_sha256,'candidate SHA differs from deterministic preparation');
assert.equal(diagnostic.pass,true,'v180 reading-pool diagnostic did not pass');

const EXPECTED_MANUAL={
  255:['ちょうせつ','ちょうせい','がくせつ'],
  327:['いしき','いせき','うつわ'],
  1819:['うちがわ','うつわ','うわき']
};

async function main(){
  const browser=await chromium.launch({headless:true});
  try{
    const page=await browser.newPage({viewport:{width:1280,height:900}});
    const errors=[];
    page.on('pageerror',e=>errors.push(String(e)));
    await page.goto(pathToFileURL(path.resolve(HTML)).href);
    const result=await page.evaluate(({diagnostic,prepare,expectedManual})=>{
      const clone=x=>JSON.parse(JSON.stringify(x));
      const getVocab=id=>DEFAULT_VOCAB.find(x=>Number(x.id)===Number(id));
      const getDetail=id=>VOCAB_DETAILS_BY_ID[String(id)];
      const ids=diagnostic.data.readingPools.pools.map(x=>Number(x.id));
      const beforePos={255:clone(VOCAB_POS_BY_ID['255']),327:clone(VOCAB_POS_BY_ID['327'])};
      const expectedPos={255:['名詞','ナ形'],327:['名詞','ナ形']};
      const manualResults=[];
      const poolResults=ids.map(id=>{
        const item=getVocab(id);
        if(!item)throw new Error('missing reading-pool target '+id);
        const options=quizReadingOptions({kind:'v',id,word:item});
        const unique=new Set(options).size===options.length;
        const manual=Object.prototype.hasOwnProperty.call(expectedManual,id);
        const correct=item.r;
        return {id,word:item.w,reading:correct,pos:vocabPartOfSpeech(id),options,unique,correctExcluded:!options.includes(correct),manual};
      });
      for(const [id,expected] of Object.entries(expectedPos)){
        const actual=vocabPartOfSpeech(Number(id));
        if(JSON.stringify(actual)!==JSON.stringify(expected))throw new Error('POS mismatch '+id+': '+JSON.stringify(actual));
      }
      for(const [id,expected] of Object.entries(expectedManual)){
        const item=getVocab(Number(id));
        const actual=quizReadingOptions({kind:'v',id:Number(id),word:item});
        if(JSON.stringify(actual)!==JSON.stringify(expected))throw new Error('manual reading override mismatch '+id+': '+JSON.stringify(actual));
        manualResults.push({id:Number(id),word:item.w,correct:item.r,wrong:actual,unique:new Set([item.r,...actual]).size===4});
      }
      const expectedAutomatic=diagnostic.data.readingPools.pools.filter(x=>![255,327,1819].includes(Number(x.id)));
      const automaticChecks=expectedAutomatic.map(pool=>{
        const actual=poolResults.find(x=>x.id===Number(pool.id));
        const expected=pool.after.automaticOptions;
        return {id:Number(pool.id),expected,actual:actual.options,match:JSON.stringify(expected)===JSON.stringify(actual.options)};
      });
      const byId=Object.fromEntries(poolResults.map(x=>[x.id,x]));
      const clozeIds=[255,327,1819,359];
      const clozeAfter=Object.fromEntries(clozeIds.map(id=>{
        const item=getVocab(id);
        const detail=getDetail(id);
        return [id,{candidateCount:clozeWordCandidates({kind:'v',id,word:item}).length,examples:detail.examples.map(sentence=>({sentence,marked:SmartEngine.markTarget(sentence,'v',item.w).found,literal:literalClozeAvailable(sentence,{kind:'v',id,word:item},SmartEngine)}))}];
      }));
      const currentPos255=clone(VOCAB_POS_BY_ID['255']);
      const currentCloze255=clozeWordCandidates({kind:'v',id:255,word:getVocab(255)}).length;
      const savedOverrides=clone(REVIEWED_READING_OPTIONS);
      for(const id of ['255','327','1819'])delete REVIEWED_READING_OPTIONS[id];
      const allIds=DEFAULT_VOCAB.map(x=>Number(x.id));
      const autoBefore=allIds.map(id=>({id,options:quizReadingOptions({kind:'v',id,word:getVocab(id)})}));
      VOCAB_POS_BY_ID['255']=['名詞','ナ形','副詞'];
      const combinedCloze255=clozeWordCandidates({kind:'v',id:255,word:getVocab(255)}).length;
      const autoAfter=allIds.map(id=>({id,options:quizReadingOptions({kind:'v',id,word:getVocab(id)})}));
      const combinedChanged=autoBefore.map((x,i)=>({id:x.id,before:x.options,after:autoAfter[i].options})).filter(x=>JSON.stringify(x.before)!==JSON.stringify(x.after));
      const combinedLost=combinedChanged.filter(x=>x.before.length>=3&&x.after.length<3);
      const combinedGained=combinedChanged.filter(x=>x.before.length<3&&x.after.length>=3);
      for(const k of Object.keys(REVIEWED_READING_OPTIONS))delete REVIEWED_READING_OPTIONS[k];
      Object.assign(REVIEWED_READING_OPTIONS,savedOverrides);
      const combinedAfterOverrides=allIds.map(id=>({id,options:quizReadingOptions({kind:'v',id,word:getVocab(id)})}));
      const combinedRemainingLost=autoBefore.map((x,i)=>({id:x.id,before:x.options,after:combinedAfterOverrides[i].options})).filter(x=>x.before.length>=3&&x.after.length<3);
      VOCAB_POS_BY_ID['255']=currentPos255;
      const posTradeoff={currentPos:currentPos255,currentClozeCandidates:currentCloze255,withAdverbPos:['名詞','ナ形','副詞'],combinedClozeCandidates:combinedCloze255,combinedAdverbTagKeepsClozeMinimum:combinedCloze255>=3};
      const combinedPosPoolImpact={changedPoolCount:combinedChanged.length,lostEligibility:combinedLost.map(x=>({id:x.id,before:x.before,after:x.after})),gainedEligibility:combinedGained.map(x=>({id:x.id,before:x.before,after:x.after})),remainingLostAfterExistingOverrides:combinedRemainingLost.map(x=>({id:x.id,before:x.before,after:x.after}))};
      const posHtml={255:wordPosHtml({kind:'v',id:255}),327:wordPosHtml({kind:'v',id:327})};
      const usage={255:getDetail(255).usage,327:getDetail(327).usage};
      const functionSources={
        quizReadingOptions:quizReadingOptions.toString(),
        clozeWordCandidates:clozeWordCandidates.toString()
      };
      const storageKey='choba_n1uk_storage_v1';
      const oldStorage=localStorage.getItem(storageKey);
      localStorage.setItem(storageKey,'v182-progress-sentinel');
      const sentinelRoundTrip=localStorage.getItem(storageKey)==='v182-progress-sentinel';
      if(oldStorage===null)localStorage.removeItem(storageKey);else localStorage.setItem(storageKey,oldStorage);
      const storageRestored=localStorage.getItem(storageKey)===oldStorage;
      return {
        counts:{vocabulary:DEFAULT_VOCAB.length,grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,lexicalPairs:VOCAB_AUDITED_PAIRS.length,readingOverrideEntries:Object.keys(REVIEWED_READING_OPTIONS).length},
        pos:{before:beforePos,after:{255:vocabPartOfSpeech(255),327:vocabPartOfSpeech(327)}},
        poolResults,manualResults,automaticChecks,
        clozeAfter,posHtml,usage,functionSources,posTradeoff,combinedPosPoolImpact,
        storage:{sentinelRoundTrip,storageRestored}
      };
    },{diagnostic,prepare,expectedManual:EXPECTED_MANUAL});

    assert.equal(result.counts.vocabulary,3914);
    assert.equal(result.counts.grammar,130);
    assert.equal(result.counts.lexicalPairs,859);
    assert.equal(result.counts.readingOverrideEntries,4);
    assert.equal(result.poolResults.length,23);
    assert.equal(result.poolResults.every(x=>x.options.length>=3&&x.unique&&x.correctExcluded),true,'one or more reading pools lack three distinct wrong answers');
    assert.equal(result.automaticChecks.every(x=>x.match),true,'automatic pool differs from verified v180 diagnostic');
    assert.equal(result.manualResults.every(x=>x.unique),true,'manual override has duplicate or correct option');
    assert.equal(result.poolResults.find(x=>x.id===359).options.includes('うわき'),true,'ID359 did not gain the expected 浮気 distractor');
    assert.equal(result.clozeAfter[255].candidateCount,prepare.cloze_candidates_after['255']);
    assert.equal(result.clozeAfter[327].candidateCount,prepare.cloze_candidates_after['327']);
    assert.equal(result.clozeAfter[1819].candidateCount,prepare.cloze_candidates_after['1819']);
    assert.equal(result.clozeAfter[359].candidateCount,prepare.cloze_candidates_after['359']);
    assert.equal(result.clozeAfter[255].candidateCount>=3,true);
    assert.equal(result.posTradeoff.currentClozeCandidates>=3,true);
    assert.equal(result.posTradeoff.combinedClozeCandidates<3,true,'adding 副詞 to the POS set unexpectedly preserves the cloze minimum');
    assert.equal(result.clozeAfter[327].candidateCount>=3,true);
    assert.equal(result.clozeAfter[1819].candidateCount>=3,true);
    assert.equal(result.clozeAfter[359].candidateCount>=3,true);
    assert.equal(result.clozeAfter[255].examples.every(x=>x.marked&&x.literal),true,'ID255 example cloze eligibility changed');
    assert.equal(result.clozeAfter[327].examples.every(x=>x.marked&&x.literal),true,'ID327 example cloze eligibility changed');
    assert.equal(result.posHtml[255].includes('ナ形'),true);
    assert.equal(result.posHtml[327].includes('ナ形'),true);
    assert.equal(result.usage[255].includes('直接な交渉'),true);
    assert.equal(result.usage[327].includes('浮気な人'),true);
    assert.equal(result.functionSources.quizReadingOptions,diagnostic.data.id2433FunctionSources.quizReadingOptions,'reading algorithm changed');
    assert.equal(result.functionSources.clozeWordCandidates,diagnostic.data.id2433FunctionSources.clozeWordCandidates,'cloze algorithm changed');
    assert.equal(result.storage.sentinelRoundTrip,true);
    assert.equal(result.storage.storageRestored,true);
    assert.deepEqual(errors,[]);

    const responsive=[];
    for(const width of [360,412,1280]){
      await page.setViewportSize({width,height:900});
      responsive.push(await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth,overflow:document.documentElement.scrollWidth>innerWidth})));
    }
    assert.equal(responsive.every(x=>!x.overflow),true,'horizontal overflow at one or more widths');
    const output={pass:true,candidate_sha256:sha,candidate_bytes:bytes.length,counts:result.counts,pos:result.pos,reading_pool_count:result.poolResults.length,reading_pool_min_options:Math.min(...result.poolResults.map(x=>x.options.length)),manual_overrides:result.manualResults,automatic_pool_checks:result.automaticChecks.length,cloze_after:result.clozeAfter,pos_tradeoff:result.posTradeoff,combined_pos_pool_impact:result.combinedPosPoolImpact,responsive,storage:result.storage,pageErrors:errors};
    fs.writeFileSync('completion/v182-work/browser-results.json',JSON.stringify(output,null,2)+'\n');
    console.log(JSON.stringify(output,null,2));
  }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
