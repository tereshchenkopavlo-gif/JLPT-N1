"""Build the C12 draft plus the IR10 correction from exact source material."""
import hashlib
import json
import re
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / "JLPT_N1_ukrainian_reading_v229_C12k.html"
BASE_SHA = "409913f3e2a91056e8905cfafe545eba5b6bb142749f0e96f5e5493918147e19"
OUTPUT = HERE / "JLPT_N1_C12_candidate_UNACCEPTED.html"


def main():
    raw = BASE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == BASE_SHA
    base = raw.decode()
    start = re.search(r"const readingBank\s*=\s*", base).end()
    bank, end = json.JSONDecoder().raw_decode(base, start)
    drafts = json.loads((HERE / "drafts.json").read_text())
    correction = json.loads((HERE / "ir10-patch.json").read_text())
    assert (len(bank["medium"]), len(bank["long"])) == (112, 69)
    repaired = next(row for row in bank["long"] if row.get("id") == correction["case_id"])
    index = correction["question_index"]
    assert repaired["questions"][index] == correction["before"]
    repaired["questions"][index] = correction["after"]
    for draft in drafts:
        assert all(draft["id"] != row.get("id") and draft["title"] != row["title"]
                   for rows in bank.values() for row in rows)
    bank["medium"].extend(drafts)
    payload = json.dumps(bank, ensure_ascii=False, separators=(",", ":"))
    candidate = base[:start] + payload + base[end:]
    assert candidate[:start] + base[start:end] + candidate[start + len(payload):] == base
    checked, _ = json.JSONDecoder().raw_decode(candidate, start)
    for row in [*drafts, repaired]:
        for question in row["questions"]:
            assert len(set(question["choices"])) == 4 and 0 <= question["answer"] < 4
            assert question["evidence"] in row["ja"]
    fixtures = [{"level": level, "count": len(checked[level]), "index": checked[level].index(row), "row": row}
                for level, row in [("medium", drafts[0]), ("long", repaired)]]
    with TemporaryDirectory() as temp:
        for index, script in enumerate(re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", candidate, re.S)):
            path = Path(temp) / f"{index}.js"
            path.write_text(script)
            subprocess.run(["node", "--check", str(path)], check=True)
    OUTPUT.write_bytes(candidate.encode())
    (HERE / "browser-fixtures.json").write_text(json.dumps(fixtures, ensure_ascii=False))
    print(json.dumps({"candidate_sha256": hashlib.sha256(candidate.encode()).hexdigest(),
                      "medium": len(bank["medium"]), "long": len(bank["long"]), "exact_rollback": True,
                      "node_syntax": True, "independent_recheck": "pending"}))


if __name__ == "__main__":
    main()
