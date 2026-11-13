import csv
import hashlib
import json
import re
from pathlib import Path

BASE = Path("JLPT_N1_ukrainian_reading_v181.html")
OUT = Path("JLPT_N1_ukrainian_reading_v182.html")
WORK = Path("completion/v182-work")
WORK.mkdir(parents=True, exist_ok=True)
BASE_SHA256 = "32c6f482db1e98dd1f98deb0197324a037fbd1a1bae8d5dd4b4f7123f126da7f"

POS_UPDATES = {
    "255": ["名詞", "ナ形"],
    "327": ["名詞", "ナ形"],
}
USAGE_UPDATES = {
    "255": "Іменник, な-прикметник і прислівник: 直接会う, 直接の原因, 直接な交渉 (формальне атрибутивне вживання), 直接的な影響. Означає відсутність посередника або проміжної ланки; не обов’язково фізичну зустріч. じかに близьке в побутових контекстах. Протилежне — 間接.",
    "327": "Іменник, な-прикметник і する-дієслово: 浮気を疑う, 浮気な人, 浮気する. Невірність партнерові; у переносному вживанні — тимчасове захоплення іншим заняттям або брендом. 不倫 часто передбачає зв’язок із людиною, яка перебуває в шлюбі; 浮気 можливе й у неодруженої пари.",
}
READING_UPDATES = {
    "255": {"word": "直接", "correct": "ちょくせつ", "wrong": ["ちょうせつ", "ちょうせい", "がくせつ"]},
    "327": {"word": "浮気", "correct": "うわき", "wrong": ["いしき", "いせき", "うつわ"]},
    "1819": {"word": "内訳", "correct": "うちわけ", "wrong": ["うちがわ", "うつわ", "うわき"]},
}


def extract_json_const(text, name):
    match = re.search(r"const " + re.escape(name) + r"\s*=\s*", text)
    if not match:
        raise RuntimeError(f"missing JS constant: {name}")
    start = match.end()
    if text[start] not in "[{":
        raise RuntimeError(f"{name} is not a JSON array/object")
    opening = text[start]
    closing = "]" if opening == "[" else "}"
    depth = 0
    in_string = False
    escaped = False
    end = None
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == opening:
            depth += 1
        elif ch == closing:
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        raise RuntimeError(f"unterminated JSON constant: {name}")
    literal = text[start:end]
    return start, end, literal, json.loads(literal)


def replace_json_const(text, name, value):
    start, end, old_literal, _ = extract_json_const(text, name)
    new_literal = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return text[:start] + new_literal + text[end:], old_literal, new_literal


def cloze_count(vocab, details, pos_map, target_id):
    target_pos = pos_map[str(target_id)]
    target = next(x for x in vocab if int(x["id"]) == target_id)
    return sum(
        1 for x in vocab
        if int(x["id"]) != target_id
        and str(x["id"]) in details
        and pos_map[str(x["id"])] == target_pos
        and not re.search(r"[〜～・／/]", x["w"])
    )


base_bytes = BASE.read_bytes()
base_sha = hashlib.sha256(base_bytes).hexdigest()
if base_sha != BASE_SHA256:
    raise RuntimeError(f"unexpected v181 HTML SHA-256: {base_sha}")
base = base_bytes.decode("utf-8")

_, _, _, vocab = extract_json_const(base, "DEFAULT_VOCAB")
_, _, _, grammar = extract_json_const(base, "GRAMMAR_DETAILS_BY_ID")
_, _, _, details = extract_json_const(base, "VOCAB_DETAILS_BY_ID")
_, _, _, pos = extract_json_const(base, "VOCAB_POS_BY_ID")
_, _, _, pairs = extract_json_const(base, "VOCAB_AUDITED_PAIRS")
_, _, _, base_reading_overrides = extract_json_const(base, "REVIEWED_READING_OPTIONS")

if len(vocab) != 3914 or len(grammar) != 130 or len(details) != 3914 or len(pairs) != 859:
    raise RuntimeError("base record counts do not match approved scope")
if len({int(x["id"]) for x in vocab}) != 3914 or len(pos) != 3914:
    raise RuntimeError("base vocabulary IDs or POS map are not unique/complete")
if base_reading_overrides != {"3005": {"word": "著しい", "correct": "いちじるしい", "wrong": ["いちずるしい", "いちじらしい", "いちじろしい"]}}:
    raise RuntimeError("unexpected existing reviewed reading override")

by_id = {int(x["id"]): x for x in vocab}
expected_cards = {
    255: ("直接", "ちょくせつ", ["名詞"]),
    327: ("浮気", "うわき", ["名詞"]),
    1819: ("内訳", "うちわけ", ["名詞"]),
    359: ("本気", "ほんき", ["名詞", "ナ形"]),
}
for card_id, (word, expected_reading, old_pos) in expected_cards.items():
    item = by_id[card_id]
    if (item["w"], item["r"], pos[str(card_id)]) != (word, expected_reading, old_pos):
        raise RuntimeError(f"unexpected baseline card {card_id}")

# Verify every manual distractor is an existing, different headword's recorded reading.
source_ids = {
    "255": {"ちょうせつ": 1724, "ちょうせい": 1723, "がくせつ": 950},
    "327": {"いしき": 4, "いせき": 832, "うつわ": 709},
    "1819": {"うちがわ": 285, "うつわ": 709, "うわき": 327},
}
for target_id, mapping in source_ids.items():
    for kana, source_id in mapping.items():
        if by_id[source_id]["r"] != kana or by_id[source_id]["id"] == int(target_id):
            raise RuntimeError(f"invalid distractor source {target_id}: {kana} -> {source_id}")

before_cloze = {str(i): cloze_count(vocab, details, pos, i) for i in [255, 327, 1819, 359]}
new_pos = dict(pos)
new_pos.update(POS_UPDATES)
new_details = json.loads(json.dumps(details, ensure_ascii=False))
for card_id, usage in USAGE_UPDATES.items():
    new_details[card_id]["usage"] = usage
new_reading = dict(base_reading_overrides)
new_reading.update(READING_UPDATES)
after_cloze = {str(i): cloze_count(vocab, details, new_pos, i) for i in [255, 327, 1819, 359]}

candidate = base
old_blocks = {}
new_blocks = {}
for name, value in [
    ("VOCAB_POS_BY_ID", new_pos),
    ("VOCAB_DETAILS_BY_ID", new_details),
    ("REVIEWED_READING_OPTIONS", new_reading),
]:
    candidate, old_literal, new_literal = replace_json_const(candidate, name, value)
    old_blocks[name] = old_literal
    new_blocks[name] = new_literal

old_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v181</title>"
new_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v182</title>"
if candidate.count(old_title) != 1:
    raise RuntimeError("expected v181 title marker was not found exactly once")
candidate = candidate.replace(old_title, new_title, 1)

reverse = candidate.replace(new_title, old_title, 1)
for name in ["REVIEWED_READING_OPTIONS", "VOCAB_DETAILS_BY_ID", "VOCAB_POS_BY_ID"]:
    if reverse.count(new_blocks[name]) != 1:
        raise RuntimeError(f"cannot reverse {name} exactly")
    reverse = reverse.replace(new_blocks[name], old_blocks[name], 1)
if reverse != base:
    raise RuntimeError("v182 patch is not exactly reversible to v181")

for target_id, payload in READING_UPDATES.items():
    choices = [payload["correct"], *payload["wrong"]]
    if len(payload["wrong"]) != 3 or len(set(choices)) != 4 or payload["correct"] in payload["wrong"]:
        raise RuntimeError(f"invalid reviewed reading options for {target_id}")

out_bytes = candidate.encode("utf-8")
OUT.write_bytes(out_bytes)
digest = hashlib.sha256(out_bytes).hexdigest()

prepare = {
    "pass": True,
    "base_version": "v181",
    "base_sha256": base_sha,
    "base_bytes": len(base_bytes),
    "candidate_version": "v182",
    "candidate_sha256": digest,
    "candidate_bytes": len(out_bytes),
    "vocabulary_records": len(vocab),
    "grammar_records": len(grammar),
    "lexical_pairs": len(pairs),
    "unique_vocabulary_ids": 3914,
    "pos_updates": POS_UPDATES,
    "usage_updates": sorted(USAGE_UPDATES),
    "reading_override_ids_added": sorted(READING_UPDATES),
    "reading_override_entries_before": len(base_reading_overrides),
    "reading_override_entries_after": len(new_reading),
    "reading_pool_diagnostic": "completion/v180-c11-diagnostics.json",
    "reading_pool_review_scope": 23,
    "cloze_candidates_before": before_cloze,
    "cloze_candidates_after": after_cloze,
    "changed_blocks": ["VOCAB_POS_BY_ID", "VOCAB_DETAILS_BY_ID", "REVIEWED_READING_OPTIONS", "document title"],
    "unchanged": {
        "vocabulary_records": True,
        "grammar_records": True,
        "lexical_pairs": True,
        "all_ids": True,
        "learning_engine": True,
        "progress_storage_code": True,
        "reading_quiz_algorithm": True,
        "cloze_algorithm": True,
        "reviewed_meaning_quizzes": True
    },
    "exact_rollback": True,
    "full_card_credit_changed": False,
    "author_review_only": True
}
(WORK / "prepare-results.json").write_text(json.dumps(prepare, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
updates = [
    {"op": "replace", "block": "VOCAB_POS_BY_ID", "path": ["255", "327"], "before": {"255": ["名詞"], "327": ["名詞"]}, "after": POS_UPDATES, "evidence": "completion/v182-work/source-review.md"},
    {"op": "replace", "block": "VOCAB_DETAILS_BY_ID", "path": ["255", "usage", "327", "usage"], "before": {"255": details["255"]["usage"], "327": details["327"]["usage"]}, "after": USAGE_UPDATES, "evidence": "completion/v182-work/source-review.md"},
    {"op": "add", "block": "REVIEWED_READING_OPTIONS", "path": ["255", "327", "1819"], "before": None, "after": READING_UPDATES, "source_ids": source_ids, "evidence": "completion/v182-reading-pool-review.tsv"}
]
(WORK / "updates.json").write_text(json.dumps(updates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
checkpoint = {
    "checkpoint": "v182-c11-reading-pool-review",
    "created": "2026-11-13",
    "base_main_sha": "d225ad1e5f023a776153394562287f4bff920cb5",
    "base_html": "JLPT_N1_ukrainian_reading_v181.html",
    "base_html_sha256": BASE_SHA256,
    "previous_status_work_branch": "work/v181-c11-id2433-quiz-review",
    "previous_status_work_head": "bb8732d5847bc0a3407ced17e0bdae37bcef8e6d",
    "diagnostic_checkpoint": "completion/v180-c11-checkpoint.json",
    "diagnostic_sha256": "479e95f7f53287cd4ea2a9d1144e0e1d516731a2cc5f4c29dc76c2bc3cceb34a",
    "scope": ["23 reading pools affected by ID255/327 POS correction", "ID1819 minimum distractor eligibility", "ID359 gained pool quality", "POS/usage source review for ID255 and ID327"],
    "guardrails": ["content-only POS/usage and existing reviewed-reading override fields", "no learning algorithm changes", "no grammar or lexical-pair changes", "no user progress/storage changes", "no full-card credit for partial field review", "no data or ID removal"],
    "status": "candidate prepared; awaiting Chromium verification",
    "candidate_sha256": digest,
    "candidate_bytes": len(out_bytes)
}
(WORK / "checkpoint.json").write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(prepare, ensure_ascii=False, indent=2))
