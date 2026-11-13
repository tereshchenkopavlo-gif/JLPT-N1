#!/usr/bin/env python3
import csv,json
from collections import Counter
from pathlib import Path
W=Path("completion/v179-work")
def main():
 prep=json.loads((W/"prepare-results.json").read_text(encoding="utf-8"))
 browser=json.loads((W/"browser-results.json").read_text(encoding="utf-8"))
 if not prep.get("pass") or not browser.get("pass") or browser.get("sha256")!=prep.get("candidate_sha256"): raise ValueError("Candidate verification incomplete or hash mismatch")
 reg=Path("completion/review-register.csv")
 with reg.open(encoding="utf-8",newline="") as f:
  reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
 if any(r["kind"]=="reviewed_meaning_quiz" and r["key"]=="v_2468" for r in rows): raise ValueError("ID2468 meaning quiz already registered")
 rows.append({"kind":"reviewed_meaning_quiz","key":"v_2468","baselineLocation":"REVIEWED_EXAMPLE_TARGETS:v_2468","finalReview":"reviewed","evidence":"completion/v179-acceptance.tsv; two exact context-specific payloads; author review, not independent"})
 with reg.open("w",encoding="utf-8",newline="") as f:
  writer=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");writer.writeheader();writer.writerows(rows)
 c=Counter(r["finalReview"] for r in rows)
 v=Counter(r["finalReview"] for r in rows if r["kind"]=="vocab")
 p=Counter(r["finalReview"] for r in rows if r["kind"]=="vocab_pair")
 q=Counter(r["finalReview"] for r in rows if r["kind"]=="reviewed_meaning_quiz")
 if dict(c)!={"reviewed":3892,"fixed_rechecked":59,"pending":1892}: raise ValueError("Register totals mismatch: "+repr(dict(c)))
 if dict(v)!={"reviewed":3327,"fixed_rechecked":58,"pending":529}: raise ValueError("Vocabulary totals mismatch: "+repr(dict(v)))
 if p.get("reviewed",0)!=18 or p.get("pending",0)!=841: raise ValueError("Pair totals mismatch")
 if q.get("reviewed",0)!=266: raise ValueError("Meaning quiz count mismatch")
 with Path("completion/v179-acceptance.tsv").open("w",encoding="utf-8",newline="") as f:
  w=csv.writer(f,delimiter="\t",lineterminator="\n");w.writerow(["kind","key","decision","scope","evidence","acceptance_boundary"])
  w.writerow(["reviewed_meaning_quiz","v_2468","reviewed","two context-specific example payloads","completion/v179-c11-review.tsv; completion/v179-source-review.md","author review only; not independent linguistic acceptance"])
 result={"pass":True,"registry_rows":len(rows),"registry_counts":dict(c),"vocabulary_counts":dict(v),"lexical_pair_counts":{"reviewed":18,"pending":841},"reviewed_meaning_quizzes":q.get("reviewed",0),"author_credit":"3385/3914","new_reviewed_meaning_quiz":["v_2468"],"vocabulary_credit_change":0,"independent_acceptance":False,"physical_acceptance":False}
 (W/"registry-results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
