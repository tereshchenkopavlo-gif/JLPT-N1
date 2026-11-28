const assert = require("node:assert/strict");
const fs = require("node:fs");
const { chromium } = require("playwright");

const deferred = [1510, 3363, 3375, 3417, 3441, 3444, 3525, 3561, 3565,
  3569, 3594, 3636, 3646, 3652, 3654, 3677, 3679];

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH });
  try {
    const base = await browser.newPage();
    const candidate = await browser.newPage();
    const errors = [];
    for (const [page, file] of [[base, process.argv[2]], [candidate, process.argv[3]]]) {
      page.on("pageerror", error => errors.push(error.message));
      await page.route("http://localhost/", route => route.fulfill({
        contentType: "text/html", body: fs.readFileSync(file)
      }));
      await page.goto("http://localhost/");
    }
    await base.evaluate(ids => {
      ACTIVE_VOCAB = ACTIVE_VOCAB.filter(word => !ids.includes(word.id));
    }, deferred);
    async function snapshot(page, start) {
      return page.evaluate(async ({ start, deferred }) => {
        const digest = async value => {
          const data = new TextEncoder().encode(JSON.stringify(value));
          const hash = await crypto.subtle.digest("SHA-256", data);
          return Array.from(new Uint8Array(hash));
        };
        const rows = DEFAULT_VOCAB.slice(start, start + 100);
        const pools = [];
        for (const word of rows) {
          if (deferred.includes(word.id)) continue;
          const item = {kind: "v", id: String(word.id), word};
          const def = SmartEngine.getDefinition(word.w, item.kind, item.id);
          const meaning = def?.m ? quizCandidateRows(item, def).map(row => [row.v.id, row.choice, row.score]) : [];
          pools.push([word.id,
            await digest(meaning),
            await digest(clozeWordCandidates(item)),
            await digest(quizReadingOptions(item))]);
        }
        return pools;
      }, { start, deferred });
    }
    let count = 0;
    for (let start = 0; start < 3914; start += 100) {
      const [expected, actual] = await Promise.all([snapshot(base, start), snapshot(candidate, start)]);
      assert.deepEqual(actual, expected, "Pool mismatch at offset " + start);
      count += actual.length;
    }
    assert.equal(count, 3897);
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({passed: true, checkedVocabulary: count, deferred: deferred.length,
      compared: ["ordered meaning candidates", "ordered cloze candidates", "ordered reading candidates"],
      reference: "published engine with only deferred IDs removed from exercise inventory",
      pageErrors: errors}, null, 2));
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
