from pathlib import Path
import json,re,hashlib,runpy
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit151';R=ROOT/'release151';R.mkdir(exist_ok=True)
base=(ROOT/'JLPT_N1_ukrainian_reading_v150.html').read_text()
assert hashlib.sha256(base.encode()).hexdigest()=='02fa1c3e6bdcf44b8bf3a50afd39b55287567b8ed63da9da55a6b4d29de85c84'
def data(s,n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
def replace(s,n,d):
 m=re.search(r'const '+n+r'\s*=\s*',s);_,end=json.JSONDecoder().raw_decode(s[m.end():]);return s[:m.end()]+json.dumps(d,ensure_ascii=False,separators=(',',':'))+s[m.end()+end:]
vocabulary=data(base,'VOCAB_DETAILS_BY_ID')
author=runpy.run_path(str(P/'author.py'))
author['revise'](vocabulary)
s=replace(base,'VOCAB_DETAILS_BY_ID',vocabulary).replace('学習アプリ · v150','学習アプリ · v151')
(R/'JLPT_N1_ukrainian_reading_v151.html').write_text(s);(P/'app.js').write_text(s.split('<script>',1)[1].split('</script>',1)[0])
summary=dict(version=151,baseSha256=hashlib.sha256(base.encode()).hexdigest(),sha256=hashlib.sha256(s.encode()).hexdigest(),bytes=len(s.encode()),vocabIds=author['CARD_IDS'],changedJapaneseExampleSentences=0,changedUkrainianExampleTranslations=len(author["TRANSLATIONS"]),newQuizPayloads=0,newDatabaseEntries=0)
(P/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary))
