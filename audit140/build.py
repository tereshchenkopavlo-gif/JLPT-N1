from pathlib import Path
import json,re,hashlib,copy
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit140';R=ROOT/'release140';R.mkdir(exist_ok=True)
base=(ROOT/'JLPT_N1_ukrainian_reading_v139.html').read_text();assert hashlib.sha256(base.encode()).hexdigest()=='e18ab0ee3ec3a56dced31b9abb6ec4813d92c102f93f20922e3dc05718d1dd17'
def get(n):return json.JSONDecoder().raw_decode(base[re.search(r'const '+n+r'\s*=\s*',base).end():])[0]
def replace_data(s,n,d):
 m=re.search(r'const '+n+r'\s*=\s*',s);_,end=json.JSONDecoder().raw_decode(s[m.end():]);return s[:m.end()]+json.dumps(d,ensure_ascii=False,separators=(',',':'))+s[m.end()+end:]
v=get('DEFAULT_VOCAB');vd=get('VOCAB_DETAILS_BY_ID');pos=get('VOCAB_POS_BY_ID');bank=get('readingBank');aliases=[]
for x in v:
 if 'ナ形' in pos[str(x['id'])] and x['w'].endswith('な'):
  assert x['r'].endswith('な');aliases.append(dict(id=x['id'],oldWord=x['w'],oldReading=x['r'],word=x['w'][:-1],reading=x['r'][:-1]));x['w']=x['w'][:-1];x['r']=x['r'][:-1];vd[str(x['id'])]['w']=x['w']
assert len(aliases)==286
rename={x['oldWord']:x['word'] for x in aliases};byid={str(x['id']):x for x in v}
ns=dict(P=P);exec((P/'author.py').read_text(),ns);glosses=ns['glosses'];overrides=ns['note_overrides'];assert len(glosses)==228
changed_notes=[];changed_texts=[]
for level,items in bank.items():
 for ix,r in enumerate(items):
  if r.get('id')=='m130-11':
   old='止めた後の扱いがあってこそ';new='止めた後の扱いがあればこそ';assert old in r['ja'];r['ja']=r['ja'].replace(old,new);r['questions'][1]['evidence']=new
   n=next(n for n in r['contextNotes'] if n['kind']=='g' and n['id']=='9');n['quote']='扱いがあればこそ';changed_texts.append(r['id'])
  for ni,n in enumerate(r.get('contextNotes',[])):
   if n['kind']=='v':
    n['label']=byid[n['id']]['w'];
    if (r['id'],n['id']) in ns['context_overrides']:n['context']=ns['context_overrides'][(r['id'],n['id'])]
    n['translation']=overrides.get((r['id'],n['id']),glosses[n['id']]);changed_notes.append(dict(readingId=r['id'],index=ni,id=n['id'],translation=n['translation'],context=n['meaning']))
# Exact spelling references change; sentences/forms stay source-bound and unchanged.
kana=get('VOCAB_KANA_EXAMPLE_TARGETS');kana={rename.get(k,k):val for k,val in kana.items()}
exact=get('REVIEWED_EXAMPLE_TARGETS')
for row in exact:
 if row['kind']=='v':row['word']=rename.get(row['word'],row['word'])
auto=get('AUTO_VOCAB_COMPARISONS');auto={rename.get(k,k):[dict(row,label=rename.get(row['label'],row['label'])) for row in rows] for k,rows in auto.items()}
antonyms=[[rename.get(w,w) for w in pair] for pair in get('AUTO_ANTONYM_PAIRS')]
for d in vd.values():d['s']=[rename.get(w,w) for w in d.get('s',[])]
s=base
for n,d in [('DEFAULT_VOCAB',v),('VOCAB_DETAILS_BY_ID',vd),('VOCAB_KANA_EXAMPLE_TARGETS',kana),('REVIEWED_EXAMPLE_TARGETS',exact),('AUTO_VOCAB_COMPARISONS',auto),('AUTO_ANTONYM_PAIRS',antonyms),('readingBank',bank)]:s=replace_data(s,n,d)
# Legacy labels remain resolvable; only exact known built-in tuples in old custom data normalize.
helper='const VOCAB_HEADWORD_ALIASES = '+json.dumps(aliases,ensure_ascii=False,separators=(',',':'))+''';
function canonicalVocabLabel(label) { return VOCAB_HEADWORD_ALIASES.find(x=>x.oldWord===label)?.word || label; }
function normalizeLegacyVocabRow(row) {
  const old=VOCAB_HEADWORD_ALIASES.find(x=>String(x.id)===String(row.id)&&x.oldWord===row.w&&x.oldReading===row.r);
  return old ? {...row,w:old.word,r:old.reading} : row;
}
'''
s=s.replace('let ACTIVE_VOCAB = [...DEFAULT_VOCAB];',helper+'let ACTIVE_VOCAB = [...DEFAULT_VOCAB];')
s=s.replace('parsed.map(it => ({ ...it, tags: enrichItemTags(it) }))','parsed.map(normalizeLegacyVocabRow).map(it => ({ ...it, tags: enrichItemTags(it) }))')
s=s.replace("    const cleanWord = word.replace(/^[〜～]/, '');","    if (kind === 'v') word=canonicalVocabLabel(word);\n    const cleanWord = word.replace(/^[〜～]/, '');",1)
s=s.replace("  return getAllItems().find(it => it.label === label && (!kind || it.kind === kind));","  return getAllItems().find(it => it.label === label && (!kind || it.kind === kind)) || getAllItems().find(it => it.kind==='v' && (!kind || kind==='v') && it.label === canonicalVocabLabel(label));")
word=next(x for x in v if x['w']=='著しい');readingOptions={str(word['id']):dict(word=word['w'],correct=word['r'],wrong=ns['reading_for_ichijirushii'])};assert word['r']=='いちじるしい'
helper='const REVIEWED_READING_OPTIONS = '+json.dumps(readingOptions,ensure_ascii=False,separators=(',',':'))+';\n'+(P/'runtime.js').read_text()+'\n'
s=s.replace('const SmartEngine = {',helper+'const SmartEngine = {')
s=s.replace("if (real && found && !reviewedExampleTarget(ex,it.kind,label) && !REVIEWED_MEANING_QUIZZES[it.kind+'_'+it.id]) types.push('cloze');","const clozeCandidates=clozeWordCandidates(it);\n        if (real && found && literalClozeAvailable(ex,it,this) && clozeCandidates.length>=3 && !reviewedExampleTarget(ex,it.kind,label) && !REVIEWED_MEANING_QUIZZES[it.kind+'_'+it.id]) types.push('cloze');")
a=s.index('        const isPrefix = /^[〜～]/.test(label);');b=s.index("        const type = types.length",a)
s=s[:a]+"        const readingCandidates=real ? quizReadingOptions(it) : [];\n        if (readingCandidates.length>=3 && (!reviewedExampleTarget(ex,it.kind,label) || reviewedExampleTarget(ex,it.kind,label).forms.some(hasKanji))) types.push('reading');\n"+s[b:]
a=s.index('          let cand;',s.index("} else if (type === 'cloze')"));b=s.index('          const opts = shuffleArray([correct, ...wrong]);',a)
s=s[:a]+"          const correct = label;\n          const wrong = shuffleArray(clozeCandidates.filter(c=>c!==correct)).slice(0,3);\n"+s[b:]
s=s.replace("it.kind === 'g' ? '空欄に入る文法表現として最も適切なものはどれか。' : '空欄の部分に対応する語（辞書形・基本形）として最も適切なものはどれか。'","'空欄に入る語として最も適切なものはどれか。'")
a=s.index('          const len = correct.length;',s.index('} else { // reading'));b=s.index('          const opts = shuffleArray([correct, ...wrong]);',a)
s=s[:a]+"          const wrong = shuffleArray(readingCandidates).slice(0,3);\n"+s[b:]
s=s.replace('meaning: note.meaning, quote: note.quote','meaning: note.meaning, translation: note.translation, context: note.context, quote: note.quote')
old="${(p.glossary || []).map(g => `<div><b>${escapeLex(g.label)}</b>${g.quote ? `<div lang=\"ja\">${escapeLex(g.quote)}</div>` : ''}<span>${escapeLex(g.meaning)}</span></div>`).join('')}"
assert old in s;s=s.replace(old,"${(p.glossary || []).map(readingGlossaryEntryHtml).join('')}")
# New canonical headings can coincide; ratings must use the existing kind/ID, not text.
s=s.replace("targetIds: grp.map(g => g.it.word.w),", "targetIds: grp.map(g => g.it.word.w),\n        targetKeys: grp.map(g => g.it.kind+':'+g.it.id),")
s=s.replace("const currentTargets = matched.filter(x => currentIds.has(`${x.it.kind}:${x.it.id}`)).map(x => x.it.word.w);", "const currentMatches = matched.filter(x => currentIds.has(`${x.it.kind}:${x.it.id}`));\n      const currentTargets = currentMatches.map(x=>x.it.word.w);\n      const currentTargetKeys = [...new Set(currentMatches.map(x=>x.it.kind+':'+x.it.id))];")
s=s.replace("translation: chosen.uk, targetIds: currentTargets,", "translation: chosen.uk, targetIds: currentTargets, targetKeys: currentTargetKeys,")
s=s.replace("const targetItems = (p.targetIds || []).map(label => findItemByLabel(label)).filter(Boolean);", "const targetItems = Array.isArray(p.targetKeys)\n    ? p.targetKeys.map(key=>{const [kind,id]=key.split(':');return curSession.items.find(it=>it.kind===kind&&String(it.id)===id)}).filter(Boolean)\n    : (p.targetIds || []).map(label => findItemByLabel(label)).filter(Boolean);")
s=s.replace('学習アプリ · v139','学習アプリ · v140')
(R/'JLPT_N1_ukrainian_reading_v140.html').write_text(s);(P/'app.js').write_text(s.split('<script>',1)[1].split('</script>',1)[0])
for name,d in [('aliases.json',aliases),('glossary-review.json',changed_notes),('reading-options.json',readingOptions)]: (P/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
summary=dict(version=140,baseSha256=hashlib.sha256(base.encode()).hexdigest(),sha256=hashlib.sha256(s.encode()).hexdigest(),bytes=len(s.encode()),normalizedHeadwords=len(aliases),lexicalGlosses=len(changed_notes),uniqueGlossIds=len(glosses),changedReadings=changed_texts,readingOptionIds=list(readingOptions))
(P/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps(summary))
