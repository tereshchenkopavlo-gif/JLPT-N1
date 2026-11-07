"""Apply and validate the reviewed v156 candidate against the exact v155."""
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys

source, target = map(Path, sys.argv[1:3])
raw = source.read_bytes()
if sha256(raw).hexdigest() != "39a765cc1b0e7e24ac353b06a647218db86fc99a790c99979ca12539b5a6d6d8":
    raise ValueError("Expected published v155")
if source.resolve() == target.resolve():
    raise ValueError("Use a separate checkpoint path")
original = raw.decode("utf-8")
updates = json.loads(Path(__file__).with_name("updates.json").read_text())
if len(updates) != 17:
    raise ValueError("Expected 17 reviewed fields")

def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

def block(html, name):
    match = re.search(r"const " + name + r"\s*=\s*", html)
    if match is None:
        raise ValueError(name)
    start = match.end()
    value, end = json.JSONDecoder().raw_decode(html, start)
    if compact(value) != html[start:end]:
        raise ValueError("Unexpected serialization")
    return value, start, end

html = original
seen = set()
for edit in updates:
    name, path = edit["block"], edit["path"]
    identity = (name, compact(path))
    if identity in seen or name not in {"VOCAB_DETAILS_BY_ID", "AUTO_VOCAB_COMPARISONS", "VOCAB_POS_BY_ID", "VOCAB_AUDITED_PAIRS"}:
        raise ValueError("Invalid field")
    value, start, end = block(html, name)
    parent = value
    for key in path[:-1]:
        parent = parent[key]
    if parent[path[-1]] != edit["before"] or edit["before"] == edit["after"]:
        raise ValueError("Unexpected original field")
    parent[path[-1]] = edit["after"]
    html = html[:start] + compact(value) + html[end:]
    seen.add(identity)

old_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v155</title>"
new_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v156</title>"
if html.count(old_title) != 1:
    raise ValueError("Unexpected title")
html = html.replace(old_title, new_title, 1)

restored = html.replace(new_title, old_title, 1)
for edit in reversed(updates):
    value, start, end = block(restored, edit["block"])
    parent = value
    for key in edit["path"][:-1]:
        parent = parent[key]
    if parent[edit["path"][-1]] != edit["after"]:
        raise ValueError("Unexpected changed field")
    parent[edit["path"][-1]] = edit["before"]
    restored = restored[:start] + compact(value) + restored[end:]
if restored != original:
    raise ValueError("Changes exceed reviewed scope")
cards = block(html, "VOCAB_DETAILS_BY_ID")[0]
if len(cards) != 3914 or len(block(html, "GRAMMAR_DETAILS_BY_ID")[0]) != 130:
    raise ValueError("Unexpected record counts")
if list(cards) != list(block(original, "VOCAB_DETAILS_BY_ID")[0]):
    raise ValueError("IDs changed")
scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", html, re.S)
if not scripts:
    raise ValueError("Missing script")
for script in scripts:
    subprocess.run(["node", "--check", "-"], input=script, text=True, check=True)

render_targets = []
for edit in updates:
    if len(edit["path"]) == 3 and edit["path"][1] == "exampleTranslations":
        key, _, index = edit["path"]
        render_targets.append([key, index, cards[key]])
functions = re.search(r"function escapeLex\(.*?(?=const STUDY_SECTION_LABELS)", html, re.S)[0]
probe = "const assert=require('node:assert/strict'); const VOCAB_DETAILS_BY_ID={};\n" + functions
probe += "\nfor(const [id,index,card] of " + json.dumps(render_targets, ensure_ascii=False) + """){
 VOCAB_DETAILS_BY_ID[id]=card;
 const result=vocabExamplesHtml(id,card.examples);
 assert(result.includes(escapeLex(card.examples[index])));
 assert(result.includes(escapeLex(card.exampleTranslations[index])));
}
"""
subprocess.run(["node", "-"], input=probe, text=True, check=True)
result = html.encode("utf-8")
with target.open("xb") as file:
    file.write(result)
print(json.dumps(dict(sha256=sha256(result).hexdigest(), bytes=len(result),
                     reviewed_fields=len(updates), translation_renders=len(render_targets),
                     scripts_checked=len(scripts), exact_rollback=True)))
