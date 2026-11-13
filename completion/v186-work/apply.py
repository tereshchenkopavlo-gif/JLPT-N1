import csv, hashlib, json, re
from pathlib import Path

BASE = Path("JLPT_N1_ukrainian_reading_v185.html")
OUT = Path("JLPT_N1_ukrainian_reading_v186.html")
WORK = Path("completion/v186-work")
REGISTER = Path("completion/review-register.csv")
BASE_SHA = "0cc48969700d238c27e7c3d4f18773ab31508257b0b11a544e5b15f83a178042"

UPDATES = [
    ("565", "exampleTranslations[0]", "Роботи йдуть добре, і завершити їх планують наступного місяця, як і передбачено.", "Роботи йдуть добре, і, як очікується, їх завершать наступного місяця за графіком."),
    ("571", "exampleTranslations[1]", "Багато хто шкодував через його вихід на пенсію, і на прощання влаштували велике святкування.", "Багато хто шкодував через його відхід із роботи, тож для нього влаштували пишний прощальний захід."),
    ("572", "t", "ініціативний, такий, що охоче діє або бере участь, а не чекає", "активний, ініціативний; прихильний до чогось, такий, що позитивно оцінює й підтримує"),
    ("579", "exampleTranslations[0]", "Саме накопичення результатів малопомітної роботи дає великі здобутки.", "Саме послідовна малопомітна праця й дає великі результати."),
    ("586", "exampleTranslations[1]", "У цій історії зображено персонажа, який уособлює типового героя.", "У цій історії є персонаж, який утілює типовий образ героя."),
    ("590", "exampleTranslations[1]", "Важливо сумлінно приймати негативні оцінки й використовувати їх для поліпшення.", "Важливо серйозно ставитися до негативних оцінок і використовувати їх для поліпшення."),
    ("593", "exampleTranslations[0]", "Не можна миритися з тим, що людина раз у раз незворушно запізнюється попри численні зауваження.", "Не можна миритися з тим, що людина, попри численні зауваження, знову й знову запізнюється, наче нічого не сталося."),
    ("595", "exampleTranslations[0]", "Якщо відвантажувати продукцію з недостатньо відпрацьованою технологією, можна спричинити непоправну аварію.", "Якщо відвантажувати продукцію з недостатньо відпрацьованою технологією, це може призвести до аварії з непоправними наслідками."),
    ("597", "exampleTranslations[1]", "На нараді впадали в око учасники, які обмежувалися лише безпечними, нікого не дратівливими думками.", "На нараді впадали в око учасники, які обмежувалися нейтральними висловлюваннями, що нікого не зачіпали."),
    ("609", "usage", "Самостійне わりに — порівняно, доволі; Nの／V・いAの普通形／なAな＋わりに — як на певну обставину. 暑いわりに人が多い: людей багато, попри спеку. Зазвичай є розбіжність із очікуванням, але не завжди негативна оцінка.", "Самостійне わりに — порівняно, доволі; Nの／V普通形／イ形容詞普通形／ナ形容詞な＋わりに — як на певну обставину. 暑いわりに人が多い: людей багато, попри спеку. Зазвичай є розбіжність із очікуванням, але не завжди негативна оцінка.")
]

EXPECTED = {
    "565": ("順調", "じゅんちょう", ["ナ形"]),
    "571": ("盛大", "せいだい", ["ナ形"]),
    "572": ("積極的", "せっきょくてき", ["ナ形"]),
    "579": ("地味", "じみ", ["ナ形"]),
    "586": ("典型的", "てんけいてき", ["ナ形"]),
    "588": ("独特", "どくとく", ["ナ形"]),
    "590": ("否定的", "ひていてき", ["ナ形"]),
    "593": ("平気", "へいき", ["ナ形"]),
    "595": ("未熟", "みじゅく", ["ナ形"]),
    "597": ("無難", "ぶなん", ["ナ形"]),
    "599": ("無礼", "ぶれい", ["ナ形"]),
    "609": ("わりに", "", ["副詞"])
}

EXPECTED_EXAMPLES = {
    "565": ["計画は順調に進んでおり、予定どおり来月に完成する見込みだ。", "事業の順調な拡大を背景に、新たな人材の採用を強化している。"],
    "571": ["創立五十周年の記念式典が、盛大に開催された。", "彼の退職を惜しむ声は多く、盛大な送別会が催された。"],
    "572": ["新規顧客の開拓に、積極的に取り組んでいる。", "若手社員の積極的な提案を、会社は歓迎している。"],
    "579": ["地味な作業の積み重ねこそが、大きな成果を生む。", "彼の地味ながらも誠実な仕事ぶりは、社内で高く評価されている。"],
    "586": ["これは、組織の硬直化がもたらす典型的な失敗例だ。", "この物語には、典型的な英雄像を体現する人物が登場する。"],
    "588": ["同社の独特な企業文化は、他社にはまねしにくい強みとなっている。", "彼は独特な視点から、市場の動向を鋭く分析した。"],
    "590": ["計画に対して否定的な意見が相次ぎ、見直しを迫られた。", "否定的な評価を真摯に受け止め、改善に生かす姿勢が大切だ。"],
    "593": ["何度注意されても平気な顔で遅刻を繰り返す姿勢は、容認できない。", "彼は批判を浴びても平気な様子で、持論を貫いた。"],
    "595": ["未熟な技術のままで製品を出荷すれば、取り返しのつかない事故を招きかねない。", "私の技術はまだ未熟ですが、精一杯努力してまいります。"],
    "597": ["無難な選択をするだけでは、競合との差別化は図れない。", "会議では、無難な意見に終始する出席者が目立った。"],
    "599": ["初対面の相手に対して無礼な態度を取ることは、厳に慎むべきだ。", "無礼な言動に対し、被害者は謝罪を求めた。"],
    "609": ["最新の機器にしては、価格はわりに手頃だった。", "準備期間が短かったわりに、イベントは盛況のうちに幕を閉じた。"]
}

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
    raise RuntimeError("unexpected v185 base SHA-256: " + base_sha)
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
    raise RuntimeError("published base counts do not match the protected inventory")
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
expected_changed = ["565", "571", "572", "579", "586", "590", "593", "595", "597", "609"]
if changed_cards != expected_changed:
    raise RuntimeError("unexpected changed-card set: " + str(changed_cards))
if details["588"] != before["588"] or details["599"] != before["599"]:
    raise RuntimeError("C11-dependent cards 588/599 must remain unchanged")

allowed_fields = {
    "565": {"exampleTranslations"},
    "571": {"exampleTranslations"},
    "572": {"t"},
    "579": {"exampleTranslations"},
    "586": {"exampleTranslations"},
    "590": {"exampleTranslations"},
    "593": {"exampleTranslations"},
    "595": {"exampleTranslations"},
    "597": {"exampleTranslations"},
    "609": {"usage"}
}
for card_id in details:
    for field in before[card_id]:
        if before[card_id][field] != details[card_id][field] and field not in allowed_fields.get(card_id, set()):
            raise RuntimeError("unexpected field mutation: " + card_id + "." + field)
    if before[card_id]["examples"] != details[card_id]["examples"]:
        raise RuntimeError("Japanese example changed: " + card_id)

literal = json.dumps(details, ensure_ascii=False, separators=(",", ":"))
candidate = base[:detail_start] + literal + base[detail_end:]
old_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v185</title>"
new_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v186</title>"
if candidate.count(old_title) != 1:
    raise RuntimeError("version title marker mismatch")
candidate = candidate.replace(old_title, new_title, 1)
rollback = candidate.replace(new_title, old_title, 1)
rollback = rollback.replace(literal, base[detail_start:detail_end], 1)
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

register_text = REGISTER.read_text(encoding="utf-8")
register_rows = list(csv.DictReader(register_text.splitlines()))
if len(register_rows) != 5847:
    raise RuntimeError("unexpected register row count: " + str(len(register_rows)))
before_all = counts(register_rows)
before_vocab = counts(register_rows, "vocab")
if before_all != {"reviewed": 3905, "fixed_rechecked": 84, "pending": 1858, "total": 5847}:
    raise RuntimeError("register baseline mismatch: " + str(before_all))
if before_vocab != {"reviewed": 3336, "fixed_rechecked": 83, "pending": 495, "total": 3914}:
    raise RuntimeError("vocabulary register baseline mismatch: " + str(before_vocab))

fixed_ids = set(expected_changed)
pending_ids = {"588", "599"}
for card_id in scope:
    matches = [row for row in register_rows if row["kind"] == "vocab" and row["key"] == card_id]
    if len(matches) != 1 or matches[0]["finalReview"] != "pending":
        raise RuntimeError("register pending preimage mismatch for " + card_id)
    if card_id in fixed_ids:
        matches[0]["finalReview"] = "fixed_rechecked"
        matches[0]["evidence"] = "v186-acceptance.tsv; JLPT_N1_v186_audit.md"
    elif card_id not in pending_ids:
        raise RuntimeError("scope decision missing for " + card_id)

after_all = counts(register_rows)
after_vocab = counts(register_rows, "vocab")
if after_all != {"reviewed": 3905, "fixed_rechecked": 94, "pending": 1848, "total": 5847}:
    raise RuntimeError("register result mismatch: " + str(after_all))
if after_vocab != {"reviewed": 3336, "fixed_rechecked": 93, "pending": 485, "total": 3914}:
    raise RuntimeError("vocabulary result mismatch: " + str(after_vocab))

with REGISTER.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=["kind", "key", "baselineLocation", "finalReview", "evidence"], lineterminator="\n")
    writer.writeheader()
    writer.writerows(register_rows)

prepare = {
    "pass": True,
    "base_version": "v185",
    "base_sha256": base_sha,
    "candidate_version": "v186",
    "candidate_sha256": candidate_sha,
    "candidate_bytes": OUT.stat().st_size,
    "vocabulary_records": len(vocab),
    "grammar_records": len(grammar),
    "lexical_pairs": len(pairs),
    "unique_vocabulary_ids": len({int(item["id"]) for item in vocab}),
    "review_scope": [int(card_id) for card_id in scope],
    "fixed_rechecked": [int(card_id) for card_id in expected_changed],
    "pending_c11": [588, 599],
    "updated_fields": len(UPDATES),
    "changed_cards": [int(card_id) for card_id in changed_cards],
    "field_updates": [{"id": int(card_id), "field": field, "before": old_value, "after": new_value} for card_id, field, old_value, new_value in UPDATES],
    "author_credit_before": 3419,
    "author_credit_addition": 10,
    "author_credit_after": 3429,
    "protected_unchanged": {name: True for name in protected},
    "japanese_examples_unchanged": True,
    "exact_rollback": True,
    "register_updated": True,
    "author_review_only": True
}
registry = {
    "pass": True,
    "register_rows": len(register_rows),
    "before": {"all": before_all, "vocabulary": before_vocab},
    "after": {"all": after_all, "vocabulary": after_vocab},
    "fixed_rechecked_ids": [int(card_id) for card_id in expected_changed],
    "pending_c11_ids": [588, 599],
    "author_credit_before": 3419,
    "author_credit_after": 3429,
    "duplicate_keys": 0,
    "records_deleted": 0,
    "history_rewritten": False
}
(WORK / "prepare-results.json").write_text(json.dumps(prepare, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(WORK / "registry-results.json").write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

checkpoint_path = WORK / "checkpoint.json"
checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
checkpoint["status"] = "author review complete; deterministic candidate and register prepared; Chromium verification pending"
checkpoint["author_review"] = {"fixed_rechecked": [int(card_id) for card_id in expected_changed], "pending_c11": [588, 599], "author_credit_after": 3429}
checkpoint["candidate_sha256"] = candidate_sha
checkpoint["candidate_bytes"] = OUT.stat().st_size
checkpoint["exact_rollback"] = True
checkpoint_path.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({"pass": True, "candidate_sha256": candidate_sha, "candidate_bytes": OUT.stat().st_size, "fixed_rechecked": expected_changed, "pending_c11": sorted(pending_ids, key=int), "register_before": before_all, "register_after": after_all}, ensure_ascii=False, indent=2))
