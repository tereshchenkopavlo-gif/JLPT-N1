const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const crypto=require('node:crypto');
const path=require('node:path');
const {pathToFileURL}=require('node:url');

const HTML='JLPT_N1_ukrainian_reading_v181.html';
const prepare=JSON.parse(fs.readFileSync('completion/v181-work/prepare-results.json','utf8'));
const bytes=fs.readFileSync(HTML);
const sha=crypto.createHash('sha256').update(bytes).digest('hex');
assert.equal(sha,prepare.candidate_sha256,'candidate SHA differs from deterministic preparation');

async function main(){
  const browser=await chromium.launch({headless:true});
  try{
    const page=await browser.newPage({viewport:{width:1280,height:900}});
    const errors=[];
    page.on('pageerror',e=>errors.push(String(e)));
    await page.goto(pathToFileURL(path.resolve(HTML)).href);
    const result=await page.evaluate(()=>{
      const item=DEFAULT_VOCAB.find(x=>Number(x.id)===2433);
      const detail=VOCAB_DETAILS_BY_ID['2433'];
      const it={kind:'v',id:2433,word:item};
      const entry=REVIEWED_MEANING_QUIZZES['v_2433'];
      if(!item||!detail||!entry)throw new Error('ID2433 or its saved meaning entry is missing');
      const rows=detail.examples.map((sentence,index)=>{
        const q=quizMeaningOptions(it,SmartEngine.getDefinition(item.w,'v',2433),sentence);
        const marked=SmartEngine.markTarget(sentence,'v',item.w);
        const spans=[...marked.s.matchAll(/\u0001([^\u0002]*)\u0002/g)].map(m=>m[1]);
        return {
          index,sentence,quiz:q,
          unique:new Set([q.correct,...q.wrong]).size===4,
          markedFound:marked.found,markedSpans:spans,
          literalClozeAvailable:literalClozeAvailable(sentence,it,SmartEngine)
        };
      });
      const oldEntry=REVIEWED_MEANING_QUIZZES['v_2433'];
      delete REVIEWED_MEANING_QUIZZES['v_2433'];
      const beforeEligibility=detail.examples.map(sentence=>{
        const found=SmartEngine.markTarget(sentence,'v',item.w).found;
        return found&&literalClozeAvailable(sentence,it,SmartEngine)&&clozeWordCandidates(it).length>=3&&!reviewedExampleTarget(sentence,'v',item.w)&&!REVIEWED_MEANING_QUIZZES['v_2433'];
      });
      REVIEWED_MEANING_QUIZZES['v_2433']=oldEntry;
      const afterEligibility=detail.examples.map(sentence=>{
        const found=SmartEngine.markTarget(sentence,'v',item.w).found;
        return found&&literalClozeAvailable(sentence,it,SmartEngine)&&clozeWordCandidates(it).length>=3&&!reviewedExampleTarget(sentence,'v',item.w)&&!REVIEWED_MEANING_QUIZZES['v_2433'];
      });
      const generated=[];
      for(const seed of [0,0.999]){
        const oldRandom=Math.random;
        let calls=0;
        Math.random=()=>{calls++;return calls===1?seed:0.25;};
        const passage=SmartEngine.generateOfflinePassage([it])[0];
        Math.random=oldRandom;
        const q=passage.questions[0];
        generated.push({
          seed,passageText:passage.text,
          questionCount:passage.questions.length,
          question:q,correct:q?q.choices[q.answer]:null,
          targetKey:passage.targetKeys[0]
        });
      }
      const storageKey='choba_n1uk_storage_v1';
      const oldStorage=localStorage.getItem(storageKey);
      localStorage.setItem(storageKey,'v181-progress-sentinel');
      const storageRoundTrip=localStorage.getItem(storageKey)==='v181-progress-sentinel';
      if(oldStorage===null)localStorage.removeItem(storageKey);else localStorage.setItem(storageKey,oldStorage);
      const storageRestored=localStorage.getItem(storageKey)===oldStorage;
      return {
        counts:{
          vocabulary:DEFAULT_VOCAB.length,
          grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,
          lexicalPairs:VOCAB_AUDITED_PAIRS.length,
          meaningQuizEntries:Object.keys(REVIEWED_MEANING_QUIZZES).length
        },
        id2433:{headword:item.w,reading:item.r,pos:vocabPartOfSpeech(2433),examples:rows,generated},
        cloze:{candidateCount:clozeWordCandidates(it).length,beforeEligibility,afterEligibility,unchanged:JSON.stringify(beforeEligibility)===JSON.stringify(afterEligibility)},
        progressStorageRestored:storageRoundTrip&&storageRestored
      };
    });
    assert.deepEqual(errors,[],'page errors');
    assert.deepEqual(result.counts,{vocabulary:3914,grammar:130,lexicalPairs:859,meaningQuizEntries:384});
    assert.equal(result.id2433.headword,'そびえる');
    assert.equal(result.id2433.reading,'そびえる');
    assert.equal(result.id2433.examples.length,2);
    for(const row of result.id2433.examples){
      assert.equal(row.quiz.wrong.length,3);
      assert.equal(row.unique,true);
      assert.equal(row.markedFound,true);
      assert.deepEqual(row.markedSpans,['そびえて']);
      assert.equal(row.literalClozeAvailable,false);
      assert.ok(row.quiz.note.length>0);
    }
    assert.deepEqual(result.cloze.beforeEligibility,[false,false]);
    assert.deepEqual(result.cloze.afterEligibility,[false,false]);
    assert.equal(result.cloze.unchanged,true);
    assert.equal(result.progressStorageRestored,true);
    assert.equal(result.id2433.generated.length,2);
    assert.equal(result.id2433.generated[0].questionCount,1);
    assert.equal(result.id2433.generated[1].questionCount,1);
    for(let i=0;i<2;i++){
      const generated=result.id2433.generated[i];
      const expected=result.id2433.examples[i];
      assert.ok(generated.passageText.includes('<b>そびえて</b>'));
      assert.equal(generated.targetKey,'v:2433');
      assert.equal(generated.correct,expected.quiz.correct);
      assert.equal(new Set(generated.question.choices).size,4);
    }
    const widths=[];
    for(const width of [360,412,1280]){
      await page.setViewportSize({width,height:900});
      const metrics=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,bodyScrollWidth:document.body.scrollWidth}));
      assert.ok(metrics.scrollWidth<=width+1,'horizontal overflow at '+width+'px: '+metrics.scrollWidth);
      widths.push({...metrics,pass:true});
    }
    const output={
      pass:true,version:'v181',sha256:sha,bytes:bytes.length,
      cardsChecked:1,contextsChecked:2,generatedPassagesChecked:2,
      uniqueFourOptionSets:true,clozeEligibilityUnchanged:true,
      progressStorageRestored:true,widths,pageErrors:errors,data:result
    };
    fs.writeFileSync('completion/v181-work/browser-results.json',JSON.stringify(output,null,2)+'\n');
    console.log(JSON.stringify(output,null,2));
  }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
