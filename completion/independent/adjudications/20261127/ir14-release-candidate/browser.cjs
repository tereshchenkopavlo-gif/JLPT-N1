const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs");

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", error => errors.push(error.message));
    let html = fs.readFileSync(process.argv[2], "utf8");
    await page.route("http://c12.test/", route => route.fulfill({ contentType: "text/html", body: html }));
    await page.goto("http://c12.test/");
    const progress = await page.evaluate(() => {
      state.vp["1510"] = { status: "S", due: "2026-12-01" };
      state.gp["1"] = { status: "X", due: "2026-12-01" };
      if (!saveStorage()) throw new Error("Save failed");
      return JSON.parse(localStorage.getItem(STORAGE_KEY));
    });
    html = fs.readFileSync(process.argv[3], "utf8");
    await page.reload();
    assert.deepEqual(await page.evaluate(() => state), progress);
    assert.deepEqual(await page.evaluate(() => [
      DEFAULT_VOCAB.length, Object.keys(GRAMMAR_DETAILS_BY_ID).length
    ]), [3914, 130]);
    const [caseData] = JSON.parse(fs.readFileSync(process.argv[4], "utf8")).cases;
    const widths = [360, 412, 1280];
    for (const width of widths) {
      await page.setViewportSize({width, height: 900});
      const generated = await page.evaluate(id => {
        const index = readingBank.long.findIndex(row => row.id === id);
        if (index < 0) throw new Error("Missing reading");
        const random = Math.random;
        let passages;
        try {
          Math.random = () => (index + 0.5) / readingBank.long.length;
          passages = SmartEngine.generateOfflinePassage([]);
        } finally {
          Math.random = random;
        }
        const passage = passages.find(row => row.level === "long");
        curSession = {items: [], passageIdx: 0, passages: [passage]};
        showView("session");
        document.getElementById("sessBody").style.display = "";
        renderPassage();
        return passage;
      }, caseData.case_id);
      assert.equal(generated.title, caseData.fields.title);
      assert.equal(generated.plainText, caseData.fields.ja);
      assert.equal(await page.locator(".qchoice").count(), 12);
      for (const [index, expected] of caseData.fields.questions.entries()) {
        const question = generated.questions[index];
        assert.equal(question.prompt, expected.prompt);
        assert.equal(question.choices[question.answer], expected.choices[expected.answer]);
        assert.deepEqual([...question.choices].sort(), [...expected.choices].sort());
        await page.locator(`.qchoice[data-qi="${index}"][data-ci="${question.answer}"]`).click();
        assert.equal(await page.locator(`#exp-${index}`).innerText(), expected.explain);
      }
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false);
    }
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({ pass: true, widths, vocab: 3914, grammar: 130, restoredProgress: true, questions: 3, pageErrors: errors }, null, 2));
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
