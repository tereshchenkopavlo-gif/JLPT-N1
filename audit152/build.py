from pathlib import Path
import json,re,hashlib,runpy
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit152';R=ROOT/'release152';R.mkdir(exist_ok=True)
base=(ROOT/'JLPT_N1_ukrainian_reading_v151.html').read_text()
assert hashlib.sha256(base.encode()).hexdigest()=='8344b61d1e84b6d9251218bc2334c9336bb2409cdd9a36f8307a349d6d4e57b7'
def data(s,n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
def replace(s,n,d):
 m=re.search(r'const '+n+r'\s*=\s*',s);_,end=json.JSONDecoder().raw_decode(s[m.end():]);return s[:m.end()]+json.dumps(d,ensure_ascii=False,separators=(',',':'))+s[m.end()+end:]
vocabulary=data(base,'VOCAB_DETAILS_BY_ID')
author=runpy.run_path(str(P/'author.py'))
author['revise'](vocabulary)
s=replace(base,'VOCAB_DETAILS_BY_ID',vocabulary).replace('学習アプリ · v151','学習アプリ · v152')
(R/'JLPT_N1_ukrainian_reading_v152.html').write_text(s);(P/'app.js').write_text(s.split('<script>',1)[1].split('</script>',1)[0])
summary=dict(version=152,baseSha256=hashlib.sha256(base.encode()).hexdigest(),sha256=hashlib.sha256(s.encode()).hexdigest(),bytes=len(s.encode()),vocabIds=author['CARD_IDS'],changedJapaneseExampleSentences=0,changedUkrainianExampleTranslations=len(author["TRANSLATIONS"]),newQuizPayloads=0,newDatabaseEntries=0)
(P/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary))
