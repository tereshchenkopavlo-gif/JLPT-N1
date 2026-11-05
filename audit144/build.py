from pathlib import Path
import json,re,hashlib,runpy
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit144';R=ROOT/'release144';R.mkdir(exist_ok=True)
base=(ROOT/'JLPT_N1_ukrainian_reading_v143.html').read_text()
assert hashlib.sha256(base.encode()).hexdigest()=='028c8ffc1f03bef57c9a833a86553eaee977678bb596526bfaab04cfa6a867f4'
def data(s,n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
def replace(s,n,d):
 m=re.search(r'const '+n+r'\s*=\s*',s);_,end=json.JSONDecoder().raw_decode(s[m.end():])
 return s[:m.end()]+json.dumps(d,ensure_ascii=False,separators=(',',':'))+s[m.end()+end:]
q=data(base,'REVIEWED_MEANING_QUIZZES');g=data(base,'GRAMMAR_DETAILS_BY_ID');author=runpy.run_path(str(P/'author.py'));author['revise'](q,g)
s=replace(base,'REVIEWED_MEANING_QUIZZES',q).replace('学習アプリ · v143','学習アプリ · v144')
(R/'JLPT_N1_ukrainian_reading_v144.html').write_text(s);(P/'app.js').write_text(s.split('<script>',1)[1].split('</script>',1)[0])
summary=dict(version=144,baseSha256=hashlib.sha256(base.encode()).hexdigest(),sha256=hashlib.sha256(s.encode()).hexdigest(),bytes=len(s.encode()),newGrammarKeys=['g_'+str(i)for i in author['IDS']],grammarContexts=sum(len(g[str(i)]['examples'])for i in author['REVIEW_IDS']),newSetCardContexts=sum(len(g[str(i)]['examples'])for i in author['IDS']),newPayloadContexts=91,retainedExactContexts=33,retainedC04Contexts=23,retainedC05Contexts=10,changedCardFields={str(i):list(x)for i,x in author['CARD_CHANGES'].items()},newExampleOverrides=sum(len(q['g_'+str(i)]['byExample'])for i in author['IDS']))
(P/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary))
