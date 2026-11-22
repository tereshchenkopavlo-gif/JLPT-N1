"""Validate a reviewer JSON and stage it for author adjudication."""
import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path

def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


KEY = r"[A-Za-z_][A-Za-z_0-9]*"
ACCESS = re.compile(r'\.(' + KEY + r')|\[(\d+|"(?:[^"\\]|\\.)*")\]')
LEGACY_IR01 = "e416c4e96849ff039f28543554297ac3e71292277bb2477fcc377b9010e8f3ac"


def field_tokens(path, *, legacy=False):
    if legacy and path == "contextNotes[*].id (cross-check against full grammar registry not provided)":
        return ("contextNotes",)
    first = re.match(KEY, path)
    assert first, path
    keys = [first.group()]
    offset = first.end()
    while offset < len(path):
        match = ACCESS.match(path, offset)
        assert match, path
        keys.append(match[1] if match[1] is not None else json.loads(match[2]))
        offset = match.end()
    return tuple(keys)


def resolve_field(fields, path, *, legacy=False):
    value = fields
    for key in field_tokens(path, legacy=legacy):
        assert isinstance(value, list if type(key) is int else dict), path
        value = value[key]
    return value


def leaf_tokens(value, keys=()):
    if isinstance(value, dict) and value:
        for key, child in value.items():
            yield from leaf_tokens(child, keys + (key,))
    elif isinstance(value, list) and value:
        for key, child in enumerate(value):
            yield from leaf_tokens(child, keys + (key,))
    else:
        yield keys


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
    legacy = hashlib.sha256((json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()).hexdigest() == LEGACY_IR01
    for case in result["cases"]:
        assert case["verdict"] in ["pass", "issues", "uncertain", "not_reviewed"]
        checked, unchecked = case["checked_fields"], case["unchecked_fields"]
        assert isinstance(checked, list) and isinstance(unchecked, list)
        assert all(nonempty(path) for path in checked + unchecked)
        assert len(set(checked + unchecked)) == len(checked + unchecked)
        fields = expected[case["case_id"]]["fields"]
        coverage = set()
        for path in checked + unchecked:
            historic_exclusion = legacy and path in unchecked
            resolve_field(fields, path, legacy=historic_exclusion)
            coverage.add(field_tokens(path, legacy=historic_exclusion))
        assert len(coverage) == len(checked + unchecked), "Duplicate field path"
        for leaf in leaf_tokens(fields):
            if legacy and leaf == ("vocabulary", "id"):
                continue
            assert any(leaf[:len(path)] == path for path in coverage), f"Missing coverage: {leaf}"
        scope = package.get("review_scope", {}).get(case["case_id"])
        if scope is not None:
            allowed = [field_tokens(path) for path in scope]
            for path in checked:
                tokens = field_tokens(path)
                assert any(tokens[:len(parent)] == parent for parent in allowed), f"Outside review scope: {path}"
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
