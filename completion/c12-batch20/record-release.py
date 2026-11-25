import csv
import io
from pathlib import Path

register = Path("completion/review-register.csv")
raw = register.read_bytes()
rows = list(csv.DictReader(io.StringIO(raw.decode())))
assert len(rows) == 5958
key = "l-c12-20261125-32"
assert all(not item["key"].startswith(key) for item in rows)
evidence = "completion/c12-batch20/acceptance.md; author review; Chromium 45515009349; independent pending"
entries = [("reading", key, "readingBank.long[73]", "reviewed", evidence)]
entries += [
    ("reading_question", f"{key}:q{i + 1}", f"readingBank.long[73].questions[{i}]", "reviewed", evidence)
    for i in range(3)
]
out = io.StringIO()
csv.writer(out, lineterminator="\n").writerows(entries)
register.write_bytes(raw.rstrip(b"\r\n") + b"\n" + out.getvalue().encode())
notes = Path("JLPT_N1_v229_C12u_audit.md").read_bytes()
for name in ("PROJECT_STATUS.md", "completion/BACKLOG.md"):
    path = Path(name)
    path.write_bytes(notes + b"\n" + path.read_bytes())
