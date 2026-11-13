const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const crypto=require('node:crypto');
const path=require('node:path');
const {pathToFileURL}=require('node:url');

const HTML='JLPT_N1_ukrainian_reading_v184.html';
const prepare=JSON.parse(fs.readFileSync('completion/v184-work/prepare-results.json','utf8'));
const bytes=fs.readFileSync(HTML);
const sha=crypto.createHash('sha256').update(bytes).digest('hex');
assert.equal(sha,prepare.candidate_sha256,'candidate SHA differs from deterministic preparation');
assert.equal(prepare.pass,true);
assert.equal(prepare.exact_rollback,true);

const IDS=[485,488,489,491,496,498,499,501,503,504,510,524];
const EXPECTED={
  485:{word:'設ける',translation:'засновувати установу; запроваджувати правило; відводити час або створювати можливість',example:'Створюють консультаційний пункт і уважно вислуховують думки користувачів.'},
  488:{word:'染める',meaning:'染料などを使って色を付ける。また、「手を染める」の形で、ある事に取りかかる。',usage:'Перехідне 一段: 布を藍で染める／髪を赤く染める. Надавати предмету певного кольору. У сталому 悪事に手を染める — почати займатися негідною справою; колір тут не буквальний. Неперехідне 染まる. 彩る ширше — прикрашати кольором чи надавати виразності.'},
  489:{word:'狙う',meaning:'目標や対象を定めてそこを目指す。また、何かを手に入れたり実現したりする機会をうかがう。'},
  491:{word:'訴える',meaning:'裁判所などに申し立てる。また、人々に働きかけて理解や賛同を求める。苦痛や不満を言葉で伝える。感覚や感情に強く働きかける。'},
  496:{word:'担う',example:'Нагальним завданням стало підготувати фахівців, які візьмуть на себе відповідальність за наступне покоління.'},
  498:{word:'断つ',example:'Переглядають коло ділових партнерів, щоб припинити будь-яку причетність до неправомірних дій.'},
  499:{word:'断る',translation:'відмовляти в проханні чи пропозиції; також заздалегідь повідомляти про обставини або просити дозволу'},
  501:{word:'調える'},
  503:{word:'通じる'},
  504:{word:'締める',examples:['Перед початком роботи я міцно затягнув болти, щоб вони не послабилися.','Наприкінці місяця відділ бухгалтерії закриває бухгалтерські книги й звітує перед правлінням.']},
  510:{word:'片付ける',example:'За успішне врегулювання давньої проблеми його підвищили до посади члена правління.'},
  524:{word:'飽きる',example:'Деякі споживачі швидко втрачають інтерес до нових продуктів, тому компанії шукають способи, щоб вони користувалися ними довше.'}
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

    const data=await page.evaluate(ids=>{
      return ids.map(id=>{
        const d=VOCAB_DETAILS_BY_ID[String(id)];
        const item=DEFAULT_VOCAB.find(x=>Number(x.id)===id);
        return {id,word:d.w,pos:VOCAB_POS_BY_ID[String(id)],m:d.m,t:d.t,usage:d.usage,examples:d.examples,translations:d.exampleTranslations};
      });
    },IDS);
    for(const card of data){
      const expected=EXPECTED[card.id];
      assert.equal(card.word,expected.word);
      if(expected.translation)assert.equal(card.t,expected.translation);
      if(expected.meaning)assert.equal(card.m,expected.meaning);
      if(expected.usage)assert.equal(card.usage,expected.usage);
      if(expected.example)assert.ok(card.translations.includes(expected.example));
      if(expected.examples)for(const e of expected.examples)assert.ok(card.translations.includes(e));
      assert.deepEqual(card.pos,['動詞']);
    }

    const rendered=await page.evaluate(async ids=>{
      showView('cards');
      const results=[];
      for(const id of ids){
        await openCardDetail('v',id);
        const body=document.getElementById('cardDetailBody');
        const text=body.innerText;
        const d=VOCAB_DETAILS_BY_ID[String(id)];
        const normalize=value=>String(value).replace(/\\s+/g,' ').trim();
        results.push({
          id,
          word:d.w,
          titleVisible:normalize(text).includes(normalize(d.w)),
          translationVisible:normalize(text).includes(normalize(d.t)),
          examplesVisible:d.exampleTranslations.every(t=>normalize(text).includes(normalize(t))),
          bodyTextLength:text.length
        });
      }
      return results;
    },IDS);
    assert.equal(rendered.length,12);
    process.stdout.write('RENDERED CARD CHECK '+JSON.stringify(rendered)+'\\n');
    assert.equal(rendered.every(x=>x.titleVisible&&x.translationVisible&&x.examplesVisible),true,'one or more reviewed cards did not render all translations');

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
      const sentinel=JSON.stringify({meta:{sessionSize:10,streak:4,lastStudyDate:'2026-11-13'},vp:{'485':{status:'S',timesShown:3}},gp:{'90':{status:'X'}}});
      localStorage.setItem(key,sentinel);
      const roundTrip=localStorage.getItem(key)===sentinel;
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
      reviewed_card_count:rendered.length,
      reviewed_cards:rendered,
      responsive,
      storage,
      pageErrors:errors
    };
    fs.writeFileSync('completion/v184-work/browser-results.json',JSON.stringify(result,null,2)+'\n');
    process.stdout.write(JSON.stringify(result,null,2)+'\n');
  }finally{
    await browser.close();
  }
}
main().catch(e=>{console.error(e);process.exit(1);});
