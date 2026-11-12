#!/usr/bin/env python3
import csv,json,re,hashlib
from collections import Counter
from pathlib import Path
W=Path("completion/v177-work")
def compact(x): return json.dumps(x,ensure_ascii=False,separators=(",",":"))
def block(s,n):
 m=re.search(r"\bconst\s+"+re.escape(n)+r"\s*=\s*",s)
 if not m: raise ValueError(n)
 x,_=json.JSONDecoder().raw_decode(s,m.end())
 return x
def main():
 prep=json.loads((W/"prepare-results.json").read_text(encoding="utf-8"))
 browser=json.loads((W/"browser-results.json").read_text(encoding="utf-8"))
 if not prep.get("pass") or not browser.get("pass"): raise ValueError("verification missing")
 if browser.get("sha256")!=prep.get("checkpoint_sha256"): raise ValueError("browser hash")
 base=block(Path("JLPT_N1_ukrainian_reading_v176.html").read_text(encoding="utf-8"),"VOCAB_DETAILS_BY_ID")
 after=block(Path("JLPT_N1_ukrainian_reading_v177.html").read_text(encoding="utf-8"),"VOCAB_DETAILS_BY_ID")
 updates=json.loads((W/"updates.json").read_text(encoding="utf-8"))
 def digest(x): return hashlib.sha256(compact(x).encode("utf-8")).hexdigest()
 with (Path("completion/v177-acceptance.tsv")).open("w",encoding="utf-8",newline="") as f:
  w=csv.writer(f,delimiter="\t",lineterminator="\n")
  w.writerow(["id","headword","decision","fields","before_sha256","after_sha256","rationale","sources"])
  for x in updates:
   i=str(x["id"]);w.writerow([i,x["headword"],"fixed_rechecked",x["field"],digest(base[i]),digest(after[i]),x["rationale"],"; ".join(x["sources"])])
  i="371";w.writerow([i,base[i]["w"],"reviewed","",digest(base[i]),digest(after[i]),"もっか is a noun with adverbial use; adding 副詞 reduces the reading pool from six to one.","https://kotobank.jp/word/%E7%9B%AE%E4%B8%8B-643739"])
 pairs=list(csv.DictReader((W/"pair-review.tsv").open(encoding="utf-8"),delimiter="\t"))
 old=block(Path("JLPT_N1_ukrainian_reading_v176.html").read_text(encoding="utf-8"),"VOCAB_AUDITED_PAIRS")
 new=block(Path("JLPT_N1_ukrainian_reading_v177.html").read_text(encoding="utf-8"),"VOCAB_AUDITED_PAIRS")
 with Path("completion/v177-pair-review.tsv").open("w",encoding="utf-8",newline="") as f:
  w=csv.writer(f,delimiter="\t",lineterminator="\n")
  w.writerow(["pair_index","pair_key","type","decision","before_sha256","after_sha256","rationale","sources"])
  for x in pairs:
   i=int(x["pair_index"]);key=str(i)+":"+str(old[i]["a"])+":"+str(old[i]["b"])
   if key!=x["pair_key"] or old[i]!=new[i]: raise ValueError("pair mismatch")
   w.writerow([str(i),key,old[i]["type"],"reviewed unchanged",digest(old[i]),digest(new[i]),x["rationale"],x["sources"]])
 reg=Path("completion/review-register.csv")
 with reg.open(encoding="utf-8",newline="") as f:
  r=csv.DictReader(f);names=r.fieldnames;rows=list(r)
 for x in updates:
  row=next(r for r in rows if r["kind"]=="vocab" and r["key"]==str(x["id"]))
  if row["finalReview"]!="pending": raise ValueError("not pending "+str(x["id"]))
  row["finalReview"]="fixed_rechecked";row["evidence"]="completion/v177-acceptance.tsv:"+str(x["id"])+"; author review, not independent"
 row=next(r for r in rows if r["kind"]=="vocab" and r["key"]=="371")
 if row["finalReview"]!="pending": raise ValueError("371 not pending")
 row["finalReview"]="reviewed";row["evidence"]="completion/v177-acceptance.tsv:371; author review, not independent"
 for x in pairs:
  row=next(r for r in rows if r["kind"]=="vocab_pair" and r["key"]==x["pair_key"])
  if row["finalReview"]!="pending": raise ValueError("pair not pending")
  row["finalReview"]="reviewed";row["evidence"]="completion/v177-pair-review.tsv:"+x["pair_index"]+"; author review, not independent"
 with reg.open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=names,lineterminator="\n");w.writeheader();w.writerows(rows)
 c=Counter(r["finalReview"] for r in rows)
 v=Counter(r["finalReview"] for r in rows if r["kind"]=="vocab")
 p=Counter(r["finalReview"] for r in rows if r["kind"]=="vocab_pair")
 if dict(c)!={"reviewed":3890,"fixed_rechecked":48,"pending":1904}: raise ValueError("registry "+repr(dict(c)))
 if dict(v)!={"reviewed":3326,"fixed_rechecked":47,"pending":541}: raise ValueError("vocab "+repr(dict(v)))
 if {k:p.get(k,0) for k in ["reviewed","pending"]}!={"reviewed":18,"pending":841}: raise ValueError("pairs")
 result={"pass":True,"registry_counts":dict(c),"vocabulary_counts":dict(v),"lexical_pair_counts":{"reviewed":18,"pending":841},"author_credit":"3373/3914","independent_acceptance":False,"physical_acceptance":False}
 (W/"registry-results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
