import csv, hashlib, json, re
from pathlib import Path

BASE = Path("JLPT_N1_ukrainian_reading_v186.html")
OUT = Path("JLPT_N1_ukrainian_reading_v187.html")
WORK = Path("completion/v187-work")
REGISTER = Path("completion/review-register.csv")
BASE_SHA = "75387f14bb77bfcc9f5d0ec224e5f4e6e14ba3d51465b0f435117d4f3af4351b"

UPDATES = [
    ("615", "exampleTranslations[0]", "Навіть якщо припустити, що попит зменшиться більше за початкові очікування, це не завадить продовженню роботи.", "Навіть якщо попит знизиться сильніше, ніж передбачалося спочатку, це не завадить продовженню діяльності."),
    ("615", "exampleTranslations[1]", "Якщо припустити, що цю пропозицію приймуть, як розподілиться фінансове навантаження?", "Якщо припустити, що цю пропозицію ухвалять, яким буде фінансове навантаження?"),
    ("616", "exampleTranslations[0]", "Хоча певне поліпшення помітне, до остаточного розв’язання ще не дійшло.", "Хоча певне поліпшення помітне, докорінного розв’язання проблеми ще не досягнуто."),
    ("618", "exampleTranslations[0]", "Після цього випадку ми маємо намір знову забезпечити суворе виконання заходів проти його повторення.", "Після цього випадку ми маємо намір посилити виконання заходів, щоб подібне не повторилося."),
    ("629", "usage", "わざと間違える — навмисно помилитися, тобто зробити вигляд помилки. Часто звучить як докір, але може описувати навчальний прийом або жарт. あえて — свідомо піти на дію попри перешкоди; не просто будь-який намір.", "わざと間違える — навмисно припуститися помилки. Часто звучить як докір, але може описувати навчальний прийом або жарт. あえて — свідомо піти на дію попри перешкоди; не просто будь-який намір."),
    ("629", "exampleTranslations[1]", "Працівника покарали за те, що він навмисно приховував важливу інформацію.", "Працівника покарали, вважаючи, що він навмисно приховував важливу інформацію."),
    ("644", "exampleTranslations[0]", "Дотримуватися законів — природний обов’язок компанії.", "Дотримуватися законів — само собою зрозумілий обов’язок компанії."),
    ("651", "m", "ウイルスにより起こる急性の感染症。", "インフルエンザウイルスによって起こる急性の感染症。"),
    ("654", "m", "生物の細胞内で増えるウイルス。また、コンピューター上で自己を複製して広がる不正プログラムを指す。", "生きた細胞に入り込み、その細胞の仕組みを利用して増殖する感染性の病原体。また、コンピューター上で自己を複製して広がる不正プログラムを指す。"),
    ("664", "t", "простір, місце, пропуск", "простір, місце; пробіл (у тексті)"),
    ("672", "t", "прилавок, стійка (бару); лічильник", "прилавок, стійка (бару); лічильник; контратака, контрудар (у спорті)"),
    ("672", "exampleTranslations[1]", "Особливість цього закладу — уважне обслуговування покупців через прилавок.", "Особливість цього закладу — уважне обслуговування покупців біля прилавка."),
    ("674", "t", "основа, фундамент, база", "основа, фундамент, база; база (у бейсболі); бас-гітара, басова партія")
]

EXPECTED = {
    "615": ("仮に", "かりに", ["副詞"]),
    "616": ("いくらか", "", ["副詞"]),
    "618": ("改めて", "あらためて", ["副詞"]),
    "624": ("間もなく", "まもなく", ["副詞"]),
    "629": ("わざと", "", ["副詞"]),
    "644": ("当然", "とうぜん", ["副詞"]),
    "651": ("インフルエンザ", "", ["名詞"]),
    "654": ("ウイルス", "", ["名詞"]),
    "663": ("オーバー", "", ["名詞"]),
    "664": ("スペース", "", ["名詞"]),
    "672": ("カウンター", "", ["名詞"]),
    "674": ("ベース", "", ["名詞"])
}
EXPECTED_EXAMPLES = {
    "615": ["仮に当初の想定より需要が減少したとしても、事業継続に支障はない。", "仮にこの提案が採用されたとして、費用面の負担はどうなるのか。"],
    "616": ["いくらかの改善は見られるものの、根本的な解決には至っていない。", "いくらか時間をいただければ、対応可能と存じます。"],
    "618": ["今回の件を受け、改めて再発防止策を徹底する方針だ。", "改めてご連絡いたしますので、少々お待ちください。"],
    "624": ["間もなく会議が始まりますので、お席にお着きください。", "新しい制度は、間もなく施行される予定だ。"],
    "629": ["彼女はわざと厳しい意見を述べて、議論を活性化させようとした。", "重要な情報をわざと隠していたとして、担当者は処分を受けた。"],
    "644": ["法令を遵守することは、企業として当然の責務だ。", "当然のことながら、顧客の個人情報は厳重に管理されなければならない。"],
    "651": ["インフルエンザの流行により、複数の学校が学級閉鎖に踏み切った。", "彼はインフルエンザにかかり、今日の会議を欠席すると連絡してきた。"],
    "654": ["その文章には、いくつかの種類のウイルスが登場した。", "ウイルスに感染したパソコンから、機密情報が流出する恐れがある。"],
    "663": ["その説明は少しオーバーに聞こえるが、事実に基づいている。", "予算を大幅にオーバーしてしまい、計画を見直す必要がある。"],
    "664": ["オフィスのスペースが手狭になり、移転を検討している。", "新製品は、設置スペースをほとんど取らないコンパクト設計だ。"],
    "672": ["受付のカウンターで、来訪者の氏名を記入する決まりになっている。", "カウンター越しに丁寧に接客するのが、この店の特徴だ。"],
    "674": ["当社は、都内の拠点をベースに、全国へ事業を展開している。", "基本給をベースにして、賞与額が算定される。"]
}

FIXED_IDS = ["615", "616", "618", "629", "651", "654", "664", "672", "674"]
REVIEWED_IDS = ["624"]
PENDING_IDS = ["644", "663"]
EXPECTED_CHANGED = ["615", "616", "618", "629", "644", "651", "654", "664", "672", "674"]
EVIDENCE = "completion/v187-acceptance.tsv; JLPT_N1_v187_audit.md"

def extract(source, name):
    match = re.search(r"\\bconst " + re.escape(name) + r"\\s*=\\s*", source)
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
            elif char == "\\\\":
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
    raise RuntimeError("unexpected v186 base SHA-256: " + base_sha)
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
    raise RuntimeError("protected inventory counts do not match v186")
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
        index = int(re.search(r"\\[(\\d+)\\]", field).group(1))
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
if details["663"] != before["663"]:
    raise RuntimeError("C11-dependent card 663 must remain unchanged")

allowed_fields = {
    "615": {"exampleTranslations"},
    "616": {"exampleTranslations"},
    "618": {"exampleTranslations"},
    "629": {"usage", "exampleTranslations"},
    "644": {"exampleTranslations"},
    "651": {"m"},
    "654": {"m"},
    "664": {"t"},
    "672": {"t", "exampleTranslations"},
    "674": {"t"}
}
for card_id in details:
    for field in before[card_id]:
        if before[card_id][field] != details[card_id][field] and field not in allowed_fields.get(card_id, set()):
            raise RuntimeError("unexpected field mutation: " + card_id + "." + field)
    if before[card_id]["examples"] != details[card_id]["examples"]:
        raise RuntimeError("Japanese example changed: " + card_id)

literal = json.dumps(details, ensure_ascii=False, separators=(",", ":"))
candidate = base[:detail_start] + literal + base[detail_end:]
old_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v186</title>"
new_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v187</title>"
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
baseline_all = {"reviewed": 3905, "fixed_rechecked": 94, "pending": 1848, "total": 5847}
baseline_vocab = {"reviewed": 3336, "fixed_rechecked": 93, "pending": 485, "total": 3914}
target_all = {"reviewed": 3906, "fixed_rechecked": 103, "pending": 1838, "total": 5847}
target_vocab = {"reviewed": 3337, "fixed_rechecked": 102, "pending": 475, "total": 3914}
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
    for card_id in PENDING_IDS:
        row = rows_by_id[card_id][0]
        if row["finalReview"] != "pending" or row["evidence"]:
            raise RuntimeError("pending C11 preimage mismatch for " + card_id)
    with REGISTER.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["kind", "key", "baselineLocation", "finalReview", "evidence"], lineterminator="\\n")
        writer.writeheader()
        writer.writerows(register_rows)
    register_mode = "applied_from_baseline"
elif current_all == target_all and current_vocab == target_vocab:
    for card_id in FIXED_IDS:
        row = rows_by_id[card_id][0]
        if row["finalReview"] != "fixed_rechecked":
            raise RuntimeError("fixed target mismatch for " + card_id)
        row["evidence"] = EVIDENCE
    for card_id in REVIEWED_IDS:
        row = rows_by_id[card_id][0]
        if row["finalReview"] != "reviewed":
            raise RuntimeError("reviewed target mismatch for " + card_id)
        row["evidence"] = EVIDENCE
    for card_id in PENDING_IDS:
        row = rows_by_id[card_id][0]
        if row["finalReview"] != "pending" or row["evidence"]:
            raise RuntimeError("pending target mismatch for " + card_id)
else:
    raise RuntimeError("register state is neither v186 baseline nor expected v187 target")

after_all = counts(register_rows)
after_vocab = counts(register_rows, "vocab")
if after_all != target_all or after_vocab != target_vocab:
    raise RuntimeError("register target mismatch: " + str(after_all) + " / " + str(after_vocab))

prepare = {
    "pass": True,
    "base_version": "v186",
    "base_sha256": base_sha,
    "candidate_version": "v187",
    "candidate_sha256": candidate_sha,
    "candidate_bytes": OUT.stat().st_size,
    "vocabulary_records": len(vocab),
    "grammar_records": len(grammar),
    "lexical_pairs": len(pairs),
    "unique_vocabulary_ids": len({int(item["id"]) for item in vocab}),
    "review_scope": [int(card_id) for card_id in scope],
    "fixed_rechecked": [int(card_id) for card_id in FIXED_IDS],
    "reviewed_without_change": [int(card_id) for card_id in REVIEWED_IDS],
    "pending_c11": [int(card_id) for card_id in PENDING_IDS],
    "updated_fields": len(UPDATES),
    "changed_cards": [int(card_id) for card_id in changed_cards],
    "field_updates": [{"id": int(card_id), "field": field, "before": old, "after": new} for card_id, field, old, new in UPDATES],
    "author_credit_before": 3429,
    "author_credit_addition": 10,
    "author_credit_after": 3439,
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
    "pending_c11_ids": [int(card_id) for card_id in PENDING_IDS],
    "author_credit_before": 3429,
    "author_credit_after": 3439,
    "duplicate_keys": 0,
    "records_deleted": 0,
    "history_rewritten": False
}
(WORK / "prepare-results.json").write_text(json.dumps(prepare, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
(WORK / "registry-results.json").write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")

checkpoint_path = WORK / "checkpoint.json"
checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
checkpoint["status"] = "author review complete; deterministic candidate and register prepared; Chromium verification pending"
checkpoint["candidate_sha256"] = candidate_sha
checkpoint["candidate_bytes"] = OUT.stat().st_size
checkpoint["exact_rollback"] = True
checkpoint["register_mode"] = register_mode
checkpoint_path.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")

print(json.dumps({"pass": True, "candidate_sha256": candidate_sha, "candidate_bytes": OUT.stat().st_size, "fixed_rechecked": FIXED_IDS, "reviewed": REVIEWED_IDS, "pending_c11": PENDING_IDS, "register_after": after_all, "vocabulary_after": after_vocab}, ensure_ascii=False, indent=2))
