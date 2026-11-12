#!/usr/bin/env python3
"""Guarded publication of the verified v174 C10 follow-up release."""
from __future__ import annotations
import csv
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "completion" / "v174-work"

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
    require(git(["branch", "--show-current"]) == "work/v174-c10-remaining-open-ids",
            "refusing publication from an unexpected branch")

    html = ROOT / "JLPT_N1_ukrainian_reading_v174.html"
    actual_hash = hashlib.sha256(html.read_bytes()).hexdigest()
    require(actual_hash == expected_hash, "v174 HTML SHA-256 differs from PUBLISH marker")
    prepared = json.loads((WORK / "prepare-results.json").read_text(encoding="utf-8"))
    browser = json.loads((WORK / "browser-results.json").read_text(encoding="utf-8"))
    registry_results = json.loads((WORK / "registry-results.json").read_text(encoding="utf-8"))
    require(prepared.get("pass") is True and prepared.get("checkpoint_sha256") == expected_hash,
            "deterministic preparation evidence does not match the release HTML")
    require(prepared.get("base_sha256") == "e04cad2441928457d359bd7fb9f42123bf6eec75ffac104db671f1d51edf6d6f"
            and prepared.get("changed_ids") == ["3828", "3836", "3900"]
            and prepared.get("changed_fields") == ["3828.exampleTranslations.0", "3836.exampleTranslations.1", "3900.exampleTranslations.0"]
            and prepared.get("operations") == 3 and prepared.get("exact_rollback") is True
            and prepared.get("reviewed_without_change") == [3820]
            and prepared.get("vocabulary_records") == 3914 and prepared.get("grammar_records") == 130
            and prepared.get("lexical_pairs") == 859,
            "v174 preparation evidence does not match the exact three-field scope")
    require(browser.get("pass") is True and browser.get("sha256") == expected_hash
            and browser.get("changedIds") == ["3828", "3836", "3900"]
            and browser.get("cardsChecked") == 4 and browser.get("translationsChecked") == 3
            and browser.get("progressStorageUnchanged") is True,
            "Chromium evidence does not match the release HTML")
    require(set(x.get("width") for x in browser.get("widths", [])) == {360, 412, 1280}
            and all(x.get("pass") is True and x.get("cardsRendered") == [True, True, True, True]
                    for x in browser.get("widths", [])),
            "missing or failed viewport rendering checks")
    require(len(browser.get("renderedCards", [])) == 4
            and all(x.get("expectedTranslation") and x.get("cardRendered")
                    and x.get("exampleRendered") and x.get("translationRendered")
                    for x in browser.get("renderedCards", [])),
            "not all four reviewed cards rendered their expected translations")
    require(registry_results.get("pass") is True
            and registry_results.get("registry_counts") == {
                "reviewed": 3875, "fixed_rechecked": 19, "pending": 1948
            } and registry_results.get("author_credit") == "3342/3914"
            and registry_results.get("independent_acceptance") is False
            and registry_results.get("physical_acceptance") is False,
            "author acceptance register evidence does not match v174")

    with (ROOT / "completion" / "v174-acceptance.tsv").open(encoding="utf-8") as f:
        acceptance = list(csv.DictReader(f, delimiter="\t"))
    require([row["id"] for row in acceptance] == ["3820", "3828", "3836", "3900"]
            and acceptance[0]["decision"] == "reviewed unchanged after author review"
            and all(row["decision"].startswith("fixed_rechecked after exact field review and Chromium regression")
                    for row in acceptance[1:]),
            "v174 acceptance file does not contain the exact four author decisions")
    register = (ROOT / "completion" / "review-register.csv").read_text(encoding="utf-8")
    require("vocab,3820,vocab:3820,reviewed," in register,
            "ID3820 is not reviewed in the active registry")
    for id in (3828, 3836, 3900):
        require(f"vocab,{id},vocab:{id},fixed_rechecked," in register,
                f"ID{id} is not fixed_rechecked in the active registry")
    audit = (ROOT / "JLPT_N1_v174_audit.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    backlog = (ROOT / "completion" / "BACKLOG.md").read_text(encoding="utf-8")
    require(expected_hash in audit and all(str(x) in audit for x in (3820, 3828, 3836, 3900))
            and "не незалежна" in audit.lower(),
            "audit is missing exact release hash, IDs or acceptance boundary")
    require("v174" in readme and "3342 із 3914" in readme
            and "v174" in status and "3342/3914" in status
            and "work/v175-c10-remaining-open-ids" in status,
            "README or status does not identify the release and next checkpoint")
    require("v174" in backlog and all(str(x) in backlog for x in (3820, 3828, 3836, 3900)),
            "BACKLOG does not preserve the v174 C10 result")

    required = [
        html, ROOT / "JLPT_N1_v174_audit.md",
        ROOT / "completion" / "v174-acceptance.tsv",
        ROOT / "completion" / "C10-followup-3820-3900-20261113.md",
        ROOT / "completion" / "review-register.csv",
        ROOT / "README.md", ROOT / "PROJECT_STATUS.md",
        ROOT / "completion" / "BACKLOG.md",
        WORK / "prepare-results.json", WORK / "browser-results.json",
        WORK / "registry-results.json", WORK / "updates.json",
        ROOT / ".github" / "workflows" / "v171-grammar-order-ci.yml",
        WORK / "prepare.py", WORK / "browser.cjs",
        WORK / "finalize-evidence.py", WORK / "publish-main.py"
    ]
    for path in required:
        require(path.is_file(), f"publication source missing: {path.relative_to(ROOT)}")

    git(["fetch", "origin", "main"])
    remote_main = git(["rev-parse", "origin/main"])
    require(remote_main == expected_main,
            f"main moved since v174 preparation: expected {expected_main}, got {remote_main}")
    target_path = "JLPT_N1_ukrainian_reading_v174.html"
    exists = subprocess.run(["git", "cat-file", "-e", f"origin/main:{target_path}"],
                            cwd=ROOT, text=True, capture_output=True, check=False)
    require(exists.returncode != 0, f"{target_path} already exists on main; refusing overwrite")

    temp_parent = Path(tempfile.mkdtemp(prefix="jlpt-n1-v174-main-"))
    temp = temp_parent / "main"
    added = False
    try:
        git(["worktree", "add", "--detach", str(temp), "origin/main"])
        added = True
        copies = {
            html: target_path,
            ROOT / "JLPT_N1_v174_audit.md": "JLPT_N1_v174_audit.md",
            ROOT / "completion" / "v174-acceptance.tsv": "completion/v174-acceptance.tsv",
            WORK / "prepare-results.json": "completion/v174-prepare-results.json",
            WORK / "browser-results.json": "completion/v174-browser-results.json",
            WORK / "registry-results.json": "completion/v174-registry-results.json",
            WORK / "updates.json": "completion/v174-updates.json",
            ROOT / "completion" / "C10-followup-3820-3900-20261113.md": "completion/C10-followup-3820-3900-20261113.md",
            ROOT / "completion" / "review-register.csv": "completion/review-register.csv",
            ROOT / "README.md": "README.md",
            ROOT / "PROJECT_STATUS.md": "PROJECT_STATUS.md",
            ROOT / "completion" / "BACKLOG.md": "completion/BACKLOG.md",
            ROOT / ".github" / "workflows" / "v171-grammar-order-ci.yml": ".github/workflows/v171-grammar-order-ci.yml",
            WORK / "prepare.py": "completion/v174-work/prepare.py",
            WORK / "browser.cjs": "completion/v174-work/browser.cjs",
            WORK / "finalize-evidence.py": "completion/v174-work/finalize-evidence.py",
            WORK / "publish-main.py": "completion/v174-work/publish-main.py",
            WORK / "updates.json": "completion/v174-work/updates.json",
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
        git(["commit", "-m", "Publish verified JLPT N1 v174 C10 follow-up release"], cwd=temp)
        commit_sha = git(["rev-parse", "HEAD"], cwd=temp)
        blob_sha = git(["rev-parse", f"HEAD:{target_path}"], cwd=temp)
        git(["push", "origin", "HEAD:main"], cwd=temp)
        git(["fetch", "origin", "main"])
        published = git(["rev-parse", "origin/main"])
        require(published == commit_sha, f"post-push main SHA mismatch: expected {commit_sha}, got {published}")
        remote_html = subprocess.run(["git", "show", f"origin/main:{target_path}"],
                                      cwd=ROOT, text=False, capture_output=True, check=True).stdout
        require(hashlib.sha256(remote_html).hexdigest() == expected_hash,
                "published HTML bytes do not match the tested candidate")
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
