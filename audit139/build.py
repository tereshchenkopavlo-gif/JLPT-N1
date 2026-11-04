from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit139';R=ROOT/'release139';R.mkdir(exist_ok=True)
base=(ROOT/'JLPT_N1_ukrainian_reading_v138.html').read_text();assert hashlib.sha256(base.encode()).hexdigest()=='6f7ea6a3d4ca30e8a9cc6ffad31994d99e925809fa4d4b94fe2bf28349027dfc'
def get(n):return json.JSONDecoder().raw_decode(base[re.search(r'const '+n+r'\s*=\s*',base).end():])[0]
v,g,vd,gd=[get(n) for n in ['DEFAULT_VOCAB','GRAMMAR','VOCAB_DETAILS_BY_ID','GRAMMAR_DETAILS_BY_ID']]
# Stable identity and progress; ordinary noun spelling, not an isolated kanji mnemonic.
v[715]['w']='恵み';v[715]['c']='名詞(その他)'
vd['716']['w']='恵み';vd['716']['t']='дари, благо, благодіяння'
vd['716']['usage']='恵み（めぐみ）— отримане благо або дар. 自然の恵み — дари природи; 恵みを受ける — отримувати благо.\n\nЗвичайне написання іменника — 恵み. 恵まれる — окреме дієслово зі значенням «бути обдарованим чимось, мати сприятливі умови».'
vd['790']['examples'][1]='警察は各地に捜査の網を張り、容疑者の行方を追っている。'
vd['790']['exampleTranslations'][1]='Поліція розгорнула в різних місцях мережу розшуку й намагається встановити місцеперебування підозрюваного.'
ns=dict(P=P,v=v,g=g,vd=vd,gd=gd);exec((P/'author.py').read_text(),ns);records=ns['records'];assert len(records)==237
allrecords=get('REVIEWED_EXAMPLE_TARGETS')+records

def replace_data(s,name,value):
 m=re.search(r'const '+name+r'\s*=\s*',s);_,end=json.JSONDecoder().raw_decode(s[m.end():]);return s[:m.end()]+json.dumps(value,ensure_ascii=False,separators=(',',':'))+s[m.end()+end:]
s=base
for name,value in [('DEFAULT_VOCAB',v),('VOCAB_DETAILS_BY_ID',vd),('REVIEWED_EXAMPLE_TARGETS',allrecords)]:s=replace_data(s,name,value)
s=s.replace("explain: reviewedExampleTarget(ex,it.kind,label) ?", "explain: reviewedExampleTarget(ex,it.kind,label)?.quiz ?")
s=s.replace('太字の語「${label}」の読み方として最も適切なものはどれか。','見出し語「${label}」の読み方として最も適切なものはどれか。')
s=s.replace('学習アプリ · v138','学習アプリ · v139')
(R/'JLPT_N1_ukrainian_reading_v139.html').write_text(s);(P/'app.js').write_text(s.split('<script>',1)[1].split('</script>',1)[0]);(P/'targets.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
# One decision for every historical candidate. Original triage remains immutable.
key=lambda x:(x['kind'],x['id'],x['exampleIndex'])
bykey={key(x):x for x in records};decisions=[]
for row in json.loads((ROOT/'completion/target-triage.json').read_text())['singleCharacter']:
 target=bykey.get(key(row));d={k:row[k] for k in ['kind','id','word','exampleIndex','sentence','spans','technicalClass']}
 if target:
  d.update(decision='replace_with_exact_surface',forms=target['forms'],currentWord=target['word'],rationale=('Повна реалізована граматична конструкція; контекстний ключ і три перевірені альтернативи.' if row['kind']=='g' else 'Точна форма цього слова в реченні: відмінювання, звичайне написання або повторення; не скорочений один кандзі.'))
 elif row['id']==790 and row['exampleIndex']==1:
  d.update(decision='replace_example',sentenceNow=vd['790']['examples'][1],forms=['網'],rationale='Інформаційна мережа 情報網 має читання もう, а картка — あみ. Новий природний переносний приклад 捜査の網 зберігає あみ; 〜網 ID3733 лишається окремою карткою.')
 else:
  reason='Окремий іменник або змістово відповідна морфема цього слова; один знак не є обрізаною дієслівною формою.'
  if row['id']>=3693:reason='Навчальна ціль — саме однознаковий префікс/суфікс '+row['word']+'; у цьому слові він реалізований повністю. Виділяти ціле складене слово замість афікса не потрібно.'
  d.update(decision='retain',forms=row['spans'],rationale=reason)
 decisions.append(d)
assert len(decisions)==526
(P/'adjudications.json').write_text(json.dumps(dict(scope='Author review of target identity/boundaries only, not all card fields or every distractor.',rows=decisions),ensure_ascii=False,indent=2))
summary=dict(version=139,baseSha256=hashlib.sha256(base.encode()).hexdigest(),sha256=hashlib.sha256(s.encode()).hexdigest(),bytes=len(s.encode()),reviewedCandidates=526,newExactTargets=len(records),totalExactTargets=len(allrecords),decisions={k:sum(x['decision']==k for x in decisions) for k in sorted({x['decision'] for x in decisions})},affectedCards=len({(x['kind'],x['id']) for x in records}|{('v',790)}))
(P/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps(summary))
