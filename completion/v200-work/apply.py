import csv, hashlib, json, re
from pathlib import Path

BASE = Path("JLPT_N1_ukrainian_reading_v199.html")
OUT = Path("JLPT_N1_ukrainian_reading_v200.html")
WORK = Path("completion/v200-work")
REGISTER = Path("completion/review-register.csv")
BASE_SHA = "c81d7624557b2193bd6bc7939c93e200b054323f4b845f19921d70924a9ab280"

UPDATES = [
    ("1077", "t", "риболовне судно, човен або корабель, призначений для промислового вилову риби", "риболовне судно, човен або корабель, призначений для вилову риби й молюсків"),
    ("1077", "exampleTranslations[1]", "Через подорожчання пального дедалі більше рибалок відмовляються виходити в море.", "Через подорожчання пального дедалі більше рибалок відкладають вихід у море."),
    ("1090", "exampleTranslations[1]", "Цей університет широко відомий сильними легкоатлетами.", "Цей університет широко відомий як один із лідерів у легкій атлетиці.")
]
EXPECTED = {
    "1075": ("虚偽", "きょぎ", ["名詞"]),
    "1077": ("漁船", "ぎょせん", ["名詞"]),
    "1080": ("競走", "きょうそう", ["名詞"]),
    "1081": ("共鳴", "きょうめい", ["名詞"]),
    "1083": ("協議", "きょうぎ", ["名詞"]),
    "1085": ("協定", "きょうてい", ["名詞"]),
    "1087": ("境地", "きょうち", ["名詞"]),
    "1088": ("境内", "けいだい", ["名詞"]),
    "1090": ("強豪", "きょうごう", ["名詞"]),
    "1092": ("強盗", "ごうとう", ["名詞"]),
    "1094": ("教科", "きょうか", ["名詞"]),
    "1095": ("教訓", "きょうくん", ["名詞"])
}
EXPECTED_EXAMPLES = {
    "1075": ["申告書に虚偽の内容がないか、担当者が確認した。", "虚偽の情報が拡散し、市場に大きな混乱を招いた。"],
    "1077": ["夜明けとともに、港から多くの漁船が沖へと出ていった。", "燃料の高騰で、漁船の出港を見合わせる漁師が相次いでいる。"],
    "1080": ["子どもたちは、運動会で百メートルを競走した。", "地元の商店街では、毎年恒例の馬車競走が行われている。"],
    "1081": ["彼の理念に共鳴した若者たちが、各地から集まってきた。", "二つの音叉は共鳴して、静かな部屋に澄んだ音が響いた。"],
    "1083": ["今後の方針については、両社の担当者が改めて協議する予定である。", "各国代表は、気候変動への対応策を協議した。"],
    "1085": ["両国は、関税を段階的に引き下げる協定を結んだ。", "新たに結ばれた協定により、環境保護の枠組みが強化された。"],
    "1087": ["長年の修練の末、彼は無心の境地に到達したと語った。", "達観した境地に至るまでには、多くの苦労があったという。"],
    "1088": ["正月には、多くの参拝客で神社の境内が埋め尽くされる。", "境内の古い杉の大木は、市の天然記念物に指定されている。"],
    "1090": ["予選では、全国の強豪が顔を合わせる白熱した試合が続いた。", "この大学は、陸上競技の強豪として広く知られている。"],
    "1092": ["深夜の住宅街で発生した強盗事件に、警察が捜査を始めた。", "店に押し入った強盗の一人が、警察に逮捕された。"],
    "1094": ["新しい学習指導要領により、小学校で教える教科の内容が見直された。", "得意な教科を伸ばすことが、学習意欲の向上につながる。"],
    "1095": ["過去の失敗から得た教訓を、組織全体で共有することが重要である。", "この災害の教訓を、次の世代に確実に伝えていかなければならない。"]
}
FIXED_IDS = ["1077", "1090"]
REVIEWED_IDS = ["1075", "1080", "1081", "1083", "1085", "1087", "1088", "1092", "1094", "1095"]
PENDING_IDS = []
EXPECTED_CHANGED = FIXED_IDS
EVIDENCE = "completion/v200-acceptance.tsv; JLPT_N1_v200_audit.md"

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
    raise RuntimeError("unexpected v199 base SHA-256: " + base_sha)
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
    raise RuntimeError("protected inventory counts do not match v199")
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
    "1077": {"t","exampleTranslations"},
    "1090": {"exampleTranslations"}
}
for card_id in details:
    for field in before[card_id]:
        if before[card_id][field] != details[card_id][field] and field not in allowed_fields.get(card_id, set()):
            raise RuntimeError("unexpected field mutation: " + card_id + "." + field)
    if before[card_id]["examples"] != details[card_id]["examples"]:
        raise RuntimeError("Japanese example changed: " + card_id)

literal = json.dumps(details, ensure_ascii=False, separators=(",", ":"))
candidate = base[:detail_start] + literal + base[detail_end:]
old_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v199</title>"
new_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v200</title>"
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
baseline_all = {"reviewed": 3914, "fixed_rechecked": 231, "pending": 1702, "total": 5847}
baseline_vocab = {"reviewed": 3345, "fixed_rechecked": 230, "pending": 339, "total": 3914}
target_all = {"reviewed": 3924, "fixed_rechecked": 233, "pending": 1690, "total": 5847}
target_vocab = {"reviewed": 3355, "fixed_rechecked": 232, "pending": 327, "total": 3914}
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
    raise RuntimeError("register state is neither v199 baseline nor expected v200 target")

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
    "base_version": "v199",
    "base_sha256": base_sha,
    "candidate_version": "v200",
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
    "author_credit_before": 3575,
    "author_credit_addition": 12,
    "author_credit_after": 3587,
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
    "author_credit_before": 3575,
    "author_credit_after": 3587,
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
