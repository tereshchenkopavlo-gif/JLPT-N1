import csv,hashlib,json,re
from pathlib import Path
BASE=Path("JLPT_N1_ukrainian_reading_v204.html");OUT=Path("JLPT_N1_ukrainian_reading_v205.html")
WORK=Path("completion/v205-work");REGISTER=Path("completion/review-register.csv")
BASE_SHA="19b13f568b34d26d72d40ee09866dfab5c2ca90532dbd8b9f5fe1abda0802383"
UPDATES=[
 ("1297","exampleTranslations[0]","Нині в нашому навчальному закладі числиться близько тисячі студентів, які щодня займаються дослідженнями.","Нині в нашому навчальному закладі навчається близько тисячі студентів, які щодня займаються дослідженнями."),
 ("1297","exampleTranslations[1]","Навіть під час тривалої перерви в роботі він залишається в штаті компанії й чекає на повернення.","Під час тимчасової перерви в роботі він залишається в штаті компанії й чекає на повернення."),
 ("1300","exampleTranslations[1]","У колоніальну добу місцеві ресурси нещадно використовували, а жителі жили в злиднях.","У колоніальну добу місцеві ресурси експлуатували, а жителі потерпали від злиднів."),
 ("1301","exampleTranslations[1]","Останнім часом разом із урізноманітненням способів роботи істотно змінюються й кадрові системи підприємств.","Останнім часом, із поширенням різних форм роботи, істотно змінюються й кадрові системи підприємств."),
 ("1303","usage","危険・変化を察知する: помітити за непрямими ознаками. Часто йдеться про швидке усвідомлення прихованого. 感知 може означати також реєстрацію сигналу приладом.","危険・変化を察知する／センサーが異常を察知する: розпізнати небезпеку, зміну чи відхилення за ознаками або сигналами. 察知 підкреслює розпізнавання значущої ознаки; 感知 нейтральніше описує виявлення сигналу приладом."),
 ("1306","exampleTranslations[1]","Студентів, які відвідали завод, вразив високий рівень місцевих технологій.","Студентів, які побували на заводі, вразив високий технологічний рівень виробництва."),
 ("1309","exampleTranslations[0]","У горах погода легко змінюється раптово, тому альпіністам потрібна ретельна підготовка.","У гірській місцевості погода може різко змінитися, тому тим, хто вирушає в гори, потрібно ретельно підготуватися."),
 ("1311","exampleTranslations[0]","Гірський хребет, яким проходить кордон, здавна був природною перепоною для спілкування між двома країнами.","Гірський хребет, яким проходить кордон, здавна був природною перепоною для зв’язків між двома країнами."),
 ("1312","exampleTranslations[0]","Було дано обіцянку суворо дотримуватися заходів безпеки, щоб така трагедія більше не повторилася.","Було пообіцяно забезпечити повне виконання заходів безпеки, щоб така трагедія більше не повторилася."),
 ("1313","exampleTranslations[0]","Правляча партія зазнала нищівної поразки від опозиції на місцевих виборах, і вимоги відповідальності її лідера посилилися.","Правляча партія зазнала нищівної поразки від опозиції на місцевих виборах, і посилилися заклики притягнути її лідера до відповідальності."),
 ("1313","exampleTranslations[1]","Новий товар програв конкурентам, і компанія була змушена згорнути цей напрям бізнесу.","Новий товар зазнав нищівної поразки в конкуренції з іншими виробниками, і компанія була змушена згорнути цей напрям бізнесу."),
 ("1315","exampleTranslations[0]","Ця страва відома як місцевий делікатес, у якому майстерно використано продукти регіону.","Це відома страва місцевої кухні, у якій майстерно використано продукти регіону."),
 ("1316","t","окиснення — хімічна реакція сполуки з киснем або втрата електронів (酸化する — окиснюватися)","окиснення — сполучення речовини з киснем або, у ширшому визначенні, втрата електронів (酸化する — окиснюватися)"),
 ("1319","t","чиїсь дії, що призвели до небажаного результату; «це його рук справа» (誰の仕業だ — хто це накоїв?)","чиїсь дії, що призвели до небажаного результату; «це справа його рук» (誰の仕業だ — хто це накоїв?)")
]
EXPECTED={
 "1297":("在籍","ざいせき",["名詞"]),"1300":("搾取","さくしゅ",["名詞"]),
 "1301":("昨今","さっこん",["名詞"]),"1303":("察知","さっち",["名詞"]),
 "1306":("参観","さんかん",["名詞"]),"1309":("山岳","さんがく",["名詞"]),
 "1311":("山脈","さんみゃく",["名詞"]),"1312":("惨事","さんじ",["名詞"]),
 "1313":("惨敗","ざんぱい",["名詞"]),"1315":("産物","さんぶつ",["名詞"]),
 "1316":("酸化","さんか",["名詞"]),"1319":("仕業","しわざ",["名詞"])
}
BASE_EXAMPLES={
 "1297":["現在、当校には約千名の学生が在籍し、日々研究に励んでいる。","彼は、休職中も会社に在籍し、復帰の時期を待っている。"],
 "1300":["劣悪な環境で長時間働かせ、労働者を搾取する企業は、厳しく非難された。","植民地時代には、現地の資源が搾取され、住民の暮らしは困窮した。"],
 "1301":["昨今の物価高を受けて、家計の見直しを図る世帯が増えている。","昨今、働き方の多様化に伴い、企業の人事制度も大きく変化している。"],
 "1303":["担当者は、取引先の不穏な動きを早い段階で察知し、上司に報告した。","異常を察知したセンサーが、自動的に生産ラインを停止させた。"],
 "1306":["保護者は、授業の様子を参観するため、午前中から学校を訪れた。","工場を参観した学生たちは、現場の技術の高さに感銘を受けた。"],
 "1309":["山岳地帯では、天候が急変しやすく、登山者は十分な備えが必要である。","この国の国土の大半は、険しい山岳に覆われている。"],
 "1311":["国境をなす山脈は、古くから両国の交流を隔てる自然の壁であった。","雪をいただく山脈が、地平線の彼方まで連なっている。"],
 "1312":["二度とこのような惨事を繰り返さないよう、安全対策の徹底が誓われた。","大規模な火災による惨事を受け、建築基準の見直しが進められている。"],
 "1313":["与党は、地方選挙で野党に惨敗し、党首の責任を問う声が強まった。","新商品は競合他社に惨敗し、事業の撤退を余儀なくされた。"],
 "1315":["この料理は、地域の産物を巧みに生かした郷土の味として知られている。","今回の成功は、関係者の長年にわたる努力の産物にほかならない。"],
 "1316":["鉄の表面が酸化して、さびが生じた。","食品の酸化を防ぐため、包装には特殊な素材が用いられている。"],
 "1319":["警察は、一連の放火は同一人物の仕業とみて、捜査を進めている。","こんな悪質ないたずらは、一体誰の仕業なのかと、住民は首をかしげた。"]
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
if base_sha!=BASE_SHA:raise RuntimeError("unexpected v204 base SHA-256: "+base_sha)
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
allowed={"1297":{"exampleTranslations"},"1300":{"exampleTranslations"},"1301":{"exampleTranslations"},"1303":{"usage"},"1306":{"exampleTranslations"},"1309":{"exampleTranslations"},"1311":{"exampleTranslations"},"1312":{"exampleTranslations"},"1313":{"exampleTranslations"},"1315":{"exampleTranslations"},"1316":{"t"},"1319":{"t"}}
for cid in details:
 for field in before[cid]:
  if before[cid][field]!=details[cid][field] and field not in allowed.get(cid,set()):raise RuntimeError("unexpected field mutation "+cid+"."+field)
 if cid in BASE_EXAMPLES and before[cid]["examples"]!=details[cid]["examples"]:raise RuntimeError("unexpected Japanese example change "+cid)
literal=json.dumps(details,ensure_ascii=False,separators=(",",":"));candidate=base[:ds]+literal+base[de:]
old="<title>JLPT N1 — ウクライナ語対応学習アプリ · v204</title>";new="<title>JLPT N1 — ウクライナ語対応学習アプリ · v205</title>"
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
base_all={"reviewed":3915,"fixed_rechecked":276,"pending":1656,"total":5847}
base_vocab={"reviewed":3346,"fixed_rechecked":275,"pending":293,"total":3914}
target_all={"reviewed":3915,"fixed_rechecked":288,"pending":1644,"total":5847}
target_vocab={"reviewed":3346,"fixed_rechecked":287,"pending":281,"total":3914}
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
 r["finalReview"]="fixed_rechecked";r["evidence"]="completion/v205-acceptance.tsv; JLPT_N1_v205_audit.md"
with REGISTER.open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=["kind","key","baselineLocation","finalReview","evidence"],lineterminator="\n");w.writeheader();w.writerows(rows)
if counts(rows)!=target_all or counts(rows,"vocab")!=target_vocab:raise RuntimeError("register target mismatch")
prepare={"pass":True,"base_version":"v204","base_sha256":base_sha,"candidate_version":"v205","candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"vocabulary_records":len(vocab),"grammar_records":len(grammar),"lexical_pairs":len(pairs),"unique_vocabulary_ids":len({int(x["id"]) for x in vocab}),"review_scope":[int(x) for x in FIXED_IDS],"fixed_rechecked":[int(x) for x in FIXED_IDS],"reviewed_without_change":[],"updated_fields":len(UPDATES),"changed_cards":[int(x) for x in changed],"field_updates":[{"id":int(cid),"field":field,"before":old,"after":new} for cid,field,old,new in UPDATES],"japanese_example_changes":[],"author_credit_before":3621,"author_credit_addition":12,"author_credit_after":3633,"protected_unchanged":{k:True for k in protected},"exact_rollback":True,"register_updated":True,"author_review_only":True}
registry={"pass":True,"register_rows":len(rows),"before":{"all":base_all,"vocabulary":base_vocab},"after":{"all":counts(rows),"vocabulary":counts(rows,"vocab")},"fixed_rechecked_ids":[int(x) for x in FIXED_IDS],"reviewed_ids":[],"author_credit_before":3621,"author_credit_after":3633,"duplicate_keys":0,"records_deleted":0,"history_rewritten":False}
(WORK/"prepare-results.json").write_text(json.dumps(prepare,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(WORK/"registry-results.json").write_text(json.dumps(registry,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
cp=WORK/"checkpoint.json";d=json.loads(cp.read_text(encoding="utf-8"));d["status"]="author review complete; deterministic candidate and registry prepared; Chromium verification pending";d["candidate_sha256"]=digest;d["candidate_bytes"]=OUT.stat().st_size;d["exact_rollback"]=True;cp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"pass":True,"candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"fixed_rechecked":FIXED_IDS,"updated_fields":len(UPDATES),"register_after":counts(rows),"vocabulary_after":counts(rows,"vocab")},ensure_ascii=False,indent=2))
