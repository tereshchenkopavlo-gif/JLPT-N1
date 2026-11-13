import hashlib
import json
import re
from pathlib import Path

BASE = Path("JLPT_N1_ukrainian_reading_v182.html")
OUT = Path("JLPT_N1_ukrainian_reading_v183.html")
WORK = Path("completion/v183-work")
WORK.mkdir(parents=True, exist_ok=True)
BASE_SHA256 = "53f8dd4153cab99850d9291dbd1343a58908b2dadb877f0c3a9f223ef6e54031"

UPDATES = {
    "454": {
        "field": "t",
        "before": "бути спрямованим у певний бік; підходити для справи або людині (教師に向いている)",
        "after": "бути спрямованим у певний бік; пасувати людині; бути придатним для певної роботи чи справи",
    },
    "466": {
        "field": "exampleTranslations[1]",
        "before": "Відповідно до змін ситуації спосіб реагування гнучко змінюватимуть.",
        "after": "Зі зміною обставин підхід до реагування гнучко коригуватимуть.",
    },
    "472": {
        "field": "exampleTranslations[1]",
        "before": "Знайомство з твором дало нове відкриття.",
        "after": "Завдяки безпосередньому знайомству з твором вдалося відкрити для себе щось нове.",
    },
    "477": {
        "field": "t",
        "before": "призвичаюватися до чогось і відчувати близькість або прихильність (книг, природи, культури)",
        "after": "зближуватися з кимось; часто й невимушено звертатися до чогось, відчуваючи близькість або прихильність (читання, природа, культура)",
    },
    "477_example": {
        "field": "exampleTranslations[0]",
        "before": "Створюють середовище, де діти можуть близько знайомитися з природою.",
        "after": "Створюють умови, щоб діти могли відчути близькість до природи.",
    },
    "479": {
        "field": "t",
        "before": "тремтіти голосом, плечима чи тілом; спричиняти тремтіння або сильне хвилювання; перехідне дієслово",
        "after": "змушувати голос, плечі чи тіло тремтіти; глибоко зворушувати (心を震わせる)",
    },
    "479_example": {
        "field": "exampleTranslations[0]",
        "before": "Він говорив із тремтячими від гніву плечима.",
        "after": "Він палко звертався до співрозмовників, тремтячи плечима від гніву.",
    },
}

def extract_json_const(text, name):
    match = re.search(r"\bconst " + re.escape(name) + r"\s*=\s*", text)
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

base_bytes = BASE.read_bytes()
base_sha = hashlib.sha256(base_bytes).hexdigest()
if base_sha != BASE_SHA256:
    raise RuntimeError(f"unexpected v182 HTML SHA-256: {base_sha}")
base = base_bytes.decode("utf-8")

_, _, _, vocab = extract_json_const(base, "DEFAULT_VOCAB")
_, _, _, grammar = extract_json_const(base, "GRAMMAR_DETAILS_BY_ID")
_, _, _, details = extract_json_const(base, "VOCAB_DETAILS_BY_ID")
_, _, _, pos = extract_json_const(base, "VOCAB_POS_BY_ID")
_, _, _, pairs = extract_json_const(base, "VOCAB_AUDITED_PAIRS")
_, _, _, meaning_quizzes = extract_json_const(base, "REVIEWED_MEANING_QUIZZES")
_, _, _, reading_options = extract_json_const(base, "REVIEWED_READING_OPTIONS")
_, _, _, kana_targets = extract_json_const(base, "VOCAB_KANA_EXAMPLE_TARGETS")
_, _, _, example_targets = extract_json_const(base, "REVIEWED_EXAMPLE_TARGETS")

if len(vocab) != 3914 or len(grammar) != 130 or len(details) != 3914 or len(pairs) != 859:
    raise RuntimeError("base record counts do not match the approved scope")
ids = [int(x["id"]) for x in vocab]
if len(set(ids)) != 3914 or len(pos) != 3914 or set(map(str, ids)) != set(details):
    raise RuntimeError("base vocabulary IDs/POS/details are not complete and unique")

by_id = {str(x["id"]): x for x in vocab}
expected = {
    "454": ("向く", "むく", ["動詞"]),
    "455": ("広まる", "ひろまる", ["動詞"]),
    "458": ("合わす", "あわす", ["動詞"]),
    "459": ("込める", "こめる", ["動詞"]),
    "461": ("仕上げる", "しあげる", ["動詞"]),
    "464": ("謝る", "あやまる", ["動詞"]),
    "466": ("従う", "したがう", ["動詞"]),
    "470": ("招く", "まねく", ["動詞"]),
    "472": ("触れる", "ふれる", ["動詞"]),
    "477": ("親しむ", "したしむ", ["動詞"]),
    "479": ("震わせる", "ふるわせる", ["動詞"]),
    "483": ("生じる", "しょうじる", ["動詞"]),
}
for card_id, (word, reading, expected_pos) in expected.items():
    item = by_id[card_id]
    if (item["w"], item["r"], pos[card_id]) != (word, reading, expected_pos):
        raise RuntimeError(f"unexpected card identity/POS for ID {card_id}: {item['w']} {item['r']} {pos[card_id]}")

before_details = json.loads(json.dumps(details, ensure_ascii=False))
field_updates = []
for key, update in UPDATES.items():
    if key.endswith("_example"):
        card_id = key.split("_")[0]
    else:
        card_id = key
    field = update["field"]
    if field == "t":
        actual = details[card_id]["t"]
        if actual != update["before"]:
            raise RuntimeError(f"unexpected preimage for ID {card_id}.t")
        details[card_id]["t"] = update["after"]
    else:
        index = int(field.split("[")[1].split("]")[0])
        actual = details[card_id]["exampleTranslations"][index]
        if actual != update["before"]:
            raise RuntimeError(f"unexpected preimage for ID {card_id}.{field}")
        details[card_id]["exampleTranslations"][index] = update["after"]
    field_updates.append({"id": int(card_id), "field": field, "before": update["before"], "after": update["after"]})

changed_ids = {key for key in details if details[key] != before_details[key]}
expected_changed_ids = {"454", "466", "472", "477", "479"}
if changed_ids != expected_changed_ids:
    raise RuntimeError(f"unexpected changed card IDs: {sorted(changed_ids)}")
for card_id in details:
    old = before_details[card_id]
    new = details[card_id]
    for field in old:
        if field not in ("t", "exampleTranslations") and old[field] != new[field]:
            raise RuntimeError(f"unexpected field change on ID {card_id}: {field}")
    if old["examples"] != new["examples"]:
        raise RuntimeError(f"Japanese examples changed on ID {card_id}")

candidate, old_literal, new_literal = replace_json_const(base, "VOCAB_DETAILS_BY_ID", details)
old_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v182</title>"
new_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v183</title>"
if candidate.count(old_title) != 1:
    raise RuntimeError("expected v182 title marker was not found exactly once")
candidate = candidate.replace(old_title, new_title, 1)

# Exact rollback: only the one JSON data block and document title may differ.
reverse = candidate.replace(new_title, old_title, 1)
if reverse.count(new_literal) != 1:
    raise RuntimeError("cannot reverse VOCAB_DETAILS_BY_ID exactly")
reverse = reverse.replace(new_literal, old_literal, 1)
if reverse != base:
    raise RuntimeError("v183 patch is not exactly reversible to v182")

# Confirm all quiz dependencies and structural constants are unchanged.
for name, before_value in [
    ("DEFAULT_VOCAB", vocab),
    ("GRAMMAR_DETAILS_BY_ID", grammar),
    ("VOCAB_POS_BY_ID", pos),
    ("VOCAB_AUDITED_PAIRS", pairs),
    ("REVIEWED_MEANING_QUIZZES", meaning_quizzes),
    ("REVIEWED_READING_OPTIONS", reading_options),
    ("VOCAB_KANA_EXAMPLE_TARGETS", kana_targets),
    ("REVIEWED_EXAMPLE_TARGETS", example_targets),
]:
    _, _, _, after_value = extract_json_const(candidate, name)
    if after_value != before_value:
        raise RuntimeError(f"dependent constant unexpectedly changed: {name}")

out_bytes = candidate.encode("utf-8")
OUT.write_bytes(out_bytes)
digest = hashlib.sha256(out_bytes).hexdigest()
prepare = {
    "pass": True,
    "base_version": "v182",
    "base_sha256": base_sha,
    "base_bytes": len(base_bytes),
    "candidate_version": "v183",
    "candidate_sha256": digest,
    "candidate_bytes": len(out_bytes),
    "vocabulary_records": len(vocab),
    "grammar_records": len(grammar),
    "lexical_pairs": len(pairs),
    "unique_vocabulary_ids": len(set(ids)),
    "review_scope": [454,455,458,459,461,464,466,470,472,477,479,483],
    "author_credit_addition": 12,
    "reviewed_without_change": [455,458,459,461,464,470,483],
    "fixed_rechecked": [454,466,472,477,479],
    "field_updates": field_updates,
    "changed_blocks": ["VOCAB_DETAILS_BY_ID", "document title"],
    "unchanged": {
        "vocabulary_records": True,
        "grammar_records": True,
        "lexical_pairs": True,
        "all_ids": True,
        "pos_map": True,
        "reading_quiz_targets": True,
        "meaning_quizzes": True,
        "reading_overrides": True,
        "learning_engine": True,
        "progress_storage_code": True
    },
    "exact_rollback": True,
    "author_review_only": True
}
(WORK / "prepare-results.json").write_text(json.dumps(prepare, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(prepare, ensure_ascii=False, indent=2))
