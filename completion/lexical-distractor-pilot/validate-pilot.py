"""Validate the author and blind data against the reviewed pilot snapshot."""
import argparse
import hashlib
import json
from pathlib import Path


BLIND_FIELDS = ("id", "type", "prompt", "choices")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def fingerprint(item):
    payload = json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validate(folder):
    items = load(folder / "items.json")
    blind = load(folder / "review-blind.json")
    evidence = load(folder / "accepted-items.json")
    if set(blind) != {"instructions", "items"}:
        raise ValueError("Unexpected fields in blind review packet")
    ids = [item["id"] for item in items]
    if not ids or len(set(ids)) != len(ids):
        raise ValueError("Missing or duplicate item IDs")
    if set(ids) != set(evidence["item_sha256"]):
        raise ValueError("Item IDs differ from the reviewed snapshot")
    projected = [{field: item[field] for field in BLIND_FIELDS} for item in items]
    if projected != blind["items"]:
        raise ValueError("Blind packet differs from author items or contains extra fields")
    for item in items:
        choices = item["choices"]
        if len(choices) != 4 or not all(isinstance(c, str) and c.strip() for c in choices):
            raise ValueError(f"{item['id']}: expected four nonempty options")
        if len({c.strip() for c in choices}) != 4:
            raise ValueError(f"{item['id']}: duplicate options")
        if type(item["answer"]) is not int or not 0 <= item["answer"] < 4:
            raise ValueError(f"{item['id']}: invalid answer index")
        if fingerprint(item) != evidence["item_sha256"][item["id"]]:
            raise ValueError(f"{item['id']}: differs from reviewed snapshot")
    return len(items)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", nargs="?", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    try:
        count = validate(args.folder)
    except (OSError, ValueError, TypeError, KeyError) as error:
        parser.exit(1, f"{error}\n")
    print(f"{count} items match the reviewed snapshot and blind packet.")
