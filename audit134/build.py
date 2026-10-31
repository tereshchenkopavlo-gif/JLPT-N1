import hashlib,json,re
from pathlib import Path
root=Path(__file__).resolve().parent.parent;p=root/'audit134';r=root/'release134';r.mkdir(exist_ok=True)
s=(root/'JLPT_N1_ukrainian_reading_v133.html').read_text()
assert hashlib.sha256(s.encode()).hexdigest()=='7acdc03322bfa2d8e40650353de418e184b6391d212de461da0970d61f39dca5'
patch=json.loads((p/'changes.json').read_text())
def edit(name,fn):
 global s
 a=re.search(r'const '+name+r'\s*=\s*',s).end();value,n=json.JSONDecoder().raw_decode(s[a:]);fn(value)
 s=s[:a]+json.dumps(value,ensure_ascii=False,separators=(',',':'))+s[a+n:]
def cards(db):
 for id,text in patch['usage'].items():assert db[id]['w'] in ['情けない','情け深い'];db[id]['usage']=text
def pairs(db):
 for index,text in patch['pairs'].items():db[int(index)]['note']=text
edit('VOCAB_DETAILS_BY_ID',cards);edit('VOCAB_AUDITED_PAIRS',pairs)
s=s.replace('学習アプリ · v133','学習アプリ · v134')
out=r/'JLPT_N1_ukrainian_reading_v134.html';out.write_text(s)
(p/'app.js').write_text(s.split('<script>',1)[1].split('</script>',1)[0])
summary={'sha256':hashlib.sha256(s.encode()).hexdigest(),'bytes':len(s.encode()),'changedUsageIds':list(patch['usage']),'changedPairIndexes':[int(x) for x in patch['pairs']]}
(p/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps(summary))
