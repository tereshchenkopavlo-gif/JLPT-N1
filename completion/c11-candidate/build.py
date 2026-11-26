import hashlib
import json
import re
import subprocess
from pathlib import Path

base = Path("ancestor.html")
current = Path("current.html")
original = Path("candidate.html")
expected = {
    base: "e5e298e9f5efcf45c7cfd1fe83ab9ce5a19dcde13759482d54e3b8313bd92dab",
    current: "c76aeb70f628123e35766055c5bcbc3e9f542b1c39f578405f7df32879458707",
    original: "34f1cc21116da7575d731a2ee484d41044c0934cfe7bcebf9d78fe2ef7d66ab2",
}
for file, digest in expected.items():
    assert hashlib.sha256(file.read_bytes()).hexdigest() == digest
source = original.read_bytes()
for change in json.loads(Path("completion/c11-meaning-key-revisions.json").read_text()):
    before, after = (change[key].encode() for key in ("before", "after"))
    assert source.count(before) == 1 and after not in source
    source = source.replace(before, after, 1)
Path("revised.html").write_bytes(source)
def merge(a, b, c):
    return subprocess.check_output(["git", "merge-file", "-p", a, b, c])
merged = merge(current, base, "revised.html")
Path("merged.html").write_bytes(merged)
assert merge(base, current, "merged.html") == source
assert hashlib.sha256(merged).hexdigest() == "a6e7db84e2c05df80c23ba9340daecd6c879050b4656b06f57db21504a42fd2d"

def section(html, name):
    start = re.search(r"\bconst\s+" + name + r"\s*=\s*", html).end()
    return json.JSONDecoder().raw_decode(html, start)[0]

html = merged.decode()
released = current.read_text()
for name, count in (("DEFAULT_VOCAB", 3914), ("GRAMMAR_DETAILS_BY_ID", 130),
                    ("VOCAB_AUDITED_PAIRS", 859)):
    data = section(html, name)
    assert len(data) == count and data == section(released, name)
bank = section(html, "readingBank")
assert bank == section(released, "readingBank")
assert (len(bank["medium"]), len(bank["long"])) == (120, 80)
for script in re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", html, re.S):
    subprocess.run(["node", "--check"], input=script, text=True, check=True)
print("Pinned hashes, inverse merge, protected data and JS syntax passed")
