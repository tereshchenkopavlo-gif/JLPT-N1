import csv,hashlib,json,re
from pathlib import Path
BASE=Path("JLPT_N1_ukrainian_reading_v211.html");OUT=Path("JLPT_N1_ukrainian_reading_v212.html")
WORK=Path("completion/v212-work");REGISTER=Path("completion/review-register.csv")
BASE_SHA="c4e10162669b9b0634c9b04b9d1986895ec96d628a02514f2a9a2352989b5f68"
UPDATES=[
 ("1497","m","ある物事に刺激されて、新しい行動や考えを引き起こすこと。","ある物事がきっかけとなって、新しい行動や考えが生まれること。また、そうしたきっかけを与えること。"),
 ("1497","usage","作品に触発される／想像力を触発する: зовнішній вплив спонукає до ідеї чи творчості. Частий пасив に触発される. 刺激 ширше й може бути фізичним або неприємним.","作品に触発される／想像力を触発する: зовнішній вплив спонукає до ідеї чи творчості. Часто вживається пасивна модель に触発される. У спеціалізованому контексті також про стимул, що запускає реакцію. 刺激 ширше й може бути фізичним або неприємним."),
 ("1500","exampleTranslations[1]","Президент компанії дуже йому довіряв і одноосібно доручив вести важливі переговори.","Президент компанії мав до нього велику довіру й повністю доручив йому ведення важливих переговорів."),
 ("1502","exampleTranslations[1]","Після того як військо перетнуло кордон і почало вторгнення, було скликано термінову зустріч.","Після того як військо перетнуло кордон і вторглося на чужу територію, скликали термінову нараду."),
 ("1503","m","他人の土地や建物などに、無断で入り込むこと。","他人の土地や建物、または保護された空間やシステムに、無断で入り込むこと。"),
 ("1505","exampleTranslations[1]","Обговорення законопроєкту затягується, а політичний торг між владою й опозицією триває.","Обговорення законопроєкту затягується, а політичний торг між партіями влади й опозиції триває."),
 ("1507","exampleTranslations[1]","Коли перед відходом із посади президента компанії запитали про його почуття, він висловив вдячність.","Коли президента компанії запитали про його почуття з нагоди відставки, він висловив вдячність."),
 ("1508","usage","心情を察する／心情に配慮する: зважати на внутрішні почуття людини. 心境 — її стан у певний момент; у літературі 作者の心情 — переживання, виражені автором.","心情を察する: здогадуватися про почуття людини; 心情に配慮する: зважати на її почуття. 心境 — стан у певний момент; у літературі 作者の心情 — переживання, виражені автором."),
 ("1508","exampleTranslations[1]","Почуття автора майстерно передано через опис довколишньої картини.","Почуття автора майстерно передано через опис сцени."),
 ("1509","t","відчуття, самопочуття, комфорт","відчуття, самопочуття; у позитивних сполуках — комфорт, зручність"),
 ("1513","t","новітній, той, що набирає сили, новоутворений","новий, що набирає сили або впливу; 新興企業 — компанія, що набирає ваги"),
 ("1513","exampleTranslations[1]","Вихід на ринок нових перспективних компаній ще більше загострює конкуренцію в галузі.","Вихід на ринок нової компанії, що набирає ваги, ще більше загострює конкуренцію в галузі."),
 ("1515","exampleTranslations[0]","Через підвищення відсоткових ставок дедалі більше родин відкладають купівлю новозбудованого житла.","Через підвищення відсоткових ставок дедалі більше родин вирішують поки що не купувати новозбудоване житло."),
 ("1522","t","прямо вгорі, просто над головою","безпосередньо над чимось, прямо над орієнтиром"),
 ("1522","usage","頭の真上／真上を見上げる: безпосередньо над об’єктом. 頭上 стосується простору над головою, не обов’язково строго вертикально. Сонце опівдні не всюди перебуває в зеніті.","机の真上／真上を見上げる: безпосередньо вертикально над орієнтиром. 頭上 може означати простір над головою, не обов’язково строго по вертикалі.")
]
EXPECTED={
 "1497": [
  "触発",
  "しょくはつ",
  [
   "名詞"
  ]
 ],
 "1500": [
  "信任",
  "しんにん",
  [
   "名詞"
  ]
 ],
 "1502": [
  "侵攻",
  "しんこう",
  [
   "名詞"
  ]
 ],
 "1503": [
  "侵入",
  "しんにゅう",
  [
   "名詞"
  ]
 ],
 "1505": [
  "審議",
  "しんぎ",
  [
   "名詞"
  ]
 ],
 "1507": [
  "心境",
  "しんきょう",
  [
   "名詞"
  ]
 ],
 "1508": [
  "心情",
  "しんじょう",
  [
   "名詞"
  ]
 ],
 "1509": [
  "心地",
  "ここち",
  [
   "名詞"
  ]
 ],
 "1513": [
  "新興",
  "しんこう",
  [
   "名詞"
  ]
 ],
 "1515": [
  "新築",
  "しんちく",
  [
   "名詞"
  ]
 ],
 "1522": [
  "真上",
  "まうえ",
  [
   "名詞"
  ]
 ]
}
BASE_EXAMPLES={
 "1497": [
  "彼の講演に触発され、多くの若者が起業を志すようになった。",
  "些細な発言が対立を触発し、事態は思わぬ方向へ進んだ。"
 ],
 "1500": [
  "投票の結果、現会長は会員の信任を得た。",
  "彼は社長から厚く信任され、重要な交渉を一手に任された。"
 ],
 "1502": [
  "他国の領土に侵攻する行為は、国際社会から厳しく非難された。",
  "軍が国境を越えて侵攻したことを受け、緊急の会合が開かれた。"
 ],
 "1503": [
  "不審な男が敷地内に侵入し、警備員に取り押さえられた。",
  "ネットワークへの不正侵入を防ぐため、対策を強化している。"
 ],
 "1505": [
  "予算案は、委員会で慎重に審議された後、本会議に提出される。",
  "法案の審議が長引くなか、与野党の駆け引きが続いている。"
 ],
 "1507": [
  "長年の夢を叶えた彼の心境は、言葉では言い表せないものだろう。",
  "退任にあたり、心境を問われた社長は、感謝の言葉を述べた。"
 ],
 "1508": [
  "被害者の心情を思いやることなく、軽々しく発言するべきではない。",
  "作者の心情が、情景描写をとおして巧みに表現されている。"
 ],
 "1509": [
  "新しいソファは、座り心地がよく、思わず長居してしまう。",
  "生きた心地がしないほど、ひやりとする場面の連続だった。"
 ],
 "1513": [
  "新興国の経済成長が、世界の需要を大きく押し上げている。",
  "新興企業の参入により、業界の競争は一段と激しさを増している。"
 ],
 "1515": [
  "金利の上昇により、新築住宅の購入を見送る家庭が増えている。",
  "市は、老朽化した庁舎を取り壊して新築する計画を発表した。"
 ],
 "1522": [
  "照明が机の真上に取り付けられている。",
  "真上の部屋から物音が聞こえ、住民から苦情が寄せられた。"
 ]
}
PAIR_UPDATE=("Обидва читаються しんこう і пов’язані з розвитком. 振興 — активне сприяння; 新興 — нове піднесення або новий впливовий учасник. Моделі: 産業を振興する; 新興企業. 観光を振興する。— Розвивати туризм. 新興企業が参入した。— На ринок вийшла нова перспективна компанія. 新興 не підставляють у модель 産業を振興する: це не назва тієї самої дії.","Обидва читаються しんこう і пов’язані з розвитком. 振興 — активне сприяння; 新興 — нове піднесення або новий впливовий учасник. Моделі: 産業を振興する; 新興企業. 観光を振興する。— Розвивати туризм. 新興企業が参入した。— На ринок вийшла нова компанія, що набирає ваги. 新興 не підставляють у модель 産業を振興する: це не назва тієї самої дії.")
FIXED_IDS=list(EXPECTED)
PAIR_ID=395;PAIR_KEY="395:1512:1513"
def extract(source,name):
 m=re.search(r"\bconst "+re.escape(name)+r"\s*=\s*",source)
 if not m:raise RuntimeError("missing constant "+name)
 start=m.end();opening=source[start];closing="]" if opening=="[" else "}"
 depth=0;inside=False;escaped=False
 for i in range(start,len(source)):
  c=source[i]
  if inside:
   if escaped:escaped=False
   elif c=="\\":escaped=True
   elif c=='"':inside=False
  else:
   if c=='"':inside=True
   elif c==opening:depth+=1
   elif c==closing:
    depth-=1
    if depth==0:return start,i+1,json.loads(source[start:i+1]),source[start:i+1]
 raise RuntimeError("unterminated constant "+name)
def counts(rows,kind=None):
 sel=[r for r in rows if kind is None or r["kind"]==kind]
 out={s:sum(r["finalReview"]==s for r in sel) for s in ("reviewed","fixed_rechecked","pending")};out["total"]=len(sel);return out
WORK.mkdir(parents=True,exist_ok=True)
raw=BASE.read_bytes();base_sha=hashlib.sha256(raw).hexdigest()
if base_sha!=BASE_SHA:raise RuntimeError("unexpected v211 base SHA-256: "+base_sha)
base=raw.decode("utf-8")
ds,de,details,details_original=extract(base,"VOCAB_DETAILS_BY_ID");ps,pe,pairs,pairs_original=extract(base,"VOCAB_AUDITED_PAIRS")
_,_,vocab,_=extract(base,"DEFAULT_VOCAB");_,_,grammar,_=extract(base,"GRAMMAR_DETAILS_BY_ID")
_,_,pos,_=extract(base,"VOCAB_POS_BY_ID");_,_,meaning,_=extract(base,"REVIEWED_MEANING_QUIZZES")
_,_,reading,_=extract(base,"REVIEWED_READING_OPTIONS");_,_,kana,_=extract(base,"VOCAB_KANA_EXAMPLE_TARGETS")
_,_,targets,_=extract(base,"REVIEWED_EXAMPLE_TARGETS")
if (len(vocab),len(grammar),len(details),len(pairs))!=(3914,130,3914,859):raise RuntimeError("protected inventory counts mismatch")
by_id={str(x["id"]):x for x in vocab}
for cid,(word,rd,p) in EXPECTED.items():
 if cid not in by_id or (by_id[cid]["w"],by_id[cid]["r"],pos[cid])!=(word,rd,p):raise RuntimeError("identity/POS mismatch "+cid)
 if details[cid]["examples"]!=BASE_EXAMPLES[cid]:raise RuntimeError("Japanese example preimage mismatch "+cid)
before=json.loads(json.dumps(details,ensure_ascii=False))
for cid,field,old,new in UPDATES:
 if "[" in field:
  key=field.split("[")[0];i=int(re.search(r"\[(\d+)\]",field).group(1))
  if details[cid][key][i]!=old:raise RuntimeError("preimage mismatch "+cid+"."+field)
  details[cid][key][i]=new
 else:
  if details[cid][field]!=old:raise RuntimeError("preimage mismatch "+cid+"."+field)
  details[cid][field]=new
changed=sorted((cid for cid in details if details[cid]!=before[cid]),key=int)
if changed!=sorted(FIXED_IDS,key=int):raise RuntimeError("changed-card set mismatch "+str(changed))
allowed={"1497":{"m","usage"},"1500":{"exampleTranslations"},"1502":{"exampleTranslations"},"1503":{"m"},"1505":{"exampleTranslations"},"1507":{"exampleTranslations"},"1508":{"usage","exampleTranslations"},"1509":{"t"},"1513":{"t","exampleTranslations"},"1515":{"exampleTranslations"},"1522":{"t","usage"}}
for cid in details:
 for field in before[cid]:
  if before[cid][field]!=details[cid][field] and field not in allowed.get(cid,set()):raise RuntimeError("unexpected field mutation "+cid+"."+field)
pair_before=json.loads(json.dumps(pairs,ensure_ascii=False))
if str(pairs[PAIR_ID]["a"])!="1512" or str(pairs[PAIR_ID]["b"])!="1513" or pairs[PAIR_ID]["type"]!="confusable":raise RuntimeError("pair identity mismatch")
if pairs[PAIR_ID]["note"]!=PAIR_UPDATE[0]:raise RuntimeError("pair note preimage mismatch")
pairs[PAIR_ID]["note"]=PAIR_UPDATE[1]
for i,(oldp,newp) in enumerate(zip(pair_before,pairs)):
 if i==PAIR_ID:
  if oldp["note"]==newp["note"] or any(oldp[k]!=newp[k] for k in oldp if k!="note"):raise RuntimeError("unexpected pair mutation")
 elif oldp!=newp:raise RuntimeError("unexpected pair changed "+str(i))
details_literal=json.dumps(details,ensure_ascii=False,separators=(",",":"))
pairs_literal=json.dumps(pairs,ensure_ascii=False,separators=(",",":"))
repls=[(ds,de,details_literal),(ps,pe,pairs_literal)]
candidate=base
for start,end,literal in sorted(repls,reverse=True):candidate=candidate[:start]+literal+candidate[end:]
old="<title>JLPT N1 — ウクライナ語対応学習アプリ · v211</title>";new="<title>JLPT N1 — ウクライナ語対応学習アプリ · v212</title>"
if candidate.count(old)!=1:raise RuntimeError("version title marker mismatch")
candidate=candidate.replace(old,new,1)
rollback=candidate.replace(new,old,1)
_,_,_,dorig=extract(base,"VOCAB_DETAILS_BY_ID");_,_,_,porig=extract(base,"VOCAB_AUDITED_PAIRS")
ds2,de2,_,_=extract(rollback,"VOCAB_DETAILS_BY_ID");ps2,pe2,_,_=extract(rollback,"VOCAB_AUDITED_PAIRS")
for start,end,literal in sorted([(ds2,de2,dorig),(ps2,pe2,porig)],reverse=True):rollback=rollback[:start]+literal+rollback[end:]
if rollback!=base:raise RuntimeError("exact rollback failed")
protected={"DEFAULT_VOCAB":vocab,"GRAMMAR_DETAILS_BY_ID":grammar,"VOCAB_POS_BY_ID":pos,"REVIEWED_MEANING_QUIZZES":meaning,"REVIEWED_READING_OPTIONS":reading,"VOCAB_KANA_EXAMPLE_TARGETS":kana,"REVIEWED_EXAMPLE_TARGETS":targets}
for name,original in protected.items():
 _,_,after,_=extract(candidate,name)
 if after!=original:raise RuntimeError("protected data changed "+name)
_,_,afterpairs,_=extract(candidate,"VOCAB_AUDITED_PAIRS")
if len(afterpairs)!=859 or afterpairs[PAIR_ID]["note"]!=PAIR_UPDATE[1]:raise RuntimeError("pair update verification failed")
for i,p in enumerate(afterpairs):
 if i!=PAIR_ID and p!=pair_before[i]:raise RuntimeError("other pair changed "+str(i))
OUT.write_bytes(candidate.encode("utf-8"));digest=hashlib.sha256(OUT.read_bytes()).hexdigest()
rows=list(csv.DictReader(REGISTER.read_text(encoding="utf-8").splitlines()))
if len(rows)!=5847:raise RuntimeError("register row count mismatch")
base_all={"reviewed":3916,"fixed_rechecked":357,"pending":1574,"total":5847}
base_vocab={"reviewed":3347,"fixed_rechecked":356,"pending":211,"total":3914}
base_pairs={"reviewed":18,"fixed_rechecked":0,"pending":841,"total":859}
target_all={"reviewed":3916,"fixed_rechecked":369,"pending":1562,"total":5847}
target_vocab={"reviewed":3347,"fixed_rechecked":367,"pending":200,"total":3914}
target_pairs={"reviewed":18,"fixed_rechecked":1,"pending":840,"total":859}
if counts(rows)!=base_all or counts(rows,"vocab")!=base_vocab or counts(rows,"vocab_pair")!=base_pairs:raise RuntimeError("register baseline mismatch")
keys=[(r["kind"],r["key"]) for r in rows]
if len(keys)!=len(set(keys)):raise RuntimeError("duplicate register keys")
bykey={}
for r in rows:
 if r["kind"]=="vocab" and r["key"] in FIXED_IDS:bykey.setdefault(r["key"],[]).append(r)
if any(len(bykey.get(cid,[]))!=1 for cid in FIXED_IDS):raise RuntimeError("vocabulary register scope missing/duplicate")
for cid in FIXED_IDS:
 r=bykey[cid][0]
 if r["finalReview"]!="pending" or r["evidence"]:raise RuntimeError("vocabulary register preimage mismatch "+cid)
 r["finalReview"]="fixed_rechecked";r["evidence"]="completion/v212-acceptance.tsv; JLPT_N1_v212_audit.md"
pairrows=[r for r in rows if r["kind"]=="vocab_pair" and r["key"]==PAIR_KEY]
if len(pairrows)!=1 or pairrows[0]["finalReview"]!="pending" or pairrows[0]["evidence"]:raise RuntimeError("pair register preimage mismatch")
pairrows[0]["finalReview"]="fixed_rechecked";pairrows[0]["evidence"]="completion/v212-pair-review.tsv; JLPT_N1_v212_audit.md"
with REGISTER.open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=["kind","key","baselineLocation","finalReview","evidence"],lineterminator="\n");w.writeheader();w.writerows(rows)
if counts(rows)!=target_all or counts(rows,"vocab")!=target_vocab or counts(rows,"vocab_pair")!=target_pairs:raise RuntimeError("register target mismatch")
prepare={"pass":True,"base_version":"v211","base_sha256":base_sha,"candidate_version":"v212","candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"vocabulary_records":len(vocab),"grammar_records":len(grammar),"lexical_pairs":len(pairs),"unique_vocabulary_ids":len({int(x["id"]) for x in vocab}),"review_scope":[int(x) for x in FIXED_IDS],"fixed_rechecked":[int(x) for x in FIXED_IDS],"reviewed_without_change":[],"deferred_count":1,"updated_fields":len(UPDATES),"changed_cards":[int(x) for x in changed],"pair_updates":[{"index":PAIR_ID,"a":1512,"b":1513,"field":"note","before":PAIR_UPDATE[0],"after":PAIR_UPDATE[1]}],"changed_pairs":[PAIR_ID],"japanese_example_changes":[],"japanese_definition_changes":[{"id":1497,"field":"m"},{"id":1503,"field":"m"}],"author_credit_before":3703,"author_credit_addition":11,"author_credit_after":3714,"protected_unchanged":{k:True for k in protected},"all_other_pairs_unchanged":True,"exact_rollback":True,"register_updated":True,"author_review_only":True}
registry={"pass":True,"register_rows":len(rows),"before":{"all":base_all,"vocabulary":base_vocab,"vocab_pair":base_pairs},"after":{"all":counts(rows),"vocabulary":counts(rows,"vocab"),"vocab_pair":counts(rows,"vocab_pair")},"fixed_rechecked_ids":[int(x) for x in FIXED_IDS],"pair_fixed_rechecked_ids":[PAIR_ID],"reviewed_ids":[],"deferred_count":1,"author_credit_before":3703,"author_credit_after":3714,"duplicate_keys":0,"records_deleted":0,"history_rewritten":False}
(WORK/"prepare-results.json").write_text(json.dumps(prepare,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(WORK/"registry-results.json").write_text(json.dumps(registry,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
cp=WORK/"checkpoint.json";d=json.loads(cp.read_text(encoding="utf-8"));d["status"]="author review complete; deterministic candidate and registry prepared; Chromium verification pending";d["candidate_sha256"]=digest;d["candidate_bytes"]=OUT.stat().st_size;d["exact_rollback"]=True;cp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"pass":True,"candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"fixed_rechecked":FIXED_IDS,"pair_fixed_rechecked":[PAIR_ID],"deferred_count":1,"updated_fields":len(UPDATES),"register_after":{"all":counts(rows),"vocabulary":counts(rows,"vocab"),"vocab_pair":counts(rows,"vocab_pair")}},ensure_ascii=False,indent=2))
