import csv, hashlib, json, re
from pathlib import Path

BASE = Path("JLPT_N1_ukrainian_reading_v188.html")
OUT = Path("JLPT_N1_ukrainian_reading_v189.html")
WORK = Path("completion/v189-work")
REGISTER = Path("completion/review-register.csv")
BASE_SHA = "a115fbc8613d2916e9a3abcf732816e3c9853d1ae9811f02ee3c421f528bc885"

UPDATES = [
    ("712", "m", "順序や方向が反対であること。", "物事の順序・方向・結果・立場などが反対であること。"),
    ("712", "t", "протилежний напрям або порядок; 逆の — протилежний, 逆に — навпаки", "протилежний напрям, порядок, результат або позиція; 逆の — протилежний, 逆に — навпаки"),
    ("715", "m", "体の筋肉や腱。物事の道理や筋道。", "体の筋肉や腱。また、細長く続く線や筋状のもの。物事の道理や筋道。"),
    ("715", "usage", "筋を痛める — пошкодити сухожилля або м’язову тканину; 話の筋 — сюжет чи основний хід розповіді. 筋が通る — бути логічним і обґрунтованим; 筋が違う — питання поставлено не по суті або звернення недоречне. Не всі ці значення замінюються 筋肉.", "筋を痛める — пошкодити сухожилля або м’язову тканину; 筋のような線 — смуга або прожилка; 話の筋 — сюжет чи основний хід розповіді. 筋が通る — бути логічним і обґрунтованим; 筋が違う — бути невлучним/не по суті або суперечити належному порядку й моральним нормам; конкретний відтінок визначає контекст. Не всі ці значення замінюються 筋肉."),
    ("715", "exampleTranslations[1]", "У цій пропозиції порушено саму логіку справи, тому я не можу її прийняти.", "Ця пропозиція недоречна, тому я не можу її прийняти."),
    ("720", "m", "事柄、案件。", "事柄、案件。また、事柄や案件を数える助数詞。"),
    ("722", "m", "体の二つに分かれた部分。両足の付け根。", "胴から足が分かれる所。また、道や物が二つ以上に分かれる所。"),
    ("724", "t", "бруд, що накопичився на шкірі чи предметі; переносно — моральна скверна", "бруд або наліт, що накопичився на шкірі чи предметі; переносно — застарілі звички, заскорузлі порядки"),
    ("724", "exampleTranslations[0]", "Труби, в які в’ївся багаторічний бруд, ретельно очистили.", "Труби, на яких за багато років накопичився наліт, ретельно очистили."),
    ("731", "m", "敷地などを囲って仕切る囲い。", "敷地などの境界に設ける仕切り。"),
    ("731", "usage", "柵を設ける／越える — поставити або перелізти огорожу. 柵 часто має стовпці, рейки, дріт; не обов’язково суцільну стіну. 垣根 може бути живоплотом, 囲い — загальніша огорожа; конкретна конструкція визначає можливість заміни.", "柵を設ける／越える — поставити або перелізти огорожу. 柵 часто має стовпи, рейки або дріт; не обов’язково суцільну стіну. 垣根 може бути живоплотом, 囲い — загальніша огорожа; конкретна конструкція визначає можливість заміни."),
    ("739", "t", "ぬし — господар, власник, старожил; おも／しゅ — головне, провідне у відповідних сполуках", "ぬし — господар, власник, старожил; おも — головний, основний; しゅ — господар, володар; головний, основний у відповідних сполуках"),
    ("739", "exampleTranslations[1]", "Працівники шанують його як людину, що стала для цієї компанії справжнім старожилом.", "Працівники шанують його, вважаючи майже господарем компанії."),
    ("741", "t", "особлива атмосфера, смак чи чарівність; також зміст і обставини висловленого", "особлива атмосфера, колорит, чарівність; характер або стан справ; книжн. зміст, суть, задум (справи чи висловлення)"),
    ("741", "usage", "趣（おもむき）がある — мати особливий шарм або атмосферу; 趣を異にする — відрізнятися характером. Також повідомлений зміст у книжних висловах. 風情 близьке до естетичної атмосфери, 趣旨 — до задуму висловлення; не взаємозамінні в усіх значеннях.", "趣（おもむき）がある — мати особливий шарм або атмосферу; 趣を異にする — відрізнятися характером. Книжне 趣 може означати зміст, суть або задум справи; це окреме значення, не «обставини висловленого». 風情 близьке до естетичної атмосфери, 趣旨 — до задуму/мети висловлення; не взаємозамінні в усіх значеннях."),
    ("744", "t", "щит; опора, заступництво", "щит; прикриття, захист або виправдання; підтримка, заступництво (後ろ盾)"),
    ("745", "m", "水深が浅く、泥の多い水たまり。抜け出せない状況。", "湖より浅く、泥が多い水域。水草などが生えることが多い。また、俗に趣味などに深くのめり込み、抜け出せなくなる対象。"),
    ("745", "t", "неглибока мулиста водойма, заболочений ставок; переносно — ситуація, з якої важко вибратися", "неглибока мулиста водойма; переносно — ситуація, з якої важко вибратися; розм. — захоплення, у яке людина занурюється з головою"),
    ("745", "usage", "沼 — неглибока водойма з мулистим дном, часто із заростями; не будь-яка заболочена місцевість. 沼にはまる — загрузнути, буквально або переносно. 湿地 означає вологі заболочені землі; 泥沼 сильніше підкреслює трясовину й складність виходу.", "沼 — неглибока водойма з мулистим дном, часто із заростями; не будь-яка заболочена місцевість. 沼にはまる — загрузнути, буквально або переносно. 俗に趣味などに深くのめり込む対象を「沼」と呼ぶ: カメラ沼に落ちる — глибоко захопитися фотографією чи камерами. 湿地 означає вологі заболочені землі; 泥沼 сильніше підкреслює трясовину й складність виходу."),
    ("746", "m", "事実であることを示す根拠。", "事実や関係・存在を示す根拠やしるし。"),
    ("749", "exampleTranslations[1]", "Щиро перепрошую за те, що сталося.", "Щиро перепрошую.")
]

EXPECTED = {
    "712": ("逆", "ぎゃく", ["名詞"]),
    "715": ("筋", "すじ", ["名詞"]),
    "720": ("件", "けん", ["名詞"]),
    "722": ("股", "また", ["名詞"]),
    "724": ("垢", "あか", ["名詞"]),
    "731": ("柵", "さく", ["名詞"]),
    "739": ("主", "ぬし／おも／しゅ", ["名詞"]),
    "741": ("趣", "おもむき", ["名詞"]),
    "744": ("盾", "たて", ["名詞"]),
    "745": ("沼", "ぬま", ["名詞"]),
    "746": ("証", "あかし", ["名詞"]),
    "749": ("誠", "まこと", ["名詞"])
}
EXPECTED_EXAMPLES = {
    "712": ["期待とは逆の結果になったことで、現場には落胆が広がった。", "逆の立場から物事を見ることで、新たな気づきが得られる。"],
    "715": ["筋の通った説明をしなければ、関係者の納得は得られない。", "この話は、筋が違うので、受け入れることができない。"],
    "720": ["その件については、後日改めてご連絡いたします。", "同様の件が相次いで報告されており、調査が進められている。"],
    "722": ["彼は世界を股にかけて活躍する、国際的なビジネスマンだ。", "道が二股に分かれる地点で、一行は進路を巡って意見が割れた。"],
    "724": ["長年の垢が染みついた配管を、徹底的に洗浄した。", "古い体質の垢を落とすことが、組織改革の第一歩だ。"],
    "731": ["牧場の周囲には、動物が逃げ出さないよう柵が設けられている。", "工事現場は、安全のために高い柵で囲まれている。"],
    "739": ["この古い屋敷の主は、長年にわたって地域の発展に尽くしてきた。", "彼は、この会社の主のような存在として、社員から慕われている。"],
    "741": ["古い街並みが残るこの地域には、独特の趣がある。", "改装後の部屋は、以前とは趣が異なる。"],
    "744": ["担当者は規則を盾にして、相談にも応じなかった。", "兵士は盾を構え、飛んでくる矢を防いだ。"],
    "745": ["湖のほとりに沼が広がり、多様な生物が生息している。", "一度手を出すと抜け出せない、借金の沼にはまってしまった。"],
    "746": ["二人の絆の証として、結婚指輪を交換した。", "彼が生きた証は、後世に語り継がれるだろう。"],
    "749": ["誠をもって顧客に接する姿勢が、長年にわたる信頼関係を築いた。", "誠に申し訳ございませんでした。"]
}

FIXED_IDS = ["712", "715", "720", "722", "724", "731", "739", "741", "744", "745", "746", "749"]
REVIEWED_IDS = []
PENDING_IDS = []
EXPECTED_CHANGED = FIXED_IDS
EVIDENCE = "completion/v189-acceptance.tsv; JLPT_N1_v189_audit.md"

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
    raise RuntimeError("unexpected v188 base SHA-256: " + base_sha)
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
    raise RuntimeError("protected inventory counts do not match v188")
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
    "712": {"m", "t"},
    "715": {"m", "usage", "exampleTranslations"},
    "720": {"m"},
    "722": {"m"},
    "724": {"t", "exampleTranslations"},
    "731": {"m", "usage"},
    "739": {"t", "exampleTranslations"},
    "741": {"t", "usage"},
    "744": {"t"},
    "745": {"m", "t", "usage"},
    "746": {"m"},
    "749": {"exampleTranslations"}
}
for card_id in details:
    for field in before[card_id]:
        if before[card_id][field] != details[card_id][field] and field not in allowed_fields.get(card_id, set()):
            raise RuntimeError("unexpected field mutation: " + card_id + "." + field)
    if before[card_id]["examples"] != details[card_id]["examples"]:
        raise RuntimeError("Japanese example changed: " + card_id)

literal = json.dumps(details, ensure_ascii=False, separators=(",", ":"))
candidate = base[:detail_start] + literal + base[detail_end:]
old_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v188</title>"
new_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v189</title>"
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
baseline_all = {"reviewed": 3906, "fixed_rechecked": 115, "pending": 1826, "total": 5847}
baseline_vocab = {"reviewed": 3337, "fixed_rechecked": 114, "pending": 463, "total": 3914}
target_all = {"reviewed": 3906, "fixed_rechecked": 127, "pending": 1814, "total": 5847}
target_vocab = {"reviewed": 3337, "fixed_rechecked": 126, "pending": 451, "total": 3914}
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
    raise RuntimeError("register state is neither v188 baseline nor expected v189 target")

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
    "base_version": "v188",
    "base_sha256": base_sha,
    "candidate_version": "v189",
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
    "author_credit_before": 3451,
    "author_credit_addition": 12,
    "author_credit_after": 3463,
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
    "author_credit_before": 3451,
    "author_credit_after": 3463,
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
