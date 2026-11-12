#!/usr/bin/env python3
"""Extract exact v171 records for the already-adjudicated C10 follow-up batch."""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path

HTML = Path("JLPT_N1_ukrainian_reading_v171.html")
IDS = [3701, 3710, 3716, 3723, 3724, 3725, 3736, 3739, 3742, 3745, 3747, 3753, 3757, 3761, 3764]

def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

def extract(source: str, name: str):
    match = re.search(r"\bconst\s+" + re.escape(name) + r"\s*=\s*", source)
    if not match:
        return None
    start = match.end()
    value, end = json.JSONDecoder().raw_decode(source, start)
    if compact(value) != source[start:end]:
        raise ValueError(f"Unexpected serialization for {name}")
    return value

def main():
    raw = HTML.read_bytes()
    source = raw.decode("utf-8")
    names = [
        "VOCAB_DETAILS_BY_ID", "VOCAB_POS_BY_ID",
        "VOCAB_KANA_EXAMPLE_TARGETS", "VOCAB_AUDITED_PAIRS",
        "AUTO_VOCAB_COMPARISONS", "REVIEWED_MEANING_QUIZZES",
        "VOCAB_DETAILS", "DEFAULT_VOCAB",
    ]
    blocks = {name: extract(source, name) for name in names}
    cards = blocks["VOCAB_DETAILS_BY_ID"]
    pos = blocks["VOCAB_POS_BY_ID"]
    if not isinstance(cards, dict) or len(cards) != 3914:
        raise ValueError("Expected exactly 3914 vocabulary records")
    if not isinstance(pos, dict):
        raise ValueError("Missing VOCAB_POS_BY_ID")
    result = {
        "source": "JLPT_N1_ukrainian_reading_v171.html",
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "vocabulary_records": len(cards),
        "target_ids": IDS,
        "records": {str(i): {"card": cards[str(i)], "pos": pos.get(str(i))} for i in IDS},
        "available_blocks": [name for name, value in blocks.items() if value is not None],
    }
    pairs = blocks.get("VOCAB_AUDITED_PAIRS")
    if isinstance(pairs, list):
        result["related_pairs"] = [p for p in pairs if any(str(i) in json.dumps(p, ensure_ascii=False) for i in IDS)]
    for name in ("VOCAB_KANA_EXAMPLE_TARGETS", "AUTO_VOCAB_COMPARISONS", "REVIEWED_MEANING_QUIZZES"):
        value = blocks.get(name)
        if isinstance(value, dict):
            result[name] = {k: v for k, v in value.items() if any(str(i) in k for i in IDS)}
    out = Path("completion/v172-work/inspect-targets.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"pass": True, "sha256": result["source_sha256"], "ids": len(IDS), "blocks": result["available_blocks"]}, ensure_ascii=False))

if __name__ == "__main__":
    main()
