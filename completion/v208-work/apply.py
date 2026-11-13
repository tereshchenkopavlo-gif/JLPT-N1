import csv,hashlib,json,re
from pathlib import Path
BASE=Path("JLPT_N1_ukrainian_reading_v207.html");OUT=Path("JLPT_N1_ukrainian_reading_v208.html")
WORK=Path("completion/v208-work");REGISTER=Path("completion/review-register.csv")
BASE_SHA="f27b47c33dd4b427cbdc36ac1a3f2b126a1656e36055d2598fc6a5bbcd5e526d"
UPDATES=[
 ("1378","m","他人の幸せや、すぐれた点を、うらやみねたむこと。","他人の幸せや優れた点をうらやみ、ねたむこと。また、恋愛関係などで相手の愛情や関心を他人に向けられることをねたむこと。"),
 ("1378","examples[0]","同僚の昇進を嫉妬するあまり、彼は不当な噂を流してしまった。","同僚の昇進に嫉妬するあまり、彼は不当な噂を流してしまった。"),
 ("1379","exampleTranslations[1]","Голос репортера, який вів репортаж із місця стихійного лиха, передавав напруженість ситуації.","Голос репортера, який вів репортаж із місця лиха, передавав напруженість ситуації."),
 ("1380","examples[0]","裁判所は、被告に対し、執行猶予をつけずに実刑を言い渡した。","裁判所は、被告人に対し、執行猶予をつけずに実刑を言い渡した。"),
 ("1380","exampleTranslations[0]","Суд призначив підсудному реальне покарання без умовного відстрочення його виконання.","Суд призначив підсудному реальний строк ув’язнення без умовного відстрочення."),
 ("1383","t","суть, справжня природа, фактично","реальний зміст, сутність; фактично, по суті"),
 ("1386","usage","実費を負担する: відшкодувати фактично понесені витрати. 実費で精算する: провести розрахунок за фактичною сумою.","実費を負担する: покривати фактичні витрати. 実費で精算する: проводити розрахунок за фактичною сумою."),
 ("1389","t","спілкування, товариськість, світське життя","спілкування, підтримання соціальних контактів; світське життя"),
 ("1390","t","вибачення, визнання своєї провини; する — просити вибачення","вибачення, прохання пробачити; する — просити вибачення"),
 ("1390","usage","相手に過失を謝罪する／謝罪の言葉: визнати провину й попросити вибачення. 陳謝 офіційніше, часто з поясненням; 謝る звичайніше в повсякденному мовленні.","相手に謝罪する／謝罪の言葉: попросити вибачення за свою провину чи образливий вчинок. Саме визнання провини без вибачення не є 謝罪. 深く передає силу вибачення, 誠意ある — щирість. 陳謝 офіційніше, часто з поясненням."),
 ("1396","exampleTranslations[1]","Як ключовий гравець команди, він веде за собою її лінію відбивачів.","Він є стрижневим гравцем команди й веде за собою її атакувальну ланку."),
 ("1401","exampleTranslations[0]","По всій країні частішають випадки шахрайства, коли в літніх людей хитрими способами виманюють гроші.","По всій країні один за одним трапляються випадки шахрайства, коли в літніх людей хитрими способами виманюють гроші."),
 ("1401","exampleTranslations[1]","Поліція розслідує справу, звернувши увагу на спосіб дій, дуже схожий на попередні злочини.","Поліція розслідує справу, звернувши увагу на спосіб дій, дуже схожий на той, що використовували в попередніх справах."),
 ("1405","usage","手数がかかる／お手数をおかけします: клопіт, потрібні дії. Читання てすう і てかず; у ввічливому お手数 звичайне てすう. У ґо та сьоґі також кількість ходів.","手数がかかる／お手数をおかけします: てすう — клопіт, витрати зусиль. 将棋・囲碁の手数: てかず — кількість ходів; в інших контекстах також кількість потрібних дій."),
 ("1405","exampleTranslations[0]","Перепрошуємо за клопіт і просимо повернути документи поштою.","Перепрошуємо за клопіт і просимо повернути документи."),
 ("1406","t","надбавка, доплата; медична допомога, лікування","забезпечення потрібним персоналом або ресурсами; надбавка, доплата; перша допомога, медична обробка травми"),
 ("1407","t","організовувати, готувати, влаштовувати","підготовка, організація, забезпечення необхідним; у 指名手配 — оголошення в розшук; 手配する — організовувати, забезпечувати")
]
EXPECTED={
 "1378":("嫉妬","しっと",["名詞"]),"1379":("実況","じっきょう",["名詞"]),
 "1380":("実刑","じっけい",["名詞"]),"1383":("実質","じっしつ",["名詞"]),
 "1386":("実費","じっぴ",["名詞"]),"1389":("社交","しゃこう",["名詞"]),
 "1390":("謝罪","しゃざい",["名詞"]),"1396":("主軸","しゅじく",["名詞"]),
 "1401":("手口","てぐち",["名詞"]),"1405":("手数","てすう／てかず",["名詞"]),
 "1406":("手当","てあて",["名詞"]),"1407":("手配","てはい",["名詞"])
}
BASE_EXAMPLES={
 "1378":["同僚の昇進を嫉妬するあまり、彼は不当な噂を流してしまった。","他人の成功に嫉妬する気持ちは、誰もが多少はもっているものだ。"],
 "1379":["試合の様子を、アナウンサーが興奮した口調で実況した。","災害の現場から実況する記者の声が、緊迫した状況を伝えていた。"],
 "1380":["裁判所は、被告に対し、執行猶予をつけずに実刑を言い渡した。","詐欺の罪に問われた男は、実刑を免れず、服役することになった。"],
 "1383":["この改革は、名ばかりのもので、実質的な変化はほとんど見られない。","実質賃金が下がり続けるなか、家計の負担は重くなる一方である。"],
 "1386":["出張にかかった交通費は、領収書をもとに、実費で精算される。","参加費には、会場の使用料など、運営の実費のみが含まれている。"],
 "1389":["営業職として、取引先との社交の場に、積極的に顔を出している。","彼は、社交的な性格で、初対面の人とも、すぐに打ち解けられる。"],
 "1390":["社長は、記者会見の場で、顧客に深く謝罪した。","誠意ある謝罪がなければ、傷ついた信頼は、決して元に戻らない。"],
 "1396":["輸出は、この国の経済成長を支える主軸の一つである。","彼は、チームの主軸として、打線を引っ張っている。"],
 "1401":["巧妙な手口で高齢者から金をだまし取る詐欺が、全国で相次いでいる。","警察は、過去の事件と酷似した手口に着目して捜査を進めている。"],
 "1405":["お手数をおかけしますが、書類のご返送をお願い申し上げます。","事務処理の手数を減らすため、申請手続きの電子化が進められている。"],
 "1406":["通勤手当や住宅手当など、各種手当の見直しが労使交渉の焦点となった。","負傷者は、現場で応急の手当を受けた後、病院へ搬送された。"],
 "1407":["出張に必要な航空券とホテルは、すでに総務部が手配している。","警察は、逃走した容疑者を全国に指名手配した。"]
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
if base_sha!=BASE_SHA:raise RuntimeError("unexpected v207 base SHA-256: "+base_sha)
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
allowed={"1378":{"m","examples"},"1379":{"exampleTranslations"},"1380":{"examples","exampleTranslations"},"1383":{"t"},"1386":{"usage"},"1389":{"t"},"1390":{"t","usage"},"1396":{"exampleTranslations"},"1401":{"exampleTranslations"},"1405":{"usage","exampleTranslations"},"1406":{"t"},"1407":{"t"}}
for cid in details:
 for field in before[cid]:
  if before[cid][field]!=details[cid][field] and field not in allowed.get(cid,set()):raise RuntimeError("unexpected field mutation "+cid+"."+field)
literal=json.dumps(details,ensure_ascii=False,separators=(",",":"));candidate=base[:ds]+literal+base[de:]
old="<title>JLPT N1 — ウクライナ語対応学習アプリ · v207</title>";new="<title>JLPT N1 — ウクライナ語対応学習アプリ · v208</title>"
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
base_all={"reviewed":3916,"fixed_rechecked":311,"pending":1620,"total":5847}
base_vocab={"reviewed":3347,"fixed_rechecked":310,"pending":257,"total":3914}
target_all={"reviewed":3916,"fixed_rechecked":323,"pending":1608,"total":5847}
target_vocab={"reviewed":3347,"fixed_rechecked":322,"pending":245,"total":3914}
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
 r["finalReview"]="fixed_rechecked";r["evidence"]="completion/v208-acceptance.tsv; JLPT_N1_v208_audit.md"
with REGISTER.open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=["kind","key","baselineLocation","finalReview","evidence"],lineterminator="\n");w.writeheader();w.writerows(rows)
if counts(rows)!=target_all or counts(rows,"vocab")!=target_vocab:raise RuntimeError("register target mismatch")
prepare={"pass":True,"base_version":"v207","base_sha256":base_sha,"candidate_version":"v208","candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"vocabulary_records":len(vocab),"grammar_records":len(grammar),"lexical_pairs":len(pairs),"unique_vocabulary_ids":len({int(x["id"]) for x in vocab}),"review_scope":[int(x) for x in FIXED_IDS],"fixed_rechecked":[int(x) for x in FIXED_IDS],"reviewed_without_change":[],"updated_fields":len(UPDATES),"changed_cards":[int(x) for x in changed],"field_updates":[{"id":int(cid),"field":field,"before":old,"after":new} for cid,field,old,new in UPDATES],"japanese_example_changes":[{"id":1378,"field":"examples[0]"},{"id":1380,"field":"examples[0]"}],"japanese_definition_changes":[{"id":1378,"field":"m"}],"author_credit_before":3657,"author_credit_addition":12,"author_credit_after":3669,"protected_unchanged":{k:True for k in protected},"exact_rollback":True,"register_updated":True,"author_review_only":True}
registry={"pass":True,"register_rows":len(rows),"before":{"all":base_all,"vocabulary":base_vocab},"after":{"all":counts(rows),"vocabulary":counts(rows,"vocab")},"fixed_rechecked_ids":[int(x) for x in FIXED_IDS],"reviewed_ids":[],"author_credit_before":3657,"author_credit_after":3669,"duplicate_keys":0,"records_deleted":0,"history_rewritten":False}
(WORK/"prepare-results.json").write_text(json.dumps(prepare,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(WORK/"registry-results.json").write_text(json.dumps(registry,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
cp=WORK/"checkpoint.json";d=json.loads(cp.read_text(encoding="utf-8"));d["status"]="author review complete; deterministic candidate and registry prepared; Chromium verification pending";d["candidate_sha256"]=digest;d["candidate_bytes"]=OUT.stat().st_size;d["exact_rollback"]=True;cp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"pass":True,"candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"fixed_rechecked":FIXED_IDS,"updated_fields":len(UPDATES),"register_after":counts(rows),"vocabulary_after":counts(rows,"vocab")},ensure_ascii=False,indent=2))
