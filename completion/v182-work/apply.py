import csv
import hashlib
import json
import re
from pathlib import Path

BASE = Path("JLPT_N1_ukrainian_reading_v181.html")
OUT = Path("JLPT_N1_ukrainian_reading_v182.html")
BASE_SHA256 = "32c6f482db1e98dd1f98deb0197324a037fbd1a1bae8d5dd4b4f7123f126da7f"
WORK = Path("completion/v182-work")
WORK.mkdir(parents=True, exist_ok=True)

OVERRIDES = {
    "255": {"word": "直接", "correct": "ちょくせつ", "wrong": ["ちょうせつ", "ちょうせい", "ちくせき"]},
    "327": {"word": "浮気", "correct": "うわき", "wrong": ["いしき", "いせき", "うつわ"]},
    "1819": {"word": "内訳", "correct": "うちわけ", "wrong": ["うちがわ", "うつわ", "うわき"]}
}

def extract_json_const(text, name):
    match = re.search(r"const " + re.escape(name) + r"\s*=\s*", text)
    if not match:
        raise RuntimeError(f"missing JS constant: {name}")
    start = match.end()
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
            continue
        if ch == '"':
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

def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()

base_bytes = BASE.read_bytes()
base_sha = sha256_bytes(base_bytes)
if base_sha != BASE_SHA256:
    raise RuntimeError(f"unexpected v181 base SHA-256: {base_sha}")
base = base_bytes.decode("utf-8")

_, _, _, vocab = extract_json_const(base, "DEFAULT_VOCAB")
_, _, _, grammar = extract_json_const(base, "GRAMMAR_DETAILS_BY_ID")
_, _, _, details = extract_json_const(base, "VOCAB_DETAILS_BY_ID")
pos_start, pos_end, pos_literal, pos = extract_json_const(base, "VOCAB_POS_BY_ID")
pairs_start, pairs_end, pairs_literal, pairs = extract_json_const(base, "VOCAB_AUDITED_PAIRS")
reading_start, reading_end, reading_literal, reading_overrides = extract_json_const(base, "REVIEWED_READING_OPTIONS")
_, _, _, meaning = extract_json_const(base, "REVIEWED_MEANING_QUIZZES")

if len(vocab) != 3914 or len(grammar) != 130 or len(pairs) != 859:
    raise RuntimeError("base record counts do not match approved scope")
ids = [str(x.get("id")) for x in vocab]
if len(set(ids)) != 3914 or len(pos) != 3914:
    raise RuntimeError("base vocabulary IDs or POS map are not unique/complete")
if pos.get("255") != ["名詞"] or pos.get("327") != ["名詞"] or pos.get("1819") != ["名詞"] or pos.get("359") != ["名詞", "ナ形"]:
    raise RuntimeError("base POS for the four reading-pool targets differs from v182 checkpoint")
if set(reading_overrides) != {"3005"}:
    raise RuntimeError("unexpected baseline reading overrides; refusing to overwrite active work")
if "v_2433" not in meaning:
    raise RuntimeError("v181 C11 meaning quiz for ID2433 is missing from base")

expected = {
    "255": ("直接", "ちょくせつ", ["名詞", "副詞"], ["詳細については、担当者に直接お問い合わせください。", "問題の直接の原因は、操作ミスにあった。"]),
    "327": ("浮気", "うわき", ["名詞", "ナ形"], ["浮気が原因で、夫婦関係が破綻した。", "浮気を疑われ、信頼を取り戻すのに長い時間を要した。"]),
    "1819": ("内訳", "うちわけ", ["名詞"], ["予算の内訳を示さなければ、議会の承認は得られない。", "参加者の内訳は、学生が六割、社会人が四割であった。"]),
    "359": ("本気", "ほんき", ["名詞", "ナ形"], ["彼が本気で取り組んだ結果、計画は予定よりも早く完了した。", "本気で変わろうとしなければ、組織は再生しない。"])
}
for key, (word, reading, new_pos, examples) in expected.items():
    item = next((x for x in vocab if str(x.get("id")) == key), None)
    detail = details.get(key)
    if not item or item.get("w") != word or item.get("r") != reading:
        raise RuntimeError(f"headword/reading mismatch for ID {key}")
    if not detail or detail.get("examples") != examples:
        raise RuntimeError(f"example mismatch for ID {key}")

new_pos_literal = pos_literal
for key, new_value in (("255", ["名詞", "副詞"]), ("327", ["名詞", "ナ形"])):
    old_fragment = json.dumps(key, ensure_ascii=False) + ":" + json.dumps(pos[key], ensure_ascii=False, separators=(",", ":"))
    new_fragment = json.dumps(key, ensure_ascii=False) + ":" + json.dumps(new_value, ensure_ascii=False, separators=(",", ":"))
    if new_pos_literal.count(old_fragment) != 1:
        raise RuntimeError(f"exact POS fragment not found once for ID {key}")
    new_pos_literal = new_pos_literal.replace(old_fragment, new_fragment, 1)

new_pos = json.loads(new_pos_literal)
if new_pos.get("255") != ["名詞", "副詞"] or new_pos.get("327") != ["名詞", "ナ形"]:
    raise RuntimeError("POS patch did not round-trip")
if len(new_pos) != 3914:
    raise RuntimeError("POS patch changed map size")

new_reading_literal = reading_literal[:-1] + "," + json.dumps(OVERRIDES, ensure_ascii=False, separators=(",", ":"))[1:-1] + "}"
new_reading = json.loads(new_reading_literal)
if len(new_reading) != 4 or new_reading.get("3005") != reading_overrides["3005"]:
    raise RuntimeError("reading override patch changed baseline entry or count")
for key, entry in OVERRIDES.items():
    item = next(x for x in vocab if str(x["id"]) == key)
    choices = [entry["correct"], *entry["wrong"]]
    if entry["word"] != item["w"] or entry["correct"] != item["r"]:
        raise RuntimeError(f"reading override target mismatch for ID {key}")
    if len(entry["wrong"]) != 3 or len(set(choices)) != 4:
        raise RuntimeError(f"reading override options are not four unique choices for ID {key}")
    for wrong in entry["wrong"]:
        if not any(x["r"] == wrong and str(x["id"]) != key for x in vocab):
            raise RuntimeError(f"reading distractor {wrong} is not an existing distinct vocabulary reading")

replacements = [
    (pos_start, pos_end, new_pos_literal),
    (reading_start, reading_end, new_reading_literal)
]
candidate = base
for start, end, replacement in sorted(replacements, key=lambda x: x[0], reverse=True):
    candidate = candidate[:start] + replacement + candidate[end:]

old_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v181</title>"
new_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v182</title>"
if candidate.count(old_title) != 1:
    raise RuntimeError("expected exact v181 title marker was not found once")
candidate = candidate.replace(old_title, new_title, 1)

reverse = candidate.replace(new_title, old_title, 1)
reverse = reverse.replace(new_pos_literal, pos_literal, 1)
reverse = reverse.replace(new_reading_literal, reading_literal, 1)
if reverse != base:
    raise RuntimeError("v182 patch is not exactly reversible to v181 base")

_, _, _, candidate_pos = extract_json_const(candidate, "VOCAB_POS_BY_ID")
_, _, _, candidate_reading = extract_json_const(candidate, "REVIEWED_READING_OPTIONS")
_, _, _, candidate_vocab = extract_json_const(candidate, "DEFAULT_VOCAB")
_, _, _, candidate_grammar = extract_json_const(candidate, "GRAMMAR_DETAILS_BY_ID")
_, _, _, candidate_pairs = extract_json_const(candidate, "VOCAB_AUDITED_PAIRS")
_, _, _, candidate_meaning = extract_json_const(candidate, "REVIEWED_MEANING_QUIZZES")
if len(candidate_vocab) != 3914 or len(candidate_grammar) != 130 or len(candidate_pairs) != 859:
    raise RuntimeError("candidate record counts changed")
if len(set(str(x["id"]) for x in candidate_vocab)) != 3914 or len(candidate_pos) != 3914:
    raise RuntimeError("candidate IDs or POS map are not unique/complete")
if candidate_pos["255"] != ["名詞", "副詞"] or candidate_pos["327"] != ["名詞", "ナ形"]:
    raise RuntimeError("candidate POS tags incorrect")
if candidate_reading != new_reading or len(candidate_reading) != 4:
    raise RuntimeError("candidate reading overrides incorrect")
if candidate_meaning != meaning:
    raise RuntimeError("v181 meaning quiz data changed unexpectedly")

out_bytes = candidate.encode("utf-8")
OUT.write_bytes(out_bytes)
digest = sha256_bytes(out_bytes)
prepare = {
    "pass": True,
    "base_version": "v181",
    "base_sha256": base_sha,
    "candidate_version": "v182",
    "candidate_sha256": digest,
    "candidate_bytes": len(out_bytes),
    "vocabulary_records": len(candidate_vocab),
    "unique_vocabulary_ids": 3914,
    "grammar_records": len(candidate_grammar),
    "lexical_pairs": len(candidate_pairs),
    "pos_entries": len(candidate_pos),
    "reading_overrides_before": len(reading_overrides),
    "reading_overrides_after": len(candidate_reading),
    "reviewed_meaning_quiz_entries": len(candidate_meaning),
    "pos_changes": {"255": {"before": ["名詞"], "after": ["名詞", "副詞"]}, "327": {"before": ["名詞"], "after": ["名詞", "ナ形"]}},
    "reading_overrides_added": OVERRIDES,
    "changed_blocks": ["VOCAB_POS_BY_ID.255", "VOCAB_POS_BY_ID.327", "REVIEWED_READING_OPTIONS.255/327/1819", "document title"],
    "unchanged": {
        "all_vocabulary_records": True,
        "all_vocabulary_ids": True,
        "grammar_records": True,
        "lexical_pairs": True,
        "vocab_details": True,
        "reviewed_meaning_quizzes": True,
        "learning_engine": True,
        "progress_storage_code": True
    },
    "exact_rollback": True,
    "card_credit_effect": "two pending cards fixed_rechecked after browser verification",
    "author_review_only": True
}
(WORK / "prepare-results.json").write_text(json.dumps(prepare, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(WORK / "updates.json").write_text(json.dumps([
    {"op": "replace", "block": "VOCAB_POS_BY_ID", "id": "255", "before": ["名詞"], "after": ["名詞", "副詞"], "evidence": "completion/v182-work/source-review.md"},
    {"op": "replace", "block": "VOCAB_POS_BY_ID", "id": "327", "before": ["名詞"], "after": ["名詞", "ナ形"], "evidence": "completion/v182-work/source-review.md"},
    {"op": "add", "block": "REVIEWED_READING_OPTIONS", "entries": OVERRIDES, "evidence": "completion/v182-work/reading-pool-review.tsv"}
], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

with Path("completion/v182-c10-review.tsv").open("w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f, delimiter="\t", lineterminator="\n")
    writer.writerow(["id", "word", "reading", "pos_before", "pos_after", "fields_rechecked", "decision", "source", "note"])
    writer.writerow(["255", "直接", "ちょくせつ", "名詞", "名詞|副詞", "definition; reading; 2 Japanese examples; 2 Ukrainian translations; usage", "fixed_rechecked", "NINJAL CHOKUSETSU entry", "直接 is 名・副; 直接的 is 形動. The examples support adverbial and noun use."])
    writer.writerow(["327", "浮気", "うわき", "名詞", "名詞|ナ形", "definition; reading; 2 Japanese examples; 2 Ukrainian translations; usage", "fixed_rechecked", "Kotobank Digital Daijisen", "浮気 is 名・形動; ふき is a separate historical reading and is not used as a distractor."])

with Path("completion/v182-acceptance.tsv").open("w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f, delimiter="\t", lineterminator="\n")
    writer.writerow(["object_type", "id", "decision", "credit_effect", "evidence"])
    writer.writerow(["vocab", "255", "fixed_rechecked", "+1 accepted vocabulary card", "completion/v182-c10-review.tsv#255"])
    writer.writerow(["vocab", "327", "fixed_rechecked", "+1 accepted vocabulary card", "completion/v182-c10-review.tsv#327"])
    writer.writerow(["reviewed_reading_quiz", "r_255", "reviewed", "no additional card credit", "completion/v182-reading-pool-review.tsv#255"])
    writer.writerow(["reviewed_reading_quiz", "r_327", "reviewed", "no additional card credit", "completion/v182-reading-pool-review.tsv#327"])
    writer.writerow(["reviewed_reading_quiz", "r_1819", "reviewed", "no additional card credit", "completion/v182-reading-pool-review.tsv#1819"])

checkpoint = json.loads((WORK / "checkpoint.json").read_text(encoding="utf-8"))
checkpoint.update({
    "status": "candidate prepared; awaiting Chromium verification",
    "candidate_html": "JLPT_N1_ukrainian_reading_v182.html",
    "candidate_sha256": digest,
    "candidate_bytes": len(out_bytes),
    "card_credit_effect": "+2 fixed_rechecked",
    "reading_quiz_objects": 3
})
(WORK / "checkpoint.json").write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(prepare, ensure_ascii=False, indent=2))
