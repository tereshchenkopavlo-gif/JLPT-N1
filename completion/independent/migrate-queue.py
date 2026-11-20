"""Register the two already-issued packages without changing their bytes."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for folder in ["packages","reviews"]:
    (ROOT/folder).mkdir(exist_ok=True)
review_source = ROOT/"results/IR-20261120-01-e416c4e96849ff03.json"
review_target = ROOT/"reviews"/review_source.name
if review_source.exists():
    assert not review_target.exists()
    review_source.rename(review_target)
rows = []
for number in [1,2]:
    id = f"IR-20261120-{number:02d}"
    source = ROOT/(id+".json")
    target = ROOT/"packages"/source.name
    raw = source.read_bytes()
    if target.exists():
        assert target.read_bytes() == raw
    else:
        target.write_bytes(raw)
    packet = json.loads(raw)
    rows.append({
        "package_id":id,"path":"packages/"+source.name,
        "package_sha256":hashlib.sha256(raw).hexdigest(),
        "sources_sha256":packet["sources_sha256"],
        "source_commits":sorted({s["commit"] for c in packet["cases"] for s in c["sources"]}),
        "status":"corrections_pending" if number==1 else "pending_review",
        "predecessor":None if number==1 else "IR-20261120-01",
        "scope":packet["scope"],
        "reviews":[{"path":"reviews/"+review_target.name,
                    "sha256":hashlib.sha256(review_target.read_bytes()).hexdigest()}] if number==1 else [],
        "history":[{"status":"pending_review","date":"2026-11-20"}] + (
            [{"status":"reviewed_with_issues","date":"2026-11-20"},
             {"status":"corrections_pending","date":"2026-11-20"}] if number==1 else []),
        "notes":"Six adjudicated improvements await recheck in IR02; one suggestion rejected with dictionary evidence." if number==1
                else "Revised fields from IR01 plus four further vocabulary cases; unchanged supporting context is retained."})
(ROOT/"queue.json").write_text(json.dumps({"schema_version":1,"packages":rows},ensure_ascii=False,indent=2)+"\n")
md = [
    "# Черга незалежного мовного аудиту JLPT N1","",
    "Наступний пакет для перевірки — **IR-20261120-02**. Відкрийте його JSON і виконайте інструкції всередині. До першого висновку читайте тільки пакет. Після явного початку рецензування стан змінюється на in_review.","",
    "| Пакет | Стан | Попередній пакет | Обсяг | Рецензія |",
    "|---|---|---|---|---|"]
for row in rows:
    review = f"[ChatGPT]({row['reviews'][0]['path']})" if row["reviews"] else "Очікується"
    md.append(f"| [{row['package_id']}]({row['path']}) | {row['status']} | {row['predecessor'] or '—'} | 6 карток, 12 meaning-контекстів, 2 тексти, 4 питання | {review} |")
md += ["","## Джерела й контрольні суми",""]
for row in rows:
    md += [f"### {row['package_id']}","",
           f"- SHA-256 файла — `{row['package_sha256']}`.",
           f"- sources_sha256 — `{row['sources_sha256']}`.",
           "- Commit SHA вихідних матеріалів — " + ", ".join(f"`{s}`" for s in row["source_commits"]) + ".",""]
md += ["IR01 не має повного незалежного приймання. Шість підтверджених правок очікують повторного перегляду через IR02. Перевірені поля й виключення наведено в [acceptance-register.json](acceptance-register.json).",
       "","Пакети в packages/ збережені побайтово. Історичні кореневі файли лишаються доступними за старими посиланнями. Єдину отриману рецензію перенесено в reviews/.",
       "","[Правила процесу](README.md) · [Машиночитна черга](queue.json)",
       "","Основний аудит і C12 продовжуються під час очікування незалежних висновків."]
(ROOT/"QUEUE.md").write_text("\n".join(md)+"\n")
for file in ["acceptance-register.json","IR01-adjudication.md"]:
    path = ROOT/file
    text = path.read_text().replace("results/IR-20261120-01-e416c4e96849ff03.json",
                                  "reviews/IR-20261120-01-e416c4e96849ff03.json")
    path.write_text(text)
