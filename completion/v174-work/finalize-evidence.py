#!/usr/bin/env python3
"""Create v174 acceptance hashes and transition exactly four C10 registry rows."""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path
import re

BASE = Path("JLPT_N1_ukrainian_reading_v173.html")
TARGET = Path("JLPT_N1_ukrainian_reading_v174.html")
UPDATES = Path("completion/v174-work/updates.json")
REGISTRY = Path("completion/review-register.csv")
ACCEPTANCE = Path("completion/v174-acceptance.tsv")
IDS = [3820, 3828, 3836, 3900]

def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
def block(source, name):
    match = re.search(r"\bconst\s+" + re.escape(name) + r"\s*=\s*", source)
    if not match:
        raise ValueError(f"Missing {name}")
    start = match.end()
    value, end = json.JSONDecoder().raw_decode(source, start)
    if compact(value) != source[start:end]:
        raise ValueError(f"Unexpected serialization in {name}")
    return value
def digest(value):
    return hashlib.sha256(compact(value).encode("utf-8")).hexdigest()

def main():
    before = block(BASE.read_text(encoding="utf-8"), "VOCAB_DETAILS_BY_ID")
    after = block(TARGET.read_text(encoding="utf-8"), "VOCAB_DETAILS_BY_ID")
    updates = {str(x["id"]): x for x in json.loads(UPDATES.read_text(encoding="utf-8"))}
    rows = []
    # ID3820 was fully reviewed and accepted unchanged.
    if before["3820"] != after["3820"]:
        raise ValueError("ID3820 must remain byte-equivalent at card level")
    rows.append({
        "id": 3820, "headword": after["3820"]["w"],
        "before": digest(before["3820"]), "after": digest(after["3820"]),
        "changed": "none", "evidence": "completion/C10-followup-3820-3900-20261113.md#3820",
        "decision": "reviewed unchanged after author review"
    })
    for id in (3828, 3836, 3900):
        old, new, row = before[str(id)], after[str(id)], updates[str(id)]
        if old["w"] != row["headword"]:
            raise ValueError(f"Headword mismatch for {id}")
        index = int(row["field"].split(".")[-1])
        if old["exampleTranslations"][index] != row["before"] or new["exampleTranslations"][index] != row["after"]:
            raise ValueError(f"Translation mismatch for {id}")
        restored = json.loads(json.dumps(new, ensure_ascii=False))
        restored["exampleTranslations"][index] = row["before"]
        if restored != old:
            raise ValueError(f"Unexpected changed field in {id}")
        rows.append({
            "id": id, "headword": new["w"], "before": digest(old), "after": digest(new),
            "changed": row["field"], "evidence": row["evidence"],
            "decision": "fixed_rechecked after exact field review and Chromium regression"
        })
    with ACCEPTANCE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(["id","headword","card_before_sha256","card_after_sha256","changed_fields","evidence","decision"])
        for row in rows:
            writer.writerow([row["id"],row["headword"],row["before"],row["after"],row["changed"],row["evidence"],row["decision"]])

    lines = REGISTRY.read_text(encoding="utf-8").splitlines()
    new_lines, changed = [], 0
    for line in lines:
        replacement = None
        for id in IDS:
            if line == f"vocab,{id},vocab:{id},pending,":
                if id == 3820:
                    status = "reviewed"
                    evidence = f'"completion/v174-acceptance.tsv#{id}; author review, no content change; v174 SHA-256={hashlib.sha256(TARGET.read_bytes()).hexdigest()}"'
                else:
                    status = "fixed_rechecked"
                    evidence = f'"completion/v174-acceptance.tsv#{id}; author recheck and Chromium regression; v174 SHA-256={hashlib.sha256(TARGET.read_bytes()).hexdigest()}"'
                replacement = f"vocab,{id},vocab:{id},{status},{evidence}"
                changed += 1
                break
            if line.startswith(f"vocab,{id},vocab:{id},") and "completion/v174-acceptance.tsv" in line:
                replacement = line
                break
        new_lines.append(replacement if replacement is not None else line)
    if changed not in (0, 4):
        raise ValueError(f"Expected 0 or 4 registry transitions, got {changed}")
    if changed == 0:
        for id in IDS:
            expected_status = "reviewed" if id == 3820 else "fixed_rechecked"
            if not any(line.startswith(f"vocab,{id},vocab:{id},{expected_status},") and "completion/v174-acceptance.tsv" in line for line in new_lines):
                raise ValueError(f"Registry already has unrelated status for {id}")
    REGISTRY.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    counts = {}
    for line in new_lines[1:]:
        if line:
            status = line.split(",", 4)[3]
            counts[status] = counts.get(status, 0) + 1
    expected = {"reviewed": 3875, "fixed_rechecked": 19, "pending": 1948}
    if counts != expected:
        raise ValueError(f"Registry counts mismatch: {counts}")
    result = {
        "release_acceptances": 4,
        "newly_transitioned_this_run": changed,
        "reviewed_without_change": [3820],
        "fixed_rechecked": [3828, 3836, 3900],
        "registry_counts": counts,
        "author_credit": "3342/3914",
        "independent_acceptance": False,
        "physical_acceptance": False,
        "pass": True
    }
    Path("completion/v174-work/registry-results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
