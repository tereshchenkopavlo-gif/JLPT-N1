#!/usr/bin/env python3
"""Build IR20 for the two original C12 batch-14 medium readings."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKAGE_ID = "IR-20261123-20"
SOURCE_COMMIT = "942665bc1126de52728446aa8d6bae673f985cce"
SOURCE_PATH = "completion/c12-batch14/drafts.json"
CASE_IDS = ["m-c12-20261123-22", "m-c12-20261123-23"]


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")


source = subprocess.check_output(["git", "show", f"{SOURCE_COMMIT}:{SOURCE_PATH}"])
drafts = json.loads(source)
rows = {item["id"]: item for item in drafts}
assert set(rows) == set(CASE_IDS)
cases = [
    {
        "case_id": case_id,
        "kind": "reading",
        "sources": [{"commit": SOURCE_COMMIT, "path": SOURCE_PATH}],
        "fields": rows[case_id],
    }
    for case_id in CASE_IDS
]
sources_sha256 = hashlib.sha256(canonical(cases)).hexdigest()
instructions = (
    "Проведи незалежний мовний аудит вкладених матеріалів. Працюй лише з цим пакетом і фактично "
    "перевіреними словниковими джерелами. Не читай авторські звіти чи історію чату. Не припускай, "
    "що кожен матеріал містить помилку. Альтернативний коректний переклад сам по собі не є помилкою.\n"
    "Перевір природність і зв’язність японського тексту, точність і природність українського перекладу, "
    "внутрішню узгодженість та стиль. Для кожного питання перевір усі варіанти, єдиність ключа, природність "
    "і правдоподібність distractors, а також підказки довжиною, граматичною формою чи логікою без знання тексту. "
    "Перевір точність пояснення й цитати evidence.\n"
    "Зафіксуй кожне перевірене поле й кожне пропущене поле. Не видавай структурні тести за мовну перевірку. "
    "Не вигадуй джерела. Невпевненість явно позначай. Поверни один JSON, заповнивши return_template. "
    "checked_fields може містити назву верхнього поля лише якщо перевірено весь його вміст; інакше переліч "
    "точні шляхи та решту в unchecked_fields. Наведи evidence і proposed_change для кожного зауваження. "
    "Збережи package_id та sources_sha256."
)
package = {
    "schema_version": 1,
    "package_id": PACKAGE_ID,
    "instructions": instructions,
    "sources_sha256": sources_sha256,
    "scope": {"vocab_ids": [], "meaning_contexts": 0, "readings": 2, "reading_questions": 4},
    "cases": cases,
    "return_template": {
        "schema_version": 1,
        "package_id": PACKAGE_ID,
        "sources_sha256": sources_sha256,
        "reviewer": {
            "system": "ChatGPT",
            "session": "",
            "reviewed_at": "",
            "participated_in_authoring": False,
        },
        "cases": [
            {
                "case_id": case_id,
                "checked_fields": [],
                "unchecked_fields": ["id", "title", "ja", "uk", "contextNotes", "questions"],
                "verdict": "not_reviewed",
                "findings": [],
            }
            for case_id in CASE_IDS
        ],
        "finding_format": {
            "field_path": "",
            "severity": "minor|major|critical",
            "confidence": "high|medium|low",
            "claim": "",
            "evidence": "",
            "sources": [],
            "proposed_change": "",
        },
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
        "predecessor": None,
        "scope": package["scope"],
        "reviews": [],
        "history": [{"status": "pending_review", "date": "2026-11-23"}],
        "notes": "Two original C12 batch-14 medium readings and four questions from released v229-C12o.",
    }
)
queue_path.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

queue_md_path = ROOT / "QUEUE.md"
queue_md = queue_md_path.read_text(encoding="utf-8")
marker = "| [IR-20261123-19]"
line = "| [IR-20261123-20](packages/IR-20261123-20.json) | pending_review | 0 карток, 2 тексти, 4 питання | Очікується |\n"
position = queue_md.index("\n", queue_md.index(marker)) + 1
queue_md = queue_md[:position] + line + queue_md[position:]
queue_md += (
    "\n## IR-20261123-20\n\n"
    "Два оригінальні середні тексти C12 із випуску v229-C12o та чотири питання. "
    "Авторські оцінки в пакет не включено. Джерело — release commit "
    "`942665bc1126de52728446aa8d6bae673f985cce`; main data checks 45162434824 успішні.\n"
)
queue_md_path.write_text(queue_md, encoding="utf-8")

print(json.dumps({"package_id": PACKAGE_ID, "package_sha256": package_sha256, "sources_sha256": sources_sha256}))
