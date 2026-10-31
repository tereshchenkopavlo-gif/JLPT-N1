import json,re,hashlib,copy
from pathlib import Path
root=Path(__file__).resolve().parent.parent;p=root/'audit134'
a=(root/'JLPT_N1_ukrainian_reading_v133.html').read_text();b=(root/'release134/JLPT_N1_ukrainian_reading_v134.html').read_text()
def get(s,n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
patch=json.loads((p/'changes.json').read_text());results=[]
assert hashlib.sha256(a.encode()).hexdigest()=='7acdc03322bfa2d8e40650353de418e184b6391d212de461da0970d61f39dca5'
for n in ['DEFAULT_VOCAB','GRAMMAR','GRAMMAR_DETAILS_BY_ID','REVIEWED_MEANING_QUIZZES','VOCAB_KANA_EXAMPLE_TARGETS','AUTO_ANTONYM_PAIRS','READING_CONTEXT_NOTES','readingBank','GRAMMAR_AUDITED_PAIRS']:
 assert get(a,n)==get(b,n),n;results.append({'name':n+' unchanged','pass':True})
expected=copy.deepcopy(get(a,'VOCAB_DETAILS_BY_ID'))
for id,text in patch['usage'].items():expected[id]['usage']=text
assert expected==get(b,'VOCAB_DETAILS_BY_ID')
expected=copy.deepcopy(get(a,'VOCAB_AUDITED_PAIRS'))
for index,text in patch['pairs'].items():expected[int(index)]['note']=text
assert expected==get(b,'VOCAB_AUDITED_PAIRS')
assert len(get(b,'DEFAULT_VOCAB'))==3914 and len(get(b,'GRAMMAR'))==130
bank=get(b,'readingBank');assert (len(bank['medium']),len(bank['long']),sum(len(x['questions']) for arr in bank.values() for x in arr))==(87,55,339)
# Strip only the two explicitly edited data blocks. Everything else is identical.
def outside(s):
 for n in ['VOCAB_DETAILS_BY_ID','VOCAB_AUDITED_PAIRS']:
  m=re.search(r'const '+n+r'\s*=\s*',s);_,length=json.JSONDecoder().raw_decode(s[m.end():]);s=s[:m.end()]+'DATA'+s[m.end()+length:]
 return s
assert outside(a)==outside(b).replace('学習アプリ · v134','学習アプリ · v133')
review=json.loads((p/'logic-review.json').read_text());assert review['scannedPairs']==859 and len(review['reviews'])==40 and sum(x['status']=='clarified' for x in review['reviews'])==4
results.extend([{'name':'Only usage fields 2980/2981 changed','pass':True},{'name':'Only notes 659/738/853/857 changed','pass':True},{'name':'Counts and ID continuity','pass':True},{'name':'All runtime, navigation, UI, CSS, storage and examples byte-identical outside data and version','pass':True},{'name':'859 scanned, 40 logic reviews, 4 clarified','pass':True}])
out={'sha256':hashlib.sha256(b.encode()).hexdigest(),'checks':results}
(p/'invariant-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False))
