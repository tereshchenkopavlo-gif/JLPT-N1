// Reading options preserve all visible kana and differ only in the hidden reading core.
function readingFrame(word) { return String(word).replace(/[一-鿿々]+/g,'#'); }
function readingDistance(a,b) {
  const row=Array.from({length:b.length+1},(_,i)=>i);
  for(let i=1;i<=a.length;i++){let prev=row[0];row[0]=i;for(let j=1;j<=b.length;j++){const old=row[j];row[j]=Math.min(row[j]+1,row[j-1]+1,prev+(a[i-1]===b[j-1]?0:1));prev=old;}}
  return row[b.length];
}
function quizReadingOptions(item) {
  const v=item.word;
  if(item.kind!=='v'||!v.r||!/^[ぁ-ゟー]+$/.test(v.r)||!/[一-鿿]/.test(v.w)||/[〜～・／/]/.test(v.w))return [];
  const reviewed=REVIEWED_READING_OPTIONS[String(item.id)];
  if(reviewed && reviewed.word===v.w && reviewed.correct===v.r)return reviewed.wrong.slice();
  const frame=readingFrame(v.w),pos=vocabPartOfSpeech(v.id).join('|');
  const prefix=(v.w.match(/^[ぁ-ゟー]+/)||[''])[0],tail=(v.w.match(/[ぁ-ゟー]+$/)||[''])[0];
  if(prefix&&!v.r.startsWith(prefix)||tail&&!v.r.endsWith(tail))return [];
  const core=v.r.slice(prefix.length,tail.length?-tail.length:undefined);
  const candidates=ACTIVE_VOCAB.filter(x=>x.id!==v.id&&x.r!==v.r&&/^[ぁ-ゟー]+$/.test(x.r||'')&&readingFrame(x.w)===frame&&vocabPartOfSpeech(x.id).join('|')===pos&&Math.abs(x.r.length-v.r.length)<=1&&(!prefix||x.r.startsWith(prefix))&&(!tail||x.r.endsWith(tail)))
    .map(x=>({r:x.r,d:readingDistance(core,x.r.slice(prefix.length,tail.length?-tail.length:undefined))})).filter(x=>x.d>0&&x.d<=2).sort((a,b)=>a.d-b.d||a.r.localeCompare(b.r));
  return [...new Set(candidates.map(x=>x.r))].slice(0,6);
}
function literalClozeAvailable(sentence,item,engine) {
  if(item.kind!=='v'||/[〜～・／/]/.test(item.word.w))return false;
  const marked=engine.markTarget(sentence,item.kind,item.word.w);
  const spans=[...marked.s.matchAll(/\u0001([^\u0002]*)\u0002/g)].map(m=>m[1]);
  return marked.found&&spans.length===1&&spans[0]===item.word.w;
}
function clozeWordCandidates(item) {
  if(item.kind!=='v')return [];
  const pos=vocabPartOfSpeech(item.id).join('|');
  return [...new Set(ACTIVE_VOCAB.filter(v=>v.id!==item.word.id&&VOCAB_DETAILS_BY_ID[v.id]&&vocabPartOfSpeech(v.id).join('|')===pos&&!/[〜～・／/]/.test(v.w)).map(v=>v.w))];
}
function readingGlossaryEntryHtml(g) {
  const quote=g.quote && g.quote!==g.label ? `<div lang="ja">${escapeLex(g.quote)}</div>`:'';
  const context=g.context||g.meaning;
  const meaning=g.translation
    ? escapeLex(g.translation)+(context&&context!==g.translation?` (тут — ${escapeLex(context)})`:'')
    : escapeLex(g.meaning||'');
  return `<div><b>${escapeLex(g.label)}</b>${quote}<span>${meaning}</span></div>`;
}
