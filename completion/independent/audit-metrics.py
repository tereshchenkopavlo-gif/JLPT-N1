"""Report evidenced unit counts and package lead times."""
import json
from collections import Counter
from datetime import date
from importlib import import_module
from statistics import mean

tools = import_module("sync-reviews")


def units(case):
    cid = case["case_id"]
    yield cid
    if case["kind"] == "reading":
        yield from (f"{cid}/questions[{i}]" for i, _ in enumerate(case["fields"]["questions"]))
    if case["kind"] == "vocab":
        contexts = case["fields"].get("meaning_quiz", {}).get("byExample", {})
        yield from (f"{cid}/meaning/{context}" for context in contexts)


def main():
    root = tools.ROOT
    queue = tools.load_json((root / "queue.json").read_bytes())
    tools.queue_tools.validate_queue(queue)
    statuses, created, reviewed, closed, lead, close_lead = Counter(), set(), set(), set(), [], []
    bags = {}
    for row in queue["packages"]:
        statuses[row["status"]] += 1
        packet = tools.load_json((root / row["path"]).read_bytes())
        cases = {case["case_id"]: case for case in packet["cases"]}
        bags[row["package_id"]] = cases
        for case in cases.values():
            created.update(units(case))
        published = date.fromisoformat(row["history"][0]["date"][:10])
        dates = []
        for entry in row["reviews"]:
            report = tools.load_json((root / entry["path"]).read_bytes())
            tools.validate(packet, report)
            dates.append(date.fromisoformat(report["reviewer"]["reviewed_at"][:10]))
            for case in report["cases"]:
                if case["checked_fields"]:
                    reviewed.add(case["case_id"])
        if dates and min(dates) >= published:
            lead.append((min(dates) - published).days)
        if row["status"] == "closed":
            close_date = date.fromisoformat(row["history"][-1]["date"][:10])
            close_lead.append((close_date - published).days)
        # Closed rows may record only partial or administrative completion.
        for cid in row.get("closed_case_ids", []):
            assert row["status"] == "closed" and cid in cases
            closed.add(cid)
    corrected = set()
    for path in (root / "adjudications").glob("*/patches.json"):
        for patch in tools.load_json(path.read_bytes()):
            corrected.add(patch["case_id"])
    fixed_ir01 = tools.load_json((root / "IR01-confirmed-patches.json").read_bytes())
    corrected.update(patch["case_id"] for patch in fixed_ir01)
    report = {
        "unique_cases_created": len(set().union(*(set(cases) for cases in bags.values()))),
        "unique_learning_units_packaged_including_questions_and_meaning_contexts": len(created),
        "unique_cases_with_independent_checked_fields": len(reviewed),
        "unique_cases_with_recorded_corrections": len(corrected),
        "unique_cases_explicitly_closed": len(closed),
        "packages_by_state": dict(statuses),
        "packages_waiting_for_review": statuses["pending_review"] + statuses["in_review"],
        "packages_awaiting_adjudication": statuses["review_received"],
        "mean_calendar_days_to_first_review": round(mean(lead), 2) if lead else None,
        "packages_measured_to_first_review": len(lead),
        "mean_calendar_days_to_closure": round(mean(close_lead), 2) if close_lead else None,
        "packages_measured_to_closure": len(close_lead),
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
