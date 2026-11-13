import csv, hashlib, json, re
from pathlib import Path

BASE = Path("JLPT_N1_ukrainian_reading_v191.html")
OUT = Path("JLPT_N1_ukrainian_reading_v192.html")
WORK = Path("completion/v192-work")
REGISTER = Path("completion/review-register.csv")
BASE_SHA = "3358191011496dbe19506879d850f767544e491dc9daa1017ca45cfd74659fe3"

UPDATES = [
    ("815", "exampleTranslations[0]", "Найбільша перевага цієї компанії — технологічна майстерність, що значно перевершує конкурентів.", "Найбільша перевага цієї компанії — технологічний рівень, що значно випереджає конкурентів."),
    ("818", "t", "політично або ідеологічно мотивоване таємне вбивство (暗殺する); не будь-який замах", "зазвичай політично або ідеологічно мотивоване таємне вбивство (暗殺する); не будь-який замах"),
    ("818", "exampleTranslations[1]", "Цей роман розповідає про події навколо вбивства одного політика.", "Цей роман розповідає про події навколо таємного вбивства одного політика."),
    ("819", "t", "усний рахунок без записування проміжних обчислень; рахування подумки", "обчислення подумки; рахунок у голові без записування проміжних дій"),
    ("822", "exampleTranslations[1]", "Проведення дослідження планують доручити незалежній установі.", "Проведення дослідження планують доручити сторонній організації."),
    ("825", "exampleTranslations[1]", "Усі учасники ще раз разом з’ясували важливість цієї діяльності.", "Усі учасники ще раз разом підтвердили значущість цієї діяльності."),
    ("828", "usage", "人事異動／部署を異動する — кадрове переміщення / перейти в інший підрозділ. Може охоплювати зміну посади без переїзду. 転勤 зазвичай означає зміну місця роботи або офісу в межах організації. 移動 — загальне переміщення, інше написання того самого いどう.", "人事異動／部署を異動する — кадрове переведення / перейти в інший підрозділ. Може охоплювати зміну посади без переїзду. 転勤 зазвичай означає зміну місця роботи або офісу. 移動 — загальне переміщення; 異動 — кадрова зміна в межах організації. Це різні слова з однаковим читанням, а не варіанти написання."),
    ("831", "exampleTranslations[0]", "В останній волі дідусь залишив слова вдячності родині.", "У заповіті дідусь висловив вдячність родині."),
    ("839", "exampleTranslations[0]", "Коли важливу справу довели до певного завершення, команда перепочила.", "Коли завершився черговий етап важливої справи, команда перепочила."),
    ("844", "m", "続いて起こる、一連なりの物事。", "互いに関連し、ひと続きとして捉えられる物事。"),
    ("844", "exampleTranslations[1]", "Усю пов’язану послідовність процедур планують перевести в електронну форму.", "Усі ці процедури планують перевести в електронну форму."),
    ("845", "exampleTranslations[1]", "Винятковий виріб, у який майстер вклав усю старанність, став головною принадою виставки.", "Винятковий виріб, який майстер виготовив із великою ретельністю, став головною принадою виставки."),
    ("855", "exampleTranslations[0]", "У бібліотеці доступ до перегляду цінних давніх документів обмежено.", "У бібліотеці обмежено перегляд цінних давніх документів."),
    ("856", "usage", "人に援助する／人を援助する／援助を受ける — допомагати / отримувати допомогу. Часто ресурси для того, хто має труднощі: 経済援助. 支援 ширше охоплює підтримку діяльності та самостійних зусиль; 救援 пов’язане з порятунком у скрутній чи надзвичайній ситуації.", "人を援助する／人に援助を行う／援助を受ける — допомагати людині / надавати людині допомогу / отримувати допомогу. Часто ресурси для того, хто має труднощі: 経済援助. 支援 ширше охоплює підтримку діяльності та самостійних зусиль; 救援 пов’язане з порятунком у скрутній чи надзвичайній ситуації.")
]

EXPECTED = {
    "815": ("圧倒", "あっとう", ["名詞"]),
    "818": ("暗殺", "あんさつ", ["名詞"]),
    "819": ("暗算", "あんざん", ["名詞"]),
    "822": ("委託", "いたく", ["名詞"]),
    "825": ("意義", "いぎ", ["名詞"]),
    "828": ("異動", "いどう", ["名詞"]),
    "831": ("遺言", "ゆいごん／いごん", ["名詞"]),
    "839": ("一息", "ひといき", ["名詞"]),
    "844": ("一連", "いちれん", ["名詞"]),
    "845": ("逸品", "いっぴん", ["名詞"]),
    "855": ("閲覧", "えつらん", ["名詞"]),
    "856": ("援助", "えんじょ", ["名詞"])
}
EXPECTED_EXAMPLES = {
    "815": ["競合他社を圧倒する技術力が、同社の最大の強みである。", "その壮大なスケールに、観客は圧倒された。"],
    "818": ["要人の暗殺未遂事件を受け、警備体制が大幅に強化された。", "この小説は、ある政治家の暗殺をめぐる物語だ。"],
    "819": ["彼は複雑な計算を、暗算であっという間にこなしてしまう。", "暗算が得意な生徒たちが、全国大会で腕を競った。"],
    "822": ["製造工程の一部を、外部の専門業者に委託している。", "調査の実施は、第三者機関に委託される予定だ。"],
    "825": ["今回の調査は、政策立案の観点から大きな意義を持つ。", "活動の意義を、改めて参加者全員で確認し合った。"],
    "828": ["四月の人事異動により、彼は営業部の課長に昇進した。", "人事異動に伴い、後任への引き継ぎが慌ただしく行われた。"],
    "831": ["祖父は遺言に、家族への感謝の言葉を残した。", "小説の主人公は、父の遺言を読み返した。"],
    "839": ["重要な案件が一段落し、チームは一息ついた。", "もう一息で完成するところまで、作業は進んでいる。"],
    "844": ["一連の不祥事を受け、経営陣は総辞職した。", "一連の手続きは、すべて電子化される予定だ。"],
    "845": ["この陶器は、名工の手による逸品として知られている。", "職人が丹精込めて作り上げた逸品が、展示会の目玉となった。"],
    "855": ["図書館では、貴重な古文書の閲覧が制限されている。", "資料の閲覧には、事前の申請が必要となる。"],
    "856": ["被災国に対して、人道的な援助が行われた。", "その団体は、学生への経済的な援助を続けている。"]
}

FIXED_IDS = ["815", "818", "819", "822", "825", "828", "831", "839", "844", "845", "855", "856"]
REVIEWED_IDS = []
PENDING_IDS = []
EXPECTED_CHANGED = FIXED_IDS
EVIDENCE = "completion/v192-acceptance.tsv; JLPT_N1_v192_audit.md"

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
    raise RuntimeError("unexpected v191 base SHA-256: " + base_sha)
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
    raise RuntimeError("protected inventory counts do not match v191")
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
    "815": {"exampleTranslations"},
    "818": {"t", "exampleTranslations"},
    "819": {"t"},
    "822": {"exampleTranslations"},
    "825": {"exampleTranslations"},
    "828": {"usage"},
    "831": {"exampleTranslations"},
    "839": {"exampleTranslations"},
    "844": {"m", "exampleTranslations"},
    "845": {"exampleTranslations"},
    "855": {"exampleTranslations"},
    "856": {"usage"}
}
for card_id in details:
    for field in before[card_id]:
        if before[card_id][field] != details[card_id][field] and field not in allowed_fields.get(card_id, set()):
            raise RuntimeError("unexpected field mutation: " + card_id + "." + field)
    if before[card_id]["examples"] != details[card_id]["examples"]:
        raise RuntimeError("Japanese example changed: " + card_id)

literal = json.dumps(details, ensure_ascii=False, separators=(",", ":"))
candidate = base[:detail_start] + literal + base[detail_end:]
old_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v191</title>"
new_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v192</title>"
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
baseline_all = {"reviewed": 3906, "fixed_rechecked": 151, "pending": 1790, "total": 5847}
baseline_vocab = {"reviewed": 3337, "fixed_rechecked": 150, "pending": 427, "total": 3914}
target_all = {"reviewed": 3906, "fixed_rechecked": 163, "pending": 1778, "total": 5847}
target_vocab = {"reviewed": 3337, "fixed_rechecked": 162, "pending": 415, "total": 3914}
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
    raise RuntimeError("register state is neither v191 baseline nor expected v192 target")

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
    "base_version": "v191",
    "base_sha256": base_sha,
    "candidate_version": "v192",
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
    "updated_fields": len(UPDATES),
    "changed_cards": [int(card_id) for card_id in changed_cards],
    "field_updates": [{"id": int(card_id), "field": field, "before": old, "after": new} for card_id, field, old, new in UPDATES],
    "author_credit_before": 3487,
    "author_credit_addition": 12,
    "author_credit_after": 3499,
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
    "pending_c11_ids": [],
    "author_credit_before": 3487,
    "author_credit_after": 3499,
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

print(json.dumps({"pass": True, "candidate_sha256": candidate_sha, "candidate_bytes": OUT.stat().st_size, "fixed_rechecked": FIXED_IDS, "updated_fields": len(UPDATES), "register_after": after_all, "vocabulary_after": after_vocab}, ensure_ascii=False, indent=2))
