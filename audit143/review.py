from pathlib import Path
import json,re,hashlib,runpy,csv
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit143';s=(ROOT/'release143/JLPT_N1_ukrainian_reading_v143.html').read_text()
def data(n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
targets=data('REVIEWED_EXAMPLE_TARGETS');g=data('GRAMMAR_DETAILS_BY_ID');q=data('REVIEWED_MEANING_QUIZZES');words={x['id']:x['w']for x in data('GRAMMAR')};a=runpy.run_path(str(P/'author.py'));decisions={int(x.split('\t')[0]):x.rstrip().split('\t')[2]for x in (ROOT/'review20261105/grammar-decisions.tsv').read_text().splitlines()}
rows=[]
for i in a['IDS']:
 key='g_'+str(i);contexts=[]
 for j,sentence in enumerate(g[str(i)]['examples']):
  exact=next((r for r in targets if r['kind']=='g'and r['id']==i and r['sentence']==sentence),None)
  payload=exact['quiz']if exact else q[key].get('byExample',{}).get(sentence,q[key]);options=[payload['correct'],*payload['wrong']];assert len(options)==len(set(options))==4
  assert all(not any(marker in x for marker in ['参照','接続','辞書形','基本形','【','〜','～'])for x in options)
  assert max(map(len,options))/min(map(len,options))<2.1
  contexts.append(dict(exampleIndex=j,sentence=sentence,source='exact_C04_retained'if exact else('default'if j==0 else'byExample'),**{k:payload[k]for k in ['correct','wrong','note']},payloadSha256=digest({k:payload[k]for k in ['correct','wrong','note']})))
 rows.append(dict(key=key,word=words[i],decision='authored_context_sets',previousFinding=decisions[i],rationale=('The second C04 context was reread and retained with its precedence, forms and quiz unchanged; first context newly authored.'if i in a['RETAINED_C04_SECOND_IDS']else'Original context interpretations; the Ukrainian note explains the contrasts with all three wrong options. No synonymous key is treated as wrong.'),contexts=contexts))
report=dict(version=143,reviewType='author_editorial_review',independentReview=False,sha256=hashlib.sha256(s.encode()).hexdigest(),sets=51,newPayloads=98,retainedExactC04Contexts=4,contexts=sum(len(r['contexts'])for r in rows),scope='All existing examples of 51 selected grammar cards; options/keys/notes with every card field unchanged. Not full-card or independent acceptance.',rows=rows,sources='audit143/sources.md')
(P/'editorial-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
# Resolve only exact diagnostic cases, not all uses of these cards.
old=json.loads((ROOT/'review20261105/grammar-findings.json').read_text());print('Author review:',report['sets'],'sets;',report['contexts'],'contexts')
