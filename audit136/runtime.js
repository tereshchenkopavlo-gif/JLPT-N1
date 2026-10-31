// v136: shared presentation for cards and comparisons; original learning data stays intact.
function vocabPartOfSpeech(id) { return VOCAB_POS_BY_ID[String(id)] || ['連語']; }
function wordPosHtml(item) {
  if (item.kind !== 'v') return '';
  return `<span class="word-pos" lang="ja" aria-label="品詞：${vocabPartOfSpeech(item.id).join('・')}">${vocabPartOfSpeech(item.id).map(p=>`<span>${escapeLex(p)}</span>`).join('')}</span>`;
}
function displayUsageText(value, kind) {
  if (kind !== 'v') return String(value || '');
  // Remove only a standalone leading POS label. Inflection, transitivity and restrictions remain.
  return String(value || '').replace(/^(?:Іменник|Дієслово|Прислівник|[なナ][-‑]прикметник|[いイ][-‑]прикметник)\s*(?:[;:,—–]\s*|\.\s+)/u, '');
}
function cardStudyModel(kind, data) {
  let translation=String(data.translation || ''), usage=String(data.usage || '');
  if (kind === 'g') {
    const boundary=translation.match(/(?:Приєднання|Форма):\s*/u);
    if (boundary) {
      usage=translation.slice(boundary.index)+(usage?'\n'+usage:'');
      translation=translation.slice(0,boundary.index).trim();
    }
  }
  return {translation,usage:displayUsageText(usage,kind)};
}
function studyProseHtml(value) {
  const paragraph = text => text.trim() === '/' ? '<span class="study-example-separator" aria-hidden="true">/</span>' : text.trim().split(/(?<=[。.!?])\s+(?![—–])|(?<=;)\s*(?=[一-鿿ぁ-ゟァ-ヿ][^;。.!?]{0,32}\s*[—–])/u).filter(Boolean).map(part=>{
    const term=part.match(/^([一-鿿ぁ-ゟァ-ヿー〜～][^А-Яа-яІЇЄҐіїєґ]{0,48}?)\s*([—–])\s*(.+)$/u);
    return `<p class="study-paragraph">${term?`<strong lang="ja">${escapeLex(term[1].trim())}</strong> ${term[2]} ${escapeLex(term[3])}`:escapeLex(part)}</p>`;
  }).join('');
  // Only an explicit Japanese full sentence + dash + Ukrainian translation becomes an example.
  // Other punctuation is retained. No automatic semantic rewriting or short-stem matching.
  const pattern=/([「『（]?[一-鿿ぁ-ゟァ-ヿ][一-鿿ぁ-ゟァ-ヿーA-Za-z0-9０-９\s、，「」『』（）()〜～＋／\/・＝｛｝：:;!?―—–−\-]*。)\s*([—–])\s*([^。]*?[.!?](?=\s|$)|[^。]+$)/gu;
  let html='',cursor=0;
  for(const m of value.matchAll(pattern)) {
    if(!/[А-Яа-яІЇЄҐіїєґ]/u.test(m[3])) continue;
    html+=paragraph(value.slice(cursor,m.index));
    html+=`<div class="study-example"><div lang="ja">${escapeLex(m[1].trim())}</div><div class="study-example-translation" lang="uk">${m[2]} ${escapeLex(m[3].trim())}</div></div>`;
    cursor=m.index+m[0].length;
  }
  return html+paragraph(value.slice(cursor));
}
function studyTextHtml(value) {
  const text=localizeStudyHeadings(value).replace(/Форма:/g,'形：');
  const marked=text.replace(/(^|\s)(接続|形|共通点|違い|例文|置き換え|用法|制約|文体)：/gu,'$1【$2】');
  const parts=marked.split(/(【[^】]+】)/u).filter(Boolean);
  return `<div class="study-text">${parts.map(part=>/^【[^】]+】$/u.test(part)?`<div class="study-subheading" lang="ja">${escapeLex(part.slice(1,-1))}</div>`:studyProseHtml(part)).join('')}</div>`;
}
function lexicalNoteHtml(pair) {
  const key=[Number(pair.a),Number(pair.b)].sort((a,b)=>a-b).join('_');
  const layout=LEXICAL_PRESENTATION[key];
  if (!layout) return studyTextHtml(pair.note);
  return `<div class="study-text curated-study">${layout.map(block=>{
    if(block.type==='heading')return `<div class="study-subheading" lang="ja">${escapeLex(block.text)}</div>`;
    if(block.type==='term')return `<p class="study-paragraph"><strong lang="ja">${escapeLex(block.term)}</strong> — ${escapeLex(block.text)}</p>`;
    if(block.type==='example')return `<div class="study-example"><div lang="ja">${escapeLex(block.ja)}</div><div class="study-example-translation" lang="uk">— ${escapeLex(block.uk)}</div></div>`;
    return `<p class="study-paragraph">${escapeLex(block.text)}</p>`;
  }).join('')}</div>`;
}
