"""Bind this turn's individually recorded author decisions to current, exact contexts."""
from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit141'
old=(ROOT/'JLPT_N1_ukrainian_reading_v140.html').read_text();s=(ROOT/'release141/JLPT_N1_ukrainian_reading_v141.html').read_text()
def data(s,n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
decisions=dict(x.split('\t',1)for x in (P/'decisions.tsv').read_text().splitlines());q=data(s,'REVIEWED_MEANING_QUIZZES');before=data(old,'REVIEWED_MEANING_QUIZZES');details=data(s,'VOCAB_DETAILS_BY_ID');words={str(x['id']):x for x in data(s,'DEFAULT_VOCAB')}
assert len(decisions)==len(q)==265 and decisions.keys()==q.keys()
rows=[]
for key,quiz in q.items():
 id=key[2:];d=details[id];assert len(d['examples'])==2
 assert set(quiz.get('byExample',{}))<=set(d['examples'])
 contexts=[]
 for i,ex in enumerate(d['examples']):
  z=quiz.get('byExample',{}).get(ex,quiz)
  assert len(z['wrong'])==3 and len(set([z['correct'],*z['wrong']]))==4
  contexts.append(dict(exampleIndex=i,sentence=ex,source='byExample'if ex in quiz.get('byExample',{})else'default',correct=z['correct'],wrong=z['wrong'],note=z.get('note','')))
 rows.append(dict(key=key,word=words[id]['w'],decision='revised'if quiz!=before[key]else'retained',rationale=decisions[key],beforePayloadSha256=digest(before[key]),afterPayloadSha256=digest(quiz),contexts=contexts))
report=dict(version=141,reviewType='author_editorial_review',independentReview=False,baseSha256=hashlib.sha256(old.encode()).hexdigest(),sha256=hashlib.sha256(s.encode()).hexdigest(),scope='265 saved vocabulary meaning sets, both existing examples, all alternatives/keys/notes. Not full cards, all grammar, or all random generators.',sets=len(rows),contexts=sum(len(x['contexts'])for x in rows),revised=[x['key']for x in rows if x['decision']=='revised'],sources='audit141/sources.md',rows=rows,additionalGrammar=dict(key='g_95',examples=data(s,'GRAMMAR_DETAILS_BY_ID')['95']['examples'],decision='retained',rationale='状況を背景に行為や状態を述べる。状況終了後・条件限定・行為不能を意味しない。',creditedAsFullGrammarCard=False))
(P/'editorial-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(sets=report['sets'],contexts=report['contexts'],revised=len(report['revised']),additionalGrammarContexts=2)))
