"""Build a scoped candidate from the pinned published trainer."""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

source, output = map(Path, sys.argv[1:])
raw = source.read_bytes()
assert hashlib.sha256(raw).hexdigest() == "06a7d463257c83816b28532a261d0be42728386655722c8c58a2231b28f174c7"
html = raw.decode()
sentence = "古い体質の組織と心中するわけにはいかないと、彼は転職を決意した。"
assert sentence in html
old = "if (real && found && literalClozeAvailable(ex,it,this)"
new = f"""// ID1510: the random pool can supply 協力, another natural completion.
        const ambiguousCloze = it.kind === 'v' && String(it.id) === '1510'
          && ex === '{sentence}';
        if (!ambiguousCloze && real && found && literalClozeAvailable(ex,it,this)"""
assert html.count(old) == 1
candidate = html.replace(old, new, 1)
assert candidate.replace(new, old, 1).encode() == raw
for script in re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", candidate, re.S):
    subprocess.run(["node", "--check"], input=script, text=True, check=True)
output.write_bytes(candidate.encode())
print(hashlib.sha256(candidate.encode()).hexdigest())
