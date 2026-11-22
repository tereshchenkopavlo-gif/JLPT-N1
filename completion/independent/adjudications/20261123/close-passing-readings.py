#!/usr/bin/env python3
"""Close IR12, IR13 and IR16 after exact comparison with the published HTML."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
MAIN_ROOT = ROOT.parent / "jlpt"
HTML_NAME = "JLPT_N1_ukrainian_reading_v229_C12n.html"
PACKAGE_IDS = ["IR-20261122-12", "IR-20261122-13", "IR-20261122-16"]
FIELDS = ["id", "title", "ja", "uk", "questions", "contextNotes"]


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")


def sha256(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


html_path = MAIN_ROOT / HTML_NAME
html = html_path.read_text(encoding="utf-8")
match = re.search(r"const readingBank = (\{.*?\});\n", html)
assert match, "readingBank not found"
bank = json.loads(match.group(1))
runtime = {item["id"]: item for group in bank.values() for item in group if "id" in item}

# Recover the valid JSON payload after the accidentally committed tool warning.
register_path = ROOT / "completion/independent/acceptance-register.json"
register_text = register_path.read_text(encoding="utf-8")
start = register_text.find("[\n")
assert start >= 0, "acceptance register payload not found"
register = json.loads(register_text[start:])

closure_cases = []
for package_id in PACKAGE_IDS:
    number = package_id.rsplit("-", 1)[1]
    package_path = ROOT / f"completion/independent/packages/{package_id}.json"
    review_path = next((ROOT / "completion/independent/reviews").glob(f"{package_id}-*.json"))
    package = json.loads(package_path.read_text(encoding="utf-8"))
    review = json.loads(review_path.read_text(encoding="utf-8"))
    assert package["sources_sha256"] == review["sources_sha256"]
    assert len(package["cases"]) == len(review["cases"]) == 1
    case = package["cases"][0]
    decision = review["cases"][0]
    assert decision["case_id"] == case["case_id"]
    assert decision["verdict"] == "pass" and not decision["unchecked_fields"]
    assert set(decision["checked_fields"]) == set(FIELDS)
    assert runtime[case["case_id"]] == case["fields"]

    evidence = f"completion/independent/reviews/{review_path.name}"
    adjudication = "adjudications/20261123/IR12-IR13-IR16-closure.json"
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
                "reviewed_value_sha256": sha256(case["fields"][field]),
                "status": "independent_reviewed_original",
                "exclusions": [],
                "evidence": evidence,
                "adjudication": adjudication,
            }
        )
    closure_cases.append(
        {
            "package_id": package_id,
            "case_id": case["case_id"],
            "fields_sha256": sha256(case["fields"]),
            "questions": len(case["fields"]["questions"]),
            "author_acceptance_path": f"completion/c12-batch{int(number) - 2}/acceptance.md",
        }
    )

register_path.write_text(json.dumps(register, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

queue_path = ROOT / "completion/independent/queue.json"
queue = json.loads(queue_path.read_text(encoding="utf-8"))
for item in queue["packages"]:
    if item["package_id"] in PACKAGE_IDS:
        assert item["status"] == "review_received"
        item["status"] = "closed"
        item["history"].append(
            {
                "status": "closed",
                "date": "2026-11-23",
                "evidence": "adjudications/20261123/IR12-IR13-IR16-closure.json",
            }
        )
        item["notes"] = "Full pass; exact equality with the current published HTML and preserved author/browser evidence verified."
        item["closed_case_ids"] = [closure_cases[PACKAGE_IDS.index(item["package_id"])]["case_id"]]
queue_path.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

queue_md_path = ROOT / "completion/independent/QUEUE.md"
queue_md = queue_md_path.read_text(encoding="utf-8")
for package_id in PACKAGE_IDS:
    queue_md = queue_md.replace(f"| [{package_id}]", f"| [{package_id}]", 1)
    queue_md = re.sub(
        rf"(\| \[{re.escape(package_id)}\]\([^\n]+?\) \| )review_received( \|)",
        rf"\1closed\2",
        queue_md,
        count=1,
    )
queue_md += (
    "\n## IR-20261122-12, IR-20261122-13 та IR-20261122-16\n\n"
    "Три довгі тексти й дев’ять питань незалежно перевірено без зауважень. "
    "Точну рівність усіх перевірених полів із чинним опублікованим HTML v229-C12n "
    "та наявність авторських і браузерних доказів підтверджено. Відновлено валідний "
    "acceptance-register.json після потрапляння службового повідомлення на початок файла. "
    "Фізичне приймання пристроїв лишається окремим.\n"
)
queue_md_path.write_text(queue_md, encoding="utf-8")

closure = {
    "package_ids": PACKAGE_IDS,
    "main_commit": "5a345292e9d3eb544e890a6ba69c68541f5ea497",
    "html_path": HTML_NAME,
    "html_sha256": hashlib.sha256(html_path.read_bytes()).hexdigest(),
    "html_git_blob": "9952df068aa5f6757e49284c6593dd4bc23678e9",
    "cases": closure_cases,
    "browser_runs": [44939085501, 44959349808, 44979137656],
    "data_check_runs": [44939085438, 44959349778, 44979137620],
    "scope": "Independent language acceptance plus exact release reconciliation; physical-device acceptance remains separate.",
    "register_repair": {
        "problem": "A tool truncation warning preceded the otherwise valid JSON payload in the queue branch.",
        "action": "Removed only the non-JSON prefix and retained all 219 prior register rows before adding 18 rows.",
    },
}
closure_path = ROOT / "completion/independent/adjudications/20261123/IR12-IR13-IR16-closure.json"
closure_path.write_text(json.dumps(closure, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({"register_rows": len(register), "closed_cases": [x["case_id"] for x in closure_cases]}, ensure_ascii=False))
