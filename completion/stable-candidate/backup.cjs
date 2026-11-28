const assert = require("node:assert/strict");
const fs = require("node:fs");
const { chromium } = require("playwright");

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH });
  try {
    const errors = [];
    async function open(file) {
      const page = await browser.newPage({ acceptDownloads: true });
      page.on("pageerror", error => errors.push(error.message));
      await page.route("http://n1.test/", route => route.fulfill({
        body: fs.readFileSync(file), contentType: "text/html"
      }));
      await page.goto("http://n1.test/");
      return page;
    }
    async function download(page) {
      const event = page.waitForEvent("download");
      await page.locator("#btnExportProgress").evaluate(button => button.click());
      return JSON.parse(fs.readFileSync(await (await event).path(), "utf8"));
    }
    const baseline = await open(process.argv[2]);
    await baseline.evaluate(() => {
      state.vp["1510"] = { status: "S", due: "2026-12-04" };
      state.vp["3363"] = { status: "X" };
      state.vp["1509"] = { status: "G" };
      state.gp["1"] = { status: "S" };
      state.meta.vocabTarget = 3914;
      if (!saveStorage() || !saveComparisonKeys(["v_1510", "g_1"])) throw new Error("Fixture save failed");
    });
    const expected = await download(baseline);
    const candidate = await open(process.argv[3]);
    await candidate.locator("#importProgressInput").setInputFiles({
      name: "progress.json", mimeType: "application/json", buffer: Buffer.from(JSON.stringify(expected))
    });
    await candidate.waitForFunction(() => state.vp["1510"]?.status === "S"
      && getComparisonKeys().includes("v_1510"));
    assert.deepEqual(await download(candidate), expected);
    await candidate.reload();
    assert.deepEqual(await download(candidate), expected);
    assert.equal(await candidate.locator("#dueNum").textContent(), "1");
    assert.equal(await candidate.locator("#masteredNum").textContent(), "1");
    assert.equal(await candidate.locator("#vocabTargetLabel").textContent(), "3,897");
    await candidate.locator("#importProgressInput").setInputFiles({
      name: "invalid.json", mimeType: "application/json", buffer: Buffer.from('{"vp":[]}')
    });
    await candidate.getByText("ファイルが正しくありません。", {exact: true}).waitFor();
    assert.deepEqual(await download(candidate), expected);
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({ pass: true, backupVersion: expected.backupVersion,
      identicalAfterImportAndReload: true, invalidBackupPreservedProgress: true,
      originalTarget: expected.meta.vocabTarget, displayedTarget: 3897,
      deferredProgressRetained: [1510, 3363], comparisonKeys: expected.comparisonKeys, errors }, null, 2));
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
