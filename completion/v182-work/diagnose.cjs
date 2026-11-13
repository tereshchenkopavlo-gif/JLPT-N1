const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const crypto=require('node:crypto');
const path=require('node:path');
const {pathToFileURL}=require('node:url');

const HTML='JLPT_N1_ukrainian_reading_v181.html';
const EXPECTED_SHA='32c6f482db1e98dd1f98deb0197324a037fbd1a1bae8d5dd4b4f7123f126da7f';
const OVERRIDES={
  "255":{word:"直接",correct:"ちょくせつ",wrong:["ちょうせつ","ちょうせい","ちくせき"]},
  "327":{word:"浮気",correct:"うわき",wrong:["いしき","いせき","うつわ"]},
  "1819":{word:"内訳",correct:"うちわけ",wrong:["うちがわ","うつわ","うわき"]}
};

async function main(){
  const htmlBytes=fs.readFileSync(HTML);
  const htmlSha=crypto.createHash('sha256').update(htmlBytes).digest('hex');
  assert.equal(htmlSha,EXPECTED_SHA,'unexpected v181 HTML');
  const browser=await chromium.launch({headless:true});
  try{
    const page=await browser.newPage({viewport:{width:1280,height:900}});
    const errors=[];
    page.on('pageerror',e=>errors.push(String(e)));
    await page.goto(pathToFileURL(path.resolve(HTML)).href);
    const data=await page.evaluate(overrides=>{
      const clone=x=>JSON.parse(JSON.stringify(x));
      const getVocab=id=>DEFAULT_VOCAB.find(x=>Number(x.id)===Number(id));
      const getOptions=id=>{
        const word=getVocab(id);
        if(!word)throw new Error('missing vocabulary ID '+id);
        return quizReadingOptions({kind:'v',id:Number(id),word});
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
      const ids=DEFAULT_VOCAB.map(x=>Number(x.id));
      const originalPos255=clone(VOCAB_POS_BY_ID['255']);
      const originalPos327=clone(VOCAB_POS_BY_ID['327']);
      const originalOverrides=clone(REVIEWED_READING_OPTIONS);
      const before=ids.map(id=>({id,options:getOptions(id)}));
      VOCAB_POS_BY_ID['255']=['名詞','副詞'];
      VOCAB_POS_BY_ID['327']=['名詞','ナ形'];
      const after=ids.map(id=>({id,options:getOptions(id)}));
      const changed=before.map((x,i)=>({id:x.id,before:x.options,after:after[i].options}))
        .filter(x=>JSON.stringify(x.before)!==JSON.stringify(x.after));
      const lost=changed.filter(x=>x.before.length>=3&&x.after.length<3);
      const gained=changed.filter(x=>x.before.length<3&&x.after.length>=3);
      const details=changed.map(x=>{
        const item=getVocab(x.id);
        return {id:x.id,word:item.w,reading:item.r,pos:vocabPartOfSpeech(x.id),beforeOptions:x.before,afterOptions:x.after,afterCandidates:uniquePool(item)};
      });
      const sourceForReading=reading=>DEFAULT_VOCAB.filter(x=>x.r===reading).map(x=>({id:x.id,word:x.w,reading:x.r,pos:vocabPartOfSpeech(x.id)}));
      const overrideValidation=Object.entries(overrides).map(([id,entry])=>{
        const item=getVocab(id);
        const choices=[entry.correct,...entry.wrong];
        return {
          id:Number(id),word:item.w,reading:item.r,pos:vocabPartOfSpeech(id),
          correctMatches:item.w===entry.word&&item.r===entry.correct,
          threeUniqueWrong:entry.wrong.length===3&&new Set(choices).size===4,
          wrongSources:entry.wrong.map(r=>({reading:r,sources:sourceForReading(r)}))
        };
      });
      Object.assign(REVIEWED_READING_OPTIONS,overrides);
      const withOverrides=ids.map(id=>({id,options:getOptions(id)}));
      const remainingLost=before.map((x,i)=>({id:x.id,before:x.options,after:withOverrides[i].options}))
        .filter(x=>x.before.length>=3&&x.after.length<3);
      const restoredTargets=Object.entries(overrides).map(([id,entry])=>({id:Number(id),options:getOptions(id)}));
      const originalStorage='choba_n1uk_storage_v1';
      const oldStorage=localStorage.getItem(originalStorage);
      localStorage.setItem(originalStorage,'v182-diagnostic-sentinel');
      const storageWrite=localStorage.getItem(originalStorage)==='v182-diagnostic-sentinel';
      if(oldStorage===null)localStorage.removeItem(originalStorage);else localStorage.setItem(originalStorage,oldStorage);
      const storageRestored=localStorage.getItem(originalStorage)===oldStorage;
      const overrideRestoredCheck=(()=>{for(const k of Object.keys(REVIEWED_READING_OPTIONS))delete REVIEWED_READING_OPTIONS[k];Object.assign(REVIEWED_READING_OPTIONS,originalOverrides);return JSON.stringify(REVIEWED_READING_OPTIONS)===JSON.stringify(originalOverrides);})();
      VOCAB_POS_BY_ID['255']=originalPos255;
      VOCAB_POS_BY_ID['327']=originalPos327;
      const posRestored=JSON.stringify(VOCAB_POS_BY_ID['255'])===JSON.stringify(originalPos255)&&JSON.stringify(VOCAB_POS_BY_ID['327'])===JSON.stringify(originalPos327);
      const targetIds=[255,327,1819,359];
      const targets=targetIds.map(id=>{
        const item=getVocab(id);
        return {id,word:item.w,reading:item.r,pos:vocabPartOfSpeech(id),before:getOptions(id)};
      });
      return {
        counts:{vocabulary:DEFAULT_VOCAB.length,uniqueVocabIds:new Set(ids).size,grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,lexicalPairs:VOCAB_AUDITED_PAIRS.length,posEntries:Object.keys(VOCAB_POS_BY_ID).length,readingOverrides:Object.keys(REVIEWED_READING_OPTIONS).length},
        posProposal:{"255":["名詞","副詞"],"327":["名詞","ナ形"]},
        changedPoolCount:changed.length,
        changedPools:details,
        lostEligibility:lost,
        gainedEligibility:gained,
        overrideProposal:overrides,
        overrideValidation,
        afterOverrides:restoredTargets,
        remainingLostAfterOverrides:remainingLost,
        targetsBefore:targets,
        progressStorageWrite:storageWrite,
        progressStorageRestored:storageRestored,
        posRestored,
        overrideRestored:overrideRestoredCheck
      };
    },OVERRIDES);
    assert.deepEqual(errors,[],'page errors');
    assert.deepEqual(data.counts,{vocabulary:3914,uniqueVocabIds:3914,grammar:130,lexicalPairs:859,posEntries:3914,readingOverrides:1});
    assert.equal(data.posProposal['255'].join('|'),'名詞|副詞');
    assert.equal(data.posProposal['327'].join('|'),'名詞|ナ形');
    assert.equal(data.overrideValidation.length,3);
    for(const v of data.overrideValidation){
      assert.equal(v.correctMatches,true,'wrong override headword/reading for '+v.id);
      assert.equal(v.threeUniqueWrong,true,'non-unique override options for '+v.id);
      assert.ok(v.wrongSources.every(x=>x.sources.length>=1),'a distractor is not an existing vocabulary reading for '+v.id);
    }
    assert.deepEqual(data.remainingLostAfterOverrides,[],'manual overrides do not restore all previously eligible pools');
    assert.equal(data.progressStorageWrite,true);
    assert.equal(data.progressStorageRestored,true);
    assert.equal(data.posRestored,true);
    assert.equal(data.overrideRestored,true);
    const result={
      pass:true,diagnosticOnly:true,baseVersion:'v181',baseSha256:htmlSha,baseBytes:htmlBytes.length,
      posProposal:data.posProposal,changedPoolCount:data.changedPoolCount,
      lostEligibility:data.lostEligibility,gainedEligibility:data.gainedEligibility,
      overrideValidation:data.overrideValidation,remainingLostAfterOverrides:data.remainingLostAfterOverrides,
      counts:data.counts,data,pageErrors:errors
    };
    fs.mkdirSync('completion/v182-work',{recursive:true});
    fs.writeFileSync('completion/v182-work/diagnostics.json',JSON.stringify(result,null,2)+'\n');
    const tsvRows=[['id','word','reading','pos_after','before_count','before_options','after_count','after_options','after_override_count','decision','note']];
    const lostIds=new Set(data.lostEligibility.map(x=>x.id));
    const gainedIds=new Set(data.gainedEligibility.map(x=>x.id));
    const overrideIds=new Set(Object.keys(OVERRIDES).map(Number));
    for(const p of data.changedPools){
      let decision='automatic_pool_retained';
      let note='Automatic pool retains at least three distinct readings; no override proposed.';
      if(lostIds.has(p.id)){decision='manual_override_proposed';note='Automatic pool falls below three after POS correction; a context-reviewed reading override is proposed.';}
      if(gainedIds.has(p.id)){decision='automatic_pool_gained';note='Pool gains eligibility from the corrected POS of another vocabulary item.';}
      if(overrideIds.has(p.id)){decision='manual_override_proposed';note='Exact override options are source-checked against existing vocabulary readings; author review pending.';}
      const afterOverride=data.afterOverrides.find(x=>x.id===p.id)?.options??p.afterOptions;
      tsvRows.push([p.id,p.word,p.reading,p.pos.join('|'),p.beforeOptions.length,p.beforeOptions.join(' / '),p.afterOptions.length,p.afterOptions.join(' / '),afterOverride.length,decision,note]);
    }
    fs.writeFileSync('completion/v182-work/reading-pool-review.tsv',tsvRows.map(row=>row.map(v=>String(v??'').replace(/\t/g,' ')).join('\t')).join('\n')+'\n');
    const cp=JSON.parse(fs.readFileSync('completion/v182-work/checkpoint.json','utf8'));
    cp.status='diagnostic passed; awaiting manual author acceptance';
    cp.base_html_sha256=htmlSha;
    cp.changed_pool_count=data.changedPoolCount;
    cp.lost_eligibility=data.lostEligibility;
    cp.gained_eligibility=data.gainedEligibility;
    cp.remaining_lost_after_overrides=data.remainingLostAfterOverrides;
    cp.diagnostic_file='completion/v182-work/diagnostics.json';
    fs.writeFileSync('completion/v182-work/checkpoint.json',JSON.stringify(cp,null,2)+'\n');
    console.log(JSON.stringify(result,null,2));
  }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
