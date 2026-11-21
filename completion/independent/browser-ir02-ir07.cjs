const fs = require("node:fs");
const assert = require("node:assert/strict");
const {chromium} = require("playwright");
const directory = "completion/independent/adjudications/20261121";

(async () => {
  const html = fs.readFileSync(directory + "/candidate_UNACCEPTED.html", "utf8");
  const declaration = html.slice(html.indexOf("const readingBank")).split("\n")[0];
  const bank = JSON.parse(declaration.slice(declaration.indexOf("=")+1).trim().replace(/;$/,""));
  const fields = JSON.parse(fs.readFileSync(directory + "/reviewed-materials.json"));
  const rows = Object.values(fields).filter(row => row.id && row.ja);
  assert.equal(rows.length, 14);
  const browser = await chromium.launch({headless:true});
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror",error => errors.push(error.message));
    await page.route("http://review.test/",route => route.fulfill({contentType:"text/html",body:html}));
    await page.goto("http://review.test/");
    const cases = [];
    for (const width of [360,412,1280]) {
      await page.setViewportSize({width,height:900});
      for (const row of rows) {
        const level = row.id.startsWith("l-") ? "long" : "medium";
        const index = bank[level].findIndex(item => item.id === row.id);
        assert.ok(index >= 0);
        const generated = await page.evaluate(({row,level,index,total}) => {
          const random = Math.random;
          let passages;
          try {
            Math.random = () => (index + 0.5) / total;
            passages = SmartEngine.generateOfflinePassage([]);
          } finally {
            Math.random = random;
          }
          const passage = passages.find(p => p.level === level);
          curSession = {items:[],passageIdx:0,passages:[passage]};
          showView("session");
          document.getElementById("sessBody").style.display = "";
          renderPassage();
          return passage;
        },{row,level,index,total:bank[level].length});
        assert.equal(generated.title,row.title);
        assert.equal(generated.plainText,row.ja);
        assert.equal(generated.translation,row.uk);
        assert.equal(generated.glossary.length,row.contextNotes.length);
        assert.equal(generated.questions.length,row.questions.length);
        for (let i=0; i<row.questions.length; i++) {
          const q=generated.questions[i];
          assert.equal(q.choices[q.answer],row.questions[i].choices[row.questions[i].answer]);
          assert.deepEqual([...q.choices].sort(),[...row.questions[i].choices].sort());
          await page.locator('.qchoice[data-qi="'+i+'"][data-ci="'+q.answer+'"]').click();
          assert.equal(await page.locator("#exp-"+i).innerText(),row.questions[i].explain);
        }
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth>innerWidth+1),false);
        cases.push({id:row.id,width,questions:row.questions.length});
      }
    }
    const cards = await page.evaluate(async () => {
      const out=[];
      for (const id of [3375,3417]) {
        await openCardDetail("v",id);
        const text=document.getElementById("cardDetail").innerText;
        const details=VOCAB_DETAILS_BY_ID[String(id)];
        out.push({id,gloss:text.includes(details.t),
                  translations:details.exampleTranslations.every(s=>text.includes(s))});
      }
      return out;
    });
    assert.ok(cards.every(c=>c.gloss&&c.translations));
    assert.deepEqual(errors,[]);
    fs.writeFileSync(directory+"/browser-results.json",JSON.stringify({pass:true,cases,cards,pageErrors:errors},null,2));
  } finally {
    await browser.close();
  }
})().catch(error => {console.error(error);process.exit(1);});
