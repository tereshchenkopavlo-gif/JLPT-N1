const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const readHtml = version => fs.readFileSync(`JLPT_N1_ukrainian_reading_v${version}.html`, "utf8");
const baseline = readHtml(229);
const candidate = readHtml(230);
const nextPos = JSON.parse(fs.readFileSync(process.argv[2], "utf8")).pos;
const definition = (html, start) => html.split("\n").find(line => line.startsWith(start));
const displayPos = html => JSON.parse(definition(html, "const VOCAB_POS_BY_ID = ").slice(23, -1));
const originalPos = displayPos(baseline);
const revisedPos = displayPos(candidate);
assert.equal(Object.keys(nextPos).length, 3);
for (const [id, pos] of Object.entries(nextPos)) assert.notDeepEqual(pos, originalPos[id]);

function evaluate(html, pos, imported) {
  const data = ["DEFAULT_VOCAB", "VOCAB_DETAILS_BY_ID", "REVIEWED_READING_OPTIONS"]
    .map(name => {
      const line = definition(html, `const ${name} =`);
      assert.ok(line, name);
      return line;
    }).join("\n");
  const selectors = html.slice(html.indexOf("function readingFrame("), html.indexOf("function readingGlossaryEntryHtml("));
  const displayHelper = definition(html, "function vocabPartOfSpeech(");
  return vm.runInThisContext(`(() => {
    ${data}
    const VOCAB_POS_BY_ID = ${JSON.stringify(pos)};
    ${displayHelper}
    ${selectors}
    const ACTIVE_VOCAB = ${imported
      ? 'DEFAULT_VOCAB.filter(w => Number(w.id) % 3 !== 0).reverse().concat([{id: 900001, w: "試験", r: "しけん"}])'
      : 'DEFAULT_VOCAB'};
    return ACTIVE_VOCAB.map(word => {
      const item = {kind: "v", id: String(word.id), word};
      return [word.id, quizReadingOptions(item), clozeWordCandidates(item)];
    });
  })()`);
}

for (const imported of [false, true]) {
  const expected = evaluate(baseline, originalPos, imported);
  assert.equal(expected.length, imported ? 2611 : 3914);
  assert.deepEqual(evaluate(candidate, revisedPos, imported), expected);
  assert.deepEqual(evaluate(candidate, {...revisedPos, ...nextPos}, imported), expected);
  if (!imported) {
    for (const id of [3375, 3389]) {
      assert.ok(expected.find(row => Number(row[0]) === id)[1].length >= 3);
    }
  }
  console.log(`${expected.length} ${imported ? "import fixture" : "built-in"} IDs: ordered reading and cloze pools match v229 for v230 and projected v231 POS.`);
}
