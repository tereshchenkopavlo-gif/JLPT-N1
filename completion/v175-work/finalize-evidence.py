#!/usr/bin/env python3
"""Create v175 acceptance evidence and update only the exact C10 register rows."""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path
import re

BASE = Path("JLPT_N1_ukrainian_reading_v174.html")
TARGET = Path("JLPT_N1_ukrainian_reading_v175.html")
UPDATES = Path("completion/v175-work/updates.json")
PAIR_INPUT = Path("completion/v175-work/pair-review.tsv")
REGISTRY = Path("completion/review-register.csv")
ACCEPTANCE = Path("completion/v175-acceptance.tsv")
PAIR_OUTPUT = Path("completion/v175-pair-review.tsv")
PAIR_INDEXES = [836, 838, 840, 841, 843]
CARD_IDS = [3802, 3803, 3807, 3808, 3809, 3810, 3812, 3814, 3816]
CHANGED_IDS = [3802, 3807, 3808, 3809, 3810, 3812, 3814, 3816]
PAIR_ROWS = [
    ("836", "836:3807:3822"),
    ("838", "838:3814:3817"),
    ("840", "840:3802:3803"),
    ("841", "841:3803:3832"),
    ("843", "843:3816:3820"),
]

def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

def block(source, name):
    match = re.search(r"\bconst\s+" + re.escape(name) + r"\s*=\s*", source)
    if not match:
        raise ValueError(f"Missing {name}")
    start = match.end()
    value, end = json.JSONDecoder().raw_decode(source, start)
    if compact(value) != source[start:end]:
        raise ValueError(f"Unexpected serialization in {name}")
    return value

def digest(value):
    return hashlib.sha256(compact(value).encode("utf-8")).hexdigest()

def main():
    prep = json.loads(Path("completion/v175-work/prepare-results.json").read_text(encoding="utf-8"))
    browser = json.loads(Path("completion/v175-work/browser-results.json").read_text(encoding="utf-8"))
    if prep.get("pass") is not True or browser.get("pass") is not True:
        raise ValueError("Preparation and Chromium evidence must both pass")
    if browser.get("sha256") != prep.get("checkpoint_sha256"):
        raise ValueError("Chromium result is for a different HTML hash")
    if prep.get("base_sha256") != "a012b3d50685353354417e89f4d6ab2767c8003ce1d77b4ff84ef85c77ed8c20":
        raise ValueError("v175 base hash mismatch")
    if prep.get("changed_ids") != [str(x) for x in CHANGED_IDS] or prep.get("operations") != 10:
        raise ValueError("v175 exact field scope mismatch")
    if prep.get("reviewed_without_change") != [3803] or prep.get("pair_reviewed_without_change") != PAIR_INDEXES:
        raise ValueError("v175 unchanged review scope mismatch")
    if prep.get("vocabulary_records") != 3914 or prep.get("grammar_records") != 130 or prep.get("lexical_pairs") != 859 or prep.get("exact_rollback") is not True:
        raise ValueError("v175 structural/rollback evidence mismatch")
    if browser.get("cardsChecked") != 9 or browser.get("fieldsChecked") != 10 or browser.get("pairsChecked") != 5:
        raise ValueError("Chromium scope mismatch")
    if set(x.get("width") for x in browser.get("widths", [])) != {360, 412, 1280}:
        raise ValueError("Chromium viewport coverage mismatch")
    if not all(x.get("pass") is True for x in browser.get("widths", [])):
        raise ValueError("A Chromium viewport failed")
    if browser.get("progressStorageUnchanged") is not True:
        raise ValueError("Progress storage sentinel changed")
    if len(browser.get("renderedCards", [])) != 9 or not all(
        x.get("cardRendered") and x.get("allExamplesRendered") and all(f.get("present") for f in x.get("fields", []))
        for x in browser.get("renderedCards", [])
    ):
        raise ValueError("A reviewed card or expected field did not render")

    before = block(BASE.read_text(encoding="utf-8"), "VOCAB_DETAILS_BY_ID")
    after = block(TARGET.read_text(encoding="utf-8"), "VOCAB_DETAILS_BY_ID")
    updates = json.loads(UPDATES.read_text(encoding="utf-8"))
    update_by_id = {}
    for row in updates:
        update_by_id.setdefault(str(row["id"]), []).append(row)
    if list(update_by_id) != [str(x) for x in CHANGED_IDS]:
        raise ValueError("Update IDs are not the exact expected order")
    if before["3803"] != after["3803"]:
        raise ValueError("ID3803 must be accepted without content changes")

    acceptance_rows = []
    for id in CARD_IDS:
        old, new = before[str(id)], after[str(id)]
        changed_fields = [row["field"] for row in update_by_id.get(str(id), [])]
        if id in CHANGED_IDS and not changed_fields:
            raise ValueError(f"Missing update fields for {id}")
        if id == 3803 and changed_fields:
            raise ValueError("ID3803 should have no changed fields")
        acceptance_rows.append({
            "id": id,
            "headword": new["w"],
            "before": digest(old),
            "after": digest(new),
            "changed": ";".join(changed_fields) if changed_fields else "none",
            "evidence": f"completion/C10-followup-3802-3816-20261113.md#{id}",
            "decision": "reviewed unchanged after author review" if id == 3803 else "fixed_rechecked after exact field review and Chromium regression"
        })
    with ACCEPTANCE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(["id", "headword", "card_before_sha256", "card_after_sha256", "changed_fields", "evidence", "decision"])
        for row in acceptance_rows:
            writer.writerow([row["id"], row["headword"], row["before"], row["after"], row["changed"], row["evidence"], row["decision"]])

    pair_input = list(csv.DictReader(PAIR_INPUT.open(encoding="utf-8"), delimiter="\t"))
    pair_before = block(BASE.read_text(encoding="utf-8"), "VOCAB_AUDITED_PAIRS")
    pair_after = block(TARGET.read_text(encoding="utf-8"), "VOCAB_AUDITED_PAIRS")
    if len(pair_input) != 5:
        raise ValueError("Expected exactly five pair-review decisions")
    pair_acceptance = []
    for expected_index, expected_key in PAIR_ROWS:
        row = next((x for x in pair_input if x["pair_index"] == expected_index), None)
        index = int(expected_index)
        if row is None or row["pair_key"] != expected_key or row["decision"] != "reviewed unchanged after author review":
            raise ValueError(f"Missing pair review {expected_index}")
        if pair_before[index] != pair_after[index]:
            raise ValueError(f"Pair {expected_index} unexpectedly changed")
        pair_acceptance.append({
            "pair_index": index,
            "pair_key": expected_key,
            "relation": pair_after[index].get("type", ""),
            "before": digest(pair_before[index]),
            "after": digest(pair_after[index]),
            "decision": row["decision"],
            "rationale": row["rationale"],
            "source": row["source"]
        })
    with PAIR_OUTPUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(["pair_index", "pair_key", "relation", "before_sha256", "after_sha256", "decision", "rationale", "source"])
        for row in pair_acceptance:
            writer.writerow([row["pair_index"], row["pair_key"], row["relation"], row["before"], row["after"], row["decision"], row["rationale"], row["source"]])

    registry_rows = list(csv.DictReader(REGISTRY.open(encoding="utf-8", newline="")))
    if len(registry_rows) != 5842:
        raise ValueError(f"Unexpected register row count: {len(registry_rows)}")
    targets = {}
    for id in CARD_IDS:
        targets[("vocab", str(id))] = ("reviewed" if id == 3803 else "fixed_rechecked",
            f"completion/v175-acceptance.tsv#{id}; author review and Chromium regression; v175 SHA-256={prep['checkpoint_sha256']}")
    for index, key in PAIR_ROWS:
        targets[("vocab_pair", key)] = ("reviewed",
            f"completion/v175-pair-review.tsv#{index}; author pair review, no data change; v175 SHA-256={prep['checkpoint_sha256']}")
    seen = set()
    transitioned = 0
    for row in registry_rows:
        key = (row["kind"], row["key"])
        if key not in targets:
            continue
        status, evidence = targets[key]
        if key in seen:
            raise ValueError(f"Duplicate register key {key}")
        seen.add(key)
        if row["finalReview"] == "pending":
            row["finalReview"] = status
            row["evidence"] = evidence
            transitioned += 1
        elif row["finalReview"] == status and "v175 SHA-256=" in row["evidence"]:
            pass
        else:
            raise ValueError(f"Unexpected prior register state for {key}: {row['finalReview']}")
    if seen != set(targets):
        raise ValueError(f"Missing register keys: {set(targets) - seen}")
    with REGISTRY.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["kind", "key", "baselineLocation", "finalReview", "evidence"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(registry_rows)

    counts = {}
    for row in registry_rows:
        counts[row["finalReview"]] = counts.get(row["finalReview"], 0) + 1
    expected_counts = {"reviewed": 3881, "fixed_rechecked": 27, "pending": 1934}
    if counts != expected_counts:
        raise ValueError(f"Registry counts mismatch: {counts}")
    next_pending = sorted(int(row["key"]) for row in registry_rows if row["kind"] == "vocab" and row["finalReview"] == "pending")
    next_ids = next_pending[:12]
    next_text = ", ".join(str(x) for x in next_ids) if next_ids else "—"
    registry_result = {
        "card_acceptances": 9,
        "newly_transitioned_this_run": transitioned,
        "reviewed_without_change": [3803],
        "fixed_rechecked": CHANGED_IDS,
        "pair_reviews": PAIR_INDEXES,
        "registry_counts": counts,
        "author_credit": "3351/3914",
        "next_pending_vocabulary_ids": next_ids,
        "independent_acceptance": False,
        "physical_acceptance": False,
        "pass": True
    }
    Path("completion/v175-work/registry-results.json").write_text(json.dumps(registry_result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    hash_value = prep["checkpoint_sha256"]
    byte_count = prep["checkpoint_bytes"]
    audit_path = Path("JLPT_N1_v175_audit.md")
    audit = audit_path.read_text(encoding="utf-8")
    audit = audit.replace("__V175_SHA256__", hash_value).replace("__V175_BYTES__", str(byte_count)).replace("__NEXT_PENDING_IDS__", next_text)
    audit_path.write_text(audit, encoding="utf-8")

    readme_path = Path("README.md")
    readme = readme_path.read_text(encoding="utf-8")
    replacements = [
        (r"^Актуальна \*\*v(?:174|175)\*\*.*$", f"Актуальна **v175**. [Повний HTML](JLPT_N1_ukrainian_reading_v175.html) · [Аудит](JLPT_N1_v175_audit.md)"),
        (r"^У v(?:174|175) повторно перевірено.*$", f"У v175 авторськи переглянуто 9 pending карток C10: ID3803 прийнято без зміни; ID{', '.join(str(x) for x in CHANGED_IDS)} виправлено в 10 полях і повторно перевірено. Додатково без зміни переглянуто п’ять пар 836, 838, 840, 841, 843. 3914 слів, 130 конструкцій, 160 текстів і 381 питання читання збережено. SHA-256 HTML: {hash_value}."),
        (r"^Після v(?:174|175) авторськи зараховано.*$", f"Після v175 авторськи зараховано **3351 із 3914** словникових карток; завершальний реєстр — **3881 reviewed / 27 fixed_rechecked / 1934 pending**. C10 лишається відкритим; наступні pending ID: {next_text}. C07, C11, C12, незалежне мовне, фізичне та правове/походження приймання не завершені.")
    ]
    for pattern, replacement in replacements:
        readme, count = re.subn(pattern, lambda _: replacement, readme, count=1, flags=re.M)
        if count != 1:
            raise ValueError(f"README line not replaced: {pattern}")
    readme_path.write_text(readme, encoding="utf-8")

    status_path = Path("PROJECT_STATUS.md")
    status = status_path.read_text(encoding="utf-8")
    top = f"Оновлено 13 листопада 2026. Актуальна **v175**. Основа main перед випуском — 7384ad7af1de8172f079768117fc7507af83eaf4 (v174). Повний JLPT_N1_ukrainian_reading_v175.html, {byte_count:,} байт, SHA-256 {hash_value}. [Аудит](JLPT_N1_v175_audit.md)"
    status, count = re.subn(r"^Оновлено .*?$", top, status, count=1, flags=re.M)
    if count != 1:
        raise ValueError("Could not update PROJECT_STATUS header")
    new_block = f"""## Поточний випуск v175 — C10 follow-up

Авторськи переглянуто дев’ять pending карток: ID3803 прийнято без зміни; ID{', '.join(str(x) for x in CHANGED_IDS)} виправлено в 10 полях і повторно перевірено. П’ять лексичних пар (836, 838, 840, 841, 843) переглянуто без зміни. Авторський credit — **3351/3914**; реєстр — **3881 reviewed /27 fixed_rechecked /1934 pending**.

Детермінований preparer підтвердив точну основу v174, 10 змінених полів, незмінність 3914 словникових записів, 130 граматичних конструкцій, 859 лексичних пар і повний rollback. Chromium перевірив дев’ять карток, десять полів і п’ять пар при 360, 412 і 1280 px; sentinel прогресу не змінився. Докази: [аудит v175](JLPT_N1_v175_audit.md), [acceptance](completion/v175-acceptance.tsv), [pair review](completion/v175-pair-review.tsv), [prepare](completion/v175-prepare-results.json), [Chromium](completion/v175-browser-results.json), [registry](completion/v175-registry-results.json).

C10 не завершено. Наступні pending словникові ID за реєстром: {next_text}. Поточна робоча гілка — work/v175-c10-remaining-open-ids; наступний checkpoint планується у work/v176-c10-remaining-open-ids. C07 для ID230/3890, C11 (семантична якість автоматичних вправ), C12 (21 середній і 19 довгих текстів), C14, C16 і C17 залишаються відкритими. Незалежне мовне, правове/походження та фізичне приймання не виконані. v175 — проміжний випуск, не кандидат 1.0.

"""
    current = status.find("## Поточний випуск v175 — C10 follow-up")
    if current >= 0:
        end = status.find("## Архівований випуск v174 — C10 follow-up", current)
        if end < 0:
            raise ValueError("Missing archived v174 section")
        status = status[:current] + new_block + status[end:]
    else:
        start = status.find("## Поточний випуск v174 — C10 follow-up")
        end = status.find("## Архівований checkpoint v173", start)
        if start < 0 or end < 0:
            raise ValueError("Could not locate current v174 status section")
        old_v174 = status[start:end].strip()
        archived = old_v174.replace("## Поточний випуск v174 — C10 follow-up", "## Архівований випуск v174 — C10 follow-up", 1)
        status = status[:start] + new_block + archived + "\n\n" + status[end:]
    status_path.write_text(status, encoding="utf-8")

    backlog_path = Path("completion/BACKLOG.md")
    backlog = backlog_path.read_text(encoding="utf-8")
    backlog, count = re.subn(r"^Оновлено .*?$", f"Оновлено 13 листопада 2026 (Asia/Tokyo). [Критерії й порядок](PLAN.md). Поточний HTML — v175, SHA-256 {hash_value}; початкова інвентаризація зафіксована на v135. C04 закрито окремим звітом, C27 виконано у v171, історичні дані не переписано.", backlog, count=1, flags=re.M)
    if count != 1:
        raise ValueError("Could not update BACKLOG header")
    summary = f"v175 — C10 follow-up: дев’ять карток авторськи переглянуто (8 fixed_rechecked, 1 reviewed без зміни), п’ять пар reviewed без зміни; 10 точних полів. Авторський credit 3351/3914; реєстр 3881/27/1934. Докази: v175-acceptance.tsv, v175-pair-review.tsv, v175-prepare-results.json, v175-browser-results.json, v175-registry-results.json та JLPT_N1_v175_audit.md. Незалежне, фізичне й правове/походження приймання окремі."
    if "v175 — C10 follow-up:" not in backlog:
        lines = backlog.splitlines()
        insert_at = next((i + 1 for i, line in enumerate(lines) if line.startswith("Оновлено ")), 3)
        lines.insert(insert_at, "")
        lines.insert(insert_at + 1, summary)
        backlog = "\n".join(lines) + "\n"
    c10_lines = backlog.splitlines()
    for i, line in enumerate(c10_lines):
        if line.startswith("| C10 |") and "v175:" not in line:
            c10_lines[i] = line[:-1] + f" v175: 9 карток (8 fixed_rechecked, 1 reviewed), 5 пар reviewed; 3351/3914; наступні pending: {next_text}. |"
            break
    backlog_path.write_text("\n".join(c10_lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "pass": True,
        "checkpoint_sha256": hash_value,
        "checkpoint_bytes": byte_count,
        "card_acceptances": 9,
        "pair_reviews": 5,
        "newly_transitioned_this_run": transitioned,
        "registry_counts": counts,
        "author_credit": "3351/3914",
        "next_pending_vocabulary_ids": next_ids
    }, ensure_ascii=False))

if __name__ == "__main__":
    main()
