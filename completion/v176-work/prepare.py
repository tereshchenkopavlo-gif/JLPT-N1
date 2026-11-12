#!/usr/bin/env python3
"""Reproduce the exact v176 C10 follow-up from the published v175 HTML."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import subprocess

SOURCE = Path("JLPT_N1_ukrainian_reading_v175.html")
TARGET = Path("JLPT_N1_ukrainian_reading_v176.html")
UPDATES = Path("completion/v176-work/updates.json")
BASE_SHA256 = "c3083a18181429e29fb1d63dcc4e9d39c5d68ccde49253b4f572820b27e1fb86"
EXPECTED_IDS = ["278", "330", "332", "335", "339", "347", "349", "350", "353", "355"]
EXPECTED_FIELDS = [
    "278.m",
    "330.exampleTranslations.1",
    "332.usage",
    "335.exampleTranslations.0",
    "339.m",
    "347.m",
    "349.exampleTranslations.1",
    "350.exampleTranslations.1",
    "353.m",
    "355.exampleTranslations.0",
]
PAIR_INDEXES = [72, 81, 85, 167]
PENDING_IDS = ["255", "327"]

def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

def block(source, name):
    match = re.search(r"\bconst\s+" + re.escape(name) + r"\s*=\s*", source)
    if not match:
        raise ValueError("Missing block " + name)
    start = match.end()
    value, end = json.JSONDecoder().raw_decode(source, start)
    if compact(value) != source[start:end]:
        raise ValueError("Unexpected serialization in " + name)
    return value, start, end

def get_path(value, path):
    current = value
    for part in path.split("."):
        current = current[int(part)] if isinstance(current, list) else current[part]
    return current

def set_path(value, path, replacement):
    parts = path.split(".")
    last = parts.pop()
    current = value
    for part in parts:
        current = current[int(part)] if isinstance(current, list) else current[part]
    if isinstance(current, list):
        current[int(last)] = replacement
    else:
        current[last] = replacement

def main():
    raw = SOURCE.read_bytes()
    source_hash = hashlib.sha256(raw).hexdigest()
    if source_hash != BASE_SHA256:
        raise ValueError("Published v175 baseline changed: " + source_hash)
    original = raw.decode("utf-8")
    cards, start, end = block(original, "VOCAB_DETAILS_BY_ID")
    original_cards = json.loads(json.dumps(cards, ensure_ascii=False))
    updates = json.loads(UPDATES.read_text(encoding="utf-8"))
    actual_fields = [str(row["id"]) + "." + row["field"] for row in updates]
    if actual_fields != EXPECTED_FIELDS:
        raise ValueError("Unexpected update scope: " + repr(actual_fields))
    for row in updates:
        card = cards[str(row["id"])]
        if card["w"] != row["headword"]:
            raise ValueError("Headword mismatch for " + str(row["id"]))
        if get_path(card, row["field"]) != row["before"]:
            raise ValueError("Before-value mismatch for " + str(row["id"]) + "." + row["field"])
        set_path(card, row["field"], row["after"])

    html = original[:start] + compact(cards) + original[end:]
    old_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v175</title>"
    new_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v176</title>"
    if html.count(old_title) != 1:
        raise ValueError("Unexpected v175 title")
    html = html.replace(old_title, new_title, 1)

    after_cards, _, _ = block(html, "VOCAB_DETAILS_BY_ID")
    changed = [key for key in original_cards if original_cards[key] != after_cards[key]]
    if changed != EXPECTED_IDS:
        raise ValueError("Unexpected changed card IDs: " + repr(changed))
    for id in changed:
        restored = json.loads(json.dumps(after_cards[id], ensure_ascii=False))
        for row in updates:
            if str(row["id"]) == id:
                set_path(restored, row["field"], row["before"])
        if restored != original_cards[id]:
            raise ValueError("Unexpected field mutation in " + id)
    for id in PENDING_IDS:
        if after_cards[id] != original_cards[id]:
            raise ValueError("Pending card was changed: " + id)

    unchanged_names = [
        "DEFAULT_VOCAB", "GRAMMAR_DETAILS_BY_ID", "VOCAB_POS_BY_ID",
        "VOCAB_AUDITED_PAIRS", "VOCAB_KANA_EXAMPLE_TARGETS",
        "REVIEWED_READING_OPTIONS", "REVIEWED_MEANING_QUIZZES",
    ]
    unchanged_counts = {}
    for name in unchanged_names:
        before, _, _ = block(original, name)
        after, _, _ = block(html, name)
        if before != after:
            raise ValueError("Unexpected change in " + name)
        unchanged_counts[name] = len(before)

    vocab, _, _ = block(html, "DEFAULT_VOCAB")
    grammar, _, _ = block(html, "GRAMMAR_DETAILS_BY_ID")
    pos, _, _ = block(html, "VOCAB_POS_BY_ID")
    pairs, _, _ = block(html, "VOCAB_AUDITED_PAIRS")
    if len(vocab) != 3914 or len(after_cards) != 3914 or len(grammar) != 130 or len(pos) != 3914 or len(pairs) != 859:
        raise ValueError("Record counts changed")
    if list(after_cards) != list(original_cards):
        raise ValueError("Vocabulary ID order changed")

    restored_html = html.replace(new_title, old_title, 1)
    restored_cards, restored_start, restored_end = block(restored_html, "VOCAB_DETAILS_BY_ID")
    for row in updates:
        set_path(restored_cards[str(row["id"])], row["field"], row["before"])
    restored_html = restored_html[:restored_start] + compact(restored_cards) + restored_html[restored_end:]
    if restored_html != original:
        raise ValueError("Exact rollback did not restore v175")

    scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", html, re.S)
    checked = 0
    for script in scripts:
        if script.strip():
            subprocess.run(["node", "--check", "-"], input=script, text=True, check=True)
            checked += 1

    result_bytes = html.encode("utf-8")
    TARGET.write_bytes(result_bytes)
    result = {
        "base_version": "v175",
        "base_sha256": source_hash,
        "checkpoint_version": "v176",
        "checkpoint_sha256": hashlib.sha256(result_bytes).hexdigest(),
        "checkpoint_bytes": len(result_bytes),
        "vocabulary_records": len(vocab),
        "grammar_records": len(grammar),
        "vocab_pos_records": len(pos),
        "lexical_pairs": len(pairs),
        "changed_ids": changed,
        "changed_fields": actual_fields,
        "operations": len(updates),
        "reviewed_without_change": [],
        "pair_reviewed_without_change": PAIR_INDEXES,
        "unresolved_pos_ids": PENDING_IDS,
        "unchanged_data_blocks": unchanged_counts,
        "inline_scripts_checked": checked,
        "exact_rollback": True,
        "pass": True,
    }
    Path("completion/v176-work/prepare-results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
