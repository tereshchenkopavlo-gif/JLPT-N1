"""Register new immutable revisions for the changed IR02–IR07 material."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = "3e37dc35adacbadc7637094ea6e9ed304671bbaa"
PATH = "completion/independent/adjudications/20261121/reviewed-materials.json"
materials = json.loads((ROOT/"adjudications/20261121/reviewed-materials.json").read_text())
patches = json.loads((ROOT/"adjudications/20261121/patches.json").read_text())
changed = {p["case_id"]:p for p in patches}
decisions = json.loads((ROOT/"adjudications/20261121/decisions.json").read_text())
template_source = json.loads((ROOT/"packages/IR-20261120-02.json").read_text())
queue = json.loads((ROOT/"queue.json").read_text())
groups = [
    ("IR-20261121-08",["v_3375","v_3652","v_3417","v_3444","v_3565",
                      "m-c12-20261120-03","m-c12-20261120-04","l-c12-20261120-01"],
     ["IR-20261120-02","IR-20261121-03"]),
    ("IR-20261121-09",["l-c12-20261121-02","m-c12-20261121-05","m-c12-20261121-06",
                      "l-c12-20261121-07","l-c12-20261121-08","m-c12-20261121-09",
                      "m-c12-20261121-10","m-c12-20261121-12"],
     ["IR-20261121-04","IR-20261121-05","IR-20261121-06","IR-20261121-07"])]
def sha(value):
    return hashlib.sha256(value).hexdigest()
def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True).encode()
for id,ids,predecessors in groups:
    assert len(ids)==len(set(ids))
    cases=[]
    for cid in ids:
        assert cid in changed
        fields=copy.deepcopy(materials[cid])
        cases.append({"case_id":cid,"kind":"vocab" if cid.startswith("v_") else "reading",
                      "sources":[{"commit":SOURCE,"path":PATH,"case_id":cid}],
                      "fields":fields})
    digest=sha(canonical(cases))
    template=copy.deepcopy(template_source["return_template"])
    template.update(package_id=id,sources_sha256=digest)
    template["cases"]=[{"case_id":c["case_id"],"checked_fields":[],
                        "unchecked_fields":list(c["fields"]),"verdict":"not_reviewed",
                        "findings":[]} for c in cases]
    scope={"vocab_ids":[int(cid[2:]) for cid in ids if cid.startswith("v_")],
           "meaning_contexts":sum(len(c["fields"]["meaning_quiz"]["byExample"]) for c in cases if c["kind"]=="vocab"),
           "readings":sum(c["kind"]=="reading" for c in cases),
           "reading_questions":sum(len(c["fields"]["questions"]) for c in cases if c["kind"]=="reading")}
    packet={"schema_version":1,"package_id":id,
            "instructions":template_source["instructions"],
            "sources_sha256":digest,"predecessors":predecessors,
            "scope":scope,"cases":cases,"return_template":template}
    # Check active exact content before creating the new immutable package.
    for row in queue["packages"]:
        if row["package_id"]==id:
            continue
        if row["status"] not in ["pending_review","in_review"]:
            continue
        active=json.loads((ROOT/row["path"]).read_text())
        keys={(c["case_id"],sha(canonical(c["fields"]))) for c in active["cases"]}
        assert not any((c["case_id"],sha(canonical(c["fields"]))) in keys for c in cases)
    path=ROOT/"packages"/(id+".json")
    raw=(json.dumps(packet,ensure_ascii=False,indent=2)+"\n").encode()
    if path.exists():
        assert path.read_bytes()==raw,"Immutable packet changed"
    else:
        path.write_bytes(raw)
    row={"package_id":id,"path":"packages/"+path.name,"package_sha256":sha(raw),
         "sources_sha256":digest,"source_commits":[SOURCE],"status":"pending_review",
         "predecessor":predecessors[0],"predecessors":predecessors,"scope":scope,
         "reviews":[],"history":[{"status":"pending_review","date":"2026-11-21"}],
         "notes":"Revised material; complete source context included for an independent assessment. Earlier reviewer findings are excluded."}
    existing=next((r for r in queue["packages"] if r["package_id"]==id),None)
    if existing:
        assert existing==row
    else:
        queue["packages"].append(row)
(ROOT/"queue.json").write_text(json.dumps(queue,ensure_ascii=False,indent=2)+"\n")
lines=["# Черга незалежного мовного аудиту JLPT N1","",
       "Наступний pending_review — **IR-20261121-08**, потім IR-20261121-09. Відкрийте пакет і виконайте його інструкції. До першого висновку читайте лише навчальні матеріали пакета.","",
       "| Пакет | Статус | Обсяг | Рецензії |","|---|---|---|---|"]
for row in queue["packages"]:
    s=row["scope"]
    scope=f"{len(s['vocab_ids'])} карток, {s['readings']} текстів, {s['reading_questions']} питань"
    reviews=" · ".join(f"[ChatGPT]({r['path']})" for r in row["reviews"]) or "Очікується"
    lines.append(f"| [{row['package_id']}]({row['path']}) | {row['status']} | {scope} | {reviews} |")
lines+=["","Усі шість рецензій IR02–IR07 отримано й розглянуто. Змінені поля очікують повторного незалежного перегляду; pass двох попередньо виправлених C12-текстів і m-c12-20261121-11 зафіксовано для точних вихідних полів.",
        "","Незмінні пакети, SHA джерел, SHA-256 файлів, predecessors і історія станів — [queue.json](queue.json).",
        "","[Розгляд зауважень](adjudications/20261121/README.md) · [Реєстр полів](acceptance-register.json) · [Правила](README.md)",
        "","Основний аудит і наступні партії C12 продовжуються під час очікування висновків."]
(ROOT/"QUEUE.md").write_text("\n".join(lines)+"\n")
print("IR08 and IR09 registered with immutable hashes and predecessor links")
