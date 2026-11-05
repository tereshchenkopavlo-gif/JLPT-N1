from pathlib import Path
import json,re,hashlib,runpy,subprocess
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit143';old=(ROOT/'JLPT_N1_ukrainian_reading_v142.html').read_text();new=(ROOT/'release143/JLPT_N1_ukrainian_reading_v143.html').read_text();a=runpy.run_path(str(P/'author.py'))
def data(s,n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
checks=[]
def check(n,ok):
 assert ok,n
 checks.append(dict(name=n,pass_=True))
check('Exact published v142 base',hashlib.sha256(old.encode()).hexdigest()=='b2064d5a6201bfea593b9a131e56b38ed44347bf74ba820b769120bfc04e57be')
for n in ['DEFAULT_VOCAB','GRAMMAR','VOCAB_DETAILS_BY_ID','GRAMMAR_DETAILS_BY_ID','VOCAB_POS_BY_ID','VOCAB_HEADWORD_ALIASES','VOCAB_KANA_EXAMPLE_TARGETS','REVIEWED_EXAMPLE_TARGETS','REVIEWED_READING_OPTIONS','VOCAB_AUDITED_PAIRS','GRAMMAR_AUDITED_PAIRS','AUTO_ANTONYM_PAIRS','readingBank']:
 check(n+' unchanged',data(old,n)==data(new,n))
p=data(old,'REVIEWED_MEANING_QUIZZES');q=data(new,'REVIEWED_MEANING_QUIZZES');keys={'g_'+str(i)for i in a['IDS']}
check('All 281 previous JSON sets unchanged; exactly 51 added grammar keys',set(q)-set(p)==keys and all(q[k]==v for k,v in p.items()) and len(p)==281 and len(q)==332)
g=data(new,'GRAMMAR_DETAILS_BY_ID')
check('All 102 examples bound: 47 byExample keys and four preserved exact C04 contexts',sum(len(g[str(i)]['examples'])for i in a['IDS'])==102 and all(set(q['g_'+str(i)]['byExample'])==({g[str(i)]['examples'][1]}if i not in a['RETAINED_C04_SECOND_IDS']else set())for i in a['IDS']))
def scrub(s):
 m=re.search(r'const REVIEWED_MEANING_QUIZZES\s*=\s*',s);_,end=json.JSONDecoder().raw_decode(s[m.end():]);return s[:m.end()]+'DATA'+s[m.end()+end:]
check('Every other HTML/JS/CSS/storage byte unchanged except version label',scrub(old).replace('学習アプリ · v142','学習アプリ · v143')==scrub(new))
check('3914 words /130 grammar /160 texts /381 reading questions',len(data(new,'DEFAULT_VOCAB'))==3914 and len(data(new,'GRAMMAR'))==130 and sum(map(len,data(new,'readingBank').values()))==160 and sum(len(x['questions'])for group in data(new,'readingBank').values()for x in group)==381)
subprocess.run(['python',str(P/'review.py')],check=True)
review=json.loads((P/'editorial-review.json').read_text());check('Author evidence binds 51 sets /102 contexts; not independent acceptance',review['sets']==51 and review['contexts']==102 and not review['independentReview'])
previous=json.loads((ROOT/'completion/C11-grammar-v142-result.json').read_text());check('Exactly the remaining 51 prior diagnostic IDs, not an invented denominator',set(a['IDS'])=={int(x.split(':')[1])for x in previous['remainingPriorFlaggedCases']})
manifest=json.loads((P/'baseline-integrity.json').read_text());bad=[]
for row in manifest['files']:
 b=(ROOT/row['path']).read_bytes();sha=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
 if sha!=row['gitBlobSha']:bad.append(row['path'])
check('All '+str(len(manifest['files']))+' previous tracked release/audit files and register preserved',not bad)
with (ROOT/'completion/review-register.csv').open()as f:
 import csv,collections
 rows=list(csv.DictReader(f));counts=dict(collections.Counter(x['finalReview']for x in rows))
check('Prior 325 credits /5517 pending /5842 rows unchanged',len(rows)==5842 and counts=={'reviewed':325,'pending':5517})
(P/'invariant-results.json').write_text(json.dumps(dict(sha256=hashlib.sha256(new.encode()).hexdigest(),pass_=True,checks=checks,previousFilesChecked=len(manifest['files'])),ensure_ascii=False,indent=2)+'\n');print('PASS',len(checks),'invariant groups;',len(manifest['files']),'prior files preserved')
