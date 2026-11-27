const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs");

const decisions = JSON.parse(fs.readFileSync("cloze-context-review.json", "utf8")).decisions;
assert.equal(decisions.length, 24);
assert.equal(new Set(decisions.map(row => JSON.stringify([row.id, row.example]))).size, 24);
assert.ok(decisions.every(row => row.decision === "reject_cloze" && row.allowCloze === false));

(async () => {
    const browser = await chromium.launch();
    try {
        const results = [];
        for (const name of ["current", "merged", "fixture"]) {
            const page = await browser.newPage();
            const errors = [];
            page.on("pageerror", error => errors.push(error.message));
            const html = fs.readFileSync((name === "fixture" ? "merged" : name) + ".html", "utf8");
            const marker = "const type = types.length ? types[Math.floor(Math.random() * types.length)] : null;";
            assert.equal(html.split(marker).length, 2);
            await page.route("https://jlpt.test/", route => route.fulfill({
                contentType: "text/html",
                body: html.replace(marker, "globalThis.c11Observed.push({ex, types: types.slice()}); " + marker)
            }));
            await page.goto("https://jlpt.test/");
            await page.waitForFunction(() => ACTIVE_VOCAB.length === 3914);
            results.push(await page.evaluate(({rows, fixture}) => {
                if (fixture) {
                    const exact = rows.find(row => row.id === 3375).example;
                    REVIEWED_CLOZE_QUIZZES.v_3375 = {
                        byExample: {[exact]: {allowCloze: true, wrong: ["fixture A", "fixture B", "fixture C"]}}
                    };
                }
                return rows.map(({id, example}) => {
                const word = DEFAULT_VOCAB.find(v => v.id === id);
                const item = {kind: "v", id: String(id), word};
                const definition = SmartEngine.getDefinition(word.w, item.kind, item.id);
                const examples = definition.examples.filter(s => SmartEngine.markTarget(s, item.kind, word.w).found);
                const index = examples.indexOf(example);
                if (index < 0) throw new Error("Historical example missing: " + id);
                const random = Math.random;
                let first = true;
                globalThis.c11Observed = [];
                try {
                    Math.random = () => {
                        if (!first) return 0.5;
                        first = false;
                        return (index + 0.5) / examples.length;
                    };
                    SmartEngine.generateOfflinePassage([item]);
                } finally {
                    Math.random = random;
                }
                const [observed] = globalThis.c11Observed;
                if (globalThis.c11Observed.length !== 1 || observed.ex !== example)
                    throw new Error("Did not exercise the exact context: " + id);
                return {id, example, types: observed.types};
            });
            }, {rows: decisions, fixture: name === "fixture"}));
            assert.deepEqual(errors, []);
            await page.close();
        }
        const [baseline, candidate, fixture] = results;
        const selected = decisions.findIndex(row => row.id === 3375);
        for (const [i, row] of fixture.entries()) {
            const expected = candidate[i].types.slice();
            if (i === selected) {
                expected.push("cloze");
                assert.ok(row.types.includes("meaning"));
                assert.ok(row.types.includes("reading"));
            }
            assert.deepEqual(row.types.slice().sort(), expected.sort());
        }
        console.log(JSON.stringify({fixtureContexts: fixture.length, onlyExactContextActivated: true}));
        const losses = baseline.filter((row, i) => row.types.includes("cloze") && !candidate[i].types.includes("cloze"));
        assert.ok(candidate.every(row => !row.types.includes("cloze") && row.types.includes("meaning")));
        for (let i = 0; i < baseline.length; i++) {
            assert.deepEqual(candidate[i].types.filter(type => type !== "cloze"), baseline[i].types.filter(type => type !== "cloze"));
        }
        console.log(JSON.stringify({checked: decisions.length, eligibleBefore: baseline.filter(row => row.types.includes("cloze")).length, eligibleAfter: 0, losses}));
    } finally {
        await browser.close();
    }
})().catch(error => { console.error(error); process.exitCode = 1; });
