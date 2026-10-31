from pathlib import Path
import json,re,hashlib
from collections import Counter
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit136';R=ROOT/'release136';R.mkdir(exist_ok=True)
s=(ROOT/'JLPT_N1_ukrainian_reading_v135.html').read_text();assert hashlib.sha256(s.encode()).hexdigest()=='142c5b7d3ad77b034d17778885de83fd928cdd2c99d1f06c9ad3012012353a12'
get=lambda n:json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
pos={};unhandled=[]
for x in get('DEFAULT_VOCAB'):
 c=x['c'];w=x['w'];labels=[]
 if c=='名詞・動詞':labels=['動詞'] if w.endswith('する') else ['名詞','動詞']
 elif c=='名詞・形容動詞':labels=['名詞','ナ形']
 elif c=='副詞・形容動詞':labels=['副詞','ナ形']
 elif c=='副詞・接続詞':labels=['副詞','接続詞']
 elif c.startswith('名詞'):labels=['名詞']+(['副詞'] if '副詞的' in c else [])
 elif c.startswith('動詞'):labels=['動詞']
 elif c.startswith('な形容詞'):labels=['ナ形']
 elif c=='い形容詞':labels=['イ形']
 elif c.startswith('副詞'):labels=['副詞']
 elif c.startswith('カタカナ'):labels=['ナ形'] if x['s']=='な' else ['名詞']
 elif c.startswith('代名詞'):labels=['代名詞']
 elif c in ['接尾語','接頭語','接続詞','連体詞','副助詞']:labels=[c]
 elif c in ['尊敬語','謙譲語','謙譲語Ⅱ（丁重語）']:labels=['連語'] if x['id']==3804 else ['動詞']
 elif c=='敬語表現':labels=['名詞'] if x['id']>=3901 else ['定型表現']
 elif c=='書簡表現':labels=['定型表現']
 elif c=='慣用表現':labels=['慣用句']
 elif c.startswith('四字熟語'):labels=['四字熟語']+(['ナ形'] if '形容動詞' in c else [])
 elif c=='連語':labels=['連語']
 else:unhandled.append(x)
 if c.startswith('名詞') and x['s']=='な' and 'ナ形' not in labels:labels.append('ナ形')
 pos[str(x['id'])]=labels
assert not unhandled,unhandled
# Treat nominal する forms as nouns; keep the full inflection and transitivity note in usage.
labels=['名詞','動詞','ナ形','イ形','副詞','代名詞','連体詞','接続詞','副助詞','接頭語','接尾語','連語','慣用句','四字熟語','定型表現']
counts={k:sum(k in a for a in pos.values()) for k in labels};labels=[k for k in labels if counts[k]]
options='<option value="all">全品詞</option>'+''.join(f'<option value="{k}">{k}</option>' for k in labels)
needle='      <div class="cat-chips-wrap" id="categoryChips">';assert s.count(needle)==1
s=s.replace(needle,'      <div class="pos-filter" id="cardPosFilter"><label for="cardPos">品詞</label><select id="cardPos">'+options+'</select></div>\n'+needle)
needle='function getAllItems() {';assert s.count(needle)==1
s=s.replace(needle,'const VOCAB_POS_BY_ID = '+json.dumps(pos,ensure_ascii=False,separators=(',',':'))+';\nconst LEXICAL_PRESENTATION = '+json.dumps(json.loads((P/'presentation.json').read_text()),ensure_ascii=False,separators=(',',':'))+';\n'+(P/'runtime.js').read_text()+'\n'+needle)
s=s.replace('</style>',(P/'style.css').read_text()+'\n</style>',1)
s=s.replace('let selectedCategory = \'all\';','let selectedCategory = \'all\';\nlet selectedPos = \'all\';')
s=s.replace("  pool = pool.filter(it => it.kind === cardFilter);","  pool = pool.filter(it => it.kind === cardFilter);\n  if (cardFilter === 'v' && selectedPos !== 'all') pool = pool.filter(it => vocabPartOfSpeech(it.id).includes(selectedPos));")
s=s.replace("    cardFilter = b.dataset.f;","    cardFilter = b.dataset.f;\n    document.getElementById('cardPosFilter').style.display = cardFilter === 'v' ? 'flex' : 'none';")
needle="document.getElementById('cardHideMastered').addEventListener('change', () => {"
s=s.replace(needle,"document.getElementById('cardPos').addEventListener('change', event => {\n  selectedPos = event.target.value;\n  curPage = 1;\n  renderCardsList();\n});\n"+needle)
s=s.replace('<div class="patt">${it.label}</div>','<div class="patt">${escapeLex(it.label)} ${wordPosHtml(it)}</div>')
s=s.replace('<div class="fc-word">${it.label} ${badge} ${spkBtn}</div>','<div class="fc-word">${escapeLex(it.label)} ${wordPosHtml(it)} ${badge} ${spkBtn}</div>')
s=s.replace("  const reading = data.reading || it.reading || '';","  const reading = data.reading || it.reading || '';\n  const study = cardStudyModel(kind, data);")
s=s.replace('${localizeStudyHeadings(data.translation)}</div>','${studyTextHtml(study.translation)}</div>')
s=s.replace('${data.usage ? `<div class="fc-section-label">用法・接続</div><div class="fc-trans" lang="uk">${localizeStudyHeadings(escapeLex(data.usage))}</div>` : \'\'}','${study.usage ? `<div class="fc-section-label">用法・接続</div><div class="fc-trans" lang="uk">${studyTextHtml(study.usage)}</div>` : \'\'}')
s=s.replace('<div class="nuance-lines"><div class="nuance-line">${localizeStudyHeadings(escapeLex(p.note))}</div></div>','${lexicalNoteHtml(p)}')
a=s.index('  const formatNuance = note => {');b=s.index('  const visibleRelatedLabels',a);s=s[:a]+'  const formatNuance = note => studyTextHtml(note);\n'+s[b:]
s=s.replace("+ '</h3><p>' + escapeLex(p.note) + '</p></div>';","+ '</h3>' + lexicalNoteHtml(p) + '</div>';")
s=s.replace("sections.map(part => `<p>${localizeStudyHeadings(escapeGuide(part))}</p>`).join('')","studyTextHtml(note)")
s=s.replace('<h3>${it.label}</h3>','<h3>${escapeLex(it.label)} ${wordPosHtml(it)}</h3>')
s=s.replace('${localizeStudyHeadings(it.translation) || \'ウクライナ語訳は未登録です\'}','${studyTextHtml(cardStudyModel(it.kind,it).translation) || \'ウクライナ語訳は未登録です\'}')
s=s.replace('${it.usage ? `<div class="compare-ua"><b>用法・接続：</b> ${localizeStudyHeadings(escapeLex(it.usage))}</div>` : \'\'}','${cardStudyModel(it.kind,it).usage ? `<div class="compare-ua"><div class="study-subheading">用法・接続</div>${studyTextHtml(cardStudyModel(it.kind,it).usage)}</div>` : \'\'}')
s=s.replace('学習アプリ · v135','学習アプリ · v136')
(R/'JLPT_N1_ukrainian_reading_v136.html').write_text(s);(P/'app.js').write_text(s.split('<script>',1)[1].split('</script>',1)[0])
(P/'pos.json').write_text(json.dumps(pos,ensure_ascii=False,indent=2))
summary=dict(sha256=hashlib.sha256(s.encode()).hexdigest(),bytes=len(s.encode()),vocab=len(pos),grammar=130,texts=160,questions=381,posCounts=counts,structuredPresentationPairs=['58_75'])
(P/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False))
