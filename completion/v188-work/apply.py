import csv, hashlib, json, re
from pathlib import Path

BASE = Path("JLPT_N1_ukrainian_reading_v187.html")
OUT = Path("JLPT_N1_ukrainian_reading_v188.html")
WORK = Path("completion/v188-work")
REGISTER = Path("completion/review-register.csv")
BASE_SHA = "f321dd68a4beb1958031b000dd8eb94de9106cfc5e84041c4d70ca8cc0e67656"

UPDATES = [
    ("677", "m", "大きな広間。会場。", "大きな広間。会場。また、ゴルフでボールを入れる穴。"),
    ("677", "exampleTranslations[0]", "Урочиста церемонія відбулася з великим розмахом у міській великій залі.", "Урочиста церемонія відбулася з великим розмахом у великій залі міста."),
    ("683", "exampleTranslations[1]", "Він попросив помасажувати йому спину, яка затерпла.", "Йому помасажували затерплу спину."),
    ("685", "exampleTranslations[1]", "Магазин, оформлений молодим дизайнером, привернув увагу галузі.", "Магазин, дизайн якого розробив молодий дизайнер, привернув увагу галузі."),
    ("687", "exampleTranslations[0]", "Призначений працівник послідовно забезпечує всю підтримку після впровадження.", "Фахівець, спеціально закріплений за цим завданням, забезпечуватиме постійний супровід після впровадження."),
    ("691", "exampleTranslations[0]", "Вона дбайливо носить намисто, успадковане від бабусі.", "Вона дуже дорожить намистом, що дісталося їй від бабусі, й носить його."),
    ("691", "exampleTranslations[1]", "На виставці популярністю користувалися намиста ручної роботи.", "На виставці популярністю користувалися намиста, виготовлені майстрами вручну."),
    ("692", "exampleTranslations[0]", "Мелодія головної пісні фільму глибоко закарбувалася в пам’яті слухачів.", "Мелодія головної пісні до фільму глибоко запам’яталася слухачам."),
    ("692", "exampleTranslations[1]", "Глядачі в залі тихо вслухалися в прекрасну мелодію.", "Люди в залі тихо вслухалися в прекрасну мелодію."),
    ("697", "t", "темрява, морок; тіньовий світ, чорний ринок", "темрява, морок; тіньовий світ"),
    ("697", "exampleTranslations[1]", "Щоб припинити незаконні тіньові операції, органи влади посилюють розслідування.", "Щоб припинити незаконну приховану торгівлю, органи влади посилюють розслідування."),
    ("701", "t", "відкрите море на віддалі від берега; морська далечінь (沖に出る — вийти у відкрите море)", "водний простір на віддалі від берега (у морі чи озері); морська далечінь (沖に出る — вийти у відкрите море)"),
    ("703", "m", "物事の中心となる重要な部分。また、原子や細胞の内部にある核。", "物事の中心となる重要な部分。また、原子の中心部や、細胞内で遺伝情報を含む構造。"),
    ("706", "m", "木の枝や根を支える中心の太い部分。物事の中心となる部分。", "木の中心にある太い部分で、枝を支える。物事の中心となる部分。"),
    ("707", "usage", "管（くだ／かん）— порожниста трубка або труба; читання залежить від сполуки. 水道管（すいどうかん）, 管を通す. 管を巻く（くだをまく）— буркотіти, повторюючи те саме, часто напідпитку. 筒 підкреслює циліндричну форму; не кожна трубка є провідником рідини.", "単独の管はくだと読む。複合語ではかんとなることが多い: 水道管（すいどうかん）。管を巻く（くだをまく）— буркотіти, повторюючи те саме, часто напідпитку. 筒 підкреслює циліндричну форму; не кожна трубка є провідником рідини."),
    ("708", "t", "рак — злоякісна пухлина; переносно — задавнена проблема, що підточує організацію", "рак — злоякісна пухлина; переносно — руйнівна вада, що підточує організацію")
]

EXPECTED = {
    "677": ("ホール", "", ["名詞"]),
    "683": ("マッサージ", "", ["名詞"]),
    "685": ("デザイン", "", ["名詞"]),
    "687": ("サポート", "", ["名詞"]),
    "691": ("ネックレス", "", ["名詞"]),
    "692": ("メロディー", "", ["名詞"]),
    "697": ("闇", "やみ", ["名詞"]),
    "701": ("沖", "おき", ["名詞"]),
    "703": ("核", "かく", ["名詞"]),
    "706": ("幹", "みき", ["名詞"]),
    "707": ("管", "くだ／かん", ["名詞"]),
    "708": ("癌", "がん", ["名詞"])
}
EXPECTED_EXAMPLES = {
    "677": ["式典は、市内の大ホールで盛大に開催された。", "ホールには、約五百人の聴衆が詰めかけた。"],
    "683": ["長時間のデスクワークで疲れた肩を、マッサージしてもらった。", "彼は、凝り固まった背中をマッサージしてもらった。"],
    "685": ["使いやすさを重視して、製品をデザインし直す方針だ。", "若手デザイナーがデザインした店舗が、業界で注目を集めた。"],
    "687": ["専任の担当者が、導入後のサポートを一貫して行う。", "同僚をサポートする姿勢が、チーム全体の生産性を高める。"],
    "691": ["彼女は、祖母から受け継いだネックレスを大切に身に着けている。", "展示会では、職人が手作りしたネックレスが人気を集めた。"],
    "692": ["映画の主題歌のメロディーが、聴く者の心に深く残った。", "会場の人々は、美しいメロディーに静かに聴き入った。"],
    "697": ["停電により、街全体が一瞬にして闇に包まれた。", "違法な闇取引を取り締まるため、当局は調査を強化している。"],
    "701": ["白い船がゆっくり沖を進んでいた。", "漁船は、沖に出たまま嵐に巻き込まれた。"],
    "703": ["この問題の核にあるのは、制度そのものの欠陥である。", "授業では、細胞の核の働きについて学んだ。"],
    "706": ["この大木の幹は、大人が三人でも抱えきれないほど太い。", "事業の幹となる部分を見極め、経営資源を集中させるべきだ。"],
    "707": ["老朽化した水道の管から漏水が相次ぎ、早急な交換が必要となっている。", "細い管を通して、容器に水を入れた。"],
    "708": ["彼は癌について書かれた本を読んだ。", "記事では、その制度を組織の癌と呼んでいた。"]
}

FIXED_IDS = ["677", "683", "685", "687", "691", "692", "697", "701", "703", "706", "707", "708"]
REVIEWED_IDS = []
PENDING_IDS = []
EXPECTED_CHANGED = FIXED_IDS
EVIDENCE = "completion/v188-acceptance.tsv; JLPT_N1_v188_audit.md"

def extract(source, name):
    match = re.search(r"\bconst " + re.escape(name) + r"\s*=\s*", source)
    if not match:
        raise RuntimeError("missing constant " + name)
    start = match.end()
    opening = source[start]
    closing = "]" if opening == "[" else "}"
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(source)):
        char = source[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        else:
            if char == '"':
                in_string = True
            elif char == opening:
                depth += 1
            elif char == closing:
                depth -= 1
                if depth == 0:
                    return start, index + 1, json.loads(source[start:index + 1])
    raise RuntimeError("unterminated constant " + name)

def counts(rows, kind=None):
    selected = [row for row in rows if kind is None or row["kind"] == kind]
    result = {status: sum(row["finalReview"] == status for row in selected) for status in ("reviewed", "fixed_rechecked", "pending")}
    result["total"] = len(selected)
    return result

WORK.mkdir(parents=True, exist_ok=True)
raw = BASE.read_bytes()
base_sha = hashlib.sha256(raw).hexdigest()
if base_sha != BASE_SHA:
    raise RuntimeError("unexpected v187 base SHA-256: " + base_sha)
base = raw.decode("utf-8")

_, _, vocab = extract(base, "DEFAULT_VOCAB")
_, _, grammar = extract(base, "GRAMMAR_DETAILS_BY_ID")
detail_start, detail_end, details = extract(base, "VOCAB_DETAILS_BY_ID")
_, _, pos_map = extract(base, "VOCAB_POS_BY_ID")
_, _, pairs = extract(base, "VOCAB_AUDITED_PAIRS")
_, _, meaning = extract(base, "REVIEWED_MEANING_QUIZZES")
_, _, reading = extract(base, "REVIEWED_READING_OPTIONS")
_, _, kana_targets = extract(base, "VOCAB_KANA_EXAMPLE_TARGETS")
_, _, example_targets = extract(base, "REVIEWED_EXAMPLE_TARGETS")

if (len(vocab), len(grammar), len(details), len(pairs)) != (3914, 130, 3914, 859):
    raise RuntimeError("protected inventory counts do not match v187")
by_id = {str(item["id"]): item for item in vocab}
scope = list(EXPECTED)
for card_id, (word, reading_value, expected_pos) in EXPECTED.items():
    item = by_id.get(card_id)
    if item is None or (item["w"], item["r"], pos_map[card_id]) != (word, reading_value, expected_pos):
        raise RuntimeError("identity/reading/POS mismatch for " + card_id)
    if details[card_id]["examples"] != EXPECTED_EXAMPLES[card_id]:
        raise RuntimeError("Japanese example preimage mismatch for " + card_id)

before = json.loads(json.dumps(details, ensure_ascii=False))
for card_id, field, old_value, new_value in UPDATES:
    if field.startswith("exampleTranslations["):
        index = int(re.search(r"\[(\d+)\]", field).group(1))
        actual = details[card_id]["exampleTranslations"][index]
        if actual != old_value:
            raise RuntimeError("translation preimage mismatch for " + card_id + "." + field)
        details[card_id]["exampleTranslations"][index] = new_value
    else:
        if details[card_id][field] != old_value:
            raise RuntimeError("field preimage mismatch for " + card_id + "." + field)
        details[card_id][field] = new_value

changed_cards = sorted((card_id for card_id in details if details[card_id] != before[card_id]), key=int)
if changed_cards != EXPECTED_CHANGED:
    raise RuntimeError("unexpected changed-card set: " + str(changed_cards))

allowed_fields = {
    "677": {"m", "exampleTranslations"},
    "683": {"exampleTranslations"},
    "685": {"exampleTranslations"},
    "687": {"exampleTranslations"},
    "691": {"exampleTranslations"},
    "692": {"exampleTranslations"},
    "697": {"t", "exampleTranslations"},
    "701": {"t"},
    "703": {"m"},
    "706": {"m"},
    "707": {"usage"},
    "708": {"t"}
}
for card_id in details:
    for field in before[card_id]:
        if before[card_id][field] != details[card_id][field] and field not in allowed_fields.get(card_id, set()):
            raise RuntimeError("unexpected field mutation: " + card_id + "." + field)
    if before[card_id]["examples"] != details[card_id]["examples"]:
        raise RuntimeError("Japanese example changed: " + card_id)

literal = json.dumps(details, ensure_ascii=False, separators=(",", ":"))
candidate = base[:detail_start] + literal + base[detail_end:]
old_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v187</title>"
new_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v188</title>"
if candidate.count(old_title) != 1:
    raise RuntimeError("version title marker mismatch")
candidate = candidate.replace(old_title, new_title, 1)
rollback = candidate.replace(new_title, old_title, 1).replace(literal, base[detail_start:detail_end], 1)
if rollback != base:
    raise RuntimeError("exact rollback failed")

protected = {
    "DEFAULT_VOCAB": vocab,
    "GRAMMAR_DETAILS_BY_ID": grammar,
    "VOCAB_POS_BY_ID": pos_map,
    "VOCAB_AUDITED_PAIRS": pairs,
    "REVIEWED_MEANING_QUIZZES": meaning,
    "REVIEWED_READING_OPTIONS": reading,
    "VOCAB_KANA_EXAMPLE_TARGETS": kana_targets,
    "REVIEWED_EXAMPLE_TARGETS": example_targets
}
for name, original in protected.items():
    _, _, after = extract(candidate, name)
    if after != original:
        raise RuntimeError("protected learning data changed: " + name)

OUT.write_bytes(candidate.encode("utf-8"))
candidate_sha = hashlib.sha256(OUT.read_bytes()).hexdigest()

register_rows = list(csv.DictReader(REGISTER.read_text(encoding="utf-8").splitlines()))
if len(register_rows) != 5847:
    raise RuntimeError("unexpected register row count: " + str(len(register_rows)))
baseline_all = {"reviewed": 3906, "fixed_rechecked": 103, "pending": 1838, "total": 5847}
baseline_vocab = {"reviewed": 3337, "fixed_rechecked": 102, "pending": 475, "total": 3914}
target_all = {"reviewed": 3906, "fixed_rechecked": 115, "pending": 1826, "total": 5847}
target_vocab = {"reviewed": 3337, "fixed_rechecked": 114, "pending": 463, "total": 3914}
current_all = counts(register_rows)
current_vocab = counts(register_rows, "vocab")
keys = [(row["kind"], row["key"]) for row in register_rows]
if len(keys) != len(set(keys)):
    raise RuntimeError("duplicate review-register keys")

rows_by_id = {}
for row in register_rows:
    if row["kind"] == "vocab" and row["key"] in scope:
        rows_by_id.setdefault(row["key"], []).append(row)
if any(len(rows_by_id.get(card_id, [])) != 1 for card_id in scope):
    raise RuntimeError("missing or duplicated register scope row")

register_mode = "already_applied"
register_changed = False
if current_all == baseline_all and current_vocab == baseline_vocab:
    for card_id in FIXED_IDS:
        row = rows_by_id[card_id][0]
        if row["finalReview"] != "pending" or row["evidence"]:
            raise RuntimeError("fixed preimage mismatch for " + card_id)
        row["finalReview"] = "fixed_rechecked"
        row["evidence"] = EVIDENCE
    register_mode = "applied_from_baseline"
    register_changed = True
elif current_all == target_all and current_vocab == target_vocab:
    for card_id in FIXED_IDS:
        row = rows_by_id[card_id][0]
        if row["finalReview"] != "fixed_rechecked":
            raise RuntimeError("fixed target mismatch for " + card_id)
        if row["evidence"] != EVIDENCE:
            row["evidence"] = EVIDENCE
            register_changed = True
else:
    raise RuntimeError("register state is neither v187 baseline nor expected v188 target")

if register_changed:
    with REGISTER.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["kind", "key", "baselineLocation", "finalReview", "evidence"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(register_rows)

after_all = counts(register_rows)
after_vocab = counts(register_rows, "vocab")
if after_all != target_all or after_vocab != target_vocab:
    raise RuntimeError("register target mismatch: " + str(after_all) + " / " + str(after_vocab))

prepare = {
    "pass": True,
    "base_version": "v187",
    "base_sha256": base_sha,
    "candidate_version": "v188",
    "candidate_sha256": candidate_sha,
    "candidate_bytes": OUT.stat().st_size,
    "vocabulary_records": len(vocab),
    "grammar_records": len(grammar),
    "lexical_pairs": len(pairs),
    "unique_vocabulary_ids": len({int(item["id"]) for item in vocab}),
    "review_scope": [int(card_id) for card_id in scope],
    "fixed_rechecked": [int(card_id) for card_id in FIXED_IDS],
    "reviewed_without_change": [],
    "pending_c11": [],
    "updated_fields": len(UPDATES),
    "changed_cards": [int(card_id) for card_id in changed_cards],
    "field_updates": [{"id": int(card_id), "field": field, "before": old, "after": new} for card_id, field, old, new in UPDATES],
    "author_credit_before": 3439,
    "author_credit_addition": 12,
    "author_credit_after": 3451,
    "protected_unchanged": {name: True for name in protected},
    "japanese_examples_unchanged": True,
    "exact_rollback": True,
    "register_updated": True,
    "register_mode": register_mode,
    "author_review_only": True
}
registry = {
    "pass": True,
    "register_rows": len(register_rows),
    "before": {"all": baseline_all, "vocabulary": baseline_vocab},
    "after": {"all": after_all, "vocabulary": after_vocab},
    "fixed_rechecked_ids": [int(card_id) for card_id in FIXED_IDS],
    "reviewed_ids": [],
    "pending_c11_ids": [],
    "author_credit_before": 3439,
    "author_credit_after": 3451,
    "duplicate_keys": 0,
    "records_deleted": 0,
    "history_rewritten": False
}
(WORK / "prepare-results.json").write_text(json.dumps(prepare, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(WORK / "registry-results.json").write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

checkpoint_path = WORK / "checkpoint.json"
checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
checkpoint["status"] = "author review complete; deterministic candidate and register prepared; Chromium verification pending"
checkpoint["candidate_sha256"] = candidate_sha
checkpoint["candidate_bytes"] = OUT.stat().st_size
checkpoint["exact_rollback"] = True
checkpoint["register_mode"] = register_mode
checkpoint_path.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({"pass": True, "candidate_sha256": candidate_sha, "candidate_bytes": OUT.stat().st_size, "fixed_rechecked": FIXED_IDS, "updated_fields": len(UPDATES), "register_after": after_all, "vocabulary_after": after_vocab}, ensure_ascii=False, indent=2))
