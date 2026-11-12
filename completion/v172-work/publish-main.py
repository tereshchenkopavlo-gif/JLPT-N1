#!/usr/bin/env python3
"""Guarded publication of the verified v172 C10 follow-up release."""
from __future__ import annotations
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "completion" / "v172-work"

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
    require(git(["branch", "--show-current"]) == "work/v172-c10-followups",
            "refusing publication from an unexpected branch")
    checkpoint = ROOT / "JLPT_N1_ukrainian_reading_v172.html"
    actual_hash = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    require(actual_hash == expected_hash, "checkpoint SHA-256 differs from PUBLISH marker")

    prepared = json.loads((WORK / "prepare-results.json").read_text(encoding="utf-8"))
    browser = json.loads((WORK / "browser-results.json").read_text(encoding="utf-8"))
    registry_results = json.loads((WORK / "registry-results.json").read_text(encoding="utf-8"))
    require(prepared.get("pass") is True and prepared.get("checkpoint_sha256") == expected_hash,
            "deterministic preparation did not pass for the expected HTML")
    require(prepared.get("operations") == 17 and prepared.get("cards_corrected") == 13
            and prepared.get("vocabulary_records") == 3914 and prepared.get("grammar_records") == 130
            and prepared.get("exact_rollback") is True,
            "preparation evidence does not match the exact v172 scope")
    require(browser.get("pass") is True and browser.get("sha256") == expected_hash,
            "Chromium evidence does not match the exact v172 HTML")
    require(browser.get("quizEligibility", {}).get("records") == 3914
            and browser.get("quizEligibility", {}).get("unchanged") is True,
            "quiz eligibility changed unexpectedly")
    render_checks = browser.get("cardRenderChecks", {})
    require(browser.get("cardsChecked") == 13 and browser.get("translationsChecked") == 11
            and render_checks.get("progressStorageUnchanged") is True
            and len(render_checks.get("checked", [])) == 13
            and all(x.get("mainTranslation") and x.get("exampleTranslations") and x.get("usage")
                    for x in render_checks.get("checked", [])),
            "card rendering or progress-preservation checks are incomplete")
    require(set(x.get("width") for x in browser.get("widths", [])) == {360, 412, 1280},
            "missing POS filter viewport checks")
    require(all(x.get("pass") is True for x in browser.get("widths", [])),
            "a POS filter viewport check failed")
    require(len(browser.get("renderedExamples", [])) == 11
            and all(x.get("expectedValue") and x.get("exampleRendered") and x.get("translationRendered")
                    for x in browser.get("renderedExamples", [])),
            "not all corrected example translations rendered")
    require(browser.get("id3757Target", {}).get("pass") is True,
            "ID3757 exact target mapping failed")
    require(registry_results.get("pass") is True
            and registry_results.get("card_acceptances") == 13
            and registry_results.get("pair_reviews") == 5
            and registry_results.get("registry_counts") == {
                "reviewed": 3874, "fixed_rechecked": 14, "pending": 1954
            }, "review register evidence does not match the accepted scope")

    required = [
        ROOT / "JLPT_N1_v172_audit.md",
        ROOT / "completion" / "v172-acceptance.tsv",
        ROOT / "completion" / "v172-pair-review.tsv",
        ROOT / "README.md",
        ROOT / "PROJECT_STATUS.md",
        ROOT / "completion" / "BACKLOG.md",
        ROOT / "completion" / "review-register.csv",
        ROOT / "completion" / "feedback-20261112-grammar.md",
        ROOT / "completion" / "C10-followup-3701-3716-20261112.md",
        ROOT / "completion" / "C10-followup-3723-3739-20261112.md",
        ROOT / "completion" / "C10-followup-3742-3757-20261112.md",
    ]
    for path in required:
        require(path.is_file(), f"publication source is missing: {path.relative_to(ROOT)}")
    audit = (ROOT / "JLPT_N1_v172_audit.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    backlog = (ROOT / "completion" / "BACKLOG.md").read_text(encoding="utf-8")
    register = (ROOT / "completion" / "review-register.csv").read_text(encoding="utf-8")
    require(expected_hash in audit and "3701" in audit and "3757" in audit,
            "audit does not identify the exact checkpoint and reviewed IDs")
    require("v172" in readme and "v172" in status and "v172" in backlog
            and "3336 із 3914" in readme and "3336 із 3914" in status,
            "README/status/backlog do not point to v172 or the accepted-card count")
    require("3761" in backlog and "3764" in backlog,
            "remaining C10 IDs 3761/3764 are not retained in BACKLOG")
    require("| C27 |" in backlog and "**done**" in backlog.split("| C27 |", 1)[1].splitlines()[0],
            "previous C27 completion was not preserved")
    for id in (3701,3710,3716,3723,3724,3725,3736,3739,3742,3745,3747,3753,3757):
        require(f"vocab,{id},vocab:{id},fixed_rechecked," in register,
                f"vocabulary ID {id} is not fixed_rechecked")
    for key in ("817:3702:3710","819:3706:3723","821:3725:3726","822:3736:3737","823:3742:3759"):
        require(f"vocab_pair,{key}," in register and f"vocab_pair,{key}," in register and "completion/v172-pair-review.tsv" in register,
                f"pair {key} lacks v172 review evidence")

    for name in ("C10-followup-3701-3716-20261112.md",
                 "C10-followup-3723-3739-20261112.md",
                 "C10-followup-3742-3757-20261112.md"):
        require("Результат v172" in (ROOT / "completion" / name).read_text(encoding="utf-8"),
                f"{name} has no v172 resolution section")
    require(marker.get("data_check_run") and marker.get("chromium_run"),
            "PUBLISH marker must identify successful data and Chromium runs")
    git(["fetch", "origin", "main"])
    remote_main = git(["rev-parse", "origin/main"])
    require(remote_main == expected_main,
            f"main moved since the v172 checkpoint: expected {expected_main}, got {remote_main}")
    target_html = "JLPT_N1_ukrainian_reading_v172.html"
    exists = subprocess.run(["git","cat-file","-e",f"origin/main:{target_html}"],
                            cwd=ROOT,text=True,capture_output=True,check=False)
    require(exists.returncode != 0, f"{target_html} already exists on main; refusing overwrite")

    temp_parent = Path(tempfile.mkdtemp(prefix="jlpt-n1-v172-main-"))
    temp = temp_parent / "main"
    added = False
    try:
        git(["worktree","add","--detach",str(temp),"origin/main"])
        added = True
        copies = {
            checkpoint: target_html,
            ROOT / "JLPT_N1_v172_audit.md": "JLPT_N1_v172_audit.md",
            ROOT / "completion" / "v172-acceptance.tsv": "completion/v172-acceptance.tsv",
            ROOT / "completion" / "v172-pair-review.tsv": "completion/v172-pair-review.tsv",
            WORK / "prepare-results.json": "completion/v172-prepare-results.json",
            WORK / "browser-results.json": "completion/v172-browser-results.json",
            WORK / "registry-results.json": "completion/v172-registry-results.json",
            ROOT / "README.md": "README.md",
            ROOT / "PROJECT_STATUS.md": "PROJECT_STATUS.md",
            ROOT / "completion" / "BACKLOG.md": "completion/BACKLOG.md",
            ROOT / "completion" / "review-register.csv": "completion/review-register.csv",
            ROOT / "completion" / "feedback-20261112-grammar.md": "completion/feedback-20261112-grammar.md",
            ROOT / "completion" / "C10-followup-3701-3716-20261112.md": "completion/C10-followup-3701-3716-20261112.md",
            ROOT / "completion" / "C10-followup-3723-3739-20261112.md": "completion/C10-followup-3723-3739-20261112.md",
            ROOT / "completion" / "C10-followup-3742-3757-20261112.md": "completion/C10-followup-3742-3757-20261112.md",
            WORK / "inspect-targets.json": "completion/v172-target-inspection.json",
            WORK / "updates.json": "completion/v172-updates.json",
        }
        targets=[]
        for source,relative in copies.items():
            destination=temp/relative
            destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,destination)
            targets.append(relative)
        git(["config","user.name","github-actions[bot]"],cwd=temp)
        git(["config","user.email","41898282+actions@users.noreply.github.com"],cwd=temp)
        git(["add","--",*targets],cwd=temp)
        staged=subprocess.run(["git","diff","--cached","--quiet"],cwd=temp,text=True,capture_output=True,check=False)
        require(staged.returncode!=0,"publication tree contains no changes")
        git(["commit","-m","Publish verified JLPT N1 v172 C10 follow-up release"],cwd=temp)
        commit_sha=git(["rev-parse","HEAD"],cwd=temp)
        git(["push","origin","HEAD:main"],cwd=temp)
        git(["fetch","origin","main"])
        published=git(["rev-parse","origin/main"])
        require(published==commit_sha,f"post-push main SHA mismatch: expected {commit_sha}, got {published}")
        print(json.dumps({"pass":True,"main_commit":commit_sha,"html_sha256":actual_hash,
                          "html_bytes":checkpoint.stat().st_size,"files":targets},ensure_ascii=False,indent=2))
    finally:
        if added:
            git(["worktree","remove","--force",str(temp)],check=False)
        shutil.rmtree(temp_parent,ignore_errors=True)

if __name__=="__main__":
    main()
