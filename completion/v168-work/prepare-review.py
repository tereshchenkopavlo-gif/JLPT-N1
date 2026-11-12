import hashlib,json,re
from pathlib import Path
p=Path(__file__).resolve().parent
raw=Path('JLPT_N1_v168_working.html').read_bytes()
html=raw.decode()
def data(name):
 start=re.search(r'const '+name+r'\s*=\s*',html).end()
 return json.JSONDecoder().raw_decode(html,start)[0]
cards=data('VOCAB_DETAILS_BY_ID')
vocab=data('DEFAULT_VOCAB')
pos=data('VOCAB_POS_BY_ID')
edits=json.loads((p/'updates.json').read_text())
ids={e['path'][0] for e in edits if e['block'] in {'VOCAB_DETAILS_BY_ID','VOCAB_POS_BY_ID'}}
labels={e['path'][0] for e in edits if e['block']=='AUTO_VOCAB_COMPARISONS'}
ids.update(str(v['id']) for v in vocab if v['w'] in labels)
assert len(ids)==10
by_id={str(v['id']):v for v in vocab}
rows=[dict(key=key,word=cards[key]['w'],reading=by_id[key]['r'],partsOfSpeech=pos[key]) for key in sorted(ids,key=int)]
(p/'editorial-review.json').write_text(json.dumps(dict(sha256=hashlib.sha256(raw).hexdigest(),rows=rows),ensure_ascii=False,indent=2)+'\n')
