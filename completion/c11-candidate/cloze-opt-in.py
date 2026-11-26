import re
import subprocess
from pathlib import Path

file = Path("merged.html")
html = file.read_text(encoding="utf-8")
old = "if(!reviewed||!Array.isArray(reviewed.wrong)||reviewed.wrong.length!==3)return null;"
new = """if (reviewed?.allowCloze !== true || !Array.isArray(reviewed.wrong)
      || reviewed.wrong.length !== 3
      || reviewed.wrong.some(option => typeof option !== "string" || !option.trim())) return null;"""
assert html.count(old) == 1
revised = html.replace(old, new, 1)
assert revised.replace(new, old, 1) == html
file.write_text(revised, encoding="utf-8")
helper = re.search(r"function reviewedClozeOptions\(item, example\) \{.*?\n\}", revised, re.S).group()
subprocess.run(["node"], input="""
const assert = require("node:assert/strict");
const REVIEWED_CLOZE_QUIZZES = {};
""" + helper + """
const item = {kind: "v", id: "fixture", word: {w: "target"}};
const exact = "fixture context";
const record = {wrong: ["one", "two", "three"]};
REVIEWED_CLOZE_QUIZZES.v_fixture = {byExample: {[exact]: record}};
assert.equal(reviewedClozeOptions(item, exact), null);
record.allowCloze = true;
assert.equal(reviewedClozeOptions(item, exact), record);
assert.equal(reviewedClozeOptions(item, exact + "."), null);
assert.equal(reviewedClozeOptions({...item, id: "other"}, exact), null);
for (const wrong of [["target","two","three"], ["one","one","three"], ["","two","three"], ["one","two"]]) {
    record.wrong = wrong;
    assert.equal(reviewedClozeOptions(item, exact), null);
}
console.log("Exact example, explicit opt-in and option validation passed");
""", text=True, check=True)
