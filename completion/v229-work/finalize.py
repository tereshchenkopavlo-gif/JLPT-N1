import json, os
from pathlib import Path

work = Path("completion/v229-work")
prepare = json.loads((work / "prepare-results.json").read_text(encoding="utf-8"))
browser = json.loads((work / "browser-results.json").read_text(encoding="utf-8"))
if not prepare.get("pass") or not browser.get("pass"):
    raise RuntimeError("v229 candidate or Chromium verification did not pass")
checkpoint_path = work / "checkpoint.json"
checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
checkpoint["technical_verification"] = "passed"
checkpoint["chromium_verification"] = "passed"
checkpoint["meaning_quiz_structure"] = "three unique distractors and correct-answer exclusion verified; semantic review pending"
checkpoint["workflow_run_id"] = int(os.environ.get("GITHUB_RUN_ID", "0"))
checkpoint["status"] = "candidate and technical checks passed; manual semantic review of meaning-quiz diagnostics pending; no registry credit or main publication"
checkpoint_path.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
summary = {
    "pass": True,
    "technical_verification": "passed",
    "chromium_verification": "passed",
    "semantic_quiz_review": "pending_manual",
    "registry_credit_applied": False,
    "main_publication": False,
    "workflow_run_id": checkpoint["workflow_run_id"]
}
(work / "finalize-results.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
