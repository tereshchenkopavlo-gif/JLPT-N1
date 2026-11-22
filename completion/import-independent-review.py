"""Validate a reviewer JSON and stage it for author adjudication."""
import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path

def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def resolve_field(fields, path, *, legacy=False):
    if legacy and path == "contextNotes[*].id (cross-check against full grammar registry not provided)":
        return fields["contextNotes"]
    assert re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*|\[\d+\])*", path), path
    value = fields
    for key in re.findall(r"[A-Za-z_][A-Za-z_0-9]*|\d+", path):
        value = value[int(key)] if key.isdecimal() else value[key]
    return value


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(raw):
    return json.loads(raw, object_pairs_hook=unique_keys)


def validate(package, result):
    assert type(result["schema_version"]) is int and result["schema_version"] == 1
    assert re.fullmatch(r"IR-\d{8}-[A-Za-z0-9-]+", package["package_id"])
    assert hashlib.sha256(json.dumps(package["cases"], ensure_ascii=False, sort_keys=True).encode()).hexdigest() == package["sources_sha256"]
    assert result["package_id"] == package["package_id"]
    assert result["sources_sha256"] == package["sources_sha256"]
    reviewer = result["reviewer"]
    assert reviewer["participated_in_authoring"] is False
    assert all(nonempty(reviewer[key]) for key in ("system", "session", "reviewed_at"))
    date.fromisoformat(reviewer["reviewed_at"][:10])
    expected = {c["case_id"]: c for c in package["cases"]}
    assert len(package["cases"]) == len(expected)
    assert isinstance(result["cases"], list) and len(result["cases"]) == len(expected)
    assert {c["case_id"] for c in result["cases"]} == set(expected)
    for case in result["cases"]:
        assert case["verdict"] in ["pass", "issues", "uncertain", "not_reviewed"]
        checked, unchecked = case["checked_fields"], case["unchecked_fields"]
        assert isinstance(checked, list) and isinstance(unchecked, list)
        assert all(nonempty(path) for path in checked + unchecked)
        assert len(set(checked + unchecked)) == len(checked + unchecked)
        fields = expected[case["case_id"]]["fields"]
        roots = {re.split(r"[.\[/]", path)[0] for path in checked + unchecked}
        assert roots == set(fields), "Every source field needs checked or unchecked coverage"
        for path in checked + unchecked:
            resolve_field(fields, path, legacy=result["package_id"] == "IR-20261120-01" and path in unchecked)
        assert isinstance(case["findings"], list)
        # Preserve the reviewer's granular paths and exclusions verbatim.
        # Adjudication computes field coverage; staging grants no acceptance credit.
        if case["verdict"] == "pass":
            assert checked and not case["findings"]
        if case["verdict"] == "not_reviewed":
            assert not checked
        for finding in case["findings"]:
            assert all(nonempty(finding[key]) for key in ("field_path", "claim", "evidence"))
            assert re.split(r"[.\[/]", finding["field_path"])[0] in fields
            assert finding["severity"] in ["minor", "major", "critical"]
            assert finding["confidence"] in ["high", "medium", "low"]
            assert isinstance(finding["sources"], list) and all(map(nonempty, finding["sources"]))
            assert "proposed_change" in finding


def main():
    p = argparse.ArgumentParser()
    p.add_argument("package")
    p.add_argument("result")
    p.add_argument("--output-dir", default="completion/independent/reviews")
    p.add_argument("--validate-only", action="store_true")
    args = p.parse_args()
    package = load_json(Path(args.package).read_bytes())
    result = load_json(Path(args.result).read_bytes())
    validate(package, result)
    if args.validate_only:
        print(json.dumps({"validated":args.result,"package_id":result["package_id"],
                          "registry_credit_applied":False}))
        raise SystemExit(0)
    payload = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    digest = hashlib.sha256(payload.encode()).hexdigest()
    dest = Path(args.output_dir) / (package["package_id"] + "-" + digest[:16] + ".json")
    dest.parent.mkdir(parents=True, exist_ok=True)
    for existing in dest.parent.glob("*.json"):
        if json.loads(existing.read_text()) == result:
            print(json.dumps({"staged":str(existing),"duplicate_reused":True,
                              "registry_credit_applied":False}))
            raise SystemExit(0)
    if dest.exists():
        assert dest.read_text() == payload
    else:
        dest.write_text(payload)
    print(json.dumps({"staged": str(dest), "sha256": digest,
                      "adjudication": "pending", "registry_credit_applied": False}))


if __name__ == "__main__":
    main()
