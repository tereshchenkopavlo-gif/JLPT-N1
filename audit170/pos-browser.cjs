const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

const base = 'JLPT_N1_ukrainian_reading_v169.html';
const file = 'JLPT_N1_v170_working.html';
const sha256 = require('node:crypto').createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const ids = [3510, 3516, 3527, 3538, 3542, 3546, 3552, 3605, 3611, 3623, 3638, 3645];

async function open(browser, file, width) {
  const page = await browser.newPage({ viewport: { width, height: 915 } });
  await page.goto(pathToFileURL(path.resolve(file)).href);
  return page;
}
async function exercisePools(page) {
  return page.evaluate(ids => {
    const rows = ACTIVE_VOCAB.map(word => {
      const item = { kind: 'v', word, id: word.id };
      const readings = quizReadingOptions(item);
      const cloze = clozeWordCandidates(item).length;
      return { id:word.id, readings, cloze };
    });
    return {
      availability: rows.map(row => [row.id, row.readings.length >= 3, row.cloze >= 3]),
      targets: rows.filter(row => ids.includes(row.id)),
    };
  }, ids);
}
async function run() {
  const browser = await chromium.launch({ headless: true });
  const results = [];
  try {
    const beforePage = await open(browser,base,1280);
    const afterPage = await open(browser,file,1280);
    const before = await exercisePools(beforePage);
    const after = await exercisePools(afterPage);
    assert.equal(before.availability.length,3914);
    assert.deepEqual(after.availability,before.availability);
    await beforePage.close();
    await afterPage.close();

    for (const width of [360,412,1280]) {
      const page = await open(browser,file,width);
      await page.locator('.nav-tab[data-view="cards"]').click();
      const checks = {};
      for (const part of ['名詞','ナ形','動詞']) {
        await page.locator('#cardPos').selectOption(part);
        checks[part] = await page.evaluate(ids => getCardPool().filter(row => row.kind === 'v' && ids.includes(Number(row.id))).map(row=>Number(row.id)),ids);
        assert.deepEqual(checks[part].sort((a,b)=>a-b),part==='動詞'?[]:part==='名詞'?[3510, 3611, 3623, 3638]:ids);
      }
      results.push({width,checks,pass:true});
      await page.close();
    }
    fs.writeFileSync('completion/v170-work/pos-results.json',JSON.stringify({
      sha256, results, checkedVocabulary:3914, sameEligibility:true,
      before:before.targets, after:after.targets,
    },null,2)+'\n');
  } finally {
    await browser.close();
  }
}
run().catch(error => { console.error(error); process.exitCode = 1; });
