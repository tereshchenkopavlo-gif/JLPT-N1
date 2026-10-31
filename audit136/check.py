from pathlib import Path
import json,re,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parent
old=(ROOT/'JLPT_N1_ukrainian_reading_v135.html').read_text();new=(ROOT/'release136/JLPT_N1_ukrainian_reading_v136.html').read_text()
checks=[]
def check(name,fn):
 try:fn();checks.append(dict(name=name,pass_=True))
 except Exception as e:checks.append(dict(name=name,pass_=False,error=str(e)))
def eq(a,b):assert a==b,(a,b)
def get(s,n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
check('Exact v135 baseline',lambda:eq(hashlib.sha256(old.encode()).hexdigest(),'142c5b7d3ad77b034d17778885de83fd928cdd2c99d1f06c9ad3012012353a12'))
for n in ['DEFAULT_VOCAB','VOCAB_DETAILS_BY_ID','GRAMMAR','GRAMMAR_DETAILS_BY_ID','VOCAB_AUDITED_PAIRS','GRAMMAR_AUDITED_PAIRS','AUTO_ANTONYM_PAIRS','READING_CONTEXT_NOTES','REVIEWED_MEANING_QUIZZES','VOCAB_KANA_EXAMPLE_TARGETS','readingBank']:
 check(n+' unchanged, including IDs, examples and all answer keys',lambda n=n:eq(get(old,n),get(new,n)))
def pos():
 a=get(new,'VOCAB_POS_BY_ID');v=get(new,'DEFAULT_VOCAB');assert set(a)=={str(x['id']) for x in v};assert all(x and len(set(x))==len(x) for x in a.values());eq(a['1'],['名詞']);eq(a['3892'],['副詞','ナ形']);eq(a['3815'],['動詞']);assert '名詞' in a['113'] and 'ナ形' in a['113']
check('Complete per-ID POS presentation registry and multiple functions',pos)
def engine():
 def block(s):return s[s.index('const SmartEngine = {'):s.index('const COMPARE_STORAGE_KEY')]
 eq(block(old),block(new))
check('Session generation, target matching and quiz engine byte-identical',engine)
def storage():
 names=['DB_NAME','DB_VERSION','STORE_VOCAB','STORE_GRAMMAR','COMPARE_STORAGE_KEY']
 for n in names:
  pattern=r"(?:const|let) "+n+r"\s*=\s*([^;]+);"
  a=re.search(pattern,old);b=re.search(pattern,new)
  if a:assert b and a.group(0)==b.group(0),n
 literals=lambda s:set(re.findall(r"['\"]([A-Za-z][A-Za-z0-9_]*(?:storage|CompareList)[A-Za-z0-9_]*)['\"]",s))
 assert literals(old);eq(literals(old),literals(new))
check('Existing storage-key references preserved',storage)
check('160 texts and 381 reading questions',lambda:eq((sum(map(len,get(new,'readingBank').values())),sum(len(x['questions']) for a in get(new,'readingBank').values() for x in a)),(160,381)))
check('Only one POS filter and no obsolete example heading',lambda:eq((new.count('id="cardPos"'),'格調高い例文' in new),(1,False)))
(P/'invariant-results.json').write_text(json.dumps(dict(sha256=hashlib.sha256(new.encode()).hexdigest(),checks=checks),ensure_ascii=False,indent=2));print('Invariant groups',len(checks));print(json.dumps([x for x in checks if not x['pass_']],ensure_ascii=False));assert all(x['pass_'] for x in checks)
