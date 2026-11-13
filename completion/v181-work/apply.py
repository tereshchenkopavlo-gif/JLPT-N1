import csv
import hashlib
import json
import re
from pathlib import Path

BASE = Path("JLPT_N1_ukrainian_reading_v179.html")
OUT = Path("JLPT_N1_ukrainian_reading_v181.html")
BASE_SHA256 = "359490152e9d4c7ae86cc746e2b69d132922946767890bc7aa7be6f5cdef2ba8"
WORK = Path("completion/v181-work")
WORK.mkdir(parents=True, exist_ok=True)

SENTENCES = [
    "市の中心部には、高さ二百メートルの超高層ビルがそびえている。",
    "雪をいただいた山々が、湖の向こうにそびえて見える。"
]
PAYLOADS = {
    SENTENCES[0]: {
        "correct": "建物などが、非常に高く立っていること。",
        "wrong": [
            "建物などが、低い位置に建っていること。",
            "建物などが、地面に沿って横に長く広がること。",
            "建物などが、地面の下に建てられていること。"
        ],
        "note": "У цьому реченні そびえる описує дуже високу вертикальну споруду. Інші варіанти описують низьку будівлю, довгу горизонтальну забудову або підземну споруду."
    },
    SENTENCES[1]: {
        "correct": "山などが、非常に高く立っていること。",
        "wrong": [
            "山などが、低い谷間に沈んで見えること。",
            "山などが、低い丘のように丸くなだらかに見えること。",
            "山などが、周囲の地面と同じ高さで平らに続くこと。"
        ],
        "note": "Тут そびえる означає, що гори високо здіймаються над місцевістю за озером. Інші варіанти описують низину, невисокий пагорб або пласку рівнину."
    }
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
    raise RuntimeError(f"unexpected base HTML SHA-256: {base_sha}")
base = base_bytes.decode("utf-8")

_, _, _, vocab = extract_json_const(base, "DEFAULT_VOCAB")
_, _, _, grammar = extract_json_const(base, "GRAMMAR_DETAILS_BY_ID")
_, _, _, details = extract_json_const(base, "VOCAB_DETAILS_BY_ID")
_, _, _, pos = extract_json_const(base, "VOCAB_POS_BY_ID")
_, _, _, pairs = extract_json_const(base, "VOCAB_AUDITED_PAIRS")
_, _, _, reading_overrides = extract_json_const(base, "REVIEWED_READING_OPTIONS")
meaning_start, meaning_end, meaning_literal, meaning = extract_json_const(base, "REVIEWED_MEANING_QUIZZES")

if len(vocab) != 3914 or len(grammar) != 130 or len(pairs) != 859:
    raise RuntimeError("base record counts do not match the approved scope")
if "v_2433" in meaning:
    raise RuntimeError("ID2433 already has a saved meaning quiz; refusing duplicate work")

item = next((x for x in vocab if str(x.get("id")) == "2433"), None)
detail = details.get("2433")
if not item or item.get("w") != "そびえる" or item.get("r") != "そびえる":
    raise RuntimeError("ID2433 headword/reading differs from the reviewed target")
if not detail or detail.get("examples") != SENTENCES:
    raise RuntimeError("ID2433 examples differ from the exact reviewed sentences")
if pos.get("2433") != ["動詞"]:
    raise RuntimeError("ID2433 POS changed from the expected baseline")
if reading_overrides != {"3005": {"word": "著しい", "correct": "いちじるしい", "wrong": ["いちずるしい", "いちじらしい", "いちじろしい"]}}:
    raise RuntimeError("reading overrides differ from the verified v179 baseline")

entry = {"byExample": PAYLOADS}
addition = "," + json.dumps({"v_2433": entry}, ensure_ascii=False, separators=(",", ":"))[1:-1]
new_meaning_literal = meaning_literal[:-1] + addition + "}"
candidate = base[:meaning_start] + new_meaning_literal + base[meaning_end:]
old_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v179</title>"
new_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v181</title>"
if candidate.count(old_title) != 1:
    raise RuntimeError("expected exact v179 title marker was not found once")
candidate = candidate.replace(old_title, new_title, 1)

reverse = candidate.replace(new_title, old_title, 1)
reverse = reverse.replace(new_meaning_literal, meaning_literal, 1)
if reverse != base:
    raise RuntimeError("v181 patch is not exactly reversible to the v179 base")

_, _, _, candidate_meaning = extract_json_const(candidate, "REVIEWED_MEANING_QUIZZES")
if candidate_meaning.get("v_2433") != entry or len(candidate_meaning) != len(meaning) + 1:
    raise RuntimeError("saved ID2433 meaning payload did not round-trip")
for sentence, payload in PAYLOADS.items():
    choices = [payload["correct"], *payload["wrong"]]
    if len(payload["wrong"]) != 3 or len(set(choices)) != 4:
        raise RuntimeError(f"non-unique or incomplete options for {sentence}")
    if any(not x for x in choices) or not payload["note"]:
        raise RuntimeError(f"empty quiz field for {sentence}")

out_bytes = candidate.encode("utf-8")
OUT.write_bytes(out_bytes)
digest = sha256_bytes(out_bytes)
prepare = {
    "pass": True,
    "base_version": "v179",
    "base_sha256": base_sha,
    "base_bytes": len(base_bytes),
    "candidate_version": "v181",
    "candidate_sha256": digest,
    "candidate_bytes": len(out_bytes),
    "vocabulary_records": len(vocab),
    "grammar_records": len(grammar),
    "lexical_pairs": len(pairs),
    "meaning_quiz_entries_before": len(meaning),
    "meaning_quiz_entries_after": len(candidate_meaning),
    "added_entries": 1,
    "context_payloads": 2,
    "changed_blocks": ["REVIEWED_MEANING_QUIZZES.v_2433", "document title"],
    "unchanged": {
        "vocabulary_records": True,
        "grammar_records": True,
        "lexical_pairs": True,
        "all_ids": True,
        "VOCAB_POS_BY_ID": True,
        "REVIEWED_READING_OPTIONS": True,
        "learning_engine": True,
        "progress_storage_code": True
    },
    "exact_rollback": True,
    "no_card_credit": True,
    "author_review_only": True
}
(WORK / "prepare-results.json").write_text(json.dumps(prepare, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(WORK / "updates.json").write_text(json.dumps([{
    "op": "add",
    "block": "REVIEWED_MEANING_QUIZZES",
    "path": ["v_2433", "byExample"],
    "before": None,
    "after": PAYLOADS,
    "evidence": "completion/v181-work/source-review.md"
}], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

with Path("completion/v181-c11-review.tsv").open("w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f, delimiter="\t", lineterminator="\n")
    writer.writerow(["id", "headword", "example_index", "example", "decision", "correct", "wrong_1", "wrong_2", "wrong_3", "note", "boundary"])
    for index, sentence in enumerate(SENTENCES):
        p = PAYLOADS[sentence]
        writer.writerow(["2433", "そびえる", index, sentence, "reviewed_saved_contextual_quiz", p["correct"], *p["wrong"], p["note"], "author review; not independent; cloze unavailable before and after"])
with Path("completion/v181-acceptance.tsv").open("w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f, delimiter="\t", lineterminator="\n")
    writer.writerow(["object_type", "id", "contexts", "decision", "credit_effect", "evidence"])
    writer.writerow(["reviewed_meaning_quiz", "v_2433", "2", "reviewed", "no full-card credit", "completion/v181-c11-review.tsv"])

checkpoint = json.loads((WORK / "checkpoint.json").read_text(encoding="utf-8"))
checkpoint.update({
    "status": "candidate prepared; awaiting Chromium verification",
    "candidate_html": "JLPT_N1_ukrainian_reading_v181.html",
    "candidate_sha256": digest,
    "candidate_bytes": len(out_bytes),
    "meaning_quiz_entries_added": 1,
    "context_payloads_added": 2,
    "card_credit_changed": False
})
(WORK / "checkpoint.json").write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(prepare, ensure_ascii=False, indent=2))
