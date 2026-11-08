const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { createHash } = require('node:crypto');
const { pathToFileURL } = require('node:url');

const file = 'JLPT_N1_v157_working.html';
const sha256 = createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const review = JSON.parse(fs.readFileSync('completion/v157-work/editorial-review.json', 'utf8'));
assert.equal(review.sha256, sha256);

async function run() {
  const browser = await chromium.launch({ headless: true });
  const results = [];
  try {
    for (const width of [360, 412, 1280]) {
      const page = await browser.newPage({ viewport: { width, height: 915 } });
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto(pathToFileURL(path.resolve(file)).href);
      for (const row of review.rows) {
        await page.evaluate(id => {
          showView('cards');
          openCardDetail('v', id);
        }, row.key);
        await page.waitForFunction(id => document.getElementById('cardDetailBody').dataset.currentKey === 'v_' + id, row.key);
        const checks = await page.evaluate(({ key, reading, partsOfSpeech, word }) => {
          const body = document.getElementById('cardDetailBody');
          const card = VOCAB_DETAILS_BY_ID[key];
          const normalize = value => value.replace(/\s/g, '');
          const includes = (selector, value) => normalize(body.querySelector(selector)?.textContent || '').includes(normalize(value));
          return {
            headword: includes('.fc-word', word),
            reading: body.querySelector('.fc-reading')?.textContent.trim() === reading,
            partsOfSpeech: partsOfSpeech.every(part => includes('.word-pos', part)),
            definition: includes('.fc-meaning', card.m),
            meaning: includes('.fc-trans', card.t),
            usage: [...body.querySelectorAll('.fc-section-label')].some(label => label.textContent === '用法・接続')
              && includes('.fc-trans + .fc-section-label + .fc-trans', displayUsageText(card.usage, 'v')),
            examples: card.examples.every(value => includes('.fc-examples', value)),
            translations: card.exampleTranslations.every(value => includes('.fc-examples', value)),
            viewport: document.documentElement.scrollWidth <= innerWidth + 1,
          };
        }, row);
        assert(Object.values(checks).every(Boolean), JSON.stringify({ id: row.key, width, checks }));
        results.push({ id: Number(row.key), width, pass: true, ...checks });
      }
      assert.deepEqual(errors, []);
      await page.close();
    }
    fs.writeFileSync('completion/v157-work/vocab-results.json', JSON.stringify({ sha256, pass: true, results }, null, 2)+'\n');
    console.log('PASS '+review.rows.length+' vocabulary cards at three widths');
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
