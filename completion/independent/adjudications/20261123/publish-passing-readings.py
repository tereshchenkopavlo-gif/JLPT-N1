#!/usr/bin/env python3
"""Publish field-level independent acceptance for IR12, IR13 and IR16."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
HTML = ROOT / "JLPT_N1_ukrainian_reading_v229_C12n.html"
PACKAGE_IDS = ["IR-20261122-12", "IR-20261122-13", "IR-20261122-16"]
FIELDS = ["id", "title", "ja", "uk", "questions", "contextNotes"]


def digest(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


html = HTML.read_text(encoding="utf-8")
match = re.search(r"const readingBank = (\{.*?\});\n", html)
assert match
bank = json.loads(match.group(1))
runtime = {item["id"]: item for group in bank.values() for item in group if "id" in item}

register_path = ROOT / "completion/independent/acceptance-register.json"
register = json.loads(register_path.read_text(encoding="utf-8"))

for package_id in PACKAGE_IDS:
    package = json.loads((ROOT / f"completion/independent/packages/{package_id}.json").read_text(encoding="utf-8"))
    review_path = next((ROOT / "completion/independent/reviews").glob(f"{package_id}-*.json"))
    review = json.loads(review_path.read_text(encoding="utf-8"))
    assert package["sources_sha256"] == review["sources_sha256"]
    case = package["cases"][0]
    verdict = review["cases"][0]
    assert verdict["case_id"] == case["case_id"]
    assert verdict["verdict"] == "pass" and not verdict["unchecked_fields"]
    assert set(verdict["checked_fields"]) == set(FIELDS)
    assert runtime[case["case_id"]] == case["fields"]

    for field in FIELDS:
        key = (package_id, case["case_id"], field)
        assert not any((row["package_id"], row["case_id"], row["reviewed_field"]) == key for row in register)
        register.append(
            {
                "package_id": package_id,
                "case_id": case["case_id"],
                "reviewed_field": field,
                "reviewer_verdict": "pass",
                "source_sha256": package["sources_sha256"],
                "reviewed_value_sha256": digest(case["fields"][field]),
                "status": "independent_reviewed_original",
                "exclusions": [],
                "evidence": f"completion/independent/reviews/{review_path.name}",
                "adjudication": "completion/independent/adjudications/20261123/IR12-IR13-IR16-closure.json",
            }
        )

assert len({(row["package_id"], row["case_id"], row["reviewed_field"]) for row in register}) == len(register)
register_path.write_text(json.dumps(register, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"acceptance_rows": len(register), "new_rows": 18}))
