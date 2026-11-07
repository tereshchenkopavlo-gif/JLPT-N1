import re, json, csv, subprocess, sys
from pathlib import Path
before, after = [Path(x).read_text() for x in sys.argv[1:3]]
p=Path(__file__).resolve().parent
def section(html,name):
 start=re.search(r'const '+name+r'\s*=\s*',html).end()
 value,end=json.JSONDecoder().raw_decode(html,start)
 return value,start,end
def replace(html,name,value):
 _,start,end=section(html,name)
 return html[:start]+json.dumps(value,ensure_ascii=False,separators=(',',':'))+html[end:]
orig=section(before,'VOCAB_DETAILS_BY_ID')[0]
new=section(after,'VOCAB_DETAILS_BY_ID')[0]
q0=section(before,'REVIEWED_MEANING_QUIZZES')[0]
q1=section(after,'REVIEWED_MEANING_QUIZZES')[0]
assert len(orig)==len(new)==3914 and list(orig)==list(new)
assert len(section(after,'GRAMMAR_DETAILS_BY_ID')[0])==130
assert len(section(after,'DEFAULT_VOCAB')[0])==3914
render=[]
for row in csv.DictReader((p/'translations.tsv').open(),delimiter='\t'):
 key, index=row['id'],int(row['index'])
 assert new[key]['exampleTranslations'][index]==row['translation']
 render.append([key,index,new[key]])
 new[key]['exampleTranslations'][index]=orig[key]['exampleTranslations'][index]
for row in csv.DictReader((p/'pilot-fields.tsv').open(),delimiter='\t'):
 key,field=row['id'],row['field']
 assert new[key][field]==row['value']
 new[key][field]=orig[key][field]
assert new==orig
assert q1['v_293']['correct']==section(after,'VOCAB_DETAILS_BY_ID')[0]['293']['m']
q1['v_293']['correct']=q0['v_293']['correct']
assert q1==q0
assert set(q1['v_293']['byExample'])==set(orig['293']['examples'])
assert all(len(set([x['correct'],*x['wrong']]))==4 for x in q1['v_293']['byExample'].values())
assert replace(replace(after,'VOCAB_DETAILS_BY_ID',orig),'REVIEWED_MEANING_QUIZZES',q0).replace('· v154</title>','· v153</title>',1)==before
scripts=re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',after,re.S)
assert scripts
for script in scripts:
 subprocess.run(['node','--check','-'],input=script,text=True,check=True)
functions=re.search(r'function escapeLex\(.*?(?=const STUDY_SECTION_LABELS)',after,re.S)[0]
probe='''const assert=require('node:assert/strict');
const VOCAB_DETAILS_BY_ID={};
'''+functions+'''
for(const [id,index,card] of '''+json.dumps(render,ensure_ascii=False)+'''){
 VOCAB_DETAILS_BY_ID[id]=card;
 const html=vocabExamplesHtml(id,card.examples);
 assert(html.includes(escapeLex(card.examples[index])));
 assert(html.includes(escapeLex(card.exampleTranslations[index])));
}
'''
subprocess.run(['node','-'],input=probe,text=True,check=True)
print(f'{len(render)} example renders, 8 reviewed fields, 2 exact contexts, {len(scripts)} scripts, byte-identical rollback')
