import csv,hashlib,json,re
from pathlib import Path
BASE=Path("JLPT_N1_ukrainian_reading_v206.html");OUT=Path("JLPT_N1_ukrainian_reading_v207.html")
WORK=Path("completion/v207-work");REGISTER=Path("completion/review-register.csv")
BASE_SHA="c2ec95102d848b728d352393863fbb4604b29dec864950529cd93f7a5b4c56fd"
UPDATES=[
 ("1351","exampleTranslations[1]","Для стоматологічного лікування потрібні висококваліфікований лікар і сучасне обладнання.","Для стоматологічного лікування потрібні висококваліфікований лікар і найновіше обладнання."),
 ("1352","exampleTranslations[0]","Через раптову зміну ситуації нараду вирішили провести раніше запланованого.","Через різку зміну ситуації нараду вирішили провести раніше, ніж планували."),
 ("1352","exampleTranslations[1]","Уряд оголосив надзвичайний стан і попросив мешканців утриматися від виходів без нагальної потреби із дому.","Уряд оголосив надзвичайний стан і попросив мешканців не виходити з дому без нагальної потреби."),
 ("1353","t","справа, обставини","конкретне питання, обставина або предмет розгляду"),
 ("1353","exampleTranslations[0]","На нараді вирішили письмово повідомляти всім учасникам про ухвалені питання.","На нараді вирішили письмово повідомляти всіх учасників про ухвалені рішення."),
 ("1358","exampleTranslations[1]","Перебіг загоєння систематизували в записах.","Перебіг одужання задокументували."),
 ("1359","m","磁石の働きによって生じる、鉄などを引きつける性質。","磁石や電流の周囲に生じ、磁力を及ぼす性質や現象。"),
 ("1362","exampleTranslations[0]","Коли в ранньому дитинстві формується усвідомлення себе, дитина починає наполягати на власній волі.","Коли в ранньому дитинстві формується усвідомлення себе, дитина починає заявляти про власні бажання."),
 ("1363","m","捜査機関に犯人が誰であるか発覚する前に、自発的に自分の犯罪を申告して処分を求めること。","捜査機関に犯罪事実が発覚する前に、自発的に自分の犯罪を申告すること。"),
 ("1363","t","добровільне повідомлення правоохоронним органам про власний злочин до того, як стане відомо, хто його вчинив; する — з’явитися з повинною","добровільне повідомлення правоохоронним органам про власний злочин до того, як їм стало відомо про сам злочин; 自首する — з’явитися з повинною"),
 ("1363","usage","捜査機関に犯人が特定される前の申告。出頭するだけでは自首とは限らない。","捜査機関に犯罪事実が発覚する前の申告が要件。犯罪自体が既に発覚していれば、犯人が特定されていなくても自首とは限らない。単に出頭することとも区別する。"),
 ("1370","exampleTranslations[0]","На пресконференції міністр повідомив, що має намір подати у відставку, беручи відповідальність за підозри навколо нього.","На пресконференції міністр заявив, що має намір подати у відставку, взявши на себе відповідальність за ситуацію, пов’язану з підозрами."),
 ("1372","usage","判決・予算を執行する: рішення або бюджет виконати на практиці. 実行 — здійснення плану чи дії; 執行 частіше має офіційний, інституційний відтінок。","判決・予算を執行する: рішення або бюджет виконати на практиці. 執行部 у другому прикладі — складне слово на позначення виконавчого органу, а не форма дієслова 執行する. 実行 — здійснення плану чи дії; 執行 частіше має офіційний, інституційний відтінок。"),
 ("1373","t","прив’язаність, впертість, одержимість","надмірна прив’язаність, чіпляння за щось, одержимість"),
 ("1375","m","資格や条件を、失うこと。","資格や条件を失い、参加・任務などに適さないと判断されること。"),
 ("1375","t","дискваліфікація, бути дискваліфікованим, непридатний","дискваліфікація; невідповідність вимогам; 失格になる — бути дискваліфікованим")
]
EXPECTED={
 "1351":("歯科","しか",["名詞"]),"1352":("事態","じたい",["名詞"]),
 "1353":("事柄","ことがら",["名詞"]),"1354":("児童","じどう",["名詞"]),
 "1358":("治癒","ちゆ",["名詞"]),"1359":("磁気","じき",["名詞"]),
 "1362":("自我","じが",["名詞"]),"1363":("自首","じしゅ",["名詞"]),
 "1370":("辞任","じにん",["名詞"]),"1372":("執行","しっこう",["名詞"]),
 "1373":("執着","しゅうちゃく",["名詞"]),"1375":("失格","しっかく",["名詞"])
}
BASE_EXAMPLES={
 "1351":["歯科医の不足に悩む地域では、巡回診療の重要性が高まっている。","歯科の治療には、技術の高い医師と、最新の設備が欠かせない。"],
 "1352":["事態が急変したため、会議は予定より早く開催されることになった。","政府は非常事態を宣言し、住民に不要不急の外出を控えるよう呼びかけた。"],
 "1353":["会議で決定した事柄は、すべて書面で参加者に通知することになった。","事実と意見を区別し、事柄を客観的に整理する必要がある。"],
 "1354":["少子化により、地方では児童の数が年々減少の一途をたどっている。","児童の安全を守るため、地域住民が通学路の見守り活動を行っている。"],
 "1358":["治癒には時間がかかるため、医師の指示に従って療養を続ける必要がある。","治癒までの経過を、記録にまとめた。"],
 "1359":["強い磁気を帯びた物体は、周囲の電子機器に影響を与えることがある。","磁気の影響を避けるため、精密機器は専用のケースに保管されている。"],
 "1362":["幼児期に自我が形成されると、子どもは自分の意思を主張し始める。","自我を抑え、他人の意見を受け入れることも、時には必要である。"],
 "1363":["容疑者は、警察に自首して事件の全容を明らかにした。","自首した場合、刑が軽くなることがある。"],
 "1370":["大臣は、自らの疑惑の責任をとって辞任する意向を、記者会見で表明した。","社長の突然の辞任を受け、取締役会は後任人事を急いだ。"],
 "1372":["刑が執行されるまで、被告人は拘置所で過ごした。","理事会が決定した方針を、執行部が速やかに実行に移した。"],
 "1373":["過去に執着すると、新しい一歩を踏み出せなくなることがある。","彼は結果に執着しすぎて、周囲の助言を聞かなくなった。"],
 "1375":["規定違反が判明し、その選手は大会で失格となった。","必要な資格を持たない者は、この職務において失格とみなされる。"]
}
FIXED_IDS=["1351","1352","1353","1358","1359","1362","1363","1370","1372","1373","1375"]
REVIEWED_IDS=["1354"]
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
if base_sha!=BASE_SHA:raise RuntimeError("unexpected v206 base SHA-256: "+base_sha)
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
allowed={"1351":{"exampleTranslations"},"1352":{"exampleTranslations"},"1353":{"t","exampleTranslations"},"1358":{"exampleTranslations"},"1359":{"m"},"1362":{"exampleTranslations"},"1363":{"m","t","usage"},"1370":{"exampleTranslations"},"1372":{"usage"},"1373":{"t"},"1375":{"m","t"}}
for cid in details:
 for field in before[cid]:
  if before[cid][field]!=details[cid][field] and field not in allowed.get(cid,set()):raise RuntimeError("unexpected field mutation "+cid+"."+field)
 if cid in BASE_EXAMPLES and before[cid]["examples"]!=details[cid]["examples"]:raise RuntimeError("unexpected Japanese example change "+cid)
literal=json.dumps(details,ensure_ascii=False,separators=(",",":"));candidate=base[:ds]+literal+base[de:]
old="<title>JLPT N1 — ウクライナ語対応学習アプリ · v206</title>";new="<title>JLPT N1 — ウクライナ語対応学習アプリ · v207</title>"
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
base_all={"reviewed":3915,"fixed_rechecked":300,"pending":1632,"total":5847}
base_vocab={"reviewed":3346,"fixed_rechecked":299,"pending":269,"total":3914}
target_all={"reviewed":3916,"fixed_rechecked":311,"pending":1620,"total":5847}
target_vocab={"reviewed":3347,"fixed_rechecked":310,"pending":257,"total":3914}
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
 r["finalReview"]="fixed_rechecked";r["evidence"]="completion/v207-acceptance.tsv; JLPT_N1_v207_audit.md"
for cid in REVIEWED_IDS:
 r=bykey[cid][0]
 if r["finalReview"]!="pending" or r["evidence"]:raise RuntimeError("register preimage mismatch "+cid)
 r["finalReview"]="reviewed";r["evidence"]="completion/v207-acceptance.tsv; JLPT_N1_v207_audit.md"
with REGISTER.open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=["kind","key","baselineLocation","finalReview","evidence"],lineterminator="\n");w.writeheader();w.writerows(rows)
if counts(rows)!=target_all or counts(rows,"vocab")!=target_vocab:raise RuntimeError("register target mismatch")
prepare={"pass":True,"base_version":"v206","base_sha256":base_sha,"candidate_version":"v207","candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"vocabulary_records":len(vocab),"grammar_records":len(grammar),"lexical_pairs":len(pairs),"unique_vocabulary_ids":len({int(x["id"]) for x in vocab}),"review_scope":[int(x) for x in EXPECTED],"fixed_rechecked":[int(x) for x in FIXED_IDS],"reviewed_without_change":[int(x) for x in REVIEWED_IDS],"updated_fields":len(UPDATES),"changed_cards":[int(x) for x in changed],"field_updates":[{"id":int(cid),"field":field,"before":old,"after":new} for cid,field,old,new in UPDATES],"japanese_example_changes":[],"japanese_definition_changes":[{"id":1359,"field":"m"},{"id":1363,"field":"m"},{"id":1375,"field":"m"}],"author_credit_before":3645,"author_credit_addition":12,"author_credit_after":3657,"protected_unchanged":{k:True for k in protected},"exact_rollback":True,"register_updated":True,"author_review_only":True}
registry={"pass":True,"register_rows":len(rows),"before":{"all":base_all,"vocabulary":base_vocab},"after":{"all":counts(rows),"vocabulary":counts(rows,"vocab")},"fixed_rechecked_ids":[int(x) for x in FIXED_IDS],"reviewed_ids":[int(x) for x in REVIEWED_IDS],"author_credit_before":3645,"author_credit_after":3657,"duplicate_keys":0,"records_deleted":0,"history_rewritten":False}
(WORK/"prepare-results.json").write_text(json.dumps(prepare,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(WORK/"registry-results.json").write_text(json.dumps(registry,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
cp=WORK/"checkpoint.json";d=json.loads(cp.read_text(encoding="utf-8"));d["status"]="author review complete; deterministic candidate and registry prepared; Chromium verification pending";d["candidate_sha256"]=digest;d["candidate_bytes"]=OUT.stat().st_size;d["exact_rollback"]=True;cp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"pass":True,"candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"fixed_rechecked":FIXED_IDS,"reviewed_without_change":REVIEWED_IDS,"updated_fields":len(UPDATES),"register_after":counts(rows),"vocabulary_after":counts(rows,"vocab")},ensure_ascii=False,indent=2))
