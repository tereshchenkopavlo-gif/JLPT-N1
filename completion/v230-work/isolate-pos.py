"""Apply the C11 exercise-POS compatibility change to a built v230 HTML."""

import json
import re
from pathlib import Path

BASE = Path("JLPT_N1_ukrainian_reading_v229.html")
CANDIDATE = Path("JLPT_N1_ukrainian_reading_v230.html")
PINNED_IDS = (3363, 3375, 3417, 3441, 3444, 3525, 3561, 3565,
              3569, 3594, 3636, 3646, 3652, 3677, 3679)


def main():
    baseline = BASE.read_bytes().decode("utf-8")
    candidate = CANDIDATE.read_bytes().decode("utf-8")
    baseline_pos = json.loads(re.search(
        r"^const VOCAB_POS_BY_ID = (.+);$", baseline, re.MULTILINE
    ).group(1))
    pinned = {str(i): baseline_pos[str(i)] for i in PINNED_IDS}
    start = candidate.index("function quizReadingOptions(")
    end = candidate.index("function readingGlossaryEntryHtml(", start)
    selectors = candidate[start:end]
    assert selectors.count("vocabPartOfSpeech(") == 4
    compatibility = (
        "// Preserve v229 exercise pools for the C11 display-POS corrections.\n"
        f"const EXERCISE_POS_OVERRIDES = {json.dumps(pinned, ensure_ascii=False)};\n"
        "function exercisePartOfSpeech(id) {\n"
        "  return EXERCISE_POS_OVERRIDES[String(id)] ?? vocabPartOfSpeech(id);\n"
        "}\n"
    )
    revised = (candidate[:start] + compatibility
               + selectors.replace("vocabPartOfSpeech(", "exercisePartOfSpeech(")
               + candidate[end:])
    CANDIDATE.write_bytes(revised.encode("utf-8"))


if __name__ == "__main__":
    main()
