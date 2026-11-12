#!/usr/bin/env python3
"""Guarded publication of the verified v175 C10 follow-up release."""
from __future__ import annotations
import csv
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "completion" / "v175-work"

def git(args, cwd=ROOT, check=True):
    result = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=False)
    if check and result.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed ({result.returncode}): {result.stderr[-4000:]}")
    return result.stdout.strip()

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def main():
    marker = json.loads((WORK / "PUBLISH").read_text(encoding="utf-8"))
    expected_main = marker["expected_main_sha"]
    expected_hash = marker["checkpoint_sha256"]
    require(git(["branch", "--show-current"]) == "work/v175-c10-remaining-open-ids",
            "refusing publication from an unexpected branch")

    html = ROOT / "JLPT_N1_ukrainian_reading_v175.html"
    actual_hash = hashlib.sha256(html.read_bytes()).hexdigest()
    require(actual_hash == expected_hash, "v175 HTML SHA-256 differs from PUBLISH marker")
    prepared = json.loads((WORK / "prepare-results.json").read_text(encoding="utf-8"))
    browser = json.loads((WORK / "browser-results.json").read_text(encoding="utf-8"))
    registry_results = json.loads((WORK / "registry-results.json").read_text(encoding="utf-8"))
    require(prepared.get("pass") is True and prepared.get("checkpoint_sha256") == expected_hash,
            "deterministic preparation evidence does not match release HTML")
    require(prepared.get("base_sha256") == "a012b3d50685353354417e89f4d6ab2767c8003ce1d77b4ff84ef85c77ed8c20"
            and prepared.get("changed_ids") == ["3802", "3807", "3808", "3809", "3810", "3812", "3814", "3816"]
            and prepared.get("operations") == 10
            and prepared.get("changed_fields") == [
                "3802.exampleTranslations.1", "3807.usage", "3807.exampleTranslations.0",
                "3808.exampleTranslations.0", "3809.exampleTranslations.1", "3810.t",
                "3812.exampleTranslations.1", "3814.usage", "3816.t", "3816.exampleTranslations.1"
            ]
            and prepared.get("exact_rollback") is True
            and prepared.get("reviewed_without_change") == [3803]
            and prepared.get("pair_reviewed_without_change") == [836, 838, 840, 841, 843]
            and prepared.get("vocabulary_records") == 3914 and prepared.get("grammar_records") == 130
            and prepared.get("lexical_pairs") == 859,
            "v175 preparation evidence does not match the exact ten-field scope")
    require(browser.get("pass") is True and browser.get("sha256") == expected_hash
            and browser.get("changedIds") == ["3802", "3807", "3808", "3809", "3810", "3812", "3814", "3816"]
            and browser.get("cardsChecked") == 9 and browser.get("fieldsChecked") == 10
            and browser.get("pairsChecked") == 5 and browser.get("progressStorageUnchanged") is True,
            "Chromium evidence does not match the release HTML")
    require(set(x.get("width") for x in browser.get("widths", [])) == {360, 412, 1280}
            and all(x.get("pass") is True and x.get("cardsRendered") == [True] * 9
                    for x in browser.get("widths", [])),
            "missing or failed viewport rendering checks")
    require(len(browser.get("renderedCards", [])) == 9
            and all(x.get("cardRendered") and x.get("allExamplesRendered")
                    and all(f.get("present") for f in x.get("fields", []))
                    for x in browser.get("renderedCards", [])),
            "not all reviewed cards rendered their expected fields")
    require(registry_results.get("pass") is True
            and registry_results.get("registry_counts") == {
                "reviewed": 3881, "fixed_rechecked": 27, "pending": 1934
            } and registry_results.get("author_credit") == "3351/3914"
            and registry_results.get("independent_acceptance") is False
            and registry_results.get("physical_acceptance") is False,
            "author acceptance register evidence does not match v175")

    with (ROOT / "completion" / "v175-acceptance.tsv").open(encoding="utf-8") as f:
        acceptance = list(csv.DictReader(f, delimiter="\t"))
    require([row["id"] for row in acceptance] == ["3802", "3803", "3807", "3808", "3809", "3810", "3812", "3814", "3816"]
            and acceptance[1]["decision"] == "reviewed unchanged after author review"
            and all(row["decision"].startswith("fixed_rechecked after exact field review and Chromium regression")
                    for row in acceptance if row["id"] != "3803"),
            "v175 acceptance file does not contain the exact nine author decisions")
    with (ROOT / "completion" / "v175-pair-review.tsv").open(encoding="utf-8") as f:
        pair_rows = list(csv.DictReader(f, delimiter="\t"))
    require([row["pair_index"] for row in pair_rows] == ["836", "838", "840", "841", "843"]
            and all(row["decision"] == "reviewed unchanged after author review" for row in pair_rows),
            "v175 pair-review file does not contain the exact five decisions")

    with (ROOT / "completion" / "review-register.csv").open(encoding="utf-8", newline="") as f:
        register_rows = list(csv.DictReader(f))
    counts = {}
    for row in register_rows:
        counts[row["finalReview"]] = counts.get(row["finalReview"], 0) + 1
    require(counts == {"reviewed": 3881, "fixed_rechecked": 27, "pending": 1934},
            f"active registry counts mismatch: {counts}")
    audit = (ROOT / "JLPT_N1_v175_audit.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    backlog = (ROOT / "completion" / "BACKLOG.md").read_text(encoding="utf-8")
    require(expected_hash in audit and all(str(x) in audit for x in (3802, 3803, 3807, 3808, 3809, 3810, 3812, 3814, 3816))
            and "не незалежне" in audit.lower(),
            "audit is missing exact release hash, IDs or acceptance boundary")
    require("v175" in readme and "3351 із 3914" in readme
            and "v175" in status and "3351/3914" in status
            and "work/v175-c10-remaining-open-ids" in status,
            "README or status does not identify v175 and its work branch")
    require("v175" in backlog and all(str(x) in backlog for x in (3802, 3803, 3807, 3808, 3809, 3810, 3812, 3814, 3816)),
            "BACKLOG does not preserve the v175 C10 result")

    required = [
        html, ROOT / "JLPT_N1_v175_audit.md",
        ROOT / "completion" / "v175-acceptance.tsv",
        ROOT / "completion" / "v175-pair-review.tsv",
        ROOT / "completion" / "C10-followup-3802-3816-20261113.md",
        ROOT / "completion" / "review-register.csv",
        ROOT / "README.md", ROOT / "PROJECT_STATUS.md",
        ROOT / "completion" / "BACKLOG.md",
        WORK / "prepare-results.json", WORK / "browser-results.json",
        WORK / "registry-results.json", WORK / "updates.json", WORK / "pair-review.tsv",
        ROOT / ".github" / "workflows" / "v175-c10.yml",
        WORK / "prepare.py", WORK / "browser.cjs",
        WORK / "finalize-evidence.py", WORK / "publish-main.py"
    ]
    for path in required:
        require(path.is_file(), f"publication source missing: {path.relative_to(ROOT)}")

    git(["fetch", "origin", "main"])
    remote_main = git(["rev-parse", "origin/main"])
    require(remote_main == expected_main,
            f"main moved since v175 preparation: expected {expected_main}, got {remote_main}")
    target_path = "JLPT_N1_ukrainian_reading_v175.html"
    exists = subprocess.run(["git", "cat-file", "-e", f"origin/main:{target_path}"],
                            cwd=ROOT, text=True, capture_output=True, check=False)
    require(exists.returncode != 0, f"{target_path} already exists on main; refusing overwrite")

    temp_parent = Path(tempfile.mkdtemp(prefix="jlpt-n1-v175-main-"))
    temp = temp_parent / "main"
    added = False
    try:
        git(["worktree", "add", "--detach", str(temp), "origin/main"])
        added = True
        copies = {
            html: target_path,
            ROOT / "JLPT_N1_v175_audit.md": "JLPT_N1_v175_audit.md",
            ROOT / "completion" / "v175-acceptance.tsv": "completion/v175-acceptance.tsv",
            ROOT / "completion" / "v175-pair-review.tsv": "completion/v175-pair-review.tsv",
            WORK / "prepare-results.json": "completion/v175-prepare-results.json",
            WORK / "browser-results.json": "completion/v175-browser-results.json",
            WORK / "registry-results.json": "completion/v175-registry-results.json",
            WORK / "updates.json": "completion/v175-updates.json",
            ROOT / "completion" / "C10-followup-3802-3816-20261113.md": "completion/C10-followup-3802-3816-20261113.md",
            ROOT / "completion" / "review-register.csv": "completion/review-register.csv",
            ROOT / "README.md": "README.md",
            ROOT / "PROJECT_STATUS.md": "PROJECT_STATUS.md",
            ROOT / "completion" / "BACKLOG.md": "completion/BACKLOG.md",
            ROOT / ".github" / "workflows" / "v175-c10.yml": ".github/workflows/v175-c10.yml",
            WORK / "prepare.py": "completion/v175-work/prepare.py",
            WORK / "browser.cjs": "completion/v175-work/browser.cjs",
            WORK / "finalize-evidence.py": "completion/v175-work/finalize-evidence.py",
            WORK / "publish-main.py": "completion/v175-work/publish-main.py",
            WORK / "updates.json": "completion/v175-work/updates.json",
            WORK / "pair-review.tsv": "completion/v175-work/pair-review.tsv",
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
        git(["commit", "-m", "Publish verified JLPT N1 v175 C10 follow-up release"], cwd=temp)
        commit_sha = git(["rev-parse", "HEAD"], cwd=temp)
        blob_sha = git(["rev-parse", f"HEAD:{target_path}"], cwd=temp)
        git(["push", "origin", "HEAD:main"], cwd=temp)
        git(["fetch", "origin", "main"])
        published = git(["rev-parse", "origin/main"])
        require(published == commit_sha, f"post-push main SHA mismatch: expected {commit_sha}, got {published}")
        remote_html = subprocess.run(["git", "show", f"origin/main:{target_path}"],
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
