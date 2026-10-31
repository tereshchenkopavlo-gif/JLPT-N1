"""Rebuild the pinned 1.0 baseline inventory. Does not mark semantic work completed."""
from pathlib import Path
import json,re,hashlib,csv,io,subprocess
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'completion'
BASE='JLPT_N1_ukrainian_reading_v135.html';EXPECTED='142c5b7d3ad77b034d17778885de83fd928cdd2c99d1f06c9ad3012012353a12'
s=(ROOT/BASE).read_text();assert hashlib.sha256(s.encode()).hexdigest()==EXPECTED
get=lambda n:json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
v,g,vd,gd,bank,vp,gp,ap,quizzes=[get(n) for n in ['DEFAULT_VOCAB','GRAMMAR','VOCAB_DETAILS_BY_ID','GRAMMAR_DETAILS_BY_ID','readingBank','VOCAB_AUDITED_PAIRS','GRAMMAR_AUDITED_PAIRS','AUTO_ANTONYM_PAIRS','REVIEWED_MEANING_QUIZZES']]
assert len(v)==3914 and len(g)==130 and len(vp)==859 and len(gp)==92 and len(ap)==41
assert len({x['id'] for x in v})==3914 and len({x['id'] for x in g})==130
rows=[]
def add(kind,key,loc):rows.append(dict(kind=kind,key=key,baselineLocation=loc,finalReview='pending',evidence=''))
for kind,arr in [('vocab',v),('grammar',g)]:
 for x in arr:add(kind,str(x['id']),f'{kind}:{x["id"]}')
for i,x in enumerate(vp):add('vocab_pair',f'{i}:{x["a"]}:{x["b"]}',f'VOCAB_AUDITED_PAIRS[{i}]')
for i,x in enumerate(gp):add('grammar_pair',str(i),f'GRAMMAR_AUDITED_PAIRS[{i}]')
for i,x in enumerate(ap):add('antonym_pair',str(i),f'AUTO_ANTONYM_PAIRS[{i}]')
readings=[];grammar_contexts={x['id']:[] for x in g}
for level,arr in bank.items():
 for i,x in enumerate(arr):
  key=x.get('id') or f'legacy-{level}-{i+1:02}'
  add('reading',key,f'readingBank.{level}[{i}]')
  for j,q in enumerate(x['questions']):add('reading_question',key+f':q{j+1}',f'readingBank.{level}[{i}].questions[{j}]')
  readings.append(dict(key=key,inHtmlId=x.get('id'),level=level,index=i,title=x['title'],jaSha256=hashlib.sha256(x['ja'].encode()).hexdigest(),questions=len(x['questions']),source=x.get('source','legacy'),contextNotes=len(x.get('contextNotes',[]))))
  for note in x.get('contextNotes',[]):
   if note['kind']=='g':grammar_contexts[int(note['id'])].append(dict(readingKey=key,quote=note['quote'],meaning=note['meaning']))
for key in sorted(quizzes):add('reviewed_meaning_quiz',key,'REVIEWED_MEANING_QUIZZES.'+key)
assert len(rows)==5842 and len({(r['kind'],r['key']) for r in rows})==len(rows)
# Separate register: do not reset manually recorded progress when rebuilding a baseline.
register=P/'review-register.csv'
initial=io.StringIO();w=csv.DictWriter(initial,fieldnames=list(rows[0]),lineterminator="\n");w.writeheader();w.writerows(rows)
if not register.exists():register.write_text(initial.getvalue())
else:
 with register.open(newline='') as f:actual=list(csv.DictReader(f))
 assert {(r['kind'],r['key'],r['baselineLocation']) for r in actual}=={(r['kind'],r['key'],r['baselineLocation']) for r in rows},'Register scope drift; review explicitly'
 assert all(r['finalReview'] in {'pending','reviewed','fixed_rechecked','blocked'} for r in actual)
 assert all(r['evidence'] for r in actual if r['finalReview'] in {'reviewed','fixed_rechecked'})
method=s[s.index('  markTarget(sentence, kind, word) {'):s.index('  boldTarget(sentence, kind, word) {')]
scan=json.loads(subprocess.run(['node',str(P/'scan-targets.cjs')],input=json.dumps(dict(method=method,forms=get('VOCAB_KANA_EXAMPLE_TARGETS'),v=v,g=g,vd=vd,gd=gd),ensure_ascii=False),text=True,capture_output=True,check=True).stdout)
scan['htmlSha256']=EXPECTED;scan['scope']='actual markTarget matching only; candidates are not confirmed semantic errors'
(P/'target-diagnostics.json').write_text(json.dumps(scan,ensure_ascii=False,indent=2))
(P/'reading-inventory.json').write_text(json.dumps(readings,ensure_ascii=False,indent=2))
contexts=[dict(id=x['id'],label=x['w'],reviewedContextOccurrences=grammar_contexts[x['id']],hasAuthoredContextNote=bool(grammar_contexts[x['id']]),senseReview='pending') for x in g]
(P/'grammar-contexts.json').write_text(json.dumps(contexts,ensure_ascii=False,indent=2))
counts=dict(vocab=len(v),grammar=len(g),vocabPairs=len(vp),grammarPairs=len(gp),antonymPairs=len(ap),medium=len(bank['medium']),long=len(bank['long']),readings=len(readings),readingQuestions=sum(x['questions'] for x in readings),reviewedMeaningQuizzes=len(quizzes),finalRegisterRows=len(rows),grammarWithAuthoredContextNotes=sum(x['hasAuthoredContextNote'] for x in contexts))
summary=dict(baseline=BASE,htmlSha256=EXPECTED,sourceCommit='031f227ea9c1e404e0d5f267bd0f2f1455b18ac0',counts=counts,remainingReadingSlots=dict(medium=120-counts['medium'],long=80-counts['long']),missingGrammarContextIds=[x['id'] for x in contexts if not x['hasAuthoredContextNote']],diagnostics=dict(examples=scan['examples'],byKind=scan['byKind'],unmarked=len(scan['unmarked']),singleCharacterCandidates=len(scan['singleCharacter'])),semanticCompletionClaim=False)
(P/'baseline.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False,indent=2))
