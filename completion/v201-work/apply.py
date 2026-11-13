import csv, hashlib, json, re
from pathlib import Path

BASE=Path("JLPT_N1_ukrainian_reading_v200.html")
OUT=Path("JLPT_N1_ukrainian_reading_v201.html")
WORK=Path("completion/v201-work")
REGISTER=Path("completion/review-register.csv")
BASE_SHA="d3563bf1f9601d8b87b5508e979116dfde07a8135cd46311d0626c8a1aac7d1a"

UPDATES=[
 ("1097","exampleTranslations[1]","Учитель-практик поділився досвідом зі студентами, які прагнуть працювати в освіті.","Учитель-практик поділився досвідом зі студентами, які прагнуть стати вчителями."),
 ("1100","m","感情が高ぶって、気持ちが落ち着かなくなること。","感情や神経などが高ぶり、心身が落ち着かなくなること。"),
 ("1102","exampleTranslations[1]","Перед дивами природи гостро усвідомлюєш, наскільки малі людські справи.","Перед дивами природи усвідомлюєш, якими незначними здаються людські зусилля."),
 ("1105","exampleTranslations[0]","Місцева влада призупинила діяльність підприємця, який вчинив порушення.","Місцева влада призупинила діяльність суб’єкта господарювання, який вчинив порушення.")
]
EXPECTED={
 "1097":("教職","きょうしょく",["名詞"]),
 "1100":("興奮","こうふん",["名詞"]),
 "1102":("驚異","きょうい",["名詞"]),
 "1105":("業者","ぎょうしゃ",["名詞"])
}
EXPECTED_EXAMPLES={
 "1097":["彼は大学卒業後、教職に就いて三十年以上を生徒の指導に捧げた。","教職を志す学生に向け、現場の教員が体験談を語った。"],
 "1100":["優勝が決まった瞬間、観客は興奮して総立ちになった。","興奮した群衆を鎮めるため、警備員が急いで駆けつけた。"],
 "1102":["この都市の復興の速さは、世界中の専門家にとって驚異であった。","自然の驚異を前に、人間の営みの小ささを思い知らされる。"],
 "1105":["不正を働いた業者に対して、自治体は営業停止の処分を下した。","工事を請け負う業者を選ぶ際は、実績を慎重に確認すべきだ。"]
}
FIXED_IDS=["1097","1100","1102","1105"]
REVIEWED_IDS=[]
PENDING_IDS=[]
EXPECTED_CHANGED=FIXED_IDS
EVIDENCE="completion/v201-acceptance.tsv; JLPT_N1_v201_audit.md"

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
    if depth==0:return start,i+1,json.loads(source[start:i+1])
 raise RuntimeError("unterminated constant "+name)

def counts(rows,kind=None):
 selected=[r for r in rows if kind is None or r["kind"]==kind]
 out={s:sum(r["finalReview"]==s for r in selected) for s in ("reviewed","fixed_rechecked","pending")}
 out["total"]=len(selected)
 return out

WORK.mkdir(parents=True,exist_ok=True)
raw=BASE.read_bytes(); base_sha=hashlib.sha256(raw).hexdigest()
if base_sha!=BASE_SHA: raise RuntimeError("unexpected v200 base SHA-256: "+base_sha)
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
allowed={"1097":{"exampleTranslations"},"1100":{"m"},"1102":{"exampleTranslations"},"1105":{"exampleTranslations"}}
for cid in details:
 for field in before[cid]:
  if before[cid][field]!=details[cid][field] and field not in allowed.get(cid,set()):raise RuntimeError("unexpected field mutation "+cid+"."+field)
 if before[cid]["examples"]!=details[cid]["examples"]:raise RuntimeError("Japanese example changed "+cid)
literal=json.dumps(details,ensure_ascii=False,separators=(",",":"))
candidate=base[:ds]+literal+base[de:]
old="<title>JLPT N1 — ウクライナ語対応学習アプリ · v200</title>"
new="<title>JLPT N1 — ウクライナ語対応学習アプリ · v201</title>"
if candidate.count(old)!=1:raise RuntimeError("version title marker mismatch")
candidate=candidate.replace(old,new,1)
if candidate.replace(new,old,1).replace(literal,base[ds:de],1)!=base:raise RuntimeError("exact rollback failed")
protected={"DEFAULT_VOCAB":vocab,"GRAMMAR_DETAILS_BY_ID":grammar,"VOCAB_POS_BY_ID":pos,"VOCAB_AUDITED_PAIRS":pairs,"REVIEWED_MEANING_QUIZZES":meaning,"REVIEWED_READING_OPTIONS":reading,"VOCAB_KANA_EXAMPLE_TARGETS":kana,"REVIEWED_EXAMPLE_TARGETS":targets}
for name,original in protected.items():
 _,_,after=extract(candidate,name)
 if after!=original:raise RuntimeError("protected data changed "+name)
OUT.write_bytes(candidate.encode("utf-8")); digest=hashlib.sha256(OUT.read_bytes()).hexdigest()
rows=list(csv.DictReader(REGISTER.read_text(encoding="utf-8").splitlines()))
if len(rows)!=5847:raise RuntimeError("register row count mismatch")
base_all={"reviewed":3914,"fixed_rechecked":238,"pending":1695,"total":5847}
base_vocab={"reviewed":3345,"fixed_rechecked":237,"pending":332,"total":3914}
target_all={"reviewed":3914,"fixed_rechecked":242,"pending":1691,"total":5847}
target_vocab={"reviewed":3345,"fixed_rechecked":241,"pending":328,"total":3914}
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
prepare={"pass":True,"base_version":"v200","base_sha256":base_sha,"candidate_version":"v201","candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"vocabulary_records":len(vocab),"grammar_records":len(grammar),"lexical_pairs":len(pairs),"unique_vocabulary_ids":len({int(x["id"]) for x in vocab}),"review_scope":[1097,1100,1102,1105],"fixed_rechecked":[1097,1100,1102,1105],"reviewed_without_change":[],"updated_fields":len(UPDATES),"changed_cards":[int(x) for x in changed],"field_updates":[{"id":int(cid),"field":field,"before":old,"after":new} for cid,field,old,new in UPDATES],"author_credit_before":3582,"author_credit_addition":4,"author_credit_after":3586,"protected_unchanged":{k:True for k in protected},"japanese_examples_unchanged":True,"exact_rollback":True,"register_updated":True,"author_review_only":True}
registry={"pass":True,"register_rows":len(rows),"before":{"all":base_all,"vocabulary":base_vocab},"after":{"all":counts(rows),"vocabulary":counts(rows,"vocab")},"fixed_rechecked_ids":[1097,1100,1102,1105],"reviewed_ids":[],"author_credit_before":3582,"author_credit_after":3586,"duplicate_keys":0,"records_deleted":0,"history_rewritten":False}
(WORK/"prepare-results.json").write_text(json.dumps(prepare,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(WORK/"registry-results.json").write_text(json.dumps(registry,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
cp=WORK/"checkpoint.json"; d=json.loads(cp.read_text(encoding="utf-8"));d["status"]="author review complete; deterministic candidate and register prepared; Chromium verification pending";d["candidate_sha256"]=digest;d["candidate_bytes"]=OUT.stat().st_size;d["exact_rollback"]=True;cp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"pass":True,"candidate_sha256":digest,"candidate_bytes":OUT.stat().st_size,"fixed_rechecked":FIXED_IDS,"updated_fields":len(UPDATES),"register_after":counts(rows),"vocabulary_after":counts(rows,"vocab")},ensure_ascii=False,indent=2))
