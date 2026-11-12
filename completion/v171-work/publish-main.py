#!/usr/bin/env python3
"""Guarded publication of the verified v171 release from its work checkpoint."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "completion" / "v171-work"


def git(args: list[str], cwd: Path = ROOT, *, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, text=True, capture_output=True, check=False
    )
    if check and result.returncode:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({result.returncode}): "
            f"{result.stderr[-4000:]}"
        )
    return result.stdout.strip()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    marker = json.loads((WORK / "PUBLISH").read_text(encoding="utf-8"))
    expected_main = marker["expected_main_sha"]
    expected_hash = marker["checkpoint_sha256"]

    branch = git(["branch", "--show-current"])
    require(branch == "work/v171-grammar-order-checkpoint",
            f"refusing publication from unexpected branch: {branch!r}")

    checkpoint = ROOT / "JLPT_N1_v171_checkpoint.html"
    actual_hash = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    require(actual_hash == expected_hash, "checkpoint SHA-256 differs from PUBLISH marker")

    prepared = json.loads((WORK / "prepare-results.json").read_text(encoding="utf-8"))
    browser = json.loads((WORK / "grammar-order-results.json").read_text(encoding="utf-8"))
    require(prepared.get("pass") is True, "prepare-checkpoint guard did not pass")
    require(browser.get("pass") is True, "Chromium verification did not pass")
    require(prepared.get("checkpoint_sha256") == expected_hash, "prepare result hash mismatch")
    require(browser.get("sha256") == expected_hash, "browser result hash mismatch")
    require(prepared.get("grammar_records") == 130 and prepared.get("split_before_after") == 130,
            "not all 130 grammar records were split")
    results = {item["width"]: item for item in browser.get("results", [])}
    require(set(results) == {360, 412, 1280}, "missing viewport results")
    require(results[412].get("cardsChecked") == 130
            and results[412].get("cardLayouts") == 130
            and results[412].get("sessionLayouts") == 130
            and results[412].get("comparisonLayouts") == 130,
            "the 412px all-grammar verification is incomplete")
    require(results[412].get("vocabularyRecords") == 3914
            and results[412].get("grammarRecords") == 130
            and results[412].get("translatedMainExamples") == 261
            and results[412].get("g90SupplementalExamples") == 2
            and results[412].get("progressStorageUnchanged") is True,
            "browser evidence does not match the required record/example/progress checks")
    for width in (360, 1280):
        require(results[width].get("cardsChecked") == 3
                and results[width].get("cardLayouts") == 3
                and results[width].get("sessionLayouts") == 3
                and results[width].get("comparisonLayouts") == 3,
                f"representative edge-width checks are incomplete at {width}px")

    required = [
        WORK / "JLPT_N1_v171_audit.md",
        ROOT / "README.md",
        ROOT / "PROJECT_STATUS.md",
        ROOT / "completion" / "BACKLOG.md",
        ROOT / "completion" / "review-register.csv",
        ROOT / "completion" / "feedback-20261112-grammar.md",
    ]
    for path in required:
        require(path.is_file(), f"publication source is missing: {path.relative_to(ROOT)}")

    audit = (WORK / "JLPT_N1_v171_audit.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    backlog = (ROOT / "completion" / "BACKLOG.md").read_text(encoding="utf-8")
    register = (ROOT / "completion" / "review-register.csv").read_text(encoding="utf-8")
    feedback = (ROOT / "completion" / "feedback-20261112-grammar.md").read_text(encoding="utf-8")
    require("80f557ef2951c3557178f12537e67440d80e35c66d7daaa84a1407f161777d32" in audit,
            "audit does not identify the exact checkpoint hash")
    require("v171" in readme and "v171" in status, "README/status do not point to v171")
    require("| C27 |" in backlog and "**done**" in backlog.split("| C27 |", 1)[1].splitlines()[0],
            "C27 is not marked done in BACKLOG")
    require("grammar,90,grammar:90,fixed_rechecked," in register,
            "grammar ID 90 is not marked fixed_rechecked")
    require("Результат v171" in feedback, "feedback file lacks the v171 resolution")

    git(["fetch", "origin", "main"])
    remote_main = git(["rev-parse", "origin/main"])
    require(remote_main == expected_main,
            f"main moved since approval checkpoint: expected {expected_main}, got {remote_main}")
    target_html = "JLPT_N1_ukrainian_reading_v171.html"
    exists = subprocess.run(
        ["git", "cat-file", "-e", f"origin/main:{target_html}"],
        cwd=ROOT, text=True, capture_output=True, check=False
    )
    require(exists.returncode != 0, f"{target_html} already exists on main; refusing overwrite")

    temp_parent = Path(tempfile.mkdtemp(prefix="jlpt-n1-v171-main-"))
    temp = temp_parent / "main"
    worktree_added = False
    try:
        git(["worktree", "add", "--detach", str(temp), "origin/main"])
        worktree_added = True
        copies = {
            checkpoint: target_html,
            WORK / "JLPT_N1_v171_audit.md": "JLPT_N1_v171_audit.md",
            WORK / "grammar-order-results.json": "completion/v171-grammar-order-results.json",
            WORK / "prepare-results.json": "completion/v171-prepare-results.json",
            ROOT / "README.md": "README.md",
            ROOT / "PROJECT_STATUS.md": "PROJECT_STATUS.md",
            ROOT / "completion" / "BACKLOG.md": "completion/BACKLOG.md",
            ROOT / "completion" / "review-register.csv": "completion/review-register.csv",
            ROOT / "completion" / "feedback-20261112-grammar.md": "completion/feedback-20261112-grammar.md",
        }
        targets: list[str] = []
        for source, relative in copies.items():
            destination = temp / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
            targets.append(relative)

        git(["config", "user.name", "github-actions[bot]"], cwd=temp)
        git(["config", "user.email", "41898282+actions@users.noreply.github.com"], cwd=temp)
        git(["add", "--", *targets], cwd=temp)
        staged = subprocess.run(
            ["git", "diff", "--cached", "--quiet"], cwd=temp,
            text=True, capture_output=True, check=False
        )
        require(staged.returncode != 0, "publication tree contains no changes")
        git(["commit", "-m", "Publish verified JLPT N1 v171 grammar-card revision"], cwd=temp)
        commit_sha = git(["rev-parse", "HEAD"], cwd=temp)
        git(["push", "origin", "HEAD:main"], cwd=temp)
        git(["fetch", "origin", "main"])
        published_head = git(["rev-parse", "origin/main"])
        require(published_head == commit_sha,
                f"post-push main SHA mismatch: expected {commit_sha}, got {published_head}")
        print(json.dumps({
            "pass": True,
            "main_commit": commit_sha,
            "html_sha256": actual_hash,
            "html_bytes": checkpoint.stat().st_size,
            "files": targets,
        }, ensure_ascii=False, indent=2))
    finally:
        if worktree_added:
            git(["worktree", "remove", "--force", str(temp)], check=False)
        shutil.rmtree(temp_parent, ignore_errors=True)


if __name__ == "__main__":
    main()
