import csv,hashlib,json,re
from pathlib import Path
BASE=Path("JLPT_N1_ukrainian_reading_v208.html");OUT=Path("JLPT_N1_ukrainian_reading_v209.html")
WORK=Path("completion/v209-work");REGISTER=Path("completion/review-register.csv")
BASE_SHA="335f24392a24c895e14d60c306b63568804ab3713865b4c212e37baa4ec087ee"
UPDATES=[
 ("1408","s","手薄い|不十分","人手不足|不十分"),
 ("1408","usage","警備が手薄だ／手薄な体制: бракує людей, засобів або уваги. Приєднання な. Не описує фізичну тонкість долоні; 不十分 ширше й не завжди передає брак ресурсів.","警備が手薄だ／手薄な体制: бракує людей, засобів або уваги. У ролі присудка — 手薄だ, перед іменником — 手薄な. 人手不足 прямо називає нестачу персоналу; 不十分 ширше й не завжди передає брак ресурсів."),
 ("1413","t","приймати (заяву), офіційно отримувати, опрацьовувати","офіційне прийняття документа до розгляду; 受理する — офіційно приймати заяву або документ"),
 ("1415","exampleTranslations[0]","Відзначаючи багаторічні наукові заслуги, університет присвоїв йому звання почесного доктора.","Відзначаючи багаторічні наукові заслуги, університет присудив йому почесний докторський ступінь."),
 ("1417","exampleTranslations[0]","Партії правлячої коаліції поспішають узгодити створення стабільного уряду.","Партії правлячої коаліції поспішають узгодити формування стабільного уряду."),
 ("1417","s","確立|樹てる","確立|打ち立てる"),
 ("1419","t","збирати врожай, жати, врожай","урожай, збирання врожаю; здобутий результат; 収穫する — збирати врожай"),
 ("1421","t","збирання, колекціонування; する — збирати","збирання, колекціонування; 収集する — збирати, накопичувати"),
 ("1423","t","упорядкування, зведення до певного результату; する — стабілізуватися, сходитися","вщухання, стабілізація; збіжність (матем.); 収束する — стабілізуватися, сходитися"),
 ("1426","t","пошук роботи, шукати роботу","пошук роботи (переважно першої); 就活する — шукати роботу"),
 ("1427","usage","就業時間／業務に就業する: здійснювати трудову діяльність, працювати. 就職 — отримати місце роботи; 就業 може описувати стан зайнятості після працевлаштування.","就業する／就業時間／就業規則: працювати, робочий час, правила трудового розпорядку. 業務に従事する — виконувати службові обов’язки. 就職 — отримати місце роботи; 就業 — здійснювати трудову діяльність."),
 ("1431","t","означення іншого слова в граматиці; прикрашання; する — означувати, прикрашати","граматичне означення, модифікація (уточнення іншого слова); оздоблення, прикрашання; 修飾する — означувати, уточнювати, прикрашати"),
 ("1436","t","від початку до кінця, послідовно","від початку до кінця; обмежуватися чимось (〜に終始する)"),
 ("1443","t","утворювати затор, затор (на дорозі), затримуватися","затор, уповільнення руху; 道路が渋滞する — на дорозі виникає затор")
]
EXPECTED={
 "1408":("手薄","てうす",["名詞","ナ形"]),"1413":("受理","じゅり",["名詞"]),
 "1415":("授与","じゅよ",["名詞"]),"1417":("樹立","じゅりつ",["名詞"]),
 "1419":("収穫","しゅうかく",["名詞"]),"1421":("収集","しゅうしゅう",["名詞"]),
 "1423":("収束","しゅうそく",["名詞"]),"1426":("就活","しゅうかつ",["名詞"]),
 "1427":("就業","しゅうぎょう",["名詞"]),"1431":("修飾","しゅうしょく",["名詞"]),
 "1436":("終始","しゅうし",["名詞"]),"1443":("渋滞","じゅうたい",["名詞"])
}
BASE_EXAMPLES={
 "1408":["繁忙期は現場の人員が手薄になり、対応の遅れが懸念されている。","夜間の警備が手薄な地域では、空き巣の被害が増加している。"],
 "1413":["提出された申請書は、不備がなければ速やかに受理される。","裁判所は、遺族による再審の請求を受理した。"],
 "1415":["大学は、長年の研究功績を称え、同氏に名誉博士号を授与した。","卒業式では、代表者に学位記が授与される予定である。"],
 "1417":["連立与党は、安定した政権を樹立するための協議を急いでいる。","彼女は世界新記録を樹立し、日本中に大きな感動を与えた。"],
 "1419":["今年は天候に恵まれ、例年より早く稲を収穫することができた。","今回の視察では、新たな提携先の確保という大きな収穫があった。"],
 "1421":["顧客の声を収集し、サービスの改善に役立てる取り組みを進めている。","各地の民話を収集した資料が、図書館に寄贈された。"],
 "1423":["政府は、混乱の収束に向けて関係各国との調整を急いでいる。","騒動が収束するまでには、なお相当の時間を要する見通しだ。"],
 "1426":["学生の就活は年々早期化しており、大学側も支援体制を強化している。","彼は大学三年の夏から就活を始め、秋には内定を得た。"],
 "1427":["就業規則に違反した場合は、懲戒処分の対象となることがある。","育児をしながら就業する人を支援する制度が、拡充されつつある。"],
 "1431":["形容詞は名詞を修飾し、その性質や状態を詳しく説明する働きをもつ。","過度に修飾した表現は、かえって文章の主旨をぼやけさせてしまう。"],
 "1436":["会談は終始、和やかな雰囲気のなかで行われた。","彼は質問に対し、終始一貫して同じ主張を繰り返した。"],
 "1443":["事故の影響で、高速道路は三十キロにわたって渋滞している。","手続きが渋滞し、書類の処理に通常の倍の日数を要している。"]
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
if base_sha!=BASE_SHA:raise RuntimeError("unexpected v208 base SHA-256: "+base_sha)
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
 if field=="s":
  if details[cid]["s"]!=old.split("|"):raise RuntimeError("preimage mismatch "+cid+".s")
  details[cid]["s"]=new.split("|")
 elif "[" in field:
  key=field.split("[")[0];i=int(re.search(r"\[(\d+)\]",field).group(1))
  if details[cid][key][i]!=old:raise RuntimeError("preimage mismatch "+cid+"."+field)
  details[cid][key][i]=new
 else:
  if details[cid][field]!=old:raise RuntimeError("preimage mismatch "+cid+"."+field)
  details[cid][field]=new
changed=sorted((cid for cid in details if details[cid]!=before[cid]),key=int)
if changed!=sorted(FIXED_IDS,key=int):raise RuntimeError("changed-card set mismatch "+str(changed))
allowed={"1408":{"s","usage"},"1413":{"t"},"1415":{"exampleTranslations"},"1417":{"exampleTranslations","s"},"1419":{"t"},"1421":{"t"},"1423":{"t"},"1426":{"t"},"1427":{"usage"},"1431":{"t"},"1436":{"t"},"1443":{"t"}}
for cid in details:
 for field in before[cid]:
  if before[cid][field]!=details[cid][field] and field not in allowed.get(cid,set()):raise RuntimeError("unexpected field mutation "+cid+"."+field)
literal=json.dumps(details,ensure_ascii=False,separators=(",",":"));candidate=base[:ds]+literal+base[de:]
old="<title>JLPT N1 — ウクライナ語対応学習アプリ · v208</title>";new="<title>JLPT N1 — ウクライナ語対応学習アプリ · v209</title>"
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
base_all={"reviewed":3916,"fixed_rechecked":323,"pending":1608,"total":5847}
base_vocab={"reviewed":3347,"fixed_rechecked":322,"pending":245,"total":3914}
target_all={"reviewed":3916,"fixed_rechecked":335,"pending":1596,"total":5847}
target_vocab={"reviewed":3347,"fixed_rechecked":334,"pending":233,"total":3914}
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
 r["finalReview"]="fixed_rechecked";r["evidence"]="completion/v209-acceptance.tsv; JLPT_N1_v209_audit.md"
with REGISTER.open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=["kind","key","baselineLocation","finalReview","evidence"],lineterminator="\n");w.writeheader();w.writerows(rows)
if counts(rows)!=target_all or counts(rows,"vocab")!=target_vocab:raise RuntimeError("register target mismatch")
prepare={"pass":True,"base_version":"v208","base_sha256":base_sha,"candidate_version":"v209","candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"vocabulary_records":len(vocab),"grammar_records":len(grammar),"lexical_pairs":len(pairs),"unique_vocabulary_ids":len({int(x["id"]) for x in vocab}),"review_scope":[int(x) for x in FIXED_IDS],"fixed_rechecked":[int(x) for x in FIXED_IDS],"reviewed_without_change":[],"updated_fields":len(UPDATES),"changed_cards":[int(x) for x in changed],"field_updates":[{"id":int(cid),"field":field,"before":old,"after":new} for cid,field,old,new in UPDATES],"japanese_example_changes":[],"japanese_definition_changes":[],"author_credit_before":3669,"author_credit_addition":12,"author_credit_after":3681,"protected_unchanged":{k:True for k in protected},"exact_rollback":True,"register_updated":True,"author_review_only":True}
registry={"pass":True,"register_rows":len(rows),"before":{"all":base_all,"vocabulary":base_vocab},"after":{"all":counts(rows),"vocabulary":counts(rows,"vocab")},"fixed_rechecked_ids":[int(x) for x in FIXED_IDS],"reviewed_ids":[],"author_credit_before":3669,"author_credit_after":3681,"duplicate_keys":0,"records_deleted":0,"history_rewritten":False}
(WORK/"prepare-results.json").write_text(json.dumps(prepare,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(WORK/"registry-results.json").write_text(json.dumps(registry,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
cp=WORK/"checkpoint.json";d=json.loads(cp.read_text(encoding="utf-8"));d["status"]="author review complete; deterministic candidate and registry prepared; Chromium verification pending";d["candidate_sha256"]=digest;d["candidate_bytes"]=OUT.stat().st_size;d["exact_rollback"]=True;cp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"pass":True,"candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"fixed_rechecked":FIXED_IDS,"updated_fields":len(UPDATES),"register_after":counts(rows),"vocabulary_after":counts(rows,"vocab")},ensure_ascii=False,indent=2))
