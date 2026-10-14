import fs from 'node:fs';
import assert from 'node:assert/strict';

const html = fs.readFileSync(new URL('../JLPT_N1_ukrainian_reading_v26.html', import.meta.url), 'utf8');
const vocabularyMatch = html.match(/const VOCAB_DETAILS_BY_ID = (\{.*?\});\s*const SPECIAL_VOCAB_DICT/s);
assert(vocabularyMatch, 'Vocabulary data block missing');
const vocab = JSON.parse(vocabularyMatch[1]);
const ids = Object.keys(vocab).map(Number).sort((a,b)=>a-b);
assert.equal(ids.length, 3914, 'Vocabulary item count');
assert(ids.every((id,i)=>id===i+1), 'Vocabulary IDs must be 1–3914');

for (const [id, entry] of Object.entries(vocab)) {
  for(const field of ['w','m','t']) assert.equal(typeof entry[field],'string', `Vocabulary ${id}: ${field} missing`);
  for(const field of ['w','m','t']) assert(entry[field].trim(), `Vocabulary ${id}: empty ${field}`);
  assert(Array.isArray(entry.s), `Vocabulary ${id}: relations must be an array`);
  assert(Array.isArray(entry.examples) && entry.examples.length===2 && entry.examples.every(s=>typeof s==='string' && s.trim()), `Vocabulary ${id}: exactly 2 non-empty examples required`);
}
const grammarMatch=html.match(/const GRAMMAR_DETAILS_BY_ID = \{([\s\S]*?)\n\};\s*\/\/ 主要カタカナ語/);
assert(grammarMatch, 'Grammar data block missing');
const grammarIds=[...grammarMatch[1].matchAll(/^\s*(\d+):\s*\{/gm)].map(x=>Number(x[1]));
assert.equal(grammarIds.length,130,'Grammar item count');
assert(grammarIds.every((id,i)=>id===i+1),'Grammar IDs must be 1–130');

const rows=fs.readFileSync(new URL('../audit/audit-log.csv',import.meta.url),'utf8').trim().split(/\r?\n/);
assert.equal(rows.length,4045,'Audit ledger must have header + 4044 entries');
const ledgerKeys=new Set();
for(const [i,row] of rows.slice(1).entries()) {
  const match=row.match(/^(vocab|grammar),(\d+),(pending|needs_review|passed|fixed),/);
  assert(match,`Audit ledger row ${i+2} malformed`);
  const key=`${match[1]}:${match[2]}`;
  assert(!ledgerKeys.has(key),`Duplicate ledger key: ${key}`);
  ledgerKeys.add(key);
}
for(let id=1;id<=3914;id++) assert(ledgerKeys.has(`vocab:${id}`),`Missing vocab audit entry ${id}`);
for(let id=1;id<=130;id++) assert(ledgerKeys.has(`grammar:${id}`),`Missing grammar audit entry ${id}`);

const byWord=new Map();
for(const [id, entry] of Object.entries(vocab)) byWord.set(entry.w,[...(byWord.get(entry.w)||[]),id]);
const repeats=[...byWord.entries()].filter(([word,ids])=>ids.length>1);
console.log('PASS: 3914 vocabulary entries, 130 grammar entries, 4044 audit rows.');
console.log('Repeated headwords for manual examination:', JSON.stringify(repeats));
console.log('NOTE: Semantic correctness is NOT checked automatically.');
