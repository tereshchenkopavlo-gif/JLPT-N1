import json,re,hashlib,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parent
old=(ROOT/'JLPT_N1_ukrainian_reading_v136.html').read_text();new=(ROOT/'release137/JLPT_N1_ukrainian_reading_v137.html').read_text()
def get(s,n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
checks=[]
def check(n,fn):
 try:fn();checks.append(dict(name=n,pass_=True))
 except Exception as e:checks.append(dict(name=n,pass_=False,error=str(e)))
def eq(a,b):assert a==b,(a,b)
check('Exact v136 baseline SHA-256',lambda:eq(hashlib.sha256(old.encode()).hexdigest(),'b2632788ee7f50d6c8872f05c86e006379159afcdad3ced6678c98fca7a6cd2a'))
for n in ['DEFAULT_VOCAB','GRAMMAR','GRAMMAR_DETAILS_BY_ID','VOCAB_AUDITED_PAIRS','GRAMMAR_AUDITED_PAIRS','AUTO_ANTONYM_PAIRS','REVIEWED_MEANING_QUIZZES','VOCAB_KANA_EXAMPLE_TARGETS','READING_CONTEXT_NOTES','readingBank','VOCAB_POS_BY_ID','LEXICAL_PRESENTATION']:
 check(n+' unchanged',lambda n=n:eq(get(old,n),get(new,n)))
def lexical():
 a=get(old,'VOCAB_DETAILS_BY_ID');b=get(new,'VOCAB_DETAILS_BY_ID');a['210']['examples'][1]=b['210']['examples'][1];a['210']['exampleTranslations'][1]=b['210']['exampleTranslations'][1];eq(a,b)
check('Only v210 second example and its translation changed',lexical)
def records():
 rows=get(new,'REVIEWED_EXAMPLE_TARGETS');assert len(rows)==30
 assert len({(x['kind'],x['id'],x['exampleIndex']) for x in rows})==30
 for r in rows:
  db=get(new,'VOCAB_DETAILS_BY_ID' if r['kind']=='v' else 'GRAMMAR_DETAILS_BY_ID')
  assert r['sentence']==db[str(r['id'])]['examples'][r['exampleIndex']]
  assert all(form in r['sentence'] for form in r['forms'])
  q=r['quiz'];assert len(q['wrong'])==3 and len(set([q['correct']]+q['wrong']))==4 and q['note']
check('30 exact sentence-bound forms and contextual questions',records)
def layout():
 for a,b in [('function vocabPartOfSpeech','function getAllItems'),('function renderAutoRecommendations','function escapeLex'),('function renderCardShell','function bindChips'),('function getCardPool','function runTeachPhase')]:
  eq(old[old.index(a):old.index(b,old.index(a))],new[new.index(a):new.index(b,new.index(a))])
 eq(old[old.index('<style>'):old.index('</style>')],new[new.index('<style>'):new.index('</style>')])
check('All v136 presentation/POS/filter/navigation source and CSS unchanged',layout)
check('160 texts, 381 questions',lambda:eq((sum(len(a) for a in get(new,'readingBank').values()),sum(len(x['questions']) for a in get(new,'readingBank').values() for x in a)),(160,381)))
# Full-scan executes the actual old/new markTarget source rather than a reimplementation.
def context(s,include):
 a=s.index('  markTarget(sentence, kind, word) {');b=s.index('  boldTarget(sentence, kind, word) {',a)
 helper=s[s.index('function reviewedExampleTarget'):s.index('function quizMeaningOptions')] if include else ''
 return dict(method=s[a:b],helper=helper,targets=get(s,'REVIEWED_EXAMPLE_TARGETS') if include else [],forms=get(s,'VOCAB_KANA_EXAMPLE_TARGETS'))
payload=dict(old=context(old,False),now=context(new,True),v=get(new,'DEFAULT_VOCAB'),g=get(new,'GRAMMAR'),vd=get(new,'VOCAB_DETAILS_BY_ID'),oldVd=get(old,'VOCAB_DETAILS_BY_ID'),gd=get(new,'GRAMMAR_DETAILS_BY_ID'),sha256=hashlib.sha256(new.encode()).hexdigest())
r=subprocess.run(['node',str(P/'scan.cjs')],input=json.dumps(payload,ensure_ascii=False),text=True,capture_output=True)
check('All 8089 examples: 30 exact fixes, zero unmarked, 526 single-character candidates unchanged; 90 negative scope checks',lambda:eq(r.returncode,0))
if r.returncode==0:(P/'scan-results.json').write_text(r.stdout)
else:print(r.stderr)
(P/'invariant-results.json').write_text(json.dumps(dict(sha256=payload['sha256'],checks=checks),ensure_ascii=False,indent=2));print('Invariant groups',len(checks));print(json.dumps([x for x in checks if not x['pass_']],ensure_ascii=False));assert all(x['pass_'] for x in checks)
