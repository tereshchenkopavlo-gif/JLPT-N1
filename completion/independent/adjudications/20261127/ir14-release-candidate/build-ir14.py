"""Apply the independently reviewed IR14 question to the pinned trainer."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

baseline, package, output = map(Path, sys.argv[1:])
html = baseline.read_bytes().decode()
assert hashlib.sha256(html.encode()).hexdigest() == "6fe18a574b0fa9a4f11c20bd6cacefb3142c6c9c28907cc8a159dc62c500bf41"
case, = json.loads(package.read_text())["cases"]
reviewed = case["fields"]
start = re.search(r"const readingBank = ", html).end()
bank, end = json.JSONDecoder().raw_decode(html, start)
reading = next(row for row in bank["long"] if row.get("id") == case["case_id"])
assert all(reading[key] == value for key, value in reviewed.items() if key != "questions")
before, after = reading["questions"][1], reviewed["questions"][1]
assert set(before) == set(after)
assert {key for key in before if before[key] != after[key]} == {"choices", "explain"}
assert len(after["choices"]) == len(set(after["choices"])) == 4
assert after["evidence"] in reading["ja"]
assert all(question == reviewed["questions"][index]
           for index, question in enumerate(reading["questions"]) if index != 1)
encode = lambda value: json.dumps(value, ensure_ascii=False, separators=(",", ":"))
old_question, new_question = map(encode, (before, after))
block = html[start:end]
assert block.count(old_question) == 1 and new_question not in block
updated = block.replace(old_question, new_question, 1)
reading["questions"][1] = after
assert json.loads(updated) == bank
assert updated.replace(new_question, old_question, 1) == block
candidate = html[:start] + updated + html[end:]
for script in re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", candidate, re.S):
    subprocess.run(["node", "--check"], input=script, text=True, check=True)
output.write_bytes(candidate.encode())
print(hashlib.sha256(output.read_bytes()).hexdigest())
