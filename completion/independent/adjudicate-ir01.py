import copy
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT / "completion/independent"
package = json.loads((DIR / "IR-20261120-01.json").read_text())
result_path = next((DIR / "results").glob("IR-20261120-01-*.json"))
result = json.loads(result_path.read_text())
assert result["sources_sha256"] == package["sources_sha256"]
base = ROOT / "JLPT_N1_ukrainian_reading_v229_C12b.html"
original = base.read_text()
assert hashlib.sha256(base.read_bytes()).hexdigest() == "d4d38ebd380cbb054fc97d631abbc455f093808df97e1e24eb6f27a198b1a0c7"

def block(text, name):
    start = re.search(r"const\s+" + name + r"\s*=\s*", text).end()
    data, end = json.JSONDecoder().raw_decode(text, start)
    return data, start, end

details, ds, de = block(original, "VOCAB_DETAILS_BY_ID")
bank, bs, be = block(original, "readingBank")
old_details, old_bank = copy.deepcopy(details), copy.deepcopy(bank)
gloss = "наразі, поки що; поточний, найближчий (у сполуках на зразок 当面の課題)"
old_gloss = details["3375"]["t"]
assert old_gloss == "наразі, поки що, нагальний"
details["3375"]["t"] = gloss
cases = {c["case_id"]: c for c in package["cases"]}
texts = {t["id"]: t for t in bank["medium"] if "id" in t}
assert len(bank["medium"]) == 103 and len(bank["long"]) == 61
for id in ["m-c12-20261119-01", "m-c12-20261119-02"]:
    assert texts[id] == cases[id]["fields"], "Published source drift: review manually"
a, b = texts["m-c12-20261119-01"], texts["m-c12-20261119-02"]
a["questions"][0]["choices"] = [
    a["questions"][0]["choices"][0],
    "点検が間に合わない場合の開場延期は、毎回館長が判断する。",
    "開場を遅らせる代わりに開演を遅らせ、入場後に点検を終える。",
    "開場延期の判断を避けるため、次回から点検項目を減らす。"]
a["questions"][0]["explain"] = "Опора — 「責任者に判断の権限を与える」. Рішення про затримку допуску глядачів передають відповідальній особі. Щоразу звертатися до директора, перевіряти після входу глядачів або скорочувати перевірку не вирішували."
a["questions"][1]["choices"] = [
    "観客を退場させた段階で、照明の復旧作業も完了したという意味。",
    "観客を退場させることが、照明の点検より優先すべき目的だったという意味。",
    a["questions"][1]["choices"][2],
    "観客を退場させるまでの手順が、順序よく説明されているという意味。"]
a["questions"][1]["explain"] = "始末だった підкреслює небажаний підсумок — довелося вивести глядачів. Це не завершення ремонту, не первісна мета дії й не нейтральний опис порядку операцій."
b["questions"][0]["choices"] = [
    "毎月の回収量から清掃の効果を比べやすくするため。",
    b["questions"][0]["choices"][1],
    "清掃場所を順番に変え、各場所の作業量を均等にするため。",
    "水路を調べる住民と清掃する住民の担当区域を決めるため。"]
b["questions"][0]["explain"] = "Опора — 「量を比べるだけでは、原因は見えてこない」. До обсягу додали вид і місце сміття для пошуку причин повторного накопичення. Порівняння результативності, вирівнювання навантаження й розподіл ділянок не названо метою."
b["questions"][1]["choices"] = [
    "住民の態度が変わるのは、ごみの原因を一つに特定できた場合だけだ。",
    "代表者自身が態度を変えたくなり、その気持ちを抑えられないということだ。",
    "住民の態度を変えるため、代表者が全員に調査への参加を命じるということだ。",
    b["questions"][1]["choices"][3]]
b["questions"][1]["explain"] = "主語 — 「小さな発見の積み重ね」. Керівник переконаний, що відкриття спричинятимуть зміну ставлення мешканців. Установлення єдиної причини, особисте непереборне бажання керівника й наказ усім брати участь цього змісту не передають."
unique = copy.deepcopy(cases["v_3652"]["fields"]["meaning_quiz"])
sentence = next(iter(unique["byExample"]))
unique["byExample"][sentence]["wrong"] = [
    "従来の商品より使いやすく、日常の用途によく合っているさま。",
    "品質や性能が平均を上回り、ほかの商品より優れているさま。",
    "幅広い人の好みに合い、多くの人から受け入れられるさま。"]
patches = [
    {"case_id": "v_3375", "field": "details.t", "before": old_gloss, "after": gloss},
    {"case_id": "v_3652", "field": "meaning_quiz.byExample", "before": cases["v_3652"]["fields"]["meaning_quiz"], "after": unique}]
for id in [a["id"], b["id"]]:
    for i in range(2):
        patches.append({"case_id": id, "field": f"questions[{i}]",
                        "before": cases[id]["fields"]["questions"][i],
                        "after": texts[id]["questions"][i]})
for text in [a, b]:
    for q in text["questions"]:
        assert len(set(q["choices"])) == 4
        assert q["evidence"] in text["ja"]
        old = cases[text["id"]]["fields"]["questions"][text["questions"].index(q)]
        assert q["answer"] == old["answer"]
        assert q["choices"][q["answer"]] == old["choices"][old["answer"]]
out = original
for start, end, data in sorted([(ds,de,details), (bs,be,bank)], reverse=True):
    out = out[:start] + json.dumps(data, ensure_ascii=False, separators=(",",":")) + out[end:]
for name in ["DEFAULT_VOCAB", "GRAMMAR_DETAILS_BY_ID", "VOCAB_POS_BY_ID",
             "REVIEWED_MEANING_QUIZZES", "VOCAB_AUDITED_PAIRS"]:
    assert block(out,name)[0] == block(original,name)[0], name
restored_details = copy.deepcopy(details); restored_details["3375"]["t"] = old_gloss
assert restored_details == old_details
restored_bank = copy.deepcopy(bank)
for row in restored_bank["medium"]:
    if row.get("id") in [a["id"],b["id"]]:
        row["questions"] = cases[row["id"]]["fields"]["questions"]
assert restored_bank == old_bank
candidate = DIR / "IR01_candidate_UNACCEPTED.html"
candidate.write_text(out)
(DIR / "IR01-confirmed-patches.json").write_text(json.dumps(patches,ensure_ascii=False,indent=2)+"\n")
(DIR / "IR01-readings-revised.json").write_text(json.dumps([a,b],ensure_ascii=False,indent=2)+"\n")
entries = []
for case in result["cases"]:
    for field in case["checked_fields"]:
        affected = [x for x in patches if x["case_id"] == case["case_id"] and
                    (x["field"].startswith(field) or field.startswith(x["field"]))]
        entries.append({"package_id": package["package_id"], "case_id": case["case_id"],
                        "reviewed_field": field, "source_sha256": package["sources_sha256"],
                        "reviewer_verdict": case["verdict"],
                        "status": "revised_pending_independent_review" if affected else "reviewed_original_field",
                        "exclusions": case["unchecked_fields"], "evidence": str(result_path.relative_to(ROOT)),
                        "scope_note": "Reported field only; exclusions override parent coverage."})
    for field in case["unchecked_fields"]:
        entries.append({"package_id":package["package_id"],"case_id":case["case_id"],
                        "reviewed_field":field,"status":"not_reviewed",
                        "evidence":str(result_path.relative_to(ROOT))})
(DIR / "acceptance-register.json").write_text(json.dumps(entries,ensure_ascii=False,indent=2)+"\n")
report = {"base":base.name,"candidate":str(candidate.relative_to(ROOT)),
          "candidate_sha256":hashlib.sha256(candidate.read_bytes()).hexdigest(),
          "patch_groups":len(patches),"reading_questions_revised":4,
          "existing_keys_preserved":True,"protected_blocks_equal":True,
          "vocabulary":len(block(out,"DEFAULT_VOCAB")[0]),"grammar":len(block(out,"GRAMMAR_DETAILS_BY_ID")[0]),
          "medium":len(bank["medium"]),"long":len(bank["long"]),
          "browser_acceptance":"pending","independent_recheck":"pending",
          "unique_quiz_patch":"staged for v231 only"}
(DIR / "IR01-validation.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
