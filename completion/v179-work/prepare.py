#!/usr/bin/env python3
import copy,hashlib,json,re,subprocess
from pathlib import Path
SOURCE=Path("JLPT_N1_ukrainian_reading_v178.html")
TARGET=Path("JLPT_N1_ukrainian_reading_v179.html")
UPDATES=Path("completion/v179-work/updates.json")
BASE_SHA256="b8120e2bffc45936aa1208251d6b5ccee549daf54a1ce644693a458224c039e9"
def compact(v): return json.dumps(v,ensure_ascii=False,separators=(",",":"))
def block(source,name):
 m=re.search(r"\bconst\s+"+re.escape(name)+r"\s*=\s*",source)
 if not m: raise ValueError("Missing block "+name)
 start=m.end();value,end=json.JSONDecoder().raw_decode(source,start)
 if compact(value)!=source[start:end]: raise ValueError("Unexpected serialization "+name)
 return value,start,end
def frame(word): return re.sub(r"[一-鿿々]+","#",str(word))
def distance(a,b):
 row=list(range(len(b)+1))
 for i in range(1,len(a)+1):
  prev=row[0];row[0]=i
  for j in range(1,len(b)+1):
   old=row[j];row[j]=min(row[j]+1,row[j-1]+1,prev+(0 if a[i-1]==b[j-1] else 1));prev=old
 return row[len(b)]
def reading_options(item,vocab,pos,reviewed):
 override=reviewed.get(str(item["id"]))
 if override and override.get("word")==item["w"] and override.get("correct")==item.get("r"): return list(override.get("wrong",[]))
 word=item["w"];reading=item.get("r","")
 if not reading or not re.fullmatch(r"[ぁ-ゟー]+",reading) or not re.search(r"[一-鿿]",word) or re.search(r"[〜～・／/]",word): return []
 pos_key="|".join(pos.get(str(item["id"]),["連語"]))
 prefix=(re.match(r"^[ぁ-ゟー]+",word) or [""])[0];tail=(re.search(r"[ぁ-ゟー]+$",word) or [""])[0]
 if (prefix and not reading.startswith(prefix)) or (tail and not reading.endswith(tail)): return []
 core=reading[len(prefix):len(reading)-len(tail) if tail else None];candidates=[]
 for other in vocab:
  if other["id"]==item["id"] or other.get("r")==reading: continue
  if not re.fullmatch(r"[ぁ-ゟー]+",other.get("r","")) or frame(other["w"])!=frame(word): continue
  if "|".join(pos.get(str(other["id"]),["連語"]))!=pos_key or abs(len(other["r"])-len(reading))>1: continue
  if prefix and not other["r"].startswith(prefix): continue
  if tail and not other["r"].endswith(tail): continue
  other_core=other["r"][len(prefix):len(other["r"])-len(tail) if tail else None]
  d=distance(core,other_core)
  if 0<d<=2: candidates.append((other["r"],d))
 candidates.sort(key=lambda x:(x[1],x[0]));result=[]
 for value,_ in candidates:
  if value not in result: result.append(value)
 return result[:6]
def main():
 original=SOURCE.read_text(encoding="utf-8")
 base_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
 if base_hash!=BASE_SHA256: raise ValueError("v178 baseline mismatch: "+base_hash)
 targets,start,end=block(original,"REVIEWED_EXAMPLE_TARGETS");before=copy.deepcopy(targets)
 updates=json.loads(UPDATES.read_text(encoding="utf-8"))
 if len(updates)!=2: raise ValueError("Expected exactly two context-specific payloads")
 changed=[]
 for u in updates:
  matches=[r for r in targets if r.get("kind")=="v" and r.get("id")==u["id"] and r.get("word")==u["word"] and r.get("sentence")==u["sentence"]]
  if len(matches)!=1: raise ValueError("Exact reviewed target missing or duplicated")
  row=matches[0]
  if row.get("exampleIndex")!=u["exampleIndex"] or row.get("forms")!=["下した"] or "quiz" in row: raise ValueError("Existing target mismatch")
  q=u["quiz"]
  if len(q.get("wrong",[]))!=3 or len(set([q["correct"],*q["wrong"]]))!=4: raise ValueError("Quiz must have four unique options")
  row["quiz"]=q;changed.append({"id":u["id"],"word":u["word"],"exampleIndex":u["exampleIndex"],"sentence":u["sentence"]})
 html=original[:start]+compact(targets)+original[end:]
 old_title="<title>JLPT N1 — ウクライナ語対応学習アプリ · v178</title>"
 new_title="<title>JLPT N1 — ウクライナ語対応学習アプリ · v179</title>"
 if html.count(old_title)!=1: raise ValueError("Unexpected v178 title")
 html=html.replace(old_title,new_title,1)
 after,_,_=block(html,"REVIEWED_EXAMPLE_TARGETS")
 a=copy.deepcopy(before);b=copy.deepcopy(after)
 for rows in (a,b):
  for r in rows:
   if r.get("id")==2468 and r.get("word")=="下す" and any(r.get("sentence")==u["sentence"] for u in updates): r.pop("quiz",None)
 if a!=b: raise ValueError("Unexpected target mutation outside the two quiz payloads")
 names=["DEFAULT_VOCAB","VOCAB_DETAILS_BY_ID","GRAMMAR_DETAILS_BY_ID","VOCAB_POS_BY_ID","VOCAB_AUDITED_PAIRS","REVIEWED_READING_OPTIONS","REVIEWED_MEANING_QUIZZES","VOCAB_KANA_EXAMPLE_TARGETS"]
 counts={}
 for name in names:
  x,_,_=block(original,name);y,_,_=block(html,name)
  if x!=y: raise ValueError("Unexpected data mutation: "+name)
  counts[name]=len(x)
 vocab,_,_=block(html,"DEFAULT_VOCAB");cards,_,_=block(html,"VOCAB_DETAILS_BY_ID")
 grammar,_,_=block(html,"GRAMMAR_DETAILS_BY_ID");pos,_,_=block(html,"VOCAB_POS_BY_ID")
 pairs,_,_=block(html,"VOCAB_AUDITED_PAIRS")
 if (len(vocab),len(cards),len(grammar),len(pos),len(pairs))!=(3914,3914,130,3914,859): raise ValueError("Structural count mismatch")
 if list(cards)!=list(block(original,"VOCAB_DETAILS_BY_ID")[0]): raise ValueError("Vocabulary ID order changed")
 rollback=html.replace(new_title,old_title,1);rt,rs,re_=block(rollback,"REVIEWED_EXAMPLE_TARGETS")
 for r in rt:
  if r.get("id")==2468 and r.get("word")=="下す" and any(r.get("sentence")==u["sentence"] for u in updates): r.pop("quiz",None)
 rollback=rollback[:rs]+compact(rt)+rollback[re_:]
 if rollback!=original: raise ValueError("Exact rollback failed")
 scripts=0
 for script in re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",html,re.S):
  if script.strip(): subprocess.run(["node","--check","-"],input=script,text=True,check=True);scripts+=1
 output=html.encode("utf-8");TARGET.write_bytes(output)
 result={"pass":True,"base_version":"v178","base_sha256":base_hash,"candidate_version":"v179","candidate_sha256":hashlib.sha256(output).hexdigest(),"candidate_bytes":len(output),"vocabulary_records":len(vocab),"grammar_records":len(grammar),"lexical_pairs":len(pairs),"changed_payloads":changed,"unchanged_blocks":counts,"inline_scripts_checked":scripts,"exact_rollback":True,"author_credit_change":0}
 (Path("completion/v179-work")/"prepare-results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 candidate={"checkpoint":"v179-c11-context-quiz","base_main_sha":"fc644673247f6b334e73e634e2c5ec7fdb31c740","work_branch":"work/v179-c11-context-quiz-review","base_html_sha256":base_hash,"candidate_html":"JLPT_N1_ukrainian_reading_v179.html","candidate_sha256":result["candidate_sha256"],"scope":["ID2468 example 0 meaning quiz","ID2468 example 1 meaning quiz"],"status":"candidate pending Chromium and publication gate"}
 (Path("completion/v179-work")/"candidate.json").write_text(json.dumps(candidate,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 cp={"checkpoint":"v179-c11-context-quiz-review","base_main_sha":"fc644673247f6b334e73e634e2c5ec7fdb31c740","work_branch":"work/v179-c11-context-quiz-review","base_html_sha256":base_hash,"candidate_sha256":result["candidate_sha256"],"scope_ids":[2433,2468,255,327],"status":"candidate generated; awaiting verification"}
 (Path("completion/v179-work")/"checkpoint.json").write_text(json.dumps(cp,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 reviewed=block(original,"REVIEWED_READING_OPTIONS")[0]
 proposed=copy.deepcopy(pos);proposed["255"]=["名詞","ナ形"];proposed["327"]=["名詞","ナ形"]
 before_pools={str(v["id"]):reading_options(v,vocab,pos,reviewed) for v in vocab}
 after_pools={str(v["id"]):reading_options(v,vocab,proposed,reviewed) for v in vocab}
 changed_pools=[];lost=[];gained=[]
 for v in vocab:
  key=str(v["id"]);a=before_pools[key];b=after_pools[key]
  if a!=b: changed_pools.append({"id":v["id"],"word":v["w"],"reading":v.get("r",""),"before":a,"after":b})
  if len(a)>=3 and len(b)<3: lost.append({"id":v["id"],"word":v["w"],"before_count":len(a),"after_count":len(b)})
  if len(a)<3 and len(b)>=3: gained.append({"id":v["id"],"word":v["w"],"before_count":len(a),"after_count":len(b)})
 impact={"baseline_eligible":sum(len(x)>=3 for x in before_pools.values()),"proposed_pos_only_eligible":sum(len(x)>=3 for x in after_pools.values()),"changed_pool_count":len(changed_pools),"lost_eligibility":lost,"gained_eligibility":gained,"changed_pools":changed_pools,"pos_changes_applied":False,"note":"Diagnostic only. Proposed POS tags for ID255/327 are not applied because 23 pools change and ID1819 falls below the three-distractor threshold. No learning mechanism or POS data changed in v179."}
 Path("completion/v179-reading-pool-impact.json").write_text(json.dumps(impact,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
