import csv, hashlib, json, re
from pathlib import Path

BASE = Path("JLPT_N1_ukrainian_reading_v190.html")
OUT = Path("JLPT_N1_ukrainian_reading_v191.html")
WORK = Path("completion/v191-work")
REGISTER = Path("completion/review-register.csv")
BASE_SHA = "6e44e0c4de3a89e2c1ad91bfab697910e88fa343f862648f310f963a8f862728"

UPDATES = [
    ("788", "exampleTranslations[1]", "Судячи з реакції іншої сторони, ця ділова пропозиція ще має шанси на успіх.", "Судячи з реакції іншої сторони, ці переговори ще мають шанси на успіх."),
    ("789", "m", "娘の結婚相手。", "娘の結婚相手。また、結婚式での新郎。"),
    ("789", "t", "зять, наречений", "чоловік дочки (зять); наречений (у весільному контексті)"),
    ("790", "exampleTranslations[0]", "Рибалки з раннього ранку тягнуть сітки, ловлячи рибу.", "Рибалки від світанку тягнуть сітки, ловлячи рибу."),
    ("790", "exampleTranslations[1]", "Поліція розгорнула в різних місцях мережу розшуку й намагається встановити місцеперебування підозрюваного.", "Поліція розгорнула пошукові заходи в різних місцях і відстежує пересування підозрюваного."),
    ("793", "exampleTranslations[1]", "Отримавши крила у вигляді нової технології, компанія зробила великий злет.", "Завдяки новій технології компанія ніби отримала крила й стрімко злетіла."),
    ("794", "t", "голий, оголений", "нагота, оголеність; 裸の — голий, оголений"),
    ("797", "exampleTranslations[1]", "Як завжди, нарада значно перевищила заплановану тривалість.", "Як завжди, нарада закінчилася значно пізніше, ніж планували."),
    ("801", "m", "体の側面。中心から外れた所。", "体の側面、特に腕の付け根の下の部分。中心から外れた所。"),
    ("803", "exampleTranslations[1]", "На церемонії вступу нові військовослужбовці складали присягу з урочистими обличчями.", "Під час церемонії вступу на службу новобранці урочисто й зосереджено склали присягу."),
    ("805", "exampleTranslations[1]", "Щоб оцінка не була однобічно суб’єктивною, перевірку проводять кілька відповідальних працівників.", "Щоб оцінка не залежала надмірно від особистих поглядів, перевірку проводять кілька відповідальних працівників."),
    ("808", "m", "人から好かれる、にこやかな様子。", "人から好かれる、にこやかさやかわいらしさのある様子。"),
    ("809", "s[0]", "愛敬", "愛嬌／愛敬"),
    ("809", "usage", "Читання あいそ та あいそう. 愛想がいい／悪い — привітний / непривітний; 愛想を尽かす — остаточно розчаруватися в комусь. 愛想笑い — ввічлива, іноді нещира усмішка. 応対 — обслуговування або відповідь людині, без обов’язкової привітності.", "Читання あいそ та あいそう. 愛嬌／愛敬（あいきょう）— варіанти написання іншого слова зі значенням чарівності або милої риси; це не варіант написання 愛想. 愛想がいい／悪い — привітний / непривітний; 愛想を尽かす — остаточно розчаруватися в комусь. 愛想笑い — ввічлива, іноді нещира усмішка. 応対 — обслуговування або відповідь людині, без обов’язкової привітності."),
    ("811", "exampleTranslations[1]", "Перед вступом на посаду наступного місяця я здійснив ввічливі візити до причетних установ.", "Перед вступом на посаду наступного місяця я завітав до відповідних установ, щоб привітатися.")
]

EXPECTED = {
    "788": ("脈", "みゃく", ["名詞"]),
    "789": ("婿", "むこ", ["名詞"]),
    "790": ("網", "あみ", ["名詞"]),
    "793": ("翼", "つばさ", ["名詞"]),
    "794": ("裸", "はだか", ["名詞"]),
    "797": ("例", "れい", ["名詞"]),
    "801": ("脇", "わき", ["名詞"]),
    "803": ("入隊", "にゅうたい", ["名詞"]),
    "805": ("主観", "しゅかん", ["名詞"]),
    "808": ("愛嬌", "あいきょう", ["名詞"]),
    "809": ("愛想", "あいそ／あいそう", ["名詞"]),
    "811": ("挨拶", "あいさつ", ["名詞"])
}
EXPECTED_EXAMPLES = {
    "788": ["看護師は、患者の脈を測って体調を確認した。", "相手の反応を見ると、この商談にはまだ脈がありそうだ。"],
    "789": ["彼は娘の婿として、家業を継ぐことになった。", "娘と婿が、週末に訪ねてきた。"],
    "790": ["漁師たちは、早朝から網を引いて魚を獲る。", "警察は各地に捜査の網を張り、容疑者の行方を追っている。"],
    "793": ["大きな翼を広げた鷲が、悠々と空を舞っている。", "新たな技術という翼を得て、企業は大きく羽ばたいた。"],
    "794": ["彼は裸一貫から身を起こし、一代で巨万の富を築いた。", "子供は裸になって、風呂に入った。"],
    "797": ["具体的な例を挙げて、仕組みを説明した。", "例によって、会議は予定時刻を大幅に超過した。"],
    "801": ["彼は書類を脇に抱えて、慌ただしく会議室を後にした。", "本題から外れる話は、いったん脇に置こう。"],
    "803": ["彼は大学卒業後、自衛隊に入隊して国防の任に当たった。", "入隊式では、新隊員たちが厳粛な面持ちで宣誓した。"],
    "805": ["主観を排して、客観的な事実のみを報告すること。", "評価が主観に偏らないよう、複数の担当者で審査を行う。"],
    "808": ["彼は愛嬌があり、誰からも親しまれる営業担当者だ。", "愛嬌を振りまくだけでは、本質的な信頼は得られない。"],
    "809": ["愛想よく接客することが、店の評判を高める基本だ。", "彼の冷たい対応に、取引先は愛想を尽かした。"],
    "811": ["初対面の挨拶では、相手の目を見て、はっきりと話すことが大切だ。", "来月の就任に先立ち、関係各所へ挨拶に伺った。"]
}

FIXED_IDS = ["788", "789", "790", "793", "794", "797", "801", "803", "805", "808", "809", "811"]
REVIEWED_IDS = []
PENDING_IDS = []
EXPECTED_CHANGED = FIXED_IDS
EVIDENCE = "completion/v191-acceptance.tsv; JLPT_N1_v191_audit.md"

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
    raise RuntimeError("unexpected v190 base SHA-256: " + base_sha)
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
    raise RuntimeError("protected inventory counts do not match v190")
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
    elif field.startswith("s["):
        index = int(re.search(r"\[(\d+)\]", field).group(1))
        actual = details[card_id]["s"][index]
        if actual != old_value:
            raise RuntimeError("related-chip preimage mismatch for " + card_id + "." + field)
        details[card_id]["s"][index] = new_value
    else:
        if details[card_id][field] != old_value:
            raise RuntimeError("field preimage mismatch for " + card_id + "." + field)
        details[card_id][field] = new_value

changed_cards = sorted((card_id for card_id in details if details[card_id] != before[card_id]), key=int)
if changed_cards != EXPECTED_CHANGED:
    raise RuntimeError("unexpected changed-card set: " + str(changed_cards))

allowed_fields = {
    "788": {"exampleTranslations"},
    "789": {"m", "t"},
    "790": {"exampleTranslations"},
    "793": {"exampleTranslations"},
    "794": {"t"},
    "797": {"exampleTranslations"},
    "801": {"m"},
    "803": {"exampleTranslations"},
    "805": {"exampleTranslations"},
    "808": {"m"},
    "809": {"s", "usage"},
    "811": {"exampleTranslations"}
}
for card_id in details:
    for field in before[card_id]:
        if before[card_id][field] != details[card_id][field] and field not in allowed_fields.get(card_id, set()):
            raise RuntimeError("unexpected field mutation: " + card_id + "." + field)
    if before[card_id]["examples"] != details[card_id]["examples"]:
        raise RuntimeError("Japanese example changed: " + card_id)

literal = json.dumps(details, ensure_ascii=False, separators=(",", ":"))
candidate = base[:detail_start] + literal + base[detail_end:]
old_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v190</title>"
new_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v191</title>"
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
baseline_all = {"reviewed": 3906, "fixed_rechecked": 139, "pending": 1802, "total": 5847}
baseline_vocab = {"reviewed": 3337, "fixed_rechecked": 138, "pending": 439, "total": 3914}
target_all = {"reviewed": 3906, "fixed_rechecked": 151, "pending": 1790, "total": 5847}
target_vocab = {"reviewed": 3337, "fixed_rechecked": 150, "pending": 427, "total": 3914}
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
    raise RuntimeError("register state is neither v190 baseline nor expected v191 target")

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
    "base_version": "v190",
    "base_sha256": base_sha,
    "candidate_version": "v191",
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
    "author_credit_before": 3475,
    "author_credit_addition": 12,
    "author_credit_after": 3487,
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
    "author_credit_before": 3475,
    "author_credit_after": 3487,
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
