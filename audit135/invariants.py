import json,re,hashlib
from pathlib import Path
P=Path('audit135');basepath=Path('JLPT_N1_ukrainian_reading_v134.html')
if not basepath.exists():basepath=Path('JLPT_N1_ukrainian_reading_v134.html')
a=basepath.read_text();b=Path('release135/JLPT_N1_ukrainian_reading_v135.html').read_text();results=[]
def check(name,fn):
 try:fn();results.append(dict(name=name,pass_=True))
 except Exception as e:results.append(dict(name=name,pass_=False,error=str(e)))
def eq(x,y):assert x==y,(x,y)
def get(s,n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
old=get(a,'readingBank');new=get(b,'readingBank');added=json.loads((P/'new-readings.json').read_text());coverage=json.loads((P/'coverage.json').read_text())
check('Exact v134 baseline SHA-256',lambda:eq(hashlib.sha256(a.encode()).hexdigest(),'4b5be94dd862493ddde4ed3d893168b9d58dbea85a75b0341cd83e8735f96514'))
check('All 142 existing texts and 339 questions unchanged',lambda:eq({k:v[:len(old[k])] for k,v in new.items()},old))
check('99 medium, 61 long, 381 total questions',lambda:eq((len(new['medium']),len(new['long']),sum(len(x['questions']) for v in new.values() for x in v)),(99,61,381)))
for n in ['DEFAULT_VOCAB','VOCAB_DETAILS_BY_ID','GRAMMAR','GRAMMAR_DETAILS_BY_ID','VOCAB_AUDITED_PAIRS','REVIEWED_MEANING_QUIZZES','VOCAB_KANA_EXAMPLE_TARGETS','AUTO_ANTONYM_PAIRS','READING_CONTEXT_NOTES']:
 check(n+' unchanged data and IDs',lambda n=n:eq(get(a,n),get(b,n)))
def shape():
 ids=set();texts=set();titles=set()
 for level,entries in new.items():
  for x in entries:
   assert x['ja'] not in texts and x['title'] not in titles,(level,x['title']);texts.add(x['ja']);titles.add(x['title'])
   if x.get('id'):assert x['id'] not in ids;ids.add(x['id'])
   if x.get('source')!='original_v135':continue
   assert len(x['questions'])==(2 if level=='medium' else 3)
   assert 350<=len(x['ja'])<=650 if level=='medium' else 800<=len(x['ja'])<=1200
   assert x['ja'].count('\n\n')==x['uk'].count('\n\n')
   assert len({(n['kind'],n['id']) for n in x['contextNotes']})==len(x['contextNotes'])
   for q in x['questions']:
    assert len(set(q['choices']))==len(q['choices'])==4 and q['answer'] in range(4)
    assert q['evidence'] in x['ja'] and re.search('[іїєґ]',q['explain'],re.I)
   for note in x['contextNotes']:assert note['quote'] in x['ja'] and note['meaning']
 assert len(ids)==114
check('Unique IDs/titles/bodies, length, paragraph alignment, evidence, four distinct choices, glossary',shape)
def scope():
 def norm(s):
  x=s.index('    const readingBank = {');y=s.index('    const makeIntegrated',x);return s[:x]+s[y:]
 eq(norm(a),norm(b).replace('学習アプリ · v135','学習アプリ · v134'))
check('Outside reading bank only version changed: all CSS, logic, storage and planner byte-identical',scope)
def words():
 v={x['id']:x['w'] for x in get(b,'DEFAULT_VOCAB')};g={x['id']:x['w'] for x in get(b,'GRAMMAR')}
 assert len(v)==3914 and len(g)==130
 for c in coverage:
  assert c['label']==(v if c['kind']=='v' else g)[c['itemId']]
  if c['kind']=='v':assert c['label']==c['quote']
check('All coverage refers to actual stable IDs and exact lexical forms',words)
def answer_mapping():
 source={x['id']:x for x in added}
 generated={x['id']:x for group in new.values() for x in group if x.get('source')=='original_v135'}
 assert set(source)==set(generated)
 for rid,x in source.items():
  target=generated[rid]
  assert len(x['questions'])==len(target['questions'])
  for orig,built in zip(x['questions'],target['questions']):
   assert orig['choices'][orig['answer']]==built['choices'][built['answer']],rid
   assert set(orig['choices'])==set(built['choices']),rid
   assert orig['prompt']==built['prompt'] and orig['explain']==built['explain'],rid
   assert orig['evidence']==built['evidence'],rid
check('Question answer keys and explanations preserved through option rotation',answer_mapping)
def positions():
 answers=[q['answer'] for k,arr in new.items() for x in arr[len(old[k]):] for q in x['questions']]
 eq(set(answers),{0,1,2,3})
check('New source answer keys use all four positions',positions)
(P/'invariant-results.json').write_text(json.dumps(dict(sha256=hashlib.sha256(b.encode()).hexdigest(),checks=results),ensure_ascii=False,indent=2));print(json.dumps(results,ensure_ascii=False,indent=2));assert all(x['pass_'] for x in results)
