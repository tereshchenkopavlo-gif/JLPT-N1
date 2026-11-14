import csv, json, os
from collections import Counter
from pathlib import Path

w=Path("completion/v229-work")
p=json.loads((w/"prepare-results.json").read_text(encoding="utf-8"))
b=json.loads((w/"browser-results.json").read_text(encoding="utf-8"))
s=json.loads((w/"semantic-review.json").read_text(encoding="utf-8"))
cp=json.loads((w/"checkpoint.json").read_text(encoding="utf-8"))
ids=[2734,544,550,552,557,588,599,644,663,1631,3337,3345]
assert p.get("pass") and b.get("pass")
assert p["candidate_sha256"]==b["candidate_sha256"] and p["candidate_bytes"]==b["candidate_bytes"]
assert s["overall_decision"]=="pass" and s["scope"]==ids and s["context_count"]==24
assert len(s["decisions"])==24 and len({(x["id"],x["exampleIndex"]) for x in s["decisions"]})==24
assert b["meaningStructurePass"] and b["meaningLengthPass"] and b["meaningDiagnosticCount"]==24
checks=b["reviewedOverrideChecks"]
assert len(checks)==22 and all(x["correctMatch"] and x["wrongSetMatch"] and x["noteMatch"] for x in checks)
assert b["pageErrors"]==[] and b["storage"]["roundTrip"] and b["storage"]["restored"]
assert all(not x["overflow"] for x in b["responsive"])
assert len(b["rendered"])==12 and all(x["title"] and x["meaning"] and x["usageData"] and x["examples"] and x["translations"] and x["pos"]==x["expectedPos"] for x in b["rendered"])
pool=b["poolImpact"]
assert len(pool)==12
x=next(x for x in pool if x["id"]==2734)
assert x["posAfter"]==["連体詞"] and x["readingAfter"]==0 and x["clozeAfter"]==2
assert not x["readingEligibleAfter"] and not x["clozeEligibleAfter"]
assert all(y["readingBefore"]==y["readingAfter"] and y["clozeBefore"]==y["clozeAfter"] for y in pool if y["id"]!=2734)

rp=Path("completion/review-register.csv")
with rp.open(encoding="utf-8",newline="") as f: rows=list(csv.reader(f))
assert rows[0]==["kind","key","baselineLocation","finalReview","evidence"] and len(rows)-1==5847
ev="JLPT_N1_v229_audit.md; completion/v229-acceptance.tsv; completion/v229-c11-review.tsv; completion/v229-semantic-review.md; C11 manual semantic review and POS/pool impact; no v153 pilot credit"
found=set()
for r in rows[1:]:
    if len(r)>=5 and r[0]=="vocab" and r[1] in {str(i) for i in ids}:
        assert r[3]=="blocked"
        r[3]="fixed_rechecked"; r[4]=ev; found.add(int(r[1]))
assert found==set(ids)
with rp.open("w",encoding="utf-8",newline="") as f: csv.writer(f,lineterminator="\\n").writerows(rows)

def count(rs):
    c=Counter(r[3] for r in rs if len(r)>=4)
    return {k:c.get(k,0) for k in ("reviewed","fixed_rechecked","pending","blocked")}
allc=count(rows[1:])
vr=[r for r in rows[1:] if len(r)>=4 and r[0]=="vocab"]
pr=[r for r in rows[1:] if len(r)>=4 and r[0]=="vocab_pair"]
vc=count(vr); pc=count(pr)
assert allc=={"reviewed":4017,"fixed_rechecked":487,"pending":1327,"blocked":16}
assert vc=={"reviewed":3412,"fixed_rechecked":485,"pending":1,"blocked":16}
assert pc=={"reviewed":54,"fixed_rechecked":1,"pending":804,"blocked":0}
remaining=[int(r[1]) for r in vr if r[3]=="blocked"]
cp.update({
 "candidate_sha256":p["candidate_sha256"],"candidate_blob_sha":p["candidate_blob_sha"],
 "candidate_bytes":p["candidate_bytes"],"technical_verification":"passed",
 "chromium_verification":"passed","semantic_review":"passed_manual_author_review",
 "semantic_review_contexts":24,"registry_credit_applied":True,
 "author_credit_after":f"{vc['reviewed']+vc['fixed_rechecked']}/3914",
 "registry_counts_after":{"overall":allc,"vocabulary":vc,"lexical_pairs":pc},
 "remaining_blocked_ids":remaining,"pilot_credit_applied":0,"main_publication":False,
 "status":"12 cards fixed_rechecked; author semantic review and technical/Chromium checks passed; ready for guarded main publication",
 "meaning_quiz_structure":"24 contexts manually reviewed; three unique distractors, correct-answer exclusion, stable samples and length ratio <=1.5 verified",
 "workflow_run_id":int(os.environ.get("GITHUB_RUN_ID","0"))
})
(w/"checkpoint.json").write_text(json.dumps(cp,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")
summary={"pass":True,"technical_verification":"passed","chromium_verification":"passed",
 "semantic_quiz_review":"passed_manual_author_review","semantic_contexts_reviewed":24,
 "registry_credit_applied":True,"main_publication":False,
 "author_credit_after":cp["author_credit_after"],"registry_counts_after":cp["registry_counts_after"],
 "remaining_blocked_ids":remaining,"candidate_sha256":p["candidate_sha256"],
 "candidate_blob_sha":p["candidate_blob_sha"],"candidate_bytes":p["candidate_bytes"],
 "workflow_run_id":cp["workflow_run_id"]}
(w/"finalize-results.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")
(w/"review-register-results.json").write_text(json.dumps(cp["registry_counts_after"],ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")
print(json.dumps(summary,ensure_ascii=False,indent=2))
