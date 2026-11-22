#!/usr/bin/env python3
"""Build the narrow IR19 recheck package for the corrected IR15 translation."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKAGE_ID = "IR-20261123-19"
SOURCE_COMMIT = "44187479ec8f2c7c4f22f17ad869387637ae3139"
SOURCE_PATH = "completion/c12-batch12/drafts.json"
CASE_ID = "m-c12-20261122-20"


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")


source = subprocess.check_output(["git", "show", f"{SOURCE_COMMIT}:{SOURCE_PATH}"])
drafts = json.loads(source)
row = next(item for item in drafts if item["id"] == CASE_ID)
cases = [
    {
        "case_id": CASE_ID,
        "kind": "reading",
        "sources": [{"commit": SOURCE_COMMIT, "path": SOURCE_PATH}],
        "fields": {"ja": row["ja"], "uk": row["uk"]},
    }
]
sources_sha256 = hashlib.sha256(canonical(cases)).hexdigest()
package = {
    "schema_version": 1,
    "package_id": PACKAGE_ID,
    "instructions": "Повторно перевірте лише український переклад uk на відповідність японському тексту ja. Японський текст наведено як контекст. Зафіксуйте ja як unchecked та оцініть точність, природність і повноту uk. Не читайте авторські звіти чи попередній висновок.",
    "sources_sha256": sources_sha256,
    "scope": {"vocab_ids": [], "meaning_contexts": 0, "readings": 1, "reading_questions": 0},
    "cases": cases,
    "return_template": {
        "schema_version": 1,
        "package_id": PACKAGE_ID,
        "sources_sha256": sources_sha256,
        "reviewer": {"system": "ChatGPT", "session": "", "reviewed_at": "", "participated_in_authoring": False},
        "cases": [
            {
                "case_id": CASE_ID,
                "checked_fields": [],
                "unchecked_fields": ["ja", "uk"],
                "verdict": "not_reviewed",
                "findings": [],
            }
        ],
        "finding_format": {"field_path": "", "severity": "minor|major|critical", "confidence": "high|medium|low", "claim": "", "evidence": "", "sources": [], "proposed_change": ""},
        "allowed_verdicts": ["pass", "issues", "uncertain", "not_reviewed"],
    },
}
package_path = ROOT / f"packages/{PACKAGE_ID}.json"
package_path.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
package_sha256 = hashlib.sha256(package_path.read_bytes()).hexdigest()

queue_path = ROOT / "queue.json"
queue = json.loads(queue_path.read_text(encoding="utf-8"))
assert not any(item["package_id"] == PACKAGE_ID for item in queue["packages"])
queue["packages"].append(
    {
        "package_id": PACKAGE_ID,
        "path": f"packages/{PACKAGE_ID}.json",
        "package_sha256": package_sha256,
        "sources_sha256": sources_sha256,
        "source_commits": [SOURCE_COMMIT],
        "status": "pending_review",
        "predecessor": "IR-20261122-15",
        "scope": package["scope"],
        "reviews": [],
        "history": [{"status": "pending_review", "date": "2026-11-23"}],
        "notes": "Recheck only the corrected Ukrainian translation; Japanese source is context and must remain unchecked.",
    }
)
queue_path.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

queue_md_path = ROOT / "QUEUE.md"
queue_md = queue_md_path.read_text(encoding="utf-8")
marker = "| [IR-20261122-18]"
line = "| [IR-20261123-19](packages/IR-20261123-19.json) | pending_review | Український переклад одного тексту | Очікується |\n"
position = queue_md.index("\n", queue_md.index(marker)) + 1
queue_md = queue_md[:position] + line + queue_md[position:]
queue_md += (
    "\n## IR-20261123-19\n\n"
    "Вузька повторна перевірка виправленого `m-c12-20261122-20.uk` після IR15. "
    "Джерело — checkpoint `44187479ec8f2c7c4f22f17ad869387637ae3139`; "
    "data checks 45037552477 і Chromium 45037552756 успішні. `ja` наведено лише як контекст.\n"
)
queue_md_path.write_text(queue_md, encoding="utf-8")

print(json.dumps({"package_id": PACKAGE_ID, "package_sha256": package_sha256, "sources_sha256": sources_sha256}))
