import csv, hashlib, json, re
from pathlib import Path

BASE = Path("JLPT_N1_ukrainian_reading_v197.html")
OUT = Path("JLPT_N1_ukrainian_reading_v198.html")
WORK = Path("completion/v198-work")
REGISTER = Path("completion/review-register.csv")
BASE_SHA = "d158eb7d7a619718e982ad4117f603f208339178d47ec0417c2adeab238c1620"

UPDATES = [
    ("1018", "exampleTranslations[0]", "Він мав непоступливу вдачу майстра й ніколи не відвантажував вироби, доки не був задоволений результатом.", "Він, як справжній майстер, ніколи не відвантажував вироби, доки не був цілком задоволений результатом."),
    ("1024", "exampleTranslations[1]", "Притаманна цьому краю підприємливість сприяла появі численних підприємців.", "Ініціативний дух, притаманний цьому краю, сприяв появі багатьох підприємців."),
    ("1026", "exampleTranslations[1]", "На будівельному майданчику провели обряд освячення землі, молячись про безпеку робіт.", "На будівельному майданчику провели традиційний обряд перед початком робіт, просячи про їхню безпеку."),
    ("1034", "exampleTranslations[1]", "Нове електрогенерувальне обладнання запустили, і почалося постачання електроенергії в регіон.", "Нове обладнання для виробництва електроенергії запустили, і почалося її постачання в регіон.")
]
EXPECTED = {
    "1015": ("機材", "きざい", ["名詞"]),
    "1016": ("帰省", "きせい", ["名詞"]),
    "1018": ("気質", "きしつ／かたぎ", ["名詞"]),
    "1021": ("気配", "けはい", ["名詞"]),
    "1023": ("気品", "きひん", ["名詞"]),
    "1024": ("気風", "きふう", ["名詞"]),
    "1025": ("気流", "きりゅう", ["名詞"]),
    "1026": ("祈願", "きがん", ["名詞"]),
    "1027": ("規定", "きてい", ["名詞"]),
    "1030": ("記述", "きじゅつ", ["名詞"]),
    "1031": ("貴族", "きぞく", ["名詞"]),
    "1034": ("起動", "きどう", ["名詞"])
}
EXPECTED_EXAMPLES = {
    "1015": ["工事に使う機材の搬入が遅れ、予定していた着工が先送りとなった。", "高性能な撮影機材をそろえるだけで、良い作品ができるわけではない。"],
    "1016": ["年末年始に帰省する人々で、新幹線の主要駅は大変な混雑となった。", "仕事が忙しく、この数年は帰省できないままになっている。"],
    "1018": ["職人気質の彼は、納得がいくまで決して製品を出荷しなかった。", "この地域には、新しいものを受け入れる開放的な気質がある。"],
    "1021": ["市場には、景気が回復に向かう気配がようやく見え始めている。", "交渉が決裂する気配を察して、仲介役が急いで間に入った。"],
    "1023": ["その老紳士は、立ち居振る舞いのすべてに気品が漂っていた。", "気品のあるデザインが評価され、このブランドは長く支持されている。"],
    "1024": ["この会社には、若手の発言を尊重する自由な気風が根付いている。", "進取の気風に富んだ土地柄が、数々の起業家を生み出してきた。"],
    "1025": ["飛行機は、乱気流に巻き込まれて大きく揺れた。", "山の斜面を駆け上がる気流が、独特の雲を生み出している。"],
    "1026": ["受験生の家族が、合格祈願のために神社へ大勢参拝している。", "工事の安全を祈願して、現場で地鎮祭が執り行われた。"],
    "1027": ["法律で規定された手続きを経ずに、役所が処分を下すことはできない。", "就業規則には、休暇の取得方法が詳細に規定されている。"],
    "1030": ["報告書では、調査の経緯を客観的に記述することが重視される。", "この論文は、実験の手順をきわめて詳細に記述している。"],
    "1031": ["中世の貴族は、広大な荘園から得る収入で優雅な生活を送っていた。", "貴族階級の没落は、社会構造を大きく変える契機となった。"],
    "1034": ["システムを起動すると、設定画面が表示される。", "新型の発電設備が起動し、地域への電力供給が始まった。"]
}
FIXED_IDS = ["1018", "1024", "1026", "1034"]
REVIEWED_IDS = ["1015", "1016", "1021", "1023", "1025", "1027", "1030", "1031"]
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

allowed_fields = {card_id: {"exampleTranslations"} for card_id in FIXED_IDS}
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
target_all = {"reviewed": 3922, "fixed_rechecked": 219, "pending": 1706, "total": 5847}
target_vocab = {"reviewed": 3353, "fixed_rechecked": 218, "pending": 343, "total": 3914}
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
    for card_id in REVIEWED_IDS:
        row = rows_by_id[card_id][0]
        if row["finalReview"] != "pending" or row["evidence"]:
            raise RuntimeError("reviewed preimage mismatch for " + card_id)
        row["finalReview"] = "reviewed"
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
    for card_id in REVIEWED_IDS:
        row = rows_by_id[card_id][0]
        if row["finalReview"] != "reviewed":
            raise RuntimeError("reviewed target mismatch for " + card_id)
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
    "reviewed_without_change": [int(card_id) for card_id in REVIEWED_IDS],
    "pending_c11": [],
    "updated_fields": len(UPDATES),
    "changed_cards": [int(card_id) for card_id in changed_cards],
    "field_updates": [{"id": int(card_id), "field": field, "before": old, "after": new} for card_id, field, old, new in UPDATES],
    "author_credit_before": 3559,
    "author_credit_addition": 12,
    "author_credit_after": 3571,
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
    "reviewed_ids": [int(card_id) for card_id in REVIEWED_IDS],
    "pending_c11_ids": [],
    "author_credit_before": 3559,
    "author_credit_after": 3571,
    "duplicate_keys": 0,
    "records_deleted": 0,
    "history_rewritten": False
}
(WORK / "prepare-results.json").write_text(json.dumps(prepare, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(WORK / "registry-results.json").write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

checkpoint_path = WORK / "checkpoint.json"
checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
checkpoint["status"] = "author review complete; deterministic candidate and register prepared; Chromium verification pending"
checkpoint["candidate_sha256"] = candidate_sha
checkpoint["candidate_bytes"] = OUT.stat().st_size
checkpoint["exact_rollback"] = True
checkpoint["register_mode"] = register_mode
checkpoint_path.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({"pass": True, "candidate_sha256": candidate_sha, "candidate_bytes": OUT.stat().st_size, "fixed_rechecked": FIXED_IDS, "reviewed_without_change": REVIEWED_IDS, "updated_fields": len(UPDATES), "register_after": after_all, "vocabulary_after": after_vocab}, ensure_ascii=False, indent=2))
