import csv, hashlib, json, re
from pathlib import Path

BASE = Path("JLPT_N1_ukrainian_reading_v189.html")
OUT = Path("JLPT_N1_ukrainian_reading_v190.html")
WORK = Path("completion/v190-work")
REGISTER = Path("completion/review-register.csv")
BASE_SHA = "868b1e37c671a0ecd74c5dea2168d50c3b994e66ef912912b90ea5b426aac4ba"

UPDATES = [
    ("759", "exampleTranslations[1]", "Давні документи, що довго лежали в коморі, виявилися цінними історичними джерелами.", "У коморі знайшли давні документи, що виявилися цінними історичними джерелами."),
    ("761", "m", "二つで一組になっているもの。向かい合うもの。", "二つで一組になっているもの。向かい合うもの。また、二つの数の比率を表す語。"),
    ("763", "t", "край або кінчик предмета; початок чи кінець події (у сталих висловах)", "край або кінчик предмета; початок, витік (у 端を発する)"),
    ("766", "exampleTranslations[0]", "Я вирішив спробувати розвивати бізнес за кордоном, налаштувавшись відкрити нові двері.", "Зважившись відкрити нові можливості, я вирішив узятися за бізнес за кордоном."),
    ("771", "t", "морська вода; приплив і відплив; у 潮時 — слушний момент", "морська вода; приплив і відплив, течія; у 潮時 — слушний момент"),
    ("771", "exampleTranslations[1]", "Визначивши слушний момент, він вирішив вийти з бізнесу.", "Визначивши слушний момент, він вирішив відмовитися від цього бізнес-напряму."),
    ("772", "t", "голос (бюлетень), бюлетень; талон", "голос (одиниця підрахунку); бюлетень для голосування; талон або квиток (у відповідних сполуках)"),
    ("774", "exampleTranslations[0]", "Навесні фермери висаджують розсаду рису на залитих полях.", "Навесні фермери висаджують розсаду рису на рисових полях."),
    ("775", "exampleTranslations[1]", "Прагнучи світової вершини, спортсмени невтомно тренуються день у день.", "Прагнучи світової вершини, спортсмени тренуються вдень і вночі."),
    ("779", "m", "家の屋根の最も高い部分。建物を数える語。", "家の屋根の最も高い部分。また、建物の棟や、建物を数える語。"),
    ("780", "m", "器具の、手で握る部分。模様。人柄・品格。", "器具の、手で握る部分。模様。また、人の体格や人柄・品格。"),
    ("783", "usage", "Тут 頭（あたま）— голова, розум: 頭が切れる — швидко й точно міркувати; 頭を冷やす — заспокоїтися. 頭（かしら）може означати ватажка, 頭（とう）є лічильником тварин. Це інші читання й моделі, не варіанти читання двох наведених прикладів.", "Тут 頭（あたま）— голова, розум: 頭が切れる — швидко й точно міркувати; 頭を冷やす — заспокоїтися. 頭（あたま）に立つ — стояти на чолі, очолювати групу; 頭（かしら）може означати ватажка; 頭（とう）є лічильником тварин. Це різні читання й моделі, не варіанти читання двох наведених прикладів."),
    ("785", "m", "繊維をとる植物。麻で作られた布。", "アサ・カラムシ・アマなど、繊維をとる植物。また、その繊維や織物。"),
    ("785", "exampleTranslations[0]", "Улітку віддають перевагу добре повітропроникним сорочкам із тканини 麻 (льон, рамі тощо).", "Улітку віддають перевагу добре повітропроникним сорочкам із тканини з рослинних волокон."),
    ("785", "exampleTranslations[1]", "Волокнисті рослини, що називаються 麻, здавна використовували як сировину для одягу та мотузок。", "Волокнисті рослини цієї групи здавна використовували для виготовлення одягу й мотузок.")
]

EXPECTED = {
    "759": ("蔵", "くら", ["名詞"]),
    "761": ("対", "つい／たい", ["名詞"]),
    "763": ("端", "はし／はた／たん", ["名詞"]),
    "766": ("扉", "とびら", ["名詞"]),
    "771": ("潮", "しお", ["名詞"]),
    "772": ("票", "ひょう", ["名詞"]),
    "774": ("苗", "なえ", ["名詞"]),
    "775": ("頂", "いただき", ["名詞"]),
    "779": ("棟", "むね／とう", ["名詞"]),
    "780": ("柄", "え／がら", ["名詞"]),
    "783": ("頭", "あたま", ["名詞"]),
    "785": ("麻", "あさ", ["名詞"])
}
EXPECTED_EXAMPLES = {
    "759": ["古い蔵を改修して、小さな展示室にした。", "蔵に眠っていた古文書が、貴重な史料として発見された。"],
    "761": ["この二つの花瓶は対になっている。", "試合は三対二で終わった。"],
    "763": ["町の端にある工場が、地域の雇用を支えている。", "机の端に置いた資料が、誤って床に落ちてしまった。"],
    "766": ["新たな扉を開く覚悟で、海外事業への挑戦を決めた。", "重い鉄の扉が、ゆっくりと開いた。"],
    "771": ["潮の満ち引きを利用して、小さな漁船が港を出入りしている。", "潮時を見極めて、事業から撤退する判断を下した。"],
    "772": ["選挙の結果、与党が過半数の票を獲得した。", "わずか数票の差で、法案が可決された。"],
    "774": ["春になると、農家は田んぼに稲の苗を植える。", "ベランダで野菜の苗を育てている。"],
    "775": ["彼らは、数日がかりでついに山の頂に到達した。", "世界の頂を目指して、選手たちは日夜鍛錬を重ねている。"],
    "779": ["屋根の棟を修理するため、職人が足場を組んだ。", "新たに三棟のマンションが完成する予定だ。"],
    "780": ["このナイフは、柄が握りやすいように工夫されている。", "彼は柄にもなく、会議で終始おとなしくしていた。"],
    "783": ["彼は頭が切れ、状況を的確に把握する能力に優れている。", "頭を冷やして、冷静に対応を検討することが肝要だ。"],
    "785": ["夏には、風通しのよい麻のシャツが好まれる。", "古くから、麻は衣料や縄の原料として利用されてきた。"]
}

FIXED_IDS = ["759", "761", "763", "766", "771", "772", "774", "775", "779", "780", "783", "785"]
REVIEWED_IDS = []
PENDING_IDS = []
EXPECTED_CHANGED = FIXED_IDS
EVIDENCE = "completion/v190-acceptance.tsv; JLPT_N1_v190_audit.md"

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
    raise RuntimeError("unexpected v189 base SHA-256: " + base_sha)
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
    raise RuntimeError("protected inventory counts do not match v189")
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
    "759": {"exampleTranslations"},
    "761": {"m"},
    "763": {"t"},
    "766": {"exampleTranslations"},
    "771": {"t", "exampleTranslations"},
    "772": {"t"},
    "774": {"exampleTranslations"},
    "775": {"exampleTranslations"},
    "779": {"m"},
    "780": {"m"},
    "783": {"usage"},
    "785": {"m", "exampleTranslations"}
}
for card_id in details:
    for field in before[card_id]:
        if before[card_id][field] != details[card_id][field] and field not in allowed_fields.get(card_id, set()):
            raise RuntimeError("unexpected field mutation: " + card_id + "." + field)
    if before[card_id]["examples"] != details[card_id]["examples"]:
        raise RuntimeError("Japanese example changed: " + card_id)

literal = json.dumps(details, ensure_ascii=False, separators=(",", ":"))
candidate = base[:detail_start] + literal + base[detail_end:]
old_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v189</title>"
new_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v190</title>"
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
baseline_all = {"reviewed": 3906, "fixed_rechecked": 127, "pending": 1814, "total": 5847}
baseline_vocab = {"reviewed": 3337, "fixed_rechecked": 126, "pending": 451, "total": 3914}
target_all = {"reviewed": 3906, "fixed_rechecked": 139, "pending": 1802, "total": 5847}
target_vocab = {"reviewed": 3337, "fixed_rechecked": 138, "pending": 439, "total": 3914}
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
    raise RuntimeError("register state is neither v189 baseline nor expected v190 target")

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
    "base_version": "v189",
    "base_sha256": base_sha,
    "candidate_version": "v190",
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
    "author_credit_before": 3463,
    "author_credit_addition": 12,
    "author_credit_after": 3475,
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
    "author_credit_before": 3463,
    "author_credit_after": 3475,
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
