from pathlib import Path
import json,re,hashlib,runpy,subprocess
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit142';old=(ROOT/'JLPT_N1_ukrainian_reading_v141.html').read_text();new=(ROOT/'release142/JLPT_N1_ukrainian_reading_v142.html').read_text();a=runpy.run_path(str(P/'author.py'))
def data(s,n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
checks=[]
def check(n,ok):
 assert ok,n
 checks.append(dict(name=n,pass_=True))
check('Exact published v141 base',hashlib.sha256(old.encode()).hexdigest()=='08e016a95f1786f243c29f54289edf5dd65aac4c43c9ff863b25c9f0422f75a3')
for n in ['DEFAULT_VOCAB','GRAMMAR','VOCAB_DETAILS_BY_ID','VOCAB_POS_BY_ID','VOCAB_HEADWORD_ALIASES','VOCAB_KANA_EXAMPLE_TARGETS','REVIEWED_EXAMPLE_TARGETS','REVIEWED_READING_OPTIONS','VOCAB_AUDITED_PAIRS','GRAMMAR_AUDITED_PAIRS','AUTO_ANTONYM_PAIRS','readingBank']:
 check(n+' unchanged',data(old,n)==data(new,n))
p=data(old,'REVIEWED_MEANING_QUIZZES');q=data(new,'REVIEWED_MEANING_QUIZZES');keys={'g_'+str(i)for i in a['IDS']}
check('265 saved vocabulary sets byte-equivalent as parsed; exactly sixteen added grammar keys',set(q)-set(p)==keys and all(q[k]==v for k,v in p.items()) and len(p)==265)
g0=data(old,'GRAMMAR_DETAILS_BY_ID');g=data(new,'GRAMMAR_DETAILS_BY_ID');diff={(i,f)for i in g for f in set(g[i])|set(g0[i])if g[i].get(f)!=g0[i].get(f)}
check('Only five specified fields on four grammar cards changed; all examples/translations retained',diff=={(str(i),f)for i,fields in a['CARD_CHANGES'].items()for f in fields})
check('All 33 exact examples bound; no unknown byExample keys',sum(len(g[str(i)]['examples'])for i in a['IDS'])==33 and all(set(q['g_'+str(i)]['byExample'])==set(g[str(i)]['examples'][1:])for i in a['IDS']))
def scrub(s):
 for n in ['REVIEWED_MEANING_QUIZZES','GRAMMAR_DETAILS_BY_ID']:
  m=re.search(r'const '+n+r'\s*=\s*',s);_,end=json.JSONDecoder().raw_decode(s[m.end():]);s=s[:m.end()]+'DATA'+s[m.end()+end:]
 return s
check('Runtime/UI/CSS/storage unchanged except version label',scrub(old).replace('学習アプリ · v141','学習アプリ · v142')==scrub(new))
check('3914 words /130 grammar /160 texts /381 reading questions',len(data(new,'DEFAULT_VOCAB'))==3914 and len(data(new,'GRAMMAR'))==130 and sum(map(len,data(new,'readingBank').values()))==160 and sum(len(x['questions'])for group in data(new,'readingBank').values()for x in group)==381)
subprocess.run(['python',str(P/'review.py')],check=True)
review=json.loads((P/'editorial-review.json').read_text());check('Author evidence binds 16 sets /33 contexts, not independent acceptance',review['sets']==16 and review['contexts']==33 and not review['independentReview'])
# Completion register must remain identical, preserving all 325 prior credits.
check('Prior completion ledger untouched',hashlib.sha256((ROOT/'completion/review-register.csv').read_bytes()).hexdigest()=='34c13ac15ae20a90843212d45f03d38bfc123e46d1238984f5d50b82343c2f56')
(P/'invariant-results.json').write_text(json.dumps(dict(sha256=hashlib.sha256(new.encode()).hexdigest(),pass_=True,checks=checks),ensure_ascii=False,indent=2)+'\n');print('PASS',len(checks),'invariant groups')
