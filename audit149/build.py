from pathlib import Path
import json,re,hashlib,runpy
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit149';R=ROOT/'release149';R.mkdir(exist_ok=True)
base=(ROOT/'JLPT_N1_ukrainian_reading_v148.html').read_text()
assert hashlib.sha256(base.encode()).hexdigest()=='eedf3b91ec0fe31ec6a51414b36b4fbbab229b9feb6065402088fc6ccd6af60e'
def data(s,n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
def replace(s,n,d):
 m=re.search(r'const '+n+r'\s*=\s*',s);_,end=json.JSONDecoder().raw_decode(s[m.end():]);return s[:m.end()]+json.dumps(d,ensure_ascii=False,separators=(',',':'))+s[m.end()+end:]
g=data(base,'GRAMMAR_DETAILS_BY_ID');pairs=data(base,'GRAMMAR_AUDITED_PAIRS');a=runpy.run_path(str(P/'author.py'));a['revise'](g,pairs)
s=replace(replace(base,'GRAMMAR_DETAILS_BY_ID',g),'GRAMMAR_AUDITED_PAIRS',pairs).replace('学習アプリ · v148','学習アプリ · v149')
(R/'JLPT_N1_ukrainian_reading_v149.html').write_text(s);(P/'app.js').write_text(s.split('<script>',1)[1].split('</script>',1)[0])
summary=dict(version=149,baseSha256=hashlib.sha256(base.encode()).hexdigest(),sha256=hashlib.sha256(s.encode()).hexdigest(),bytes=len(s.encode()),grammarIds=a['CARD_IDS'],pairIndices=a['PAIR_IDS'],changedJapaneseExampleSentences=0,changedUkrainianExampleTranslations=len(a["TRANSLATIONS"]),newQuizPayloads=0,newDatabaseEntries=0)
(P/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary))
