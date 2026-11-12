#!/usr/bin/env python3
"""Guarded publication of the verified v176 C10 follow-up release."""
from __future__ import annotations
import csv
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "completion" / "v176-work"

def git(args, cwd=ROOT, check=True):
    result = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=False)
    if check and result.returncode:
        raise RuntimeError("git " + " ".join(args) + " failed: " + result.stderr[-4000:])
    return result.stdout.strip()

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def main():
    marker = json.loads((WORK / "PUBLISH").read_text(encoding="utf-8"))
    expected_main = marker["expected_main_sha"]
    prepared = json.loads((WORK / "prepare-results.json").read_text(encoding="utf-8"))
    browser = json.loads((WORK / "browser-results.json").read_text(encoding="utf-8"))
    registry_results = json.loads((WORK / "registry-results.json").read_text(encoding="utf-8"))
    expected_hash = prepared["checkpoint_sha256"]
    require(git(["branch", "--show-current"]) == "work/v176-c10-remaining-open-ids",
            "refusing publication from an unexpected branch")
    html = ROOT / "JLPT_N1_ukrainian_reading_v176.html"
    actual_hash = hashlib.sha256(html.read_bytes()).hexdigest()
    require(actual_hash == expected_hash and prepared.get("pass") is True,
            "v176 HTML does not match deterministic preparation")
    require(prepared.get("base_sha256") == "c3083a18181429e29fb1d63dcc4e9d39c5d68ccde49253b4f572820b27e1fb86"
            and prepared.get("changed_ids") == ["278", "330", "332", "335", "339", "347", "349", "350", "353", "355"]
            and prepared.get("operations") == 10
            and prepared.get("pair_reviewed_without_change") == [72, 81, 85, 167]
            and prepared.get("unresolved_pos_ids") == ["255", "327"]
            and prepared.get("exact_rollback") is True
            and prepared.get("vocabulary_records") == 3914
            and prepared.get("grammar_records") == 130
            and prepared.get("lexical_pairs") == 859,
            "v176 exact scope or structural evidence mismatch")
    require(browser.get("pass") is True and browser.get("sha256") == expected_hash
            and browser.get("cardsChecked") == 12 and browser.get("fieldsChecked") == 10
            and browser.get("pairsChecked") == 4 and browser.get("progressStorageUnchanged") is True,
            "Chromium evidence does not match the release HTML")
    require(set(x.get("width") for x in browser.get("widths", [])) == {360, 412, 1280}
            and all(x.get("pass") is True and x.get("cardsRendered") == [True] * 12
                    for x in browser.get("widths", [])),
            "missing or failed viewport rendering checks")
    require({x["id"]: x["proposedCount"] for x in browser.get("posDiagnostics", [])}
            == {"255": 0, "278": 0, "327": 2}
            and all(x.get("currentCount", 0) >= 3 for x in browser.get("posDiagnostics", [])),
            "POS/reading-pool diagnostic mismatch")
    require(registry_results.get("pass") is True
            and registry_results.get("registry_counts") == {
                "reviewed": 3885, "fixed_rechecked": 37, "pending": 1920
            }
            and registry_results.get("vocabulary_counts") == {
                "reviewed": 3325, "fixed_rechecked": 36, "pending": 553
            }
            and registry_results.get("lexical_pair_counts") == {"reviewed": 14, "pending": 845}
            and registry_results.get("author_credit") == "3361/3914"
            and registry_results.get("independent_acceptance") is False
            and registry_results.get("physical_acceptance") is False,
            "v176 author register evidence mismatch")

    with (ROOT / "completion" / "v176-acceptance.tsv").open(encoding="utf-8") as f:
        acceptance = list(csv.DictReader(f, delimiter="\t"))
    require([row["id"] for row in acceptance] == ["278", "330", "332", "335", "339", "347", "349", "350", "353", "355"]
            and all(row["decision"].startswith("fixed_rechecked") for row in acceptance),
            "v176 acceptance file has an unexpected card scope")
    with (ROOT / "completion" / "v176-pair-review.tsv").open(encoding="utf-8") as f:
        pair_rows = list(csv.DictReader(f, delimiter="\t"))
    require([row["pair_index"] for row in pair_rows] == ["72", "81", "85", "167"]
            and all(row["decision"] == "reviewed unchanged after author review" for row in pair_rows),
            "v176 pair-review file has an unexpected scope")
    with (ROOT / "completion" / "review-register.csv").open(encoding="utf-8", newline="") as f:
        register = list(csv.DictReader(f))
    counts = {}
    for row in register:
        counts[row["finalReview"]] = counts.get(row["finalReview"], 0) + 1
    require(counts == {"reviewed": 3885, "fixed_rechecked": 37, "pending": 1920},
            "v176 active registry count mismatch: " + repr(counts))
    audit = (ROOT / "JLPT_N1_v176_audit.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    backlog = (ROOT / "completion" / "BACKLOG.md").read_text(encoding="utf-8")
    require(expected_hash in audit and "не є незалежною" in audit.lower(),
            "v176 audit lacks exact hash or acceptance boundary")
    require("v176" in readme and "3361 із 3914" in readme
            and "v176" in status and "work/v176-c10-remaining-open-ids" in status
            and "v176" in backlog,
            "README, PROJECT_STATUS or BACKLOG does not identify v176")

    required = [
        html, ROOT / "JLPT_N1_v176_audit.md",
        ROOT / "completion" / "v176-acceptance.tsv",
        ROOT / "completion" / "v176-pair-review.tsv",
        WORK / "prepare-results.json",
        WORK / "browser-results.json",
        WORK / "registry-results.json",
        ROOT / "completion" / "C10-followup-255-355-20261113.md",
        ROOT / "completion" / "review-register.csv",
        ROOT / "README.md", ROOT / "PROJECT_STATUS.md",
        ROOT / "completion" / "BACKLOG.md",
        WORK / "prepare.py", WORK / "browser.cjs",
        WORK / "finalize-evidence.py", WORK / "publish-main.py",
        WORK / "updates.json", WORK / "pair-review.tsv",
        ROOT / ".github" / "workflows" / "v176-c10.yml",
    ]
    for path in required:
        require(path.is_file(), "publication source missing: " + str(path.relative_to(ROOT)))

    git(["fetch", "origin", "main"])
    remote_main = git(["rev-parse", "origin/main"])
    require(remote_main == expected_main,
            "main moved since v176 preparation: expected " + expected_main + ", got " + remote_main)
    target_path = "JLPT_N1_ukrainian_reading_v176.html"
    exists = subprocess.run(["git", "cat-file", "-e", "origin/main:" + target_path],
                            cwd=ROOT, text=True, capture_output=True, check=False)
    require(exists.returncode != 0, target_path + " already exists on main; refusing overwrite")

    temp_parent = Path(tempfile.mkdtemp(prefix="jlpt-n1-v176-main-"))
    temp = temp_parent / "main"
    added = False
    try:
        git(["worktree", "add", "--detach", str(temp), "origin/main"])
        added = True
        copies = {
            html: target_path,
            ROOT / "JLPT_N1_v176_audit.md": "JLPT_N1_v176_audit.md",
            ROOT / "completion" / "v176-acceptance.tsv": "completion/v176-acceptance.tsv",
            ROOT / "completion" / "v176-pair-review.tsv": "completion/v176-pair-review.tsv",
            WORK / "prepare-results.json": "completion/v176-prepare-results.json",
            WORK / "browser-results.json": "completion/v176-browser-results.json",
            WORK / "registry-results.json": "completion/v176-registry-results.json",
            ROOT / "completion" / "C10-followup-255-355-20261113.md": "completion/C10-followup-255-355-20261113.md",
            ROOT / "completion" / "review-register.csv": "completion/review-register.csv",
            ROOT / "README.md": "README.md",
            ROOT / "PROJECT_STATUS.md": "PROJECT_STATUS.md",
            ROOT / "completion" / "BACKLOG.md": "completion/BACKLOG.md",
            WORK / "prepare.py": "completion/v176-work/prepare.py",
            WORK / "browser.cjs": "completion/v176-work/browser.cjs",
            WORK / "finalize-evidence.py": "completion/v176-work/finalize-evidence.py",
            WORK / "publish-main.py": "completion/v176-work/publish-main.py",
            WORK / "updates.json": "completion/v176-work/updates.json",
            WORK / "pair-review.tsv": "completion/v176-work/pair-review.tsv",
            ROOT / ".github" / "workflows" / "v176-c10.yml": ".github/workflows/v176-c10.yml",
        }
        targets = []
        for source, relative in copies.items():
            destination = temp / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
            targets.append(relative)
        git(["config", "user.name", "github-actions[bot]"], cwd=temp)
        git(["config", "user.email", "41898282+actions@users.noreply.github.com"], cwd=temp)
        git(["add", "--", *targets], cwd=temp)
        staged = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=temp,
                                text=True, capture_output=True, check=False)
        require(staged.returncode != 0, "publication tree contains no changes")
        git(["commit", "-m", "Publish verified JLPT N1 v176 C10 follow-up release"], cwd=temp)
        commit_sha = git(["rev-parse", "HEAD"], cwd=temp)
        blob_sha = git(["rev-parse", "HEAD:" + target_path], cwd=temp)
        git(["push", "origin", "HEAD:main"], cwd=temp)
        git(["fetch", "origin", "main"])
        published = git(["rev-parse", "origin/main"])
        require(published == commit_sha, "post-push main SHA mismatch")
        remote_html = subprocess.run(["git", "show", "origin/main:" + target_path],
                                     cwd=ROOT, text=False, capture_output=True, check=True).stdout
        require(hashlib.sha256(remote_html).hexdigest() == expected_hash,
                "published HTML bytes do not match tested candidate")
        print(json.dumps({
            "pass": True, "main_commit": commit_sha, "html_blob_sha": blob_sha,
            "html_sha256": expected_hash, "html_bytes": len(remote_html), "files": targets
        }, ensure_ascii=False, indent=2))
    finally:
        if added:
            git(["worktree", "remove", "--force", str(temp)], check=False)
        shutil.rmtree(temp_parent, ignore_errors=True)

if __name__ == "__main__":
    main()
