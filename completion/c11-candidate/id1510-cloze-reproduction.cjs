const assert = require("node:assert/strict");
const fs = require("node:fs");
const { chromium } = require("playwright");

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", error => errors.push(error.message));
    const html = fs.readFileSync(process.argv[2]);
    await page.route("http://jlpt.test/", route => route.fulfill({ contentType: "text/html", body: html }));
    await page.goto("http://jlpt.test/");
    const result = await page.evaluate(() => {
      const word = DEFAULT_VOCAB.find(row => row.id === 1510);
      const item = { kind: "v", id: "1510", word };
      const pool = clozeWordCandidates(item).filter(label => label !== word.w);
      const competingIndex = pool.indexOf("協力");
      if (competingIndex < 0) throw new Error("Missing competing option");
      const previousRandom = Math.random;
      let draw = 0;
      // Select the second example, then cloze. In Fisher–Yates swap 協力 into slot zero.
      Math.random = () => {
        draw += 1;
        if (draw === 1) return 0.75;
        if (draw === 2) return 0.5;
        if (draw === pool.length - competingIndex + 2) return 0;
        return 0.999999;
      };
      try {
        const passage = SmartEngine.generateOfflinePassage([item])[0];
        return { text: passage.text, question: passage.questions[0], poolSize: pool.length };
      } finally {
        Math.random = previousRandom;
      }
    });
    assert.match(result.text, /古い体質の組織と.*するわけにはいかない/);
    assert.equal(result.question.choices[result.question.answer], "心中");
    assert.ok(result.question.choices.includes("協力"));
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({ ...result, errors }, null, 2));
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
