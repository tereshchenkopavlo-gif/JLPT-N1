"""Replay the previously reviewed C11 payloads onto the current C12 release."""
import json
import re
from pathlib import Path
import sys
import hashlib

base_path, gate_path, v230_path, v231_path, output = map(Path, sys.argv[1:])
base = base_path.read_bytes().decode()
assert hashlib.sha256(base.encode()).hexdigest() == "d4605e825f2724986ab128930bb010074d3254dcb4e4569cd7632b6da641e1ef"
gate = gate_path.read_bytes().decode()
candidate = base
original_pos = {}

for block, field in (("VOCAB_POS_BY_ID", "pos"), ("REVIEWED_MEANING_QUIZZES", "quizzes")):
    match = re.search(rf"^const {block} = (.+);$", candidate, re.M)
    values = json.loads(match[1])
    for path in (v230_path, v231_path):
        for key, value in json.loads(path.read_text())[field].items():
            if field == "pos":
                original_pos[key] = values[key]
            values[key] = value
    candidate = candidate[:match.start(1)] + json.dumps(values, ensure_ascii=False) + candidate[match.end(1):]

marker = "const REVIEWED_READING_OPTIONS ="
cloze = gate[gate.index("const REVIEWED_CLOZE_QUIZZES ="):gate.index(marker)]
assert cloze.startswith("const REVIEWED_CLOZE_QUIZZES = {};")
candidate = candidate.replace(marker, cloze + marker, 1)
for needle in ("types.push('cloze')", "const wrong = shuffleArray(clozeCandidates"):
    old, = [line for line in candidate.splitlines() if needle in line]
    new, = [line for line in gate.splitlines() if ("types.push('cloze')" if "types.push" in needle else "const wrong = reviewedCloze ?") in line]
    if "types.push" in needle:
        new = "        const reviewedCloze=reviewedClozeOptions(it,ex);\n" + new
    candidate = candidate.replace(old, new, 1)

start = candidate.index("function quizReadingOptions(")
end = candidate.index("function readingGlossaryEntryHtml(", start)
selectors = candidate[start:end]
assert selectors.count("vocabPartOfSpeech(") == 4
compat = (
    "const EXERCISE_POS_OVERRIDES = " + json.dumps(original_pos, ensure_ascii=False) + ";\n"
    "function exercisePartOfSpeech(id) {\n"
    "  return EXERCISE_POS_OVERRIDES[String(id)] ?? vocabPartOfSpeech(id);\n"
    "}\n"
)
candidate = candidate[:start] + compat + selectors.replace("vocabPartOfSpeech(", "exercisePartOfSpeech(") + candidate[end:]
output.write_bytes(candidate.encode())
