import csv,hashlib,json,re
from pathlib import Path
BASE=Path("JLPT_N1_ukrainian_reading_v214.html")
OUT=Path("JLPT_N1_ukrainian_reading_v215.html")
WORK=Path("completion/v215-work")
REGISTER=Path("completion/review-register.csv")
BASE_SHA="0436bb8dc402e85eab47c442e094c1b725c3e97302500f559bd5b1fe944225b8"
UPDATES=[
 ("1019","exampleTranslations[0]","Працюючи з добре знайомими товаришами, значно легше порозумітися.","Коли працюєш із товаришами, чию вдачу добре знаєш, порозумітися значно легше."),
 ("1028","exampleTranslations[0]","Від державних службовців очікують високих етичних стандартів, щоб вони були прикладом для суспільства.","Від державних службовців вимагають високих етичних норм, що слугують взірцем для суспільства."),
 ("1078","exampleTranslations[0]","Це маленьке рибацьке село сповнене туристів, які приїздять по свіжі морепродукти.","У цьому маленькому рибальському селі людно через туристів, які приїздять сюди за свіжими морепродуктами."),
 ("1078","exampleTranslations[1]","У рибацьких селах, де скорочується населення, гостро стоїть проблема пошуку наступників.","У рибальських селах, де населення скорочується, гостро стоїть проблема залучення людей, які продовжать рибальську справу."),
 ("1082","exampleTranslations[0]","Через затяжні дощі врожай рису цього року виявився поганим.","Через затяжні дощі цього року був неврожай рису."),
 ("1089","exampleTranslations[1]","Через продовження будівництва попри негоду виникли побоювання за безпеку працівників.","Будівельні роботи провели попри негоду, що викликало занепокоєння щодо безпеки працівників."),
 ("1093","t","масова паніка; в економіці — тяжка фінансова криза (世界恐慌 — Велика депресія)","паніка; в економіці — тяжка фінансова криза (世界恐慌／世界大恐慌 — Велика депресія)"),
 ("1191","exampleTranslations[0]","У цій зоні суворо заборонено відкритий вогонь, тому куріння категорично не допускається.","У цій зоні суворо заборонено користуватися будь-якими джерелами займання, тому куріння категорично не допускається."),
 ("1255","t","злиття двох або кількох компаній, організацій чи адміністративних одиниць в одну (合併する — об’єднуватися)","злиття двох або кількох компаній, організацій чи адміністративних одиниць в одну; у медицині — поєднання з іншим захворюванням (合併する — об’єднуватися/поєднуватися)"),
 ("1258","exampleTranslations[1]","Потерпілий подав кримінальну скаргу проти недобросовісного підприємця за підозрою в шахрайстві.","Потерпілий подав кримінальну скаргу проти недобросовісного суб’єкта господарювання за підозрою в шахрайстві."),
 ("1260","exampleTranslations[0]","У парламенті розгорнулися дебати щодо належного обсягу й структури оборонного бюджету.","У парламенті розгорнулися дебати щодо того, яким має бути бюджет на національну оборону."),
 ("1270","exampleTranslations[1]","У хаотичній ситуації з суперечливою інформацією працівники на місцях були поглинуті невідкладними діями.","За хаотичної ситуації, коли інформація надходила безладно, працівники на місцях ледве встигали реагувати."),
 ("1272","exampleTranslations[0]","Різницю між кошторисом і фактичними витратами буде остаточно врегульовано пізніше.","Різницю між кошторисом і фактичними витратами остаточно розрахують пізніше.")
 ("1276","exampleTranslations[1]","Його розвинула готовність не здаватися після першої невдачі й наполегливо продовжувати спроби.","Він не здався після першої невдачі й наполегливо продовжив спроби — саме це допомогло йому зрости."),
 ("1280","usage","再三注意する／再三の要請／再三にわたって. Кілька разів, а не рівно два чи три. Часто з проханнями й попередженнями. Прислівникове вживання; 採算 — омонім про окупність.","再三注意する／再三の要請／再三にわたって. У словниках 再三 подають як іменник, але часто вживають прислівниково. 採算 — омонім про окупність."),
 ("1285","exampleTranslations[0]","Цей маршрут не окупається, і лунають думки, що його закриття неминуче.","Ця лінія не окупається, тож лунають думки, що її, можливо, доведеться скасувати."),
 ("1290","exampleTranslations[1]","Через багато років жителі громади відродили традиційне свято, яке було занепало.","Минуло багато років, і місцеві жителі відродили традиційне свято, яке вже перестали проводити."),
 ("1292","t","бактерія, одноклітинний мікроорганізм; не будь-який «мікроб» і не вірус","бактерія — представник групи прокаріотів; зазвичай одноклітинний мікроорганізм, не вірус"),
 ("1292","m","細胞内に核膜で囲まれた核を持たない微小な生物の一群。病気を引き起こすものも、人に役立つものもある。","細胞核を持たない原核生物の一群。古細菌とは別の生物群に属し、多くは単細胞からなる。病気を引き起こすものも、人に役立つものもある。"),
 ("1293","m","手先を使って、細かい物を作ること。また、人をあざむくための手段。","手先を使って、細かい物を作ること。また、そのようにして作った物。さらに、細かなところに手を加えて見た目を整えたり、人を欺いたりすること、そのたくらみ。"),
 ("1296","exampleTranslations[1]","У цій компанії розмір виплати при звільненні визначають залежно від тривалості роботи.","У цій компанії розмір виплати після завершення роботи визначають залежно від стажу.")
]
EXPECTED={
 "1019":("気心","きごころ",["名詞"]),
 "1028":("規範","きはん",["名詞"]),
 "1078":("漁村","ぎょそん",["名詞"]),
 "1082":("凶作","きょうさく",["名詞"]),
 "1089":("強行","きょうこう",["名詞"]),
 "1093":("恐慌","きょうこう",["名詞"]),
 "1191":("厳禁","げんきん",["名詞"]),
 "1255":("合併","がっぺい",["名詞"]),
 "1258":("告訴","こくそ",["名詞"]),
 "1260":("国防","こくぼう",["名詞"]),
 "1270":("混沌","こんとん",["名詞"]),
 "1272":("差額","さがく",["名詞"]),

 "1276":("挫折","ざせつ",["名詞"]),
 "1280":("再三","さいさん",["名詞"]),
 "1285":("採算","さいさん",["名詞"]),
 "1290":("歳月","さいげつ",["名詞"]),
 "1292":("細菌","さいきん",["名詞"]),
 "1293":("細工","さいく",["名詞"]),
 "1296":("在職","ざいしょく",["名詞"])
}
BASE_EXAMPLES={
 "1019":["気心の知れた仲間と仕事をすると、意思疎通が格段にしやすくなる。","長い付き合いなので、彼の気心はよく知っている。"],
 "1028":["公務員には、社会の模範となる高い倫理規範が求められる。","社会規範から逸脱した行為に、世間は厳しい目を向けた。"],
 "1078":["この小さな漁村は、新鮮な海産物を求める観光客でにぎわっている。","過疎化の進む漁村では、後継者の確保が深刻な課題となっている。"],
 "1082":["長雨の影響で、今年の稲作は凶作となった。","凶作が続いた結果、農家の生活は一段と苦しくなった。"],
 "1089":["与党は、反対を押し切って採決を強行する姿勢を崩さなかった。","悪天候の中で工事を強行したため、作業員の安全が懸念された。"],
 "1093":["金融恐慌を題材にした本を読み、経済の仕組みを学んだ。","銀行の破綻が連鎖すれば、金融恐慌に発展しかねない。"],
 "1191":["この区域は火気厳禁のため、喫煙は固くお断りいたします。","情報の持ち出しは、社内規則で厳禁とされている。"],
 "1255":["二つの地方銀行が合併して、地域最大規模の金融機関が誕生した。","市町村の合併により、行政サービスの効率化が進んだとされる。"],
 "1258":["会社は、機密情報を漏らした元社員を告訴する方針を明らかにした。","被害者は、悪質な業者を詐欺の疑いで告訴した。"],
 "1260":["国防に関する予算の在り方をめぐって、国会で論戦が繰り広げられた。","国防を担う人材の育成は、どの国にとっても重要な課題である。"],
 "1270":["政局は混沌としており、今後の展開を見通すことは難しい。","情報が錯綜する混沌とした状況の中で、現場は対応に追われた。"],
 "1272":["見積もりと実際の費用との差額は、後日あらためて精算される。","両社の入札価格の差額は、わずか数万円にとどまった."],

 "1276":["資金不足により、大型の開発計画は着工前に挫折した。","一度の挫折で諦めず、粘り強く挑戦を続ける姿勢が、彼を成長させた。"],
 "1280":["再三の注意にもかかわらず、事業者は表示の誤りを改めなかった。","再三にわたる要請を受け、役員会はようやく調査の実施を決めた。"],
 "1285":["この路線は採算が取れず、廃止もやむを得ないとの声が上がっている。","採算を度外視した価格設定は、長期的には経営を圧迫しかねない。"],
 "1290":["計画の実現までには、十数年の歳月と莫大な費用が費やされた。","長い歳月を経て、廃れていた伝統行事が地域住民の手で復活した。"],
 "1292":["授業では、発酵に役立つ細菌についても学んだ。","病院では、薬の効かない細菌への感染を防ぐ対策が徹底されている。"],
 "1293":["職人は、小さな木片を細工して、精巧な箱をつくり上げた。","帳簿に細工を施して、不正を隠そうとした疑いが持たれている。"],
 "1296":["彼は在職中、一貫して社員の働きやすい環境づくりに力を尽くした。","この会社では、在職期間に応じて退職金の額が決まる。"]
}
FIXED_IDS=[1019,1028,1078,1082,1089,1093,1191,1255,1258,1260,1270,1272,1276,1280,1285,1290,1292,1293,1296]
PAIR_KEYS=[]
def extract(source,name):
 m=re.search(r"\bconst "+re.escape(name)+r"\s*=\s*",source)
 if not m: raise RuntimeError("missing constant "+name)
 start=m.end(); opening=source[start]; closing="]" if opening=="[" else "}"
 depth=0; inside=False; escaped=False
 for i in range(start,len(source)):
  c=source[i]
  if inside:
   if escaped: escaped=False
   elif c=="\\": escaped=True
   elif c=='"': inside=False
  else:
   if c=='"': inside=True
   elif c==opening: depth+=1
   elif c==closing:
    depth-=1
    if depth==0: return start,i+1,json.loads(source[start:i+1]),source[start:i+1]
 raise RuntimeError("unterminated constant "+name)
def counts(rows,kind=None):
 sel=[r for r in rows if kind is None or r["kind"]==kind]
 out={s:sum(r["finalReview"]==s for r in sel) for s in ("reviewed","fixed_rechecked","pending")}
 out["total"]=len(sel)
 return out
WORK.mkdir(parents=True,exist_ok=True)
raw=BASE.read_bytes()
base_sha=hashlib.sha256(raw).hexdigest()
if base_sha!=BASE_SHA: raise RuntimeError("unexpected v214 base SHA-256: "+base_sha)
base=raw.decode("utf-8")
ds,de,details,dorig=extract(base,"VOCAB_DETAILS_BY_ID")
_,_,pos,posorig=extract(base,"VOCAB_POS_BY_ID")
_,_,vocab,_=extract(base,"DEFAULT_VOCAB")
_,_,grammar,_=extract(base,"GRAMMAR_DETAILS_BY_ID")
_,_,pairs,_=extract(base,"VOCAB_AUDITED_PAIRS")
_,_,meaning,_=extract(base,"REVIEWED_MEANING_QUIZZES")
_,_,reading,_=extract(base,"REVIEWED_READING_OPTIONS")
_,_,kana,_=extract(base,"VOCAB_KANA_EXAMPLE_TARGETS")
_,_,targets,_=extract(base,"REVIEWED_EXAMPLE_TARGETS")
if (len(vocab),len(grammar),len(details),len(pairs))!=(3914,130,3914,859): raise RuntimeError("protected inventory counts mismatch")
by_id={str(x["id"]):x for x in vocab}
for cid,(word,rd,p) in EXPECTED.items():
 if cid not in by_id or (by_id[cid]["w"],by_id[cid]["r"],pos[cid])!=(word,rd,p): raise RuntimeError("identity/POS preimage mismatch "+cid)
 if details[cid]["examples"]!=BASE_EXAMPLES[cid]: raise RuntimeError("Japanese example preimage mismatch "+cid)
before=json.loads(json.dumps(details,ensure_ascii=False))
for cid,field,old,new in UPDATES:
 if "[" in field:
  key=field.split("[")[0]; index=int(re.search(r"\[(\d+)\]",field).group(1))
  if details[cid][key][index]!=old: raise RuntimeError("preimage mismatch "+cid+"."+field)
  details[cid][key][index]=new
 else:
  if details[cid][field]!=old: raise RuntimeError("preimage mismatch "+cid+"."+field)
  details[cid][field]=new
changed=sorted((cid for cid in details if details[cid]!=before[cid]),key=int)
if changed!=sorted(map(str,FIXED_IDS),key=int): raise RuntimeError("changed-card set mismatch "+str(changed))
allowed={
 "1019":{"exampleTranslations"},
 "1028":{"exampleTranslations"},
 "1078":{"exampleTranslations"},
 "1082":{"exampleTranslations"},
 "1089":{"exampleTranslations"},
 "1093":{"t"},
 "1191":{"exampleTranslations"},
 "1255":{"t"},
 "1258":{"exampleTranslations"},
 "1260":{"exampleTranslations"},
 "1270":{"exampleTranslations"},
 "1272":{"exampleTranslations"},
 "1276":{"exampleTranslations"},
 "1280":{"usage"},
 "1285":{"exampleTranslations"},
 "1290":{"exampleTranslations"},
 "1292":{"t","m"},
 "1293":{"m"},
 "1296":{"exampleTranslations"}
}
for cid in details:
 for field in before[cid]:
  if before[cid][field]!=details[cid][field] and field not in allowed.get(cid,set()):
   raise RuntimeError("unexpected field mutation "+cid+"."+field)
details_literal=json.dumps(details,ensure_ascii=False,separators=(",",":"))
candidate=base[:ds]+details_literal+base[de:]
old="<title>JLPT N1 — ウクライナ語対応学習アプリ · v214</title>"
new="<title>JLPT N1 — ウクライナ語対応学習アプリ · v215</title>"
if candidate.count(old)!=1: raise RuntimeError("version title marker mismatch")
candidate=candidate.replace(old,new,1)
rollback=candidate.replace(new,old,1)
ds2,de2,_,_=extract(rollback,"VOCAB_DETAILS_BY_ID")
rollback=rollback[:ds2]+dorig+rollback[de2:]
if rollback!=base: raise RuntimeError("exact rollback failed")
protected={
 "DEFAULT_VOCAB":vocab,"GRAMMAR_DETAILS_BY_ID":grammar,"VOCAB_POS_BY_ID":pos,
 "VOCAB_AUDITED_PAIRS":pairs,"REVIEWED_MEANING_QUIZZES":meaning,
 "REVIEWED_READING_OPTIONS":reading,"VOCAB_KANA_EXAMPLE_TARGETS":kana,
 "REVIEWED_EXAMPLE_TARGETS":targets
}
for name,original in protected.items():
 _,_,after,_=extract(candidate,name)
 if after!=original: raise RuntimeError("protected data changed "+name)
OUT.write_bytes(candidate.encode("utf-8"))
digest=hashlib.sha256(OUT.read_bytes()).hexdigest()
rows=list(csv.DictReader(REGISTER.read_text(encoding="utf-8").splitlines()))
if len(rows)!=5847: raise RuntimeError("register row count mismatch")
base_all={"reviewed":3918,"fixed_rechecked":392,"pending":1537,"total":5847}
base_vocab={"reviewed":3347,"fixed_rechecked":390,"pending":177,"total":3914}
base_pairs={"reviewed":20,"fixed_rechecked":1,"pending":838,"total":859}
target_all={"reviewed":3918,"fixed_rechecked":411,"pending":1518,"total":5847}
target_vocab={"reviewed":3347,"fixed_rechecked":409,"pending":158,"total":3914}
target_pairs={"reviewed":20,"fixed_rechecked":1,"pending":838,"total":859}
keys=[(r["kind"],r["key"]) for r in rows]
if len(keys)!=len(set(keys)): raise RuntimeError("duplicate register keys")
cur=counts(rows); cv=counts(rows,"vocab"); cp=counts(rows,"vocab_pair")
if cur==base_all and cv==base_vocab and cp==base_pairs: state="baseline"
elif cur==target_all and cv==target_vocab and cp==target_pairs: state="already_applied"
else: raise RuntimeError("register is neither exact v214 baseline nor exact v215 target")
bykey={(r["kind"],r["key"]):r for r in rows}
if state=="baseline":
 for cid in FIXED_IDS:
  r=bykey.get(("vocab",str(cid)))
  if not r or r["finalReview"]!="pending" or r["evidence"]: raise RuntimeError("card register preimage mismatch "+str(cid))
  r["finalReview"]="fixed_rechecked"
  r["evidence"]="completion/v215-acceptance.tsv; JLPT_N1_v215_audit.md"
 for key in PAIR_KEYS:
  r=bykey.get(("vocab_pair",key))
  if not r or r["finalReview"]!="pending" or r["evidence"]: raise RuntimeError("pair register preimage mismatch "+key)
  r["finalReview"]="reviewed"
  r["evidence"]="completion/v215-pair-review.tsv; author review, not independent"
 with REGISTER.open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=["kind","key","baselineLocation","finalReview","evidence"],lineterminator="\n")
  w.writeheader(); w.writerows(rows)
else:
 for cid in FIXED_IDS:
  r=bykey[("vocab",str(cid))]
  if r["finalReview"]!="fixed_rechecked" or r["evidence"]!="completion/v215-acceptance.tsv; JLPT_N1_v215_audit.md":
   raise RuntimeError("already-applied card evidence mismatch "+str(cid))
 for key in PAIR_KEYS:
  r=bykey[("vocab_pair",key)]
  if r["finalReview"]!="reviewed" or r["evidence"]!="completion/v215-pair-review.tsv; author review, not independent":
   raise RuntimeError("already-applied pair evidence mismatch "+key)
if counts(rows)!=target_all or counts(rows,"vocab")!=target_vocab or counts(rows,"vocab_pair")!=target_pairs:
 raise RuntimeError("register target mismatch")
prepare={
 "pass":True,"base_version":"v214","base_sha256":base_sha,
 "candidate_version":"v215","candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,
 "vocabulary_records":len(vocab),"grammar_records":len(grammar),"lexical_pairs":len(pairs),
 "unique_vocabulary_ids":len({int(x["id"]) for x in vocab}),
 "review_scope":[int(x) for x in EXPECTED],
 "fixed_rechecked":[int(x) for x in FIXED_IDS],"pending_ids":[],"reviewed_ids":[],
 "updated_fields":len(UPDATES),"changed_cards":[int(x) for x in changed],
 "japanese_example_changes":[],"japanese_definition_changes": [1292,1293],
 "pos_map_unchanged":True,"comparison_pairs_unchanged":True,
 "pair_reviewed_indices":[],
 "author_credit_before":3737,"author_credit_addition":19,"author_credit_after":3756,
 "protected_unchanged":{k:True for k in protected},
 "exact_rollback":True,"register_state":state,"author_review_only":True
}
registry={
 "pass":True,"register_rows":len(rows),
 "before":{"all":base_all,"vocabulary":base_vocab,"vocab_pair":base_pairs},
 "after":{"all":counts(rows),"vocabulary":counts(rows,"vocab"),"vocab_pair":counts(rows,"vocab_pair")},
 "fixed_rechecked_ids":[int(x) for x in FIXED_IDS],"pending_ids":[],
 "reviewed_pair_keys":PAIR_KEYS,"duplicate_keys":0,"records_deleted":0,
 "history_rewritten":False,"idempotent_reuse":state=="already_applied"
}
(WORK/"prepare-results.json").write_text(json.dumps(prepare,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(WORK/"registry-results.json").write_text(json.dumps(registry,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
cp=WORK/"checkpoint.json"
d=json.loads(cp.read_text(encoding="utf-8"))
d["status"]="candidate and registry prepared; Chromium verification pending"
d["candidate_sha256"]=digest; d["candidate_bytes"]=OUT.stat().st_size; d["exact_rollback"]=True
cp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"pass":True,"candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"fixed_rechecked":FIXED_IDS,"pair_reviewed":PAIR_KEYS,"updated_fields":len(UPDATES),"register_after":{"all":counts(rows),"vocabulary":counts(rows,"vocab"),"vocab_pair":counts(rows,"vocab_pair")},"author_credit_after":3749},ensure_ascii=False,indent=2))
