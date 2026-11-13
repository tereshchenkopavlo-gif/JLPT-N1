import csv,hashlib,json,re
from pathlib import Path
BASE=Path("JLPT_N1_ukrainian_reading_v202.html")
OUT=Path("JLPT_N1_ukrainian_reading_v203.html")
WORK=Path("completion/v203-work")
REGISTER=Path("completion/review-register.csv")
BASE_SHA="39aa398f92db161d4c396038d588872b2fabb9fc9c45713a5e530f5a03bae14c"
UPDATES=[
 ("1153","exampleTranslations[1]","У регіоні з нестачею ресурсів життя людей зазнає значного тиску.","Нестача ресурсів суттєво ускладнює життя людей."),
 ("1157","t","зрив переговорів або розрив узгодження позицій, коли сторони не доходять згоди","зрив переговорів; розходження сторін без досягнення згоди"),
 ("1158","exampleTranslations[1]","У місці спільного проживання виявили туберкульоз, і орган охорони здоров’я провів обстеження.","У місці спільного проживання виявили випадок туберкульозу, після чого орган охорони здоров’я провів обстеження."),
 ("1169","t","поєднання двох або більше професій чи видів діяльності; 兼業する — працювати за сумісництвом","поєднання основної роботи з іншою професійною діяльністю; 兼業する — поєднувати основну професію з іншою діяльністю"),
 ("1173","exampleTranslations[0]","Розмежування проголошених позицій і справжніх почуттів ускладнює стосунки в організації.","Необхідність залежно від обставин по-різному висловлювати офіційну позицію та справжні почуття ускладнює стосунки в організації."),
 ("1173","exampleTranslations[1]","За принципом, покладеним в основу правил, визнати виняток неможливо.","Згідно з формальними положеннями правил, допустити виняток неможливо."),
 ("1175","exampleTranslations[0]","У матеріалах, оприлюднених поліцією, зазначено кількість розкритих справ.","У матеріалах, оприлюднених поліцією, зазначено кількість справ, у яких поліція ідентифікувала підозрюваних."),
 ("1175","exampleTranslations[1]","Кількість осіб, щодо яких проведено відповідні слідчі дії, значно зросла порівняно з минулим роком.","Кількість осіб, яких поліція ідентифікувала як підозрюваних, значно зросла порівняно з минулим роком."),
 ("1178","examples[0]","検事は、法廷で被告の責任を厳しく追及した。","検事は、法廷で被告人の責任を厳しく追及した。"),
 ("1178","exampleTranslations[1]","Склавши кваліфікаційний іспит із права, він обрав професію прокурора.","Після складання японського кваліфікаційного іспиту для юридичних професій він обрав кар’єру прокурора."),
 ("1182","exampleTranslations[1]","Вечірнє меню в традиційному готелі було побудоване переважно на сезонних місцевих стравах.","Вечірнє меню в традиційному готелі переважно складалося з місцевих сезонних продуктів."),
 ("1194","exampleTranslations[1]","Вона й досі береже уявні образи, які плекала в дитинстві.","Вона й досі береже мрії, які виникли в неї ще в дівоцтві."),
 ("1195","exampleTranslations[0]","За помилки або пропущені знаки у відповіді можуть зняти бали.","За неправильно написані або пропущені знаки у відповіді можуть зняти бали."),
 ("1196","exampleTranslations[1]","Часто кажуть, що джерело конкурентоспроможності компанії — її люди.","Часто кажуть, що джерело конкурентоспроможності компанії — її кадри.")
]
EXPECTED={
 "1153":("欠乏","けつぼう",["名詞"]),
 "1157":("決裂","けつれつ",["名詞"]),
 "1158":("結核","けっかく",["名詞"]),
 "1169":("兼業","けんぎょう",["名詞"]),
 "1173":("建前","たてまえ",["名詞"]),
 "1175":("検挙","けんきょ",["名詞"]),
 "1178":("検事","けんじ",["名詞"]),
 "1182":("献立","こんだて",["名詞"]),
 "1194":("幻想","げんそう",["名詞"]),
 "1195":("減点","げんてん",["名詞"]),
 "1196":("源泉","げんせん",["名詞"])
}
BASE_EXAMPLES={
 "1153":["ビタミンが欠乏すると、さまざまな健康障害を引き起こすことがある。","資源が欠乏した地域では、人々の暮らしが大きく圧迫されている。"],
 "1157":["労使の交渉は、賃金の引き上げ幅をめぐって決裂した。","両国の会談が決裂し、関係の悪化が懸念されている。"],
 "1158":["授業で、結核という病気の歴史を学んだ。","集団生活の場で結核が見つかり、保健所が検査を実施した。"],
 "1169":["彼は会社勤めと農業を兼業している。","兼業農家が、人手不足の地域の農業を長年支えている。"],
 "1173":["建前と本音の使い分けが、組織の人間関係を複雑にしている。","規則の建前上、例外を認めるわけにはいかない。"],
 "1175":["警察が公表した資料には、事件の検挙件数が記されている。","検挙された人数は、昨年に比べて大きく増加している。"],
 "1178":["検事は、法廷で被告の責任を厳しく追及した。","彼は司法試験に合格したのち、検事の道を選んだ。"],
 "1182":["栄養士は、季節の食材を生かした献立を毎日考えている。","旅館の夕食の献立は、地元の旬の味を中心に構成されていた。"],
 "1194":["理想ばかりを追い求める彼の計画は、幻想に過ぎないと批判された。","彼女は、少女のころに抱いた幻想を、いまも大切にしている。"],
 "1195":["答案に誤字や脱字があると、減点されることがある。","違反を犯した選手は、審判の判断で減点された。"],
 "1196":["この温泉の源泉は、山のふもとにある。","企業の競争力の源泉は、人材にあるとよくいわれる。"]
}
AFTER_EXAMPLES={k:list(v) for k,v in BASE_EXAMPLES.items()}
AFTER_EXAMPLES["1178"][0]="検事は、法廷で被告人の責任を厳しく追及した。"
FIXED_IDS=["1153","1157","1158","1169","1173","1175","1178","1182","1194","1195","1196"]
EXPECTED_CHANGED=FIXED_IDS
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
    if depth==0:return start,i+1,json.loads(source[start:i+1])
 raise RuntimeError("unterminated constant "+name)
def counts(rows,kind=None):
 sel=[r for r in rows if kind is None or r["kind"]==kind]
 out={s:sum(r["finalReview"]==s for r in sel) for s in ("reviewed","fixed_rechecked","pending")};out["total"]=len(sel);return out
WORK.mkdir(parents=True,exist_ok=True)
raw=BASE.read_bytes();base_sha=hashlib.sha256(raw).hexdigest()
if base_sha!=BASE_SHA:raise RuntimeError("unexpected v202 base SHA-256: "+base_sha)
base=raw.decode("utf-8")
_,_,vocab=extract(base,"DEFAULT_VOCAB")
_,_,grammar=extract(base,"GRAMMAR_DETAILS_BY_ID")
ds,de,details=extract(base,"VOCAB_DETAILS_BY_ID")
_,_,pos=extract(base,"VOCAB_POS_BY_ID")
_,_,pairs=extract(base,"VOCAB_AUDITED_PAIRS")
_,_,meaning=extract(base,"REVIEWED_MEANING_QUIZZES")
_,_,reading=extract(base,"REVIEWED_READING_OPTIONS")
_,_,kana=extract(base,"VOCAB_KANA_EXAMPLE_TARGETS")
_,_,targets=extract(base,"REVIEWED_EXAMPLE_TARGETS")
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
if changed!=EXPECTED_CHANGED:raise RuntimeError("changed-card set mismatch "+str(changed))
allowed={"1153":{"exampleTranslations"},"1157":{"t"},"1158":{"exampleTranslations"},"1169":{"t"},"1173":{"exampleTranslations"},"1175":{"exampleTranslations"},"1178":{"examples","exampleTranslations"},"1182":{"exampleTranslations"},"1194":{"exampleTranslations"},"1195":{"exampleTranslations"},"1196":{"exampleTranslations"}}
for cid in details:
 for field in before[cid]:
  if before[cid][field]!=details[cid][field] and field not in allowed.get(cid,set()):raise RuntimeError("unexpected field mutation "+cid+"."+field)
 if details[cid]["examples"]!=AFTER_EXAMPLES.get(cid,details[cid]["examples"]):raise RuntimeError("Japanese example postimage mismatch "+cid)
 if cid!="1178" and before[cid]["examples"]!=details[cid]["examples"]:raise RuntimeError("unexpected Japanese example change "+cid)
literal=json.dumps(details,ensure_ascii=False,separators=(",",":"))
candidate=base[:ds]+literal+base[de:]
old="<title>JLPT N1 — ウクライナ語対応学習アプリ · v202</title>";new="<title>JLPT N1 — ウクライナ語対応学習アプリ · v203</title>"
if candidate.count(old)!=1:raise RuntimeError("version title marker mismatch")
candidate=candidate.replace(old,new,1)
if candidate.replace(new,old,1).replace(literal,base[ds:de],1)!=base:raise RuntimeError("exact rollback failed")
protected={"DEFAULT_VOCAB":vocab,"GRAMMAR_DETAILS_BY_ID":grammar,"VOCAB_POS_BY_ID":pos,"VOCAB_AUDITED_PAIRS":pairs,"REVIEWED_MEANING_QUIZZES":meaning,"REVIEWED_READING_OPTIONS":reading,"VOCAB_KANA_EXAMPLE_TARGETS":kana,"REVIEWED_EXAMPLE_TARGETS":targets}
for name,original in protected.items():
 _,_,after=extract(candidate,name)
 if after!=original:raise RuntimeError("protected data changed "+name)
OUT.write_bytes(candidate.encode("utf-8"));digest=hashlib.sha256(OUT.read_bytes()).hexdigest()
rows=list(csv.DictReader(REGISTER.read_text(encoding="utf-8").splitlines()))
if len(rows)!=5847:raise RuntimeError("register row count mismatch")
base_all={"reviewed":3914,"fixed_rechecked":254,"pending":1679,"total":5847}
base_vocab={"reviewed":3345,"fixed_rechecked":253,"pending":316,"total":3914}
target_all={"reviewed":3914,"fixed_rechecked":265,"pending":1668,"total":5847}
target_vocab={"reviewed":3345,"fixed_rechecked":264,"pending":305,"total":3914}
if counts(rows)!=base_all or counts(rows,"vocab")!=base_vocab:raise RuntimeError("register baseline mismatch")
keys=[(r["kind"],r["key"]) for r in rows]
if len(keys)!=len(set(keys)):raise RuntimeError("duplicate register keys")
bykey={}
for r in rows:
 if r["kind"]=="vocab" and r["key"] in FIXED_IDS:bykey.setdefault(r["key"],[]).append(r)
if any(len(bykey.get(cid,[]))!=1 for cid in FIXED_IDS):raise RuntimeError("register scope missing/duplicate")
for cid in FIXED_IDS:
 r=bykey[cid][0]
 if r["finalReview"]!="pending" or r["evidence"]:raise RuntimeError("register preimage mismatch "+cid)
 r["finalReview"]="fixed_rechecked";r["evidence"]="completion/v203-acceptance.tsv; JLPT_N1_v203_audit.md"
with REGISTER.open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=["kind","key","baselineLocation","finalReview","evidence"],lineterminator="\n");w.writeheader();w.writerows(rows)
if counts(rows)!=target_all or counts(rows,"vocab")!=target_vocab:raise RuntimeError("register target mismatch")
prepare={"pass":True,"base_version":"v202","base_sha256":base_sha,"candidate_version":"v203","candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"vocabulary_records":len(vocab),"grammar_records":len(grammar),"lexical_pairs":len(pairs),"unique_vocabulary_ids":len({int(x["id"]) for x in vocab}),"review_scope":[int(x) for x in FIXED_IDS],"fixed_rechecked":[int(x) for x in FIXED_IDS],"reviewed_without_change":[],"updated_fields":len(UPDATES),"changed_cards":[int(x) for x in changed],"field_updates":[{"id":int(cid),"field":field,"before":old,"after":new} for cid,field,old,new in UPDATES],"japanese_example_changes":[{"id":1178,"index":0,"before":BASE_EXAMPLES["1178"][0],"after":AFTER_EXAMPLES["1178"][0]}],"author_credit_before":3598,"author_credit_addition":11,"author_credit_after":3609,"protected_unchanged":{k:True for k in protected},"exact_rollback":True,"register_updated":True,"author_review_only":True}
registry={"pass":True,"register_rows":len(rows),"before":{"all":base_all,"vocabulary":base_vocab},"after":{"all":counts(rows),"vocabulary":counts(rows,"vocab")},"fixed_rechecked_ids":[int(x) for x in FIXED_IDS],"reviewed_ids":[],"author_credit_before":3598,"author_credit_after":3609,"duplicate_keys":0,"records_deleted":0,"history_rewritten":False}
(WORK/"prepare-results.json").write_text(json.dumps(prepare,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(WORK/"registry-results.json").write_text(json.dumps(registry,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
cp=WORK/"checkpoint.json";d=json.loads(cp.read_text(encoding="utf-8"));d["status"]="author review complete; deterministic candidate and registry prepared; Chromium verification pending";d["candidate_sha256"]=digest;d["candidate_bytes"]=OUT.stat().st_size;d["exact_rollback"]=True;cp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"pass":True,"candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"fixed_rechecked":FIXED_IDS,"updated_fields":len(UPDATES),"register_after":counts(rows),"vocabulary_after":counts(rows,"vocab")},ensure_ascii=False,indent=2))
