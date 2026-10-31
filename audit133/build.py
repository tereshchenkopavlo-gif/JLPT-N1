import json,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
P=ROOT/'audit133';R=ROOT/'release133';R.mkdir(exist_ok=True)
base=(ROOT/'JLPT_N1_ukrainian_reading_v132.html').read_text()
assert hashlib.sha256(base.encode()).hexdigest()=='bc6b932e63fd07b74d8b4acbf843c1214ce1638f345e5473d3c51cfac527a456'

def data_spans(s):
    spans=[]
    a=s.index('const AUTO_VOCAB_COMPARISONS =');b=s.index('for (const [a,b,note] of GRAMMAR_AUDITED_PAIRS)',a)
    spans.append((a,b))
    decoder=json.JSONDecoder()
    for match in re.finditer(r'const\s+\w+\s*=\s*(?=[\[{])',s):
        start=match.end()
        if any(a<=start<b for a,b in spans):continue
        try:_,length=decoder.raw_decode(s[start:])
        except ValueError:continue
        spans.append((start,start+length))
    return sorted(spans)

mapping=json.loads((P/'localization.json').read_text())
counts={key:0 for key in mapping}
def translate(chunk):
    for old,new in sorted(mapping.items(),key=lambda item:-len(item[0])):
        counts[old]+=chunk.count(old);chunk=chunk.replace(old,new)
    return chunk
parts=[];cursor=0
for start,end in data_spans(base):
    parts.extend([translate(base[cursor:start]),base[start:end]]);cursor=end
parts.append(translate(base[cursor:]));s=''.join(parts)
assert all(counts.values()),{k:v for k,v in counts.items() if not v}
s=s.replace('学習アプリ · v132','学習アプリ · v133')
s=s.replace('<html lang="uk">','<html lang="ja">')
s=s.replace('<div class="fc-trans">','<div class="fc-trans" lang="uk">')
s=s.replace('<div class="reading-translation">','<div class="reading-translation" lang="uk">')

top='''      <div class="card-nav" aria-label="カードの移動">
        <button type="button" class="btn btn-outline" id="btnCardPrev" data-card-step="-1">← 前のカード</button>
        <div class="card-nav-info"><span class="card-position" aria-live="polite"></span><small id="cardNavScope"></small></div>
        <button type="button" class="btn btn-outline" id="btnCardNext" data-card-step="1">次のカード →</button>
      </div>
      <div class="small card-nav-hint">左右のスワイプや ← → キーでも移動できます。</div>
'''
bottom='''      <div class="card-nav card-nav-bottom" aria-label="カードの移動">
        <button type="button" class="btn btn-outline" id="btnCardPrevBottom" data-card-step="-1">← 前のカード</button>
        <span class="card-position" aria-hidden="true"></span>
        <button type="button" class="btn btn-outline" id="btnCardNextBottom" data-card-step="1">次のカード →</button>
      </div>'''
needle='      <div class="card flashcard" id="cardDetailBody"></div>'
assert s.count(needle)==1;s=s.replace(needle,top+needle+'\n'+bottom)
css='''
/* Card navigation: both ends of long cards, without changing learning state. */
.card-nav { display:grid; grid-template-columns:minmax(0,1fr) auto minmax(0,1fr); gap:8px; align-items:center; margin-bottom:12px; }
.card-nav .btn { min-width:0; width:100%; padding:10px 4px; font-size:14px; }
.card-nav-info { text-align:center; min-width:55px; }
.card-nav-info small { display:block; font-size:10px; color:var(--ink-soft); }
.card-position { text-align:center; font-size:12px; white-space:nowrap; }
.card-nav-hint { margin-bottom:12px; }
.card-nav-bottom { margin-top:14px; }
#cardDetailBody { touch-action:pan-y pinch-zoom; }
'''
s=s.replace('</style>',css+'\n</style>',1)
a=s.index('let cardNavKeys = [];');b=s.index("document.getElementById('btnCardBack').addEventListener",a)
s=s[:a]+(P/'navigation.js').read_text()+'\n'+s[b:]
s=s.replace("cardNavKeys = getCardPool().map(it => it.kind + '_' + it.id);","cardNavKeys = getCardPool().map(it => it.kind + '_' + it.id);\n      cardNavScope = 'filtered';")
s=s.replace("document.getElementById('cardDetailPanel').style.display = 'none';\n  document.getElementById('cardListPanel').style.display = '';", "cardDetailRequest++;\n  document.getElementById('cardDetailPanel').style.display = 'none';\n  document.getElementById('cardListPanel').style.display = '';")
# Ignore a late refresh after the user has already navigated elsewhere.
needle='''    container.innerHTML = renderCardShell(kind, id, data);
    bindChips(container);'''
replacement='''    if (container.id === 'cardDetailBody' && container.dataset.currentKey !== kind + '_' + id) return;
    container.innerHTML = renderCardShell(kind, id, data);
    bindChips(container);'''
assert s.count(needle)==1;s=s.replace(needle,replacement)

helper='''const STUDY_SECTION_LABELS = {
  'Спільне':'共通点', 'Приєднання':'接続', 'Різниця':'違い', 'Приклади':'例文', 'Заміна':'置き換え',
  'Вживання':'用法', 'Уживання':'用法', 'Обмеження':'制約', 'Стиль':'文体'
};
function localizeStudyHeadings(text) {
  return String(text || '').replace(/【([^】]+)】/g, (whole,label) =>
    STUDY_SECTION_LABELS[label] ? '【' + STUDY_SECTION_LABELS[label] + '】' : whole)
    .replace(/(Приєднання|Спільне|Різниця|Приклади|Заміна|Вживання|Уживання|Обмеження|Стиль):/g,
      (whole,label) => STUDY_SECTION_LABELS[label] + '：');
}

'''
s=s.replace('function lexicalPairHeading(type) {',helper+'function lexicalPairHeading(type) {')
s=s.replace("const parts = String(note || '').split(kind", "const parts = localizeStudyHeadings(note).split(kind")
s=s.replace('${escapeGuide(part)}</p>', '${localizeStudyHeadings(escapeGuide(part))}</p>')
s=s.replace('${escapeLex(p.note)}</div>', '${localizeStudyHeadings(escapeLex(p.note))}</div>')
s=s.replace("${data.translation || ''}","${localizeStudyHeadings(data.translation)}")
s=s.replace('${escapeLex(data.usage)}','${localizeStudyHeadings(escapeLex(data.usage))}')
s=s.replace('${escapeLex(it.usage)}','${localizeStudyHeadings(escapeLex(it.usage))}')
s=s.replace("${it.translation || 'ウクライナ語訳は未登録です'}","${localizeStudyHeadings(it.translation) || 'ウクライナ語訳は未登録です'}")

out=R/'JLPT_N1_ukrainian_reading_v133.html';out.write_text(s)
(P/'app.js').write_text(s.split('<script>',1)[1].split('</script>',1)[0])
summary=dict(sha256=hashlib.sha256(s.encode()).hexdigest(),bytes=len(s.encode()),localizedStrings=len(mapping),replacementCounts=counts)
(P/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in summary.items() if k!='replacementCounts'},ensure_ascii=False))
