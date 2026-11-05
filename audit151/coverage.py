"""Consolidate author evidence for exactly the current 261 grammar examples.
Hash agreement preserves old acceptance; it is not an independent language review.
"""
from pathlib import Path
import json,re,hashlib,collections
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit151';s=(ROOT/'release151/JLPT_N1_ukrainian_reading_v151.html').read_text()
def data(n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
q=data('REVIEWED_MEANING_QUIZZES');g=data('GRAMMAR_DETAILS_BY_ID');targets=data('REVIEWED_EXAMPLE_TARGETS');evidence={}
for v in [142,143,144]:
 r=json.loads((ROOT/f'audit{v}/editorial-review.json').read_text())
 for row in r['rows']:
  for c in row['contexts']:
   k=(row['key'],c['sentence']);assert k not in evidence
   evidence[k]=dict(version=v,index=c['exampleIndex'],payload={n:c[n]for n in ['correct','wrong','note']},evidence=f'audit{v}/editorial-review.json:{row["key"]}:e{c["exampleIndex"]}')
# Re-read both unchanged runtime-g95 contexts: circumstances of a leader's action
# and circumstances of profit; not an exclusive condition, later time or inability.
g95=dict(correct='特定の状況や立場を背景として、そこでの行動や状態を述べる。',wrong=['ある状況が終わった後に、初めて行動や変化が起こることを述べる。','ある条件が実現した場合に限って、行動や状態が成り立つことを述べる。','ある事情を理由として、その後の行動ができないことを述べる。'],note='〜にあって підкреслює обставини, за яких відбувається дія. Сам зворот не означає «лише після», «тільки за умови» або неможливість дії.')
rows=[]
for word in data('GRAMMAR'):
 id=word['id'];key='g_'+str(id)
 for i,sentence in enumerate(g[str(id)]['examples']):
  exact=next((t for t in targets if t['kind']=='g'and t['id']==id and t['sentence']==sentence),None)
  if id==95:
   payload=g95;proof='audit144/coverage.py:g95_reread; previous audit141 g95 evidence retained';v=144
  else:
   payload=exact['quiz']if exact else q[key].get('byExample',{}).get(sentence,q[key]);payload={n:payload[n]for n in ['correct','wrong','note']}
   e=evidence[(key,sentence)];assert e['index']==i and e['payload']==payload
   proof=e['evidence'];v=e['version']
  rows.append(dict(kind='g',id=id,word=word['w'],exampleIndex=i,sentenceSha256=hashlib.sha256(sentence.encode()).hexdigest(),route='exact_reviewed'if exact else'saved_set',exactOrigin=('C05'if id in {120,123,124,125,127}else'C04')if exact else None,payloadSha256=digest(payload),authorEvidence=proof,evidenceVersion=v,fullCardCredit=False))
assert len(rows)==261 and len({(x['id'],x['exampleIndex'])for x in rows})==261 and len({x['id']for x in rows})==130
counts=dict(collections.Counter(x['route']for x in rows));assert counts=={'saved_set':224,'exact_reviewed':37},counts
report=dict(version=151,sha256=hashlib.sha256(s.encode()).hexdigest(),scope='All current grammar card example meaning questions only',reviewType='author_editorial_review',independentReview=False,cards=130,contexts=261,routeCounts=counts,priorEvidencePreserved=True,g95Reread=dict(contexts=2,decision='retained',rationale='В обох прикладах названо особливі обставини дії/стану: кризу для рішень керівника й економічне тло прибутку. Варіанти про лише після, виключну умову або неможливість не є цим значенням.'),exactOrigins={'C04':27,'C05':10},fullCardCredits=0,rows=rows)
(P/'grammar-coverage.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Author evidence consolidated: 130 grammar /261 examples; 224 saved /37 exact (27 C04 /10 C05); not full cards')
