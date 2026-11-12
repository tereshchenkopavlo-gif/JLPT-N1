#!/usr/bin/env python3
import csv,json,re,hashlib
from collections import Counter
from pathlib import Path
W=Path("completion/v178-work")
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
 if browser.get("sha256")!=prep.get("checkpoint_sha256"): raise ValueError("browser hash mismatch")
 base=block(Path("JLPT_N1_ukrainian_reading_v177.html").read_text(encoding="utf-8"),"VOCAB_DETAILS_BY_ID")
 after=block(Path("JLPT_N1_ukrainian_reading_v178.html").read_text(encoding="utf-8"),"VOCAB_DETAILS_BY_ID")
 updates=json.loads((W/"updates.json").read_text(encoding="utf-8"))
 def digest(x): return hashlib.sha256(compact(x).encode("utf-8")).hexdigest()
 with Path("completion/v178-acceptance.tsv").open("w",encoding="utf-8",newline="") as f:
  w=csv.writer(f,delimiter="\t",lineterminator="\n")
  w.writerow(["id","headword","decision","fields","before_sha256","after_sha256","rationale","sources"])
  for x in updates:
   i=str(x["id"]);w.writerow([i,x["headword"],"fixed_rechecked",x["field"],digest(base[i]),digest(after[i]),x["rationale"],"; ".join(x["sources"])])
  i="425";w.writerow([i,base[i]["w"],"reviewed","",digest(base[i]),digest(after[i]),"予想が外れる and メンバーから外れる are both directly covered by the existing examples; usage also explicitly covers 規則から外れる. No content change was justified.","https://kotobank.jp/word/%E5%A4%96%E3%82%8C%E3%82%8B-601500"])
 for path in [W/"author-decisions.tsv",W/"scope.tsv"]:
  with path.open(encoding="utf-8",newline="") as f:
   r=csv.DictReader(f,delimiter="\t");names=r.fieldnames;rows=list(r)
  for row in rows:
   if row["id"]=="425": row["status"]="reviewed unchanged; source and examples checked; Chromium pass"
   elif row["id"] in {str(x["id"]) for x in updates}: row["status"]="fixed_rechecked; exact before/after verified; Chromium pass"
  with path.open("w",encoding="utf-8",newline="") as f:
   w=csv.DictWriter(f,fieldnames=names,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
 reg=Path("completion/review-register.csv")
 with reg.open(encoding="utf-8",newline="") as f:
  r=csv.DictReader(f);names=r.fieldnames;rows=list(r)
 for i in sorted({str(x["id"]) for x in updates},key=int):
  row=next(r for r in rows if r["kind"]=="vocab" and r["key"]==i)
  if row["finalReview"]!="pending": raise ValueError("unexpected prior status "+i+": "+row["finalReview"])
  row["finalReview"]="fixed_rechecked";row["evidence"]="completion/v178-acceptance.tsv:"+i+"; author review, not independent"
 row=next(r for r in rows if r["kind"]=="vocab" and r["key"]=="425")
 if row["finalReview"]!="pending": raise ValueError("unexpected ID425 prior status "+row["finalReview"])
 row["finalReview"]="reviewed";row["evidence"]="completion/v178-acceptance.tsv:425; author review, not independent"
 with reg.open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=names,lineterminator="\n");w.writeheader();w.writerows(rows)
 c=Counter(r["finalReview"] for r in rows)
 v=Counter(r["finalReview"] for r in rows if r["kind"]=="vocab")
 p=Counter(r["finalReview"] for r in rows if r["kind"]=="vocab_pair")
 expected={"reviewed":3891,"fixed_rechecked":59,"pending":1892}
 if dict(c)!=expected: raise ValueError("registry totals "+repr(dict(c)))
 if dict(v)!={"reviewed":3327,"fixed_rechecked":58,"pending":529}: raise ValueError("vocabulary totals "+repr(dict(v)))
 if {k:p.get(k,0) for k in ["reviewed","pending"]}!={"reviewed":18,"pending":841}: raise ValueError("pair totals "+repr(dict(p)))
 result={"pass":True,"registry_counts":dict(c),"vocabulary_counts":dict(v),"lexical_pair_counts":{"reviewed":18,"pending":841},"author_credit":"3385/3914","fixed_rechecked_ids":[str(x["id"]) for x in updates],"reviewed_without_change":["425"],"independent_acceptance":False,"physical_acceptance":False}
 (W/"registry-results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
