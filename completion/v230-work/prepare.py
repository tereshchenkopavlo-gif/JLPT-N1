import copy, hashlib, json, re
from pathlib import Path
BASE=Path("JLPT_N1_ukrainian_reading_v229.html")
OUT=Path("JLPT_N1_ukrainian_reading_v230.html")
W=Path("completion/v230-work")
BASE_SHA="e5e298e9f5efcf45c7cfd1fe83ab9ce5a19dcde13759482d54e3b8313bd92dab"
IDS=[3363,3375,3417,3441,3444,3525,3561,3565,3569,3594,3636,3646]
def extract(text,name):
    m=re.search(r"const\s+"+re.escape(name)+r"\s*=\s*",text)
    if not m: raise RuntimeError("missing "+name)
    start=m.end(); op=text[start]; cl="]" if op=="[" else "}"
    depth=0; quoted=False; escaped=False
    for i in range(start,len(text)):
        ch=text[i]
        if quoted:
            if escaped: escaped=False
            elif ch=="\\": escaped=True
            elif ch=='"': quoted=False
        elif ch=='"': quoted=True
        elif ch==op: depth+=1
        elif ch==cl:
            depth-=1
            if depth==0:return start,i+1,json.loads(text[start:i+1])
    raise RuntimeError("unterminated "+name)
def replace(text,name,value):
    a,b,_=extract(text,name)
    return text[:a]+json.dumps(value,ensure_ascii=False,separators=(",",":"))+text[b:]
base_bytes=BASE.read_bytes()
base_sha=hashlib.sha256(base_bytes).hexdigest()
if base_sha!=BASE_SHA: raise RuntimeError("unexpected v229 base SHA: "+base_sha)
base=base_bytes.decode("utf-8")
spec=json.loads((W/"payloads.json").read_text(encoding="utf-8"))
names=["DEFAULT_VOCAB","GRAMMAR_DETAILS_BY_ID","VOCAB_DETAILS_BY_ID","VOCAB_POS_BY_ID","VOCAB_AUDITED_PAIRS","REVIEWED_MEANING_QUIZZES","REVIEWED_READING_OPTIONS","VOCAB_KANA_EXAMPLE_TARGETS","REVIEWED_EXAMPLE_TARGETS"]
blocks={n:base[extract(base,n)[0]:extract(base,n)[1]] for n in names}
data={n:extract(base,n)[2] for n in names}
vocab=data["DEFAULT_VOCAB"]; grammar=data["GRAMMAR_DETAILS_BY_ID"]; details=data["VOCAB_DETAILS_BY_ID"]
pos=data["VOCAB_POS_BY_ID"]; pairs=data["VOCAB_AUDITED_PAIRS"]; quizzes=data["REVIEWED_MEANING_QUIZZES"]
if (len(vocab),len(grammar),len(details),len(pos),len(pairs))!=(3914,130,3914,3914,859): raise RuntimeError("record counts mismatch")
by={str(x["id"]):x for x in vocab}
expected={
"3363":("相当","そうとう","副詞(一般)②",["副詞"]),
"3375":("当面","とうめん","副詞(一般)②",["副詞"]),
"3417":("だぶだぶ","だぶだぶ","副詞(オノマトペ)",["副詞"]),
"3441":("とろとろ","とろとろ","副詞(オノマトペ)",["副詞"]),
"3444":("どろどろ","どろどろ","副詞(オノマトペ)",["副詞"]),
"3525":("オートマチック","おーとまちっく","カタカナ①",["名詞"]),
"3561":("ジャンボ","じゃんぼ","カタカナ②",["名詞"]),
"3565":("タイムリー","たいむりー","カタカナ②",["名詞"]),
"3569":("コマーシャル","こまーしゃる","カタカナ②",["名詞"]),
"3594":("ストレート","すとれーと","カタカナ②",["名詞"]),
"3636":("プライベート","ぷらいべーと","カタカナ②",["名詞"]),
"3646":("モダン","もだん","カタカナ②",["名詞"])}
for k,(word,reading,category,old_pos) in expected.items():
    row=by[k]
    if (row["w"],row["r"],row["c"],pos[k])!=(word,reading,category,old_pos): raise RuntimeError("baseline identity/POS mismatch "+k)
    if details[k]["w"]!=word: raise RuntimeError("detail identity mismatch "+k)
if set(spec["pos"])!={str(i) for i in IDS}: raise RuntimeError("POS scope mismatch")
if set(spec["quizzes"])!={"v_"+str(i) for i in IDS if i!=3363}: raise RuntimeError("quiz scope mismatch")
new_pos=copy.deepcopy(pos)
for k,v in spec["pos"].items(): new_pos[k]=v
new_quizzes=copy.deepcopy(quizzes)
semantic=[]
for i in IDS:
    k=str(i); d=details[k]
    if i==3363:
        q=new_quizzes.get("v_3363")
        if not q or "byExample" in q: raise RuntimeError("missing prior ID3363 global override")
        for ei,sentence in enumerate(d["examples"]):
            vals=[q["correct"],*q["wrong"]]; lengths=[len(x) for x in vals]; ratio=max(lengths)/min(lengths)
            if len(q["wrong"])!=3 or len(set(vals))!=4 or ratio>1.5: raise RuntimeError("ID3363 override failed")
            semantic.append({"id":i,"word":d["w"],"exampleIndex":ei,"example":sentence,"decision":"retained_existing_reviewed_override","correct":q["correct"],"wrong":q["wrong"],"note":q["note"],"lengths":lengths,"ratio":round(ratio,3),"rationale":"Existing author-reviewed v141 override; binding and balance rechecked, not counted as new override."})
        continue
    key="v_"+k
    if key in new_quizzes: raise RuntimeError("quiz key already exists "+key)
    by_example=spec["quizzes"][key]["byExample"]
    if set(by_example)!=set(d["examples"]): raise RuntimeError("byExample sentence mismatch "+key)
    for ei,sentence in enumerate(d["examples"]):
        q=by_example[sentence]; vals=[q["correct"],*q["wrong"]]; lengths=[len(x) for x in vals]; ratio=max(lengths)/min(lengths)
        if len(q["wrong"])!=3 or len(set(vals))!=4 or q["correct"] in q["wrong"] or ratio>1.5: raise RuntimeError("invalid options "+key+" example "+str(ei))
        semantic.append({"id":i,"word":d["w"],"exampleIndex":ei,"example":sentence,"decision":"reviewed_context_specific_override","correct":q["correct"],"wrong":q["wrong"],"note":q["note"],"lengths":lengths,"ratio":round(ratio,3),"rationale":"Manual context-specific review; three distinct plausible contrasts and balanced answer lengths."})
    new_quizzes[key]=copy.deepcopy(spec["quizzes"][key])
candidate=replace(base,"VOCAB_POS_BY_ID",new_pos)
candidate=replace(candidate,"REVIEWED_MEANING_QUIZZES",new_quizzes)
reviewed_cloze_block='''const REVIEWED_CLOZE_QUIZZES = {};
function reviewedClozeOptions(item, example) {
  const entry=REVIEWED_CLOZE_QUIZZES[item.kind+'_'+item.id];
  const reviewed=entry?.byExample?.[example];
  if(!reviewed||!Array.isArray(reviewed.wrong)||reviewed.wrong.length!==3)return null;
  const options=[item.word.w,...reviewed.wrong];
  return new Set(options).size===4?reviewed:null;
}
'''
reviewed_reading_marker="const REVIEWED_READING_OPTIONS = "
if candidate.count(reviewed_reading_marker)!=1: raise RuntimeError("reviewed reading marker mismatch")
candidate=candidate.replace(reviewed_reading_marker,reviewed_cloze_block+"\n"+reviewed_reading_marker,1)
old_cloze_gate="if (real && found && literalClozeAvailable(ex,it,this) && clozeCandidates.length>=3 && !reviewedExampleTarget(ex,it.kind,label) && !REVIEWED_MEANING_QUIZZES[it.kind+'_'+it.id]) types.push('cloze');"
new_cloze_gate="const reviewedCloze=reviewedClozeOptions(it,ex);\n        if (real && found && literalClozeAvailable(ex,it,this) && (reviewedCloze||clozeCandidates.length>=3) && !reviewedExampleTarget(ex,it.kind,label) && (!REVIEWED_MEANING_QUIZZES[it.kind+'_'+it.id]||reviewedCloze)) types.push('cloze');"
if candidate.count(old_cloze_gate)!=1: raise RuntimeError("cloze gate marker mismatch")
candidate=candidate.replace(old_cloze_gate,new_cloze_gate,1)
old_cloze_choice="const wrong = shuffleArray(clozeCandidates.filter(c=>c!==correct)).slice(0,3);"
new_cloze_choice="const wrong = reviewedCloze ? reviewedCloze.wrong.slice() : shuffleArray(clozeCandidates.filter(c=>c!==correct)).slice(0,3);"
if candidate.count(old_cloze_choice)!=1: raise RuntimeError("cloze choice marker mismatch")
candidate=candidate.replace(old_cloze_choice,new_cloze_choice,1)
old_title="<title>JLPT N1 — ウクライナ語対応学習アプリ · v229</title>"
new_title="<title>JLPT N1 — ウクライナ語対応学習アプリ · v230</title>"
if candidate.count(old_title)!=1: raise RuntimeError("title marker mismatch")
candidate=candidate.replace(old_title,new_title,1)
reverse=candidate.replace(new_title,old_title,1)
if reverse.count(reviewed_cloze_block)!=1: raise RuntimeError("reviewed cloze rollback marker mismatch")
reverse=reverse.replace(reviewed_cloze_block+"\n","",1)
if reverse.count(new_cloze_gate)!=1 or reverse.count(new_cloze_choice)!=1: raise RuntimeError("cloze engine rollback marker mismatch")
reverse=reverse.replace(new_cloze_gate,old_cloze_gate,1).replace(new_cloze_choice,old_cloze_choice,1)
for name in ["REVIEWED_MEANING_QUIZZES","VOCAB_POS_BY_ID"]:
    a,b,_=extract(reverse,name); reverse=reverse[:a]+blocks[name]+reverse[b:]
if reverse!=base: raise RuntimeError("exact rollback failed")
for name in ["DEFAULT_VOCAB","GRAMMAR_DETAILS_BY_ID","VOCAB_DETAILS_BY_ID","VOCAB_AUDITED_PAIRS","REVIEWED_READING_OPTIONS","VOCAB_KANA_EXAMPLE_TARGETS","REVIEWED_EXAMPLE_TARGETS"]:
    if extract(candidate,name)[2]!=data[name]: raise RuntimeError("protected block changed "+name)
out=candidate.encode("utf-8"); OUT.write_bytes(out)
sha=hashlib.sha256(out).hexdigest(); blob=hashlib.sha1(b"blob "+str(len(out)).encode()+b"\0"+out).hexdigest()
cloze_reasons={
3363:"Near-equivalent degree adverbs can complete both sentences naturally; no unique three-distractor set was established.",
3375:"当分, 目下 and other time expressions can be contextually acceptable; the headword is not uniquely recoverable from either sentence.",
3417:"ぶかぶか is a genuine near-synonym in both clothing contexts, so a four-choice cloze would be ambiguous.",
3441:"Other food-state and dozing expressions can complete the sentences naturally; the exact onomatopoeia is not uniquely forced.",
3444:"Other mud-state and relationship descriptors can produce natural, defensible readings; no unique answer was proved.",
3525:"The post-POS pool is broad and mostly unrelated; a random three-choice sample would be an answer-form hint rather than a semantic test.",
3561:"Size labels can fit the pizza context, while several aircraft labels can fit the runway context; the target is not uniquely forced.",
3565:"適切 and other timing/appropriateness expressions can be valid in both contexts, creating multiple defensible answers.",
3569:"広告・宣伝 and related broadcast expressions can fit; the contexts do not uniquely require the loanword.",
3594:"率直 and other directness expressions can fit naturally; the target loanword is not uniquely recoverable.",
3636:"私生活 and related personal-life expressions can fit naturally; the target loanword is not uniquely recoverable.",
3646:"現代的・斬新 and related style expressions can fit naturally; the target loanword is not uniquely recoverable."
}
cloze_review=[]
for i in IDS:
    for ei,sentence in enumerate(details[str(i)]["examples"]):
        cloze_review.append({"id":i,"word":details[str(i)]["w"],"exampleIndex":ei,"example":sentence,"decision":"reject_cloze","allowCloze":False,"reason":cloze_reasons[i]})
(W/"cloze-context-review.json").write_text(json.dumps({"version":230,"reviewType":"author_manual_cloze_review","scope":IDS,"contexts":len(cloze_review),"approved":0,"rejected":len(cloze_review),"decisions":cloze_review},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
result={"pass":True,"base_version":"v229","base_main_sha":"afb7f3aa5ebe3d16b1a66e6aabec1648b9cb0dba","base_html_sha256":base_sha,"candidate_version":"v230","candidate_sha256":sha,"candidate_blob_sha":blob,"candidate_bytes":len(out),"scope_ids":IDS,"vocabulary_records":len(vocab),"grammar_records":len(grammar),"lexical_pairs":len(pairs),"unique_vocabulary_ids":len({x["id"] for x in vocab}),"pos_updates":{k:{"before":pos[k],"after":new_pos[k]} for k in spec["pos"]},"meaning_quiz_added":sorted(spec["quizzes"]),"meaning_contexts":len(semantic),"new_context_overrides":22,"retained_context_overrides":2,"reviewed_cloze_engine":True,"reviewed_cloze_payloads":0,"cloze_contexts_reviewed":len(cloze_review),"cloze_contexts_rejected":len(cloze_review),"protected":{"DEFAULT_VOCAB":True,"GRAMMAR_DETAILS_BY_ID":True,"VOCAB_DETAILS_BY_ID":True,"VOCAB_AUDITED_PAIRS":True,"REVIEWED_READING_OPTIONS":True,"VOCAB_KANA_EXAMPLE_TARGETS":True,"REVIEWED_EXAMPLE_TARGETS":True,"storage_keys":True,"legacy_cloze_behavior":"unchanged unless an exact REVIEWED_CLOZE_QUIZZES byExample payload exists"},"exact_rollback":True,"pilot_v153_credit":0}
(W/"prepare-results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(W/"semantic-review.json").write_text(json.dumps({"version":230,"reviewType":"author_manual_semantic_review","independentReview":False,"scope":IDS,"context_count":len(semantic),"overall_decision":"pass","decisions":semantic},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
updates=[]
for k in sorted(spec["pos"],key=int): updates.append({"op":"replace","block":"VOCAB_POS_BY_ID","path":[k],"before":pos[k],"after":new_pos[k],"reason":"C11 POS-map reconciled with selected card senses and observed forms."})
for k in sorted(spec["quizzes"]): updates.append({"op":"add","block":"REVIEWED_MEANING_QUIZZES","path":[k],"after":spec["quizzes"][k],"reason":"22 exact contexts manually reviewed with context-specific keys and balanced distractors."})
(W/"updates.json").write_text(json.dumps(updates,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
cp={"checkpoint":"v230-c11-reviewed-candidate","created":"2026-11-17","work_branch":"work/v230-reviewed-cloze-gate","base_main_sha":result["base_main_sha"],"base_html_sha256":base_sha,"candidate_sha256":sha,"candidate_blob_sha":blob,"candidate_bytes":len(out),"scope_ids":IDS,"status":"candidate prepared; awaiting Chromium verification and guarded main publication","guardrails":["retain 3914 vocabulary records, 130 grammar constructions, 859 lexical pairs and all stable IDs","do not change vocabulary data, grammar, details/examples/translations, lexical pairs, reading overrides, target tables or storage keys","only 12 scoped POS-map entries, 11 reviewed meaning-quiz keys and the inert reviewed-cloze gate may change","legacy cloze behavior must remain byte-for-byte equivalent unless an exact reviewed byExample payload exists","no v153 pilot credit; all IDs are outside 121-320","do not force reading/cloze distractors where no valid choices exist","author review and technical verification are not independent acceptance"],"next_action":"run Chromium verification for global legacy equivalence and the empty reviewed-cloze gate; finalize only if all guards pass"}
(W/"checkpoint.json").write_text(json.dumps(cp,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,ensure_ascii=False,indent=2))
