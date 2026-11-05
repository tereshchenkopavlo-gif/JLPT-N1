from pathlib import Path
import json,re,hashlib,runpy,csv,subprocess,collections
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit150';a=runpy.run_path(str(P/'author.py'));old=(ROOT/'JLPT_N1_ukrainian_reading_v149.html').read_text();new=(ROOT/'release150/JLPT_N1_ukrainian_reading_v150.html').read_text()
def data(s,n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
checks=[]
def check(n,ok):
 assert ok,n
 checks.append(dict(name=n,pass_=True))
check('Exact published v149 base',hashlib.sha256(old.encode()).hexdigest()=='4490611521fab2c9b713bfda7a39e327b9923e35ea16df5cca6aa1937b51ed38')
for n in ['DEFAULT_VOCAB','GRAMMAR','GRAMMAR_DETAILS_BY_ID','GRAMMAR_AUDITED_PAIRS','VOCAB_POS_BY_ID','VOCAB_HEADWORD_ALIASES','VOCAB_KANA_EXAMPLE_TARGETS','REVIEWED_EXAMPLE_TARGETS','REVIEWED_READING_OPTIONS','VOCAB_AUDITED_PAIRS','AUTO_ANTONYM_PAIRS','readingBank','REVIEWED_MEANING_QUIZZES']:
 check(n+' unchanged',data(old,n)==data(new,n))
old_vocab=data(old,'VOCAB_DETAILS_BY_ID')
new_vocab=data(new,'VOCAB_DETAILS_BY_ID')
expected=data(old,'VOCAB_DETAILS_BY_ID')
a['revise'](expected)
check('Only explicitly authored vocabulary fields changed',new_vocab==expected)
check('All Japanese card examples unchanged',all(new_vocab[k]['examples']==old_vocab[k]['examples'] for k in old_vocab))
check('Exactly thirteen Ukrainian translations changed',sum(x!=y for k in old_vocab for x,y in zip(new_vocab[k]['exampleTranslations'],old_vocab[k]['exampleTranslations']))==13)
def scrub(s):
 m=re.search(r'const VOCAB_DETAILS_BY_ID\s*=\s*',s)
 _,end=json.JSONDecoder().raw_decode(s[m.end():])
 return s[:m.end()]+'DATA'+s[m.end()+end:]
check('All runtime, storage, CSS and other HTML bytes unchanged except version',scrub(old).replace('学習アプリ · v149','学習アプリ · v150')==scrub(new))
check('3914 words /130 grammar /160 texts /381 reading questions',len(data(new,'DEFAULT_VOCAB'))==3914 and len(data(new,'GRAMMAR'))==130 and sum(map(len,data(new,'readingBank').values()))==160 and sum(len(x['questions'])for group in data(new,'readingBank').values()for x in group)==381)
subprocess.run(['python',str(P/'review.py')],check=True);r=json.loads((P/'editorial-review.json').read_text());check('Field-specific author evidence, 30 vocabulary cards, not independent',r['vocabCards']==30 and r['examplesRead']==60 and not r['independentReview'])
manifest=json.loads((P/'baseline-integrity.json').read_text());bad=[]
for row in manifest['files']:
 b=(ROOT/row['path']).read_bytes();sha=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
 if sha!=row['gitBlobSha']:bad.append(row['path'])
check('All previous frozen tracked files unchanged',not bad)
basecsv=subprocess.check_output(['git','show',manifest['commit']+':completion/review-register.csv'],cwd=ROOT,text=True);before=list(csv.DictReader(basecsv.splitlines()));after=list(csv.DictReader((ROOT/'completion/review-register.csv').open()));targets={(x['kind'],x['key'])for x in r['rows']};assert len(targets)==30
check('5842 register rows, keys/order preserved; all 547 previous credits unchanged',len(before)==len(after)==5842 and all(x==y or(x['kind'],x['key'])in targets for x,y in zip(before,after))and all(y==x for x,y in zip(before,after)if x['finalReview']=='reviewed'))
counts=dict(collections.Counter(x['finalReview']for x in after));check('Register either pre-publication or exactly 30 new author credits',counts in [{'reviewed':547,'pending':5295},{'reviewed':577,'pending':5265}])
(P/'invariant-results.json').write_text(json.dumps(dict(sha256=hashlib.sha256(new.encode()).hexdigest(),pass_=True,checks=checks,previousFilesChecked=len(manifest['files']),registerCounts=counts),ensure_ascii=False,indent=2)+'\n');print('PASS',len(checks),'invariant groups;',len(manifest['files']),'previous files preserved')
