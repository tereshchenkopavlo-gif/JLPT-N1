const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs");

(async () => {
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", e => errors.push(e.message));
    let html = fs.readFileSync("baseline.html", "utf8");
    await page.route("https://jlpt.test/", route => route.fulfill({contentType: "text/html", body: html}));
    await page.goto("https://jlpt.test/");
    async function exerciseSnapshot() {
      return page.evaluate(() => {
        const word = DEFAULT_VOCAB.find(row => row.id === 1510);
        const item = {kind: "v", id: "1510", word};
        const definition = SmartEngine.getDefinition(word.w, item.kind, item.id);
        const originalRandom = Math.random;
        Math.random = () => 0.25;
        try {
          return {
            vocab: DEFAULT_VOCAB.length,
            grammar: Object.keys(GRAMMAR_DETAILS_BY_ID).length,
            reading: quizReadingOptions(item),
            cloze: clozeWordCandidates(item),
            contexts: definition.examples.map(example => ({
              cloze: literalClozeAvailable(example, item, SmartEngine),
              meaning: quizMeaningOptions(item, definition, example),
            })),
          };
        } finally {
          Math.random = originalRandom;
        }
      });
    }
    const baseline = await exerciseSnapshot();
    const progress = await page.evaluate(() => {
      state.vp["1510"] = {status: "S", due: "2026-12-01"};
      state.gp["1"] = {status: "X", due: "2026-12-01"};
      state.meta.vocabTarget = 1234;
      if (!saveStorage()) throw new Error("Save failed");
      return JSON.parse(localStorage.getItem(STORAGE_KEY));
    });
    html = fs.readFileSync("id1510.html", "utf8");
    await page.reload();
    assert.deepEqual(await exerciseSnapshot(), baseline);
    assert.equal(baseline.vocab, 3914);
    assert.equal(baseline.grammar, 130);
    assert.deepEqual(await page.evaluate(() => state), progress);
    for (const width of [360, 412, 1280]) {
      await page.setViewportSize({width, height: 900});
      await page.evaluate(async () => {
        showView("cards");
        await openCardDetail("v", "1510");
      });
      assert.ok(await page.locator("#cardDetailBody").isVisible());
      assert.match(await page.locator("#cardDetailBody").innerText(), /спільне самогубство; спільна загибель; перен\. разом зазнати краху/);
    }
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({id: 1510, widths: [360,412,1280], meaningContexts: baseline.contexts.length, unchangedExerciseOptions: true, restoredProgress: true}));
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
