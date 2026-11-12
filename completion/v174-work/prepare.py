#!/usr/bin/env python3
"""Reproduce the exact v174 C10 follow-up from published v173."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import subprocess

SOURCE = Path("JLPT_N1_ukrainian_reading_v173.html")
TARGET = Path("JLPT_N1_ukrainian_reading_v174.html")
UPDATES = Path("completion/v174-work/updates.json")
BASE_SHA256 = "e04cad2441928457d359bd7fb9f42123bf6eec75ffac104db671f1d51edf6d6f"

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

def main():
    raw = SOURCE.read_bytes()
    source_hash = hashlib.sha256(raw).hexdigest()
    if source_hash != BASE_SHA256:
        raise ValueError(f"Published v173 baseline changed: {source_hash}")
    original = raw.decode("utf-8")
    cards, start, end = block(original, "VOCAB_DETAILS_BY_ID")
    original_cards = json.loads(json.dumps(cards, ensure_ascii=False))
    updates = json.loads(UPDATES.read_text(encoding="utf-8"))
    if len(updates) != 3 or {row["id"] for row in updates} != {3828, 3836, 3900}:
        raise ValueError("Expected exactly IDs 3828, 3836 and 3900")
    for row in updates:
        card = cards[str(row["id"])]
        if card["w"] != row["headword"]:
            raise ValueError(f"Headword mismatch for {row['id']}")
        index = int(row["field"].split(".")[-1])
        if card["exampleTranslations"][index] != row["before"]:
            raise ValueError(f"Before-value mismatch for {row['id']}")
        card["exampleTranslations"][index] = row["after"]
    html = original[:start] + compact(cards) + original[end:]
    old_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v173</title>"
    new_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v174</title>"
    if html.count(old_title) != 1:
        raise ValueError("Unexpected v173 title")
    html = html.replace(old_title, new_title, 1)

    after_cards, _, _ = block(html, "VOCAB_DETAILS_BY_ID")
    changed = [key for key in original_cards if original_cards[key] != after_cards[key]]
    if changed != ["3828", "3836", "3900"]:
        raise ValueError(f"Unexpected changed card IDs: {changed}")
    for row in updates:
        restored_card = json.loads(json.dumps(after_cards[str(row["id"])], ensure_ascii=False))
        index = int(row["field"].split(".")[-1])
        restored_card["exampleTranslations"][index] = row["before"]
        if restored_card != original_cards[str(row["id"])]:
            raise ValueError(f"Unexpected field mutation in {row['id']}")
    if after_cards["3820"] != original_cards["3820"]:
        raise ValueError("ID3820 must be reviewed without content changes")

    vocab, _, _ = block(html, "DEFAULT_VOCAB")
    grammar, _, _ = block(html, "GRAMMAR_DETAILS_BY_ID")
    pos, _, _ = block(html, "VOCAB_POS_BY_ID")
    pairs, _, _ = block(html, "VOCAB_AUDITED_PAIRS")
    if len(vocab) != 3914 or len(cards) != 3914 or len(grammar) != 130 or len(pos) != 3914 or len(pairs) != 859:
        raise ValueError("Record counts changed")
    if list(cards) != list(original_cards):
        raise ValueError("Vocabulary ID order changed")

    restored = html.replace(new_title, old_title, 1)
    restored_cards, restored_start, restored_end = block(restored, "VOCAB_DETAILS_BY_ID")
    for row in updates:
        index = int(row["field"].split(".")[-1])
        restored_cards[str(row["id"])]["exampleTranslations"][index] = row["before"]
    restored = restored[:restored_start] + compact(restored_cards) + restored[restored_end:]
    if restored != original:
        raise ValueError("Exact rollback did not restore v173")

    scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", html, re.S)
    checked = 0
    for script in scripts:
        if script.strip():
            subprocess.run(["node", "--check", "-"], input=script, text=True, check=True)
            checked += 1
    result_bytes = html.encode("utf-8")
    TARGET.write_bytes(result_bytes)
    result = {
        "base_version": "v173",
        "base_sha256": source_hash,
        "checkpoint_version": "v174",
        "checkpoint_sha256": hashlib.sha256(result_bytes).hexdigest(),
        "checkpoint_bytes": len(result_bytes),
        "vocabulary_records": len(vocab),
        "grammar_records": len(grammar),
        "vocab_pos_records": len(pos),
        "lexical_pairs": len(pairs),
        "changed_ids": changed,
        "changed_fields": ["3828.exampleTranslations.0", "3836.exampleTranslations.1", "3900.exampleTranslations.0"],
        "operations": 3,
        "reviewed_without_change": [3820],
        "inline_scripts_checked": checked,
        "exact_rollback": True,
        "pass": True
    }
    Path("completion/v174-work/prepare-results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
