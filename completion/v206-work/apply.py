import csv,hashlib,json,re
from pathlib import Path
BASE=Path("JLPT_N1_ukrainian_reading_v205.html");OUT=Path("JLPT_N1_ukrainian_reading_v206.html")
WORK=Path("completion/v206-work");REGISTER=Path("completion/review-register.csv")
BASE_SHA="3b06dc6001359d033d31902227e56daaacd95501471faece756c1a70a582e2aa"
UPDATES=[
 ("1322","t","судочинство, правосуддя","судочинство, правосуддя; як гілка влади — судова влада"),
 ("1323","exampleTranslations[0]","Договір передбачає відповідальне поводження з обладнанням після його використання.","Договір зобов’язує відповідально прибирати або утилізувати обладнання після використання."),
 ("1327","exampleTranslations[0]","Останніми роками молодь дедалі більше орієнтується на самореалізацію, а не на стабільність.","Останніми роками серед молоді помітна сильна орієнтація на самореалізацію, а не на стабільність."),
 ("1329","t","намір, розрахунок, мотив","намір, розрахунок; очікування, сподівання; думка інших про когось"),
 ("1331","t","вказівка, наказувати, давати розпорядження","вказівка, розпорядження; 指図する — вказувати, наказувати, розпоряджатися"),
 ("1333","exampleTranslations[1]","До показників стійкості підприємства належать не лише фінанси, а й увага до довкілля.","До показників життєздатності підприємства належать не лише фінансові параметри, а й урахування впливу на довкілля."),
 ("1334","m","指先の内側にある、渦状のすじの模様。また、それが物に付いたあと。","手指の指先の内側にある皮膚隆線がつくる模様。また、その模様を物に押しつけて残した像。"),
 ("1334","t","відбиток пальця","папілярний візерунок на подушечці пальця; також його відбиток"),
 ("1335","exampleTranslations[0]","Штаб наказав підрозділу на місці негайно відійти.","Штаб наказав підрозділу на місці негайно залишити цей район."),
 ("1339","t","уведення норми в дію; здійснення заходу; する — уводити в дію, здійснювати","уведення закону, правила чи політики в дію; набрання чинності; 施行する — уводити в дію, запроваджувати"),
 ("1339","usage","法律を施行する／法律が施行される: увести норму в дію. Читання しこう, також せこう. 制定 — установити норму; її ухвалення й набрання чинності можуть припадати на різні дати.","法律・規則・政策を施行する／施行される: запровадити закон, правило чи політику. Звичайне читання — しこう; せこう також трапляється як慣用音 у частині адміністративних контекстів. Не плутати з 施工（せこう） — виконання будівельних робіт. 制定 — ухвалити норму; 施行 — увести її в дію."),
 ("1340","t","споруда або комплекс приміщень певного призначення","спеціально облаштований об’єкт або заклад певного призначення; будівля чи комплекс приміщень"),
 ("1341","exampleTranslations[0]","В аварії загинули або були поранені понад десятеро пасажирів і членів екіпажу.","В аварії загинули або зазнали поранень близько півтора десятка пасажирів і членів екіпажу."),
 ("1344","exampleTranslations[1]","Експонати цієї виставки можна оглядати на дотик, щоб нею могли насолодитися й люди з порушеннями зору.","Експонати цієї виставки можна досліджувати на дотик, тож насолодитися нею зможуть і люди з порушеннями зору.")
]
EXPECTED={
 "1322":("司法","しほう",["名詞"]),"1323":("始末","しまつ",["名詞"]),
 "1327":("志向","しこう",["名詞"]),"1329":("思惑","おもわく",["名詞"]),
 "1331":("指図","さしず",["名詞"]),"1333":("指標","しひょう",["名詞"]),
 "1334":("指紋","しもん",["名詞"]),"1335":("指令","しれい",["名詞"]),
 "1339":("施行","しこう／せこう",["名詞"]),"1340":("施設","しせつ",["名詞"]),
 "1341":("死傷","ししょう",["名詞"]),"1344":("視覚","しかく",["名詞"])
}
BASE_EXAMPLES={
 "1322":["司法の独立は、三権分立を支える重要な原則の一つである。","司法の判断が、政治の動向に大きな影響を及ぼすこともある。"],
 "1323":["使用済みの機材は、責任をもって始末することが契約に定められている。","準備を怠ったあげく、会議に遅刻する始末だった。"],
 "1327":["近年、若い世代の間では、安定よりも自己実現を志向する傾向が強い。","同社は、海外市場を志向する戦略へと、大きくかじを切った。"],
 "1329":["各国の思惑が交錯して、交渉は思うように進展していない。","彼の思惑どおりには運ばず、計画は暗礁に乗り上げてしまった。"],
 "1331":["他人に指図されることを嫌い、彼は独立して事業を始めた。","現場の責任者の指図に従って、作業員たちが整然と動いた。"],
 "1333":["景気の動向を示す指標として、消費者物価指数が広く用いられている。","企業の健全性を測る指標には、財務面だけでなく環境への配慮も含まれる。"],
 "1334":["鑑識課員が、現場に残された指紋を丹念に採取した。","最近のスマートフォンは、指紋による認証で簡単にロックを解除できる。"],
 "1335":["本部は、現場の部隊に直ちに撤収するよう指令した。","全店舗に対して、安全点検の実施が指令された。"],
 "1339":["改正された法律は、来年四月から全面的に施行される予定である。","新しい規則が施行されるのに伴い、各社は社内規定の改定を急いでいる。"],
 "1340":["市は、高齢者が安心して過ごせる福祉施設の整備に力を入れている。","公共施設の老朽化が進み、維持管理の費用が財政を圧迫している。"],
 "1341":["事故で乗客や乗員十数人が死傷した。","死傷した人々の家族への補償について、会社は誠意ある対応を約束した。"],
 "1344":["視覚に頼りすぎると、他の感覚から得られる情報が見落とされがちである。","この展示は、視覚に障害のある人々も楽しめるよう、触れて鑑賞できる。"]
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
if base_sha!=BASE_SHA:raise RuntimeError("unexpected v205 base SHA-256: "+base_sha)
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
allowed={"1322":{"t"},"1323":{"exampleTranslations"},"1327":{"exampleTranslations"},"1329":{"t"},"1331":{"t"},"1333":{"exampleTranslations"},"1334":{"m","t"},"1335":{"exampleTranslations"},"1339":{"t","usage"},"1340":{"t"},"1341":{"exampleTranslations"},"1344":{"exampleTranslations"}}
for cid in details:
 for field in before[cid]:
  if before[cid][field]!=details[cid][field] and field not in allowed.get(cid,set()):raise RuntimeError("unexpected field mutation "+cid+"."+field)
 if cid in BASE_EXAMPLES and before[cid]["examples"]!=details[cid]["examples"]:raise RuntimeError("unexpected Japanese example change "+cid)
literal=json.dumps(details,ensure_ascii=False,separators=(",",":"));candidate=base[:ds]+literal+base[de:]
old="<title>JLPT N1 — ウクライナ語対応学習アプリ · v205</title>";new="<title>JLPT N1 — ウクライナ語対応学習アプリ · v206</title>"
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
base_all={"reviewed":3915,"fixed_rechecked":288,"pending":1644,"total":5847}
base_vocab={"reviewed":3346,"fixed_rechecked":287,"pending":281,"total":3914}
target_all={"reviewed":3915,"fixed_rechecked":300,"pending":1632,"total":5847}
target_vocab={"reviewed":3346,"fixed_rechecked":299,"pending":269,"total":3914}
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
 r["finalReview"]="fixed_rechecked";r["evidence"]="completion/v206-acceptance.tsv; JLPT_N1_v206_audit.md"
with REGISTER.open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=["kind","key","baselineLocation","finalReview","evidence"],lineterminator="\n");w.writeheader();w.writerows(rows)
if counts(rows)!=target_all or counts(rows,"vocab")!=target_vocab:raise RuntimeError("register target mismatch")
prepare={"pass":True,"base_version":"v205","base_sha256":base_sha,"candidate_version":"v206","candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"vocabulary_records":len(vocab),"grammar_records":len(grammar),"lexical_pairs":len(pairs),"unique_vocabulary_ids":len({int(x["id"]) for x in vocab}),"review_scope":[int(x) for x in FIXED_IDS],"fixed_rechecked":[int(x) for x in FIXED_IDS],"reviewed_without_change":[],"updated_fields":len(UPDATES),"changed_cards":[int(x) for x in changed],"field_updates":[{"id":int(cid),"field":field,"before":old,"after":new} for cid,field,old,new in UPDATES],"japanese_example_changes":[],"japanese_definition_changes":[{"id":1334,"field":"m","before":"指先の内側にある、渦状のすじの模様。また、それが物に付いたあと。","after":"手指の指先の内側にある皮膚隆線がつくる模様。また、その模様を物に押しつけて残した像。"}],"author_credit_before":3633,"author_credit_addition":12,"author_credit_after":3645,"protected_unchanged":{k:True for k in protected},"exact_rollback":True,"register_updated":True,"author_review_only":True}
registry={"pass":True,"register_rows":len(rows),"before":{"all":base_all,"vocabulary":base_vocab},"after":{"all":counts(rows),"vocabulary":counts(rows,"vocab")},"fixed_rechecked_ids":[int(x) for x in FIXED_IDS],"reviewed_ids":[],"author_credit_before":3633,"author_credit_after":3645,"duplicate_keys":0,"records_deleted":0,"history_rewritten":False}
(WORK/"prepare-results.json").write_text(json.dumps(prepare,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(WORK/"registry-results.json").write_text(json.dumps(registry,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
cp=WORK/"checkpoint.json";d=json.loads(cp.read_text(encoding="utf-8"));d["status"]="author review complete; deterministic candidate and registry prepared; Chromium verification pending";d["candidate_sha256"]=digest;d["candidate_bytes"]=OUT.stat().st_size;d["exact_rollback"]=True;cp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"pass":True,"candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"fixed_rechecked":FIXED_IDS,"updated_fields":len(UPDATES),"register_after":counts(rows),"vocabulary_after":counts(rows,"vocab")},ensure_ascii=False,indent=2))
