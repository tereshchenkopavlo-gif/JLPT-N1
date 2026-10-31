import json,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit137';R=ROOT/'release137';R.mkdir(exist_ok=True)
base=(ROOT/'JLPT_N1_ukrainian_reading_v136.html').read_text();assert hashlib.sha256(base.encode()).hexdigest()=='b2632788ee7f50d6c8872f05c86e006379159afcdad3ced6678c98fca7a6cd2a'
get=lambda n:json.JSONDecoder().raw_decode(base[re.search(r'const '+n+r'\s*=\s*',base).end():])[0]
v,g,vd,gd=[get(n) for n in ['DEFAULT_VOCAB','GRAMMAR','VOCAB_DETAILS_BY_ID','GRAMMAR_DETAILS_BY_ID']]
ns=dict(v=v,g=g,vd=vd,gd=gd);exec((P/'author.py').read_text(),ns);records=ns['records'];assert len(records)==30
oldrows=json.loads((ROOT/'completion/target-diagnostics.json').read_text())['unmarked'];assert {(x['kind'],x['id'],x['exampleIndex']) for x in records}=={(x['kind'],x['id'],x['exampleIndex']) for x in oldrows}
# Exactly one example and its translation change. Its previous text illustrates a different expression.
vd['210']['examples'][1]=ns['new_example'];vd['210']['exampleTranslations'][1]=ns['new_translation']
def replace_data(s,name,value):
 m=re.search(r'const '+name+r'\s*=\s*',s);_,end=json.JSONDecoder().raw_decode(s[m.end():]);return s[:m.end()]+json.dumps(value,ensure_ascii=False,separators=(',',':'))+s[m.end()+end:]
s=replace_data(base,'VOCAB_DETAILS_BY_ID',vd)
helper='''const REVIEWED_EXAMPLE_TARGETS = '''+json.dumps(records,ensure_ascii=False,separators=(',',':'))+''';
function reviewedExampleTarget(sentence, kind, word) {
  return REVIEWED_EXAMPLE_TARGETS.find(row => row.kind === kind && row.word === word && row.sentence === sentence) || null;
}
'''
s=s.replace('function quizMeaningOptions(it,def,example=\'\') {',helper+"function quizMeaningOptions(it,def,example='') {")
s=s.replace('  const reviewed=entry?.byExample?.[example] || entry;',"  const reviewed=reviewedExampleTarget(example,it.kind,it.word.w)?.quiz || entry?.byExample?.[example] || entry;")
needle='  markTarget(sentence, kind, word) {'
s=s.replace(needle,needle+'''
    const exact = reviewedExampleTarget(sentence, kind, word);
    if (exact) {
      let result='', cursor=0;
      for (const form of exact.forms) {
        const idx=sentence.indexOf(form,cursor);
        if (idx < 0) return {s:sentence,found:false};
        result+=sentence.slice(cursor,idx)+'\\u0001'+form+'\\u0002';
        cursor=idx+form.length;
      }
      return {s:result+sentence.slice(cursor),found:true};
    }
''')
s=s.replace("if (real && found && !REVIEWED_MEANING_QUIZZES[it.kind+'_'+it.id]) types.push('cloze');","if (real && found && !reviewedExampleTarget(ex,it.kind,label) && !REVIEWED_MEANING_QUIZZES[it.kind+'_'+it.id]) types.push('cloze');")
s=s.replace("if (readingCandidates.length >= 3) types.push('reading');","if (readingCandidates.length >= 3 && (!reviewedExampleTarget(ex,it.kind,label) || reviewedExampleTarget(ex,it.kind,label).forms.some(hasKanji))) types.push('reading');")
s=s.replace('学習アプリ · v136','学習アプリ · v137')
(R/'JLPT_N1_ukrainian_reading_v137.html').write_text(s);(P/'app.js').write_text(s.split('<script>',1)[1].split('</script>',1)[0]);(P/'targets.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
summary=dict(sha256=hashlib.sha256(s.encode()).hexdigest(),bytes=len(s.encode()),targets=len(records),affectedCards=len({(x['kind'],x['id']) for x in records}),vocabExamples=3,grammarExamples=27,changedExampleIds=['v_210:1'],texts=160,questions=381)
(P/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False))
