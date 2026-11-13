import csv, hashlib, json, re
from pathlib import Path

BASE = Path("JLPT_N1_ukrainian_reading_v198.html")
OUT = Path("JLPT_N1_ukrainian_reading_v199.html")
WORK = Path("completion/v199-work")
REGISTER = Path("completion/review-register.csv")
BASE_SHA = "32c0bf74d083db74576d53a249ec1858352f20efcea9a72dd3c80daf3a17a39c"

UPDATES = [
    ("1042", "t", "практична навичка чи майстерність, набута тренуванням", "практична навичка чи майстерність, набута тренуванням або досвідом"),
    ("1042", "usage", "Іменник: 技能を身につける／磨く、技能が高い. Практичне вміння, яке людина опановує тренуванням. 技術 може бути методом або системою знань і технологій; 技能 акцентує здатність виконувати конкретну роботу.", "Іменник: 技能を身につける／磨く、技能が高い. Практичне вміння, яке людина опановує тренуванням і досвідом роботи. 技術 може бути методом або системою знань і технологій; 技能 акцентує здатність виконувати конкретну роботу."),
    ("1043", "exampleTranslations[0]", "Дедалі більше людей ставлять під сумнів спосіб життя, за якого працюють навіть ціною сімейного добробуту.", "Дедалі більше людей ставлять під сумнів спосіб життя, за якого заради роботи жертвують сімейним життям."),
    ("1044", "exampleTranslations[0]", "У парламенті наполегливо вимагали пояснень щодо підозр у незаконному фінансуванні політика.", "У парламенті наполегливо вимагали пояснень щодо підозр у незаконних грошових внесках політику."),
    ("1046", "t", "моральний або соціальний обов’язок у взаєминах; також формальна люб’язність і спорідненість через шлюб: 義理の母 — свекруха або теща", "моральний або соціальний обов’язок у взаєминах; також формальна люб’язність і непрямі родинні зв’язки: 義理の母 — свекруха, теща, а залежно від контексту — мачуха чи прийомна мати"),
    ("1048", "exampleTranslations[0]", "Рада директорів мала ухвалити новий план діяльності.", "Правління мало ухвалити новий план діяльності."),
    ("1061", "exampleTranslations[0]", "У лікарні постійно чергують лікарі, щоб приймати невідкладних пацієнтів і вночі.", "У лікарні лікарі чергують цілодобово, щоб приймати пацієнтів, які потребують невідкладної допомоги."),
    ("1061", "exampleTranslations[1]", "За повідомленням, стан доставленого невідкладного пацієнта, на щастя, стабільний.", "На щастя, стан доставленого пацієнта стабільний."),
    ("1063", "exampleTranslations[0]", "Через нестачу працівників компанія вирішила терміново набрати продавців на неповний робочий час.", "Через нестачу персоналу компанія вирішила терміново набрати продавців на підробіток."),
    ("1066", "usage", "Іменник; 被害者を救済する、救済措置. Допомогти вийти зі скрути, відшкодувати несправедливість або забезпечити захист; також релігійне спасіння. 救援 частіше конкретна підтримка в кризі. Спосіб допомоги визначає контекст.", "Іменник; 被害者を救済する、救済措置. Допомогти вийти зі скрути, виправити несправедливість або забезпечити правовий захист; також релігійне спасіння. 救援 частіше конкретна підтримка в кризі. Спосіб допомоги визначає контекст."),
    ("1067", "exampleTranslations[0]", "Він прагнув створити страву, яку можна було б назвати вершиною смаку.", "Він прагнув до страви, яку можна було б назвати вершиною смаку."),
    ("1072", "m", "相手の要求や申し出を、きっぱりと断ること。", "相手の要求や申し出を、きっぱりと断ること。また、移植された臓器などを体が異物として受け入れないこと。"),
    ("1072", "usage", "Іменник; 提案／接触を拒絶する、拒絶される. Виразно відкинути або не прийняти. 拒否 близьке й теж може бути категоричним; різниця не є незмінною шкалою сили. 拒絶 часто передає особисте відторгнення, 拒否 — рішення не погодитися.", "Іменник; 提案／接触を拒絶する、拒絶される、移植片の拒絶反応. Виразно відкинути або не прийняти; у біологічному контексті — відторгнення трансплантата. 拒否 близьке й теж може бути категоричним; різниця не є незмінною шкалою сили. 拒絶 часто передає особисте відторгнення, 拒否 — рішення не погодитися."),
    ("1073", "exampleTranslations[0]", "Профспілка продемонструвала готовність відмовитися від прийняття запропонованих компанією умов.", "Профспілка дала зрозуміти, що готова відхилити запропоновані компанією умови."),
    ("1074", "exampleTranslations[0]", "Вони оголосили, що планують провести весільну церемонію наступної весни у святилищі на батьківщині.", "Вони оголосили, що планують провести весільну церемонію наступної весни у святилищі в рідному краї.")
]
EXPECTED = {
    "1042": ("技能", "ぎのう", ["名詞"]),
    "1043": ("犠牲", "ぎせい", ["名詞"]),
    "1044": ("疑惑", "ぎわく", ["名詞"]),
    "1046": ("義理", "ぎり", ["名詞"]),
    "1048": ("議決", "ぎけつ", ["名詞"]),
    "1061": ("急患", "きゅうかん", ["名詞"]),
    "1063": ("急募", "きゅうぼ", ["名詞"]),
    "1066": ("救済", "きゅうさい", ["名詞"]),
    "1067": ("究極", "きゅうきょく", ["名詞"]),
    "1072": ("拒絶", "きょぜつ", ["名詞"]),
    "1073": ("拒否", "きょひ", ["名詞"]),
    "1074": ("挙式", "きょしき", ["名詞"])
}
EXPECTED_EXAMPLES = {
    "1042": ["高度な技能を持つ職人の減少が、業界の大きな課題となっている。", "新入社員に必要な技能を習得させるため、研修制度を見直した。"],
    "1043": ["家庭を犠牲にしてまで働き続ける生き方に、疑問を持つ人が増えている。", "災害の犠牲になった方々を悼み、各地で追悼の式典が営まれた。"],
    "1044": ["政治家に対する不正献金の疑惑が、国会で厳しく追及された。", "会社は、会計処理をめぐる疑惑を否定する声明を発表した。"],
    "1046": ["世話になった先輩の頼みとあって、義理を欠くわけにはいかなかった。", "義理と人情の板挟みになって、彼は長いあいだ悩み続けた。"],
    "1048": ["理事会は、新たな事業計画を議決する運びとなった。", "出席者の過半数の賛成をもって議決される決まりである。"],
    "1061": ["夜間も急患に対応できるよう、病院は医師を常時待機させている。", "搬送された急患の容体は、幸いにも安定しているという。"],
    "1063": ["人手が足りず、会社はアルバイトの店員を急募することにした。", "欠員が出た部署では、経験者を急募している。"],
    "1066": ["被害者を救済するための基金が、国の主導で設立された。", "弱い立場の人々を救済する制度の整備が求められている。"],
    "1067": ["彼が追い求めたのは、味の究極ともいえる一皿であった。", "究極の選択を迫られ、経営者は苦渋の決断を下した。"],
    "1072": ["相手側は、こちらの提案を頑として拒絶し、交渉は行き詰まった。", "彼は、不当な要求を毅然と拒絶する姿勢を貫いた。"],
    "1073": ["組合は、会社側が示した条件の受け入れを拒否する構えを見せた。", "出席の要請を拒否した証人に、委員会は強い遺憾の意を示した。"],
    "1074": ["二人は、来春に郷里の神社で挙式する予定だと発表した。", "挙式の費用を抑えるため、招待客の人数を減らした。"]
}
FIXED_IDS = ["1042","1043","1044","1046","1048","1061","1063","1066","1067","1072","1073","1074"]
REVIEWED_IDS = []
PENDING_IDS = []
EXPECTED_CHANGED = FIXED_IDS
EVIDENCE = "completion/v199-acceptance.tsv; JLPT_N1_v199_audit.md"

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
    raise RuntimeError("unexpected v198 base SHA-256: " + base_sha)
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
    raise RuntimeError("protected inventory counts do not match v198")
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
    "1042": {"t","usage"},
    "1043": {"exampleTranslations"},
    "1044": {"exampleTranslations"},
    "1046": {"t"},
    "1048": {"exampleTranslations"},
    "1061": {"exampleTranslations"},
    "1063": {"exampleTranslations"},
    "1066": {"usage"},
    "1067": {"exampleTranslations"},
    "1072": {"m","usage"},
    "1073": {"exampleTranslations"},
    "1074": {"exampleTranslations"}
}
for card_id in details:
    for field in before[card_id]:
        if before[card_id][field] != details[card_id][field] and field not in allowed_fields.get(card_id, set()):
            raise RuntimeError("unexpected field mutation: " + card_id + "." + field)
    if before[card_id]["examples"] != details[card_id]["examples"]:
        raise RuntimeError("Japanese example changed: " + card_id)

literal = json.dumps(details, ensure_ascii=False, separators=(",", ":"))
candidate = base[:detail_start] + literal + base[detail_end:]
old_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v198</title>"
new_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v199</title>"
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
baseline_all = {"reviewed": 3914, "fixed_rechecked": 219, "pending": 1714, "total": 5847}
baseline_vocab = {"reviewed": 3345, "fixed_rechecked": 218, "pending": 351, "total": 3914}
target_all = {"reviewed": 3914, "fixed_rechecked": 231, "pending": 1702, "total": 5847}
target_vocab = {"reviewed": 3345, "fixed_rechecked": 230, "pending": 339, "total": 3914}
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
    raise RuntimeError("register state is neither v198 baseline nor expected v199 target")

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
    "base_version": "v198",
    "base_sha256": base_sha,
    "candidate_version": "v199",
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
    "author_credit_before": 3563,
    "author_credit_addition": 12,
    "author_credit_after": 3575,
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
    "author_credit_before": 3563,
    "author_credit_after": 3575,
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
