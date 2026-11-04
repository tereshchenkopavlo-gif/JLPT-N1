"""Credit only reviewed saved quizzes; keep all card/pair/reading decisions intact."""
from pathlib import Path
import json,re,hashlib,csv,collections
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit141'
s=(ROOT/'release141/JLPT_N1_ukrainian_reading_v141.html').read_text();sha=hashlib.sha256(s.encode()).hexdigest();review=json.loads((P/'editorial-review.json').read_text())
q=json.JSONDecoder().raw_decode(s[re.search(r'const REVIEWED_MEANING_QUIZZES\s*=\s*',s).end():])[0]
assert review['sha256']==sha and review['sets']==265 and review['contexts']==530 and not review['independentReview']
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
decisions={r['key']:r for r in review['rows']};assert decisions.keys()==q.keys()
for key,r in decisions.items():assert r['afterPayloadSha256']==digest(q[key]) and r['rationale'] and len(r['contexts'])==2
file=ROOT/'completion/review-register.csv'
with file.open(newline='')as f:reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
assert len(rows)==5842
credited=[]
for row in rows:
 if row['kind']=='reviewed_meaning_quiz':
  assert row['key']in decisions and row['finalReview']in {'pending','reviewed'}
  if row['finalReview']=='reviewed':assert row['evidence'].startswith('audit141/editorial-review.json:'),'Do not replace another review'
  row['finalReview']='reviewed';row['evidence']=f"audit141/editorial-review.json:{row['key']}; both examples, alternatives, key, note; author review, not independent; v141 SHA-256={sha}";credited.append(row['key'])
assert len(credited)==265
with file.open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
counts=dict(collections.Counter(r['finalReview']for r in rows));assert counts=={'pending':5517,'reviewed':325}
report=dict(version=141,sha256=sha,reviewType='author_editorial_review',independentReview=False,creditedKind='reviewed_meaning_quiz',credited=credited,registerPositions=len(rows),statusCounts=counts,fullCardCredits=0,additionalGrammarQuiz='g95 checked separately, not a full-card credit',scope='265 existing saved quiz rows only; prior 60 reviews preserved. No language/rights clearance for all other fields.')
(ROOT/'completion/reconciled-v141.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(counts))
