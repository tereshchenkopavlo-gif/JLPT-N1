import csv, json, os
from collections import Counter
from pathlib import Path
W=Path("completion/v230-work")
p=json.loads((W/"prepare-results.json").read_text(encoding="utf-8"))
b=json.loads((W/"browser-results.json").read_text(encoding="utf-8"))
s=json.loads((W/"semantic-review.json").read_text(encoding="utf-8"))
cp=json.loads((W/"checkpoint.json").read_text(encoding="utf-8"))
ids=[3363,3375,3417,3441,3444,3525,3561,3565,3569,3594,3636,3646]
assert p["pass"] and b["pass"] and p["candidate_sha256"]==b["candidate_sha256"]
assert s["overall_decision"]=="pass" and s["scope"]==ids and s["context_count"]==24 and len(s["decisions"])==24
assert b["meaningStructurePass"] and b["meaningLengthPass"] and b["meaningDiagnosticCount"]==24
assert len(b["reviewedOverrideChecks"])==24 and all(x["correctMatch"] and x["wrongSetMatch"] and x["noteMatch"] for x in b["reviewedOverrideChecks"])
assert b["pageErrors"]==[] and b["storage"]["roundTrip"] and b["storage"]["restored"]
assert all(not x["overflow"] for x in b["responsive"])
assert len(b["rendered"])==12 and all(x["title"] and x["meaning"] and x["usageData"] and x["examples"] and x["translations"] and x["pos"]==x["expectedPos"] for x in b["rendered"])
assert all(x["clozeEligibleAfter"] for x in b["poolImpact"])
assert not [x for x in b["poolImpact"] if not x["readingEligibleBefore"] and x["readingEligibleAfter"]]
rp=Path("completion/review-register.csv")
with rp.open(encoding="utf-8",newline="") as f: rows=list(csv.reader(f))
assert rows[0]==["kind","key","baselineLocation","finalReview","evidence"] and len(rows)-1==5847
ev="JLPT_N1_v230_audit.md; completion/v230-acceptance.tsv; completion/v230-c11-review.tsv; completion/v230-semantic-review.md; C11 author POS/sense and 24-context quiz review; no v153 pilot credit"
found=set()
for r in rows[1:]:
    if len(r)>=5 and r[0]=="vocab" and r[1] in {str(i) for i in ids}:
        assert r[3]=="blocked", "unexpected card status "+r[1]
        r[3]="fixed_rechecked"; r[4]=ev; found.add(int(r[1]))
assert found==set(ids)
new_keys=[f"v_{i}" for i in ids if i!=3363]
existing={(r[0],r[1]) for r in rows[1:] if len(r)>=2}
for key in new_keys:
    assert ("reviewed_meaning_quiz",key) not in existing
    rows.append(["reviewed_meaning_quiz",key,"REVIEWED_MEANING_QUIZZES."+key,"reviewed",ev])
with rp.open("w",encoding="utf-8",newline="") as f: csv.writer(f,lineterminator="\n").writerows(rows)
def count(rs):
    c=Counter(r[3] for r in rs if len(r)>=4)
    return {k:c.get(k,0) for k in ("reviewed","fixed_rechecked","pending","blocked")}
allc=count(rows[1:]); vr=[r for r in rows[1:] if len(r)>=4 and r[0]=="vocab"]; pr=[r for r in rows[1:] if len(r)>=4 and r[0]=="vocab_pair"]
vc=count(vr); pc=count(pr)
assert allc=={"reviewed":4028,"fixed_rechecked":499,"pending":1327,"blocked":4},allc
assert vc=={"reviewed":3412,"fixed_rechecked":497,"pending":1,"blocked":4},vc
assert pc=={"reviewed":54,"fixed_rechecked":1,"pending":804,"blocked":0},pc
remaining=[int(r[1]) for r in vr if r[3]=="blocked"]
assert remaining==[3652,3654,3677,3679],remaining
pool=b["poolImpact"]
with (W/"pool-impact.tsv").open("w",encoding="utf-8",newline="") as f:
    w=csv.writer(f,delimiter="\t",lineterminator="\n")
    w.writerow(["id","word","pos_before","pos_after","reading_before","reading_after","cloze_before","cloze_after","reading_eligible_after","cloze_eligible_after"])
    for x in pool: w.writerow([x["id"],x["word"],"・".join(x["posBefore"]),"・".join(x["posAfter"]),x["readingBefore"],x["readingAfter"],x["clozeBefore"],x["clozeAfter"],str(x["readingEligibleAfter"]).lower(),str(x["clozeEligibleAfter"]).lower()])
with (W/"acceptance.tsv").open("w",encoding="utf-8",newline="") as f:
    w=csv.writer(f,delimiter="\t",lineterminator="\n")
    w.writerow(["id","word","decision","pos_before","pos_after","meaning_contexts","evidence"])
    for x in b["rendered"]:
        z=next(y for y in pool if y["id"]==x["id"])
        w.writerow([x["id"],x["word"],"fixed_rechecked","・".join(z["posBefore"]),"・".join(z["posAfter"]),2,"author POS/meaning review; browser verified"])
with (W/"c11-review.tsv").open("w",encoding="utf-8",newline="") as f:
    w=csv.writer(f,delimiter="\t",lineterminator="\n")
    w.writerow(["id","word","pos_before","pos_after","reading_before","reading_after","cloze_before","cloze_after","reading_eligible_after","cloze_eligible_after","decision"])
    for x in pool: w.writerow([x["id"],x["word"],"・".join(x["posBefore"]),"・".join(x["posAfter"]),x["readingBefore"],x["readingAfter"],x["clozeBefore"],x["clozeAfter"],x["readingEligibleAfter"],x["clozeEligibleAfter"],"fixed_rechecked"])
with (W/"field-changes.tsv").open("w",encoding="utf-8",newline="") as f:
    w=csv.writer(f,delimiter="\t",lineterminator="\n")
    w.writerow(["block","id_or_key","before","after","reason"])
    for k,v in p["pos_updates"].items(): w.writerow(["VOCAB_POS_BY_ID",k,json.dumps(v["before"],ensure_ascii=False),json.dumps(v["after"],ensure_ascii=False),"C11 POS-map reconciled with selected card senses and observed forms."])
    for k in new_keys: w.writerow(["REVIEWED_MEANING_QUIZZES",k,"absent","22 byExample contexts","Context-specific key, three distinct plausible distractors, balanced length; no quiz logic change."])
(W/"registry-results.json").write_text(json.dumps({"overall":allc,"vocabulary":vc,"lexical_pairs":pc,"reviewed_meaning_quiz_rows":sum(1 for r in rows[1:] if r[0]=="reviewed_meaning_quiz")},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
cp.update({"candidate_sha256":p["candidate_sha256"],"candidate_blob_sha":p["candidate_blob_sha"],"candidate_bytes":p["candidate_bytes"],"technical_verification":"passed","chromium_verification":"passed","semantic_review":"passed_manual_author_review","semantic_review_contexts":24,"new_context_overrides":22,"retained_context_overrides":2,"registry_credit_applied":True,"author_credit_after":"3909/3914","registry_counts_after":{"overall":allc,"vocabulary":vc,"lexical_pairs":pc},"remaining_blocked_ids":remaining,"pilot_credit_applied":0,"main_publication":False,"status":"12 cards fixed_rechecked; author POS/semantic review and Chromium checks passed; ready for guarded main publication","workflow_run_id":int(os.environ.get("GITHUB_RUN_ID","0"))})
(W/"checkpoint.json").write_text(json.dumps(cp,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
summary={"pass":True,"technical_verification":"passed","chromium_verification":"passed","semantic_quiz_review":"passed_manual_author_review","semantic_contexts_reviewed":24,"new_context_overrides":22,"retained_context_overrides":2,"registry_credit_applied":True,"main_publication":False,"author_credit_after":"3909/3914","registry_counts_after":{"overall":allc,"vocabulary":vc,"lexical_pairs":pc},"remaining_blocked_ids":remaining,"candidate_sha256":p["candidate_sha256"],"candidate_blob_sha":p["candidate_blob_sha"],"candidate_bytes":p["candidate_bytes"],"workflow_run_id":cp["workflow_run_id"]}
(W/"finalize-results.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
audit="""# JLPT N1 v230 — C11 POS and meaning-quiz audit

## Decision

12 previously blocked cards were manually reviewed for POS/sense alignment and 24 exact example contexts. All 12 are fixed_rechecked after POS-map reconciliation and context-specific meaning overrides. This is an author review, not independent acceptance.

- 12 cards: 3363, 3375, 3417, 3441, 3444, 3525, 3561, 3565, 3569, 3594, 3636, 3646.
- 12 POS-map updates.
- 11 new reviewed meaning-quiz keys, covering 22 contexts.
- ID3363's two existing v141 contexts were retained and rechecked for binding and answer-length balance; they were not counted as new override creation.
- 24/24 browser override checks, three unique distractors, correct-answer exclusion, and max/min length ratio <=1.5.
- No changes to vocabulary records, grammar, examples, translations, lexical pairs, reading overrides, target tables, learning logic, or storage keys.
- No v153 pilot credit: all IDs are outside the documented 121–320 pilot range.

## Card-level decisions

| ID | Entry | POS map after | Context handling |
|---:|---|---|---|
| 3363 | 相当 | 副詞・ナ形 | Existing global degree override retained; both examples checked |
| 3375 | 当面 | 名詞・副詞 | Separate byExample payloads for 当面の課題 and 当面は |
| 3417 | だぶだぶ | 副詞・ナ形 | Clothing looseness; both examples checked |
| 3441 | とろとろ | 副詞・ナ形 | Soft/melted food vs shallow dozing separated |
| 3444 | どろどろ | 副詞・ナ形 | Muddy material vs tangled human relationships separated |
| 3525 | オートマチック | 名詞・ナ形 | Automatic-transmission car vs automatic operation separated |
| 3561 | ジャンボ | 名詞・ナ形 | Extra-large size in both contexts |
| 3565 | タイムリー | ナ形 | Well-timed contexts |
| 3569 | コマーシャル | 名詞・ナ形 | Broadcast advertisement contexts |
| 3594 | ストレート | 名詞・ナ形 | Direct/forthright expression contexts |
| 3636 | プライベート | 名詞・ナ形 | Private/personal life; source confidence limitation documented |
| 3646 | モダン | 名詞・ナ形 | Contemporary style, distinct from merely new or briefly fashionable |

## Technical verification

Chromium workflow checks 3914 vocabulary records, 130 grammar constructions, 859 lexical pairs, unique stable IDs, protected data blocks, exact example-key binding, 12 rendered cards, POS labels, all 24 reviewed quiz contexts, option uniqueness/length balance, reading/cloze pool impact, responsive widths 360/412/1280, storage round-trip/restore, and zero page errors. Linux Chromium is not a physical Android/Windows test.

## Registry

Author credit after this batch: 3909/3914. Remaining blocked: 3652, 3654, 3677, 3679. ID1510 remains pending safety hold and was not assessed. Independent linguistic acceptance, physical Android/Windows acceptance, and provenance/legal review remain open.
"""
Path("JLPT_N1_v230_audit.md").write_text(audit,encoding="utf-8")
summary_text="""# v230 C11 review result

Baseline diagnostics are retained above. The author review now covers 12 cards and 24 exact example contexts. The POS map was reconciled for 12 IDs; 11 new byExample quiz keys cover 22 contexts, while the two existing ID3363 overrides were retained. Browser verification is separate from the author review. The register records 12 fixed_rechecked cards and 11 reviewed meaning-quiz keys. No v153 credit was applied.
"""
diagpath=W/"diagnostic-summary.md"
if diagpath.exists():
    existing=diagpath.read_text(encoding="utf-8")
    if "v230 C11 review result" not in existing: diagpath.write_text(existing.rstrip()+"\n\n"+summary_text,encoding="utf-8")
else: diagpath.write_text(summary_text,encoding="utf-8")
print(json.dumps(summary,ensure_ascii=False,indent=2))
