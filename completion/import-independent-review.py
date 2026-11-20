"""Validate a reviewer JSON and stage it for author adjudication."""
import argparse
import hashlib
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("package")
p.add_argument("result")
p.add_argument("--output-dir", default="completion/independent/results")
args = p.parse_args()
package = json.loads(Path(args.package).read_text())
result = json.loads(Path(args.result).read_text())
assert result["schema_version"] == 1
assert result["package_id"] == package["package_id"]
assert result["sources_sha256"] == package["sources_sha256"]
reviewer = result["reviewer"]
assert reviewer["participated_in_authoring"] is False
assert reviewer["system"] and reviewer["session"] and reviewer["reviewed_at"]
expected = {c["case_id"]: c for c in package["cases"]}
assert len(result["cases"]) == len(expected)
assert {c["case_id"] for c in result["cases"]} == set(expected)
for case in result["cases"]:
    assert case["verdict"] in ["pass", "issues", "uncertain", "not_reviewed"]
    checked, unchecked = case["checked_fields"], case["unchecked_fields"]
    assert isinstance(checked, list) and isinstance(unchecked, list)
    assert len(set(checked + unchecked)) == len(checked + unchecked)
    assert set(checked + unchecked) == set(expected[case["case_id"]]["fields"]), (
        "Use top-level fields in importable results; mark a partial field unchecked "
        "and describe exact reviewed paths in findings.")
    if case["verdict"] == "pass":
        assert checked and not case["findings"]
    if case["verdict"] == "not_reviewed":
        assert not checked
    for finding in case["findings"]:
        assert finding["field_path"] and finding["claim"] and finding["evidence"]
        assert finding["severity"] in ["minor", "major", "critical"]
        assert finding["confidence"] in ["high", "medium", "low"]
        assert isinstance(finding["sources"], list)
        assert "proposed_change" in finding
payload = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
digest = hashlib.sha256(payload.encode()).hexdigest()
dest = Path(args.output_dir) / (package["package_id"] + "-" + digest[:16] + ".json")
dest.parent.mkdir(parents=True, exist_ok=True)
if dest.exists():
    assert dest.read_text() == payload
else:
    dest.write_text(payload)
print(json.dumps({"staged": str(dest), "sha256": digest,
                  "adjudication": "pending", "registry_credit_applied": False}))
