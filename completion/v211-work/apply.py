import csv,hashlib,json,re
from pathlib import Path
BASE=Path("JLPT_N1_ukrainian_reading_v210.html");OUT=Path("JLPT_N1_ukrainian_reading_v211.html")
WORK=Path("completion/v211-work");REGISTER=Path("completion/review-register.csv")
BASE_SHA="ced09771cf3ca0a2fdeba08691768f27a8f62b41c56353aacafee21be08f1474"
UPDATES=[
 ("1471","usage","傷跡が残る／心の傷跡: слід травми, також душевної. 傷痕 — інше написання, 痕跡 ширше. Не кожна свіжа 傷 уже є загоєним рубцем。","傷跡が残る／心の傷跡: фізичний або переносний слід ушкодження. 傷痕 — споріднене написання, зазвичай きずあと; також трапляється читання しょうこん. 痕跡 ширше й охоплює різні сліди та наслідки."),
 ("1477","t","новини, звістка, місцеперебування","звістка, відомості про стан або долю людини чи справи; 消息が分かる — дізнатися, що сталося"),
 ("1477","exampleTranslations[0]","Навіть через три дні після зникнення досі немає звісток про альпініста, який потрапив у біду。","Навіть через три дні після інциденту досі немає звісток про альпініста, який потрапив у біду."),
 ("1479","t","звірення двох наборів даних або об’єктів; する — звіряти","звірення двох або більше джерел, записів чи об’єктів; する — звіряти"),
 ("1479","usage","原本と写しを照合する: звірити два джерела на відповідність. 参照 — звернутися до джерела, 照会 — надіслати запит. Для照合 потрібен зміст, із яким порівнюють。","原本と写しを照合する: звірити два джерела на відповідність. 参照 — звернутися до джерела, 照会 — надіслати запит. 照合には比較対象となる情報が必要: для звірення потрібні дані, з якими порівнюють."),
 ("1484","exampleTranslations[1]","Слід дуже обережно уникати порушення справи за недостатніх доказів。","Не слід порушувати справу, якщо доказів недостатньо."),
 ("1485","t","подробиці; точна інформація про складники й обставини","детальний, докладний; подробиці, деталі; 詳細な説明 — докладне пояснення"),
 ("1485","exampleTranslations[0]","Про подробиці аварії планують окремо повідомити після завершення розслідування。","Щойно завершиться розслідування, про подробиці аварії повідомлять окремо."),
 ("1486","exampleTranslations[0]","Сміливість цього рішення відзначили похвалою як вітчизняні, так і закордонні медіа。","І вітчизняні, і закордонні медіа похвалили сміливе рішення."),
 ("1487","t","перешкода; порушення функції або роботи системи","перешкода; порушення функції або роботи системи; у 障害のある人 — людина з інвалідністю"),
 ("1489","usage","島に上陸する／台風が上陸する: вийти з моря на сушу; також про тайфун у спеціальному вжитку. 着岸 — причалити судном; це ще не висадка людей на берег。","島に上陸する／台風が上陸する: вийти з моря на сушу; у метеозведеннях — центр тайфуну досягає суші. 着岸 — причалити судном; це ще не висадка людей на берег."),
 ("1489","exampleTranslations[0]","Очікується, що потужний тайфун вийде на сушу на Кюсю вже завтра вранці。","За прогнозом, уже завтра вранці тайфун досягне узбережжя Кюсю."),
 ("1493","usage","条件を譲歩する／相手に譲歩する: поступитися частиною вимог або позиції. 妥協 частіше означає взаємне узгодження прийнятного рішення; поступка може бути односторонньою。","条件面で譲歩する／相手に譲歩する: поступитися в частині умов або зробити крок назустріч іншій стороні. 妥協 частіше означає взаємне узгодження прийнятного рішення; поступка може бути односторонньою."),
 ("1493","exampleTranslations[0]","Без поступок і працівників, і роботодавця завершити переговори домовленістю неможливо。","Без взаємних поступок працівників і роботодавця переговори навряд чи завершаться домовленістю."),
 ("1496","exampleTranslations[1]","Покладаючись на чутливість кінчиків пальців, майстер розрізняє найтонші відмінності товщини。","Покладаючись на чутливість кінчиків пальців, майстер розрізняє ледь помітну різницю в товщині.")
]
EXPECTED={
 "1471":("傷跡","きずあと",["名詞"]),"1477":("消息","しょうそく",["名詞"]),
 "1479":("照合","しょうごう",["名詞"]),"1484":("証拠","しょうこ",["名詞"]),
 "1485":("詳細","しょうさい",["名詞","ナ形"]),"1486":("賞賛","しょうさん",["名詞"]),
 "1487":("障害","しょうがい",["名詞"]),"1489":("上陸","じょうりく",["名詞"]),
 "1493":("譲歩","じょうほ",["名詞"]),"1496":("触覚","しょっかく",["名詞"])
}
BASE_EXAMPLES={
 "1471":["彼の腕には、若いころの事故でできた深い傷跡が今も残っている。","震災の傷跡は、十年が過ぎた今も、街のあちこちに残されている。"],
 "1477":["遭難した登山者の消息は、発生から三日たった今もつかめていない。","その業界の消息に通じた人物から、貴重な話を聞くことができた。"],
 "1479":["提出された署名を登録済みの記録と照合して、本人かどうかを確認する。","入館者の顔を事前の登録情報と照合する装置が、新たに導入された。"],
 "1484":["彼が不正に関与したことを示す決定的な証拠は、見つかっていない。","証拠が不十分なまま立件することは、慎重に避けなければならない。"],
 "1485":["事故の詳細については、調査が終わり次第、改めて報告する予定だ。","契約の詳細を確認するため、弁護士に内容の精査を依頼した。"],
 "1486":["その決断の勇気は、国内外のメディアから賞賛された。","彼の献身的な活動は、多くの人々の賞賛に値するものである。"],
 "1487":["計画の実現には、法規制という大きな障害が立ちはだかっている。","障害のある人も働きやすい職場づくりを、企業に求める声が強まっている。"],
 "1489":["大型の台風は、明朝にも九州に上陸する見通しである。","調査隊は、無人島に上陸して植物の生態を詳しく調べた。"],
 "1493":["労使双方が譲歩しなければ、交渉の妥結は望めない状況である。","これ以上は譲歩できないというのが、わが社の基本的な立場だ。"],
 "1496":["視覚に障害のある人にとって、触覚は情報を得る大切な手段である。","指先の触覚を頼りに、職人は微妙な厚みの違いを見分ける。"]
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
if base_sha!=BASE_SHA:raise RuntimeError("unexpected v210 base SHA-256: "+base_sha)
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
allowed={"1471":{"usage"},"1477":{"t","exampleTranslations"},"1479":{"t","usage"},"1484":{"exampleTranslations"},"1485":{"t","exampleTranslations"},"1486":{"exampleTranslations"},"1487":{"t"},"1489":{"usage","exampleTranslations"},"1493":{"usage","exampleTranslations"},"1496":{"exampleTranslations"}}
for cid in details:
 for field in before[cid]:
  if before[cid][field]!=details[cid][field] and field not in allowed.get(cid,set()):raise RuntimeError("unexpected field mutation "+cid+"."+field)
literal=json.dumps(details,ensure_ascii=False,separators=(",",":"));candidate=base[:ds]+literal+base[de:]
old="<title>JLPT N1 — ウクライナ語対応学習アプリ · v210</title>";new="<title>JLPT N1 — ウクライナ語対応学習アプリ · v211</title>"
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
base_all={"reviewed":3916,"fixed_rechecked":347,"pending":1584,"total":5847}
base_vocab={"reviewed":3347,"fixed_rechecked":346,"pending":221,"total":3914}
target_all={"reviewed":3916,"fixed_rechecked":357,"pending":1574,"total":5847}
target_vocab={"reviewed":3347,"fixed_rechecked":356,"pending":211,"total":3914}
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
 r["finalReview"]="fixed_rechecked";r["evidence"]="completion/v211-acceptance.tsv; JLPT_N1_v211_audit.md"
with REGISTER.open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=["kind","key","baselineLocation","finalReview","evidence"],lineterminator="\n");w.writeheader();w.writerows(rows)
if counts(rows)!=target_all or counts(rows,"vocab")!=target_vocab:raise RuntimeError("register target mismatch")
prepare={"pass":True,"base_version":"v210","base_sha256":base_sha,"candidate_version":"v211","candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"vocabulary_records":len(vocab),"grammar_records":len(grammar),"lexical_pairs":len(pairs),"unique_vocabulary_ids":len({int(x["id"]) for x in vocab}),"review_scope":[int(x) for x in FIXED_IDS],"fixed_rechecked":[int(x) for x in FIXED_IDS],"reviewed_without_change":[],"deferred_count":2,"updated_fields":len(UPDATES),"changed_cards":[int(x) for x in changed],"field_updates":[{"id":int(cid),"field":field,"before":old,"after":new} for cid,field,old,new in UPDATES],"japanese_example_changes":[],"japanese_definition_changes":[],"author_credit_before":3693,"author_credit_addition":10,"author_credit_after":3703,"protected_unchanged":{k:True for k in protected},"exact_rollback":True,"register_updated":True,"author_review_only":True}
registry={"pass":True,"register_rows":len(rows),"before":{"all":base_all,"vocabulary":base_vocab},"after":{"all":counts(rows),"vocabulary":counts(rows,"vocab")},"fixed_rechecked_ids":[int(x) for x in FIXED_IDS],"reviewed_ids":[],"deferred_count":2,"author_credit_before":3693,"author_credit_after":3703,"duplicate_keys":0,"records_deleted":0,"history_rewritten":False}
(WORK/"prepare-results.json").write_text(json.dumps(prepare,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(WORK/"registry-results.json").write_text(json.dumps(registry,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
cp=WORK/"checkpoint.json";d=json.loads(cp.read_text(encoding="utf-8"));d["status"]="author review complete; deterministic candidate and registry prepared; Chromium verification pending";d["candidate_sha256"]=digest;d["candidate_bytes"]=OUT.stat().st_size;d["exact_rollback"]=True;cp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"pass":True,"candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"fixed_rechecked":FIXED_IDS,"deferred_count":2,"updated_fields":len(UPDATES),"register_after":counts(rows),"vocabulary_after":counts(rows,"vocab")},ensure_ascii=False,indent=2))
