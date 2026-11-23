"""Check package data before sending it for independent language review."""
import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

from importlib import import_module

tools = import_module("sync-reviews")
nonempty = tools.importer["nonempty"]


def normalize(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split()).rstrip("。.!?！？")


def inspect(cases, require_questions=True):
    errors, signals = [], []
    identifiers, texts = set(), set()
    wrong_choices = Counter()
    for case in cases:
        cid, fields = case["case_id"], case["fields"]
        if cid in identifiers:
            errors.append(f"{cid}: duplicate case")
        identifiers.add(cid)
        if case["kind"] == "reading":
            passage = fields.get("ja", "")
            required = ("title", "ja", "uk") if require_questions else ("ja", "uk")
            for key in required:
                if not nonempty(fields.get(key)):
                    errors.append(f"{cid}: missing {key}")
            if not isinstance(passage, str):
                continue
            if normalize(passage) in texts:
                errors.append(f"{cid}: duplicate passage")
            texts.add(normalize(passage))
            translation = fields.get("uk")
            if nonempty(translation) and not re.search("[А-Яа-яІіЇїЄєҐґ]", translation):
                signals.append(f"{cid}: translation lacks Cyrillic")
            questions = fields.get("questions")
            if questions is None and not require_questions:
                continue
            if not isinstance(questions, list) or (require_questions and not questions):
                errors.append(f"{cid}: missing questions")
                continue
            prompts = set()
            for index, question in enumerate(questions):
                label = f"{cid}/questions[{index}]"
                if not isinstance(question, dict):
                    errors.append(f"{label}: invalid question")
                    continue
                for key in ("prompt", "explain"):
                    if not nonempty(question.get(key)):
                        errors.append(f"{label}: missing {key}")
                prompt = question.get("prompt")
                if nonempty(prompt):
                    if normalize(prompt) in prompts:
                        errors.append(f"{label}: duplicate prompt")
                    prompts.add(normalize(prompt))
                quote = question.get("evidence")
                if not nonempty(quote) or quote not in passage:
                    errors.append(f"{label}: evidence is not an exact passage quote")
                check_choices(label, question.get("choices"), question.get("answer"), errors, signals, wrong_choices)
            notes = fields.get("contextNotes")
            if not isinstance(notes, list):
                errors.append(f"{cid}: invalid contextNotes")
                continue
            for note in notes:
                quote = note.get("quote") if isinstance(note, dict) else None
                if not nonempty(quote) or quote not in passage or not nonempty(note.get("meaning")):
                    errors.append(f"{cid}: invalid context note quote or translation")
        elif case["kind"] == "vocab":
            details = fields.get("details", {})
            examples = details.get("examples", [])
            translations = details.get("exampleTranslations", [])
            if not isinstance(examples, list) or not isinstance(translations, list) or len(examples) != len(translations) or not all(map(nonempty, translations)):
                errors.append(f"{cid}: example translation alignment")
            for index, (context, item) in enumerate(fields.get("meaning_quiz", {}).get("byExample", {}).items()):
                label = f"{cid}/meaning_quiz[{index}]"
                if context not in examples:
                    errors.append(f"{label}: context absent from examples")
                if not isinstance(item.get("wrong"), list):
                    errors.append(f"{label}: invalid distractors")
                    continue
                check_choices(label, [item.get("correct"), *item["wrong"]], 0, errors, signals, wrong_choices)
        else:
            errors.append(f"{cid}: unknown case kind")
    for choice, count in sorted(wrong_choices.items()):
        if count >= 3:
            signals.append(f"Repeated distractor ({count} occurrences): {choice}")
    return {"cases": len(cases), "errors": errors, "signals": signals, "linguistic_credit": False}


def check_choices(label, choices, key, errors, signals, wrong_choices):
    if not isinstance(choices, list) or len(choices) != 4 or not all(map(nonempty, choices)):
        errors.append(f"{label}: expected four nonempty choices")
        return
    if type(key) is not int or not 0 <= key < len(choices):
        errors.append(f"{label}: invalid answer index")
        return
    cleaned = list(map(normalize, choices))
    if not all(cleaned) or len(set(cleaned)) != 4:
        errors.append(f"{label}: duplicate or empty normalized choices")
    distractors = [choice for index, choice in enumerate(cleaned) if index != key]
    wrong_choices.update(distractors)
    lengths = sorted(map(len, distractors))
    if len(cleaned[key]) > 1.6 * lengths[-1] or 1.6 * len(cleaned[key]) < lengths[0]:
        signals.append(f"{label}: key length differs substantially")
    markers = ("必ず", "すべて", "全て", "一人で", "一切", "決して", "どんな", "だけで")
    if all(any(marker in choice for marker in markers) for choice in distractors):
        if not any(marker in cleaned[key] for marker in markers):
            signals.append(f"{label}: all distractors contain categorical wording")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("packages", type=Path, nargs="+")
    args = parser.parse_args()
    results = []
    for path in args.packages:
        package = tools.load_json(path.read_bytes())
        require_questions = package.get("scope", {}).get("reading_questions", 0) > 0
        results.append(inspect(package["cases"], require_questions=require_questions))
    result = {
        "cases": sum(item["cases"] for item in results),
        "errors": [error for item in results for error in item["errors"]],
        "signals": [signal for item in results for signal in item["signals"]],
        "linguistic_credit": False,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(bool(result["errors"]))


if __name__ == "__main__":
    main()
