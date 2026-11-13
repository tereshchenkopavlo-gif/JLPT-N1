import csv
import json
import shutil
from pathlib import Path

WORK = Path("completion/v181-work")
prepare = json.loads((WORK / "prepare-results.json").read_text(encoding="utf-8"))
browser = json.loads((WORK / "browser-results.json").read_text(encoding="utf-8"))
if prepare.get("pass") is not True or browser.get("pass") is not True:
    raise RuntimeError("preparation or Chromium verification did not pass")
if browser.get("sha256") != prepare.get("candidate_sha256"):
    raise RuntimeError("Chromium evidence is not bound to the prepared HTML")
if browser.get("contextsChecked") != 2 or browser.get("generatedPassagesChecked") != 2:
    raise RuntimeError("both exact contexts were not generated and checked")
if browser.get("clozeEligibilityUnchanged") is not True or browser.get("progressStorageRestored") is not True:
    raise RuntimeError("cloze or progress preservation check failed")

html_sha = prepare["candidate_sha256"]
register_path = Path("completion/review-register.csv")
with register_path.open("r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames
    rows = list(reader)
if fields != ["kind", "key", "baselineLocation", "finalReview", "evidence"]:
    raise RuntimeError("unexpected review-register schema")
if any(r["kind"] == "reviewed_meaning_quiz" and r["key"] == "v_2433" for r in rows):
    raise RuntimeError("v_2433 meaning quiz is already registered")
before_counts = {}
for r in rows:
    before_counts[r["finalReview"]] = before_counts.get(r["finalReview"], 0) + 1
if before_counts.get("reviewed") != 3892 or before_counts.get("fixed_rechecked") != 59 or before_counts.get("pending") != 1892:
    raise RuntimeError(f"unexpected pre-v181 register counts: {before_counts}")
rows.append({
    "kind": "reviewed_meaning_quiz",
    "key": "v_2433",
    "baselineLocation": "REVIEWED_MEANING_QUIZZES.v_2433",
    "finalReview": "reviewed",
    "evidence": f"completion/v181-c11-review.tsv; two exact context-specific payloads; author review, not independent; v181 SHA-256={html_sha}"
})
with register_path.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)

counts = {}
kind_counts = {}
for r in rows:
    counts[r["finalReview"]] = counts.get(r["finalReview"], 0) + 1
    kind_counts[r["kind"]] = kind_counts.get(r["kind"], 0) + 1
if counts != {"reviewed": 3893, "fixed_rechecked": 59, "pending": 1892}:
    raise RuntimeError(f"unexpected post-v181 register counts: {counts}")
if kind_counts.get("reviewed_meaning_quiz") != 267:
    raise RuntimeError("reviewed meaning quiz count is not 267")

registry = {
    "pass": True,
    "total_objects": len(rows),
    "reviewed": counts["reviewed"],
    "fixed_rechecked": counts["fixed_rechecked"],
    "pending": counts["pending"],
    "reviewed_meaning_quiz": kind_counts["reviewed_meaning_quiz"],
    "vocabulary_author_credit": "3385/3914",
    "vocabulary_credit_changed": False,
    "independent_acceptance": False
}
Path("completion/v181-registry-results.json").write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

shutil.copyfile("completion/v180-work/diagnostics.json", "completion/v180-c11-diagnostics.json")
shutil.copyfile("completion/v180-work/checkpoint.json", "completion/v180-c11-checkpoint.json")
shutil.copyfile("completion/v180-work/preaudit-notes.md", "completion/v180-c11-preaudit-notes.md")

source_review = Path("completion/v181-work/source-review.md").read_text(encoding="utf-8")
audit = f"""# JLPT N1 v181 — C11 context-specific meaning quiz review

**Дата:** 13 листопада 2026. **Основа:** v179, SHA-256 {prepare['base_sha256']}. **Кандидат:** v181, SHA-256 {html_sha} ({prepare['candidate_bytes']:,} байт).

## Авторський перегляд

Для вже авторськи прийнятої картки **ID2433 そびえる** додано два окремі meaning-набори, прив'язані до точних прикладів:

- 市の中心部には、高さ二百メートルの超高層ビルがそびえている。
- 雪をいただいた山々が、湖の向こうにそびえて見える。

Автоматичні meaning-дистрактори до v181 бралися з віддалених значень інших карток і не перевіряли знання саме そびえる. Нові варіанти зосереджені на просторовому значенні «дуже високо стояти/височіти» та зіставляють висоту, положення й форму споруди або рельєфу. Для кожного прикладу є одна правильна відповідь, три різні хибні відповіді та українське контекстне пояснення.

**Це приймання двох контекстних наборів питань, а не повторне повнокарткове приймання ID2433.** Авторський credit словника не змінено.

## Cloze та точне виділення

Обидва речення містять форму **そびえて**, а не словникову форму **そびえる**. Чинна перевірка literal cloze вимагає точного збігу виділеної форми з headword, тому cloze для цих двох речень не був доступний і до v181. Додавання збережених meaning-наборів не забрало доступну вправу: Chromium відтворив false до й після для обох контекстів. Точне виділення そびえて збережено.

## Технічні перевірки

Детермінований preparer підтвердив основу v179, точний SHA кандидата, повний rollback і єдину зміну даних у REVIEWED_MEANING_QUIZZES.v_2433 плюс заголовок версії. Не змінювалися 3914 словникових записів, 130 граматичних конструкцій, 859 лексичних пар, ID, POS, reading overrides, навчальна логіка та код збереження прогресу. Chromium перевірив обидва контексти через quizMeaningOptions і generateOfflinePassage, чотири унікальні варіанти, правильний ключ, пояснення, точне виділення, cloze eligibility та контрольний sentinel прогресу. Перевірено ширини 360, 412 і 1280 px без горизонтального переповнення.

Докази: completion/v181-prepare-results.json, completion/v181-browser-results.json, completion/v181-registry-results.json, completion/v181-c11-review.tsv, completion/v181-acceptance.tsv.

## Облік і межі

- Авторський credit словника: **3385/3914**, без змін.
- Завершальний реєстр: **3893 reviewed / 59 fixed_rechecked / 1892 pending**.
- Збережені reviewed meaning quiz: **267** (додано один об'єкт із двома контекстними payload).
- ID255/327 залишаються відкритими POS/reading-питаннями. Діагностика v180 відтворила 23 змінені reading-пули; три цілі втрачають поріг трьох дистракторів (ID255, ID327, ID1819), один набуває його (ID359). POS і reading overrides у v181 не змінювалися.
- Незалежне лінгвістичне, фізичне та правове/походження приймання не виконані. v181 — проміжний випуск, не кандидат 1.0.

## Джерела

{source_review}
"""
Path("JLPT_N1_v181_audit.md").write_text(audit, encoding="utf-8")

checkpoint = json.loads((WORK / "checkpoint.json").read_text(encoding="utf-8"))
checkpoint["status"] = "verified; ready for publication to main"
checkpoint["registry_counts"] = counts
checkpoint["registry_total_objects"] = len(rows)
checkpoint["audit"] = "JLPT_N1_v181_audit.md"
(WORK / "checkpoint.json").write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
finalize = {
    "pass": True,
    "candidate_sha256": html_sha,
    "registry_counts": counts,
    "reviewed_meaning_quiz": 267,
    "vocabulary_author_credit": "3385/3914",
    "files_updated": [
        "completion/review-register.csv", "JLPT_N1_v181_audit.md",
        "completion/v181-c11-review.tsv", "completion/v181-acceptance.tsv",
        "completion/v181-registry-results.json",
        "completion/v180-c11-diagnostics.json", "completion/v180-c11-checkpoint.json",
        "completion/v180-c11-preaudit-notes.md"
    ]
}
(WORK / "finalize-results.json").write_text(json.dumps(finalize, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(finalize, ensure_ascii=False, indent=2))
