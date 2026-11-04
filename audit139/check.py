import json,re,hashlib,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parent
old=(ROOT/'JLPT_N1_ukrainian_reading_v138.html').read_text();new=(ROOT/'release139/JLPT_N1_ukrainian_reading_v139.html').read_text()
def get(s,n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
checks=[]
def check(n,fn):
 try:fn();checks.append(dict(name=n,pass_=True))
 except Exception as e:checks.append(dict(name=n,pass_=False,error=str(e)))
def eq(a,b):assert a==b,(str(a)[:250],str(b)[:250])
check('Exact v138 baseline SHA-256',lambda:eq(hashlib.sha256(old.encode()).hexdigest(),'6f7ea6a3d4ca30e8a9cc6ffad31994d99e925809fa4d4b94fe2bf28349027dfc'))
for n in ['GRAMMAR','GRAMMAR_DETAILS_BY_ID','VOCAB_AUDITED_PAIRS','GRAMMAR_AUDITED_PAIRS','AUTO_ANTONYM_PAIRS','REVIEWED_MEANING_QUIZZES','VOCAB_KANA_EXAMPLE_TARGETS','READING_CONTEXT_NOTES','readingBank','VOCAB_POS_BY_ID','LEXICAL_PRESENTATION']:
 check(n+' unchanged',lambda n=n:eq(get(old,n),get(new,n)))
def vocab():
 a=get(old,'DEFAULT_VOCAB');b=get(new,'DEFAULT_VOCAB');assert len(a)==len(b)==3914
 a[715]['w']='恵み';a[715]['c']='名詞(その他)';eq(a,b)
check('Only ID716 headword/category; all IDs/readings stable',vocab)
def details():
 a=get(old,'VOCAB_DETAILS_BY_ID');b=get(new,'VOCAB_DETAILS_BY_ID')
 for k in ['w','t','usage']:a['716'][k]=b['716'][k]
 for k in ['examples','exampleTranslations']:a['790'][k][1]=b['790'][k][1]
 eq(a,b)
check('Only ID716 explanation and ID790 second example/translation',details)
def records():
 a=get(old,'REVIEWED_EXAMPLE_TARGETS');b=get(new,'REVIEWED_EXAMPLE_TARGETS');eq(b[:30],a);assert len(b)==267
 assert len({(x['kind'],x['id'],x['exampleIndex']) for x in b})==267
 for r in b:
  db=get(new,'VOCAB_DETAILS_BY_ID' if r['kind']=='v' else 'GRAMMAR_DETAILS_BY_ID');assert r['sentence']==db[str(r['id'])]['examples'][r['exampleIndex']]
  pos=0
  for form in r['forms']:pos=r['sentence'].index(form,pos)+len(form)
  if 'quiz' in r:q=r['quiz'];assert len(q['wrong'])==3 and len(set([q['correct']]+q['wrong']))==4 and q['note']
check('C04 unchanged; 237 new exact forms and 10 new context quiz sets',records)
def layout():
 eq(old[old.index('<style>'):old.index('</style>')],new[new.index('<style>'):new.index('</style>')])
 for a,b in [('function vocabPartOfSpeech','function getAllItems'),('function renderAutoRecommendations','function escapeLex'),('function renderCardShell','function bindChips'),('function getCardPool','function runTeachPhase')]:eq(old[old.index(a):old.index(b,old.index(a))],new[new.index(a):new.index(b,new.index(a))])
check('Comparison typography, POS/filter/navigation source and CSS unchanged',layout)
check('160 texts and 381 questions unchanged',lambda:eq((sum(len(a) for a in get(new,'readingBank').values()),sum(len(x['questions']) for a in get(new,'readingBank').values() for x in a)),(160,381)))
def context(s):
 a=s.index('  markTarget(sentence, kind, word) {');b=s.index('  boldTarget(sentence, kind, word) {',a)
 return dict(method=s[a:b],helper=s[s.index('function reviewedExampleTarget'):s.index('function quizMeaningOptions')],targets=get(s,'REVIEWED_EXAMPLE_TARGETS'),forms=get(s,'VOCAB_KANA_EXAMPLE_TARGETS'))
payload=dict(old=context(old),now=context(new),v=get(new,'DEFAULT_VOCAB'),oldV=get(old,'DEFAULT_VOCAB'),g=get(new,'GRAMMAR'),vd=get(new,'VOCAB_DETAILS_BY_ID'),oldVd=get(old,'VOCAB_DETAILS_BY_ID'),gd=get(new,'GRAMMAR_DETAILS_BY_ID'),decisions=json.loads((P/'adjudications.json').read_text())['rows'],sha256=hashlib.sha256(new.encode()).hexdigest())
r=subprocess.run(['node',str(P/'scan.cjs')],input=json.dumps(payload,ensure_ascii=False),text=True,capture_output=True)
check('Actual old/new markTarget on all 8089 examples; every C05 decision and exact scope',lambda:eq(r.returncode,0))
if r.returncode==0:(P/'scan-results.json').write_text(r.stdout)
else:print(r.stderr)
(P/'invariant-results.json').write_text(json.dumps(dict(sha256=payload['sha256'],checks=checks),ensure_ascii=False,indent=2));print('Invariant groups',len(checks));print(json.dumps([x for x in checks if not x['pass_']],ensure_ascii=False));assert all(x['pass_'] for x in checks)
