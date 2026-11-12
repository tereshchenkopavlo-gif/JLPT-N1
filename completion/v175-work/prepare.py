#!/usr/bin/env python3
# PR-triggered verification is pinned to the published v174 baseline.
# This checkpoint is evaluated through the refreshed v175 draft PR.
"""Reproduce the exact v175 C10 follow-up from published v174."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import subprocess

SOURCE = Path("JLPT_N1_ukrainian_reading_v174.html")
TARGET = Path("JLPT_N1_ukrainian_reading_v175.html")
UPDATES = Path("completion/v175-work/updates.json")
BASE_SHA256 = "a012b3d50685353354417e89f4d6ab2767c8003ce1d77b4ff84ef85c77ed8c20"
EXPECTED_IDS = ["3802", "3807", "3808", "3809", "3810", "3812", "3814", "3816"]
EXPECTED_FIELDS = [
    "3802.exampleTranslations.1",
    "3807.usage",
    "3807.exampleTranslations.0",
    "3808.exampleTranslations.0",
    "3809.exampleTranslations.1",
    "3810.t",
    "3812.exampleTranslations.1",
    "3814.usage",
    "3816.t",
    "3816.exampleTranslations.1",
]
PAIR_INDEXES = [836, 838, 840, 841, 843]

def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

def block(source, name):
    match = re.search(r"\bconst\s+" + re.escape(name) + r"\s*=\s*", source)
    if not match:
        raise ValueError(f"Missing block {name}")
    start = match.end()
    value, end = json.JSONDecoder().raw_decode(source, start)
    if compact(value) != source[start:end]:
        raise ValueError(f"Unexpected serialization in {name}")
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
        raise ValueError(f"Published v174 baseline changed: {source_hash}")
    original = raw.decode("utf-8")
    cards, start, end = block(original, "VOCAB_DETAILS_BY_ID")
    original_cards = json.loads(json.dumps(cards, ensure_ascii=False))
    updates = json.loads(UPDATES.read_text(encoding="utf-8"))
    actual_fields = [f"{row['id']}.{row['field']}" for row in updates]
    if actual_fields != EXPECTED_FIELDS:
        raise ValueError(f"Unexpected update scope: {actual_fields}")
    for row in updates:
        card = cards[str(row["id"])]
        if card["w"] != row["headword"]:
            raise ValueError(f"Headword mismatch for {row['id']}")
        if get_path(card, row["field"]) != row["before"]:
            raise ValueError(f"Before-value mismatch for {row['id']}.{row['field']}")
        set_path(card, row["field"], row["after"])

    html = original[:start] + compact(cards) + original[end:]
    old_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v174</title>"
    new_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v175</title>"
    if html.count(old_title) != 1:
        raise ValueError("Unexpected v174 title")
    html = html.replace(old_title, new_title, 1)

    after_cards, _, _ = block(html, "VOCAB_DETAILS_BY_ID")
    changed = [key for key in original_cards if original_cards[key] != after_cards[key]]
    if changed != EXPECTED_IDS:
        raise ValueError(f"Unexpected changed card IDs: {changed}")
    for id in changed:
        restored = json.loads(json.dumps(after_cards[id], ensure_ascii=False))
        for row in updates:
            if str(row["id"]) == id:
                set_path(restored, row["field"], row["before"])
        if restored != original_cards[id]:
            raise ValueError(f"Unexpected field mutation in {id}")
    if after_cards["3803"] != original_cards["3803"]:
        raise ValueError("ID3803 must be reviewed without content changes")

    unchanged_names = [
        "DEFAULT_VOCAB", "GRAMMAR_DETAILS_BY_ID", "VOCAB_POS_BY_ID",
        "VOCAB_AUDITED_PAIRS", "VOCAB_KANA_EXAMPLE_TARGETS"
    ]
    unchanged_counts = {}
    for name in unchanged_names:
        before, _, _ = block(original, name)
        after, _, _ = block(html, name)
        if before != after:
            raise ValueError(f"Unexpected change in {name}")
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
        raise ValueError("Exact rollback did not restore v174")

    scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", html, re.S)
    checked = 0
    for script in scripts:
        if script.strip():
            subprocess.run(["node", "--check", "-"], input=script, text=True, check=True)
            checked += 1

    result_bytes = html.encode("utf-8")
    TARGET.write_bytes(result_bytes)
    result = {
        "base_version": "v174",
        "base_sha256": source_hash,
        "checkpoint_version": "v175",
        "checkpoint_sha256": hashlib.sha256(result_bytes).hexdigest(),
        "checkpoint_bytes": len(result_bytes),
        "vocabulary_records": len(vocab),
        "grammar_records": len(grammar),
        "vocab_pos_records": len(pos),
        "lexical_pairs": len(pairs),
        "changed_ids": changed,
        "changed_fields": actual_fields,
        "operations": len(updates),
        "reviewed_without_change": [3803],
        "pair_reviewed_without_change": PAIR_INDEXES,
        "unchanged_data_blocks": unchanged_counts,
        "inline_scripts_checked": checked,
        "exact_rollback": True,
        "pass": True
    }
    Path("completion/v175-work/prepare-results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
