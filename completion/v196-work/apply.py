import csv, hashlib, json, re
from pathlib import Path

BASE = Path("JLPT_N1_ukrainian_reading_v195.html")
OUT = Path("JLPT_N1_ukrainian_reading_v196.html")
WORK = Path("completion/v196-work")
REGISTER = Path("completion/review-register.csv")
BASE_SHA = "b3a8a841cf573596b3e50eed3230e038833cbd5147a1fba4939fca80eb460ff3"

UPDATES = [
    ("943", "exampleTranslations[1]", "Менеджер із продажів узявся до переговорів, налаштований не втратити велику здобич.", "Менеджер із продажів розпочав переговори, налаштований не втратити велику здобич."),
    ("944", "exampleTranslations[1]", "У результаті розслідування я дійшов твердої переконаності, що було зловживання.", "У результаті розслідування я остаточно переконався, що мали місце зловживання."),
    ("949", "t", "наука і мистецтво", "ученість (академічні заняття) і мистецтво; культурно-освітня діяльність"),
    ("949", "usage", "Іменник: 学芸の振興、学芸に親しむ. Наука й мистецтво, культурно-освітня діяльність. 学芸員 — спеціальна назва фахівця музею; 学芸会 — шкільний захід із виступами. Значення складних слів не слід зводити до буквального перекладу двох кандзі.", "Іменник: 学芸の振興、学芸に親しむ. Академічні заняття, ученість і мистецтво. 学芸員 — музейний куратор, фахівець із музейних колекцій і виставок; 学芸会 — шкільний творчий захід. Значення складних слів не слід зводити до буквального перекладу двох кандзі."),
    ("949", "exampleTranslations[0]", "У музеї наукові співробітники займаються плануванням виставок і дослідженням матеріалів.", "Музейні куратори займаються підготовкою виставок і дослідженням музейних матеріалів."),
    ("949", "exampleTranslations[1]", "У цьому регіоні проводять заняття, спрямовані на розвиток науки й мистецтва.", "У цьому регіоні проводять курси, покликані сприяти розвитку освіти й мистецтва."),
    ("951", "exampleTranslations[0]", "За нинішніх обставин не можна оптимістично оцінювати перспективу завершення кризи.", "За нинішніх обставин не можна оптимістично оцінювати перспективу врегулювання ситуації."),
    ("952", "exampleTranslations[1]", "Самого виконання за нотами недостатньо, щоб надати вираженню глибини.", "Саме виконання за нотами ще не робить гру виразною й глибокою."),
    ("956", "t", "внутрішня боротьба суперечливих почуттів або бажань; також конфлікт між несумісними вимогами", "внутрішня боротьба суперечливих почуттів або бажань; також протистояння чи конфлікт між людьми або групами"),
    ("960", "t", "підрахунок суми чи розрахунок за покупку; також рахунок до оплати (お勘定 — рахунок у закладі)", "підрахунок кількості; розрахунок за покупку або рахунок до оплати (お勘定 — рахунок у закладі)"),
    ("961", "exampleTranslations[1]", "Хотілося б, щоб мене позбавили таких непосильних вимог.", "Прошу не висувати до мене таких непосильних вимог."),
    ("963", "usage", "Іменник; 物語が完結する、手続きが一か所で完結する. Завершитися як цілісне ціле або бути повністю виконаним у певних межах. 完了 більше акцентує виконання роботи; для останньої частини твору типове 完結編.", "Іменник; 物語が完結する、手続きが一か所で完結する. Завершитися повністю, утворивши завершений результат, або бути виконаним у межах однієї процедури. 完了 більше акцентує виконання роботи; для останньої частини твору типове 完結編."),
    ("963", "exampleTranslations[0]", "Серіальна публікація, що тривала десять років, нарешті завершилася.", "Твір, який публікували частинами протягом десяти років, нарешті завершився."),
    ("965", "exampleTranslations[0]", "Усі гостьові номери повністю оснащені сучасним обладнанням зв’язку.", "Усі гостьові номери повністю оснащені найновішим обладнанням зв’язку."),
    ("968", "exampleTranslations[0]", "На нараді керівництва визначили курс управління на наступний фінансовий рік.", "На нараді керівництва визначили основні напрями роботи компанії на наступний фінансовий рік."),
    ("969", "exampleTranslations[1]", "Відповідальний працівник сказав, що переговори справили на нього добре враження.", "Відповідальний працівник сказав, що під час переговорів отримав обнадійливий сигнал.")
]
EXPECTED = {
    "943": ("獲物", "えもの", ["名詞"]),
    "944": ("確信", "かくしん", ["名詞"]),
    "949": ("学芸", "がくげい", ["名詞"]),
    "951": ("楽観", "らっかん", ["名詞"]),
    "952": ("楽譜", "がくふ", ["名詞"]),
    "956": ("葛藤", "かっとう", ["名詞"]),
    "960": ("勘定", "かんじょう", ["名詞"]),
    "961": ("勘弁", "かんべん", ["名詞"]),
    "963": ("完結", "かんけつ", ["名詞"]),
    "965": ("完備", "かんび", ["名詞"]),
    "968": ("幹部", "かんぶ", ["名詞"]),
    "969": ("感触", "かんしょく", ["名詞"])
}
EXPECTED_EXAMPLES = {
    "943": ["猟師は、獲物を求めて山奥に分け入った。", "大きな獲物を逃すまいと、営業担当者は交渉に臨んだ。"],
    "944": ["彼は、計画が成功することを確信している。", "調査の結果、不正があったと確信するに至った。"],
    "949": ["博物館では、学芸員が展示の企画や資料の研究に携わっている。", "この地域では、学芸の振興を目的とした講座が開かれている。"],
    "951": ["現状では、事態の収束を楽観することはできない。", "楽観的な見通しだけでは、リスクへの備えが疎かになる。"],
    "952": ["彼は楽譜を見ながら、ピアノの練習に励んでいる。", "楽譜通りに演奏するだけでは、表現に深みが出ない。"],
    "956": ["彼は、会社への忠誠と家族への責任との間で葛藤した。", "世代間の価値観の違いが、組織内に葛藤を生んでいる。"],
    "960": ["レジで勘定を済ませてから、店を後にした。", "収支の勘定が合わないため、帳簿を再確認した。"],
    "961": ["今回のミスは勘弁してください。二度と繰り返しません。", "こんな無理な要求は、勘弁してもらいたい。"],
    "963": ["十年にわたる連載が、ついに完結を迎えた。", "一つの手続きで完結するよう、仕組みが簡素化された。"],
    "965": ["全客室に、最新の通信設備が完備されている。", "バリアフリー設備を完備した、公共施設が増えている。"],
    "968": ["幹部会議で、来年度の経営方針が決定された。", "若手の中から、将来の幹部候補を選抜する。"],
    "969": ["この布地は、柔らかな感触が好評を博している。", "交渉でよい感触を得たと、担当者は語った。"]
}
FIXED_IDS = ["943", "944", "949", "951", "952", "956", "960", "961", "963", "965", "968", "969"]
REVIEWED_IDS = []
PENDING_IDS = []
EXPECTED_CHANGED = FIXED_IDS
EVIDENCE = "completion/v196-acceptance.tsv; JLPT_N1_v196_audit.md"

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
    raise RuntimeError("unexpected v195 base SHA-256: " + base_sha)
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
    raise RuntimeError("protected inventory counts do not match v195")
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
    "943": {"exampleTranslations"},
    "944": {"exampleTranslations"},
    "949": {"t", "usage", "exampleTranslations"},
    "951": {"exampleTranslations"},
    "952": {"exampleTranslations"},
    "956": {"t"},
    "960": {"t"},
    "961": {"exampleTranslations"},
    "963": {"usage", "exampleTranslations"},
    "965": {"exampleTranslations"},
    "968": {"exampleTranslations"},
    "969": {"exampleTranslations"}
}
for card_id in details:
    for field in before[card_id]:
        if before[card_id][field] != details[card_id][field] and field not in allowed_fields.get(card_id, set()):
            raise RuntimeError("unexpected field mutation: " + card_id + "." + field)
    if before[card_id]["examples"] != details[card_id]["examples"]:
        raise RuntimeError("Japanese example changed: " + card_id)

literal = json.dumps(details, ensure_ascii=False, separators=(",", ":"))
candidate = base[:detail_start] + literal + base[detail_end:]
old_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v195</title>"
new_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v196</title>"
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
baseline_all = {"reviewed": 3907, "fixed_rechecked": 198, "pending": 1742, "total": 5847}
baseline_vocab = {"reviewed": 3338, "fixed_rechecked": 197, "pending": 379, "total": 3914}
target_all = {"reviewed": 3907, "fixed_rechecked": 210, "pending": 1730, "total": 5847}
target_vocab = {"reviewed": 3338, "fixed_rechecked": 209, "pending": 367, "total": 3914}
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
    raise RuntimeError("register state is neither v195 baseline nor expected v196 target")

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
    "base_version": "v195",
    "base_sha256": base_sha,
    "candidate_version": "v196",
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
    "author_credit_before": 3535,
    "author_credit_addition": 12,
    "author_credit_after": 3547,
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
    "author_credit_before": 3535,
    "author_credit_after": 3547,
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
