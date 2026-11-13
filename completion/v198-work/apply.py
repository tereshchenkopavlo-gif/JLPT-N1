import csv, hashlib, json, re
from pathlib import Path

BASE = Path("JLPT_N1_ukrainian_reading_v197.html")
OUT = Path("JLPT_N1_ukrainian_reading_v198.html")
WORK = Path("completion/v198-work")
REGISTER = Path("completion/review-register.csv")
BASE_SHA = "d158eb7d7a619718e982ad4117f603f208339178d47ec0417c2adeab238c1620"

UPDATES = [
    ("1015", "exampleTranslations[1]", "Самої лише високоякісної знімальної апаратури недостатньо для створення гарного твору.", "Самої лише знімальної апаратури з високими технічними характеристиками недостатньо, щоб створити хороший твір."),
    ("1016", "usage", "Іменник; 実家に帰省する、帰省中. Тимчасово повернутися до батьківського дому чи рідних місць, часто відвідати родину. 帰郷 ширше — повернення на батьківщину, також постійне. Святкова дата для 帰省 не обов’язкова.", "Іменник; 実家に帰省する、帰省中. Тимчасово повернутися до батьківського дому чи рідних місць, часто відвідати родину. 帰郷 ширше — повернення в рідні місця; може бути постійним. Святкова дата для 帰省 не обов’язкова."),
    ("1026", "exampleTranslations[0]", "Багато родичів вступників відвідують святилище, щоб помолитися про успішне складання іспитів.", "Багато родичів тих, хто складає іспити, відвідують святилище, щоб помолитися за їхній успіх."),
    ("1027", "m", "物事の内容や手続きを、規則として定めること。", "物事の内容や手続きを、規則として定めること。また、そのように定められた条項や規則。")
]
EXPECTED = {
    "1015": ("機材", "きざい", ["名詞"]),
    "1016": ("帰省", "きせい", ["名詞"]),
    "1026": ("祈願", "きがん", ["名詞"]),
    "1027": ("規定", "きてい", ["名詞"])
}
EXPECTED_EXAMPLES = {
    "1015": ["工事に使う機材の搬入が遅れ、予定していた着工が先送りとなった。", "高性能な撮影機材をそろえるだけで、良い作品ができるわけではない。"],
    "1016": ["年末年始に帰省する人々で、新幹線の主要駅は大変な混雑となった。", "仕事が忙しく、この数年は帰省できないままになっている。"],
    "1026": ["受験生の家族が、合格祈願のために神社へ大勢参拝している。", "工事の安全を祈願して、現場で地鎮祭が執り行われた。"],
    "1027": ["法律で規定された手続きを経ずに、役所が処分を下すことはできない。", "就業規則には、休暇の取得方法が詳細に規定されている。"]
}
FIXED_IDS = ["1015", "1016", "1026", "1027"]
REVIEWED_IDS = []
PENDING_IDS = []
EXPECTED_CHANGED = FIXED_IDS
EVIDENCE = "completion/v198-acceptance.tsv; JLPT_N1_v198_audit.md"

def extract(source, name):
    match = re.search(r"\bconst " + re.escape(name) + r"\s*=\s*", source)
    if not match:
        raise RuntimeError("missing constant " + name)
    start = match.end()
    opening = source[start]
    closing = "]" if opening == "[" else "}"
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(source)):
        char = source[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        else:
            if char == '"':
                in_string = True
            elif char == opening:
                depth += 1
            elif char == closing:
                depth -= 1
                if depth == 0:
                    return start, index + 1, json.loads(source[start:index + 1])
    raise RuntimeError("unterminated constant " + name)

def counts(rows, kind=None):
    selected = [row for row in rows if kind is None or row["kind"] == kind]
    result = {status: sum(row["finalReview"] == status for row in selected) for status in ("reviewed", "fixed_rechecked", "pending")}
    result["total"] = len(selected)
    return result

WORK.mkdir(parents=True, exist_ok=True)
raw = BASE.read_bytes()
base_sha = hashlib.sha256(raw).hexdigest()
if base_sha != BASE_SHA:
    raise RuntimeError("unexpected v197 base SHA-256: " + base_sha)
base = raw.decode("utf-8")

_, _, vocab = extract(base, "DEFAULT_VOCAB")
_, _, grammar = extract(base, "GRAMMAR_DETAILS_BY_ID")
detail_start, detail_end, details = extract(base, "VOCAB_DETAILS_BY_ID")
_, _, pos_map = extract(base, "VOCAB_POS_BY_ID")
_, _, pairs = extract(base, "VOCAB_AUDITED_PAIRS")
_, _, meaning = extract(base, "REVIEWED_MEANING_QUIZZES")
_, _, reading = extract(base, "REVIEWED_READING_OPTIONS")
_, _, kana_targets = extract(base, "VOCAB_KANA_EXAMPLE_TARGETS")
_, _, example_targets = extract(base, "REVIEWED_EXAMPLE_TARGETS")

if (len(vocab), len(grammar), len(details), len(pairs)) != (3914, 130, 3914, 859):
    raise RuntimeError("protected inventory counts do not match v197")
by_id = {str(item["id"]): item for item in vocab}
scope = list(EXPECTED)
for card_id, (word, reading_value, expected_pos) in EXPECTED.items():
    item = by_id.get(card_id)
    if item is None or (item["w"], item["r"], pos_map[card_id]) != (word, reading_value, expected_pos):
        raise RuntimeError("identity/reading/POS mismatch for " + card_id)
    if details[card_id]["examples"] != EXPECTED_EXAMPLES[card_id]:
        raise RuntimeError("Japanese example preimage mismatch for " + card_id)

before = json.loads(json.dumps(details, ensure_ascii=False))
for card_id, field, old_value, new_value in UPDATES:
    if field.startswith("exampleTranslations["):
        index = int(re.search(r"\[(\d+)\]", field).group(1))
        actual = details[card_id]["exampleTranslations"][index]
        if actual != old_value:
            raise RuntimeError("translation preimage mismatch for " + card_id + "." + field)
        details[card_id]["exampleTranslations"][index] = new_value
    else:
        if details[card_id][field] != old_value:
            raise RuntimeError("field preimage mismatch for " + card_id + "." + field)
        details[card_id][field] = new_value

changed_cards = sorted((card_id for card_id in details if details[card_id] != before[card_id]), key=int)
if changed_cards != EXPECTED_CHANGED:
    raise RuntimeError("unexpected changed-card set: " + str(changed_cards))

allowed_fields = {
    "1015": {"exampleTranslations"},
    "1016": {"usage"},
    "1026": {"exampleTranslations"},
    "1027": {"m"}
}
for card_id in details:
    for field in before[card_id]:
        if before[card_id][field] != details[card_id][field] and field not in allowed_fields.get(card_id, set()):
            raise RuntimeError("unexpected field mutation: " + card_id + "." + field)
    if before[card_id]["examples"] != details[card_id]["examples"]:
        raise RuntimeError("Japanese example changed: " + card_id)

literal = json.dumps(details, ensure_ascii=False, separators=(",", ":"))
candidate = base[:detail_start] + literal + base[detail_end:]
old_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v197</title>"
new_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v198</title>"
if candidate.count(old_title) != 1:
    raise RuntimeError("version title marker mismatch")
candidate = candidate.replace(old_title, new_title, 1)
rollback = candidate.replace(new_title, old_title, 1).replace(literal, base[detail_start:detail_end], 1)
if rollback != base:
    raise RuntimeError("exact rollback failed")

protected = {
    "DEFAULT_VOCAB": vocab,
    "GRAMMAR_DETAILS_BY_ID": grammar,
    "VOCAB_POS_BY_ID": pos_map,
    "VOCAB_AUDITED_PAIRS": pairs,
    "REVIEWED_MEANING_QUIZZES": meaning,
    "REVIEWED_READING_OPTIONS": reading,
    "VOCAB_KANA_EXAMPLE_TARGETS": kana_targets,
    "REVIEWED_EXAMPLE_TARGETS": example_targets
}
for name, original in protected.items():
    _, _, after = extract(candidate, name)
    if after != original:
        raise RuntimeError("protected learning data changed: " + name)

OUT.write_bytes(candidate.encode("utf-8"))
candidate_sha = hashlib.sha256(OUT.read_bytes()).hexdigest()

register_rows = list(csv.DictReader(REGISTER.read_text(encoding="utf-8").splitlines()))
if len(register_rows) != 5847:
    raise RuntimeError("unexpected register row count: " + str(len(register_rows)))
baseline_all = {"reviewed": 3914, "fixed_rechecked": 215, "pending": 1718, "total": 5847}
baseline_vocab = {"reviewed": 3345, "fixed_rechecked": 214, "pending": 355, "total": 3914}
target_all = {"reviewed": 3914, "fixed_rechecked": 219, "pending": 1714, "total": 5847}
target_vocab = {"reviewed": 3345, "fixed_rechecked": 218, "pending": 351, "total": 3914}
current_all = counts(register_rows)
current_vocab = counts(register_rows, "vocab")
keys = [(row["kind"], row["key"]) for row in register_rows]
if len(keys) != len(set(keys)):
    raise RuntimeError("duplicate review-register keys")

rows_by_id = {}
for row in register_rows:
    if row["kind"] == "vocab" and row["key"] in scope:
        rows_by_id.setdefault(row["key"], []).append(row)
if any(len(rows_by_id.get(card_id, [])) != 1 for card_id in scope):
    raise RuntimeError("missing or duplicated register scope row")

register_mode = "already_applied"
register_changed = False
if current_all == baseline_all and current_vocab == baseline_vocab:
    for card_id in FIXED_IDS:
        row = rows_by_id[card_id][0]
        if row["finalReview"] != "pending" or row["evidence"]:
            raise RuntimeError("fixed preimage mismatch for " + card_id)
        row["finalReview"] = "fixed_rechecked"
        row["evidence"] = EVIDENCE
    register_mode = "applied_from_baseline"
    register_changed = True
elif current_all == target_all and current_vocab == target_vocab:
    for card_id in FIXED_IDS:
        row = rows_by_id[card_id][0]
        if row["finalReview"] != "fixed_rechecked":
            raise RuntimeError("fixed target mismatch for " + card_id)
        if row["evidence"] != EVIDENCE:
            row["evidence"] = EVIDENCE
            register_changed = True
else:
    raise RuntimeError("register state is neither v197 baseline nor expected v198 target")

if register_changed:
    with REGISTER.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["kind", "key", "baselineLocation", "finalReview", "evidence"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(register_rows)

after_all = counts(register_rows)
after_vocab = counts(register_rows, "vocab")
if after_all != target_all or after_vocab != target_vocab:
    raise RuntimeError("register target mismatch: " + str(after_all) + " / " + str(after_vocab))

prepare = {
    "pass": True,
    "base_version": "v197",
    "base_sha256": base_sha,
    "candidate_version": "v198",
    "candidate_sha256": candidate_sha,
    "candidate_bytes": OUT.stat().st_size,
    "vocabulary_records": len(vocab),
    "grammar_records": len(grammar),
    "lexical_pairs": len(pairs),
    "unique_vocabulary_ids": len({int(item["id"]) for item in vocab}),
    "review_scope": [int(card_id) for card_id in scope],
    "fixed_rechecked": [int(card_id) for card_id in FIXED_IDS],
    "reviewed_without_change": [],
    "already_reviewed_excluded": [1018,1021,1023,1024,1025,1030,1031,1034],
    "pending_c11": [],
    "updated_fields": len(UPDATES),
    "changed_cards": [int(card_id) for card_id in changed_cards],
    "field_updates": [{"id": int(card_id), "field": field, "before": old, "after": new} for card_id, field, old, new in UPDATES],
    "author_credit_before": 3559,
    "author_credit_addition": 4,
    "author_credit_after": 3563,
    "protected_unchanged": {name: True for name in protected},
    "japanese_examples_unchanged": True,
    "exact_rollback": True,
    "register_updated": True,
    "register_mode": register_mode,
    "author_review_only": True
}
registry = {
    "pass": True,
    "register_rows": len(register_rows),
    "before": {"all": baseline_all, "vocabulary": baseline_vocab},
    "after": {"all": after_all, "vocabulary": after_vocab},
    "fixed_rechecked_ids": [int(card_id) for card_id in FIXED_IDS],
    "reviewed_ids": [],
    "already_reviewed_excluded": [1018,1021,1023,1024,1025,1030,1031,1034],
    "pending_c11_ids": [],
    "author_credit_before": 3559,
    "author_credit_after": 3563,
    "duplicate_keys": 0,
    "records_deleted": 0,
    "history_rewritten": False
}
(WORK / "prepare-results.json").write_text(json.dumps(prepare, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(WORK / "registry-results.json").write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

checkpoint_path = WORK / "checkpoint.json"
checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
checkpoint["status"] = "corrected four-card pending scope; deterministic candidate and register prepared; Chromium verification pending"
checkpoint["candidate_sha256"] = candidate_sha
checkpoint["candidate_bytes"] = OUT.stat().st_size
checkpoint["exact_rollback"] = True
checkpoint["register_mode"] = register_mode
checkpoint_path.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({"pass": True, "candidate_sha256": candidate_sha, "candidate_bytes": OUT.stat().st_size, "fixed_rechecked": FIXED_IDS, "already_reviewed_excluded": [1018,1021,1023,1024,1025,1030,1031,1034], "updated_fields": len(UPDATES), "register_after": after_all, "vocabulary_after": after_vocab}, ensure_ascii=False, indent=2))
