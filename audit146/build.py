from pathlib import Path
import json,re,hashlib,runpy
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit146';R=ROOT/'release146';R.mkdir(exist_ok=True)
base=(ROOT/'JLPT_N1_ukrainian_reading_v145.html').read_text()
assert hashlib.sha256(base.encode()).hexdigest()=='80cc4a3d35ad2257b1b38afc1ad566066db0797409892b10697a84e35cf21d47'
def data(s,n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
def replace(s,n,d):
 m=re.search(r'const '+n+r'\s*=\s*',s);_,end=json.JSONDecoder().raw_decode(s[m.end():]);return s[:m.end()]+json.dumps(d,ensure_ascii=False,separators=(',',':'))+s[m.end()+end:]
g=data(base,'GRAMMAR_DETAILS_BY_ID');pairs=data(base,'GRAMMAR_AUDITED_PAIRS');a=runpy.run_path(str(P/'author.py'));a['revise'](g,pairs)
s=replace(replace(base,'GRAMMAR_DETAILS_BY_ID',g),'GRAMMAR_AUDITED_PAIRS',pairs).replace('学習アプリ · v145','学習アプリ · v146')
(R/'JLPT_N1_ukrainian_reading_v146.html').write_text(s);(P/'app.js').write_text(s.split('<script>',1)[1].split('</script>',1)[0])
summary=dict(version=146,baseSha256=hashlib.sha256(base.encode()).hexdigest(),sha256=hashlib.sha256(s.encode()).hexdigest(),bytes=len(s.encode()),grammarIds=a['CARD_IDS'],pairIndices=a['PAIR_IDS'],changedJapaneseExampleSentences=0,changedUkrainianExampleTranslations=len(a["TRANSLATIONS"]),newQuizPayloads=0,newDatabaseEntries=0)
(P/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary))
