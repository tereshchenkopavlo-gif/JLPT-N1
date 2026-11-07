"""Build the browser target list from the two reviewed change ledgers."""
import csv
import hashlib
import json
from pathlib import Path
import re
p=Path(__file__).resolve().parent
html=Path('JLPT_N1_v154_working.html').read_text()
def data(name):
 start=re.search(r'const '+name+r'\s*=\s*',html).end()
 return json.JSONDecoder().raw_decode(html,start)[0]
cards=data('VOCAB_DETAILS_BY_ID')
vocab={str(x['id']):x for x in data('DEFAULT_VOCAB')}
pos=data('VOCAB_POS_BY_ID')
ids=set()
for name in ['translations.tsv','pilot-fields.tsv']:
 with (p/name).open() as f:
  ids.update(row['id'] for row in csv.DictReader(f,delimiter='\t'))
rows=[dict(key=key,word=cards[key]['w'],reading=vocab[key]['r'],partsOfSpeech=pos[key]) for key in sorted(ids,key=int)]
result=dict(sha256=hashlib.sha256(Path('JLPT_N1_v154_working.html').read_bytes()).hexdigest(),rows=rows)
assert len(rows)==60
(p/'editorial-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
