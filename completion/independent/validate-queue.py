"""Validate immutable packages, review linkage and active duplicate cases."""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATES = {"pending_review","in_review","reviewed_with_issues","reviewed_pass","corrections_pending","closed"}

def sha(value):
    return hashlib.sha256(value).hexdigest()

def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True).encode()

def check():
    p = argparse.ArgumentParser()
    p.add_argument("--candidate")
    args = p.parse_args()
    queue = json.loads((ROOT/"queue.json").read_text())
    seen, active, review_files = set(), {}, set()
    for row in queue["packages"]:
        id = row["package_id"]
        assert id not in seen, "Duplicate package ID"
        seen.add(id)
        assert row["status"] in STATES
        raw = (ROOT/row["path"]).read_bytes()
        assert sha(raw) == row["package_sha256"], id
        packet = json.loads(raw)
        assert packet["package_id"] == id
        assert packet["sources_sha256"] == row["sources_sha256"]
        assert sha(canonical(packet["cases"])) == packet["sources_sha256"]
        ids = [case["case_id"] for case in packet["cases"]]
        assert len(ids) == len(set(ids)), id
        commits = sorted({s["commit"] for c in packet["cases"] for s in c["sources"]})
        assert commits == row["source_commits"]
        assert all(re.fullmatch("[0-9a-f]{40}",s) for s in commits)
        for review in row["reviews"]:
            assert review["path"] not in review_files, "Review registered twice"
            review_files.add(review["path"])
            review_raw = (ROOT/review["path"]).read_bytes()
            assert sha(review_raw) == review["sha256"]
            report = json.loads(review_raw)
            assert report["package_id"] == id and report["sources_sha256"] == row["sources_sha256"]
            assert sorted(c["case_id"] for c in report["cases"]) == sorted(ids)
        if row["status"] in {"reviewed_pass","reviewed_with_issues","corrections_pending","closed"}:
            assert row["reviews"], "A received review is required"
        if row["status"] in {"pending_review","in_review"}:
            for case in packet["cases"]:
                key = (case["case_id"],sha(canonical(case["fields"])))
                assert key not in active, "Unchanged case is already pending"
                active[key] = id
    for row in queue["packages"]:
        if row["predecessor"]:
            assert row["predecessor"] in seen
    if args.candidate:
        candidate = json.loads(Path(args.candidate).read_text())
        assert candidate["package_id"] not in seen, "Package ID already registered"
        for case in candidate["cases"]:
            assert (case["case_id"],sha(canonical(case["fields"]))) not in active, "Unchanged material already queued"
    print("Queue validated: package checksums, source hashes, reviews and active-case uniqueness")

if __name__ == "__main__":
    check()
