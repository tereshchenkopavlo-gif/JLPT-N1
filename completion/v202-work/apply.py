import csv,hashlib,json,re
from pathlib import Path
BASE=Path("JLPT_N1_ukrainian_reading_v201.html")
OUT=Path("JLPT_N1_ukrainian_reading_v202.html")
WORK=Path("completion/v202-work")
REGISTER=Path("completion/review-register.csv")
BASE_SHA="ab7369a2ff4af2a74b79111713ad14b19d1dd4ae4519c15580a8e2e25674ce34"
UPDATES=[
 ("1119","t","безпосередня близькість; прилягати, розташовуватися зовсім поруч","безпосередня близькість; розташовуватися зовсім поруч"),
 ("1123","exampleTranslations[0]","Новий виріб від самого початку продавався важко, і продажі не зростали як очікувалося.","Новий продукт від самого початку мав труднощі на ринку, а продажі не зростали, як очікувалося."),
 ("1124","exampleTranslations[1]","Завдяки вправному володінню кількома мовами він довів переговори на міжнародній конференції до домовленості.","Завдяки вмілому використанню кількох мов він успішно завершив переговори на міжнародній конференції."),
 ("1127","exampleTranslations[1]","Її вважають однією з найсильніших піаністок країни.","Її вважають однією з наймайстерніших піаністок країни."),
 ("1128","t","заломлення променя світла; переносно — складні, суперечливі або викривлені почуття","згинання; заломлення світла або хвиль; переносно — складні, суперечливі чи викривлені почуття"),
 ("1129","exampleTranslations[1]","Іноді настрої натовпу легко змінюються під впливом одного підбурювача.","Іноді досить однієї людини, щоб підбурити натовп."),
 ("1132","exampleTranslations[0]","За законом порушникам передбачено суворе кримінальне покарання.","За законом за такі порушення передбачене суворе кримінальне покарання."),
 ("1135","exampleTranslations[1]","Компанії зі спільним фінансуванням привертають увагу як нова форма ведення бізнесу.","Компанії, створені на основі спільних капіталовкладень, привертають увагу як нова форма ведення бізнесу."),
 ("1139","exampleTranslations[0]","Постійні сумлінні зусилля приводять до надійних результатів.","Постійні сумлінні зусилля приводять до відчутних результатів."),
 ("1140","exampleTranslations[0]","Готуючись до наближення тайфуну, мешканці узбережжя посилюють пильність щодо штормового нагону води.","Готуючись до наближення тайфуну, мешканці узбережжя пильніше стежать за загрозою штормового нагону води."),
 ("1147","exampleTranslations[0]","Через зниження народжуваності кількість учнів сільських початкових шкіл різко скорочується.","Через зниження народжуваності кількість учнів початкових шкіл у регіонах різко скорочується."),
 ("1147","exampleTranslations[1]","Різке зменшення кількості туристів завдало тяжкого удару готельній галузі.","Різке скорочення кількості туристів завдало тяжкого удару галузі туристичного розміщення."),
 ("1148","exampleTranslations[0]","Клієнт страшенно розлютився через несправедливе ставлення й зажадав викликати відповідального працівника.","Клієнт страшенно розлютився через несправедливе ставлення й наказав відповідальному працівникові підійти.")
]
EXPECTED={
 "1119":("近接","きんせつ",["名詞"]),
 "1123":("苦戦","くせん",["名詞"]),
 "1124":("駆使","くし",["名詞"]),
 "1127":("屈指","くっし",["名詞"]),
 "1128":("屈折","くっせつ",["名詞"]),
 "1129":("群衆","ぐんしゅう",["名詞"]),
 "1132":("刑罰","けいばつ",["名詞"]),
 "1135":("形態","けいたい",["名詞"]),
 "1139":("継続","けいぞく",["名詞"]),
 "1140":("警戒","けいかい",["名詞"]),
 "1147":("激減","げきげん",["名詞"]),
 "1148":("激怒","げきど",["名詞"])
}
EXPECTED_EXAMPLES={
 "1119":["工場に近接する住宅地では、騒音への苦情が絶えなかった。","二つの町が近接しているため、合併の協議が進められている。"],
 "1123":["新製品は発売当初から苦戦を強いられ、売り上げが伸び悩んだ。","終盤まで苦戦したものの、チームはどうにか逃げ切って勝利した。"],
 "1124":["最新の技術を駆使して、古い建造物の復元が進められている。","彼は複数の言語を駆使して、国際会議で交渉をまとめた。"],
 "1127":["この港は、世界でも屈指の取扱量を誇る貿易の拠点である。","彼女は、国内でも屈指の実力を持つピアニストと評されている。"],
 "1128":["光は水中に入るとき屈折して、物が曲がって見える。","幼いころの経験から、彼の心情は複雑に屈折していった。"],
 "1129":["広場には、演説を聞こうと集まった群衆があふれていた。","群衆の心理は、時にひとりの扇動によって容易に動かされる。"],
 "1132":["違反者には、法律に基づいて厳しい刑罰が科されることになっている。","刑罰の重さだけで、犯罪を抑止できるとは限らない。"],
 "1135":["近年は、企業の雇用形態が多様化し、働き方も変わってきた。","新しい経営の形態として、共同出資の会社が注目を集めている。"],
 "1139":["地道な努力を継続することが、確かな成果へとつながる。","契約の継続を望む場合は、期限までに手続きを済ませる必要がある。"],
 "1140":["台風の接近に備えて、沿岸の住民は高潮への警戒を強めている。","彼は、見知らぬ人物からの申し出を警戒して、返事を保留した。"],
 "1147":["少子化の影響で、地方の小学校に通う児童が激減している。","観光客が激減したため、宿泊業界は深刻な打撃を受けた。"],
 "1148":["不当な扱いを受けたことに、顧客は激怒して担当者を呼びつけた。","彼は、約束を破られたことを知って激怒した。"]
}
FIXED_IDS=["1119","1123","1124","1127","1128","1129","1132","1135","1139","1140","1147","1148"]
REVIEWED_IDS=[];PENDING_IDS=[];EXPECTED_CHANGED=FIXED_IDS
EVIDENCE="completion/v202-acceptance.tsv; JLPT_N1_v202_audit.md"
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
if base_sha!=BASE_SHA:raise RuntimeError("unexpected v201 base SHA-256: "+base_sha)
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
 if details[cid]["examples"]!=EXPECTED_EXAMPLES[cid]:raise RuntimeError("Japanese example mismatch "+cid)
before=json.loads(json.dumps(details,ensure_ascii=False))
for cid,field,old,new in UPDATES:
 if field.startswith("exampleTranslations["):
  i=int(re.search(r"\[(\d+)\]",field).group(1))
  if details[cid]["exampleTranslations"][i]!=old:raise RuntimeError("preimage mismatch "+cid+"."+field)
  details[cid]["exampleTranslations"][i]=new
 else:
  if details[cid][field]!=old:raise RuntimeError("preimage mismatch "+cid+"."+field)
  details[cid][field]=new
changed=sorted((cid for cid in details if details[cid]!=before[cid]),key=int)
if changed!=EXPECTED_CHANGED:raise RuntimeError("changed-card set mismatch "+str(changed))
allowed={"1119":{"t"},"1123":{"exampleTranslations"},"1124":{"exampleTranslations"},"1127":{"exampleTranslations"},"1128":{"t"},"1129":{"exampleTranslations"},"1132":{"exampleTranslations"},"1135":{"exampleTranslations"},"1139":{"exampleTranslations"},"1140":{"exampleTranslations"},"1147":{"exampleTranslations"},"1148":{"exampleTranslations"}}
for cid in details:
 for field in before[cid]:
  if before[cid][field]!=details[cid][field] and field not in allowed.get(cid,set()):raise RuntimeError("unexpected field mutation "+cid+"."+field)
 if before[cid]["examples"]!=details[cid]["examples"]:raise RuntimeError("Japanese example changed "+cid)
literal=json.dumps(details,ensure_ascii=False,separators=(",",":"))
candidate=base[:ds]+literal+base[de:]
old="<title>JLPT N1 — ウクライナ語対応学習アプリ · v201</title>";new="<title>JLPT N1 — ウクライナ語対応学習アプリ · v202</title>"
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
base_all={"reviewed":3914,"fixed_rechecked":242,"pending":1691,"total":5847}
base_vocab={"reviewed":3345,"fixed_rechecked":241,"pending":328,"total":3914}
target_all={"reviewed":3914,"fixed_rechecked":254,"pending":1679,"total":5847}
target_vocab={"reviewed":3345,"fixed_rechecked":253,"pending":316,"total":3914}
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
 r["finalReview"]="fixed_rechecked";r["evidence"]=EVIDENCE
with REGISTER.open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=["kind","key","baselineLocation","finalReview","evidence"],lineterminator="\n");w.writeheader();w.writerows(rows)
if counts(rows)!=target_all or counts(rows,"vocab")!=target_vocab:raise RuntimeError("register target mismatch")
prepare={"pass":True,"base_version":"v201","base_sha256":base_sha,"candidate_version":"v202","candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"vocabulary_records":len(vocab),"grammar_records":len(grammar),"lexical_pairs":len(pairs),"unique_vocabulary_ids":len({int(x["id"]) for x in vocab}),"review_scope":[int(x) for x in FIXED_IDS],"fixed_rechecked":[int(x) for x in FIXED_IDS],"reviewed_without_change":[],"updated_fields":len(UPDATES),"changed_cards":[int(x) for x in changed],"field_updates":[{"id":int(cid),"field":field,"before":old,"after":new} for cid,field,old,new in UPDATES],"author_credit_before":3586,"author_credit_addition":12,"author_credit_after":3598,"protected_unchanged":{k:True for k in protected},"japanese_examples_unchanged":True,"exact_rollback":True,"register_updated":True,"author_review_only":True}
registry={"pass":True,"register_rows":len(rows),"before":{"all":base_all,"vocabulary":base_vocab},"after":{"all":counts(rows),"vocabulary":counts(rows,"vocab")},"fixed_rechecked_ids":[int(x) for x in FIXED_IDS],"reviewed_ids":[],"author_credit_before":3586,"author_credit_after":3598,"duplicate_keys":0,"records_deleted":0,"history_rewritten":False}
(WORK/"prepare-results.json").write_text(json.dumps(prepare,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(WORK/"registry-results.json").write_text(json.dumps(registry,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
cp=WORK/"checkpoint.json";d=json.loads(cp.read_text(encoding="utf-8"));d["status"]="author review complete; deterministic candidate and register prepared; Chromium verification pending";d["candidate_sha256"]=digest;d["candidate_bytes"]=OUT.stat().st_size;d["exact_rollback"]=True;cp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"pass":True,"candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"fixed_rechecked":FIXED_IDS,"updated_fields":len(UPDATES),"register_after":counts(rows),"vocabulary_after":counts(rows,"vocab")},ensure_ascii=False,indent=2))
