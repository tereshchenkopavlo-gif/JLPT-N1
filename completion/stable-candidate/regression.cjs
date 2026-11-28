const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs");
(async () => {
  const browser = await chromium.launch({executablePath: process.env.CHROMIUM_PATH});
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", e => errors.push(e.message));
    let html = fs.readFileSync(process.argv[2]);
    await page.route("http://n1.test/", r => r.fulfill({body: html, contentType: "text/html"}));
    await page.goto("http://n1.test/");
    const saved = await page.evaluate(() => {
      state.vp["1510"] = {status: "S"};
      state.vp["3363"] = {status: "X"};
      state.vp["1509"] = {status: "G"};
      state.meta.vocabTarget = 3914;
      saveStorage();
      return JSON.parse(localStorage.getItem(STORAGE_KEY));
    });
    html = fs.readFileSync(process.argv[3]);
    await page.reload();
    assert.deepEqual(await page.evaluate(() => state), saved);
    const results = await page.evaluate(async () => {
      const held = DEFAULT_VOCAB.filter(w => !isSessionVocab(w.id));
      const word = DEFAULT_VOCAB.find(row => row.id === 1509);
      const item = {word, kind: "v", id: "1509"};
      const def = SmartEngine.getDefinition(word.w, "v", item.id);
      const heldLabels = new Set(held.map(row => row.w));
      const heldReadings = new Set(held.map(row => row.r));
      const meaningLeak = quizCandidateRows(item, def).some(row => !isSessionVocab(row.v.id));
      const clozeLeak = clozeWordCandidates(item).some(label =>
        heldLabels.has(label) && !ACTIVE_VOCAB.some(row => row.w === label && isSessionVocab(row.id)));
      const readingLeak = quizReadingOptions(item).some(reading =>
        heldReadings.has(reading) && !ACTIVE_VOCAB.some(row => row.r === reading && isSessionVocab(row.id)));
      if (meaningLeak || clozeLeak || readingLeak) throw new Error("Deferred entry leaked into a generated pool");
      const review = planSession().items;
      const short = SmartEngine.generateOfflinePassage(held.map(word => ({word, kind:"v", id:String(word.id)}))).filter(p => p.level === "short");
      const originalRandom = Math.random;
      Math.random = () => 0.999999;
      let unseen;
      try {
        unseen = planSession().items;
      } finally { Math.random = originalRandom; }
      showView("cards");
      await openCardDetail("v", "1510");
      return {registered:DEFAULT_VOCAB.length, grammar:Object.keys(GRAMMAR_DETAILS_BY_ID).length,
        eligible:sessionVocabCount(), excluded:held.length,
        leakingTargets:review.concat(unseen).filter(i => i.kind==="v" && !isSessionVocab(i.id)).length,
        short:short.length, due:document.getElementById("dueNum").textContent,
        mastered:document.getElementById("masteredNum").textContent,
        target:document.getElementById("vocabTargetLabel").textContent,
        accessible:document.getElementById("cardDetailBody").textContent.includes("心中")};
    });
    assert.deepEqual(results,{registered:3914,grammar:130,eligible:3897,excluded:17,leakingTargets:0,short:0,due:"1",mastered:"0",target:"3,897",accessible:true});
    for (const width of [360, 412, 1280]) {
      await page.setViewportSize({width, height: 900});
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false);
    }
    assert.deepEqual(errors,[]);
    assert.deepEqual(await page.evaluate(() => JSON.parse(localStorage.getItem(STORAGE_KEY))),saved);
    console.log(JSON.stringify({...results, widths:[360,412,1280], excludedPoolProbe:true, savedProgressUnchanged:true, browserErrors:errors},null,2));
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
