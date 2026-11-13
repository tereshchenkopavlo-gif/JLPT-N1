import csv,hashlib,json,re
from pathlib import Path
BASE=Path("JLPT_N1_ukrainian_reading_v209.html");OUT=Path("JLPT_N1_ukrainian_reading_v210.html")
WORK=Path("completion/v210-work");REGISTER=Path("completion/review-register.csv")
BASE_SHA="dcf845b65e20764f1bb8bbf0cbff5b20a368d13e8bfaad059f8728ca0fe8b2cf"
UPDATES=[
 ("1445","m","同じ物事が重なること。むだに繰り返されること。","同じ物事が重なること。また、同じことを繰り返すこと。"),
 ("1446","m","便利で役に立つため、大切に使うこと。","便利で役に立つため、大切に使うこと。また、便利で役に立つさま。"),
 ("1446","exampleTranslations[0]","Цей словник зручно носити із собою, і він дуже стає в пригоді навіть у відрядженнях。","Цей словник зручно носити із собою, і він дуже виручає у відрядженнях."),
 ("1449","exampleTranslations[1]","Після повідомлень про появу підозрілих осіб уночі патрулювання посилили。","Після повідомлень про те, що вночі тут час від часу з’являється хтось підозрілий, патрулювання посилили."),
 ("1451","m","見回りながら、あちこちをまわること。","あちこちの場所を順番に回ること。見回りや点検をしながら回ること。"),
 ("1455","m","事態に対して、しかるべき手段を取って始末をつけること。","事態に対して、しかるべき手段を取ること。また、けがや病気に必要な手当てをすること。"),
 ("1455","examples[1]","会社は、不正に関与した社員に対し、厳正に処置する方針だ。","会社は、不正に関与した社員に対し、厳正な処置を取る方針だ。"),
 ("1455","exampleTranslations[1]","Компанія планує суворо діяти щодо працівників, причетних до порушень。","Компанія планує вжити суворих заходів щодо працівників, причетних до порушень."),
 ("1457","m","不要なものを始末すること。また、規則に違反した者に罰を与えること。","不要なものを捨てたり、財産などを売却・譲渡したりすること。また、規則に違反した者に罰を与えること。"),
 ("1459","t","чути вперше, новина для вух","уперше почути, раніше невідома інформація; 初耳だ — уперше про це чути"),
 ("1459","exampleTranslations[0]","Я вперше чую, що такий план уже просувався。","Я вперше почув, що такий план уже розробляли."),
 ("1460","exampleTranslations[1]","Нарешті з’ясувалося, де перебуває документ, який вважали загубленим。","Нарешті з’ясувалося, де був документ, місцеперебування якого досі не могли встановити."),
 ("1461","t","володіння чимось при собі; する — мати при собі, тримати у своєму розпорядженні","наявність при собі; фактичне тримання у своєму розпорядженні; する — мати при собі"),
 ("1463","exampleTranslations[1]","Ця давня їдальня багато років користується любов’ю відвідувачів як заклад для простих людей。","Цю давню їдальню вже багато років цінують як заклад, що дбає про звичайних людей."),
 ("1467","exampleTranslations[0]","Щоб уникнути майбутніх суперечок, обов’язково оформлюйте й обмінюйтеся умовами договору письмово。","Щоб уникнути подальших суперечок, обов’язково зафіксуйте умови договору письмово й обміняйтеся документами."),
 ("1469","exampleTranslations[1]","Через сніг поїзд повільно пройшов ділянку перевірки колії。","Через сніг поїзд повільно проїхав ділянку колії, яку саме перевіряли.")
]
EXPECTED={
 "1445":("重複","ちょうふく／じゅうふく",["名詞"]),"1446":("重宝","ちょうほう",["名詞"]),
 "1449":("出没","しゅつぼつ",["名詞"]),"1451":("巡回","じゅんかい",["名詞"]),
 "1455":("処置","しょち",["名詞"]),"1457":("処分","しょぶん",["名詞"]),
 "1459":("初耳","はつみみ",["名詞"]),"1460":("所在","しょざい",["名詞"]),
 "1461":("所持","しょじ",["名詞"]),"1463":("庶民","しょみん",["名詞"]),
 "1467":("書面","しょめん",["名詞"]),"1469":("徐行","じょこう",["名詞"])
}
BASE_EXAMPLES={
 "1445":["二つの部署で業務が重複しており、無駄なコストが発生している。","提出書類の内容が重複しないよう、事前に確認しておくことが肝要だ。"],
 "1446":["この辞書は持ち運びに便利で、出張先でも重宝している。","幅広い知識をもつ彼は、どの部署からも重宝される存在だ。"],
 "1449":["この地域ではクマが出没する恐れがあるため、注意が呼びかけられている。","夜間に不審者が出没しているとの情報を受け、見回りが強化された。"],
 "1451":["警備員は、夜間に工場の敷地内を二時間おきに巡回している。","移動図書館が、過疎地の集落を巡回して本の貸し出しを行っている。"],
 "1455":["けが人に対しては、まず応急の処置を施すことが何よりも大切である。","会社は、不正に関与した社員に対し、厳正に処置する方針だ。"],
 "1457":["不要になった古い機器は、業者に依頼して適切に処分する必要がある。","情報漏洩に関与した社員は、減給の処分を受けた。"],
 "1459":["そのような計画が進んでいたとは、私にとってまったくの初耳である。","取引先の撤退の話は、担当の私でさえ初耳だった。"],
 "1460":["事故の責任の所在をめぐり、関係者の主張が真っ向から対立している。","行方不明となっていた文書の所在が、ようやく明らかになった。"],
 "1461":["入場券を所持している方は、こちらにお並びください。","現金を多額に所持して外出するのは、防犯上好ましくない。"],
 "1463":["物価の高騰は、庶民の暮らしに深刻な影響を及ぼしている。","この店は、庶民の味方として長年親しまれてきた老舗の食堂だ。"],
 "1467":["契約の内容は、後の紛争を避けるため、必ず書面で取り交わすこと。","ご質問に対しては、改めて書面にてご回答申し上げます。"],
 "1469":["工事区間では、すべての車両が徐行して通過するよう求められている。","列車は、雪の影響で線路の点検区間を徐行して走行した。"]
}
FIXED_IDS=list(EXPECTED)
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
if base_sha!=BASE_SHA:raise RuntimeError("unexpected v209 base SHA-256: "+base_sha)
base=raw.decode("utf-8")
_,_,vocab=extract(base,"DEFAULT_VOCAB");_,_,grammar=extract(base,"GRAMMAR_DETAILS_BY_ID")
ds,de,details=extract(base,"VOCAB_DETAILS_BY_ID");_,_,pos=extract(base,"VOCAB_POS_BY_ID")
_,_,pairs=extract(base,"VOCAB_AUDITED_PAIRS");_,_,meaning=extract(base,"REVIEWED_MEANING_QUIZZES")
_,_,reading=extract(base,"REVIEWED_READING_OPTIONS");_,_,kana=extract(base,"VOCAB_KANA_EXAMPLE_TARGETS")
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
if changed!=sorted(FIXED_IDS,key=int):raise RuntimeError("changed-card set mismatch "+str(changed))
allowed={"1445":{"m"},"1446":{"m","exampleTranslations"},"1449":{"exampleTranslations"},"1451":{"m"},"1455":{"m","examples","exampleTranslations"},"1457":{"m"},"1459":{"t","exampleTranslations"},"1460":{"exampleTranslations"},"1461":{"t"},"1463":{"exampleTranslations"},"1467":{"exampleTranslations"},"1469":{"exampleTranslations"}}
for cid in details:
 for field in before[cid]:
  if before[cid][field]!=details[cid][field] and field not in allowed.get(cid,set()):raise RuntimeError("unexpected field mutation "+cid+"."+field)
literal=json.dumps(details,ensure_ascii=False,separators=(",",":"));candidate=base[:ds]+literal+base[de:]
old="<title>JLPT N1 — ウクライナ語対応学習アプリ · v209</title>";new="<title>JLPT N1 — ウクライナ語対応学習アプリ · v210</title>"
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
base_all={"reviewed":3916,"fixed_rechecked":335,"pending":1596,"total":5847}
base_vocab={"reviewed":3347,"fixed_rechecked":334,"pending":233,"total":3914}
target_all={"reviewed":3916,"fixed_rechecked":347,"pending":1584,"total":5847}
target_vocab={"reviewed":3347,"fixed_rechecked":346,"pending":221,"total":3914}
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
 r["finalReview"]="fixed_rechecked";r["evidence"]="completion/v210-acceptance.tsv; JLPT_N1_v210_audit.md"
with REGISTER.open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=["kind","key","baselineLocation","finalReview","evidence"],lineterminator="\n");w.writeheader();w.writerows(rows)
if counts(rows)!=target_all or counts(rows,"vocab")!=target_vocab:raise RuntimeError("register target mismatch")
prepare={"pass":True,"base_version":"v209","base_sha256":base_sha,"candidate_version":"v210","candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"vocabulary_records":len(vocab),"grammar_records":len(grammar),"lexical_pairs":len(pairs),"unique_vocabulary_ids":len({int(x["id"]) for x in vocab}),"review_scope":[int(x) for x in FIXED_IDS],"fixed_rechecked":[int(x) for x in FIXED_IDS],"reviewed_without_change":[],"updated_fields":len(UPDATES),"changed_cards":[int(x) for x in changed],"field_updates":[{"id":int(cid),"field":field,"before":old,"after":new} for cid,field,old,new in UPDATES],"japanese_example_changes":[{"id":1455,"field":"examples[1]"}],"japanese_definition_changes":[{"id":x,"field":"m"} for x in [1445,1446,1451,1455,1457]],"author_credit_before":3681,"author_credit_addition":12,"author_credit_after":3693,"protected_unchanged":{k:True for k in protected},"exact_rollback":True,"register_updated":True,"author_review_only":True}
registry={"pass":True,"register_rows":len(rows),"before":{"all":base_all,"vocabulary":base_vocab},"after":{"all":counts(rows),"vocabulary":counts(rows,"vocab")},"fixed_rechecked_ids":[int(x) for x in FIXED_IDS],"reviewed_ids":[],"author_credit_before":3681,"author_credit_after":3693,"duplicate_keys":0,"records_deleted":0,"history_rewritten":False}
(WORK/"prepare-results.json").write_text(json.dumps(prepare,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(WORK/"registry-results.json").write_text(json.dumps(registry,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
cp=WORK/"checkpoint.json";d=json.loads(cp.read_text(encoding="utf-8"));d["status"]="author review complete; deterministic candidate and registry prepared; Chromium verification pending";d["candidate_sha256"]=digest;d["candidate_bytes"]=OUT.stat().st_size;d["exact_rollback"]=True;cp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"pass":True,"candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"fixed_rechecked":FIXED_IDS,"updated_fields":len(UPDATES),"register_after":counts(rows),"vocabulary_after":counts(rows,"vocab")},ensure_ascii=False,indent=2))
