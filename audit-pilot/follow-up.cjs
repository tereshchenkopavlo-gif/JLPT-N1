const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const baseline = path.resolve(__dirname, '../JLPT_N1_ukrainian_reading_v152.html');
const html = fs.readFileSync(process.argv[2] || baseline, 'utf8');
const extraPos = process.argv.includes('--extra-pos');
const meaningTrial = process.argv.includes('--meaning');
const definitionTrial = process.argv.includes('--definitions');

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
const reviewedDefinitions = ${definitionTrial} ? [
  '122', '131', '144', '184', '203', '264', '267', '268', '293', '313',
].map(id => {
  const word = ACTIVE_VOCAB.find(v => String(v.id) === id);
  const item = {kind: 'v', id, word};
  const def = SmartEngine.getDefinition(word.w, 'v', id);
  return {
    id,
    definition: def.m,
    examples: def.examples.map(example => {
      const quiz = quizMeaningOptions(item, def, example);
      return {correct: quiz.correct, wrong: quiz.wrong};
    }),
  };
}) : [];
const contextualQuestions = ${meaningTrial} ? ['264', '293'].flatMap(id => {
  const word = ACTIVE_VOCAB.find(v => String(v.id) === id);
  const item = {kind: 'v', id, word};
  return VOCAB_DETAILS_BY_ID[id].examples.map((example, index) => {
    let calls = 0;
    Math.random = () => calls++ === 0 && index === 1 ? 0.99 : 0;
    const passage = SmartEngine.generateOfflinePassage([item]).find(p => p.level === 'short');
    return {
      id,
      example,
      expected: REVIEWED_MEANING_QUIZZES['v_' + id].byExample[example],
      question: passage.questions[0],
      text: passage.text,
      keys: passage.targetKeys,
    };
  });
}) : [];
JSON.stringify({
  contextualQuestions,
  reviewedDefinitions,
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
if (definitionTrial) {
  assert.equal(result.reviewedDefinitions.length, 10);
  for (const row of result.reviewedDefinitions) {
    assert.equal(row.examples.length, 2, row.id);
    for (const { correct, wrong } of row.examples) {
      assert.equal(correct, row.definition, row.id);
      assert.equal(wrong.length, 3, row.id);
      assert.equal(new Set([correct, ...wrong]).size, 4, row.id);
    }
  }
}
if (meaningTrial) {
  assert.equal(result.contextualQuestions.length, 4);
  for (const { id, example, expected, question, text, keys } of result.contextualQuestions) {
    const word = id === '264' ? '展開' : '破壊';
    assert(text.includes(example.replace(word, '<b>' + word + '</b>')), id);
    assert.deepEqual(keys, ['v:' + id]);
    assert.equal(question.choices[question.answer], expected.correct, id);
    assert.deepEqual([...question.choices].sort(), [expected.correct, ...expected.wrong].sort(), id);
    assert.equal(new Set(question.choices).size, 4, id);
    assert(question.explain.includes(expected.note), id);
  }
}
console.log(JSON.stringify(result, null, 2));
