#!/usr/bin/env python3
"""Apply the exact, pre-adjudicated C10 corrections to the immutable v171 baseline."""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys

SOURCE = Path("JLPT_N1_ukrainian_reading_v171.html")
TARGET = Path("JLPT_N1_ukrainian_reading_v172.html")
BASE_SHA256 = "80f557ef2951c3557178f12537e67440d80e35c66d7daaa84a1407f161777d32"
UPDATES = Path(__file__).with_name("updates.json")

def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

def block(html, name):
    match = re.search(r"const " + re.escape(name) + r"\s*=\s*", html)
    if match is None:
        raise ValueError(f"Missing block {name}")
    start = match.end()
    value, end = json.JSONDecoder().raw_decode(html, start)
    if compact(value) != html[start:end]:
        raise ValueError(f"Unexpected serialization in {name}")
    return value, start, end

def parent_at(value, path):
    parent = value
    for key in path[:-1]:
        parent = parent[key]
    return parent, path[-1]

def apply_one(html, edit, reverse=False):
    value, start, end = block(html, edit["block"])
    op = edit["op"]
    if op == "set":
        parent, key = parent_at(value, edit["path"])
        before = edit["after"] if reverse else edit["before"]
        after = edit["before"] if reverse else edit["after"]
        if parent[key] != before or before == after:
            raise ValueError(f"Unexpected field value: {edit['block']} {edit['path']}")
        parent[key] = after
    elif op == "rename_key":
        parent = value
        for key in edit["path"]:
            parent = parent[key]
        old_key = edit["new_key"] if reverse else edit["old_key"]
        new_key = edit["old_key"] if reverse else edit["new_key"]
        before_value = edit["after_value"] if reverse else edit["before_value"]
        after_value = edit["before_value"] if reverse else edit["after_value"]
        if old_key not in parent or parent[old_key] != before_value or new_key in parent:
            raise ValueError("Unexpected kana-target key")
        # Replace the key at its original insertion position so reverse application
        # restores the exact serialized JSON, not merely an equivalent mapping.
        items = list(parent.items())
        parent.clear()
        for key, item_value in items:
            if key == old_key:
                parent[new_key] = after_value
            else:
                parent[key] = item_value
    else:
        raise ValueError(f"Unknown operation {op}")
    return html[:start] + compact(value) + html[end:]

def main():
    raw = SOURCE.read_bytes()
    if sha256(raw).hexdigest() != BASE_SHA256:
        raise ValueError("The published v171 baseline changed")
    original = raw.decode("utf-8")
    edits = json.loads(UPDATES.read_text(encoding="utf-8"))
    if len(edits) != 17:
        raise ValueError("Expected 17 exact field/key operations")
    html = original
    seen = set()
    for edit in edits:
        identity = (edit["block"], json.dumps(edit.get("path", []), ensure_ascii=False), edit["op"])
        if identity in seen:
            raise ValueError("Duplicate update operation")
        html = apply_one(html, edit)
        seen.add(identity)
    old_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v171</title>"
    new_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v172</title>"
    if html.count(old_title) != 1:
        raise ValueError("Unexpected v171 title")
    html = html.replace(old_title, new_title, 1)

    restored = html.replace(new_title, old_title, 1)
    for edit in reversed(edits):
        restored = apply_one(restored, edit, reverse=True)
    if restored != original:
        raise ValueError("Changes exceed the reviewed field/key scope")

    vocab, _, _ = block(html, "VOCAB_DETAILS_BY_ID")
    grammar, _, _ = block(html, "GRAMMAR_DETAILS_BY_ID")
    pos, _, _ = block(html, "VOCAB_POS_BY_ID")
    targets, _, _ = block(html, "VOCAB_KANA_EXAMPLE_TARGETS")
    before_vocab, _, _ = block(original, "VOCAB_DETAILS_BY_ID")
    before_grammar, _, _ = block(original, "GRAMMAR_DETAILS_BY_ID")
    before_pos, _, _ = block(original, "VOCAB_POS_BY_ID")
    if len(vocab) != 3914 or len(grammar) != 130 or list(vocab) != list(before_vocab):
        raise ValueError("Record counts or IDs changed")
    if list(grammar) != list(before_grammar) or list(pos) != list(before_pos):
        raise ValueError("Grammar IDs or POS map keys changed")
    if pos["3742"] != ["名詞"]:
        raise ValueError("ID3742 POS was not corrected")
    new_sentence = "開通の日を指折り数えて待つ住民が、駅前に集まっていた。"
    if targets["指を折る"].get(new_sentence) != "指折り数えて":
        raise ValueError("ID3757 target is not bound to the revised sentence")

    scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", html, re.S)
    if not scripts:
        raise ValueError("Missing inline scripts")
    for script in scripts:
        subprocess.run(["node", "--check", "-"], input=script, text=True, check=True)

    render_targets = []
    for edit in edits:
        if edit["op"] == "set" and edit["block"] == "VOCAB_DETAILS_BY_ID" and len(edit["path"]) == 3 and edit["path"][1] == "exampleTranslations":
            render_targets.append([edit["path"][0], edit["path"][2], vocab[edit["path"][0]]])
    functions = re.search(r"function escapeLex\(.*?(?=const STUDY_SECTION_LABELS)", html, re.S)
    if functions is None:
        raise ValueError("Could not isolate example rendering functions")
    probe = "const VOCAB_DETAILS_BY_ID={}; const VOCAB_KANA_EXAMPLE_TARGETS=" + compact(targets) + ";\n"
    probe += functions.group(0)
    probe += "\nconst assert=require('node:assert/strict');\n"
    probe += "for(const [id,index,card] of " + json.dumps(render_targets, ensure_ascii=False) + "){\n"
    probe += " VOCAB_DETAILS_BY_ID[id]=card; const result=vocabExamplesHtml(id,card.examples);\n"
    probe += " assert(result.includes(escapeLex(card.examples[index]))); assert(result.includes(escapeLex(card.exampleTranslations[index])));\n}\n"
    subprocess.run(["node", "-"], input=probe, text=True, check=True)

    result = html.encode("utf-8")
    if TARGET.exists() and TARGET.read_bytes() != result:
        raise ValueError("Existing v172 checkpoint differs from deterministic output")
    TARGET.write_bytes(result)
    report = {
        "base_sha256": BASE_SHA256,
        "checkpoint_sha256": sha256(result).hexdigest(),
        "checkpoint_bytes": len(result),
        "vocabulary_records": len(vocab),
        "grammar_records": len(grammar),
        "operations": len(edits),
        "cards_corrected": 13,
        "rendered_example_translations": len(render_targets),
        "scripts_checked": len(scripts),
        "exact_rollback": True,
        "pass": True
    }
    Path("completion/v172-work/prepare-results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))

if __name__ == "__main__":
    main()
