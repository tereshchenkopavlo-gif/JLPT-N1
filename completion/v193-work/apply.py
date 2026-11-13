import csv, hashlib, json, re
from pathlib import Path

BASE = Path("JLPT_N1_ukrainian_reading_v192.html")
OUT = Path("JLPT_N1_ukrainian_reading_v193.html")
WORK = Path("completion/v193-work")
REGISTER = Path("completion/review-register.csv")
BASE_SHA = "ebd6dfe16edb7367349a299e445797fd7309c0098855b07b46bf6fb4b1f1c54a"

UPDATES = [
    ("857", "m", "海・湖・川などに沿った陸地。", "海・湖・川などの岸に沿って広がる地域。"),
    ("857", "t", "узбережжя, берег", "прибережна смуга, узбережжя; територія вздовж моря, озера чи річки"),
    ("858", "t", "територія вздовж залізничної або транспортної лінії; населені пункти біля маршруту", "територія вздовж залізниці або дороги; населені пункти біля маршруту"),
    ("858", "exampleTranslations[1]", "Мешканці вздовж лінії висунули вимоги щодо заходів проти шуму.", "Мешканці вздовж залізниці попросили вжити заходів для зменшення шуму."),
    ("860", "t", "прикмета щодо удачі; також переказ про походження храму чи святині (縁起)", "прикмета, що віщує добро чи лихо; переказ про походження храму або святині; у буддизмі — залежне виникнення"),
    ("860", "exampleTranslations[0]", "Зважаючи на добрі прикмети, для відкриття обрали день 大安, який вважають сприятливим.", "З огляду на прикмети, для відкриття обрали день 大安, який вважають сприятливим."),
    ("862", "exampleTranslations[0]", "За посередництва ділового партнера йому запропонували можливий шлюб.", "Через рекомендацію ділового партнера йому надійшла пропозиція одружитися."),
    ("863", "exampleTranslations[0]", "Створюють систему, за якою фаховий лікар на відстані допомагає під час лікування.", "Налагоджено систему, за якою фаховий лікар дистанційно підтримує надання медичної допомоги."),
    ("865", "exampleTranslations[0]", "Викриття корупційної справи політика викликало різку суспільну критику.", "Після викриття корупції за участю політика в суспільстві лунає різка критика."),
    ("867", "exampleTranslations[0]", "У жвавому торговельному районі з великим потоком людей слід остерігатися вуличних грабіжників.", "У жвавому торговельному районі з великим потоком людей слід остерігатися крадіїв, які вихоплюють речі у перехожих."),
    ("872", "m", "金。黄色に輝く金属。最も価値あるもの。", "金。また、黄金色に輝くもの。最も価値あるもののたとえ。"),
    ("872", "usage", "黄金（おうごん／こがね）— золото, золотавий колір; こがね часто літературніше. 黄金時代（おうごんじだい）— період розквіту. 黄金に輝く — сяяти золотом. Вибір читання залежить від сполуки; не підставляйте こがね в кожне складене слово.", "У прикладі 黄金に彩られた寺院 — читання おうごん; у прикладі 黄金に輝いていた — こがね (літературний образ золотавого кольору). 黄金時代 — おうごんじだい, «золотий вік». Читання залежить від усталеного сполучення й контексту; не підставляйте こがね механічно в кожну сполуку."),
    ("873", "t", "велика садиба з будинком і прилеглою територією; особняк із земельною ділянкою", "садиба; земельна ділянка при будинку; великий будинок із прилеглою територією"),
    ("874", "exampleTranslations[1]", "Оповідь змальовує чистосерду дівчину, якою розпоряджаються примхи долі.", "Оповідь змальовує чистосерду дівчину, яка стала іграшкою долі."),
    ("878", "t", "прихований, нерідко корисливий намір за зовні доброзичливою поведінкою (下心がある)", "прихований, часто корисливий намір; потаємний мотив (下心がある)"),
    ("878", "usage", "下心がある／下心を隠す — мати / приховувати потаємний, часто корисливий намір. Нерідко про прихований романтичний або сексуальний інтерес. Не кожен невисловлений задум негативний: нейтральне 意図 не завжди доречно замінювати оцінним 下心.", "下心がある／下心を隠す — мати / приховувати потаємний, часто корисливий намір. Іноді про прихований особистий або романтичний інтерес; це не обов’язково пов’язано із зовні доброзичливою поведінкою. Нейтральне 意図 не завжди доречно замінювати оцінним 下心."),
    ("880", "exampleTranslations[1]", "Перед фарбуванням потрібно ретельно обробити основу поверхні стіни.", "Перед фарбуванням потрібно ретельно підготувати поверхню стіни.")
]

EXPECTED = {
    "857": ("沿岸", "えんがん", ["名詞"]),
    "858": ("沿線", "えんせん", ["名詞"]),
    "860": ("縁起", "えんぎ", ["名詞"]),
    "862": ("縁談", "えんだん", ["名詞"]),
    "863": ("遠隔", "えんかく", ["名詞"]),
    "865": ("汚職", "おしょく", ["名詞"]),
    "867": ("往来", "おうらい", ["名詞"]),
    "872": ("黄金", "おうごん／こがね", ["名詞"]),
    "873": ("屋敷", "やしき", ["名詞"]),
    "874": ("乙女", "おとめ", ["名詞"]),
    "878": ("下心", "したごころ", ["名詞"]),
    "880": ("下地", "したじ", ["名詞"])
}
EXPECTED_EXAMPLES = {
    "857": ["台風の接近に伴い、沿岸部では高波への警戒が呼びかけられている。", "調査船は沿岸をゆっくり進み、水質を調べた。"],
    "858": ["鉄道の沿線では、新たな住宅開発が進められている。", "沿線の住民から、騒音対策を求める声が上がった。"],
    "860": ["縁起を担いで、開店の日取りを大安の日に決めた。", "縁起でもないことを口にするものではない。"],
    "862": ["彼には、取引先の紹介で縁談が持ち込まれた。", "縁談が整い、秋には式を挙げる予定だ。"],
    "863": ["遠隔地にいる専門医が、診療を支援する仕組みが整えられている。", "遠隔操作により、危険な現場での作業が可能になった。"],
    "865": ["政治家の汚職事件が発覚し、世論の厳しい批判が集まっている。", "汚職を根絶するため、制度の見直しが急務となっている。"],
    "867": ["人の往来が多い繁華街では、ひったくりに注意が必要だ。", "国境を越えた往来が再開され、観光業は活気を取り戻した。"],
    "872": ["この国は、黄金に彩られた寺院で世界的に知られている。", "夕日を浴びた草原が、黄金に輝いていた。"],
    "873": ["江戸時代の武家屋敷が、観光名所として保存されている。", "広大な屋敷には、手入れの行き届いた庭園が広がっている。"],
    "874": ["舞台には、花を手にした乙女が現れた。", "物語は、純真な乙女が運命に翻弄される姿を描いている。"],
    "878": ["彼の親切な申し出には、何か下心があるように感じられた。", "下心を見透かされ、交渉は暗礁に乗り上げた。"],
    "880": ["長年の地道な活動が、今回の成功の下地となった。", "塗装の前に、壁面の下地を丁寧に処理する必要がある。"]
}

FIXED_IDS = ["857", "858", "860", "862", "863", "865", "867", "872", "873", "874", "878", "880"]
REVIEWED_IDS = []
PENDING_IDS = []
EXPECTED_CHANGED = FIXED_IDS
EVIDENCE = "completion/v193-acceptance.tsv; JLPT_N1_v193_audit.md"

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
    raise RuntimeError("unexpected v192 base SHA-256: " + base_sha)
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
    raise RuntimeError("protected inventory counts do not match v192")
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
    "857": {"m", "t"},
    "858": {"t", "exampleTranslations"},
    "860": {"t", "exampleTranslations"},
    "862": {"exampleTranslations"},
    "863": {"exampleTranslations"},
    "865": {"exampleTranslations"},
    "867": {"exampleTranslations"},
    "872": {"m", "usage"},
    "873": {"t"},
    "874": {"exampleTranslations"},
    "878": {"t", "usage"},
    "880": {"exampleTranslations"}
}
for card_id in details:
    for field in before[card_id]:
        if before[card_id][field] != details[card_id][field] and field not in allowed_fields.get(card_id, set()):
            raise RuntimeError("unexpected field mutation: " + card_id + "." + field)
    if before[card_id]["examples"] != details[card_id]["examples"]:
        raise RuntimeError("Japanese example changed: " + card_id)

literal = json.dumps(details, ensure_ascii=False, separators=(",", ":"))
candidate = base[:detail_start] + literal + base[detail_end:]
old_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v192</title>"
new_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v193</title>"
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
baseline_all = {"reviewed": 3906, "fixed_rechecked": 163, "pending": 1778, "total": 5847}
baseline_vocab = {"reviewed": 3337, "fixed_rechecked": 162, "pending": 415, "total": 3914}
target_all = {"reviewed": 3906, "fixed_rechecked": 175, "pending": 1766, "total": 5847}
target_vocab = {"reviewed": 3337, "fixed_rechecked": 174, "pending": 403, "total": 3914}
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
    raise RuntimeError("register state is neither v192 baseline nor expected v193 target")

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
    "base_version": "v192",
    "base_sha256": base_sha,
    "candidate_version": "v193",
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
    "author_credit_before": 3499,
    "author_credit_addition": 12,
    "author_credit_after": 3511,
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
    "author_credit_before": 3499,
    "author_credit_after": 3511,
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
