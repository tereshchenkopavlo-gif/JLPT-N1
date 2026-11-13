import hashlib
import json
import re
from pathlib import Path

BASE = Path("JLPT_N1_ukrainian_reading_v183.html")
OUT = Path("JLPT_N1_ukrainian_reading_v184.html")
WORK = Path("completion/v184-work")
WORK.mkdir(parents=True, exist_ok=True)
BASE_SHA256 = "ef4705c65cf358f167cbd31400c7b69ad7419e6d4210768c5135b3225230be2e"

UPDATES = [
    {"id": "485", "field": "exampleTranslations[0]",
     "before": "Створюють консультаційне вікно й уважно вислуховують користувачів.",
     "after": "Створюють консультаційний пункт і уважно вислуховують думки користувачів."},
    {"id": "488", "field": "m",
     "before": "色を、付ける。ある状態や行為に、関わる。",
     "after": "染料などを使って色を付ける。また、「手を染める」の形で、ある事に取りかかる。"},
    {"id": "488", "field": "usage",
     "before": "Перехідне 一段: 布／髪を色に染める. Надати кольору. У сталому 悪事に手を染める — почати займатися негідною справою; колір тут не буквальний. Неперехідне 染まる. 彩る ширше — прикрашати кольором чи надавати виразності.",
     "after": "Перехідне 一段: 布を藍で染める／髪を赤く染める. Надавати предмету певного кольору. У сталому 悪事に手を染める — почати займатися негідною справою; колір тут не буквальний. Неперехідне 染まる. 彩る ширше — прикрашати кольором чи надавати виразності."},
    {"id": "489", "field": "m",
     "before": "目標を定めて、そこに当てようとする。",
     "after": "目標や対象を定めてそこを目指す。また、何かを手に入れたり実現したりする機会をうかがう。"},
    {"id": "491", "field": "m",
     "before": "裁判所に、申し立てる。人々に、働きかけて理解を求める。",
     "after": "裁判所などに申し立てる。また、人々に働きかけて理解や賛同を求める。苦痛や不満を言葉で伝える。感覚や感情に強く働きかける。"},
    {"id": "496", "field": "exampleTranslations[0]",
     "before": "Нагальне завдання — підготувати людей, які визначатимуть майбутнє наступного покоління.",
     "after": "Нагальним завданням стало підготувати фахівців, які візьмуть на себе відповідальність за наступне покоління."},
    {"id": "498", "field": "exampleTranslations[1]",
     "before": "Переглядають коло ділових партнерів, щоб розірвати зв’язки з махінаціями.",
     "after": "Переглядають коло ділових партнерів, щоб припинити будь-яку причетність до неправомірних дій."},
    {"id": "499", "field": "t",
     "before": "відмовляти в проханні чи пропозиції; також попередньо повідомляти або застерігати",
     "after": "відмовляти в проханні чи пропозиції; також заздалегідь повідомляти про обставини або просити дозволу"},
    {"id": "504", "field": "exampleTranslations[0]",
     "before": "Перед початком роботи я міцно затягнув болти, щоб переконатися, що вони не ослабли.",
     "after": "Перед початком роботи я міцно затягнув болти, щоб вони не послабилися."},
    {"id": "504", "field": "exampleTranslations[1]",
     "before": "Наприкінці місяця бухгалтерія підбиває облік і звітує перед правлінням.",
     "after": "Наприкінці місяця відділ бухгалтерії закриває бухгалтерські книги й звітує перед правлінням."},
    {"id": "510", "field": "exampleTranslations[1]",
     "before": "За заслугу в розв’язанні давньої проблеми його підвищили до члена правління.",
     "after": "За успішне врегулювання давньої проблеми його підвищили до посади члена правління."},
    {"id": "524", "field": "exampleTranslations[1]",
     "before": "Деякі споживачі швидко втрачають інтерес до нових продуктів, тому компанії шукають способи зацікавити їх надовго.",
     "after": "Деякі споживачі швидко втрачають інтерес до нових продуктів, тому компанії шукають способи, щоб вони користувалися ними довше."}
]

def extract_json_const(text, name):
    match = re.search(r"\bconst " + re.escape(name) + r"\s*=\s*", text)
    if not match:
        raise RuntimeError(f"missing JS constant: {name}")
    start = match.end()
    if text[start] not in "[{":
        raise RuntimeError(f"{name} is not a JSON array/object")
    opening = text[start]
    closing = "]" if opening == "[" else "}"
    depth = 0
    in_string = False
    escaped = False
    end = None
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == opening:
            depth += 1
        elif ch == closing:
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        raise RuntimeError(f"unterminated JSON constant: {name}")
    literal = text[start:end]
    return start, end, literal, json.loads(literal)

def replace_json_const(text, name, value):
    start, end, old_literal, _ = extract_json_const(text, name)
    new_literal = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return text[:start] + new_literal + text[end:], old_literal, new_literal

base_bytes = BASE.read_bytes()
base_sha = hashlib.sha256(base_bytes).hexdigest()
if base_sha != BASE_SHA256:
    raise RuntimeError(f"unexpected v183 HTML SHA-256: {base_sha}")
base = base_bytes.decode("utf-8")

_, _, _, vocab = extract_json_const(base, "DEFAULT_VOCAB")
_, _, _, grammar = extract_json_const(base, "GRAMMAR_DETAILS_BY_ID")
_, _, _, details = extract_json_const(base, "VOCAB_DETAILS_BY_ID")
_, _, _, pos = extract_json_const(base, "VOCAB_POS_BY_ID")
_, _, _, pairs = extract_json_const(base, "VOCAB_AUDITED_PAIRS")
_, _, _, meaning_quizzes = extract_json_const(base, "REVIEWED_MEANING_QUIZZES")
_, _, _, reading_options = extract_json_const(base, "REVIEWED_READING_OPTIONS")
_, _, _, kana_targets = extract_json_const(base, "VOCAB_KANA_EXAMPLE_TARGETS")
_, _, _, example_targets = extract_json_const(base, "REVIEWED_EXAMPLE_TARGETS")

if len(vocab) != 3914 or len(grammar) != 130 or len(details) != 3914 or len(pairs) != 859:
    raise RuntimeError("base record counts do not match the approved scope")
ids = [int(x["id"]) for x in vocab]
if len(set(ids)) != 3914 or len(pos) != 3914 or set(map(str, ids)) != set(details):
    raise RuntimeError("base vocabulary IDs/POS/details are not complete and unique")

by_id = {str(x["id"]): x for x in vocab}
expected = {
    "485": ("設ける", "もうける", ["動詞"]),
    "488": ("染める", "そめる", ["動詞"]),
    "489": ("狙う", "ねらう", ["動詞"]),
    "491": ("訴える", "うったえる", ["動詞"]),
    "496": ("担う", "になう", ["動詞"]),
    "498": ("断つ", "たつ", ["動詞"]),
    "499": ("断る", "ことわる", ["動詞"]),
    "501": ("調える", "ととのえる", ["動詞"]),
    "503": ("通じる", "つうじる", ["動詞"]),
    "504": ("締める", "しめる", ["動詞"]),
    "510": ("片付ける", "かたづける", ["動詞"]),
    "524": ("飽きる", "あきる", ["動詞"]),
}
for card_id, (word, reading, expected_pos) in expected.items():
    item = by_id[card_id]
    if (item["w"], item["r"], pos[card_id]) != (word, reading, expected_pos):
        raise RuntimeError(f"unexpected card identity/POS for ID {card_id}: {item['w']} {item['r']} {pos[card_id]}")

before_details = json.loads(json.dumps(details, ensure_ascii=False))
field_updates = []
for update in UPDATES:
    card_id = update["id"]
    field = update["field"]
    if field.startswith("exampleTranslations["):
        index = int(field.split("[")[1].split("]")[0])
        actual = details[card_id]["exampleTranslations"][index]
        if actual != update["before"]:
            raise RuntimeError(f"unexpected preimage for ID {card_id}.{field}")
        details[card_id]["exampleTranslations"][index] = update["after"]
    else:
        actual = details[card_id][field]
        if actual != update["before"]:
            raise RuntimeError(f"unexpected preimage for ID {card_id}.{field}")
        details[card_id][field] = update["after"]
    field_updates.append({
        "id": int(card_id), "field": field,
        "before": update["before"], "after": update["after"]
    })

changed_ids = {key for key in details if details[key] != before_details[key]}
expected_changed_ids = {"485", "488", "489", "491", "496", "498", "499", "504", "510", "524"}
if changed_ids != expected_changed_ids:
    raise RuntimeError(f"unexpected changed card IDs: {sorted(changed_ids)}")
allowed_fields = {
    "485": {"exampleTranslations"},
    "488": {"m", "usage"},
    "489": {"m"},
    "491": {"m"},
    "496": {"exampleTranslations"},
    "498": {"exampleTranslations"},
    "499": {"t"},
    "504": {"exampleTranslations"},
    "510": {"exampleTranslations"},
    "524": {"exampleTranslations"},
}
for card_id in details:
    old = before_details[card_id]
    new = details[card_id]
    for field in old:
        if old[field] != new[field] and field not in allowed_fields.get(card_id, set()):
            raise RuntimeError(f"unexpected field change on ID {card_id}: {field}")
    if old["examples"] != new["examples"]:
        raise RuntimeError(f"Japanese examples changed on ID {card_id}")

candidate, old_literal, new_literal = replace_json_const(base, "VOCAB_DETAILS_BY_ID", details)
old_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v183</title>"
new_title = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v184</title>"
if candidate.count(old_title) != 1:
    raise RuntimeError("expected v183 title marker was not found exactly once")
candidate = candidate.replace(old_title, new_title, 1)

reverse = candidate.replace(new_title, old_title, 1)
if reverse.count(new_literal) != 1:
    raise RuntimeError("cannot reverse VOCAB_DETAILS_BY_ID exactly")
reverse = reverse.replace(new_literal, old_literal, 1)
if reverse != base:
    raise RuntimeError("v184 patch is not exactly reversible to v183")

for name, before_value in [
    ("DEFAULT_VOCAB", vocab),
    ("GRAMMAR_DETAILS_BY_ID", grammar),
    ("VOCAB_POS_BY_ID", pos),
    ("VOCAB_AUDITED_PAIRS", pairs),
    ("REVIEWED_MEANING_QUIZZES", meaning_quizzes),
    ("REVIEWED_READING_OPTIONS", reading_options),
    ("VOCAB_KANA_EXAMPLE_TARGETS", kana_targets),
    ("REVIEWED_EXAMPLE_TARGETS", example_targets),
]:
    _, _, _, after_value = extract_json_const(candidate, name)
    if after_value != before_value:
        raise RuntimeError(f"dependent constant unexpectedly changed: {name}")

out_bytes = candidate.encode("utf-8")
OUT.write_bytes(out_bytes)
digest = hashlib.sha256(out_bytes).hexdigest()
prepare = {
    "pass": True,
    "base_version": "v183",
    "base_sha256": base_sha,
    "base_bytes": len(base_bytes),
    "candidate_version": "v184",
    "candidate_sha256": digest,
    "candidate_bytes": len(out_bytes),
    "vocabulary_records": len(vocab),
    "grammar_records": len(grammar),
    "lexical_pairs": len(pairs),
    "unique_vocabulary_ids": len(set(ids)),
    "review_scope": [485, 488, 489, 491, 496, 498, 499, 501, 503, 504, 510, 524],
    "author_credit_before": 3399,
    "author_credit_addition": 12,
    "author_credit_after": 3411,
    "reviewed_without_change": [501, 503],
    "fixed_rechecked": [485, 488, 489, 491, 496, 498, 499, 504, 510, 524],
    "field_updates": field_updates,
    "updated_fields": len(field_updates),
    "changed_blocks": ["VOCAB_DETAILS_BY_ID", "document title"],
    "unchanged": {
        "vocabulary_records": True,
        "grammar_records": True,
        "lexical_pairs": True,
        "all_ids": True,
        "pos_map": True,
        "japanese_examples": True,
        "reading_quiz_targets": True,
        "meaning_quizzes": True,
        "reading_overrides": True,
        "example_targets": True,
        "learning_engine": True,
        "progress_storage_code": True
    },
    "exact_rollback": True,
    "author_review_only": True
}
(WORK / "prepare-results.json").write_text(json.dumps(prepare, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(prepare, ensure_ascii=False, indent=2))
