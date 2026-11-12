#!/usr/bin/env python3
"""Create v173 card hashes and update only the two exact review-register rows."""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path
import re

BASE = Path("JLPT_N1_ukrainian_reading_v172.html")
TARGET = Path("JLPT_N1_ukrainian_reading_v173.html")
UPDATES = Path("completion/v173-work/updates.json")
REGISTRY = Path("completion/review-register.csv")
ACCEPTANCE = Path("completion/v173-acceptance.tsv")
IDS = [3761, 3764]

def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

def block(source, name):
    match = re.search(r"\\bconst\\s+" + re.escape(name) + r"\\s*=\\s*", source)
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
    base_html = BASE.read_text(encoding="utf-8")
    target_html = TARGET.read_text(encoding="utf-8")
    before = block(base_html, "VOCAB_DETAILS_BY_ID")
    after = block(target_html, "VOCAB_DETAILS_BY_ID")
    updates = {str(x["id"]): x for x in json.loads(UPDATES.read_text(encoding="utf-8"))}
    rows = []
    for id in IDS:
        old, new = before[str(id)], after[str(id)]
        row = updates[str(id)]
        if old["exampleTranslations"][1] != row["before"] or new["exampleTranslations"][1] != row["after"]:
            raise ValueError(f"Exact translation mismatch for {id}")
        restored = json.loads(json.dumps(new, ensure_ascii=False))
        restored["exampleTranslations"][1] = row["before"]
        if restored != old:
            raise ValueError(f"Unexpected changed field for {id}")
        rows.append({
            "id": id, "headword": new["w"],
            "before": digest(old), "after": digest(new),
            "changed": "exampleTranslations.1",
            "evidence": row["evidence"]
        })
    with ACCEPTANCE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\\t", lineterminator="\\n")
        writer.writerow(["id","headword","card_before_sha256","card_after_sha256","changed_fields","evidence","decision"])
        for row in rows:
            writer.writerow([row["id"],row["headword"],row["before"],row["after"],row["changed"],row["evidence"],"fixed_rechecked after exact field review and Chromium regression"])

    lines = REGISTRY.read_text(encoding="utf-8").splitlines()
    new_lines = []
    changed = 0
    for line in lines:
        replacement = None
        for id in IDS:
            prefix = f"vocab,{id},vocab:{id},pending,"
            if line == prefix:
                evidence = f'"completion/v173-acceptance.tsv#{id}; author recheck and Chromium regression; v173 SHA-256={hashlib.sha256(TARGET.read_bytes()).hexdigest()}"'
                replacement = f"vocab,{id},vocab:{id},fixed_rechecked,{evidence}"
                changed += 1
                break
            if line.startswith(f"vocab,{id},vocab:{id},fixed_rechecked,") and "completion/v173-acceptance.tsv" in line:
                replacement = line
                break
        new_lines.append(replacement if replacement is not None else line)
    if changed not in (0, 2):
        raise ValueError(f"Expected 0 or 2 registry transitions, got {changed}")
    if changed == 0 and not all(any(line.startswith(f"vocab,{id},vocab:{id},fixed_rechecked,") and "completion/v173-acceptance.tsv" in line for line in new_lines) for id in IDS):
        raise ValueError("Registry already has an unrelated status for a target ID")
    REGISTRY.write_text("\\n".join(new_lines) + "\\n", encoding="utf-8")

    counts = {}
    for line in new_lines[1:]:
        if line:
            status = line.split(",", 4)[3]
            counts[status] = counts.get(status, 0) + 1
    expected = {"reviewed": 3874, "fixed_rechecked": 16, "pending": 1952}
    if counts != expected:
        raise ValueError(f"Registry counts mismatch: {counts}")
    result = {
        "card_acceptances": 2,
        "newly_transitioned": changed,
        "registry_counts": counts,
        "author_credit": "3338/3914",
        "independent_acceptance": False,
        "physical_acceptance": False,
        "pass": True
    }
    Path("completion/v173-work/registry-results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
