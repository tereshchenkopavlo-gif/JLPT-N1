import json,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
P=ROOT/'audit131';R=ROOT/'release131';R.mkdir(exist_ok=True)
ns={};exec((P/'author.py').read_text(),ns)
for f in sorted(P.glob('medium_*.py'))+sorted(P.glob('long_*.py'))+[P/'notes.py']:exec(f.read_text(),ns)
new=ns['new'];assert len(new)==18
basepath=ROOT/'JLPT_N1_ukrainian_reading_v130.html'
if not basepath.exists():basepath=ROOT/'release130/JLPT_N1_ukrainian_reading_v130.html'
base=basepath.read_text()
assert hashlib.sha256(base.encode()).hexdigest()=='c049da5914210f4b517732435de2bc04c477eedfdef776fb9072bd8a155f09b8'
def get(name):return json.JSONDecoder().raw_decode(base[re.search(r'const '+name+r'\s*=\s*',base).end():])[0]
v={x['id']:x for x in get('DEFAULT_VOCAB')};g={x['id']:x for x in get('GRAMMAR')}
bank=get('readingBank');coverage=[]
for n,x in enumerate(new):
    entry={k:x[k] for k in ['id','title','ja','uk']};questions=[]
    for j,q in enumerate(x['questions']):
        assert q['evidence'] in x['ja'],(x['id'],q['evidence'])
        shift=(n+j)%4;choices=q['choices'][shift:]+q['choices'][:shift]
        questions.append({**q,'choices':choices,'answer':(-shift)%4})
    entry['questions']=questions;notes=[]
    for kind,items,db in [('v',x['vocab'],v),('g',x['grammar'],g)]:
        for id,quote,meaning in items:
            assert id in db and quote in x['ja'],(x['id'],kind,id,quote)
            if kind=='v':assert db[id]['w']==quote
            notes.append(dict(kind=kind,id=str(id),label=db[id]['w'],quote=quote,meaning=meaning))
            coverage.append(dict(readingId=x['id'],level=x['level'],kind=kind,itemId=id,label=db[id]['w'],quote=quote,meaning=meaning,coverageType='reviewed_context_occurrence'))
    entry['contextNotes']=notes;entry['source']='original_v131';bank[x['level']].append(entry)
a=base.index('    const readingBank = {');b=base.index('    const makeIntegrated',a)
s=base[:a]+'    const readingBank = '+json.dumps(bank,ensure_ascii=False,separators=(',',':'))+';\n\n'+base[b:]
s=s.replace('український тренажер · v130','український тренажер · v131')
html=R/'JLPT_N1_ukrainian_reading_v131.html';html.write_text(s)
for name,obj in [('new-readings',new),('readings-after',bank),('coverage',coverage)]:
    (P/(name+'.json')).write_text(json.dumps(obj,ensure_ascii=False,indent=2))
(P/'app.js').write_text(s.split('<script>',1)[1].split('</script>',1)[0])
summary=dict(texts={k:len(v) for k,v in bank.items()},new=len(new),newQuestions=sum(len(x['questions']) for x in new),totalQuestions=sum(len(x['questions']) for arr in bank.values() for x in arr),coverageLinks=len(coverage),vocabIds=len({x['itemId'] for x in coverage if x['kind']=='v'}),grammarIds=len({x['itemId'] for x in coverage if x['kind']=='g'}),sha256=hashlib.sha256(s.encode()).hexdigest())
(P/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False))
