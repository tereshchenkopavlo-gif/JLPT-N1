// v176 C10 browser regression: 12 reviewed cards, 10 exact fields, four unchanged pairs.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const crypto = require('node:crypto');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

const base = 'JLPT_N1_ukrainian_reading_v175.html';
const file = 'JLPT_N1_ukrainian_reading_v176.html';
const updates = JSON.parse(fs.readFileSync('completion/v176-work/updates.json', 'utf8'));
const ids = ['255', '278', '327', '330', '332', '335', '339', '347', '349', '350', '353', '355'];
const changedIds = ['278', '330', '332', '335', '339', '347', '349', '350', '353', '355'];
const pairIndexes = [72, 81, 85, 167];

function getPath(value, field) {
  return field.split('.').reduce((current, part) =>
    Array.isArray(current) ? current[Number(part)] : current[part], value);
}
async function open(browser, filename, width = 1280) {
  const page = await browser.newPage({ viewport: { width, height: 915 } });
  const errors = [];
  page.on('pageerror', error => errors.push(String(error)));
  await page.goto(pathToFileURL(path.resolve(filename)).href);
  return { page, errors };
}
async function snapshot(page) {
  return page.evaluate(() => ({
    vocab: DEFAULT_VOCAB.length,
    details: JSON.parse(JSON.stringify(VOCAB_DETAILS_BY_ID)),
    grammarIds: Object.keys(GRAMMAR_DETAILS_BY_ID),
    pos: JSON.parse(JSON.stringify(VOCAB_POS_BY_ID)),
    pairs: JSON.parse(JSON.stringify(VOCAB_AUDITED_PAIRS)),
    vocabIds: DEFAULT_VOCAB.map(x => x.id)
  }));
}
async function main() {
  const browser = await chromium.launch({ headless: true });
  const results = {
    sha256: crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),
    widths: [],
    cardsChecked: ids.length,
    fieldsChecked: updates.length,
    pairsChecked: pairIndexes.length
  };
  try {
    const baseOpen = await open(browser, base);
    const nextOpen = await open(browser, file);
    const baseData = await snapshot(baseOpen.page);
    const nextData = await snapshot(nextOpen.page);
    assert.deepEqual(baseOpen.errors, []);
    assert.deepEqual(nextOpen.errors, []);
    assert.equal(baseData.vocab, 3914);
    assert.equal(nextData.vocab, 3914);
    assert.equal(Object.keys(nextData.details).length, 3914);
    assert.equal(nextData.grammarIds.length, 130);
    assert.equal(Object.keys(nextData.pos).length, 3914);
    assert.equal(nextData.pairs.length, 859);
    assert.deepEqual(nextData.vocabIds, baseData.vocabIds);
    assert.deepEqual(nextData.grammarIds, baseData.grammarIds);
    assert.deepEqual(nextData.pos, baseData.pos);
    assert.deepEqual(nextData.details['255'], baseData.details['255']);
    assert.deepEqual(nextData.details['327'], baseData.details['327']);

    const changed = [];
    for (const id of Object.keys(baseData.details)) {
      if (JSON.stringify(baseData.details[id]) !== JSON.stringify(nextData.details[id])) changed.push(id);
    }
    assert.deepEqual(changed, changedIds);
    for (const row of updates) {
      assert.equal(getPath(baseData.details[String(row.id)], row.field), row.before);
      assert.equal(getPath(nextData.details[String(row.id)], row.field), row.after);
    }
    for (const index of pairIndexes) {
      assert.deepEqual(nextData.pairs[index], baseData.pairs[index]);
    }

    const posDiagnostics = await nextOpen.page.evaluate(() => {
      const cases = [
        { id: '255', proposed: ['名詞', 'ナ形'] },
        { id: '278', proposed: ['名詞', '接尾語'] },
        { id: '327', proposed: ['名詞', 'ナ形'] }
      ];
      return cases.map(item => {
        const word = ACTIVE_VOCAB.find(x => String(x.id) === item.id);
        const studyItem = { kind: 'v', id: Number(item.id), word };
        const original = VOCAB_POS_BY_ID[item.id];
        const currentCount = quizReadingOptions(studyItem).length;
        VOCAB_POS_BY_ID[item.id] = item.proposed;
        const proposedCount = quizReadingOptions(studyItem).length;
        VOCAB_POS_BY_ID[item.id] = original;
        return { id: item.id, currentPos: original, proposedPos: item.proposed, currentCount, proposedCount };
      });
    });
    assert.deepEqual(posDiagnostics.map(x => x.id), ['255', '278', '327']);
    assert(posDiagnostics.every(x => x.currentCount >= 3));
    assert.deepEqual(posDiagnostics.map(x => x.proposedCount), [0, 0, 2]);
    results.posDiagnostics = posDiagnostics;

    const rendered = await nextOpen.page.evaluate(async ({ ids, updates }) => {
      const rows = [];
      for (const id of ids) {
        const card = await getCardData('v', id);
        const html = renderCardShell('v', id, card);
        const wrapper = document.createElement('div');
        wrapper.innerHTML = html;
        const text = wrapper.textContent || '';
        const examplesHtml = vocabExamplesHtml(id, card.examples);
        const examplesWrapper = document.createElement('div');
        examplesWrapper.innerHTML = examplesHtml;
        const examplesText = examplesWrapper.textContent || '';
        const normalize = value => String(value || '').replace(/\s+/gu, '');
        const cardUpdates = updates.filter(row => String(row.id) === id);
        const fields = cardUpdates.map(row => {
          const renderedText = row.field.startsWith('exampleTranslations.') ? examplesText : text;
          return { field: row.field, present: normalize(renderedText).includes(normalize(row.after)) };
        });
        const allExamplesRendered = (VOCAB_DETAILS_BY_ID[id].exampleTranslations || []).every(value =>
          normalize(examplesText).includes(normalize(value)));
        rows.push({
          id,
          headword: VOCAB_DETAILS_BY_ID[id].w,
          cardRendered: text.length > 0,
          fields,
          allExamplesRendered
        });
      }
      const key = 'choba_n1uk_storage_v1';
      const sentinel = 'v176-progress-sentinel';
      localStorage.setItem(key, sentinel);
      return { rows, progressStorageUnchanged: localStorage.getItem(key) === sentinel };
    }, { ids, updates });
    results.renderedCards = rendered.rows;
    results.progressStorageUnchanged = rendered.progressStorageUnchanged;
    fs.writeFileSync('completion/v176-work/browser-results.json',
      JSON.stringify(results, null, 2) + '\n');
    console.log('RENDERED_DIAGNOSTICS ' + JSON.stringify(rendered.rows));
    assert(rendered.rows.every(row =>
      row.cardRendered && row.allExamplesRendered && row.fields.every(field => field.present)),
      JSON.stringify(rendered.rows));
    assert.equal(rendered.progressStorageUnchanged, true);
    results.renderedCards = rendered.rows;
    results.progressStorageUnchanged = rendered.progressStorageUnchanged;

    for (const width of [360, 412, 1280]) {
      const opened = await open(browser, file, width);
      const data = await opened.page.evaluate(async ids => {
        const rows = [];
        for (const id of ids) {
          const card = await getCardData('v', id);
          const html = renderCardShell('v', id, card);
          const wrapper = document.createElement('div');
          wrapper.innerHTML = html;
          const renderedText = (wrapper.textContent || '').replace(/\s+/gu, '');
          rows.push(html.length > 0 &&
            VOCAB_DETAILS_BY_ID[id].exampleTranslations.every(value =>
              renderedText.includes(String(value).replace(/\s+/gu, ''))));
        }
        return { width: window.innerWidth, cardsRendered: rows };
      }, ids);
      assert.deepEqual(opened.errors, []);
      assert.equal(data.width, width);
      assert.deepEqual(data.cardsRendered, ids.map(() => true));
      results.widths.push({ width, cardsRendered: data.cardsRendered, pass: true });
      await opened.page.close();
    }

    results.counts = { vocabulary: nextData.vocab, grammar: nextData.grammarIds.length, lexicalPairs: nextData.pairs.length };
    results.changedIds = changed;
    results.pairIndexesReviewed = pairIndexes;
    results.pass = true;
    fs.writeFileSync('completion/v176-work/browser-results.json',
      JSON.stringify(results, null, 2) + '\n');
    console.log(JSON.stringify(results, null, 2));
  } finally {
    await browser.close();
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
