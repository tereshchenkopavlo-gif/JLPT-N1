const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const file = 'JLPT_N1_v164_working.html';
const sha256 = require('node:crypto').createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const baseline = JSON.parse(fs.readFileSync('completion/v163-pos-reading-diagnostic.json','utf8')).isolated['3076'];

async function run() {
  const browser = await chromium.launch({ headless: true });
  const results = [];
  try {
    for (const width of [360,412,1280]) {
      const page = await browser.newPage({ viewport: { width, height: 915 } });
      await page.goto(pathToFileURL(path.resolve(file)).href);
      await page.locator('.nav-tab[data-view="cards"]').click();
      const searches = {};
      for (const query of ['堪能','たんのう','かんのう','たんのうな']) {
        await page.locator('#cardSearch').fill(query);
        searches[query] = await page.evaluate(() => getCardPool().some(item => item.kind === 'v' && String(item.id) === '3076'));
        assert.equal(searches[query], query !== 'たんのうな');
      }
      const exercise = await page.evaluate(() => {
        const word = ACTIVE_VOCAB.find(row => row.id === 3076);
        const item = {kind:'v',word,id:3076};
        return { reading:word.r, pos:vocabPartOfSpeech(3076), readingChoices:quizReadingOptions(item), clozePool:clozeWordCandidates(item).length };
      });
      assert.deepEqual(exercise, baseline);
      results.push({width,searches,exercise,pass:true});
      await page.close();
    }
  } finally {
    await browser.close();
  }
  fs.writeFileSync('completion/v164-work/reading-results.json',JSON.stringify({sha256,results},null,2)+'\n');
}
run().catch(error => { console.error(error); process.exitCode = 1; });
