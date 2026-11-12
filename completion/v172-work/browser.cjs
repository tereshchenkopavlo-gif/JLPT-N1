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
  ['3716',0,'Партійні реформатори зажадали від керівництва партії докорінно все переглянути.'],
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
      reading: quizReadingOptions(item).length,
      cloze: clozeWordCandidates(item).length
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
    assert.equal(correctedFields.translation3747, 'плутати головне з другорядним; підміняти мету засобом');
    assert.equal(correctedFields.usage3757, '指折り数えて待つ — нетерпляче відраховувати дні до очікуваної події; 指を折って数える — лічити на пальцях. Не буквальне ламання пальця.');
    results.correctedFields = { pass: true, ...correctedFields };
    const sentence = '開通の日を指折り数えて待つ住民が、駅前に集まっていた。';
    assert.equal(afterData.card3757.examples[0], sentence);
    assert.equal(afterData.target3757[sentence], '指折り数えて');

    const beforePools = await eligibility(before);
    const afterPools = await eligibility(after);
    assert.deepEqual(afterPools, beforePools);
    results.quizEligibility = { records: afterPools.length, unchanged: true };

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
