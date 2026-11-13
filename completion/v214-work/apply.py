import csv,hashlib,json,re
from pathlib import Path
BASE=Path("JLPT_N1_ukrainian_reading_v213.html")
OUT=Path("JLPT_N1_ukrainian_reading_v214.html")
WORK=Path("completion/v214-work")
REGISTER=Path("completion/review-register.csv")
BASE_SHA="806a4649ec32fa1d85fd3cd7066fcdcc05432ea88f2b1e7218e891e35aebb50c"
UPDATES=[
 ("1632","t","взаємний; такий, що діє між двома або кількома сторонами","взаємність; взаємний, обопільний"),
 ("1635","t","загальні збори, пленарне засідання","загальні збори організації"),
 ("1637","t","трав'янисті квіти, трави й квіти","квіткові трав’янисті рослини; трави й квіти"),
 ("1651","t","матеріальна чи інша шкода, що підлягає оцінці або відшкодуванню","шкода, збитки"),
 ("1654","m","対立する双方が、互いに譲り合って折り合いをつけること。","対立する双方が、互いに譲り合って折り合いをつけること。また、自分の要求や基準を譲ること。"),
 ("1666","exampleTranslations[1]","Орендареві запропонували виїхати через тривалу заборгованість з орендної плати.","Через тривалу заборгованість з орендної плати орендареві висунули вимогу звільнити помешкання."),
 ("1675","exampleTranslations[1]","Домовилися перейти до узгодження деталей, визначивши основні положення переговорів.","З’ясувавши загальний напрям переговорів, домовилися перейти до узгодження деталей."),
 ("1676","t","велика сума, велика партія (угода), великі обсяги","великий рот; хвастощі, самовпевнені слова; велика сума або обсяг угоди чи замовлення"),
 ("1679","m","力や地位が大きい人物。また、大きな獲物。","力や地位が大きい人物。また、大きな物や獲物。"),
 ("1679","exampleTranslations[1]","Він привертає увагу як новачок, у якому вже відчувається масштаб майбутнього майстра.","Він привертає увагу як новачок, що вже має поставу впливової постаті."),
 ("1682","exampleTranslations[0]","Керівника компанії офіційно звинуватили за підозрою в ухиленні від податків на величезну суму.","На керівника компанії подали заяву до правоохоронних органів за підозрою у масштабному ухиленні від сплати податків."),
 ("1688","m","心身や技術を、繰り返し鍛えて磨くこと。","心身や技術を、繰り返し鍛えて磨くこと。また、金属を打ち鍛えること。"),
 ("1690","t","пружність, еластичність","пружність, еластичність; переносно — гнучкість у пристосуванні до обставин")
]
EXPECTED={
 "1632":("相互","そうご",["名詞"]),
 "1635":("総会","そうかい",["名詞"]),
 "1637":("草花","くさばな",["名詞"]),
 "1651":("損害","そんがい",["名詞"]),
 "1654":("妥協","だきょう",["名詞"]),
 "1666":("滞納","たいのう",["名詞"]),
 "1675":("大筋","おおすじ",["名詞"]),
 "1676":("大口","おおぐち",["名詞"]),
 "1679":("大物","おおもの",["名詞"]),
 "1682":("脱税","だつぜい",["名詞"]),
 "1688":("鍛錬","たんれん",["名詞"]),
 "1690":("弾力","だんりょく",["名詞"])
}
BASE_EXAMPLES={
 "1632":["両国は、相互の利益を尊重しながら経済協力を進めている。","異なる文化の相互理解を深めることが、国際交流の目的である。"],
 "1635":["定時の株主総会で、役員の報酬に関する議案が承認された。","組合の総会には、全国から多くの代表者が出席した。"],
 "1637":["庭には、季節ごとに咲く草花が丁寧に植えられている。","山道の脇に咲く草花が、登山者の疲れを癒してくれる。"],
 "1651":["台風による農作物の損害は、総額で数十億円にのぼると見られる。","契約違反によって生じた損害の賠償を、相手方に請求した。"],
 "1654":["品質に関しては、どんな状況でも妥協してはならないというのが社の方針だ。","労使は交渉を重ね、ようやく妥協点を見出した。"],
 "1666":["税金を滞納した場合は、延滞金が加算されることになる。","家賃の滞納が続き、入居者は退去を求められた。"],
 "1675":["計画の大筋については、すでに関係者の間で合意が得られている。","交渉の大筋を押さえたうえで、細部の調整に入ることになった。"],
 "1676":["大口の注文が入ったため、工場はフル稼働の状態が続いている。","大口の取引先に対しては、特別な割引条件を設けている。"],
 "1679":["政界の大物と目される人物が、突如として引退を表明した。","彼は、大物の風格をそなえた新人として注目されている。"],
 "1682":["巨額の脱税を行った疑いで、会社の経営者が告発された。","脱税を防ぐため、国税当局は調査の体制を強化している。"],
 "1688":["長年の鍛錬によって、彼は卓越した技術を身につけた。","心身を鍛錬することで、困難に屈しない精神力が養われる。"],
 "1690":["この素材は、強い弾力があるため、衝撃を吸収するのに適している。","弾力のある運営が、変化の激しい市場で生き残る鍵となる。"]
}
FIXED_IDS=[1632,1635,1637,1651,1654,1666,1675,1676,1679,1682,1688,1690]
PAIR_KEYS=["417:1651:1652","421:1666:1682"]
def extract(source,name):
 m=re.search(r"\bconst "+re.escape(name)+r"\s*=\s*",source)
 if not m: raise RuntimeError("missing constant "+name)
 start=m.end(); opening=source[start]; closing="]" if opening=="[" else "}"
 depth=0; inside=False; escaped=False
 for i in range(start,len(source)):
  c=source[i]
  if inside:
   if escaped: escaped=False
   elif c=="\\": escaped=True
   elif c=='"': inside=False
  else:
   if c=='"': inside=True
   elif c==opening: depth+=1
   elif c==closing:
    depth-=1
    if depth==0: return start,i+1,json.loads(source[start:i+1]),source[start:i+1]
 raise RuntimeError("unterminated constant "+name)
def counts(rows,kind=None):
 sel=[r for r in rows if kind is None or r["kind"]==kind]
 out={s:sum(r["finalReview"]==s for r in sel) for s in ("reviewed","fixed_rechecked","pending")}
 out["total"]=len(sel)
 return out
WORK.mkdir(parents=True,exist_ok=True)
raw=BASE.read_bytes()
base_sha=hashlib.sha256(raw).hexdigest()
if base_sha!=BASE_SHA: raise RuntimeError("unexpected v213 base SHA-256: "+base_sha)
base=raw.decode("utf-8")
ds,de,details,dorig=extract(base,"VOCAB_DETAILS_BY_ID")
_,_,pos,posorig=extract(base,"VOCAB_POS_BY_ID")
_,_,vocab,_=extract(base,"DEFAULT_VOCAB")
_,_,grammar,_=extract(base,"GRAMMAR_DETAILS_BY_ID")
_,_,pairs,_=extract(base,"VOCAB_AUDITED_PAIRS")
_,_,meaning,_=extract(base,"REVIEWED_MEANING_QUIZZES")
_,_,reading,_=extract(base,"REVIEWED_READING_OPTIONS")
_,_,kana,_=extract(base,"VOCAB_KANA_EXAMPLE_TARGETS")
_,_,targets,_=extract(base,"REVIEWED_EXAMPLE_TARGETS")
if (len(vocab),len(grammar),len(details),len(pairs))!=(3914,130,3914,859): raise RuntimeError("protected inventory counts mismatch")
by_id={str(x["id"]):x for x in vocab}
for cid,(word,rd,p) in EXPECTED.items():
 if cid not in by_id or (by_id[cid]["w"],by_id[cid]["r"],pos[cid])!=(word,rd,p): raise RuntimeError("identity/POS preimage mismatch "+cid)
 if details[cid]["examples"]!=BASE_EXAMPLES[cid]: raise RuntimeError("Japanese example preimage mismatch "+cid)
before=json.loads(json.dumps(details,ensure_ascii=False))
for cid,field,old,new in UPDATES:
 if "[" in field:
  key=field.split("[")[0]; index=int(re.search(r"\[(\d+)\]",field).group(1))
  if details[cid][key][index]!=old: raise RuntimeError("preimage mismatch "+cid+"."+field)
  details[cid][key][index]=new
 else:
  if details[cid][field]!=old: raise RuntimeError("preimage mismatch "+cid+"."+field)
  details[cid][field]=new
changed=sorted((cid for cid in details if details[cid]!=before[cid]),key=int)
if changed!=sorted(map(str,FIXED_IDS),key=int): raise RuntimeError("changed-card set mismatch "+str(changed))
allowed={
 "1632":{"t"},"1635":{"t"},"1637":{"t"},"1651":{"t"},"1654":{"m"},
 "1666":{"exampleTranslations"},"1675":{"exampleTranslations"},"1676":{"t"},
 "1679":{"m","exampleTranslations"},"1682":{"exampleTranslations"},
 "1688":{"m"},"1690":{"t"}
}
for cid in details:
 for field in before[cid]:
  if before[cid][field]!=details[cid][field] and field not in allowed.get(cid,set()):
   raise RuntimeError("unexpected field mutation "+cid+"."+field)
details_literal=json.dumps(details,ensure_ascii=False,separators=(",",":"))
candidate=base[:ds]+details_literal+base[de:]
old="<title>JLPT N1 — ウクライナ語対応学習アプリ · v213</title>"
new="<title>JLPT N1 — ウクライナ語対応学習アプリ · v214</title>"
if candidate.count(old)!=1: raise RuntimeError("version title marker mismatch")
candidate=candidate.replace(old,new,1)
rollback=candidate.replace(new,old,1)
ds2,de2,_,_=extract(rollback,"VOCAB_DETAILS_BY_ID")
rollback=rollback[:ds2]+dorig+rollback[de2:]
if rollback!=base: raise RuntimeError("exact rollback failed")
protected={
 "DEFAULT_VOCAB":vocab,"GRAMMAR_DETAILS_BY_ID":grammar,"VOCAB_POS_BY_ID":pos,
 "VOCAB_AUDITED_PAIRS":pairs,"REVIEWED_MEANING_QUIZZES":meaning,
 "REVIEWED_READING_OPTIONS":reading,"VOCAB_KANA_EXAMPLE_TARGETS":kana,
 "REVIEWED_EXAMPLE_TARGETS":targets
}
for name,original in protected.items():
 _,_,after,_=extract(candidate,name)
 if after!=original: raise RuntimeError("protected data changed "+name)
OUT.write_bytes(candidate.encode("utf-8"))
digest=hashlib.sha256(OUT.read_bytes()).hexdigest()
rows=list(csv.DictReader(REGISTER.read_text(encoding="utf-8").splitlines()))
if len(rows)!=5847: raise RuntimeError("register row count mismatch")
base_all={"reviewed":3916,"fixed_rechecked":380,"pending":1551,"total":5847}
base_vocab={"reviewed":3347,"fixed_rechecked":378,"pending":189,"total":3914}
base_pairs={"reviewed":18,"fixed_rechecked":1,"pending":840,"total":859}
target_all={"reviewed":3918,"fixed_rechecked":392,"pending":1537,"total":5847}
target_vocab={"reviewed":3347,"fixed_rechecked":390,"pending":177,"total":3914}
target_pairs={"reviewed":20,"fixed_rechecked":1,"pending":838,"total":859}
keys=[(r["kind"],r["key"]) for r in rows]
if len(keys)!=len(set(keys)): raise RuntimeError("duplicate register keys")
cur=counts(rows); cv=counts(rows,"vocab"); cp=counts(rows,"vocab_pair")
if cur==base_all and cv==base_vocab and cp==base_pairs: state="baseline"
elif cur==target_all and cv==target_vocab and cp==target_pairs: state="already_applied"
else: raise RuntimeError("register is neither exact v213 baseline nor exact v214 target")
bykey={(r["kind"],r["key"]):r for r in rows}
if state=="baseline":
 for cid in FIXED_IDS:
  r=bykey.get(("vocab",str(cid)))
  if not r or r["finalReview"]!="pending" or r["evidence"]: raise RuntimeError("card register preimage mismatch "+str(cid))
  r["finalReview"]="fixed_rechecked"
  r["evidence"]="completion/v214-acceptance.tsv; JLPT_N1_v214_audit.md"
 for key in PAIR_KEYS:
  r=bykey.get(("vocab_pair",key))
  if not r or r["finalReview"]!="pending" or r["evidence"]: raise RuntimeError("pair register preimage mismatch "+key)
  r["finalReview"]="reviewed"
  r["evidence"]="completion/v214-pair-review.tsv; author review, not independent"
 with REGISTER.open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=["kind","key","baselineLocation","finalReview","evidence"],lineterminator="\n")
  w.writeheader(); w.writerows(rows)
else:
 for cid in FIXED_IDS:
  r=bykey[("vocab",str(cid))]
  if r["finalReview"]!="fixed_rechecked" or r["evidence"]!="completion/v214-acceptance.tsv; JLPT_N1_v214_audit.md":
   raise RuntimeError("already-applied card evidence mismatch "+str(cid))
 for key in PAIR_KEYS:
  r=bykey[("vocab_pair",key)]
  if r["finalReview"]!="reviewed" or r["evidence"]!="completion/v214-pair-review.tsv; author review, not independent":
   raise RuntimeError("already-applied pair evidence mismatch "+key)
if counts(rows)!=target_all or counts(rows,"vocab")!=target_vocab or counts(rows,"vocab_pair")!=target_pairs:
 raise RuntimeError("register target mismatch")
prepare={
 "pass":True,"base_version":"v213","base_sha256":base_sha,
 "candidate_version":"v214","candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,
 "vocabulary_records":len(vocab),"grammar_records":len(grammar),"lexical_pairs":len(pairs),
 "unique_vocabulary_ids":len({int(x["id"]) for x in vocab}),
 "review_scope":[int(x) for x in EXPECTED],
 "fixed_rechecked":[int(x) for x in FIXED_IDS],"pending_ids":[],"reviewed_ids":[],
 "updated_fields":len(UPDATES),"changed_cards":[int(x) for x in changed],
 "japanese_example_changes":[],"japanese_definition_changes":[
  {"id":1654,"field":"m"},{"id":1679,"field":"m"},{"id":1688,"field":"m"}
 ],
 "pos_map_unchanged":True,"comparison_pairs_unchanged":True,
 "pair_reviewed_indices":[417,421],
 "author_credit_before":3725,"author_credit_addition":12,"author_credit_after":3737,
 "protected_unchanged":{k:True for k in protected},
 "exact_rollback":True,"register_state":state,"author_review_only":True
}
registry={
 "pass":True,"register_rows":len(rows),
 "before":{"all":base_all,"vocabulary":base_vocab,"vocab_pair":base_pairs},
 "after":{"all":counts(rows),"vocabulary":counts(rows,"vocab"),"vocab_pair":counts(rows,"vocab_pair")},
 "fixed_rechecked_ids":[int(x) for x in FIXED_IDS],"pending_ids":[],
 "reviewed_pair_keys":PAIR_KEYS,"duplicate_keys":0,"records_deleted":0,
 "history_rewritten":False,"idempotent_reuse":state=="already_applied"
}
(WORK/"prepare-results.json").write_text(json.dumps(prepare,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(WORK/"registry-results.json").write_text(json.dumps(registry,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
cp=WORK/"checkpoint.json"
d=json.loads(cp.read_text(encoding="utf-8"))
d["status"]="candidate and registry prepared; Chromium verification pending"
d["candidate_sha256"]=digest; d["candidate_bytes"]=OUT.stat().st_size; d["exact_rollback"]=True
cp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"pass":True,"candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"fixed_rechecked":FIXED_IDS,"pair_reviewed":PAIR_KEYS,"updated_fields":len(UPDATES),"register_after":{"all":counts(rows),"vocabulary":counts(rows,"vocab"),"vocab_pair":counts(rows,"vocab_pair")},"author_credit_after":3737},ensure_ascii=False,indent=2))
