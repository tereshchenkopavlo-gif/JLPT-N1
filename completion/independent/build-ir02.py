import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path

DIR = Path(__file__).resolve().parent
old = json.loads((DIR / "IR-20261120-01.json").read_text())
patches = json.loads((DIR / "IR01-confirmed-patches.json").read_text())
revision = "4ac62d1ee543398b49f74a6109981e384859f0ec"
v230 = "ec3e476967a6445e0e4f31e04ba04e11836fa192"
html = subprocess.check_output(["git","show",v230+":JLPT_N1_ukrainian_reading_v230.html"]).decode()

def block(name):
    return json.JSONDecoder().raw_decode(html,re.search(r"const\s+"+name+r"\s*=\s*",html).end())[0]

vocab = {str(v["id"]):v for v in block("DEFAULT_VOCAB")}
details, pos, quizzes = (block(n) for n in ["VOCAB_DETAILS_BY_ID","VOCAB_POS_BY_ID","REVIEWED_MEANING_QUIZZES"])
cases = []
for id in [3375,3652]:
    case = copy.deepcopy(next(c for c in old["cases"] if c["case_id"] == "v_"+str(id)))
    patch = next(p for p in patches if p["case_id"] == case["case_id"])
    if id == 3375:
        case["fields"]["details"]["t"] = patch["after"]
    else:
        case["fields"]["meaning_quiz"] = patch["after"]
    case["sources"].append({"commit":revision,"path":"completion/independent/IR01-confirmed-patches.json",
                            "applied_fields":[patch["field"]]})
    cases.append(case)
for id in [3417,3444,3525,3565]:
    key = str(id)
    cases.append({"case_id":"v_"+key,"kind":"vocab",
                  "sources":[{"commit":v230,"path":"JLPT_N1_ukrainian_reading_v230.html"}],
                  "fields":{"vocabulary":vocab[key],"details":details[key],
                            "display_pos":pos[key],"meaning_quiz":quizzes["v_"+key]}})
for text in json.loads((DIR/"IR01-readings-revised.json").read_text()):
    cases.append({"case_id":text["id"],"kind":"reading",
                  "sources":[{"commit":revision,"path":"completion/independent/IR01-readings-revised.json"}],
                  "fields":text})
digest = hashlib.sha256(json.dumps(cases,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
template = copy.deepcopy(old["return_template"])
template.update(package_id="IR-20261120-02",sources_sha256=digest)
template["cases"] = [{"case_id":c["case_id"],"checked_fields":[],"unchecked_fields":list(c["fields"]),
                      "verdict":"not_reviewed","findings":[]} for c in cases]
packet = {"schema_version":1,"package_id":"IR-20261120-02","instructions":old["instructions"],
          "sources_sha256":digest,
          "scope":{"vocab_ids":[3375,3652,3417,3444,3525,3565],"meaning_contexts":12,
                   "readings":2,"reading_questions":4},
          "cases":cases,"return_template":template}
(DIR/"IR-20261120-02.json").write_text(json.dumps(packet,ensure_ascii=False,indent=2)+"\n")
print("IR-20261120-02: six cards, twelve contexts, two texts, four questions")
