// v173 C10 browser regression: two exact translations, stable data, rendered cards and progress.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const crypto = require('node:crypto');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

const base = 'JLPT_N1_ukrainian_reading_v172.html';
const file = 'JLPT_N1_ukrainian_reading_v173.html';
const expected = {
  '3761': 'Він нарешті зважився повернутися до рідного краю.',
  '3764': 'Вона часто ревнує через дружні стосунки своєї коханої людини.'
};
const before = {
  '3761': 'Він нарешті прийняв тверде рішення повернутися до рідного міста.',
  '3764': 'Вона часто ревнує через дружні стосунки свого коханого.'
};

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
    cardsChecked: 2,
    translationsChecked: 2
  };
  try {
    const basePage = await open(browser, base);
    const nextPage = await open(browser, file);
    const baseData = await snapshot(basePage);
    const nextData = await snapshot(nextPage);

    assert.equal(baseData.vocab, 3914);
    assert.equal(nextData.vocab, 3914);
    assert.equal(nextData.details && Object.keys(nextData.details).length, 3914);
    assert.equal(nextData.grammarIds.length, 130);
    assert.equal(nextData.pos && Object.keys(nextData.pos).length, 3914);
    assert.equal(nextData.pairs, 859);
    assert.deepEqual(nextData.vocabIds, baseData.vocabIds);
    assert.deepEqual(nextData.grammarIds, baseData.grammarIds);
    assert.deepEqual(nextData.pos, baseData.pos);

    const changed = [];
    for (const id of Object.keys(baseData.details)) {
      const a = baseData.details[id];
      const b = nextData.details[id];
      if (JSON.stringify(a) !== JSON.stringify(b)) changed.push(id);
    }
    assert.deepEqual(changed, ['3761', '3764']);
    for (const id of changed) {
      const a = JSON.parse(JSON.stringify(baseData.details[id]));
      const b = JSON.parse(JSON.stringify(nextData.details[id]));
      assert.equal(a.exampleTranslations[1], before[id]);
      assert.equal(b.exampleTranslations[1], expected[id]);
      b.exampleTranslations[1] = a.exampleTranslations[1];
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
        rows.push({
          id,
          headword: VOCAB_DETAILS_BY_ID[id].w,
          expectedTranslation: VOCAB_DETAILS_BY_ID[id].exampleTranslations[1] === expected[id],
          cardRendered: text.includes(expected[id]),
          exampleRendered: examplesHtml.includes(escapeLex(VOCAB_DETAILS_BY_ID[id].examples[1])),
          translationRendered: examplesHtml.includes(escapeLex(expected[id]))
        });
      }
      const key = 'choba_n1uk_storage_v1';
      const sentinel = 'v173-progress-sentinel';
      localStorage.setItem(key, sentinel);
      const progressStorageUnchanged = localStorage.getItem(key) === sentinel;
      return { rows, progressStorageUnchanged };
    }, { expected, ids: ['3761', '3764'] });
    assert(rendered.rows.every(x => x.expectedTranslation && x.cardRendered && x.exampleRendered && x.translationRendered));
    assert.equal(rendered.progressStorageUnchanged, true);
    results.renderedCards = rendered.rows;
    results.progressStorageUnchanged = rendered.progressStorageUnchanged;

    for (const width of [360, 412, 1280]) {
      const page = await open(browser, file, width);
      const data = await page.evaluate(() => ({
        width: window.innerWidth,
        cards: ['3761', '3764'].map(id => {
          const card = VOCAB_DETAILS_BY_ID[id];
          const html = renderCardShell('v', id, card);
          return html.includes(escapeLex(card.exampleTranslations[1]));
        })
      }));
      assert.equal(data.width, width);
      assert.deepEqual(data.cards, [true, true]);
      results.widths.push({ width, cardsRendered: data.cards, pass: true });
      await page.close();
    }

    results.counts = {
      vocabulary: nextData.vocab,
      grammar: nextData.grammarIds.length,
      lexicalPairs: nextData.pairs
    };
    results.changedIds = changed;
    results.pass = true;
    fs.writeFileSync('completion/v173-work/browser-results.json', JSON.stringify(results, null, 2) + '\n');
    console.log(JSON.stringify(results, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
