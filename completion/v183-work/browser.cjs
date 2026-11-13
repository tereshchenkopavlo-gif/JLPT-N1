const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const crypto=require('node:crypto');
const path=require('node:path');
const {pathToFileURL}=require('node:url');

const HTML='JLPT_N1_ukrainian_reading_v183.html';
const prepare=JSON.parse(fs.readFileSync('completion/v183-work/prepare-results.json','utf8'));
const bytes=fs.readFileSync(HTML);
const sha=crypto.createHash('sha256').update(bytes).digest('hex');
assert.equal(sha,prepare.candidate_sha256,'candidate SHA differs from deterministic preparation');
assert.equal(prepare.pass,true);
assert.equal(prepare.exact_rollback,true);

const IDS=[454,455,458,459,461,464,466,470,472,477,479,483];
const EXPECTED={
  454:{word:'向く',translation:'бути спрямованим у певний бік; пасувати людині; бути придатним для певної роботи чи справи'},
  466:{word:'従う',translation:'Зі зміною обставин підхід до реагування гнучко коригуватимуть.'},
  472:{word:'触れる',translation:'Завдяки безпосередньому знайомству з твором вдалося відкрити для себе щось нове.'},
  477:{word:'親しむ',translation:'зближуватися з кимось; часто й невимушено звертатися до чогось, відчуваючи близькість або прихильність (читання, природа, культура)'},
  479:{word:'震わせる',translation:'змушувати голос, плечі чи тіло тремтіти; глибоко зворушувати (心を震わせる)'}
};

async function main(){
  const browser=await chromium.launch({headless:true});
  try{
    const page=await browser.newPage({viewport:{width:412,height:900}});
    const errors=[];
    page.on('pageerror',e=>errors.push(String(e)));
    await page.goto(pathToFileURL(path.resolve(HTML)).href);
    const structural=await page.evaluate(()=>{
      const ids=DEFAULT_VOCAB.map(x=>Number(x.id));
      return {
        vocab:DEFAULT_VOCAB.length,
        grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,
        pairs:VOCAB_AUDITED_PAIRS.length,
        uniqueIds:new Set(ids).size,
        allIdsPresent:ids.every(id=>VOCAB_DETAILS_BY_ID[String(id)]&&VOCAB_POS_BY_ID[String(id)])
      };
    });
    assert.deepEqual(structural,{vocab:3914,grammar:130,pairs:859,uniqueIds:3914,allIdsPresent:true});

    const cardResults=await page.evaluate(async ids=>{
      showView('cards');
      const results=[];
      for(const id of ids){
        await openCardDetail('v',id);
        const body=document.getElementById('cardDetailBody');
        const item=DEFAULT_VOCAB.find(x=>Number(x.id)===id);
        const detail=VOCAB_DETAILS_BY_ID[String(id)];
        const rendered=body.innerText;
        results.push({
          id,
          word:item.w,
          titleVisible:rendered.includes(item.w),
          translationVisible:rendered.includes(detail.t),
          examplesVisible:detail.exampleTranslations.every(t=>rendered.includes(t)),
          bodyTextLength:rendered.length
        });
      }
      return results;
    },IDS);
    assert.equal(cardResults.length,12);
    assert.equal(cardResults.every(x=>x.titleVisible&&x.translationVisible&&x.examplesVisible),true,'one or more reviewed cards did not render all translations');

    const targeted=await page.evaluate(expected=>{
      return Object.entries(expected).map(([id,e])=>{
        const d=VOCAB_DETAILS_BY_ID[id];
        return {id:Number(id),word:d.w,translation:d.t,examples:d.exampleTranslations};
      });
    },EXPECTED);
    for(const item of targeted){
      const e=EXPECTED[item.id];
      assert.equal(item.word,e.word);
      if([466,472].includes(item.id)) assert.ok(item.examples.includes(e.translation));
      else assert.equal(item.translation,e.translation);
    }

    const responsive=[];
    for(const width of [360,412,1280]){
      await page.setViewportSize({width,height:900});
      await page.evaluate(()=>window.scrollTo(0,0));
      const dims=await page.evaluate(()=>({width:window.innerWidth,scrollWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth}));
      responsive.push({...dims,overflow:dims.scrollWidth>width||dims.bodyWidth>width});
    }
    assert.equal(responsive.every(x=>!x.overflow),true,'horizontal overflow detected');

    const storage=await page.evaluate(()=>{
      const key='choba_n1uk_storage_v1';
      const old=localStorage.getItem(key);
      localStorage.setItem(key,'v183-progress-sentinel');
      const roundTrip=localStorage.getItem(key)==='v183-progress-sentinel';
      if(old===null)localStorage.removeItem(key);else localStorage.setItem(key,old);
      return {roundTrip,restored:localStorage.getItem(key)===old};
    });
    assert.equal(storage.roundTrip,true);
    assert.equal(storage.restored,true);
    assert.deepEqual(errors,[],'page errors detected');

    const result={
      pass:true,
      candidate_sha256:sha,
      candidate_bytes:bytes.length,
      counts:structural,
      reviewed_card_count:cardResults.length,
      reviewed_cards:cardResults,
      responsive,
      storage,
      pageErrors:errors
    };
    fs.writeFileSync('completion/v183-work/browser-results.json',JSON.stringify(result,null,2)+'\n');
    process.stdout.write(JSON.stringify(result,null,2)+'\n');
  }finally{
    await browser.close();
  }
}
main().catch(e=>{console.error(e);process.exit(1);});
