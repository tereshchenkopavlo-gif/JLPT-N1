"""Six original question drafts, bound to existing examples, never installed in HTML."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;raw=json.loads((P/'probe.json').read_text());cases={x['id']:x for x in raw['grammarCases']}
drafts={
8:('広く紹介され注目を集めたため、客が大勢訪れたことを述べる。',[
 '紹介されるかどうかにかかわらず、客の数は変わらないと述べる。',
 '客の行列を見て、以前紹介されたのだろうと推測している。',
 '紹介されることを条件として、今後の来店を呼びかけている。']),
10:('経験の少なさを、適切に判断できなかった原因として述べる。',[
 '経験は浅いが、判断には影響しなかったと述べる。',
 '経験が浅いかどうか、まだ判断できないと述べる。',
 '経験を積むために、判断をあえて避けたと述べる。']),
27:('この大会を最後として、競技者としての活動を終えると述べる。',[
 'この大会が終わってから、競技者としての活動を始めると述べる。',
 'この大会の期間だけ休み、その後は競技を続けると述べる。',
 'この大会までに、引退するかどうかを決めたいと述べる。']),
61:('シャッターが上がると、間を置かず客が入ったことを述べる。',[
 'シャッターが上がる前に、すでに客が入っていたことを述べる。',
 'シャッターが上がった後、しばらく待って客が入ったことを述べる。',
 '客が入り終えることを、シャッターを上げる条件として述べる。']),
89:('恩師への礼を、結局伝えないままになったことを述べる。',[
 '恩師への礼を伝え終えてから、忙しくなったことを述べる。',
 '恩師への礼を伝える必要が、途中でなくなったことを述べる。',
 '恩師への礼を伝えたが、相手に届かなかったことを述べる。']),
130:('以前に世話になった、その時のことを指している。',[
 'これから初めて世話になる、将来の時のことを指している。',
 '相手の世話を受けている、まさに現在の時のことを指している。',
 '世話になった時期には触れず、相手の人柄だけを評価している。'])
}
rows=[]
for id,(correct,wrong)in drafts.items():
 assert len(wrong)==3 and len(set([correct,*wrong]))==4
 rows.append(dict(grammarId=id,exampleIndex=0,word=cases[id]['word'],sentenceSha256=hashlib.sha256(cases[id]['sentence'].encode()).hexdigest(),correct=correct,wrong=wrong,status='draft_not_installed',origin='original_editorial_draft_20261105',approvedForRuntime=False))
(P/'proposed-grammar-questions.json').write_text(json.dumps(dict(sha256=raw['sha256'],scope='Six proposed content corrections, not an algorithm change or installed learning material; second examples and runtime calls still need verification.',drafts=rows),ensure_ascii=False,indent=2)+'\n')
print('Six drafts generated; none installed')
