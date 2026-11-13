const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const crypto=require('node:crypto');
const path=require('node:path');
const {pathToFileURL}=require('node:url');

const HTML='JLPT_N1_ukrainian_reading_v182.html';
const PREP='completion/v182-work/prepare-results.json';
const DIAG='completion/v182-work/diagnostics.json';
const EXPECTED={
  "255":{word:"直接",correct:"ちょくせつ",wrong:["ちょうせつ","ちょうせい","ちくせき"],pos:["名詞","副詞"]},
  "327":{word:"浮気",correct:"うわき",wrong:["いしき","いせき","うつわ"],pos:["名詞","ナ形"]},
  "1819":{word:"内訳",correct:"うちわけ",wrong:["うちがわ","うつわ","うわき"],pos:["名詞"]},
  "359":{word:"本気",correct:"ほんき",pos:["名詞","ナ形"]}
};

async function main(){
  const htmlBytes=fs.readFileSync(HTML);
  const sha=crypto.createHash('sha256').update(htmlBytes).digest('hex');
  const prep=JSON.parse(fs.readFileSync(PREP,'utf8'));
  const diag=JSON.parse(fs.readFileSync(DIAG,'utf8'));
  assert.equal(sha,prep.candidate_sha256,'candidate SHA mismatch');
  assert.equal(prep.candidate_version,'v182');
  assert.equal(prep.exact_rollback,true);
  assert.equal(prep.vocabulary_records,3914);
  assert.equal(prep.grammar_records,130);
  assert.equal(prep.lexical_pairs,859);
  assert.deepEqual(diag.remainingLostAfterOverrides,[]);
  assert.equal(diag.changedPoolCount,23);
  assert.equal(diag.lostEligibility.length,3);
  assert.equal(diag.gainedEligibility.length,1);
  const browser=await chromium.launch({headless:true});
  try{
    const page=await browser.newPage({viewport:{width:1280,height:900}});
    const errors=[];
    page.on('pageerror',e=>errors.push(String(e)));
    await page.goto(pathToFileURL(path.resolve(HTML)).href);
    const data=await page.evaluate(expected=>{
      const ids=[255,327,1819,359];
      const records=Object.fromEntries(ids.map(id=>[id,DEFAULT_VOCAB.find(x=>Number(x.id)===id)]));
      const details=Object.fromEntries(ids.map(id=>[id,VOCAB_DETAILS_BY_ID[String(id)]]));
      const quiz=Object.fromEntries([255,327,1819].map(id=>{
        const item=records[id];
        return [id,{word:item.w,reading:item.r,pos:vocabPartOfSpeech(id),wrong:quizReadingOptions({kind:'v',id,word:item})}];
      }));
      const storageKey='choba_n1uk_storage_v1';
      const old=localStorage.getItem(storageKey);
      localStorage.setItem(storageKey,'v182-progress-sentinel');
      const write=localStorage.getItem(storageKey)==='v182-progress-sentinel';
      if(old===null)localStorage.removeItem(storageKey);else localStorage.setItem(storageKey,old);
      return {
        counts:{vocabulary:DEFAULT_VOCAB.length,uniqueVocabIds:new Set(DEFAULT_VOCAB.map(x=>String(x.id))).size,grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,lexicalPairs:VOCAB_AUDITED_PAIRS.length,posEntries:Object.keys(VOCAB_POS_BY_ID).length,readingOverrides:Object.keys(REVIEWED_READING_OPTIONS).length},
        pos:Object.fromEntries(ids.map(id=>[id,vocabPartOfSpeech(id)])),
        quiz,details,storageWrite:write,storageRestored:localStorage.getItem(storageKey)===old
      };
    },EXPECTED);
    assert.deepEqual(errors,[],'page errors');
    assert.deepEqual(data.counts,{vocabulary:3914,uniqueVocabIds:3914,grammar:130,lexicalPairs:859,posEntries:3914,readingOverrides:4});
    for(const id of [255,327,1819,359])assert.deepEqual(data.pos[id],EXPECTED[id].pos,'POS mismatch '+id);
    for(const id of [255,327,1819]){
      assert.equal(data.quiz[id].word,EXPECTED[id].word);
      assert.equal(data.quiz[id].reading,EXPECTED[id].correct);
      assert.deepEqual(data.quiz[id].wrong,EXPECTED[id].wrong,'reading override mismatch '+id);
      assert.equal(new Set([data.quiz[id].reading,...data.quiz[id].wrong]).size,4,'duplicate reading option '+id);
      assert.ok(data.quiz[id].wrong.every(r=>DEFAULT_VOCAB.some(x=>x.r===r&&Number(x.id)!==id)),'unverified reading distractor '+id);
    }
    assert.deepEqual(data.details[255].examples,[
      '詳細については、担当者に直接お問い合わせください。',
      '問題の直接の原因は、操作ミスにあった。'
    ]);
    assert.deepEqual(data.details[327].examples,[
      '浮気が原因で、夫婦関係が破綻した。',
      '浮気を疑われ、信頼を取り戻すのに長い時間を要した。'
    ]);
    assert.equal(data.storageWrite,true);
    assert.equal(data.storageRestored,true);
    const widths=[360,412,1280],layout=[];
    for(const width of widths){
      await page.setViewportSize({width,height:900});
      layout.push(await page.evaluate(()=>({width:innerWidth,documentWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth})));
    }
    assert.ok(layout.every(x=>x.documentWidth<=x.width+1&&x.bodyWidth<=x.width+1),'horizontal overflow');
    assert.deepEqual(errors,[],'page errors after resize');
    const result={
      pass:true,version:'v182',sha256:sha,bytes:htmlBytes.length,
      counts:data.counts,pos:data.pos,quiz:data.quiz,
      changedPools:diag.changedPoolCount,lostEligibility:diag.lostEligibility.length,
      gainedEligibility:diag.gainedEligibility.length,remainingLostAfterOverrides:diag.remainingLostAfterOverrides,
      progressStorageWrite:data.storageWrite,progressStorageRestored:data.storageRestored,
      widths:layout,pageErrors:errors,
      scope:'author regression only; not independent or physical acceptance'
    };
    fs.writeFileSync('completion/v182-work/browser-results.json',JSON.stringify(result,null,2)+'\n');
    console.log(JSON.stringify(result,null,2));
  }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
