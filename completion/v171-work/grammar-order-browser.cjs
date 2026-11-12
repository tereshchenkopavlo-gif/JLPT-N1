const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { pathToFileURL } = require('node:url');
const file = 'JLPT_N1_v171_checkpoint.html';
const url = pathToFileURL(path.resolve(file)).href;

(async () => {
  const browser = await chromium.launch({ headless: true });
  const results = [];
  try {
    for (const width of [360, 412, 1280]) {
      const page = await browser.newPage({ viewport: { width, height: 915 } });
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto(url, { waitUntil: 'load' });
      const result = await page.evaluate(({ width }) => {
        const all = getAllItems();
        const vocab = all.filter(item => item.kind === 'v');
        const grammar = all.filter(item => item.kind === 'g');
        if (vocab.length !== 3914 || grammar.length !== 130) throw new Error('record count changed');
        if (new Set(vocab.map(item => String(item.id))).size !== 3914) throw new Error('vocabulary IDs are not unique');
        if (new Set(grammar.map(item => String(item.id))).size !== 130) throw new Error('grammar IDs are not unique');
        const progressKey = 'choba_n1uk_storage_v1';
        const comparisonKey = 'jlptN1CompareListUA_v1';
        const oldProgress = localStorage.getItem(progressKey);
        const oldComparison = localStorage.getItem(comparisonKey);
        const sentinel = 'v171-grammar-layout-sentinel';
        localStorage.setItem(progressKey, sentinel);
        const cardBody = document.getElementById('cardDetailBody');
        const sessionBody = document.getElementById('teachBody');
        if (!cardBody || !sessionBody) throw new Error('card/session containers missing');
        const follows = (a, b) => Boolean(a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING);
        const checkCard = (html, container, id, context, data) => {
          container.innerHTML = html;
          const before = container.querySelector('[data-grammar-layout="before"]');
          const examples = container.querySelector('[data-grammar-layout="examples"]');
          const after = container.querySelector('[data-grammar-layout="after"]');
          const afterContent = after && after.nextElementSibling;
          if (!before || !examples || !after || !afterContent) { const model = cardStudyModel('g', data); const parts = splitGrammarUsage(model.usage); console.log('DEBUG_LAYOUT', JSON.stringify({context, id, labels:[...container.querySelectorAll('.fc-section-label')].map(x=>x.textContent.trim()), model, parts, rendered:html.slice(Math.max(0,html.indexOf('fc-meaning')),Math.min(html.length,html.indexOf('fc-actions')>0?html.indexOf('fc-actions'):html.length))})); throw new Error(context + ' missing sections for grammar ' + id); }
          if (!follows(before, examples) || !follows(examples, after)) throw new Error(context + ' order failure for grammar ' + id);
          const rows = [...container.querySelectorAll('.fc-examples li')];
          if (rows.length !== 2 || rows.some(row => !row.querySelector('.grammar-example-ua'))) throw new Error(context + ' examples/translations missing for grammar ' + id);
          if (!afterContent.querySelector('.study-subheading')) throw new Error(context + ' analysis headings missing for grammar ' + id);
        };
        const ids = width === 412 ? grammar.map(item => String(item.id)) : ['1', '90', '130'];
        for (const id of ids) {
          const data = getCardData('g', id);
          checkCard(renderCardShell('g', id, data), cardBody, id, 'card', data);
          checkCard(renderCardShell('g', id, data, { staticChips: true, hideActions: true }), sessionBody, id, 'session', data);
          if (!saveComparisonKeys(['g_' + id])) throw new Error('could not save comparison key for grammar ' + id);
          renderComparison();
          const entry = document.querySelector('#compareList .compare-entry');
          if (!entry) throw new Error('comparison entry missing for grammar ' + id);
          const before = entry.querySelector('[data-grammar-layout="before"]');
          const examples = entry.querySelector('.grammar-examples');
          const after = entry.querySelector('[data-grammar-layout="after"]');
          const afterContent = after && after.nextElementSibling;
          if (!before || !examples || !after || !afterContent) throw new Error('comparison sections missing for grammar ' + id);
          if (!afterContent.querySelector('.study-subheading')) throw new Error('comparison analysis headings missing for grammar ' + id);
          if (!follows(before, examples) || !follows(examples, after)) throw new Error('comparison order failure for grammar ' + id);
          const rows = [...entry.querySelectorAll('.grammar-examples li')];
          if (rows.length !== 2 || rows.some(row => !row.querySelector('.grammar-example-ua'))) throw new Error('comparison examples/translations missing for grammar ' + id);
        }
        const g90 = document.createElement('div');
        g90.innerHTML = renderCardShell('g', '90', getCardData('g', '90'));
        const afterLabel90 = g90.querySelector('[data-grammar-layout="after"]');
        const analysis90 = afterLabel90 && afterLabel90.nextElementSibling;
        if (!analysis90) throw new Error('grammar 90 analysis content missing');
        const supplemental = [...analysis90.querySelectorAll('.study-example')];
        const supplementalText = supplemental.map(node => node.textContent).join(' ');
        if (supplemental.length !== 2 || !supplementalText.includes('追及せずにはおかない') || !supplementalText.includes('笑わずにはいられなかった')) {
          throw new Error('grammar 90 must show separate intention and ずにはいられない examples');
        }
        if (localStorage.getItem(progressKey) !== sentinel) throw new Error('rendering changed the progress storage key');
        if (oldProgress === null) localStorage.removeItem(progressKey); else localStorage.setItem(progressKey, oldProgress);
        if (oldComparison === null) localStorage.removeItem(comparisonKey); else localStorage.setItem(comparisonKey, oldComparison);
        return {
          width,
          vocabularyRecords: vocab.length,
          grammarRecords: grammar.length,
          grammarIdsUnique: true,
          cardsChecked: ids.length,
          cardLayouts: ids.length,
          sessionLayouts: ids.length,
          comparisonLayouts: ids.length,
          translatedMainExamples: ids.length * 2,
          g90SupplementalExamples: supplemental.length,
          progressStorageUnchanged: true
        };
      }, { width });
      assert.deepEqual(errors, [], 'uncaught browser errors at width ' + width);
      results.push(result);
      await page.close();
    }
    const html = fs.readFileSync(file, 'utf8');
    const evidence = {
      version: 'v171 checkpoint',
      sha256: crypto.createHash('sha256').update(html).digest('hex'),
      browser: browser.version(),
      results,
      pass: true
    };
    fs.writeFileSync('completion/v171-work/grammar-order-results.json', JSON.stringify(evidence, null, 2) + '\n');
    console.log('PASS v171 grammar order: ' + JSON.stringify(results));
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
