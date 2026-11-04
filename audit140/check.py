from pathlib import Path
import json,re,hashlib,copy,subprocess
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit140';old=(ROOT/'JLPT_N1_ukrainian_reading_v139.html').read_text();new=(ROOT/'release140/JLPT_N1_ukrainian_reading_v140.html').read_text()
def get(s,n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
checks=[]
def check(n,fn):
 try:fn();checks.append(dict(name=n,pass_=True))
 except Exception as e:checks.append(dict(name=n,pass_=False,error=str(e)))
def eq(a,b):assert a==b,(str(a)[:150],str(b)[:150])
aliases=get(new,'VOCAB_HEADWORD_ALIASES');ren={x['oldWord']:x['word'] for x in aliases};idx={str(x['id']):x for x in aliases}
check('Exact v139 source hash',lambda:eq(hashlib.sha256(old.encode()).hexdigest(),'e18ab0ee3ec3a56dced31b9abb6ec4813d92c102f93f20922e3dc05718d1dd17'))
for n in ['GRAMMAR','GRAMMAR_DETAILS_BY_ID','VOCAB_POS_BY_ID','VOCAB_AUDITED_PAIRS','GRAMMAR_AUDITED_PAIRS','REVIEWED_MEANING_QUIZZES','MEANING_CHOICE_TEXT','READING_CONTEXT_NOTES','LEXICAL_PRESENTATION']:
 check(n+' unchanged',lambda n=n:eq(get(old,n),get(new,n)))
def vocab():
 a=get(old,'DEFAULT_VOCAB');b=get(new,'DEFAULT_VOCAB');assert len(a)==len(b)==3914 and len(aliases)==286
 for r in a:
  if str(r['id'])in idx:x=idx[str(r['id'])];assert r['w']==x['oldWord'] and r['r']==x['oldReading'];r['w']=x['word'];r['r']=x['reading']
 eq(a,b)
check('286 exact NA headwords/readings only; IDs/categories/progress fields unchanged',vocab)
def details():
 a=get(old,'VOCAB_DETAILS_BY_ID')
 for id,d in a.items():
  if id in idx:d['w']=idx[id]['word']
  d['s']=[ren.get(x,x) for x in d.get('s',[])]
 eq(a,get(new,'VOCAB_DETAILS_BY_ID'))
check('Definitions, usage, examples and translations unchanged; headings/synonym labels normalized',details)
def mappings():
 eq({ren.get(k,k):v for k,v in get(old,'VOCAB_KANA_EXAMPLE_TARGETS').items()},get(new,'VOCAB_KANA_EXAMPLE_TARGETS'))
 a=get(old,'REVIEWED_EXAMPLE_TARGETS')
 for r in a:
  if r['kind']=='v':r['word']=ren.get(r['word'],r['word'])
 eq(a,get(new,'REVIEWED_EXAMPLE_TARGETS'));eq([[ren.get(x,x) for x in pair] for pair in get(old,'AUTO_ANTONYM_PAIRS')],get(new,'AUTO_ANTONYM_PAIRS'))
 eq({ren.get(k,k):[dict(r,label=ren.get(r['label'],r['label'])) for r in rows] for k,rows in get(old,'AUTO_VOCAB_COMPARISONS').items()},get(new,'AUTO_VOCAB_COMPARISONS'))
check('Exact forms, quizzes and relation payloads preserved; label references normalized',mappings)
def readings():
 a=get(old,'readingBank');b=get(new,'readingBank');count=0
 for level,items in a.items():
  for i,r in enumerate(items):
   z=b[level][i]
   for ni,n in enumerate(r.get('contextNotes',[])):
    if n['kind']=='v':
     n['label']=ren.get(n['label'],n['label']);n['translation']=z['contextNotes'][ni]['translation'];assert n['translation'];count+=1
     if r.get('id')=='l131-06' and n['id'] in ['303','1750','1691','131']:n['context']=z['contextNotes'][ni]['context']
   if r.get('id')=='m130-11':
    r['ja']=r['ja'].replace('止めた後の扱いがあってこそ','止めた後の扱いがあればこそ');r['questions'][1]['evidence']='止めた後の扱いがあればこそ';next(n for n in r['contextNotes'] if n['kind']=='g' and n['id']=='9')['quote']='扱いがあればこそ'
 eq(a,b);assert count==400
 eq((sum(len(x)for x in b.values()),sum(len(r['questions'])for x in b.values()for r in x)),(160,381))
 for items in b.values():
  for r in items:
   for n in r.get('contextNotes',[]):assert n['quote'] in r['ja']
check('400 lexical translations separated from original context; only m130-11 sentence/evidence/grammar quote changed',readings)
check('CSS unchanged',lambda:eq(old[old.index('<style>'):old.index('</style>')],new[new.index('<style>'):new.index('</style>')]))
check('No dictionary/basic-form workaround in current prompt',lambda:eq('（辞書形・基本形）' in new,False))
def context(s):
 a=s.index('  markTarget(sentence, kind, word) {');b=s.index('  boldTarget(sentence, kind, word) {',a)
 return dict(method=s[a:b],helper=s[s.index('function reviewedExampleTarget'):s.index('function quizMeaningOptions')],targets=get(s,'REVIEWED_EXAMPLE_TARGETS'),forms=get(s,'VOCAB_KANA_EXAMPLE_TARGETS'))
payload=dict(old=context(old),now=context(new),v=get(new,'DEFAULT_VOCAB'),oldV=get(old,'DEFAULT_VOCAB'),g=get(new,'GRAMMAR'),vd=get(new,'VOCAB_DETAILS_BY_ID'),gd=get(new,'GRAMMAR_DETAILS_BY_ID'),aliasIds=[x['id'] for x in aliases],sha256=hashlib.sha256(new.encode()).hexdigest())
r=subprocess.run(['node',str(P/'scan.cjs')],input=json.dumps(payload,ensure_ascii=False),text=True,capture_output=True);check('All 8089 actual markTarget results; no unmarked or out-of-scope changes',lambda:eq(r.returncode,0))
if r.returncode==0:(P/'scan-results.json').write_text(r.stdout)
else:print(r.stderr)
(P/'invariant-results.json').write_text(json.dumps(dict(sha256=payload['sha256'],checks=checks),ensure_ascii=False,indent=2));print('Invariant groups',len(checks),[x for x in checks if not x['pass_']]);assert all(x['pass_']for x in checks)
