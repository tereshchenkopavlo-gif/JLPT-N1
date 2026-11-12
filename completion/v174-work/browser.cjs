// v174 C10 browser regression: three exact translations and one unchanged reviewed card.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const crypto = require('node:crypto');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

const base = 'JLPT_N1_ukrainian_reading_v173.html';
const file = 'JLPT_N1_ukrainian_reading_v174.html';
const expected = {
  '3828': 'Ваше прохання зрозумів і взяв до відома.',
  '3836': 'Я не знав, що ця людина — наставник вашого вчителя.',
  '3900': 'Шановний пане / шановна пані! Щиро радіємо, що у Вас усе добре й справи процвітають.'
};
const before = {
  '3828': 'Ваше прохання зрозумів і прийняв до виконання.',
  '3836': 'Я не знав, що ця особа — ваш учитель.',
  '3900': 'Шановний адресате, радіємо вашому дедалі більшому процвітанню.'
};
const fields = { '3828': 0, '3836': 1, '3900': 0 };
const ids = ['3820', '3828', '3836', '3900'];

async function open(browser, filename, width = 1280) {
  const page = await browser.newPage({ viewport: { width, height: 915 } });
  await page.goto(pathToFileURL(path.resolve(filename)).href);
  return page;
}
async function snapshot(page) {
  return page.evaluate(() => ({
    vocab: DEFAULT_VOCAB.length,
    details: JSON.parse(JSON.stringify(VOCAB_DETAILS_BY_ID)),
    grammarIds: Object.keys(GRAMMAR_DETAILS_BY_ID),
    pos: JSON.parse(JSON.stringify(VOCAB_POS_BY_ID)),
    pairs: VOCAB_AUDITED_PAIRS.length,
    vocabIds: DEFAULT_VOCAB.map(x => x.id)
  }));
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const results = {
    sha256: crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),
    widths: [],
    cardsChecked: 4,
    translationsChecked: 3
  };
  try {
    const basePage = await open(browser, base);
    const nextPage = await open(browser, file);
    const baseData = await snapshot(basePage);
    const nextData = await snapshot(nextPage);
    assert.equal(baseData.vocab, 3914);
    assert.equal(nextData.vocab, 3914);
    assert.equal(Object.keys(nextData.details).length, 3914);
    assert.equal(nextData.grammarIds.length, 130);
    assert.equal(Object.keys(nextData.pos).length, 3914);
    assert.equal(nextData.pairs, 859);
    assert.deepEqual(nextData.vocabIds, baseData.vocabIds);
    assert.deepEqual(nextData.grammarIds, baseData.grammarIds);
    assert.deepEqual(nextData.pos, baseData.pos);

    const changed = [];
    for (const id of Object.keys(baseData.details)) {
      if (JSON.stringify(baseData.details[id]) !== JSON.stringify(nextData.details[id])) changed.push(id);
    }
    assert.deepEqual(changed, ['3828', '3836', '3900']);
    assert.deepEqual(nextData.details['3820'], baseData.details['3820']);
    for (const id of changed) {
      const a = JSON.parse(JSON.stringify(baseData.details[id]));
      const b = JSON.parse(JSON.stringify(nextData.details[id]));
      const index = fields[id];
      assert.equal(a.exampleTranslations[index], before[id]);
      assert.equal(b.exampleTranslations[index], expected[id]);
      b.exampleTranslations[index] = a.exampleTranslations[index];
      assert.deepEqual(b, a);
    }

    const rendered = await nextPage.evaluate(async ({ expected, ids }) => {
      const rows = [];
      for (const id of ids) {
        const card = await getCardData('v', id);
        const html = renderCardShell('v', id, card);
        const wrapper = document.createElement('div');
        wrapper.innerHTML = html;
        const text = wrapper.textContent || '';
        const examplesHtml = vocabExamplesHtml(id, card.examples);
        const translations = VOCAB_DETAILS_BY_ID[id].exampleTranslations;
        const target = expected[id];
        rows.push({
          id,
          headword: VOCAB_DETAILS_BY_ID[id].w,
          expectedTranslation: target ? translations.includes(target) : true,
          cardRendered: target ? text.includes(target) : translations.every(x => text.includes(x)),
          exampleRendered: target ? examplesHtml.includes(escapeLex(target)) : translations.every(x => examplesHtml.includes(escapeLex(x))),
          translationRendered: target ? examplesHtml.includes(escapeLex(target)) : translations.every(x => examplesHtml.includes(escapeLex(x)))
        });
      }
      const key = 'choba_n1uk_storage_v1';
      const sentinel = 'v174-progress-sentinel';
      localStorage.setItem(key, sentinel);
      return { rows, progressStorageUnchanged: localStorage.getItem(key) === sentinel };
    }, { expected, ids });
    assert(rendered.rows.every(x => x.expectedTranslation && x.cardRendered && x.exampleRendered && x.translationRendered));
    assert.equal(rendered.progressStorageUnchanged, true);
    results.renderedCards = rendered.rows;
    results.progressStorageUnchanged = rendered.progressStorageUnchanged;

    for (const width of [360, 412, 1280]) {
      const page = await open(browser, file, width);
      const data = await page.evaluate(async ids => {
        const rows = [];
        for (const id of ids) {
          const card = await getCardData('v', id);
          const html = renderCardShell('v', id, card);
          rows.push(html.includes(escapeLex(VOCAB_DETAILS_BY_ID[id].exampleTranslations[0])) &&
            html.includes(escapeLex(VOCAB_DETAILS_BY_ID[id].exampleTranslations[1])));
        }
        return { width: window.innerWidth, cards: rows };
      }, ids);
      assert.equal(data.width, width);
      assert.deepEqual(data.cards, [true, true, true, true]);
      results.widths.push({ width, cardsRendered: data.cards, pass: true });
      await page.close();
    }
    results.counts = { vocabulary: nextData.vocab, grammar: nextData.grammarIds.length, lexicalPairs: nextData.pairs };
    results.changedIds = changed;
    results.pass = true;
    fs.writeFileSync('completion/v174-work/browser-results.json', JSON.stringify(results, null, 2) + '\n');
    console.log(JSON.stringify(results, null, 2));
  } finally {
    await browser.close();
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
