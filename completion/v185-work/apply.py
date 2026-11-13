import hashlib,json,re
from pathlib import Path
BASE=Path("JLPT_N1_ukrainian_reading_v184.html")
OUT=Path("JLPT_N1_ukrainian_reading_v185.html")
WORK=Path("completion/v185-work")
BASE_SHA="e49a3103e5f02c38c8ac2e92917dd268d6f2cef8001373197c5398608fe2a1bd"
UPDATES=[
("525","t","випадати або виходити звідкись; бракувати в переліку; проходити наскрізь","випадати або виходити звідкись; бракувати в переліку; проходити наскрізь; помітно вирізнятися серед інших"),
("525","usage","歯・毛が抜ける — випадати; 項目が抜ける — бути пропущеним; 集団を抜ける — залишати групу; トンネルを抜ける — проходити наскрізь. Неперехідне дієслово може мати を для шляху чи виходу. 優れている передає перевагу загальніше, ніж 頭一つ抜けている.","歯・毛が抜ける — випадати; 項目が抜ける — бути пропущеним; 集団を抜ける — залишати групу; トンネルを抜ける — проходити наскрізь. 頭一つ抜けている — помітно вирізнятися серед інших, бути на голову вище. Неперехідне дієслово може мати を для шляху чи виходу."),
("530","m","穴や隙間に物を入れて満たす。不足分を補う。","うめる：穴や隙間に物を入れて満たす。不足分を補う。うずめる：物を土や灰などの中に入れて外から見えなくする。また、物や人で場所をいっぱいにする。"),
("533","m","一緒に行くように相手に呼びかける。ある行動や感情を引き起こす。","さそう：一緒に行動するように相手に呼びかける。また、ある気持ちや行動を引き起こす。いざなう：相手をある場所へ導くように誘い、連れて行く。"),
("533","usage","人を食事に誘う — запросити разом поїсти; 涙・笑いを誘う — викликати сльози чи сміх. Основне читання さそう; いざなう — літературний варіант, часто образний. 招く може бути офіційним запрошенням гостя; 誘う підкреслює залучення до дії.","人を食事に誘う — запросити разом поїсти; 涙・笑いを誘う — викликати сльози чи сміх. Обидва наведені приклади — читання さそう. いざなう — літературний варіант «вести, запрошуючи кудись», часто образний. 招く може бути офіційним запрошенням гостя; 誘う підкреслює залучення до дії."),
("540","t","робити щось холодним; охолоджувати напій чи тіло (перехідне)","охолоджувати напій чи тіло; переносно — охолодити голову, заспокоїтися (頭を冷やす)"),
("541","exampleTranslations[0]","Слова старшого колеги, який підбадьорив засмученого молодшого, стали для того поворотним моментом.","Одна фраза старшого колеги, який підбадьорив його, стала для нього поворотним моментом."),
("547","exampleTranslations[0]","Між висловленням думки з безтурботної позиції та ухваленням рішення під власну відповідальність є велика різниця.","Є велика різниця між тим, щоб висловлювати думку без особливого тягаря відповідальності, і тим, щоб ухвалювати рішення, за які відповідаєш."),
("549","t","такий, до якого легко приступити без церемоній або особливих зусиль","невимушений; такий, до якого легко звернутися чи долучитися без вагань і зайвих церемоній"),
("552","exampleTranslations[1]","Його впевнену майстерність широко визнають у галузі.","Його безсумнівну майстерність широко визнають у галузі."),
("563","m","手間や費用をかけずに行える様子。","手間や費用をあまりかけずに行える様子。")
]
EXPECTED={"525":("抜ける","ぬける",["動詞"]),"530":("埋める","うめる／うずめる",["動詞"]),"533":("誘う","さそう／いざなう",["動詞"]),"540":("冷やす","ひやす",["動詞"]),"541":("励ます","はげます",["動詞"]),"544":("いい加減","いいかげん",["ナ形"]),"547":("気楽","きらく",["ナ形"]),"549":("気軽","きがる",["ナ形"]),"550":("わがまま","わがまま",["ナ形"]),"552":("確か","たしか",["ナ形"]),"557":("結構","けっこう",["ナ形"]),"563":("手軽","てがる",["ナ形"])}
def extract(s,name):
 m=re.search(r"\bconst "+re.escape(name)+r"\s*=\s*",s)
 if not m: raise RuntimeError("missing "+name)
 st=m.end(); op=s[st]; cl="]" if op=="[" else "}"; depth=0; q=False; esc=False
 for i in range(st,len(s)):
  c=s[i]
  if q:
   if esc: esc=False
   elif c=="\\": esc=True
   elif c=='"': q=False
  else:
   if c=='"': q=True
   elif c==op: depth+=1
   elif c==cl:
    depth-=1
    if depth==0: return st,i+1,json.loads(s[st:i+1])
 raise RuntimeError("unterminated "+name)
raw=BASE.read_bytes(); base_sha=hashlib.sha256(raw).hexdigest()
if base_sha!=BASE_SHA: raise RuntimeError("unexpected v184 SHA "+base_sha)
base=raw.decode("utf-8")
_,_,vocab=extract(base,"DEFAULT_VOCAB"); _,_,grammar=extract(base,"GRAMMAR_DETAILS_BY_ID")
_,_,details=extract(base,"VOCAB_DETAILS_BY_ID"); _,_,pos=extract(base,"VOCAB_POS_BY_ID")
_,_,pairs=extract(base,"VOCAB_AUDITED_PAIRS"); _,_,meaning=extract(base,"REVIEWED_MEANING_QUIZZES")
_,_,reading=extract(base,"REVIEWED_READING_OPTIONS"); _,_,kana=extract(base,"VOCAB_KANA_EXAMPLE_TARGETS")
_,_,targets=extract(base,"REVIEWED_EXAMPLE_TARGETS")
if (len(vocab),len(grammar),len(details),len(pairs))!=(3914,130,3914,859): raise RuntimeError("base counts mismatch")
byid={str(x["id"]):x for x in vocab}
for cid,(w,r,p) in EXPECTED.items():
 if (byid[cid]["w"],byid[cid]["r"],pos[cid])!=(w,r,p): raise RuntimeError("identity/POS mismatch "+cid)
before=json.loads(json.dumps(details,ensure_ascii=False))
for cid,field,old,new in UPDATES:
 if field.startswith("exampleTranslations["):
  ix=int(field.split("[")[1].split("]")[0]); actual=details[cid]["exampleTranslations"][ix]
  if actual!=old: raise RuntimeError("preimage mismatch "+cid+"."+field)
  details[cid]["exampleTranslations"][ix]=new
 else:
  if details[cid][field]!=old: raise RuntimeError("preimage mismatch "+cid+"."+field)
  details[cid][field]=new
changed={k for k in details if details[k]!=before[k]}
if changed!={"525","530","533","540","541","547","549","552","563"}: raise RuntimeError("unexpected changed card set "+str(changed))
allowed={"525":{"t","usage"},"530":{"m"},"533":{"m","usage"},"540":{"t"},"541":{"exampleTranslations"},"547":{"exampleTranslations"},"549":{"t"},"552":{"exampleTranslations"},"563":{"m"}}
for cid in details:
 for f in before[cid]:
  if before[cid][f]!=details[cid][f] and f not in allowed.get(cid,set()): raise RuntimeError("unexpected field "+cid+"."+f)
 if before[cid]["examples"]!=details[cid]["examples"]: raise RuntimeError("Japanese example changed "+cid)
st,en,_=extract(base,"VOCAB_DETAILS_BY_ID")
literal=json.dumps(details,ensure_ascii=False,separators=(",",":"))
candidate=base[:st]+literal+base[en:]
old_title="<title>JLPT N1 — ウクライナ語対応学習アプリ · v184</title>"
new_title="<title>JLPT N1 — ウクライナ語対応学習アプリ · v185</title>"
if candidate.count(old_title)!=1: raise RuntimeError("title marker mismatch")
candidate=candidate.replace(old_title,new_title,1)
rollback=candidate.replace(new_title,old_title,1)
if rollback.count(literal)!=1: raise RuntimeError("rollback literal missing")
rollback=rollback.replace(literal,base[st:en],1)
if rollback!=base: raise RuntimeError("exact rollback failed")
for name,old in [("DEFAULT_VOCAB",vocab),("GRAMMAR_DETAILS_BY_ID",grammar),("VOCAB_POS_BY_ID",pos),("VOCAB_AUDITED_PAIRS",pairs),("REVIEWED_MEANING_QUIZZES",meaning),("REVIEWED_READING_OPTIONS",reading),("VOCAB_KANA_EXAMPLE_TARGETS",kana),("REVIEWED_EXAMPLE_TARGETS",targets)]:
 _,_,after=extract(candidate,name)
 if after!=old: raise RuntimeError("dependent constant changed "+name)
out=candidate.encode("utf-8"); OUT.write_bytes(out); digest=hashlib.sha256(out).hexdigest()
prepare={"pass":True,"base_version":"v184","base_sha256":base_sha,"base_bytes":len(raw),"candidate_version":"v185","candidate_sha256":digest,"candidate_bytes":len(out),"vocabulary_records":len(vocab),"grammar_records":len(grammar),"lexical_pairs":len(pairs),"unique_vocabulary_ids":len({int(x["id"]) for x in vocab}),"review_scope":[525,530,533,540,541,544,547,549,550,552,557,563],"author_credit_before":3411,"author_credit_addition":8,"author_credit_after":3419,"fixed_rechecked":[525,530,533,540,541,547,549,563],"pending_due_C11":[544,550,552,557],"field_updates":[{"id":int(cid),"field":f,"before":old,"after":new} for cid,f,old,new in UPDATES],"updated_fields":len(UPDATES),"changed_blocks":["VOCAB_DETAILS_BY_ID","document title"],"unchanged":{"vocabulary_records":True,"grammar_records":True,"lexical_pairs":True,"all_ids":True,"pos_map":True,"japanese_examples":True,"reading_quiz_targets":True,"meaning_quizzes":True,"reading_overrides":True,"example_targets":True,"learning_engine":True,"progress_storage_code":True},"exact_rollback":True,"author_review_only":True}
WORK.mkdir(parents=True,exist_ok=True)
(WORK/"prepare-results.json").write_text(json.dumps(prepare,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(prepare,ensure_ascii=False,indent=2))
