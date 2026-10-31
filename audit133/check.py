import json,re,hashlib
from pathlib import Path
root=Path(__file__).resolve().parent.parent;p=root/'audit133'
base=(root/'JLPT_N1_ukrainian_reading_v132.html').read_text()
new=(root/'release133/JLPT_N1_ukrainian_reading_v133.html').read_text()
def get(s,name):return json.JSONDecoder().raw_decode(s[re.search(r'const '+name+r'\s*=\s*',s).end():])[0]
results=[]
for name in ['DEFAULT_VOCAB','GRAMMAR','VOCAB_DETAILS_BY_ID','GRAMMAR_DETAILS_BY_ID','VOCAB_AUDITED_PAIRS','REVIEWED_MEANING_QUIZZES','VOCAB_KANA_EXAMPLE_TARGETS','AUTO_ANTONYM_PAIRS','READING_CONTEXT_NOTES','readingBank','GRAMMAR_AUDITED_PAIRS']:
 assert get(base,name)==get(new,name),name
 results.append({'name':name+' unchanged','pass':True})
assert len(get(new,'DEFAULT_VOCAB'))==3914 and len(get(new,'GRAMMAR'))==130
bank=get(new,'readingBank');assert (len(bank['medium']),len(bank['long']),sum(len(x['questions']) for a in bank.values() for x in a))==(87,55,339)
for key in ['choba_n1uk_storage_v1','jlptN1CompareListUA_v1']:
 assert base.count(key)==new.count(key)>0
assert '格調高い例文' not in new
assert new.count('data-card-step="-1"')==new.count('data-card-step="1"')==2
assert 'cardDetailRequest' in new and 'touchcancel' in new
results.extend([{'name':'Counts, storage keys, example title, navigation controls and race guard','pass':True}])
out={'sha256':hashlib.sha256(new.encode()).hexdigest(),'checks':results}
(p/'invariant-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(out,ensure_ascii=False))
