"""Build the isolated ID1510 translation candidate from C12ab."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

base, output = map(Path, sys.argv[1:])
raw = base.read_bytes()
assert hashlib.sha256(raw).hexdigest() == "c76aeb70f628123e35766055c5bcbc3e9f542b1c39f578405f7df32879458707"
html = raw.decode()
start = re.search(r"const VOCAB_DETAILS_BY_ID\s*=\s*", html).end()
details, end = json.JSONDecoder().raw_decode(html, start)
before = "подвійне самогубство, загинути разом"
after = "спільне самогубство; спільна загибель; перен. разом зазнати краху"
assert len(details) == 3914 and details["1510"]["w"] == "心中"
assert details["1510"]["t"] == before
marker = json.dumps(before, ensure_ascii=False)
replacement = json.dumps(after, ensure_ascii=False)
block = html[start:end]
assert block.count(marker) == 1 and replacement not in block
revised = block.replace(marker, replacement, 1)
details["1510"]["t"] = after
assert json.loads(revised) == details
assert revised.replace(replacement, marker, 1) == block
candidate = html[:start] + revised + html[end:]
for js in re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", candidate, re.S):
    subprocess.run(["node", "--check"], input=js, text=True, check=True)
output.write_bytes(candidate.encode())
print(hashlib.sha256(output.read_bytes()).hexdigest())
