import csv,hashlib,json,re
from pathlib import Path
BASE=Path("JLPT_N1_ukrainian_reading_v212.html");OUT=Path("JLPT_N1_ukrainian_reading_v213.html")
WORK=Path("completion/v213-work");REGISTER=Path("completion/review-register.csv")
BASE_SHA="a0dd07bc265bb549b648ec3dcc02fa836f5ee59449a92cbdcc53c682bdc28bb5"
UPDATES=[
 ("1528","t","дружба, добра воля, дружні стосунки","дружні відносини, взаємна приязнь"),
 ("1529","exampleTranslations[0]","У цій клініці терапевтичних пацієнтів оглядають і лікують навіть без попереднього запису.","У цій клініці пацієнтів терапевтичного профілю оглядають і лікують навіть без попереднього запису."),
 ("1529","exampleTranslations[1]","Забезпечення лікарями малолюдних районів стало нагальним завданням.","Нагальним завданням стало забезпечити лікарів, які надаватимуть медичну допомогу в малолюдних районах."),
 ("1539","exampleTranslations[0]","Його щирий характер приваблює багатьох людей, які хочуть із ним співпрацювати.","Багато хто, приваблений його порядністю, хоче мати з ним ділові стосунки."),
 ("1541","usage","図星だ／図星を突かれる: точно вгадати приховану думку чи влучити в болючу правду. Часто реакція на зауваження. Не універсальне слово для будь-якої мішені або будь-якої істини.","図星だ／図星を突かれる: зауваження влучне або точно влучає в болюче місце чи приховану думку. Реакція залежить від контексту; не кожне влучання в ціль є 図星."),
 ("1541","exampleTranslations[1]","Йому влучили в болючу правду, і він відвів погляд, ніби приховуючи хвилювання.","Коли йому влучно вказали на болюче місце, він відвів погляд, намагаючись приховати хвилювання."),
 ("1542","m","強い風とともに雪が激しく降ること。","強い風とともに雪が激しく降ること。また、風が積もった雪を巻き上げて吹き荒れること。"),
 ("1548","exampleTranslations[0]","Якщо перед смаженням добре дати воді стекти з овочів, готова страва не буде липкою й водянистою.","Якщо перед смаженням добре дати воді стекти з овочів, готова страва не буде липкою."),
 ("1551","m","勢いが衰えて、おとろえていくこと。","勢いが弱まり、力や活気を失っていくこと。"),
 ("1554","m","社会の人々に共通する、公の意見。","社会の人々の間に形成される、公共の問題についての意見や見方。"),
 ("1558","t","ухвалення й запровадження нового закону, правила або системи норм","ухвалення, установлення нового закону, правила або системи норм"),
 ("1625","exampleTranslations[0]","Поліція веде розслідування, вважаючи ймовірною причетність організованої групи.","Поліція продовжує розслідування, оскільки підозрює, що причетність до справи мала організований характер."),
 ("1628","exampleTranslations[1]","Через несанкціоновані дії система автоматично зупинилася.","Через неправомірні маніпуляції система автоматично зупинилася.")
]
EXPECTED={
 "1528": [
  "親善",
  "しんぜん",
  [
   "名詞"
  ]
 ],
 "1529": [
  "診療",
  "しんりょう",
  [
   "名詞"
  ]
 ],
 "1539": [
  "人柄",
  "ひとがら",
  [
   "名詞"
  ]
 ],
 "1541": [
  "図星",
  "ずぼし",
  [
   "名詞"
  ]
 ],
 "1542": [
  "吹雪",
  "ふぶき",
  [
   "名詞"
  ]
 ],
 "1548": [
  "水気",
  "みずけ",
  [
   "名詞"
  ]
 ],
 "1551": [
  "衰退",
  "すいたい",
  [
   "名詞"
  ]
 ],
 "1554": [
  "世論",
  "よろん／せろん",
  [
   "名詞"
  ]
 ],
 "1558": [
  "制定",
  "せいてい",
  [
   "名詞"
  ]
 ],
 "1625": [
  "捜査",
  "そうさ",
  [
   "名詞"
  ]
 ],
 "1628": [
  "操作",
  "そうさ",
  [
   "名詞"
  ]
 ],
 "1631": [
  "相応",
  "そうおう",
  [
   "名詞"
  ]
 ]
}
BASE_EXAMPLES={
 "1528": [
  "両国の親善を深めるため、文化交流のイベントが開催された。",
  "親善試合では、勝敗よりも相互理解を重視する姿勢が示された。"
 ],
 "1529": [
  "この医院では、予約なしでも内科の患者を診療している。",
  "過疎地での診療を担う医師の確保が、喫緊の課題となっている。"
 ],
 "1539": [
  "彼の誠実な人柄に惹かれ、多くの人が取引を希望している。",
  "面接では、経歴だけでなく、応募者の人柄も重視される。"
 ],
 "1541": [
  "上司の指摘が図星だっただけに、彼は何も言い返せなかった。",
  "図星を突かれた彼は、動揺を隠すように視線をそらした。"
 ],
 "1542": [
  "猛烈な吹雪のため、山間部の道路は通行止めとなった。",
  "登山者たちは、吹雪の中、山小屋にたどり着いて難を逃れた。"
 ],
 "1548": [
  "野菜の水気をよく切ってから、炒めると、仕上がりがべたつかない。",
  "洗濯物の水気が残っていると、雑菌が繁殖しやすくなる。"
 ],
 "1551": [
  "地方の商店街は、後継者不足により、徐々に衰退している。",
  "技術革新に乗り遅れた企業は、市場での競争力を失い衰退した。"
 ],
 "1554": [
  "政府の対応に対する世論は、時間の経過とともに厳しさを増している。",
  "世論の動向を無視して、政策を進めることはできない。"
 ],
 "1558": [
  "地域の実情に合わせた独自の条例を制定する自治体が、増えつつある。",
  "会社は、新たな行動規範を制定し、全社員に周知した。"
 ],
 "1625": [
  "警察は、組織的な関与があった疑いが強いとみて捜査を進めている。",
  "事件の全容を解明するため、合同捜査本部が設置された。"
 ],
 "1628": [
  "この機器は、誰でも簡単に操作できるよう設計されている。",
  "不正な操作が行われたため、システムは自動的に停止した。"
 ],
 "1631": [
  "責任ある立場には、それに相応する覚悟と行動が求められる。",
  "収入に相応した生活を送ることが、家計を守る基本である。"
 ]
}
FIXED_IDS=[1528,1529,1539,1541,1542,1548,1551,1554,1558,1625,1628]
DEFERRED_ID=1631
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
if base_sha!=BASE_SHA:raise RuntimeError("unexpected v212 base SHA-256: "+base_sha)
base=raw.decode("utf-8")
ds,de,details,dorig=extract(base,"VOCAB_DETAILS_BY_ID");ps,pe,pos,posorig=extract(base,"VOCAB_POS_BY_ID")
_,_,vocab,_=extract(base,"DEFAULT_VOCAB");_,_,grammar,_=extract(base,"GRAMMAR_DETAILS_BY_ID")
_,_,pairs,_=extract(base,"VOCAB_AUDITED_PAIRS");_,_,meaning,_=extract(base,"REVIEWED_MEANING_QUIZZES")
_,_,reading,_=extract(base,"REVIEWED_READING_OPTIONS");_,_,kana,_=extract(base,"VOCAB_KANA_EXAMPLE_TARGETS")
_,_,targets,_=extract(base,"REVIEWED_EXAMPLE_TARGETS")
if (len(vocab),len(grammar),len(details),len(pairs))!=(3914,130,3914,859):raise RuntimeError("protected inventory counts mismatch")
by_id={str(x["id"]):x for x in vocab}
for cid,(word,rd,p) in EXPECTED.items():
 if cid not in by_id or (by_id[cid]["w"],by_id[cid]["r"],pos[cid])!=(word,rd,p):raise RuntimeError("identity/POS preimage mismatch "+cid)
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
if changed!=sorted(map(str,FIXED_IDS),key=int):raise RuntimeError("changed-card set mismatch "+str(changed))
allowed={"1528":{"t"},"1529":{"exampleTranslations"},"1539":{"exampleTranslations"},"1541":{"usage","exampleTranslations"},"1542":{"m"},"1548":{"exampleTranslations"},"1551":{"m"},"1554":{"m"},"1558":{"t"},"1625":{"exampleTranslations"},"1628":{"exampleTranslations"}}
for cid in details:
 for field in before[cid]:
  if before[cid][field]!=details[cid][field] and field not in allowed.get(cid,set()):raise RuntimeError("unexpected field mutation "+cid+"."+field)
if pos[str(DEFERRED_ID)]!=["名詞"]:raise RuntimeError("deferred POS changed")
details_literal=json.dumps(details,ensure_ascii=False,separators=(",",":"))
candidate=base[:ds]+details_literal+base[de:]
old="<title>JLPT N1 — ウクライナ語対応学習アプリ · v212</title>";new="<title>JLPT N1 — ウクライナ語対応学習アプリ · v213</title>"
if candidate.count(old)!=1:raise RuntimeError("version title marker mismatch")
candidate=candidate.replace(old,new,1)
rollback=candidate.replace(new,old,1)
ds2,de2,_,_=extract(rollback,"VOCAB_DETAILS_BY_ID")
rollback=rollback[:ds2]+dorig+rollback[de2:]
if rollback!=base:raise RuntimeError("exact rollback failed")
protected={"DEFAULT_VOCAB":vocab,"GRAMMAR_DETAILS_BY_ID":grammar,"VOCAB_POS_BY_ID":pos,"VOCAB_AUDITED_PAIRS":pairs,"REVIEWED_MEANING_QUIZZES":meaning,"REVIEWED_READING_OPTIONS":reading,"VOCAB_KANA_EXAMPLE_TARGETS":kana,"REVIEWED_EXAMPLE_TARGETS":targets}
for name,original in protected.items():
 _,_,after,_=extract(candidate,name)
 if after!=original:raise RuntimeError("protected data changed "+name)
OUT.write_bytes(candidate.encode("utf-8"));digest=hashlib.sha256(OUT.read_bytes()).hexdigest()
rows=list(csv.DictReader(REGISTER.read_text(encoding="utf-8").splitlines()))
if len(rows)!=5847:raise RuntimeError("register row count mismatch")
base_all={"reviewed":3916,"fixed_rechecked":369,"pending":1562,"total":5847}
base_vocab={"reviewed":3347,"fixed_rechecked":367,"pending":200,"total":3914}
base_pairs={"reviewed":18,"fixed_rechecked":1,"pending":840,"total":859}
target_all={"reviewed":3916,"fixed_rechecked":380,"pending":1551,"total":5847}
target_vocab={"reviewed":3347,"fixed_rechecked":378,"pending":189,"total":3914}
target_pairs=base_pairs
cur=counts(rows);cv=counts(rows,"vocab");cp=counts(rows,"vocab_pair")
if cur==base_all and cv==base_vocab and cp==base_pairs:state="baseline"
elif cur==target_all and cv==target_vocab and cp==target_pairs:state="already_applied"
else:raise RuntimeError("register is neither exact v212 baseline nor exact v213 target")
keys=[(r["kind"],r["key"]) for r in rows]
if len(keys)!=len(set(keys)):raise RuntimeError("duplicate register keys")
bykey={}
for r in rows:
 if r["kind"]=="vocab" and r["key"] in list(map(str,FIXED_IDS)):bykey.setdefault(r["key"],[]).append(r)
if any(len(bykey.get(str(cid),[]))!=1 for cid in FIXED_IDS):raise RuntimeError("register scope missing/duplicate")
pending=[r for r in rows if r["kind"]=="vocab" and r["key"]==str(DEFERRED_ID)]
if len(pending)!=1 or pending[0]["finalReview"]!="pending":raise RuntimeError("deferred record must remain pending")
if state=="baseline":
 for cid in FIXED_IDS:
  r=bykey[str(cid)][0]
  if r["finalReview"]!="pending" or r["evidence"]:raise RuntimeError("register preimage mismatch "+str(cid))
  r["finalReview"]="fixed_rechecked";r["evidence"]="completion/v213-acceptance.tsv; JLPT_N1_v213_audit.md"
 with REGISTER.open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=["kind","key","baselineLocation","finalReview","evidence"],lineterminator="\n");w.writeheader();w.writerows(rows)
else:
 for cid in FIXED_IDS:
  r=bykey[str(cid)][0]
  if r["finalReview"]!="fixed_rechecked" or r["evidence"]!="completion/v213-acceptance.tsv; JLPT_N1_v213_audit.md":raise RuntimeError("already-applied evidence mismatch "+str(cid))
if counts(rows)!=target_all or counts(rows,"vocab")!=target_vocab or counts(rows,"vocab_pair")!=target_pairs:raise RuntimeError("register target mismatch")
prepare={"pass":True,"base_version":"v212","base_sha256":base_sha,"candidate_version":"v213","candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"vocabulary_records":len(vocab),"grammar_records":len(grammar),"lexical_pairs":len(pairs),"unique_vocabulary_ids":len({int(x["id"]) for x in vocab}),"review_scope":[int(x) for x in EXPECTED],"fixed_rechecked":[int(x) for x in FIXED_IDS],"pending_ids":[DEFERRED_ID],"updated_fields":len(UPDATES),"changed_cards":[int(x) for x in changed],"japanese_example_changes":[],"japanese_definition_changes":[{"id":1542,"field":"m"},{"id":1551,"field":"m"},{"id":1554,"field":"m"}],"pos_map_unchanged":True,"pos_change_deferred":{"id":DEFERRED_ID,"current":["名詞"],"proposed":["名詞","ナ形"],"reading_candidates_before":60,"reading_candidates_after":2,"cloze_candidates_before":2269,"cloze_candidates_after":65},"author_credit_before":3714,"author_credit_addition":11,"author_credit_after":3725,"protected_unchanged":{k:True for k in protected},"exact_rollback":True,"register_state":state,"author_review_only":True}
registry={"pass":True,"register_rows":len(rows),"before":{"all":base_all,"vocabulary":base_vocab,"vocab_pair":base_pairs},"after":{"all":counts(rows),"vocabulary":counts(rows,"vocab"),"vocab_pair":counts(rows,"vocab_pair")},"fixed_rechecked_ids":[int(x) for x in FIXED_IDS],"pending_ids":[DEFERRED_ID],"reviewed_ids":[],"author_credit_before":3714,"author_credit_after":3725,"duplicate_keys":0,"records_deleted":0,"history_rewritten":False,"idempotent_reuse":state=="already_applied"}
(WORK/"prepare-results.json").write_text(json.dumps(prepare,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(WORK/"registry-results.json").write_text(json.dumps(registry,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(WORK/"pos-diagnostic.json").write_text(json.dumps(prepare["pos_change_deferred"],ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
cp=WORK/"checkpoint.json";d=json.loads(cp.read_text(encoding="utf-8"));d["status"]="author review complete; deterministic candidate and registry prepared; Chromium verification pending";d["candidate_sha256"]=digest;d["candidate_bytes"]=OUT.stat().st_size;d["exact_rollback"]=True;cp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"pass":True,"candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"fixed_rechecked":FIXED_IDS,"pending_ids":[DEFERRED_ID],"updated_fields":len(UPDATES),"register_after":{"all":counts(rows),"vocabulary":counts(rows,"vocab")},"pos_change_deferred":prepare["pos_change_deferred"]},ensure_ascii=False,indent=2))
