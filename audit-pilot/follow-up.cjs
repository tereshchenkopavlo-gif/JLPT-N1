const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const baseline = path.resolve(__dirname, '../JLPT_N1_ukrainian_reading_v152.html');
const html = fs.readFileSync(process.argv[2] || baseline, 'utf8');
const extraPos = process.argv.includes('--extra-pos');

function section(start, end) {
  const from = html.indexOf(start);
  const to = html.indexOf(end, from);
  assert(from >= 0 && to > from, start);
  return html.slice(from, to);
}

const engine = [
  section('const GRAMMAR_DETAILS_BY_ID', 'function enrichItemTags'),
  section('let state =', 'const STORAGE_KEY'),
  section('const VOCAB_AUDITED_PAIRS', 'function planSession'),
  section('const VOCAB_POS_BY_ID', '\n'),
  section('function vocabPartOfSpeech', '\nfunction wordPosHtml'),
  section('function escapeLex(value)', '\n}').concat('\n}'),
].join('\n');

const exercise = `
const ids = ['230', '3890'];
const items = ids.map(id => ({kind: 'v', id, word: ACTIVE_VOCAB.find(v => String(v.id) === id)}));
const definitions = items.map(item => SmartEngine.getDefinition(item.word.w, item.kind, item.id));
const passages = [];
for (const seed of [0, 0.99]) {
  Math.random = () => seed;
  const short = SmartEngine.generateOfflinePassage(items).find(p => p.level === 'short');
  passages.push({
    targetKeys: short.targetKeys,
    correctChoiceOccurrences: short.questions.map(q => q.choices.filter(c => c === q.choices[q.answer]).length),
  });
}
const direct = ACTIVE_VOCAB.find(v => String(v.id) === '255');
const directItem = {kind: 'v', id: '255', word: direct};
const card230 = VOCAB_DETAILS_BY_ID['230'];
JSON.stringify({
  reading255: quizReadingOptions(directItem),
  clozePool255: clozeWordCandidates(directItem).length,
  newExample230: card230.examples[0],
  markedExample230: SmartEngine.boldTarget(card230.examples[0], 'v', '先日'),
  definitionsMatchId: definitions.map((d, index) => d.m === VOCAB_DETAILS_BY_ID[ids[index]].m),
  examplesDiffer: definitions[0].examples[1] !== definitions[1].examples[1],
  partsOfSpeech: [230, 3890, 255].map(vocabPartOfSpeech),
  passages,
});
`;

const result = JSON.parse(vm.runInNewContext(engine + '\n' + exercise));
assert.deepEqual(result.definitionsMatchId, [true, true]);
assert.equal(result.examplesDiffer, true);
assert(result.markedExample230.includes('<b>先日</b>'));
assert.deepEqual(result.partsOfSpeech, [['名詞'], ['名詞', '副詞'], extraPos ? ['名詞', '副詞'] : ['名詞']]);
for (const passage of result.passages) {
  assert.deepEqual(passage.targetKeys, ['v:230', 'v:3890']);
  assert.deepEqual(passage.correctChoiceOccurrences, [1, 1]);
}
console.log(JSON.stringify(result, null, 2));
