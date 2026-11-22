"""Register deposited reviews without applying their linguistic conclusions."""
import argparse
from datetime import date
from pathlib import Path
from runpy import run_path

from importlib import import_module

queue_tools = import_module("validate-queue")
ROOT = queue_tools.ROOT
importer = run_path(str(ROOT.parent / "import-independent-review.py"))
load_json = importer["load_json"]
validate = importer["validate"]
WAITING = {"pending_review", "in_review"}


def render_queue(queue, original):
    pending = [row["package_id"] for row in queue["packages"] if row["status"] in WAITING]
    intro = (
        f"Наступний пакет — **{pending[0]}**. До першого висновку читайте лише його матеріали."
        if pending else "Усі опубліковані пакети мають рецензії."
    )
    lines = ["# Черга незалежного мовного аудиту JLPT N1", "", intro, "",
             "| Пакет | Статус | Обсяг | Рецензії |", "|---|---|---|---|"]
    for row in queue["packages"]:
        scope = row["scope"]
        counts = f"{len(scope['vocab_ids'])} карток, {scope['readings']} текстів, {scope['reading_questions']} питань"
        links = " · ".join(f"[JSON]({review['path']})" for review in row["reviews"])
        lines.append(f"| [{row['package_id']}]({row['path']}) | {row['status']} | {counts} | {links or 'Очікується'} |")
    tail = original.split("Усі шість рецензій", 1)[-1]
    if tail == original:
        tail = original.split("Незмінні пакети", 1)[1]
    else:
        tail = tail.split("Незмінні пакети", 1)[1]
    return "\n".join(lines) + "\n\nНезмінні пакети" + tail


def sync(queue):
    rows = {row["package_id"]: row for row in queue["packages"]}
    packages = {key: load_json((ROOT / row["path"]).read_bytes()) for key, row in rows.items()}
    registered = {entry["path"] for row in rows.values() for entry in row["reviews"]}
    seen = set()
    added = []
    for path in sorted((ROOT / "reviews").glob("*.json")):
        raw = path.read_bytes()
        result = load_json(raw)
        key = result["package_id"]
        validate(packages[key], result)
        reviewer = result["reviewer"]
        identity = (key, reviewer["system"].strip().casefold(), reviewer["session"].strip())
        assert identity not in seen, f"Duplicate review session: {identity}"
        seen.add(identity)
        relative = path.relative_to(ROOT).as_posix()
        if relative in registered:
            continue
        row = rows[key]
        row["reviews"].append({"path": relative, "sha256": queue_tools.sha(raw)})
        if row["status"] in WAITING:
            row["status"] = "review_received"
            row["history"].append({
                "status": "review_received", "date": date.fromisoformat(reviewer["reviewed_at"][:10]).isoformat(),
                "review": relative,
            })
        added.append(key)
    return added


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    queue_path = ROOT / "queue.json"
    queue = load_json(queue_path.read_bytes())
    queue_tools.validate_queue(queue)
    added = sync(queue)
    queue_tools.validate_queue(queue)
    if args.check:
        if added:
            raise SystemExit(f"Unregistered reviews: {', '.join(added)}")
    else:
        markdown = ROOT / "QUEUE.md"
        rendered = render_queue(queue, markdown.read_text())
        queue_path.write_text(queue_tools.json.dumps(queue, ensure_ascii=False, indent=2) + "\n")
        markdown.write_text(rendered)
    print(f"Technical receipts: {', '.join(added) or 'no new reviews'}")


if __name__ == "__main__":
    main()
