const {chromium}=require("playwright");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const crypto=require("node:crypto");
const path=require("node:path");
const {pathToFileURL}=require("node:url");

const HTML="JLPT_N1_ukrainian_reading_v229.html";
const BASE="JLPT_N1_ukrainian_reading_v228.html";
const W="completion/v229-work";
const IDS=[2734,544,550,552,557,588,599,644,663,1631,3337,3345];
const prep=JSON.parse(fs.readFileSync(path.join(W,"prepare-results.json"),"utf8"));
const norm=x=>String(x||"").replace(/[\n\r\t]/g," ").split(" ").filter(Boolean).join(" ");

(async()=>{
  const candidateBytes=fs.readFileSync(HTML);
  const candidateSha=crypto.createHash("sha256").update(candidateBytes).digest("hex");
  assert.equal(candidateSha,prep.candidate_sha256);
  assert.equal(candidateBytes.length,prep.candidate_bytes);
  const browser=await chromium.launch({headless:true});
  try{
    const errors=[];
    const page=await browser.newPage({viewport:{width:412,height:900}});
    page.on("pageerror",e=>errors.push(String(e)));
    await page.goto(pathToFileURL(path.resolve(HTML)).href);
    const base=await browser.newPage({viewport:{width:412,height:900}});
    await base.goto(pathToFileURL(path.resolve(BASE)).href);

    const structural=await page.evaluate(()=>({
      vocabulary:DEFAULT_VOCAB.length,
      grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,
      lexicalPairs:VOCAB_AUDITED_PAIRS.length,
      uniqueIds:new Set(DEFAULT_VOCAB.map(x=>Number(x.id))).size,
      allDetails:DEFAULT_VOCAB.every(x=>Boolean(VOCAB_DETAILS_BY_ID[String(x.id)])),
      allPos:DEFAULT_VOCAB.every(x=>Boolean(VOCAB_POS_BY_ID[String(x.id)])),
      storageKey:STORAGE_KEY,
      customVocabKey:VOCAB_DATA_KEY
    }));
    assert.deepEqual(
      {vocabulary:structural.vocabulary,grammar:structural.grammar,lexicalPairs:structural.lexicalPairs,uniqueIds:structural.uniqueIds,allDetails:structural.allDetails,allPos:structural.allPos},
      {vocabulary:3914,grammar:130,lexicalPairs:859,uniqueIds:3914,allDetails:true,allPos:true}
    );

    const protectedBlocks=async p=>p.evaluate(()=>({
      vocab:JSON.stringify(DEFAULT_VOCAB),
      grammar:JSON.stringify(GRAMMAR_DETAILS_BY_ID),
      pairs:JSON.stringify(VOCAB_AUDITED_PAIRS),
      readingOverrides:JSON.stringify(REVIEWED_READING_OPTIONS),
      kanaTargets:JSON.stringify(VOCAB_KANA_EXAMPLE_TARGETS),
      exampleTargets:JSON.stringify(REVIEWED_EXAMPLE_TARGETS),
      storageKey:STORAGE_KEY,
      customVocabKey:VOCAB_DATA_KEY
    }));
    assert.deepEqual(await protectedBlocks(page),await protectedBlocks(base));

    const beforePools=await base.evaluate(ids=>ids.map(id=>{
      const v=DEFAULT_VOCAB.find(x=>Number(x.id)===id);
      const item={kind:"v",id:String(id),word:v};
      const reading=quizReadingOptions(item);
      const cloze=clozeWordCandidates(item);
      const d=VOCAB_DETAILS_BY_ID[String(id)];
      return {id,word:v.w,pos:vocabPartOfSpeech(id),readingOptions:reading,readingCount:reading.length,clozeCount:cloze.length,readingEligible:reading.length>=3,clozeEligible:cloze.length>=3,clozeExamples:d.examples.map(s=>literalClozeAvailable(s,item,SmartEngine))};
    }),IDS);
    const afterPools=await page.evaluate(ids=>ids.map(id=>{
      const v=DEFAULT_VOCAB.find(x=>Number(x.id)===id);
      const item={kind:"v",id:String(id),word:v};
      const reading=quizReadingOptions(item);
      const cloze=clozeWordCandidates(item);
      const d=VOCAB_DETAILS_BY_ID[String(id)];
      return {id,word:v.w,pos:vocabPartOfSpeech(id),readingOptions:reading,readingCount:reading.length,clozeCount:cloze.length,readingEligible:reading.length>=3,clozeEligible:cloze.length>=3,clozeExamples:d.examples.map(s=>literalClozeAvailable(s,item,SmartEngine))};
    }),IDS);
    const poolImpact=beforePools.map((b,i)=>({
      id:b.id,word:b.word,posBefore:b.pos,posAfter:afterPools[i].pos,
      readingBefore:b.readingCount,readingAfter:afterPools[i].readingCount,
      clozeBefore:b.clozeCount,clozeAfter:afterPools[i].clozeCount,
      readingEligibleBefore:b.readingEligible,readingEligibleAfter:afterPools[i].readingEligible,
      clozeEligibleBefore:b.clozeEligible,clozeEligibleAfter:afterPools[i].clozeEligible,
      clozeExamplesBefore:b.clozeExamples,clozeExamplesAfter:afterPools[i].clozeExamples,
      readingOptionsBefore:b.readingOptions,readingOptionsAfter:afterPools[i].readingOptions
    }));
    for(const x of poolImpact){
      if(x.id!==2734){
        assert.equal(x.readingBefore,x.readingAfter,"unexpected reading pool change for "+x.id);
        assert.equal(x.clozeBefore,x.clozeAfter,"unexpected cloze pool change for "+x.id);
      }
    }
    const p2734=poolImpact.find(x=>x.id===2734);
    assert.deepEqual(p2734.posAfter,["連体詞"]);
    assert.equal(p2734.readingBefore,6);
    assert.equal(p2734.readingAfter,0);
    assert.equal(p2734.clozeBefore,705);
    assert.equal(p2734.clozeAfter,2);
    assert.equal(p2734.readingEligibleAfter,false);
    assert.equal(p2734.clozeEligibleAfter,false);

    const meaningDiagnostics=await page.evaluate(ids=>{
      const out=[];
      for(const id of ids){
        const v=DEFAULT_VOCAB.find(x=>Number(x.id)===id);
        const d=VOCAB_DETAILS_BY_ID[String(id)];
        const item={kind:"v",id:String(id),word:v};
        const def=SmartEngine.getDefinition(v.w,"v",id);
        for(let ei=0;ei<d.examples.length;ei++){
          const example=d.examples[ei];
          const samples=[];
          for(let trial=0;trial<3;trial++){
            const q=quizMeaningOptions(item,def,example);
            const lengths=[q.correct,...q.wrong].map(x=>String(x).length);
            const minLength=Math.min(...lengths),maxLength=Math.max(...lengths);
            samples.push({
              correct:q.correct,wrong:q.wrong,note:q.note,
              wrongCount:q.wrong.length,uniqueWrong:new Set(q.wrong).size===q.wrong.length,
              correctExcluded:!q.wrong.includes(q.correct),
              optionLengths:lengths,minLength,maxLength,lengthRatio:maxLength/minLength
            });
          }
          out.push({id,word:v.w,exampleIndex:ei,example,samples});
        }
      }
      return out;
    },IDS);
    const meaningStructurePass=meaningDiagnostics.every(x=>x.samples.every(s=>s.wrongCount===3&&s.uniqueWrong&&s.correctExcluded));
    const meaningLengthPass=meaningDiagnostics.every(x=>x.samples.every(s=>s.lengthRatio<=1.5));
    fs.writeFileSync(path.join(W,"meaning-quiz-diagnostics.json"),JSON.stringify(meaningDiagnostics,null,2)+"\\n");
    fs.writeFileSync(path.join(W,"pool-impact.json"),JSON.stringify(poolImpact,null,2)+"\\n");
    assert.ok(meaningStructurePass,"meaning quiz options must contain one key and three unique distinct distractors");
    assert.ok(meaningLengthPass,"meaning quiz option lengths must not create a strong answer-length clue");
    const quiz3345=await page.evaluate(sentence=>{
      const q=REVIEWED_MEANING_QUIZZES["v_3345"];
      return q?.byExample?.[sentence]||null;
    },"彼は会議で散々に批判され、反論できなかった。");
    assert.ok(quiz3345);
    assert.equal(quiz3345.correct,"非常に厳しい非難を受けた様子。");
    assert.equal(quiz3345.wrong.length,3);
    assert.equal(new Set([quiz3345.correct,...quiz3345.wrong]).size,4);

    const rendered=await page.evaluate(async ids=>{
      const norm=x=>String(x||"").replace(/[\\n\\r\\t]/g," ").split(" ").filter(Boolean).join(" ");
      const out=[];
      showView("cards");
      for(const id of ids){
        await openCardDetail("v",id);
        await new Promise(r=>setTimeout(r,80));
        const norm=x=>String(x||"").replace(/[\\n\\r\\t]/g," ").split(" ").filter(Boolean).join(" ");
        const body=document.getElementById("cardDetailBody");
        const txt=norm(document.getElementById("cardDetail")?.innerText||body?.innerText||document.body.innerText||"");
        const d=VOCAB_DETAILS_BY_ID[String(id)];
        const posNode=body?.querySelector(".word-pos")||document.querySelector(".word-pos");
        out.push({
          id,word:d.w,
          title:norm(txt).includes(norm(d.w)),
          meaning:norm(txt).includes(norm(d.m)),
          pos:posNode?.innerText?.replace(/\s+/g,"").replace(/・/g,"・")||"",
          expectedPos:vocabPartOfSpeech(id).join("・"),
          usageData:Boolean(d.usage),
          usageVisible:norm(txt).includes(norm(d.usage)),
          examples:d.examples.every(x=>norm(txt).includes(norm(x))),
          translations:d.exampleTranslations.every(x=>norm(txt).includes(norm(x))),
          visibleText:txt.slice(0,1600)
        });
      }
      return out;
    },IDS);
    fs.writeFileSync(path.join(W,"rendered-debug.json"),JSON.stringify(rendered,null,2)+"\\n");
    assert.ok(rendered.every(x=>x.title&&x.meaning&&x.usageData&&x.examples&&x.translations),"card detail text did not include required content; see rendered-debug.json");
    assert.ok(rendered.every(x=>norm(x.pos)===norm(x.expectedPos)),"rendered POS labels do not match POS map");
    assert.equal(rendered.find(x=>x.id===2734).pos,"連体詞");
    assert.equal(rendered.find(x=>x.id===644).pos,"副詞");
    assert.equal(rendered.find(x=>x.id===3345).pos,"副詞");

    const responsive=[];
    for(const width of [360,412,1280]){
      await page.setViewportSize({width,height:900});
      const z=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth}));
      responsive.push({...z,overflow:z.scrollWidth>width||z.bodyWidth>width});
    }
    assert.ok(responsive.every(x=>!x.overflow));

    const storage=await page.evaluate(()=>{
      const k=STORAGE_KEY,old=localStorage.getItem(k);
      const sentinel=JSON.stringify({meta:{sessionSize:10,streak:7,lastStudyDate:"2026-11-14"},vp:{"2734":{status:"S",timesShown:3}},gp:{"95":{status:"X"}}});
      localStorage.setItem(k,sentinel);
      const roundTrip=localStorage.getItem(k)===sentinel;
      if(old===null)localStorage.removeItem(k);else localStorage.setItem(k,old);
      return {roundTrip,restored:localStorage.getItem(k)===old};
    });
    assert.ok(storage.roundTrip&&storage.restored);
    assert.deepEqual(errors,[]);

    const result={
      pass:true,candidate_sha256:candidateSha,candidate_bytes:candidateBytes.length,
      counts:structural,scope_count:IDS.length,
      poolImpact,meaningStructurePass,meaningLengthPass,meaningDiagnosticCount:meaningDiagnostics.length,
      quiz3345,rendered,responsive,storage,pageErrors:errors,
      unchanged:{DEFAULT_VOCAB:true,GRAMMAR_DETAILS_BY_ID:true,VOCAB_AUDITED_PAIRS:true,REVIEWED_READING_OPTIONS:true,VOCAB_KANA_EXAMPLE_TARGETS:true,REVIEWED_EXAMPLE_TARGETS:true,storageKeys:true}
    };
    fs.writeFileSync(path.join(W,"browser-results.json"),JSON.stringify(result,null,2)+"\n");
    fs.writeFileSync(path.join(W,"rendered-debug.json"),JSON.stringify(rendered,null,2)+"\n");
    console.log(JSON.stringify(result,null,2));
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
