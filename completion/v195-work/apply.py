import csv, hashlib, json, re
from pathlib import Path

BASE = Path("JLPT_N1_ukrainian_reading_v194.html")
OUT = Path("JLPT_N1_ukrainian_reading_v195.html")
WORK = Path("completion/v195-work")
REGISTER = Path("completion/review-register.csv")
BASE_SHA = "0933cf494010d2c4a8ff3f200d35882d3773f59395193b68ea48604b8a8bfba9"

UPDATES = [
    ("914", "t", "перебудова існуючої будівлі зі зміною її конструкції або планування (改築する)", "перебудова всієї будівлі або її частини (改築する)"),
    ("915", "exampleTranslations[0]", "У зв’язку з переглядом підручника переглянули й матеріали, які використовують на заняттях.", "Після оновлення підручника переглянули й навчальні матеріали."),
    ("920", "t", "організація та проведення заходу, конференції чи змагання (開催する — проводити захід)", "проведення заходу, конференції чи змагання (開催する — проводити захід)"),
    ("922", "t", "відкриття театрального сезону, фестивалю або турніру (開幕する — розпочатися)", "відкриття вистави, фестивалю чи турніру; переносно — початок нової епохи (開幕する — розпочатися)"),
    ("927", "exampleTranslations[1]", "Важливе значення надають оцінюванню не лише зовнішнього вигляду виробу, а й його функціональності.", "Важливо оцінювати не лише зовнішній вигляд виробу, а й його функціональність."),
    ("928", "exampleTranslations[1]", "Ночівля поза домом без дозволу стала причиною сімейного конфлікту.", "Ночівля поза домом без попередження стала причиною сімейного конфлікту."),
    ("932", "exampleTranslations[0]", "Від відповідального працівника отримали пояснення основного змісту проєкту.", "Відповідальний працівник розповів про основні положення проєкту."),
    ("933", "usage", "Іменник: 概略を示す、概略を述べる. Загальний виклад без деталей; інколи також приблизно: 概略をつかむ — уловити загальну картину. З 概要 часто взаємозамінне; не слід вигадувати обов’язковий різний обсяг чи порядок двох описів.", "Іменник: 概略を示す、概略を述べる. Загальний виклад без деталей: 概略をつかむ — схопити загальну картину; 概略を述べる — викласти загальний зміст. З 概要 часто взаємозамінне; не слід вигадувати обов’язковий різний обсяг чи порядок двох описів."),
    ("934", "exampleTranslations[0]", "Кав’ярня на розі була заповнена службовцями, які поверталися з роботи.", "Кав’ярня на розі була переповнена працівниками компаній, які поверталися з роботи."),
    ("936", "exampleTranslations[1]", "Під дію цього заходу підпадають лише підприємці, які відповідають певним критеріям.", "Під дію цього заходу підпадають лише суб’єкти господарювання, які відповідають певним критеріям."),
    ("941", "m", "互いに組み合って戦うこと。困難な問題と取り組むこと。", "互いに組み合って戦うこと。また、困難な問題に取り組み、解決しようと苦労すること。")
]

EXPECTED = {
    "911": ("怪獣", "かいじゅう", ["名詞"]),
    "914": ("改築", "かいちく", ["名詞"]),
    "915": ("改訂", "かいてい", ["名詞"]),
    "920": ("開催", "かいさい", ["名詞"]),
    "922": ("開幕", "かいまく", ["名詞"]),
    "927": ("外観", "がいかん", ["名詞"]),
    "928": ("外泊", "がいはく", ["名詞"]),
    "932": ("概要", "がいよう", ["名詞"]),
    "933": ("概略", "がいりゃく", ["名詞"]),
    "934": ("街角", "まちかど", ["名詞"]),
    "936": ("該当", "がいとう", ["名詞"]),
    "941": ("格闘", "かくとう", ["名詞"])
}
EXPECTED_EXAMPLES = {
    "911": ["子供たちは、怪獣の登場する映画に夢中になった。", "伝説の怪獣の正体を探る調査が、話題を呼んでいる。"],
    "914": ["老朽化した校舎を、全面的に改築することが決まった。", "古い住宅を改築して、現代的な生活様式に合わせた。"],
    "915": ["教科書の改訂に伴い、授業で使う資料も見直した。", "辞書は、新語を加えるために定期的に改訂される。"],
    "920": ["国際会議が東京で開催されることが決定した。", "悪天候のため、予定していたイベントの開催が延期された。"],
    "922": ["映画祭が開幕し、初日から多くの観客が会場を訪れた。", "新しい時代の開幕を告げる、画期的な発表だった。"],
    "927": ["建物の外観は、周囲の景観と調和するよう設計された。", "製品の外観だけでなく、機能面の評価も重視される。"],
    "928": ["寮では、外泊する際に事前の届出が必要とされている。", "無断で外泊したことが、家族の間で問題となった。"],
    "932": ["事業の概要について、担当者から説明を受けた。", "まず、調査の概要を簡潔に報告します。"],
    "933": ["計画の概略を示した資料が、関係者に配布された。", "今日は時間がないので、概略だけをお話しします。"],
    "934": ["街角のカフェは、仕事帰りの会社員でにぎわっていた。", "街角で配られたチラシが、イベントの宣伝に一役買った。"],
    "936": ["条件に該当する項目に、印を付けてください。", "この措置の対象に該当するのは、一定の基準を満たす事業者に限られる。"],
    "941": ["技術者たちは、不具合の解消に向けて、数か月間も格闘した。", "格闘技の試合会場は、熱気に包まれていた。"]
}
FIXED_IDS = ["914", "915", "920", "922", "927", "928", "932", "933", "934", "936", "941"]
REVIEWED_IDS = ["911"]
PENDING_IDS = []
EXPECTED_CHANGED = FIXED_IDS
EVIDENCE = "completion/v195-acceptance.tsv; JLPT_N1_v195_audit.md"

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
    raise RuntimeError("unexpected v194 base SHA-256: " + base_sha)
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
    raise RuntimeError("protected inventory counts do not match v194")
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
    "914": {"t"},
    "915": {"exampleTranslations"},
    "920": {"t"},
    "922": {"t"},
    "927": {"exampleTranslations"},
    "928": {"exampleTranslations"},
    "932": {"exampleTranslations"},
    "933": {"usage"},
    "934": {"exampleTranslations"},
    "936": {"exampleTranslations"},
    "941": {"m"}
}
for card_id in details:
    for field in before[card_id]:
        if before[card_id][field] != details[card_id][field] and field not in allowed_fields.get(card_id, set()):
            raise RuntimeError("unexpected field mutation: " + card_id + "." + field)
    if before[card_id]["examples"] != details[card_id]["examples"]:
        raise RuntimeError("Japanese example changed: " + card_id)

literal = json.dumps(details, ensure_ascii=False, separators=(",", ":"))
candidate = base[:detail_start] + literal + base[detail_end:]
old_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v194</title>"
new_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v195</title>"
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
baseline_all = {"reviewed": 3906, "fixed_rechecked": 187, "pending": 1754, "total": 5847}
baseline_vocab = {"reviewed": 3337, "fixed_rechecked": 186, "pending": 391, "total": 3914}
target_all = {"reviewed": 3907, "fixed_rechecked": 198, "pending": 1742, "total": 5847}
target_vocab = {"reviewed": 3338, "fixed_rechecked": 197, "pending": 379, "total": 3914}
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
    raise RuntimeError("register state is neither v194 baseline nor expected v195 target")

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
    "base_version": "v194",
    "base_sha256": base_sha,
    "candidate_version": "v195",
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
    "author_credit_before": 3523,
    "author_credit_addition": 12,
    "author_credit_after": 3535,
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
    "author_credit_before": 3523,
    "author_credit_after": 3535,
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
