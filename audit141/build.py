from pathlib import Path
import json,re,hashlib,runpy
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit141';R=ROOT/'release141';R.mkdir(exist_ok=True)
base=(ROOT/'JLPT_N1_ukrainian_reading_v140.html').read_text()
assert hashlib.sha256(base.encode()).hexdigest()=='810af1aecf5a71b2fbd39b687e3ec310763317cb3f04821107cdeb983c31f537'
def data(s,n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
def replace(s,n,d):
 m=re.search(r'const '+n+r'\s*=\s*',s);_,end=json.JSONDecoder().raw_decode(s[m.end():])
 return s[:m.end()]+json.dumps(d,ensure_ascii=False,separators=(',',':'))+s[m.end()+end:]
q=data(base,'REVIEWED_MEANING_QUIZZES');d=data(base,'VOCAB_DETAILS_BY_ID')
runpy.run_path(str(P/'author.py'))['revise'](q,d)
s=replace(replace(base,'REVIEWED_MEANING_QUIZZES',q),'VOCAB_DETAILS_BY_ID',d)
# Never reuse a sentence-specific default for an unknown/custom example.
old="  const reviewed=reviewedExampleTarget(example,it.kind,it.word.w)?.quiz || entry?.byExample?.[example] || entry;"
new="""  const cardExamples=(it.kind==='g'?GRAMMAR_DETAILS_BY_ID:VOCAB_DETAILS_BY_ID)[it.id]?.examples || [];
  const reviewed=reviewedExampleTarget(example,it.kind,it.word.w)?.quiz || entry?.byExample?.[example] ||
    ((!example || cardExamples.includes(example)) ? entry : null);"""
assert s.count(old)==1;s=s.replace(old,new).replace('学習アプリ · v140','学習アプリ · v141')
path=R/'JLPT_N1_ukrainian_reading_v141.html';path.write_text(s)
(P/'app.js').write_text(s.split('<script>',1)[1].split('</script>',1)[0])
summary=dict(version=141,baseSha256=hashlib.sha256(base.encode()).hexdigest(),sha256=hashlib.sha256(s.encode()).hexdigest(),bytes=len(s.encode()),savedVocabularySets=len(q),changedQuizKeys=[k for k in q if q[k]!=data(base,'REVIEWED_MEANING_QUIZZES')[k]],changedCardFields={'2210':['m']},exampleOverrides=sum(len(x.get('byExample',{}))for x in q.values()))
(P/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary))
