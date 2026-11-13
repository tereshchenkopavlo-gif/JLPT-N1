import csv,hashlib,json,re
from pathlib import Path
BASE=Path("JLPT_N1_ukrainian_reading_v203.html");OUT=Path("JLPT_N1_ukrainian_reading_v204.html")
WORK=Path("completion/v204-work");REGISTER=Path("completion/review-register.csv")
BASE_SHA="81b4e4fbda3be91325493c95c3c28324deac52f69cc230f16bd630db20929339"
UPDATES=[
 ("1198","exampleTranslations[0]","У чинній системі дедалі помітніші сторони, які не відповідають змінам часу.","У чинній системі дедалі помітнішими стають аспекти, що заважають їй пристосовуватися до змін часу."),
 ("1214","exampleTranslations[0]","Слід мати на увазі, що це дослідження має похибку в кілька відсоткових пунктів.","Слід мати на увазі, що це дослідження має похибку в кілька пунктів."),
 ("1218","exampleTranslations[1]","На відкритий набір членів комісії з усієї країни надійшло більш ніж уп’ятеро більше заявок, ніж було місць.","Кількість заявок на відкритий конкурс на посади членів комісії перевищила кількість місць більш ніж у п’ять разів."),
 ("1236","t","урахування певних обставин під час рішення; 〜を考慮する — брати до уваги","урахування певних обставин під час ухвалення рішення; 〜を考慮する — брати до уваги"),
 ("1237","examples[1]","彼の提案を肯定する意見が、会議の参加者の多数を占めた。","会議では、彼の提案を肯定する意見が多数を占めた。"),
 ("1237","exampleTranslations[1]","Більшість учасників наради висловили думки на підтримку його пропозиції.","На нараді переважали думки на підтримку його пропозиції."),
 ("1239","exampleTranslations[0]","Ліси, за якими не доглядають, занепадають, і небезпека зсувів також зростає.","Ліси, за якими не доглядають, занепадають, і небезпека зсувів та селів зростає."),
 ("1241","t","читання й докладне тлумачення тексту, особливо літературного чи класичного, під керівництвом викладача (講読する — розбирати текст)","читання й докладний розбір тексту, особливо літературного чи класичного, часто в навчальному контексті (講読する — розбирати текст)"),
 ("1241","exampleTranslations[0]","На семінарі ми читаємо й докладно розбираємо класичні твори в оригіналі, вивчаючи історичне підґрунтя ідей.","На семінарі ми читаємо й докладно розбираємо класичні твори в оригіналі, вивчаючи підґрунтя відповідних ідей."),
 ("1246","exampleTranslations[1]","Зрештою інша сторона здалася під натиском його наполегливих переговорів і прийняла умови.","Зрештою інша сторона поступилася його наполегливості й прийняла умови."),
 ("1248","t","висота й низина; різниця у висоті, рівні, тоні чи ступені (高低差 — перепад висот)","високий і низький рівні; різниця у висоті, тоні чи ступені (高低差 — перепад висот)"),
 ("1249","exampleTranslations[1]","Проміння, що пробивалося крізь просвіти між хмарами, чітко освітлювало гірський хребет.","Проміння, що пробивалося крізь просвіти між хмарами, чітко освітлювало лінію гірського гребеня."),
 ("1251","exampleTranslations[1]","Оскільки всі місця зайняті, просимо відвідувачів погодитися на спільні столики.","Оскільки всі місця зайняті, просимо сідати за один стіл з іншими відвідувачами.")
]
EXPECTED={
 "1198":("現行","げんこう",["名詞"]),"1202":("古来","こらい",["名詞"]),
 "1214":("誤差","ごさ",["名詞"]),"1218":("公募","こうぼ",["名詞"]),
 "1236":("考慮","こうりょ",["名詞"]),"1237":("肯定","こうてい",["名詞"]),
 "1239":("荒廃","こうはい",["名詞"]),"1241":("講読","こうどく",["名詞"]),
 "1246":("降参","こうさん",["名詞"]),"1248":("高低","こうてい",["名詞"]),
 "1249":("合間","あいま",["名詞"]),"1251":("合席","あいせき",["名詞"])
}
BASE_EXAMPLES={
 "1198":["現行の制度には、時代の変化に対応できない面が目立ち始めている。","現行の規則と改正案を読み比べた。"],
 "1202":["この地方では、古来、治水が最大の政治課題であった。","この地域には、古来の祭りが今も受け継がれている。"],
 "1214":["この調査には数ポイントの誤差が含まれることを、念頭に置く必要がある。","測定機器の誤差を最小限に抑えるため、定期的な校正が欠かせない。"],
 "1218":["市は新しい観光キャッチコピーを広く公募することを決定した。","委員の公募には、定員の五倍を超える応募が全国から寄せられた。"],
 "1236":["委員会は、地域経済への影響を考慮した上で、最終案をまとめた。","個々の事情を考慮せずに一律に適用すれば、不公平が生じかねない。"],
 "1237":["現状を肯定するだけでは、組織が抱える課題は解決されない。","彼の提案を肯定する意見が、会議の参加者の多数を占めた。"],
 "1239":["管理されない森林は荒廃が進み、土砂災害の危険も高まっている。","長引く紛争によって、国土は荒廃し、人々の暮らしは困窮した。"],
 "1241":["ゼミでは、古典の原書を講読しながら、思想の背景を学んでいる。","学生たちは、英語の専門書を講読して、研究の基礎を固めた。"],
 "1246":["あまりに複雑な契約条項の数々に、さすがの担当者も降参した。","彼の粘り強い交渉に、相手側もついに降参して条件を受け入れた。"],
 "1248":["このコースは高低の差が大きく、選手の体力を容赦なく奪う。","音の高低を正確に聞き分ける力は、訓練によって身につけられる。"],
 "1249":["多忙な業務の合間を縫って、彼は専門資格の勉強を続けている。","雲の合間から差し込む光が、山の稜線をくっきりと照らしていた。"],
 "1251":["昼どきの食堂は混み合い、見知らぬ客同士が合席する場面も多い。","満席のため、お客様には合席をお願いしております。"]
}
AFTER_EXAMPLES={k:list(v) for k,v in BASE_EXAMPLES.items()}
AFTER_EXAMPLES["1237"][1]="会議では、彼の提案を肯定する意見が多数を占めた。"
FIXED_IDS=["1198","1214","1218","1236","1237","1239","1241","1246","1248","1249","1251"]
REVIEWED_IDS=["1202"]
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
if base_sha!=BASE_SHA:raise RuntimeError("unexpected v203 base SHA-256: "+base_sha)
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
if changed!=EXPECTED_CHANGED:raise RuntimeError("changed-card set mismatch "+str(changed))
allowed={"1198":{"exampleTranslations"},"1214":{"exampleTranslations"},"1218":{"exampleTranslations"},"1236":{"t"},"1237":{"examples","exampleTranslations"},"1239":{"exampleTranslations"},"1241":{"t","exampleTranslations"},"1246":{"exampleTranslations"},"1248":{"t"},"1249":{"exampleTranslations"},"1251":{"exampleTranslations"}}
for cid in details:
 for field in before[cid]:
  if before[cid][field]!=details[cid][field] and field not in allowed.get(cid,set()):raise RuntimeError("unexpected field mutation "+cid+"."+field)
 if cid in AFTER_EXAMPLES and details[cid]["examples"]!=AFTER_EXAMPLES[cid]:raise RuntimeError("Japanese example postimage mismatch "+cid)
 if cid!="1237" and cid in BASE_EXAMPLES and before[cid]["examples"]!=details[cid]["examples"]:raise RuntimeError("unexpected Japanese example change "+cid)
literal=json.dumps(details,ensure_ascii=False,separators=(",",":"));candidate=base[:ds]+literal+base[de:]
old="<title>JLPT N1 — ウクライナ語対応学習アプリ · v203</title>";new="<title>JLPT N1 — ウクライナ語対応学習アプリ · v204</title>"
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
base_all={"reviewed":3914,"fixed_rechecked":265,"pending":1668,"total":5847}
base_vocab={"reviewed":3345,"fixed_rechecked":264,"pending":305,"total":3914}
target_all={"reviewed":3915,"fixed_rechecked":276,"pending":1656,"total":5847}
target_vocab={"reviewed":3346,"fixed_rechecked":275,"pending":293,"total":3914}
if counts(rows)!=base_all or counts(rows,"vocab")!=base_vocab:raise RuntimeError("register baseline mismatch")
keys=[(r["kind"],r["key"]) for r in rows]
if len(keys)!=len(set(keys)):raise RuntimeError("duplicate register keys")
bykey={}
for r in rows:
 if r["kind"]=="vocab" and r["key"] in FIXED_IDS+REVIEWED_IDS:bykey.setdefault(r["key"],[]).append(r)
if any(len(bykey.get(cid,[]))!=1 for cid in FIXED_IDS+REVIEWED_IDS):raise RuntimeError("register scope missing/duplicate")
for cid in FIXED_IDS:
 r=bykey[cid][0]
 if r["finalReview"]!="pending" or r["evidence"]:raise RuntimeError("register preimage mismatch "+cid)
 r["finalReview"]="fixed_rechecked";r["evidence"]="completion/v204-acceptance.tsv; JLPT_N1_v204_audit.md"
for cid in REVIEWED_IDS:
 r=bykey[cid][0]
 if r["finalReview"]!="pending" or r["evidence"]:raise RuntimeError("register preimage mismatch "+cid)
 r["finalReview"]="reviewed";r["evidence"]="completion/v204-acceptance.tsv; JLPT_N1_v204_audit.md"
with REGISTER.open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=["kind","key","baselineLocation","finalReview","evidence"],lineterminator="\n");w.writeheader();w.writerows(rows)
if counts(rows)!=target_all or counts(rows,"vocab")!=target_vocab:raise RuntimeError("register target mismatch")
prepare={"pass":True,"base_version":"v203","base_sha256":base_sha,"candidate_version":"v204","candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"vocabulary_records":len(vocab),"grammar_records":len(grammar),"lexical_pairs":len(pairs),"unique_vocabulary_ids":len({int(x["id"]) for x in vocab}),"review_scope":[int(x) for x in EXPECTED],"fixed_rechecked":[int(x) for x in FIXED_IDS],"reviewed_without_change":[int(x) for x in REVIEWED_IDS],"updated_fields":len(UPDATES),"changed_cards":[int(x) for x in changed],"field_updates":[{"id":int(cid),"field":field,"before":old,"after":new} for cid,field,old,new in UPDATES],"japanese_example_changes":[{"id":1237,"index":1,"before":BASE_EXAMPLES["1237"][1],"after":AFTER_EXAMPLES["1237"][1]}],"author_credit_before":3609,"author_credit_addition":12,"author_credit_after":3621,"protected_unchanged":{k:True for k in protected},"exact_rollback":True,"register_updated":True,"author_review_only":True}
registry={"pass":True,"register_rows":len(rows),"before":{"all":base_all,"vocabulary":base_vocab},"after":{"all":counts(rows),"vocabulary":counts(rows,"vocab")},"fixed_rechecked_ids":[int(x) for x in FIXED_IDS],"reviewed_ids":[int(x) for x in REVIEWED_IDS],"author_credit_before":3609,"author_credit_after":3621,"duplicate_keys":0,"records_deleted":0,"history_rewritten":False}
(WORK/"prepare-results.json").write_text(json.dumps(prepare,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(WORK/"registry-results.json").write_text(json.dumps(registry,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
cp=WORK/"checkpoint.json";d=json.loads(cp.read_text(encoding="utf-8"));d["status"]="author review complete; deterministic candidate and registry prepared; Chromium verification pending";d["candidate_sha256"]=digest;d["candidate_bytes"]=OUT.stat().st_size;d["exact_rollback"]=True;cp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"pass":True,"candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"fixed_rechecked":FIXED_IDS,"reviewed_without_change":REVIEWED_IDS,"updated_fields":len(UPDATES),"register_after":counts(rows),"vocabulary_after":counts(rows,"vocab")},ensure_ascii=False,indent=2))
