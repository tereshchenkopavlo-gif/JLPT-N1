const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const crypto = require("node:crypto");

(async () => {
    const browser = await chromium.launch();
    try {
        const errors = [];
        const reports = [];
        for (const name of ["current", "merged"]) {
            const page = await browser.newPage({viewport: {width: 412, height: 900}});
            page.on("pageerror", error => errors.push(error.message));
            await page.route("https://jlpt.test/", route => route.fulfill({
                contentType: "text/html", body: fs.readFileSync(name + ".html", "utf8")
            }));
            await page.goto("https://jlpt.test/");
            await page.waitForFunction(() => ACTIVE_VOCAB.length === 3914);
            await page.evaluate(() => {
                localStorage.setItem(STORAGE_KEY + ":regression-probe", "retained");
            });
            await page.reload();
            const report = await page.evaluate(() => ({
                key: STORAGE_KEY,
                customKey: VOCAB_DATA_KEY,
                probe: localStorage.getItem(STORAGE_KEY + ":regression-probe"),
                pools: DEFAULT_VOCAB.map(v => {
                    const item = {kind: "v", id: String(v.id), word: v};
                    return [v.id, quizReadingOptions(item), clozeWordCandidates(item)];
                }),
            }));
            assert.equal(report.probe, "retained");
            reports.push(report);
            await page.close();
        }
        assert.deepEqual(errors, []);
        const [baseline, candidate] = reports;
        assert.equal(candidate.key, baseline.key);
        assert.equal(candidate.customKey, baseline.customKey);
        const digest = pools => crypto.createHash("sha256").update(JSON.stringify(pools)).digest("hex");
        assert.equal(digest(candidate.pools), digest(baseline.pools), "reading/cloze option pools");
        const reading3375 = candidate.pools.find(([id]) => id === 3375)[1];
        assert.ok(reading3375.length >= 3);
        console.log(JSON.stringify({poolCount: candidate.pools.length, poolSha256: digest(candidate.pools), reading3375, errors}));
    } finally {
        await browser.close();
    }
})().catch(error => { console.error(error); process.exitCode = 1; });
