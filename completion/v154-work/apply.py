"""Apply the reviewed translation and pilot field batches to the exact v153 HTML."""
import csv
from hashlib import sha256
import json
from pathlib import Path
import sys

source, target = map(Path, sys.argv[1:])
if source.resolve() == target.resolve():
    raise ValueError("Use a separate output path")
raw = source.read_bytes()
if sha256(raw).hexdigest() != "35d68dd5c3ba2c02f0da6881fe33e356439ae53f664038799ac0a1aa74dc120d":
    raise ValueError("Expected the published v153 HTML")

html = raw.decode("utf-8")
marker = "const VOCAB_DETAILS_BY_ID = "
start = html.index(marker) + len(marker)
cards, end = json.JSONDecoder().raw_decode(html, start)
def compact(value, *, sort_keys=False):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=sort_keys)

if compact(cards) != html[start:end]:
    raise ValueError("Unexpected vocabulary serialization")

ledger = Path(__file__).with_name("translations.tsv")
seen = set()
with ledger.open(encoding="utf-8", newline="") as file:
    for edit in csv.DictReader(file, delimiter="\t"):
        key = edit["id"]
        card = cards[key]
        index = int(edit["index"])
        if key in seen or index not in (0, 1) or card["w"] != edit["headword"]:
            raise ValueError(f"Invalid target {key}")
        if sha256(compact(card, sort_keys=True).encode()).hexdigest() != edit["before_sha256"]:
            raise ValueError(f"Unexpected original card {key}")
        translation = edit["translation"]
        if not translation.strip() or translation == card["exampleTranslations"][index]:
            raise ValueError(f"Invalid translation for {key}")
        card["exampleTranslations"][index] = translation
        seen.add(key)

if len(seen) != 52:
    raise ValueError("Expected 52 translations")

pilot_ledger = Path(__file__).with_name("pilot-fields.tsv")
pilot_seen = set()
with pilot_ledger.open(encoding="utf-8", newline="") as file:
    for edit in csv.DictReader(file, delimiter="\t"):
        key = edit["id"]
        card = cards[key]
        field = edit["field"]
        if key in seen or key in pilot_seen or field not in {"m", "t"} or card["w"] != edit["headword"]:
            raise ValueError(f"Invalid pilot target {key}")
        if sha256(compact(card, sort_keys=True).encode()).hexdigest() != edit["before_sha256"]:
            raise ValueError(f"Unexpected original pilot card {key}")
        value = edit["value"]
        if not value.strip() or value == card[field]:
            raise ValueError(f"Invalid pilot field for {key}")
        card[field] = value
        pilot_seen.add(key)

if pilot_seen != {"254", "291", "293", "1567", "1570", "1572", "1589", "1604"}:
    raise ValueError("Unexpected pilot scope")
updated = html[:start] + compact(cards) + html[end:]
quiz_marker = "const REVIEWED_MEANING_QUIZZES = "
quiz_start = updated.index(quiz_marker) + len(quiz_marker)
quizzes, quiz_end = json.JSONDecoder().raw_decode(updated, quiz_start)
if compact(quizzes) != updated[quiz_start:quiz_end]:
    raise ValueError("Unexpected quiz serialization")
quizzes["v_293"]["correct"] = cards["293"]["m"]
result = (updated[:quiz_start] + compact(quizzes) + updated[quiz_end:]).encode()
with target.open("xb") as file:
    file.write(result)
print(sha256(result).hexdigest(), len(result))
