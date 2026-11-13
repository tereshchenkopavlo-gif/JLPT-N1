import csv, hashlib, json, re
from pathlib import Path

BASE = Path("JLPT_N1_ukrainian_reading_v196.html")
OUT = Path("JLPT_N1_ukrainian_reading_v197.html")
WORK = Path("completion/v197-work")
REGISTER = Path("completion/review-register.csv")
BASE_SHA = "0bef35afbc589b4b57312e40a56c87ba3512f504071070e820849529510c7fe5"

UPDATES = [
    ("973", "exampleTranslations[1]", "Відмінності в торговельних звичаях стають проблемою в міжнародних угодах.", "Відмінності в торговельних звичаях стають проблемою в міжнародній торгівлі."),
    ("974", "exampleTranslations[0]", "«Продавати олію» — ідіоматичний вислів зі значенням «марнувати час на балачки».", "Буквально — «продавати олію»; японський ідіоматичний вислів означає «марнувати час на балачки»."),
    ("978", "exampleTranslations[1]", "Радісні вигуки глядачів потужно підбадьорювали спортсменів.", "Радісні вигуки глядачів додавали спортсменам наснаги."),
    ("989", "exampleTranslations[1]", "Місця для глядачів на публічному записі програми були зайняті вже на ранньому етапі.", "Місця для глядачів на відкритому записі телепрограми швидко заповнилися."),
    ("991", "exampleTranslations[0]", "Від підприємств очікують, що вони повертатимуть отримані прибутки суспільству у вигляді користі.", "Очікується, що компанії повертатимуть суспільству частину отриманого прибутку.")
]
EXPECTED = {
    "973": ("慣習", "かんしゅう", ["名詞"]),
    "974": ("慣用", "かんよう", ["名詞"]),
    "978": ("歓声", "かんせい", ["名詞"]),
    "986": ("観賞", "かんしょう", ["名詞"]),
    "989": ("観覧", "かんらん", ["名詞"]),
    "990": ("貫禄", "かんろく", ["名詞"]),
    "991": ("還元", "かんげん", ["名詞"]),
    "993": ("間隔", "かんかく", ["名詞"]),
    "995": ("関税", "かんぜい", ["名詞"]),
    "1004": ("器材", "きざい", ["名詞"]),
    "1008": ("寄贈", "きぞう", ["名詞"]),
    "1013": ("棄権", "きけん", ["名詞"])
}
EXPECTED_EXAMPLES = {
    "973": ["地域の慣習に従って、祭りの準備が進められた。", "商慣習の違いが、国際取引における課題となっている。"],
    "974": ["「油を売る」は、無駄話をして時間を潰すという意味の慣用表現だ。", "この表現は、日常会話で広く慣用されている。"],
    "978": ["勝利の瞬間、スタジアムは大きな歓声に包まれた。", "観客の歓声が、選手たちの背中を力強く押した。"],
    "986": ["彼は休日に、庭の花を観賞するのを楽しみにしている。", "熱帯魚を観賞しながら、心の安らぎを得る人も多い。"],
    "989": ["展覧会の観覧には、事前の予約が必要となる。", "公開番組の観覧席は、早い段階で満席になった。"],
    "990": ["長年の経験を積んだ彼には、リーダーにふさわしい貫禄がある。", "新任の部長は、若いながらも貫禄を漂わせていた。"],
    "991": ["企業が得た利益を、社会に還元することが求められている。", "酸化した物質を還元する化学反応を、実験で確認した。"],
    "993": ["一定の間隔を空けて、座席を配置した。", "発車の間隔が短縮され、利用者の利便性が向上した。"],
    "995": ["政府は、輸入品に対する関税の引き上げを発表した。", "関税撤廃を巡り、両国の協議が続いている。"],
    "1004": ["実験に使う器材を、授業の前に点検した。", "老朽化した器材を更新するため、来年度の予算に費用を計上した。"],
    "1008": ["地元の企業が、市立図書館に本一千冊を寄贈することを決めた。", "遺族から寄贈された絵画は、美術館の常設展示に加えられた。"],
    "1013": ["足の負傷により、彼女は決勝戦を目前にして棄権することになった。", "彼は、どちらの案にも賛成できず、採決を棄権した。"]
}
FIXED_IDS = ["973", "974", "978", "989", "991"]
REVIEWED_IDS = ["986", "990", "993", "995", "1004", "1008", "1013"]
PENDING_IDS = []
EXPECTED_CHANGED = FIXED_IDS
EVIDENCE = "completion/v197-acceptance.tsv; JLPT_N1_v197_audit.md"

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
    raise RuntimeError("unexpected v196 base SHA-256: " + base_sha)
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
    raise RuntimeError("protected inventory counts do not match v196")
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
old_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v196</title>"
new_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v197</title>"
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
baseline_all = {"reviewed": 3907, "fixed_rechecked": 210, "pending": 1730, "total": 5847}
baseline_vocab = {"reviewed": 3338, "fixed_rechecked": 209, "pending": 367, "total": 3914}
target_all = {"reviewed": 3914, "fixed_rechecked": 215, "pending": 1718, "total": 5847}
target_vocab = {"reviewed": 3345, "fixed_rechecked": 214, "pending": 355, "total": 3914}
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
    raise RuntimeError("register state is neither v196 baseline nor expected v197 target")

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
    "base_version": "v196",
    "base_sha256": base_sha,
    "candidate_version": "v197",
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
    "author_credit_before": 3547,
    "author_credit_addition": 12,
    "author_credit_after": 3559,
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
    "author_credit_before": 3547,
    "author_credit_after": 3559,
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
