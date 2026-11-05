from pathlib import Path
import json,re,hashlib,runpy
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit143';R=ROOT/'release143';R.mkdir(exist_ok=True)
base=(ROOT/'JLPT_N1_ukrainian_reading_v142.html').read_text()
assert hashlib.sha256(base.encode()).hexdigest()=='b2064d5a6201bfea593b9a131e56b38ed44347bf74ba820b769120bfc04e57be'
def data(s,n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
def replace(s,n,d):
 m=re.search(r'const '+n+r'\s*=\s*',s);_,end=json.JSONDecoder().raw_decode(s[m.end():])
 return s[:m.end()]+json.dumps(d,ensure_ascii=False,separators=(',',':'))+s[m.end()+end:]
q=data(base,'REVIEWED_MEANING_QUIZZES');g=data(base,'GRAMMAR_DETAILS_BY_ID');author=runpy.run_path(str(P/'author.py'));author['revise'](q,g)
s=replace(base,'REVIEWED_MEANING_QUIZZES',q).replace('学習アプリ · v142','学習アプリ · v143')
(R/'JLPT_N1_ukrainian_reading_v143.html').write_text(s);(P/'app.js').write_text(s.split('<script>',1)[1].split('</script>',1)[0])
summary=dict(version=143,baseSha256=hashlib.sha256(base.encode()).hexdigest(),sha256=hashlib.sha256(s.encode()).hexdigest(),bytes=len(s.encode()),newGrammarKeys=['g_'+str(i)for i in author['IDS']],grammarContexts=sum(len(g[str(i)]['examples'])for i in author['IDS']),changedCardFields={str(i):list(x)for i,x in author['CARD_CHANGES'].items()},newExampleOverrides=sum(len(q['g_'+str(i)]['byExample'])for i in author['IDS']))
(P/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary))
