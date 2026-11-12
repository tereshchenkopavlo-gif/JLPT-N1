#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re,subprocess
from pathlib import Path
SOURCE=Path("JLPT_N1_ukrainian_reading_v177.html")
TARGET=Path("JLPT_N1_ukrainian_reading_v178.html")
UPDATES=Path("completion/v178-work/updates.json")
BASE_SHA256="07b0c89b48ab8d3cffb7d7591a8d13b306a9512e86026e5684216b5e152df45e"
EXPECTED_CHANGED_IDS=["421","423","430","433","435","436","438","440","444","447","449"]
EXPECTED_UNCHANGED_IDS=["425"]
def compact(v): return json.dumps(v,ensure_ascii=False,separators=(",",":"))
def block(source,name):
 m=re.search(r"\bconst\s+"+re.escape(name)+r"\s*=\s*",source)
 if not m: raise ValueError("Missing block "+name)
 start=m.end(); value,end=json.JSONDecoder().raw_decode(source,start)
 if compact(value)!=source[start:end]: raise ValueError("Unexpected serialization "+name)
 return value,start,end
def get_path(v,p):
 for part in p.split("."): v=v[int(part)] if isinstance(v,list) else v[part]
 return v
def set_path(v,p,replacement):
 parts=p.split("."); last=parts.pop(); cur=v
 for part in parts: cur=cur[int(part)] if isinstance(cur,list) else cur[part]
 if isinstance(cur,list): cur[int(last)]=replacement
 else: cur[last]=replacement
def main():
 raw=SOURCE.read_bytes(); base_hash=hashlib.sha256(raw).hexdigest()
 if base_hash!=BASE_SHA256: raise ValueError("v177 baseline mismatch "+base_hash)
 original=raw.decode("utf-8")
 cards,start,end=block(original,"VOCAB_DETAILS_BY_ID")
 old_cards=json.loads(json.dumps(cards,ensure_ascii=False))
 updates=json.loads(UPDATES.read_text(encoding="utf-8"))
 if len(updates)!=13: raise ValueError("Expected 13 exact operations")
 fields=[str(x["id"])+"."+x["field"] for x in updates]
 expected_fields=["421.m","423.usage","430.m","433.m","435.t","436.examples.1","436.exampleTranslations.1","438.exampleTranslations.0","438.exampleTranslations.1","440.usage","444.exampleTranslations.0","447.exampleTranslations.1","449.exampleTranslations.0"]
 if fields!=expected_fields: raise ValueError("Update scope mismatch "+repr(fields))
 for row in updates:
  card=cards[str(row["id"])]
  if card["w"]!=row["headword"]: raise ValueError("Headword mismatch "+str(row["id"]))
  if get_path(card,row["field"])!=row["before"]: raise ValueError("Before mismatch "+str(row["id"]))
  set_path(card,row["field"],row["after"])
 html=original[:start]+compact(cards)+original[end:]
 old_title="<title>JLPT N1 — ウクライナ語対応学習アプリ · v177</title>"
 new_title="<title>JLPT N1 — ウクライナ語対応学習アプリ · v178</title>"
 if html.count(old_title)!=1: raise ValueError("Unexpected title")
 html=html.replace(old_title,new_title,1)
 after_cards,_,_=block(html,"VOCAB_DETAILS_BY_ID")
 changed=[k for k in old_cards if old_cards[k]!=after_cards[k]]
 if changed!=EXPECTED_CHANGED_IDS: raise ValueError("Changed IDs mismatch "+repr(changed))
 for i in EXPECTED_UNCHANGED_IDS:
  if after_cards[i]!=old_cards[i]: raise ValueError("Unchanged review candidate mutated "+i)
 names=["DEFAULT_VOCAB","GRAMMAR_DETAILS_BY_ID","VOCAB_POS_BY_ID","VOCAB_AUDITED_PAIRS","VOCAB_KANA_EXAMPLE_TARGETS","REVIEWED_READING_OPTIONS","REVIEWED_MEANING_QUIZZES"]
 counts={}
 for name in names:
  before,_,_=block(original,name); after,_,_=block(html,name)
  if before!=after: raise ValueError("Unexpected block mutation "+name)
  counts[name]=len(before)
 vocab,_,_=block(html,"DEFAULT_VOCAB")
 grammar,_,_=block(html,"GRAMMAR_DETAILS_BY_ID")
 pos,_,_=block(html,"VOCAB_POS_BY_ID")
 pairs,_,_=block(html,"VOCAB_AUDITED_PAIRS")
 if (len(vocab),len(after_cards),len(grammar),len(pos),len(pairs))!=(3914,3914,130,3914,859): raise ValueError("Record counts changed")
 if list(after_cards)!=list(old_cards): raise ValueError("ID order changed")
 restored=html.replace(new_title,old_title,1)
 restored_cards,rs,re_=block(restored,"VOCAB_DETAILS_BY_ID")
 for row in updates: set_path(restored_cards[str(row["id"])],row["field"],row["before"])
 restored=restored[:rs]+compact(restored_cards)+restored[re_:]
 if restored!=original: raise ValueError("Exact rollback failed")
 checked=0
 for script in re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",html,re.S):
  if script.strip(): subprocess.run(["node","--check","-"],input=script,text=True,check=True); checked+=1
 output=html.encode("utf-8"); TARGET.write_bytes(output)
 result={"pass":True,"base_version":"v177","base_sha256":base_hash,"checkpoint_version":"v178","checkpoint_sha256":hashlib.sha256(output).hexdigest(),"checkpoint_bytes":len(output),"vocabulary_records":len(vocab),"grammar_records":len(grammar),"vocab_pos_records":len(pos),"lexical_pairs":len(pairs),"changed_ids":changed,"reviewed_without_change":EXPECTED_UNCHANGED_IDS,"changed_fields":fields,"operations":len(updates),"unchanged_data_blocks":counts,"inline_scripts_checked":checked,"exact_rollback":True}
 Path("completion/v178-work/prepare-results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
