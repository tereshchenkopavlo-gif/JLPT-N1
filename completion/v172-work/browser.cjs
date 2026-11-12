// v172 C10: content rendering, POS eligibility and progress-sentinel regression checks.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const crypto = require('node:crypto');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

const base = 'JLPT_N1_ukrainian_reading_v171.html';
const file = 'JLPT_N1_ukrainian_reading_v172.html';
const expectedTranslations = [
  ['3701',0,'У період тривалої нестерпної спеки різко зросла кількість людей, яких доправляють до лікарні через перегрівання.'],
  ['3710',1,'Відповідальним за розроблення нового продукту несподівано призначили його — працівника, який працює в компанії десятий рік.'],
  ['3716',0,'Партійні реформатори зажадали від керівництва партії докорінного перегляду.'],
  ['3723',1,'Досвід за кордоном докорінно змінив його погляди на життя.'],
  ['3725',0,'У столичному регіоні тривалі поїздки на роботу давно залишаються проблемою.'],
  ['3725',1,'Агентство метеорології повідомило, що завтра тайфун, імовірно, наблизиться до столичного регіону.'],
  ['3736',0,'Рятувальники знайшли під урвищем альпініста, який не міг рухатися.'],
  ['3739',0,'Якщо попросити його про знайомство, завдяки його широким зв’язкам можна налагодити контакти з більшістю компаній.'],
  ['3745',0,'Можливо, випадкова репліка зачепила співрозмовника.'],
  ['3753',1,'Вирішили обрати людину, яка вміє тримати язик за зубами, і доручити їй таємне розслідування.'],
  ['3757',0,'Біля станції зібралися мешканці, які нетерпляче відраховували дні до відкриття руху.']
];

async function open(browser, filename, width) {
  const page = await browser.newPage({ viewport: { width, height: 915 } });
  await page.goto(pathToFileURL(path.resolve(filename)).href);
  return page;
}
async function eligibility(page) {
  return page.evaluate(() => ACTIVE_VOCAB.map(word => {
    const item = { kind: 'v', word, id: word.id };
    return {
      id: Number(word.id),
      pos: vocabPartOfSpeech(word.id).join('|'),
      reading: quizReadingOptions(item),
      cloze: clozeWordCandidates(item)
    };
  }));
}
async function main() {
  const browser = await chromium.launch({ headless: true });
  const results = { widths: [], cardsChecked: 13, translationsChecked: 11, sha256: crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex') };
  let before, after;
  try {
    before = await open(browser, base, 1280);
    after = await open(browser, file, 1280);
    const beforeData = await before.evaluate(() => ({
      vocab: Object.keys(VOCAB_DETAILS_BY_ID).length,
      grammar: Object.keys(GRAMMAR_DETAILS_BY_ID).length,
      ids: Object.keys(VOCAB_DETAILS_BY_ID),
      eligibility: ACTIVE_VOCAB.length
    }));
    const afterData = await after.evaluate(() => ({
      vocab: Object.keys(VOCAB_DETAILS_BY_ID).length,
      grammar: Object.keys(GRAMMAR_DETAILS_BY_ID).length,
      ids: Object.keys(VOCAB_DETAILS_BY_ID),
      eligibility: ACTIVE_VOCAB.length,
      pos3742: VOCAB_POS_BY_ID['3742'],
      card3757: VOCAB_DETAILS_BY_ID['3757'],
      target3757: VOCAB_KANA_EXAMPLE_TARGETS['指を折る']
    }));
    assert.equal(beforeData.vocab, 3914);
    assert.equal(afterData.vocab, 3914);
    assert.equal(afterData.grammar, 130);
    assert.deepEqual(afterData.ids, beforeData.ids);
    assert.equal(afterData.eligibility, 3914);
    assert.deepEqual(afterData.pos3742, ['名詞']);
    const correctedFields = await after.evaluate(() => ({
      usage3724: VOCAB_DETAILS_BY_ID['3724'].usage,
      translation3747: VOCAB_DETAILS_BY_ID['3747'].t,
      usage3757: VOCAB_DETAILS_BY_ID['3757'].usage
    }));
    assert.equal(correctedFields.usage3724, '〜係 — відповідальна особа або функція: N＋係 — 受付係・案内係; V連用形＋係 — 見張り係（見張る→見張り）. Окреме 係 означає доручену роль.');
    assert.equal(correctedFields.translation3747, 'плутати головне з другорядним; ставити засіб вище за мету');
    assert.equal(correctedFields.usage3757, '指折り数えて待つ — нетерпляче відраховувати дні до очікуваної події; 指を折って数える — лічити на пальцях. Не буквальне ламання пальця.');
    results.correctedFields = { pass: true, ...correctedFields };
    const sentence = '開通の日を指折り数えて待つ住民が、駅前に集まっていた。';
    assert.equal(afterData.card3757.examples[0], sentence);
    assert.equal(afterData.target3757[sentence], '指折り数えて');

    const beforePools = await eligibility(before);
    const afterPools = await eligibility(after);
    assert.equal(beforePools.length, 3914);
    assert.equal(afterPools.length, 3914);
    const clozeChanges = [];
    for (let i = 0; i < afterPools.length; i++) {
      const b = beforePools[i], a = afterPools[i];
      assert.equal(a.id, b.id);
      assert.deepEqual(a.reading, b.reading, `reading alternatives changed for ID ${a.id}`);
      const beforeSet = new Set(b.cloze), afterSet = new Set(a.cloze);
      const added = [...afterSet].filter(x => !beforeSet.has(x)).sort();
      const removed = [...beforeSet].filter(x => !afterSet.has(x)).sort();
      if (a.id === 3742) {
        assert.equal(b.pos, '名詞|ナ形');
        assert.equal(a.pos, '名詞');
        assert(a.cloze.length > 3);
        clozeChanges.push({ id: a.id, kind: 'target-pos-reclassified', before: b.cloze.length, after: a.cloze.length });
      } else if (b.pos === '名詞') {
        assert.deepEqual(added, ['お手上げ']);
        assert.deepEqual(removed, []);
        clozeChanges.push({ id: a.id, kind: 'noun-pool-addition', added });
      } else if (b.pos === '名詞|ナ形') {
        assert.deepEqual(added, []);
        assert.deepEqual(removed, ['お手上げ']);
        clozeChanges.push({ id: a.id, kind: 'na-adjective-pool-removal', removed });
      } else {
        assert.deepEqual(added, []);
        assert.deepEqual(removed, []);
      }
      if (a.id !== 3742 && b.cloze.length >= 3) assert(a.cloze.length >= 3);
    }
    const id3742Quiz = await after.evaluate(() => !!REVIEWED_MEANING_QUIZZES['v_3742']);
    assert.equal(id3742Quiz, true);
    results.quizEligibility = {
      records: afterPools.length,
      readingOptionsUnchanged: true,
      clozePoolDeltaVerified: true,
      changedRecords: clozeChanges.length,
      targetPool: clozeChanges.find(x => x.id === 3742),
      id3742ReviewedMeaningDisablesCloze: id3742Quiz
    };

    const rendered = await after.evaluate(rows => rows.map(([id,index,expected]) => {
      const card = VOCAB_DETAILS_BY_ID[id];
      const html = vocabExamplesHtml(id, card.examples);
      return {
        id, index,
        expectedValue: card.exampleTranslations[index] === expected,
        exampleRendered: html.includes(escapeLex(card.examples[index])),
        translationRendered: html.includes(escapeLex(card.exampleTranslations[index]))
      };
    }), expectedTranslations);
    assert(rendered.every(x => x.expectedValue && x.exampleRendered && x.translationRendered));
    results.renderedExamples = rendered;
    results.id3757Target = { sentence, target: afterData.target3757[sentence], pass: true };

    const cardRenderChecks = await after.evaluate(async ids => {
      const key = 'choba_n1uk_storage_v1';
      const sentinel = 'v172-progress-sentinel';
      localStorage.setItem(key, sentinel);
      const checked = [];
      const normalize = value => String(value || '').replace(/\s+/g, '');
      for (const id of ids) {
        const data = await getCardData('v', id);
        const html = renderCardShell('v', id, data);
        const record = VOCAB_DETAILS_BY_ID[id];
        const wrapper = document.createElement('div');
        wrapper.innerHTML = html;
        const translations = [...wrapper.querySelectorAll('.fc-trans[lang="uk"]')];
        const exampleTranslations = [...wrapper.querySelectorAll('.grammar-example-ua[lang="uk"]')].map(x => x.textContent);
        const expectedUsage = displayUsageText(record.usage || '', 'v');
        const mainText = translations[0]?.textContent || '';
        const usageText = translations.slice(1).map(x => x.textContent).join('');
        checked.push({
          id,
          mainTranslation: !!translations[0] && normalize(mainText).includes(normalize(record.t)),
          exampleTranslations: (record.exampleTranslations || []).every((value, i) => normalize(exampleTranslations[i]) === normalize(value)),
          usage: !expectedUsage || normalize(usageText).includes(normalize(expectedUsage)),
          mainText: normalize(mainText),
          expectedMain: normalize(record.t),
          usageText: normalize(usageText),
          expectedUsage: normalize(expectedUsage)
        });
      }
      return { checked, progressStorageUnchanged: localStorage.getItem(key) === sentinel };
    }, ['3701','3710','3716','3723','3724','3725','3736','3739','3742','3745','3747','3753','3757']);
    console.log('v172 card render diagnostics', JSON.stringify(cardRenderChecks.checked));
    assert(cardRenderChecks.checked.every(x => x.mainTranslation && x.exampleTranslations && x.usage), 'Card render content mismatch: ' + JSON.stringify(cardRenderChecks.checked.filter(x => !x.mainTranslation || !x.exampleTranslations || !x.usage)));
    assert.equal(cardRenderChecks.progressStorageUnchanged, true);
    results.cardRenderChecks = cardRenderChecks;

    for (const width of [360, 412, 1280]) {
      const page = await open(browser, file, width);
      await page.locator('.nav-tab[data-view="cards"]').click();
      await page.locator('#cardPos').selectOption('名詞');
      const noun = await page.evaluate(() => getCardPool().some(row => row.kind === 'v' && Number(row.id) === 3742));
      await page.locator('#cardPos').selectOption('ナ形');
      const na = await page.evaluate(() => getCardPool().some(row => row.kind === 'v' && Number(row.id) === 3742));
      assert.equal(noun, true);
      assert.equal(na, false);
      results.widths.push({ width, id3742: { nounFilter: noun, naFilter: na }, pass: true });
      await page.close();
    }
    results.pass = true;
    fs.writeFileSync('completion/v172-work/browser-results.json', JSON.stringify(results, null, 2) + '\n');
  } finally {
    if (before) await before.close().catch(()=>{});
    if (after) await after.close().catch(()=>{});
    await browser.close();
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
