from pathlib import Path
import json,re,hashlib,runpy,csv,subprocess,collections
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit145';a=runpy.run_path(str(P/'author.py'));old=(ROOT/'JLPT_N1_ukrainian_reading_v144.html').read_text();new=(ROOT/'release145/JLPT_N1_ukrainian_reading_v145.html').read_text()
def data(s,n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
checks=[]
def check(n,ok):
 assert ok,n
 checks.append(dict(name=n,pass_=True))
check('Exact published v144 base',hashlib.sha256(old.encode()).hexdigest()=='901ce33485bf5d42e928324c54f02d77661dc5d82456680693fb486e372e17d4')
for n in ['DEFAULT_VOCAB','GRAMMAR','VOCAB_DETAILS_BY_ID','VOCAB_POS_BY_ID','VOCAB_HEADWORD_ALIASES','VOCAB_KANA_EXAMPLE_TARGETS','REVIEWED_EXAMPLE_TARGETS','REVIEWED_READING_OPTIONS','VOCAB_AUDITED_PAIRS','AUTO_ANTONYM_PAIRS','readingBank','REVIEWED_MEANING_QUIZZES']:
 check(n+' unchanged',data(old,n)==data(new,n))
g=data(old,'GRAMMAR_DETAILS_BY_ID');p=data(old,'GRAMMAR_AUDITED_PAIRS');a['revise'](g,p)
check('Only explicitly authored 34 grammar cards and 37 pair notes changed',g==data(new,'GRAMMAR_DETAILS_BY_ID')and p==data(new,'GRAMMAR_AUDITED_PAIRS'))
oldg=data(old,'GRAMMAR_DETAILS_BY_ID');check('All Japanese card examples unchanged',all(g[k]['examples']==oldg[k]['examples']for k in g))
check('Exactly four Ukrainian translations changed',sum(x!=y for k in g for x,y in zip(g[k]['exampleTranslations'],oldg[k]['exampleTranslations']))==4)
def scrub(s):
 for n in ['GRAMMAR_DETAILS_BY_ID','GRAMMAR_AUDITED_PAIRS']:
  m=re.search('const '+n+r'\s*=\s*',s);_,end=json.JSONDecoder().raw_decode(s[m.end():]);s=s[:m.end()]+'DATA'+s[m.end()+end:]
 return s
check('All runtime, storage, CSS and other HTML bytes unchanged except version',scrub(old).replace('学習アプリ · v144','学習アプリ · v145')==scrub(new))
check('3914 words /130 grammar /160 texts /381 reading questions',len(data(new,'DEFAULT_VOCAB'))==3914 and len(data(new,'GRAMMAR'))==130 and sum(map(len,data(new,'readingBank').values()))==160 and sum(len(x['questions'])for group in data(new,'readingBank').values()for x in group)==381)
subprocess.run(['python',str(P/'review.py')],check=True);r=json.loads((P/'editorial-review.json').read_text());check('Field-specific author evidence, 34 cards and 37 pairs, not independent',r['grammarCards']==34 and r['grammarPairs']==37 and not r['independentReview'])
manifest=json.loads((P/'baseline-integrity.json').read_text());bad=[]
for row in manifest['files']:
 b=(ROOT/row['path']).read_bytes();sha=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
 if sha!=row['gitBlobSha']:bad.append(row['path'])
check('All previous frozen tracked files unchanged',not bad)
basecsv=subprocess.check_output(['git','show',manifest['commit']+':completion/review-register.csv'],cwd=ROOT,text=True);before=list(csv.DictReader(basecsv.splitlines()));after=list(csv.DictReader((ROOT/'completion/review-register.csv').open()));targets={(x['kind'],x['key'])for x in r['rows']+r['pairs']};assert len(targets)==71
check('5842 register rows, keys/order preserved; all 325 previous credits unchanged',len(before)==len(after)==5842 and all(x==y or(x['kind'],x['key'])in targets for x,y in zip(before,after))and all(y==x for x,y in zip(before,after)if x['finalReview']=='reviewed'))
counts=dict(collections.Counter(x['finalReview']for x in after));check('Register either pre-publication or exactly 71 new author credits',counts in [{'reviewed':325,'pending':5517},{'reviewed':396,'pending':5446}])
(P/'invariant-results.json').write_text(json.dumps(dict(sha256=hashlib.sha256(new.encode()).hexdigest(),pass_=True,checks=checks,previousFilesChecked=len(manifest['files']),registerCounts=counts),ensure_ascii=False,indent=2)+'\n');print('PASS',len(checks),'invariant groups;',len(manifest['files']),'previous files preserved')
