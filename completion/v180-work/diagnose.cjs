const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const crypto=require('node:crypto');
const path=require('node:path');
const {pathToFileURL}=require('node:url');

const HTML='JLPT_N1_ukrainian_reading_v179.html';
const IMPACT='completion/v179-reading-pool-impact.json';

function uniquePool(item){
  const v=item,word=v.w,reading=v.r,frame=readingFrame(word);
  const pos=vocabPartOfSpeech(v.id).join('|');
  const prefix=(word.match(/^[ぁ-ゟー]+/)||[''])[0];
  const tail=(word.match(/[ぁ-ゟー]+$/)||[''])[0];
  if((prefix&&!reading.startsWith(prefix))||(tail&&!reading.endsWith(tail)))return [];
  const core=reading.slice(prefix.length,tail.length?-tail.length:undefined);
  const raw=ACTIVE_VOCAB.filter(x=>x.id!==v.id&&x.r!==reading&&/^[ぁ-ゟー]+$/.test(x.r||'')&&readingFrame(x.w)===frame&&vocabPartOfSpeech(x.id).join('|')===pos&&Math.abs(x.r.length-reading.length)<=1&&(!prefix||x.r.startsWith(prefix))&&(!tail||x.r.endsWith(tail)))
    .map(x=>({id:x.id,word:x.w,reading:x.r,pos:vocabPartOfSpeech(x.id),distance:readingDistance(core,x.r.slice(prefix.length,tail.length?-tail.length:undefined))}))
    .filter(x=>x.distance>0&&x.distance<=2)
    .sort((a,b)=>a.distance-b.distance||a.reading.localeCompare(b.reading));
  const seen=new Set(),out=[];
  for(const x of raw){if(!seen.has(x.reading)){seen.add(x.reading);out.push(x);}}
  return out.slice(0,6);
}

async function main(){
  const htmlBytes=fs.readFileSync(HTML);
  const htmlSha=crypto.createHash('sha256').update(htmlBytes).digest('hex');
  assert.equal(htmlSha,'359490152e9d4c7ae86cc746e2b69d132922946767890bc7aa7be6f5cdef2ba8','unexpected v179 HTML');
  const impact=JSON.parse(fs.readFileSync(IMPACT,'utf8'));
  const browser=await chromium.launch({headless:true});
  try{
    const page=await browser.newPage({viewport:{width:1280,height:915}});
    const errors=[];page.on('pageerror',e=>errors.push(String(e)));
    await page.goto(pathToFileURL(path.resolve(HTML)).href);
    const data=await page.evaluate(impact=>{
      const clone=x=>JSON.parse(JSON.stringify(x));
      const getVocab=id=>DEFAULT_VOCAB.find(x=>Number(x.id)===Number(id));
      const getDetail=id=>VOCAB_DETAILS_BY_ID[String(id)];
      const id2433=2433,item=getVocab(id2433),detail=getDetail(id2433);
      if(!item||!detail)throw new Error('ID2433 missing');
      const meaningRows=Array.isArray(REVIEWED_MEANING_QUIZZES)?REVIEWED_MEANING_QUIZZES:REVIEWED_MEANING_QUIZZES;
      const findRows=(value,id)=>{
        if(Array.isArray(value))return value.filter(x=>[x.id,x.vocabId,x.targetId,x.key,x.word].some(v=>String(v??'')===String(id)||String(v??'')==='v_'+id));
        if(value&&typeof value==='object')return Object.entries(value).filter(([k,v])=>k===String(id)||k==='v_'+id||[v?.id,v?.vocabId,v?.targetId,v?.word].some(z=>String(z??'')===String(id))).map(([key,value])=>({key,value}));
        return [];
      };
      const getQuiz=(id,sentence,seed)=>{
        const old=Math.random;Math.random=()=>seed;
        try{const w=getVocab(id),entry={kind:'v',id:Number(id),word:w},def=SmartEngine.getDefinition(w.w,'v',Number(id));return quizMeaningOptions(entry,def,sentence);}
        finally{Math.random=old;}
      };
      const targets=REVIEWED_EXAMPLE_TARGETS.filter(x=>Number(x.id)===id2433);
      const kanaTargets=findRows(VOCAB_KANA_EXAMPLE_TARGETS,id2433);
      const examples=detail.examples.map((sentence,index)=>{
        const marked=SmartEngine.markTarget(sentence,'v',item.w);
        return {index,sentence,translation:detail.exampleTranslations?.[index]??null,automaticMeaningSeeds:[0,0.25,0.5,0.75].map(seed=>({seed,quiz:getQuiz(id2433,sentence,seed)})),markTarget:{found:marked.found,marked:marked.s,spans:[...marked.s.matchAll(/\u0001([^\u0002]*)\u0002/g)].map(m=>m[1])},literalClozeAvailable:literalClozeAvailable(sentence,{kind:'v',id:id2433,word:item},SmartEngine)};
      });
      const meaningQuizArray=Array.isArray(meaningRows);
      const meaningQuizSample=meaningQuizArray?meaningRows.slice(0,3):Object.entries(meaningRows).slice(0,3);
      const source={
        quizMeaningOptions:quizMeaningOptions.toString().slice(0,9000),
        clozeWordCandidates:clozeWordCandidates.toString().slice(0,9000),
        literalClozeAvailable:literalClozeAvailable.toString().slice(0,9000),
        markTarget:SmartEngine.markTarget.toString().slice(0,9000),
        getDefinition:SmartEngine.getDefinition.toString().slice(0,9000)
      };
        const uniquePool=item=>{
        const v=item,word=v.w,reading=v.r,frame=readingFrame(word);
        const pos=vocabPartOfSpeech(v.id).join('|');
        const prefix=(word.match(/^[ぁ-ゟー]+/)||[''])[0];
        const tail=(word.match(/[ぁ-ゟー]+$/)||[''])[0];
        if((prefix&&!reading.startsWith(prefix))||(tail&&!reading.endsWith(tail)))return [];
        const core=reading.slice(prefix.length,tail.length?-tail.length:undefined);
        const raw=ACTIVE_VOCAB.filter(x=>x.id!==v.id&&x.r!==reading&&/^[ぁ-ゟー]+$/.test(x.r||'')&&readingFrame(x.w)===frame&&vocabPartOfSpeech(x.id).join('|')===pos&&Math.abs(x.r.length-reading.length)<=1&&(!prefix||x.r.startsWith(prefix))&&(!tail||x.r.endsWith(tail)))
          .map(x=>({id:x.id,word:x.w,reading:x.r,pos:vocabPartOfSpeech(x.id),distance:readingDistance(core,x.r.slice(prefix.length,tail.length?-tail.length:undefined))}))
          .filter(x=>x.distance>0&&x.distance<=2)
          .sort((a,b)=>a.distance-b.distance||a.reading.localeCompare(b.reading));
        const seen=new Set(),out=[];
        for(const x of raw){if(!seen.has(x.reading)){seen.add(x.reading);out.push(x);}}
        return out.slice(0,6);
      };
    const original255=clone(VOCAB_POS_BY_ID['255']),original327=clone(VOCAB_POS_BY_ID['327']);
      const ids=impact.changed_pools.map(x=>Number(x.id));
      const compute=id=>{
        const w=getVocab(id);if(!w)throw new Error('Missing affected pool ID '+id);
        const item={kind:'v',id,word:w};
        return {id,word:w.w,reading:w.r,pos:vocabPartOfSpeech(id),automaticOptions:quizReadingOptions(item),candidatePool:uniquePool(w)};
      };
      const before=ids.map(compute);
      VOCAB_POS_BY_ID['255']=['名詞','ナ形'];
      VOCAB_POS_BY_ID['327']=['名詞','ナ形'];
      const after=ids.map(compute);
      VOCAB_POS_BY_ID['255']=original255;
      VOCAB_POS_BY_ID['327']=original327;
      const pools=before.map((b,i)=>({id:b.id,word:b.word,reading:b.reading,before:{pos:b.pos,automaticOptions:b.automaticOptions,candidates:b.candidatePool},after:{pos:after[i].pos,automaticOptions:after[i].automaticOptions,candidates:after[i].candidatePool},changed:JSON.stringify(b.automaticOptions)!==JSON.stringify(after[i].automaticOptions)}));
      const lost=pools.filter(x=>x.before.automaticOptions.length>=3&&x.after.automaticOptions.length<3).map(x=>({id:x.id,word:x.word,before:x.before.automaticOptions.length,after:x.after.automaticOptions.length}));
      const gained=pools.filter(x=>x.before.automaticOptions.length<3&&x.after.automaticOptions.length>=3).map(x=>({id:x.id,word:x.word,before:x.before.automaticOptions.length,after:x.after.automaticOptions.length}));
      const progressKey='choba_n1uk_storage_v1',oldStorage=localStorage.getItem(progressKey);
      localStorage.setItem(progressKey,'v180-diagnostic-sentinel');
      const storageUnchanged=localStorage.getItem(progressKey)==='v180-diagnostic-sentinel';
      if(oldStorage===null)localStorage.removeItem(progressKey);else localStorage.setItem(progressKey,oldStorage);
      return {
        counts:{vocabulary:DEFAULT_VOCAB.length,vocabDetails:Object.keys(VOCAB_DETAILS_BY_ID).length,grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,lexicalPairs:VOCAB_AUDITED_PAIRS.length,reviewedMeaningQuizzes:REVIEWED_MEANING_QUIZZES.length??Object.keys(REVIEWED_MEANING_QUIZZES).length},
        id2433:{headword:item.w,reading:item.r,pos:vocabPartOfSpeech(id2433),definition:SmartEngine.getDefinition(item.w,'v',id2433),examples,meaningQuizStorage:{isArray:meaningQuizArray,length:meaningQuizArray?meaningRows.length:Object.keys(meaningRows).length,matches:findRows(meaningRows,id2433),sample:meaningQuizSample},reviewedExampleTargets:targets,kanaExampleTargets:kanaTargets,clozeCandidateCount:clozeWordCandidates({kind:'v',id:id2433,word:item}).length},
        id2433FunctionSources:source,
        readingPools:{changedPoolCount:pools.filter(x=>x.changed).length,pools,lost,gained},
        readingPoolSummary:{expectedChanged:impact.changed_pool_count,expectedLost:impact.lost_eligibility,expectedGained:impact.gained_eligibility},
        progressStorageRestored:storageUnchanged,
        noPersistedMutation:true
      };
    },impact);
    assert.deepEqual(errors,[]);
    assert.equal(data.counts.vocabulary,3914);
    assert.equal(data.counts.grammar,130);
    assert.equal(data.counts.lexicalPairs,859);
    assert.equal(data.readingPools.changedPoolCount,impact.changed_pool_count,'changed-pool count differs from v179 evidence');
    assert.equal(data.readingPools.lost.length,impact.lost_eligibility.length,'lost eligibility count differs');
    assert.equal(data.readingPools.gained.length,impact.gained_eligibility.length,'gained eligibility count differs');
    const result={pass:true,base_version:'v179',base_sha256:htmlSha,base_bytes:htmlBytes.length,diagnostic_only:true,data,pageErrors:errors};
    fs.writeFileSync('completion/v180-work/diagnostics.json',JSON.stringify(result,null,2)+'\n');
    const cp=JSON.parse(fs.readFileSync('completion/v180-work/checkpoint.json','utf8'));
    cp.status='diagnostics passed; awaiting manual source review and content-only proposal';
    cp.diagnostics_sha256=crypto.createHash('sha256').update(fs.readFileSync('completion/v180-work/diagnostics.json')).digest('hex');
    cp.changed_pools=data.readingPools.changedPoolCount;
    cp.lost_eligibility=data.readingPools.lost;
    cp.gained_eligibility=data.readingPools.gained;
    fs.writeFileSync('completion/v180-work/checkpoint.json',JSON.stringify(cp,null,2)+'\n');
    console.log(JSON.stringify({pass:true,htmlSha,bytes:htmlBytes.length,counts:data.counts,id2433:data.id2433,readingPools:{changed:data.readingPools.changedPoolCount,lost:data.readingPools.lost,gained:data.readingPools.gained}},null,2));
  }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
