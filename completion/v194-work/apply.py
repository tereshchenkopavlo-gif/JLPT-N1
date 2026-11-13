import csv, hashlib, json, re
from pathlib import Path

BASE = Path("JLPT_N1_ukrainian_reading_v193.html")
OUT = Path("JLPT_N1_ukrainian_reading_v194.html")
WORK = Path("completion/v194-work")
REGISTER = Path("completion/review-register.csv")
BASE_SHA = "e5876cbc6e1799bf5aa8e4d4c6a07ee6cde1a14ffbdf5605cc1359d8623141c8"

UPDATES = [
    ("883", "exampleTranslations[1]", "Навіть сама кількість солі істотно змінює смак страви.", "Від того, скільки солі додати, смак страви може істотно змінитися."),
    ("884", "t", "додавання певного чинника до загальної оцінки чи рішення (事情を加味する — врахувати обставини)", "додавання смаку; перенесено — врахування додаткового чинника під час оцінки чи ухвалення рішення"),
    ("885", "exampleTranslations[1]", "До ухвалення законопроєкту, ймовірно, ще виникатимуть труднощі й повороти подій.", "Перш ніж законопроєкт ухвалять, імовірно, ще виникнуть складнощі й непередбачені повороти подій."),
    ("888", "exampleTranslations[1]", "Він кориться начальникові, наче слуга, й не намагається висловити власну думку.", "Він покірно слухається начальника, наче васал, і навіть не хоче висловлювати власної думки."),
    ("890", "m", "実際には存在しないが、想像で作り上げること。", "実際には存在しないものを想像によって作り上げること。また、そのように作られたもの。"),
    ("890", "t", "вигадка, уявне або фіктивне; 架空の — вигаданий, неіснуючий", "вигадування неіснуючого; вигадка, уявне або фіктивне; 架空の — вигаданий, неіснуючий"),
    ("893", "exampleTranslations[1]", "Пожежну сигналізацію регулярно перевіряють щороку.", "Пожежний сповіщувач перевіряють щороку."),
    ("894", "exampleTranslations[0]", "Новий завод планують запустити на повну потужність наступного місяця.", "Новий завод має повноцінно запрацювати наступного місяця."),
    ("900", "exampleTranslations[0]", "Надмірні запаси погіршили стан грошових потоків.", "Надмірні запаси ускладнили фінансування поточних витрат."),
    ("901", "t", "скорочення населення й занепад малонаселених районів (過疎化 — процес знелюднення)", "стан малонаселеної території, де через розріджене населення важко підтримувати звичне життя й послуги; 過疎化 — процес знелюднення"),
    ("905", "exampleTranslations[0]", "Він працює, водночас доглядаючи за літніми батьками.", "Він працює, водночас доглядаючи за своїм літнім батьком або матір’ю."),
    ("905", "exampleTranslations[1]", "Нестача працівників догляду виразно постала як проблема всього суспільства.", "Нестача фахівців із догляду виразно постала як проблема всього суспільства."),
    ("906", "exampleTranslations[0]", "Уряд обережно розглядає питання, чи здійснювати втручання у валютний ринок.", "Уряд ретельно зважує, чи втручатися у валютний ринок.")
]
POS_UPDATES = [("903", ["名詞"], ["代名詞"])]

EXPECTED = {
    "883": ("加減", "かげん", ["名詞"]),
    "884": ("加味", "かみ", ["名詞"]),
    "885": ("可決", "かけつ", ["名詞"]),
    "888": ("家来", "けらい", ["名詞"]),
    "890": ("架空", "かくう", ["名詞"]),
    "893": ("火災", "かさい", ["名詞"]),
    "894": ("稼働", "かどう", ["名詞"]),
    "900": ("過剰", "かじょう", ["名詞", "ナ形"]),
    "901": ("過疎", "かそ", ["名詞"]),
    "903": ("我々", "われわれ", ["代名詞"]),
    "905": ("介護", "かいご", ["名詞"]),
    "906": ("介入", "かいにゅう", ["名詞"])
}
EXPECTED_EXAMPLES = {
    "883": ["焦げないように、火の強さを加減してください。", "塩加減ひとつで、料理の味は大きく変わる。"],
    "884": ["今回は、現場の意見を加味して計画を修正した。", "各社の事情を加味した柔軟な契約条件が提示された。"],
    "885": ["予算案は、賛成多数で可決された。", "法案が可決されるまでには、なお曲折が予想される。"],
    "888": ["物語の中で、家来たちは主君を守るために戦った。", "彼は家来のように上司に従い、意見を述べようとしない。"],
    "890": ["この小説は、実在の事件に着想を得た架空の物語である。", "架空の請求書を作成して、会社の資金を横領した。"],
    "893": ["乾燥した季節には、火災の発生に特に注意が必要となる。", "火災報知機の点検が、毎年定期的に行われている。"],
    "894": ["新工場は、来月から本格的に稼働する予定だ。", "担当者は、設備の稼働状況を毎朝確認している。"],
    "900": ["過剰な在庫を抱えたことで、資金繰りが悪化した。", "過剰な期待が、かえって彼にとっての重圧となった。"],
    "901": ["過疎化が進む地方では、医療や交通の維持が大きな課題となっている。", "過疎地域の活性化に向けて、移住支援策が拡充された。"],
    "903": ["我々は、この問題を真摯に受け止め、再発防止に努める所存です。", "我々の使命は、顧客に最良のサービスを提供することにある。"],
    "905": ["彼は、高齢の親を介護しながら働いている。", "介護人材の不足が、社会全体の課題として顕在化している。"],
    "906": ["政府は、為替市場への介入を行うかどうかを慎重に検討している。", "第三者の介入によって、事態はかえって複雑化した。"]
}
FIXED_IDS = ["883", "884", "885", "888", "890", "893", "894", "900", "901", "903", "905", "906"]
REVIEWED_IDS = []
PENDING_IDS = []
EXPECTED_CHANGED = FIXED_IDS
EVIDENCE = "completion/v194-acceptance.tsv; JLPT_N1_v194_audit.md"

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
    raise RuntimeError("unexpected v193 base SHA-256: " + base_sha)
base = raw.decode("utf-8")

_, _, vocab = extract(base, "DEFAULT_VOCAB")
_, _, grammar = extract(base, "GRAMMAR_DETAILS_BY_ID")
detail_start, detail_end, details = extract(base, "VOCAB_DETAILS_BY_ID")
pos_start, pos_end, pos_map = extract(base, "VOCAB_POS_BY_ID")
_, _, pairs = extract(base, "VOCAB_AUDITED_PAIRS")
_, _, meaning = extract(base, "REVIEWED_MEANING_QUIZZES")
_, _, reading = extract(base, "REVIEWED_READING_OPTIONS")
_, _, kana_targets = extract(base, "VOCAB_KANA_EXAMPLE_TARGETS")
_, _, example_targets = extract(base, "REVIEWED_EXAMPLE_TARGETS")

if (len(vocab), len(grammar), len(details), len(pairs)) != (3914, 130, 3914, 859):
    raise RuntimeError("protected inventory counts do not match v193")
by_id = {str(item["id"]): item for item in vocab}
scope = list(EXPECTED)
for card_id, (word, reading_value, expected_pos) in EXPECTED.items():
    item = by_id.get(card_id)
    if item is None or (item["w"], item["r"]) != (word, reading_value):
        raise RuntimeError("identity/reading mismatch for " + card_id)
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

detail_changed_cards = {card_id for card_id in details if details[card_id] != before[card_id]}
if len(detail_changed_cards) != 11 or "903" in detail_changed_cards:
    raise RuntimeError("unexpected detail changed-card set: " + str(sorted(detail_changed_cards,key=int)))

pos_before = json.loads(json.dumps(pos_map, ensure_ascii=False))
for card_id, old_pos, new_pos in POS_UPDATES:
    if pos_map.get(card_id) != old_pos:
        raise RuntimeError("POS preimage mismatch for " + card_id)
    pos_map[card_id] = new_pos
pos_changed = {card_id for card_id in pos_map if pos_map[card_id] != pos_before[card_id]}
if pos_changed != {"903"}:
    raise RuntimeError("unexpected POS-map changed set: " + str(sorted(pos_changed,key=int)))
for card_id in pos_map:
    if card_id != "903" and pos_map[card_id] != pos_before[card_id]:
        raise RuntimeError("unexpected POS mutation: " + card_id)

allowed_fields = {
    "883": {"exampleTranslations"},
    "884": {"t"},
    "885": {"exampleTranslations"},
    "888": {"exampleTranslations"},
    "890": {"m", "t"},
    "893": {"exampleTranslations"},
    "894": {"exampleTranslations"},
    "900": {"exampleTranslations"},
    "901": {"t"},
    "903": set(),
    "905": {"exampleTranslations"},
    "906": {"exampleTranslations"}
}
for card_id in details:
    for field in before[card_id]:
        if before[card_id][field] != details[card_id][field] and field not in allowed_fields.get(card_id, set()):
            raise RuntimeError("unexpected field mutation: " + card_id + "." + field)
    if before[card_id]["examples"] != details[card_id]["examples"]:
        raise RuntimeError("Japanese example changed: " + card_id)

detail_literal = json.dumps(details, ensure_ascii=False, separators=(",", ":"))
pos_literal_old = base[pos_start:pos_end]
pos_literal_new = re.sub(r'"903"\s*:\s*\["名詞"\]', '"903":["代名詞"]', pos_literal_old, count=1)
if pos_literal_new == pos_literal_old:
    raise RuntimeError("raw POS-map replacement did not occur")
pos_after = json.loads(pos_literal_new)
if pos_after.get("903") != ["代名詞"] or any(pos_after[k] != pos_before[k] for k in pos_before if k != "903"):
    raise RuntimeError("POS-map verification failed")

replacements = [
    (detail_start, detail_end, detail_literal),
    (pos_start, pos_end, pos_literal_new)
]
candidate = base
for start, end, replacement in sorted(replacements, key=lambda x:x[0], reverse=True):
    candidate = candidate[:start] + replacement + candidate[end:]

old_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v193</title>"
new_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v194</title>"
if candidate.count(old_title) != 1:
    raise RuntimeError("version title marker mismatch")
candidate = candidate.replace(old_title, new_title, 1)

rollback = candidate.replace(new_title, old_title, 1)
rollback = rollback.replace(detail_literal, base[detail_start:detail_end], 1)
rollback = rollback.replace(pos_literal_new, pos_literal_old, 1)
if rollback != base:
    raise RuntimeError("exact rollback failed")

protected = {
    "DEFAULT_VOCAB": vocab,
    "GRAMMAR_DETAILS_BY_ID": grammar,
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
_, _, pos_candidate = extract(candidate, "VOCAB_POS_BY_ID")
if pos_candidate != pos_after:
    raise RuntimeError("candidate POS-map differs from expected map")
_, _, details_candidate = extract(candidate, "VOCAB_DETAILS_BY_ID")
if details_candidate != details:
    raise RuntimeError("candidate details differ from expected details")

OUT.write_bytes(candidate.encode("utf-8"))
candidate_sha = hashlib.sha256(OUT.read_bytes()).hexdigest()

register_rows = list(csv.DictReader(REGISTER.read_text(encoding="utf-8").splitlines()))
if len(register_rows) != 5847:
    raise RuntimeError("unexpected register row count: " + str(len(register_rows)))
baseline_all = {"reviewed": 3906, "fixed_rechecked": 175, "pending": 1766, "total": 5847}
baseline_vocab = {"reviewed": 3337, "fixed_rechecked": 174, "pending": 403, "total": 3914}
target_all = {"reviewed": 3906, "fixed_rechecked": 187, "pending": 1754, "total": 5847}
target_vocab = {"reviewed": 3337, "fixed_rechecked": 186, "pending": 391, "total": 3914}
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
    raise RuntimeError("register state is neither v193 baseline nor expected v194 target")

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
    "base_version": "v193",
    "base_sha256": base_sha,
    "candidate_version": "v194",
    "candidate_sha256": candidate_sha,
    "candidate_bytes": OUT.stat().st_size,
    "vocabulary_records": len(vocab),
    "grammar_records": len(grammar),
    "lexical_pairs": len(pairs),
    "unique_vocabulary_ids": len({int(item["id"]) for item in vocab}),
    "review_scope": [int(card_id) for card_id in scope],
    "fixed_rechecked": [int(card_id) for card_id in FIXED_IDS],
    "reviewed_without_change": [],
    "pending_c11": [],
    "updated_fields": len(UPDATES) + len(POS_UPDATES),
    "changed_cards": [int(card_id) for card_id in sorted(set(detail_changed_cards) | pos_changed, key=int)],
    "text_field_updates": [{"id": int(card_id), "field": field, "before": old, "after": new} for card_id, field, old, new in UPDATES],
    "pos_updates": [{"id": int(card_id), "before": old, "after": new} for card_id, old, new in POS_UPDATES],
    "author_credit_before": 3511,
    "author_credit_addition": 12,
    "author_credit_after": 3523,
    "protected_unchanged": {name: True for name in protected},
    "pos_map_only_id903_changed": True,
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
    "pending_c11_ids": [],
    "author_credit_before": 3511,
    "author_credit_after": 3523,
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

print(json.dumps({"pass": True, "candidate_sha256": candidate_sha, "candidate_bytes": OUT.stat().st_size, "fixed_rechecked": FIXED_IDS, "updated_fields": len(UPDATES)+len(POS_UPDATES), "register_after": after_all, "vocabulary_after": after_vocab}, ensure_ascii=False, indent=2))
