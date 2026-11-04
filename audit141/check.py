from pathlib import Path
import json,re,hashlib,subprocess
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit141';old=(ROOT/'JLPT_N1_ukrainian_reading_v140.html').read_text();new=(ROOT/'release141/JLPT_N1_ukrainian_reading_v141.html').read_text()
def data(s,n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
checks=[]
def check(name,condition):
 assert condition,name
 checks.append(dict(name=name,pass_=True))
check('Exact published v140 base',hashlib.sha256(old.encode()).hexdigest()=='810af1aecf5a71b2fbd39b687e3ec310763317cb3f04821107cdeb983c31f537')
for name in ['DEFAULT_VOCAB','GRAMMAR','GRAMMAR_DETAILS_BY_ID','VOCAB_POS_BY_ID','VOCAB_HEADWORD_ALIASES','VOCAB_KANA_EXAMPLE_TARGETS','REVIEWED_EXAMPLE_TARGETS','REVIEWED_READING_OPTIONS','VOCAB_AUDITED_PAIRS','GRAMMAR_AUDITED_PAIRS','AUTO_ANTONYM_PAIRS','readingBank']:
 check(name+' unchanged',data(old,name)==data(new,name))
q=data(new,'REVIEWED_MEANING_QUIZZES');prev=data(old,'REVIEWED_MEANING_QUIZZES')
changed={k for k in q if q[k]!=prev[k]};expected={'v_2200','v_2210','v_2364','v_2399','v_2764','v_3158','v_3707','v_3718','v_3787','v_3817','v_3820','v_3836'}
check('Same 265 saved keys, exactly twelve editorial revisions',q.keys()==prev.keys() and changed==expected)
check('156 sentence overrides, all keyed to current examples',sum(len(x.get('byExample',{}))for x in q.values())==156 and all(set(x.get('byExample',{}))<=set(data(new,'VOCAB_DETAILS_BY_ID')[key[2:]]['examples'])for key,x in q.items()))
a=data(old,'VOCAB_DETAILS_BY_ID');b=data(new,'VOCAB_DETAILS_BY_ID');diff=[(key,f)for key in a for f in set(a[key])|set(b[key])if a[key].get(f)!=b[key].get(f)]
check('Only additional card field is v2210 Japanese meaning; examples/translations/usage stable',diff==[('2210','m')])
check('3914 words, 130 grammar, 160 readings, 381 reading questions retained',len(data(new,'DEFAULT_VOCAB'))==3914 and len(data(new,'GRAMMAR'))==130 and sum(map(len,data(new,'readingBank').values()))==160 and sum(len(r['questions'])for values in data(new,'readingBank').values()for r in values)==381)
# Remove only authorized data payloads and compare every remaining byte around them.
def scrub(s):
 for name in ['REVIEWED_MEANING_QUIZZES','VOCAB_DETAILS_BY_ID']:
  m=re.search(r'const '+name+r'\s*=\s*',s);_,end=json.JSONDecoder().raw_decode(s[m.end():]);s=s[:m.end()]+'DATA'+s[m.end()+end:]
 return s
a=scrub(old).replace('学習アプリ · v140','学習アプリ · v141')
a=a.replace("  const reviewed=reviewedExampleTarget(example,it.kind,it.word.w)?.quiz || entry?.byExample?.[example] || entry;", "  const cardExamples=(it.kind==='g'?GRAMMAR_DETAILS_BY_ID:VOCAB_DETAILS_BY_ID)[it.id]?.examples || [];\n  const reviewed=reviewedExampleTarget(example,it.kind,it.word.w)?.quiz || entry?.byExample?.[example] ||\n    ((!example || cardExamples.includes(example)) ? entry : null);")
check('No other HTML/JS/CSS/storage changes',a==scrub(new))
subprocess.run(['python',str(P/'review.py')],check=True,cwd=ROOT)
review=json.loads((P/'editorial-review.json').read_text());check('265 individual decisions bind both exact current examples',review['sets']==265 and review['contexts']==530 and not review['independentReview'])
report=dict(sha256=hashlib.sha256(new.encode()).hexdigest(),pass_=True,checks=checks)
(P/'invariant-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('PASS',len(checks),'invariant groups')
