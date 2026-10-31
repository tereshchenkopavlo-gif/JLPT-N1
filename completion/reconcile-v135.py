"""Credit existing, hash-bound author reviews; never call them independent expert review."""
import csv,json,hashlib,re
from pathlib import Path
P=Path(__file__).resolve().parent;root=P.parent
baseline=json.loads((P/'baseline.json').read_text());html=(root/baseline['baseline']).read_text()
assert hashlib.sha256(html.encode()).hexdigest()==baseline['htmlSha256']
report=json.loads((root/'audit135/editorial-review.json').read_text())
assert report['htmlSha256']==baseline['htmlSha256'] and report['reviewType']=='author_editorial_review'
assert not report['independentReview'] and len(report['passages'])==18 and len(report['questions'])==42
bank=json.JSONDecoder().raw_decode(html[re.search(r'const readingBank\s*=\s*',html).end():])[0]
current={x['id']:x for a in bank.values() for x in a if x.get('source')=='original_v135'}
evidence={}
for r in report['passages']:
 x=current[r['id']];assert r['title']==x['title'] and r['jaCharacters']==len(x['ja'])
 evidence[('reading',r['id'])]=f"audit135/editorial-review.json:passage={r['id']}; author review; v135 SHA-256={baseline['htmlSha256']}"
for r in report['questions']:
 q=current[r['readingId']]['questions'][r['questionIndex']]
 assert r['prompt']==q['prompt'] and r['correctAnswer']==q['choices'][q['answer']] and r['evidence']==q['evidence']
 assert len(r['rejectedOptions'])==3 and {x['text'] for x in r['rejectedOptions']}==set(q['choices'])-{q['choices'][q['answer']]}
 evidence[('reading_question',r['readingId']+f":q{r['questionIndex']+1}")]=f"audit135/editorial-review.json:question={r['readingId']}/{r['questionIndex']}; author review; v135 SHA-256={baseline['htmlSha256']}"
with (P/'review-register.csv').open(newline='') as f:reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
credited=[]
for row in rows:
 key=(row['kind'],row['key'])
 if key in evidence:
  assert row['finalReview'] in {'pending','reviewed'},'Do not overwrite a later decision'
  row['finalReview']='reviewed';row['evidence']=evidence[key];credited.append(dict(kind=key[0],key=key[1]))
assert len(credited)==60
with (P/'review-register.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rows)
(P/'reconciled-v135.json').write_text(json.dumps(dict(baselineSha256=baseline['htmlSha256'],scope='Existing v135 author reviews of 18 readings and 42 questions credited after matching current content and keys; no independent review claimed',credited=credited),ensure_ascii=False,indent=2))
print('Credited existing evidence for 18 readings +42 questions; no new semantic review claimed')
