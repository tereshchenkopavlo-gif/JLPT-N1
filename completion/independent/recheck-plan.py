"""Plan incremental review using immutable predecessor evidence."""
import argparse
import json
import re
from importlib import import_module
from pathlib import Path

tools = import_module("sync-reviews")


def hash_value(value):
    return tools.queue_tools.sha(tools.queue_tools.canonical(value))


def slots(case):
    fields = case["fields"]
    for root, value in fields.items():
        if root in {"questions", "contextNotes"}:
            for index, item in enumerate(value):
                yield f"{root}[{index}]", item
            if value:
                continue
        yield root, value


def dependencies(case, path):
    fields = case["fields"]
    root = path.split("[")[0]
    if case["kind"] == "vocab":
        # Lexical fields are coupled. Meaning options do not change lexical evidence.
        return {k: v for k, v in fields.items() if k != "meaning_quiz"}
    keys = {
        "id": ("id",),
        "title": ("id", "ja", "uk"),
        "ja": ("id", "title", "uk"),
        "uk": ("id", "title", "ja"),
        "questions": ("id", "title", "ja", "uk", "contextNotes"),
        "contextNotes": ("id", "title", "ja", "uk"),
    }.get(root, tuple(fields))
    return {key: fields.get(key) for key in keys}


def covers(parent, path):
    return parent == path or path.startswith((parent + ".", parent + "["))


def intersects(left, right):
    return covers(left, right) or covers(right, left)


def evidence_for(report_case, path):
    if report_case["verdict"] not in {"pass", "issues"}:
        return False
    if not any(covers(checked, path) for checked in report_case["checked_fields"]):
        return False
    for excluded in report_case["unchecked_fields"]:
        if "[*]" in excluded:
            excluded = excluded.split("[*]", 1)[0]
        if intersects(excluded, path):
            return False
    # Non-structural legacy finding paths can only exclude their whole root.
    for finding in report_case["findings"]:
        finding_path = finding["field_path"]
        if not re.fullmatch(r"[A-Za-z_0-9]+(?:\.[A-Za-z_0-9]+|\[\d+\])*", finding_path):
            finding_path = re.split(r"[.\[/]", finding_path)[0]
        if intersects(finding_path, path):
            return False
    return True


def matches_register(recorded, key, cid, checked, source_hash, path, old, field):
    entry = recorded.get((key, cid, checked, source_hash, path))
    if not entry:
        return False
    for excluded in entry["exclusions"]:
        if intersects(excluded.split("[*]", 1)[0], field):
            return False
    value = tools.importer["resolve_field"](old["fields"], checked)
    return entry.get("reviewed_value_sha256", hash_value(value)) == hash_value(value)


def make_plan(candidate, rows):
    root = tools.ROOT
    lineage = candidate.get("predecessors") or [candidate.get("predecessor")]
    register = tools.load_json((root / "acceptance-register.json").read_bytes())
    recorded = {(e["package_id"], e["case_id"], e["reviewed_field"], e["source_sha256"], e["evidence"]): e
                for e in register if e["status"] in {"independent_reviewed_original", "reviewed_original_field"}}
    previous = {}
    for key in filter(None, lineage):
        row = rows[key]
        packet = tools.load_json((root / row["path"]).read_bytes())
        for entry in row["reviews"]:
            report = tools.load_json((root / entry["path"]).read_bytes())
            tools.validate(packet, report)
            evidence = (root / entry["path"]).relative_to(root.parents[1]).as_posix()
            reports = {case["case_id"]: case for case in report["cases"]}
            for case in packet["cases"]:
                previous.setdefault(case["case_id"], []).append(
                    (case, reports[case["case_id"]], key, row["sources_sha256"], evidence, entry["sha256"])
                )
    for case in candidate["cases"]:
        cid = case["case_id"]
        for field, value in slots(case):
            digest = hash_value([value, dependencies(case, field)])
            item = {"case_id": cid, "field": field, "sha256": digest, "action": "review"}
            for old, report, key, source_hash, path, evidence_hash in previous.get(cid, []):
                old_slots = dict(slots(old))
                if old["kind"] != case["kind"] or field not in old_slots:
                    continue
                if hash_value([old_slots[field], dependencies(old, field)]) != digest:
                    continue
                if not evidence_for(report, field):
                    continue
                if not any(matches_register(recorded, key, cid, checked, source_hash, path, old, field)
                           for checked in report["checked_fields"] if covers(checked, field)):
                    continue
                item.update(action="reuse_evidence", predecessor=key, evidence=path,
                            evidence_sha256=evidence_hash, predecessor_sources_sha256=source_hash)
                break
            yield item


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    queue = tools.load_json((tools.ROOT / "queue.json").read_bytes())
    tools.queue_tools.validate_queue(queue)
    tools.sync(queue)
    rows = {row["package_id"]: row for row in queue["packages"]}
    candidate = tools.load_json(args.package.read_bytes())
    if candidate["package_id"] in rows:
        lineage = rows[candidate["package_id"]].get("predecessor")
        candidate.setdefault("predecessor", lineage)
    print(json.dumps(list(make_plan(candidate, rows)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
