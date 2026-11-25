import hashlib
import json
import re
from pathlib import Path

folder = Path(__file__).resolve().parent
root = folder.parents[1]
raw = (root / "JLPT_N1_ukrainian_reading_v229_C12u.html").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "2b117b144f5691d47e1bed8752bd5aaeebdd0eb1496a27041f841c767d8ce3db"
html = raw.decode()
change = json.loads((folder / "patch.json").read_text())
start = re.search(r"const readingBank\s*=\s*", html).end()
bank, end = json.JSONDecoder().raw_decode(html, start)
index, row = next((i, x) for i, x in enumerate(bank["medium"]) if x.get("id") == change["id"])
assert row["questions"][0]["explain"] == change["before"]
row["questions"][0]["explain"] = change["after"]
before, after = [json.dumps(change[k], ensure_ascii=False) for k in ("before", "after")]
body = html[start:end]
assert body.count(before) == 1
new_body = body.replace(before, after, 1)
assert json.loads(new_body) == bank and new_body.replace(after, before, 1) == body
out = (html[:start] + new_body + html[end:]).encode()
(folder / "JLPT_N1_ukrainian_reading_v229_C12v.html").write_bytes(out)
(folder / "browser-fixtures.json").write_text(json.dumps([dict(level="medium",index=index,count=len(bank["medium"]),row=row)],ensure_ascii=False))
print(hashlib.sha256(out).hexdigest())
