import copy, hashlib, json, re
from pathlib import Path

BASE = Path("JLPT_N1_ukrainian_reading_v228.html")
OUT = Path("JLPT_N1_ukrainian_reading_v229.html")
WORK = Path("completion/v229-work")
WORK.mkdir(parents=True, exist_ok=True)
BASE_SHA256 = "189e4f570d61556cbc9073cf67cc106958e44706b9feeecd1c51abbc096ff5e8"
OLD_TITLE = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v228</title>"
NEW_TITLE = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v229</title>"

def extract_json_const(text, name):
    m = re.search(r"const\s+" + re.escape(name) + r"\s*=\s*", text)
    if not m:
        raise RuntimeError(f"missing JS constant: {name}")
    start = m.end()
    if text[start] not in "[{":
        raise RuntimeError(f"{name} is not a JSON array/object")
    opening = text[start]
    closing = "]" if opening == "[" else "}"
    depth = 0
    in_string = False
    escaped = False
    end = None
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
        elif ch == '"':
            in_string = True
        elif ch == opening:
            depth += 1
        elif ch == closing:
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        raise RuntimeError(f"unterminated JSON constant: {name}")
    literal = text[start:end]
    return start, end, literal, json.loads(literal)

def replace_json_const(text, name, value):
    start, end, old_literal, _ = extract_json_const(text, name)
    new_literal = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return text[:start] + new_literal + text[end:], old_literal, new_literal

base_bytes = BASE.read_bytes()
base_sha = hashlib.sha256(base_bytes).hexdigest()
if base_sha != BASE_SHA256:
    raise RuntimeError(f"unexpected v228 HTML SHA-256: {base_sha}")
base = base_bytes.decode("utf-8")

_, _, _, vocab = extract_json_const(base, "DEFAULT_VOCAB")
_, _, _, grammar = extract_json_const(base, "GRAMMAR_DETAILS_BY_ID")
_, _, _, details = extract_json_const(base, "VOCAB_DETAILS_BY_ID")
_, _, _, pos = extract_json_const(base, "VOCAB_POS_BY_ID")
_, _, _, pairs = extract_json_const(base, "VOCAB_AUDITED_PAIRS")
_, _, _, quizzes = extract_json_const(base, "REVIEWED_MEANING_QUIZZES")
_, _, _, reading_overrides = extract_json_const(base, "REVIEWED_READING_OPTIONS")
_, _, _, kana_targets = extract_json_const(base, "VOCAB_KANA_EXAMPLE_TARGETS")
_, _, _, example_targets = extract_json_const(base, "REVIEWED_EXAMPLE_TARGETS")

if (len(vocab), len(grammar), len(details), len(pos), len(pairs)) != (3914, 130, 3914, 3914, 859):
    raise RuntimeError("base record counts do not match approved scope")
if len({int(x["id"]) for x in vocab}) != 3914:
    raise RuntimeError("duplicate vocabulary IDs")
if len(reading_overrides) != 4:
    raise RuntimeError("unexpected baseline reviewed reading override count")

by_id = {str(x["id"]): x for x in vocab}
expected = {
    "2734": ("来る", "きたる", "動詞(一般)②", ["動詞"]),
    "544": ("いい加減", "いいかげん", "な形容詞①", ["ナ形"]),
    "550": ("わがまま", "わがまま", "な形容詞①", ["ナ形"]),
    "552": ("確か", "たしか", "な形容詞①", ["ナ形"]),
    "557": ("結構", "けっこう", "な形容詞①", ["ナ形"]),
    "588": ("独特", "どくとく", "な形容詞①", ["ナ形"]),
    "599": ("無礼", "ぶれい", "な形容詞①", ["ナ形"]),
    "644": ("当然", "とうぜん", "副詞(一般)①", ["副詞"]),
    "663": ("オーバー", "", "カタカナ①", ["名詞"]),
    "1631": ("相応", "そうおう", "名詞(2文字)", ["名詞"]),
    "3337": ("一切", "いっさい", "副詞(一般)②", ["副詞"]),
    "3345": ("散々", "さんざん", "副詞(一般)②", ["副詞"]),
}
for card_id, (word, reading, category, old_pos) in expected.items():
    row = by_id[card_id]
    if (row["w"], row.get("r", ""), row["c"], pos[card_id]) != (word, reading, category, old_pos):
        raise RuntimeError(f"unexpected baseline identity/category/POS for {card_id}")
    if card_id not in details or details[card_id]["w"] != word:
        raise RuntimeError(f"missing detail record for {card_id}")

old_644 = details["644"]
old_3345 = details["3345"]
old_3345_quiz = quizzes.get("v_3345")
if old_644["examples"] != [
    "法令を遵守することは、企業として当然の責務だ。",
    "当然のことながら、顧客の個人情報は厳重に管理されなければならない。"
]:
    raise RuntimeError("unexpected ID644 example baseline")
if old_3345["examples"][1] != "天候に恵まれず、散々な結果に終わった遠征だった。":
    raise RuntimeError("unexpected ID3345 example baseline")
if not old_3345_quiz or old_3345["examples"][1] not in old_3345_quiz.get("byExample", {}):
    raise RuntimeError("missing ID3345 reviewed byExample baseline")
if pos["2734"] != ["動詞"]:
    raise RuntimeError("unexpected ID2734 POS baseline")

before_details = copy.deepcopy(details)
before_pos = copy.deepcopy(pos)
before_quizzes = copy.deepcopy(quizzes)

# ID2734 is the lexicalized attributive きたる, not the ordinary verb くる.
# Keep DEFAULT_VOCAB.c unchanged: it is also used by the meaning-distractor grouping.
new_pos = copy.deepcopy(pos)
new_pos["2734"] = ["連体詞"]

new_details = copy.deepcopy(details)
new_details["644"]["examples"] = [
    "調査結果が異なれば、結論も当然変わってくる。",
    "当然、顧客の個人情報は厳重に管理されなければならない。"
]
new_details["644"]["exampleTranslations"] = [
    "Якщо результати дослідження різняться, то й висновок, природно, змінюється.",
    "Звісно, персональні дані клієнтів потрібно зберігати під суворим контролем."
]
new_details["644"]["usage"] = (
    "Основне прислівникове вживання: 当然、結果が変わる／当然そう思う — природно, звісно. "
    "Окреме 形動-вживання: 当然の結果／当然だ／当然の権利 — закономірний результат, це природно, належне право. "
    "Оцінює очікуваність або належність, а не просто підтверджує факт; もちろん частіше є відповіддю «звісно»."
)
new_sentence = "彼は会議で散々に批判され、反論できなかった。"
new_details["3345"]["examples"][1] = new_sentence
new_details["3345"]["exampleTranslations"][1] = "На нараді його жорстко розкритикували, і він не зміг заперечити."
new_details["3345"]["usage"] = (
    "散々議論を重ねる — дуже багато, до виснаження; "
    "散々に批判される — зазнати жорсткої критики; "
    "散々な結果 — украй поганий результат (形動-вживання). "
    "Не нейтральне схвалення ґрунтовності в усіх контекстах."
)

new_quizzes = copy.deepcopy(quizzes)
entry = new_quizzes["v_3345"]
by_example = copy.deepcopy(entry.get("byExample", {}))
old_sentence = old_3345["examples"][1]
old_payload = by_example.pop(old_sentence)
by_example[new_sentence] = {
    "correct": "非常に厳しい非難を受けた様子。",
    "wrong": [
        "軽い注意を一度受けただけの様子。",
        "非難の内容がまだ明らかでない様子。",
        "相手の意見を全面的に認めた様子。"
    ],
    "note": "散々に批判される — зазнати дуже жорсткої критики; тут прислівникове вживання, не 散々な結果."
}
entry["byExample"] = by_example

candidate = base
old_blocks, new_blocks = {}, {}
for name, value in [
    ("VOCAB_POS_BY_ID", new_pos),
    ("VOCAB_DETAILS_BY_ID", new_details),
    ("REVIEWED_MEANING_QUIZZES", new_quizzes),
]:
    candidate, old_literal, new_literal = replace_json_const(candidate, name, value)
    old_blocks[name] = old_literal
    new_blocks[name] = new_literal

if candidate.count(OLD_TITLE) != 1:
    raise RuntimeError("expected v228 title marker was not found exactly once")
candidate = candidate.replace(OLD_TITLE, NEW_TITLE, 1)

reverse = candidate.replace(NEW_TITLE, OLD_TITLE, 1)
for name in ["REVIEWED_MEANING_QUIZZES", "VOCAB_DETAILS_BY_ID", "VOCAB_POS_BY_ID"]:
    if reverse.count(new_blocks[name]) != 1:
        raise RuntimeError(f"cannot reverse {name} exactly")
    reverse = reverse.replace(new_blocks[name], old_blocks[name], 1)
if reverse != base:
    raise RuntimeError("v229 patch is not exactly reversible to v228")

# The only changed detail records are 644 and 3345; the only POS change is 2734;
# the only meaning-quiz change is the ID3345 byExample key/payload.
for key in before_details:
    if key not in {"644", "3345"} and before_details[key] != new_details[key]:
        raise RuntimeError(f"unexpected detail change at {key}")
for key in before_pos:
    if key != "2734" and before_pos[key] != new_pos[key]:
        raise RuntimeError(f"unexpected POS change at {key}")
for key in before_quizzes:
    if key != "v_3345" and before_quizzes[key] != new_quizzes[key]:
        raise RuntimeError(f"unexpected meaning-quiz change at {key}")
for name, before in [
    ("DEFAULT_VOCAB", vocab),
    ("GRAMMAR_DETAILS_BY_ID", grammar),
    ("VOCAB_AUDITED_PAIRS", pairs),
    ("REVIEWED_READING_OPTIONS", reading_overrides),
    ("VOCAB_KANA_EXAMPLE_TARGETS", kana_targets),
    ("REVIEWED_EXAMPLE_TARGETS", example_targets),
]:
    if extract_json_const(candidate, name)[3] != before:
        raise RuntimeError(f"protected block changed: {name}")

out_bytes = candidate.encode("utf-8")
OUT.write_bytes(out_bytes)
digest = hashlib.sha256(out_bytes).hexdigest()
blob_sha = hashlib.sha1(b"blob " + str(len(out_bytes)).encode() + b"\0" + out_bytes).hexdigest()

prepare = {
    "pass": True,
    "base_version": "v228",
    "base_main_sha": "bd66e3b3f01ae669bb4f3305d3f6652efb5d42f3",
    "base_html": BASE.name,
    "base_sha256": base_sha,
    "base_bytes": len(base_bytes),
    "candidate_version": "v229",
    "candidate_sha256": digest,
    "candidate_blob_sha": blob_sha,
    "candidate_bytes": len(out_bytes),
    "vocabulary_records": len(vocab),
    "grammar_records": len(grammar),
    "lexical_pairs": len(pairs),
    "unique_vocabulary_ids": len({int(x["id"]) for x in vocab}),
    "scope_ids": [2734, 544, 550, 552, 557, 588, 599, 644, 663, 1631, 3337, 3345],
    "pos_updates": {"2734": {"before": ["動詞"], "after": ["連体詞"]}},
    "detail_updates": {
        "644": ["examples[0]", "examples[1]", "exampleTranslations[0]", "exampleTranslations[1]", "usage"],
        "3345": ["examples[1]", "exampleTranslations[1]", "usage"]
    },
    "meaning_quiz_updates": {
        "v_3345": {"old_byExample_key": old_sentence, "new_byExample_key": new_sentence}
    },
    "protected": {
        "DEFAULT_VOCAB": True,
        "GRAMMAR_DETAILS_BY_ID": True,
        "VOCAB_AUDITED_PAIRS": True,
        "REVIEWED_READING_OPTIONS": True,
        "VOCAB_KANA_EXAMPLE_TARGETS": True,
        "REVIEWED_EXAMPLE_TARGETS": True,
        "storage_keys_and_learning_engine": "byte-identical outside the three JSON blocks and document title"
    },
    "exact_rollback": True,
    "full_card_credit_pending_browser_and_manual_quiz_review": True
}
(WORK / "prepare-results.json").write_text(json.dumps(prepare, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

updates = [
    {"op":"replace","block":"VOCAB_POS_BY_ID","path":["2734"],"before":["動詞"],"after":["連体詞"],"reason":"ID2734 examples are the lexicalized attributive きたる; the display/quiz POS map must not label it as ordinary 動詞."},
    {"op":"replace","block":"VOCAB_DETAILS_BY_ID","path":["644","examples","exampleTranslations","usage"],"before":{"examples":old_644["examples"],"exampleTranslations":old_644["exampleTranslations"],"usage":old_644["usage"]},"after":{"examples":new_details["644"]["examples"],"exampleTranslations":new_details["644"]["exampleTranslations"],"usage":new_details["644"]["usage"]}},
    {"op":"replace","block":"VOCAB_DETAILS_BY_ID","path":["3345","examples[1]","exampleTranslations[1]","usage"],"before":{"examples[1]":old_3345["examples"][1],"exampleTranslations[1]":old_3345["exampleTranslations"][1],"usage":old_3345["usage"]},"after":{"examples[1]":new_details["3345"]["examples"][1],"exampleTranslations[1]":new_details["3345"]["exampleTranslations"][1],"usage":new_details["3345"]["usage"]}},
    {"op":"replace","block":"REVIEWED_MEANING_QUIZZES","path":["v_3345","byExample",old_sentence],"before":old_payload,"after":by_example[new_sentence]}
]
(WORK / "updates.json").write_text(json.dumps(updates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
checkpoint = {
    "checkpoint": "v229-c11-pos-map",
    "created": "2026-11-14",
    "base_main_sha": prepare["base_main_sha"],
    "base_html": BASE.name,
    "base_html_sha256": base_sha,
    "scope": prepare["scope_ids"],
    "prior_checkpoint": "work/v229-c11-pos-map",
    "prior_main_status": "v228 published; 28 C11 blockers; author credit 3885/3914",
    "guardrails": [
        "retain 3914 vocabulary records, 130 grammar constructions, 859 lexical pairs and every stable ID",
        "no changes to DEFAULT_VOCAB, grammar, lexical pairs, reading overrides, target tables or learning algorithms",
        "no changes to progress-storage keys or state schema",
        "only ID2734 POS map and ID644/3345 content plus ID3345 byExample quiz payload are candidates",
        "do not force reading/cloze distractors where fewer than three valid choices exist",
        "keep v153 pilot credit limited to its documented ID121-320 scope"
    ],
    "status": "candidate prepared; awaiting Chromium and semantic quiz review before registry credit or publication",
    "candidate_sha256": digest,
    "candidate_blob_sha": blob_sha,
    "candidate_bytes": len(out_bytes)
}
(WORK / "checkpoint.json").write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(prepare, ensure_ascii=False, indent=2))
