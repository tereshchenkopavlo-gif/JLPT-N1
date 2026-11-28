const fs = require("node:fs");
const assert = require("node:assert/strict");
const { chromium } = require("playwright");

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", error => errors.push(error.message));
    let html;
    await page.route("http://jlpt.test/", route => route.fulfill({ contentType: "text/html", body: html }));
    async function snapshot(file, revised) {
      html = fs.readFileSync(file);
      await page.goto("http://jlpt.test/");
      return page.evaluate(revised => {
        function generate(id, example, typeDraw) {
          const word = DEFAULT_VOCAB.find(row => row.id === id);
          const originalRandom = Math.random;
          const draws = [example, typeDraw];
          Math.random = () => draws.shift() ?? 0.375;
          try {
            const passage = SmartEngine.generateOfflinePassage([{ kind: "v", id: String(id), word }])[0];
            return [passage.text, passage.questions[0]];
          } finally {
            Math.random = originalRandom;
          }
        }
        return {
          first: [0.1, 0.42, 0.91].map(draw => generate(1510, 0.1, draw)),
          second: (revised ? [0.1, 0.6] : [0.1, 0.42, 0.91]).map(draw => generate(1510, 0.75, draw)),
          controls: [1509, 1511, 3375].flatMap(id => [0.1, 0.75].flatMap(example =>
            [0.1, 0.42, 0.91].map(draw => generate(id, example, draw)))),
          size: [DEFAULT_VOCAB.length, Object.keys(GRAMMAR_DETAILS_BY_ID).length],
        };
      }, revised);
    }
    const before = await snapshot(process.argv[2], false);
    const after = await snapshot(process.argv[3], true);
    assert.match(before.second[1][0], /class="blank"/);
    assert.deepEqual(after.second, [before.second[0], before.second[2]]);
    assert.deepEqual(after.first, before.first);
    assert.deepEqual(after.controls, before.controls);
    assert.deepEqual(after.size, [3914, 130]);
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({ passed: true, changed: "ID1510 second example cloze only",
      unchangedControlScenarios: before.controls.length, vocabulary: after.size[0],
      grammar: after.size[1], browserErrors: errors }, null, 2));
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
