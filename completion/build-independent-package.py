import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path


def source(ref, path):
    return subprocess.check_output(["git", "show", ref + ":" + path]).decode()


def block(text, name):
    start = re.search(r"const\s+" + name + r"\s*=\s*", text).end()
    return json.JSONDecoder().raw_decode(text, start)[0]


main = subprocess.check_output(["git", "rev-parse", "origin/main"]).decode().strip()
v230 = "ec3e476967a6445e0e4f31e04ba04e11836fa192"
v231 = subprocess.check_output(["git", "rev-parse", "origin/work/v231-c11-last-blockers"]).decode().strip()
html_path = "JLPT_N1_ukrainian_reading_v230.html"
html = source(v230, html_path)
vocab = {str(row["id"]): row for row in block(html, "DEFAULT_VOCAB")}
details = block(html, "VOCAB_DETAILS_BY_ID")
pos = block(html, "VOCAB_POS_BY_ID")
quizzes = block(html, "REVIEWED_MEANING_QUIZZES")
spec = json.loads(source(v231, "completion/v231-work/payloads.json"))
cases = []
for id in [3375, 3441, 3594, 3652, 3677, 3679]:
    key = str(id)
    next_version = id in [3652, 3677, 3679]
    quiz = copy.deepcopy(spec["quizzes"]["v_" + key] if next_version else quizzes["v_" + key])
    field_data = {
        "vocabulary": vocab[key],
        "details": details[key],
        "display_pos": spec["pos"][key] if next_version else pos[key],
        "meaning_quiz": quiz,
    }
    cases.append({"case_id": "v_" + key, "kind": "vocab",
                  "sources": [{"commit": v230, "path": html_path}] + (
                      [{"commit": v231, "path": "completion/v231-work/payloads.json",
                        "applied_fields": ["display_pos", "meaning_quiz"]}] if next_version else []),
                  "fields": field_data})
texts = json.loads(source(main, "completion/c12-work/reading-candidates.json"))
for text in texts:
    cases.append({"case_id": text["id"], "kind": "reading",
                  "sources": [{"commit": main, "path": "completion/c12-work/reading-candidates.json"}],
                  "fields": text})
instructions = """Проведи незалежний мовний аудит вкладених матеріалів. Працюй лише з цим пакетом і фактично перевіреними словниковими джерелами. Не читай авторські звіти чи історію чату. Не припускай, що кожна картка містить помилку. Альтернативний коректний переклад сам по собі не є помилкою.
Перевір японські значення, читання, POS для конкретного значення, сполучуваність, стиль, приклади, українські переклади, зв'язки та внутрішню узгодженість. Для кожного питання перевір усі варіанти, єдиність ключа, природність і правдоподібність distractors, підказки довжиною чи формою. Для текстів перевір зв'язність, контекстні примітки, точність опори й пояснення.
У meaning_quiz ключ правильності є частиною матеріалу для критичної перевірки. byExample використовує точне речення. Для reading answer є індексом choices від нуля. Зафіксуй кожне перевірене поле й кожне пропущене поле. Не видавай структурні тести за мовну перевірку. Не вигадуй джерела. Невпевненість явно позначай. Поверни один JSON, заповнивши return_template. checked_fields може містити назву верхнього поля лише якщо перевірено весь його вміст; інакше переліч точні шляхи та решту в unchecked_fields. Наведи evidence і proposed_change для кожного зауваження. Збережи package_id та sources_sha256."""
digest = hashlib.sha256(json.dumps(cases, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
template = {"schema_version": 1, "package_id": "IR-20261120-01",
            "sources_sha256": digest,
            "reviewer": {"system": "ChatGPT", "session": "", "reviewed_at": "",
                         "participated_in_authoring": False},
            "cases": [{"case_id": case["case_id"], "checked_fields": [],
                       "unchecked_fields": list(case["fields"]), "verdict": "not_reviewed",
                       "findings": []} for case in cases],
            "finding_format": {"field_path": "", "severity": "minor|major|critical",
                               "confidence": "high|medium|low", "claim": "", "evidence": "",
                               "sources": [], "proposed_change": ""},
            "allowed_verdicts": ["pass", "issues", "uncertain", "not_reviewed"]}
packet = {"schema_version": 1, "package_id": template["package_id"],
          "instructions": instructions, "sources_sha256": digest,
          "scope": {"vocab_ids": [3375, 3441, 3594, 3652, 3677, 3679],
                    "meaning_contexts": 12, "readings": len(texts),
                    "reading_questions": sum(len(t["questions"]) for t in texts)},
          "cases": cases, "return_template": template}
out = Path("completion/independent/IR-20261120-01.json")
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"path": str(out), "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
                  "scope": packet["scope"]}, ensure_ascii=False))
