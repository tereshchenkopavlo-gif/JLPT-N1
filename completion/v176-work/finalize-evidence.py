#!/usr/bin/env python3
"""Finalize v176 author-acceptance evidence without changing learning mechanisms."""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path
import re
from collections import Counter

ROOT = Path(".")
BASE = ROOT / "JLPT_N1_ukrainian_reading_v175.html"
TARGET = ROOT / "JLPT_N1_ukrainian_reading_v176.html"
WORK = ROOT / "completion" / "v176-work"
REGISTRY = ROOT / "completion" / "review-register.csv"
ACCEPTANCE = ROOT / "completion" / "v176-acceptance.tsv"
PAIR_OUTPUT = ROOT / "completion" / "v176-pair-review.tsv"
EXPECTED_BASE = "c3083a18181429e29fb1d63dcc4e9d39c5d68ccde49253b4f572820b27e1fb86"
EXPECTED_IDS = ["278", "330", "332", "335", "339", "347", "349", "350", "353", "355"]
EXPECTED_PAIR_KEYS = ["72:293:353", "81:339:341", "85:349:350", "167:658:335"]
EXPECTED_PENDING = ["255", "327"]

def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

def digest(value):
    return hashlib.sha256(compact(value).encode("utf-8")).hexdigest()

def block(source, name):
    match = re.search(r"\bconst\s+" + re.escape(name) + r"\s*=\s*", source)
    if not match:
        raise ValueError("Missing block " + name)
    start = match.end()
    value, end = json.JSONDecoder().raw_decode(source, start)
    return value

def main():
    prep = json.loads((WORK / "prepare-results.json").read_text(encoding="utf-8"))
    browser = json.loads((WORK / "browser-results.json").read_text(encoding="utf-8"))
    if prep.get("pass") is not True or browser.get("pass") is not True:
        raise ValueError("Preparation and Chromium evidence must both pass")
    if prep.get("base_sha256") != EXPECTED_BASE:
        raise ValueError("v176 base SHA mismatch")
    if browser.get("sha256") != prep.get("checkpoint_sha256"):
        raise ValueError("Chromium result belongs to a different HTML file")
    if prep.get("changed_ids") != EXPECTED_IDS or prep.get("operations") != 10:
        raise ValueError("Exact v176 card/field scope mismatch")
    if prep.get("pair_reviewed_without_change") != [72, 81, 85, 167]:
        raise ValueError("Exact pair-review scope mismatch")
    if prep.get("unresolved_pos_ids") != EXPECTED_PENDING:
        raise ValueError("Exact pending POS scope mismatch")
    if prep.get("vocabulary_records") != 3914 or prep.get("grammar_records") != 130 or prep.get("lexical_pairs") != 859:
        raise ValueError("Structural counts changed")
    if prep.get("exact_rollback") is not True:
        raise ValueError("Exact rollback not proven")
    if browser.get("cardsChecked") != 12 or browser.get("fieldsChecked") != 10 or browser.get("pairsChecked") != 4:
        raise ValueError("Chromium scope mismatch")
    if browser.get("progressStorageUnchanged") is not True:
        raise ValueError("Progress sentinel changed")
    if set(x.get("width") for x in browser.get("widths", [])) != {360, 412, 1280} or not all(x.get("pass") for x in browser.get("widths", [])):
        raise ValueError("A viewport check failed")
    if len(browser.get("renderedCards", [])) != 12 or not all(
        row.get("cardRendered") and row.get("allExamplesRendered") and all(f.get("present") for f in row.get("fields", []))
        for row in browser.get("renderedCards", [])
    ):
        raise ValueError("A reviewed card or exact field did not render")
    expected_diagnostics = {"255": 0, "278": 0, "327": 2}
    actual_diagnostics = {x["id"]: x["proposedCount"] for x in browser.get("posDiagnostics", [])}
    if actual_diagnostics != expected_diagnostics or not all(x.get("currentCount", 0) >= 3 for x in browser.get("posDiagnostics", [])):
        raise ValueError("POS/reading-pool diagnostic does not match the reviewed baseline")

    before_html = BASE.read_text(encoding="utf-8")
    after_html = TARGET.read_text(encoding="utf-8")
    before_cards = block(before_html, "VOCAB_DETAILS_BY_ID")
    after_cards = block(after_html, "VOCAB_DETAILS_BY_ID")
    updates = json.loads((WORK / "updates.json").read_text(encoding="utf-8"))
    by_id = {}
    for row in updates:
        by_id.setdefault(str(row["id"]), []).append(row)
    if list(by_id) != EXPECTED_IDS:
        raise ValueError("Update IDs are not the exact expected order")

    # Generate card-level evidence from exact before/after JSON, not prose counts.
    with ACCEPTANCE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "headword", "decision", "fields", "before_sha256", "after_sha256", "rationale", "sources"
        ], delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for id in EXPECTED_IDS:
            rows = by_id[id]
            writer.writerow({
                "id": id,
                "headword": before_cards[id]["w"],
                "decision": "fixed_rechecked after exact field review and Chromium regression",
                "fields": "; ".join(row["field"] for row in rows),
                "before_sha256": digest(before_cards[id]),
                "after_sha256": digest(after_cards[id]),
                "rationale": " ".join(row["rationale"] for row in rows),
                "sources": "; ".join(source for row in rows for source in row.get("sources", [])),
            })

    pair_data_before = block(before_html, "VOCAB_AUDITED_PAIRS")
    pair_data_after = block(after_html, "VOCAB_AUDITED_PAIRS")
    pair_inputs = list(csv.DictReader((WORK / "pair-review.tsv").open(encoding="utf-8"), delimiter="\t"))
    if [row["pair_key"] for row in pair_inputs] != EXPECTED_PAIR_KEYS:
        raise ValueError("Pair input does not match exact four-pair scope")
    with PAIR_OUTPUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "pair_index", "pair_key", "type", "decision", "before_sha256", "after_sha256", "rationale", "sources"
        ], delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in pair_inputs:
            index = int(row["pair_index"])
            pair_before = pair_data_before[index]
            pair_after = pair_data_after[index]
            key = str(index) + ":" + str(pair_before["a"]) + ":" + str(pair_before["b"])
            if key != row["pair_key"] or pair_before != pair_after:
                raise ValueError("Pair content changed or key mismatch: " + key)
            writer.writerow({
                "pair_index": str(index),
                "pair_key": key,
                "type": pair_before["type"],
                "decision": "reviewed unchanged after author review",
                "before_sha256": digest(pair_before),
                "after_sha256": digest(pair_after),
                "rationale": row["rationale"],
                "sources": row["sources"],
            })

    # Update only the exact pending vocabulary and pair rows.
    with REGISTRY.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        register_rows = list(reader)
    transitioned = []
    for id in EXPECTED_IDS:
        row = next((r for r in register_rows if r["kind"] == "vocab" and r["key"] == id), None)
        if row is None or row["finalReview"] != "pending":
            raise ValueError("Expected pending vocabulary row missing or already reviewed: " + id)
        row["finalReview"] = "fixed_rechecked"
        row["evidence"] = "completion/v176-acceptance.tsv:" + id + "; exact field review and Chromium regression; author review, not independent"
        transitioned.append("vocab:" + id)
    for pair_row in pair_inputs:
        key = pair_row["pair_key"]
        row = next((r for r in register_rows if r["kind"] == "vocab_pair" and r["key"] == key), None)
        if row is None or row["finalReview"] != "pending":
            raise ValueError("Expected pending pair row missing or already reviewed: " + key)
        row["finalReview"] = "reviewed"
        row["evidence"] = "completion/v176-pair-review.tsv:" + pair_row["pair_index"] + "; author pair review; unchanged; not independent"
        transitioned.append("vocab_pair:" + key)
    with REGISTRY.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(register_rows)

    counts = Counter(row["finalReview"] for row in register_rows)
    vocab_counts = Counter(row["finalReview"] for row in register_rows if row["kind"] == "vocab")
    pair_counts = Counter(row["finalReview"] for row in register_rows if row["kind"] == "vocab_pair")
    if dict(counts) != {"reviewed": 3885, "fixed_rechecked": 37, "pending": 1920}:
        raise ValueError("Overall registry count mismatch: " + repr(dict(counts)))
    if dict(vocab_counts) != {"reviewed": 3325, "fixed_rechecked": 36, "pending": 553}:
        raise ValueError("Vocabulary registry count mismatch: " + repr(dict(vocab_counts)))
    if pair_counts["reviewed"] < 4 or pair_counts["pending"] != 855:
        raise ValueError("Lexical pair registry count mismatch: " + repr(dict(pair_counts)))
    pending_ids = [int(row["key"]) for row in register_rows if row["kind"] == "vocab" and row["finalReview"] == "pending"]
    next_pending = pending_ids[:14]
    author_credit = vocab_counts["reviewed"] + vocab_counts["fixed_rechecked"]
    registry_result = {
        "pass": True,
        "newly_transitioned_this_run": len(transitioned),
        "cards_fixed_rechecked": len(EXPECTED_IDS),
        "pairs_reviewed_unchanged": len(pair_inputs),
        "registry_counts": dict(counts),
        "vocabulary_counts": dict(vocab_counts),
        "lexical_pair_counts": dict(pair_counts),
        "author_credit": str(author_credit) + "/3914",
        "pending_vocab_ids_first_14": next_pending,
        "independent_acceptance": False,
        "physical_acceptance": False,
        "provenance_legal_acceptance": False,
    }
    (WORK / "registry-results.json").write_text(
        json.dumps(registry_result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    html_hash = prep["checkpoint_sha256"]
    html_bytes = prep["checkpoint_bytes"]
    audit_path = ROOT / "JLPT_N1_v176_audit.md"
    audit = audit_path.read_text(encoding="utf-8")
    if "__HTML_SHA256__" not in audit or "__HTML_BYTES__" not in audit:
        raise ValueError("Audit template placeholders missing")
    audit = audit.replace("__HTML_SHA256__", html_hash).replace("__HTML_BYTES__", str(html_bytes))
    audit_path.write_text(audit, encoding="utf-8")

    readme_path = ROOT / "README.md"
    readme_lines = readme_path.read_text(encoding="utf-8").splitlines()
    if len(readme_lines) < 7 or "v175" not in readme_lines[2] or "v175" not in readme_lines[4]:
        raise ValueError("Unexpected README v175 top block")
    readme_lines[2] = "Актуальна **v176**. [Повний HTML](JLPT_N1_ukrainian_reading_v176.html) · [Аудит](JLPT_N1_v176_audit.md)"
    readme_lines[4] = "У v176 авторськи переглянуто 12 pending карток C10: десять виправлено й повторно перевірено; ID255 та ID327 залишено pending через недостатній пул reading після уточнення POS. Чотири лексичні пари (72, 81, 85, 167) переглянуто без зміни. Збережено 3914 слів, 130 конструкцій, 160 текстів і 381 питання читання. SHA-256 HTML: " + html_hash + "."
    readme_lines[6] = "Після v176 авторськи зараховано **3361 із 3914** словникових карток; завершальний реєстр — **3885 reviewed / 37 fixed_rechecked / 1920 pending**. C10 лишається відкритим; перші pending ID: " + ", ".join(str(x) for x in next_pending) + ". C07, C11, C12, незалежне мовне, фізичне та правове/походження приймання не завершені."
    readme_path.write_text("\n".join(readme_lines) + "\n", encoding="utf-8")

    status_path = ROOT / "PROJECT_STATUS.md"
    status = status_path.read_text(encoding="utf-8")
    old_current = "## Поточний випуск v175 — C10 follow-up"
    old_archive = "## Архівований випуск v174"
    if old_current not in status or old_archive not in status:
        raise ValueError("Unexpected PROJECT_STATUS release structure")
    start = status.index(old_current)
    end = status.index(old_archive, start)
    old_block = status[start:end].strip()
    archived = old_block.replace(old_current, "## Архівований випуск v175 — 13 листопада 2026", 1)
    top_old = status.splitlines()[2]
    if "v175" not in top_old or EXPECTED_BASE not in top_old:
        raise ValueError("Unexpected PROJECT_STATUS top hash/version")
    top_new = (
        "Оновлено 13 листопада 2026. Актуальна **v176**. Основа main перед випуском — "
        + "bcc3f1ca290fb376094e53d83b65225694b96612 (v175). Повний "
        + "JLPT_N1_ukrainian_reading_v176.html, " + f"{html_bytes:,}".replace(",", " ")
        + " байт, SHA-256 " + html_hash + ". [Аудит](JLPT_N1_v176_audit.md)"
    )
    new_block = """## Поточний випуск v176 — C10 follow-up

Авторськи переглянуто 12 pending карток: десять виправлено в десяти точних полях і повторно перевірено (ID278, 330, 332, 335, 339, 347, 349, 350, 353, 355); ID255 і ID327 залишено pending через несумісність уточнених POS-позначок із мінімальним пулом reading. Чотири лексичні пари (72, 81, 85, 167) переглянуто без зміни. Авторський credit — **3361/3914**; реєстр — **3885 reviewed /37 fixed_rechecked /1920 pending**; словниковий зріз — **3325 reviewed /36 fixed_rechecked /553 pending**.

Детермінований preparer підтвердив точну основу v175, десять змінених полів, незмінність 3914 словникових записів, 130 граматичних конструкцій, 859 лексичних пар і повний rollback. Chromium перевірив 12 карток, усі приклади й десять полів при 360, 412 і 1280 px; чотири пари лишилися незмінними; sentinel прогресу не змінився. Додаткова перевірка точного quizReadingOptions показала: поточні POS дають щонайменше три варіанти для ID255/278/327; запропоновані повніші позначки дають відповідно 0, 0 і 2. Тому механізм вправ не змінювали, а ID255/327 залишили відкритими. Докази: [аудит v176](JLPT_N1_v176_audit.md), [acceptance](completion/v176-acceptance.tsv), [pair review](completion/v176-pair-review.tsv), [prepare](completion/v176-prepare-results.json), [Chromium](completion/v176-browser-results.json), [registry](completion/v176-registry-results.json).

C10 не завершено. Наступні pending ID за реєстром: """ + ", ".join(str(x) for x in next_pending) + """. Поточна робоча гілка — work/v176-c10-remaining-open-ids; наступний checkpoint планується у work/v177-c10-pos-followups. C07 для ID230/3890, C11 (семантична якість автоматичних вправ), C12 (21 середній і 19 довгих текстів), C14, C16 і C17 залишаються відкритими. Незалежне мовне, правове/походження та фізичне приймання не виконані. v176 — проміжний випуск, не кандидат 1.0.

"""
    status = status[:start] + new_block + archived + "\n\n" + status[end:]
    status = status.replace(top_old, top_new, 1)
    status_path.write_text(status, encoding="utf-8")

    backlog_path = ROOT / "completion" / "BACKLOG.md"
    backlog = backlog_path.read_text(encoding="utf-8")
    top_line = next((line for line in backlog.splitlines() if line.startswith("Оновлено 13 листопада 2026")), None)
    if top_line is None or "Поточний HTML — v175" not in top_line:
        raise ValueError("Unexpected BACKLOG top status")
    backlog = backlog.replace(top_line, top_line.replace("Поточний HTML — v175", "Поточний HTML — v176").replace("c3083a18181429e29fb1d63dcc4e9d39c5d68ccde49253b4f572820b27e1fb86", html_hash), 1)
    rows = backlog.splitlines()
    c10_index = next((i for i, line in enumerate(rows) if line.startswith("| C10 |")), None)
    if c10_index is None or "v175" not in rows[c10_index]:
        raise ValueError("C10 BACKLOG row missing v175 history")
    if "v176:" not in rows[c10_index]:
        rows[c10_index] = rows[c10_index][:-1] + " v176: десять карток fixed_rechecked, дві POS/reading залежності pending; чотири пари reviewed; credit 3361/3914; докази v176-acceptance.tsv, v176-pair-review.tsv, v176-registry-results.json. Незалежне та фізичне приймання окремі. |"
    section = """## C10 follow-up ID255–355 — 13 листопада 2026

У v176 авторськи переглянуто 12 раніше pending карток із використанням рішень пілота v153 та batch-нотаток: 10 виправлено й повторно перевірено; 2 залишено pending через доведену залежність POS-позначки від reading-пулу. Чотири лексичні пари перевірено без зміни. Повний поіменний розбір і джерела: completion/C10-followup-255-355-20261113.md; acceptance: completion/v176-acceptance.tsv; pair review: completion/v176-pair-review.tsv.

"""
    if "## C10 follow-up ID255–355 — 13 листопада 2026" not in backlog:
        backlog = "\n".join(rows).rstrip() + "\n\n" + section
    else:
        backlog = "\n".join(rows).rstrip() + "\n"
    backlog_path.write_text(backlog, encoding="utf-8")

    print(json.dumps({
        "pass": True,
        "html_sha256": html_hash,
        "html_bytes": html_bytes,
        "author_credit": str(author_credit) + "/3914",
        "registry_counts": dict(counts),
        "vocabulary_counts": dict(vocab_counts),
        "newly_transitioned": len(transitioned),
        "next_pending": next_pending,
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
