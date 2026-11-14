import copy, hashlib, json, re
from pathlib import Path

BASE = Path("JLPT_N1_ukrainian_reading_v228.html")
OUT = Path("JLPT_N1_ukrainian_reading_v229.html")
WORK = Path("completion/v229-work")
WORK.mkdir(parents=True, exist_ok=True)
BASE_SHA256 = "189e4f570d61556cbc9073cf67cc106958e44706b9feeecd1c51abbc096ff5e8"
OLD_TITLE = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v228</title>"
NEW_TITLE = "<title>JLPT N1 — ウクライナ語対応学習アプリ · v229</title>"

def extract_json_const(text, name):
    m = re.search(r"const\s+" + re.escape(name) + r"\s*=\s*", text)
    if not m:
        raise RuntimeError(f"missing JS constant: {name}")
    start = m.end()
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
        elif ch == '"':
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
    raise RuntimeError(f"unexpected v228 HTML SHA-256: {base_sha}")
base = base_bytes.decode("utf-8")

_, _, _, vocab = extract_json_const(base, "DEFAULT_VOCAB")
_, _, _, grammar = extract_json_const(base, "GRAMMAR_DETAILS_BY_ID")
_, _, _, details = extract_json_const(base, "VOCAB_DETAILS_BY_ID")
_, _, _, pos = extract_json_const(base, "VOCAB_POS_BY_ID")
_, _, _, pairs = extract_json_const(base, "VOCAB_AUDITED_PAIRS")
_, _, _, quizzes = extract_json_const(base, "REVIEWED_MEANING_QUIZZES")
_, _, _, reading_overrides = extract_json_const(base, "REVIEWED_READING_OPTIONS")
_, _, _, kana_targets = extract_json_const(base, "VOCAB_KANA_EXAMPLE_TARGETS")
_, _, _, example_targets = extract_json_const(base, "REVIEWED_EXAMPLE_TARGETS")

if (len(vocab), len(grammar), len(details), len(pos), len(pairs)) != (3914, 130, 3914, 3914, 859):
    raise RuntimeError("base record counts do not match approved scope")
if len({int(x["id"]) for x in vocab}) != 3914:
    raise RuntimeError("duplicate vocabulary IDs")
if len(reading_overrides) != 4:
    raise RuntimeError("unexpected baseline reviewed reading override count")

by_id = {str(x["id"]): x for x in vocab}
expected = {
    "2734": ("来る", "きたる", "動詞(一般)②", ["動詞"]),
    "544": ("いい加減", "いいかげん", "な形容詞①", ["ナ形"]),
    "550": ("わがまま", "わがまま", "な形容詞①", ["ナ形"]),
    "552": ("確か", "たしか", "な形容詞①", ["ナ形"]),
    "557": ("結構", "けっこう", "な形容詞①", ["ナ形"]),
    "588": ("独特", "どくとく", "な形容詞①", ["ナ形"]),
    "599": ("無礼", "ぶれい", "な形容詞①", ["ナ形"]),
    "644": ("当然", "とうぜん", "副詞(一般)①", ["副詞"]),
    "663": ("オーバー", "", "カタカナ①", ["名詞"]),
    "1631": ("相応", "そうおう", "名詞(2文字)", ["名詞"]),
    "3337": ("一切", "いっさい", "副詞(一般)②", ["副詞"]),
    "3345": ("散々", "さんざん", "副詞(一般)②", ["副詞"]),
}
for card_id, (word, reading, category, old_pos) in expected.items():
    row = by_id[card_id]
    if (row["w"], row.get("r", ""), row["c"], pos[card_id]) != (word, reading, category, old_pos):
        raise RuntimeError(f"unexpected baseline identity/category/POS for {card_id}")
    if card_id not in details or details[card_id]["w"] != word:
        raise RuntimeError(f"missing detail record for {card_id}")

old_644 = details["644"]
old_3345 = details["3345"]
old_3345_quiz = quizzes.get("v_3345")
if old_644["examples"] != [
    "法令を遵守することは、企業として当然の責務だ。",
    "当然のことながら、顧客の個人情報は厳重に管理されなければならない。"
]:
    raise RuntimeError("unexpected ID644 example baseline")
if old_3345["examples"][1] != "天候に恵まれず、散々な結果に終わった遠征だった。":
    raise RuntimeError("unexpected ID3345 example baseline")
if not old_3345_quiz or old_3345["examples"][1] not in old_3345_quiz.get("byExample", {}):
    raise RuntimeError("missing ID3345 reviewed byExample baseline")
if pos["2734"] != ["動詞"]:
    raise RuntimeError("unexpected ID2734 POS baseline")

before_details = copy.deepcopy(details)
before_pos = copy.deepcopy(pos)
before_quizzes = copy.deepcopy(quizzes)

# ID2734 is the lexicalized attributive きたる, not the ordinary verb くる.
# Keep DEFAULT_VOCAB.c unchanged: it is also used by the meaning-distractor grouping.
new_pos = copy.deepcopy(pos)
new_pos["2734"] = ["連体詞"]

new_details = copy.deepcopy(details)
new_details["644"]["examples"] = [
    "調査結果が異なれば、結論も当然変わってくる。",
    "当然、顧客の個人情報は厳重に管理されなければならない。"
]
new_details["644"]["exampleTranslations"] = [
    "Якщо результати дослідження різняться, то й висновок, природно, змінюється.",
    "Звісно, персональні дані клієнтів потрібно зберігати під суворим контролем."
]
new_details["644"]["usage"] = (
    "Основне прислівникове вживання: 当然、結果が変わる／当然そう思う — природно, звісно. "
    "Окреме 形動-вживання: 当然の結果／当然だ／当然の権利 — закономірний результат, це природно, належне право. "
    "Оцінює очікуваність або належність, а не просто підтверджує факт; もちろん частіше є відповіддю «звісно»."
)
new_sentence = "彼は会議で散々に批判され、反論できなかった。"
new_details["3345"]["examples"][1] = new_sentence
new_details["3345"]["exampleTranslations"][1] = "На нараді його жорстко розкритикували, і він не зміг заперечити."
new_details["3345"]["usage"] = (
    "散々議論を重ねる — дуже багато, до виснаження; "
    "散々に批判される — зазнати жорсткої критики; "
    "散々な結果 — украй поганий результат (形動-вживання). "
    "Не нейтральне схвалення ґрунтовності в усіх контекстах."
)

new_quizzes = copy.deepcopy(quizzes)
entry = new_quizzes["v_3345"]
entry["correct"] = "時間や労力を十分にかけ、徹底して何度も行う様子。"
entry["wrong"] = [
    "必要な部分だけを確認し、全体には踏み込まない様子。",
    "一度だけ短時間で済ませ、繰り返さない様子。",
    "論点を整理せず、話題を次々に変える様子。"
]
entry["note"] = "散々議論を重ねる — довго й ґрунтовно обговорювати; тут наголос на інтенсивності, не позитивній оцінці."
by_example = copy.deepcopy(entry.get("byExample", {}))
old_sentence = old_3345["examples"][1]
old_payload = by_example.pop(old_sentence)
by_example[new_sentence] = {
    "correct": "非常に厳しい非難を受けた様子。",
    "wrong": [
        "一部の点だけを穏やかに指摘された様子。",
        "批判を受けず、好意的に評価された様子。",
        "自分から相手の欠点を厳しく指摘した様子。"
    ],
    "note": "散々に批判される — зазнати дуже жорсткої критики; тут ідеться про оцінку з боку інших."
}
entry["byExample"] = by_example

# Manual meaning options address the automatic length cues and context drift found
# in the first Chromium diagnostic. These are content overrides only; no quiz logic changes.
const old_3337_by_example = copy.deepcopy(new_quizzes["v_3337"].get("byExample", {}))
const by_example_3337 = copy.deepcopy(old_3337_by_example)
const positive_3337 = "契約に関する費用は、一切こちらで負担いたします。"
const negative_3337 = "当社は、この件に一切関与しておりません。"
if positive_3337 not in by_example_3337:
    raise RuntimeError("missing ID3337 positive-context baseline")
by_example_3337[positive_3337] = {
    "correct": "必要な費用をすべて引き受けることを示す。",
    "wrong": [
        "必要な費用の一部だけを引き受けることを示す。",
        "必要な費用を相手と折半することを示す。",
        "必要な費用のうち、一定額だけを引き受けることを示す。"
    ],
    "note": "一切負担する — взяти на себе всі витрати; тут немає заперечення。"
}
by_example_3337[negative_3337] = {
    "correct": "後ろに否定を伴い、まったく関与していないことを示す。",
    "wrong": [
        "関与した範囲が限られ、部分的だったことを示す。",
        "以前は関与していたが、今は関与していないことを示す。",
        "関与する可能性が低く、ほとんど関わらないことを示す。"
    ],
    "note": "一切＋否定 — зовсім не причетний; не просто мала участь。"
}
new_quizzes["v_3337"]["byExample"] = by_example_3337

new_quizzes["v_2734"] = {
    "correct": "次に来る月日・行事や、これから訪れる事柄を示す。",
    "wrong": [
        "すでに過ぎた月日・行事や、過去の事柄を示す。",
        "現在進行中の月日・行事や、今の事柄を示す。",
        "毎年繰り返される月日・行事や、定例の事柄を示す。"
    ],
    "note": "来る（きたる）は「次の・近いうちの」。通常の動詞「来る（くる）」とは区別する。"
}
new_quizzes["v_544"] = {
    "correct": "責任や注意を欠き、仕事・内容が不十分である様子。",
    "wrong": [
        "必要な程度を守り、過不足なく適切に対応する様子。",
        "細部まで注意を払い、丁寧に仕上げる様子。",
        "量や程度が必要以上に大きく、誇張されている様子。"
    ],
    "note": "ここでは仕事ぶり・情報の評価。適度・ほどほどの意味ではない。"
}
new_quizzes["v_550"] = {
    "correct": "自分の都合や欲求を優先し、他人への配慮を欠く様子。",
    "wrong": [
        "自分の希望を抑え、周囲の都合に合わせる様子。",
        "自分の意見を率直に述べるが、他人の事情も尊重する様子。",
        "相手の希望を聞き入れ、その要求に応じる様子。"
    ],
    "note": "わがままな要求・振る舞い — власні бажання ставляться вище за інтереси інших."
}

new_quizzes["v_552"] = {
    "correct": "根拠や内容が確かで、信頼できる様子。",
    "wrong": [
        "根拠が不十分で、事実かどうか確認できない様子。",
        "必要な情報や資料が十分にそろっている様子。",
        "予測や計画がまだ定まっていない様子。"
    ],
    "note": "ここでは確かな根拠・腕前を表す形動用法。文末の「確か」=「якщо правильно пам’ятаю」とは区別する。"
}
new_quizzes["v_557"] = {
    "byExample": {
        "結構なお品をいただき、誠にありがとうございます。": {
            "correct": "質が高く、立派で好ましい様子。",
            "wrong": [
                "量や程度が十分で、これ以上必要ない様子。",
                "値段が高く、簡単には手に入らない様子。",
                "見た目が華やかで、よく目立つ様子。"
            ],
            "note": "結構なお品 — похвала якості або гідності речі; не значення «достатньо»."
        },
        "追加の資料は結構ですので、お気遣いなさらないでください。": {
            "correct": "それ以上は必要ないと、丁寧に断る表現。",
            "wrong": [
                "追加の資料をぜひ受け取りたいという表現。",
                "資料の内容を詳しく尋ねたいという表現。",
                "資料を早めに届けてほしいという表現。"
            ],
            "note": "資料は結構です — ввічлива відмова від додаткових матеріалів; не згода на отримання."
        }
    }
}
new_quizzes["v_588"] = {
    "correct": "他と異なり、そのものに特有の性質がある様子。",
    "wrong": [
        "他より優れていて、能力が高い様子。",
        "多くの人に共通し、特別な特徴がない様子。",
        "言動や外見に気品があり、上品な様子。"
    ],
    "note": "独特な視点・企業文化 — властива саме цьому об'єкту риса, не просто висока якість."
}
new_quizzes["v_599"] = {
    "correct": "礼儀に欠け、相手への敬意が足りない様子。",
    "wrong": [
        "相手に敬意を払い、礼儀正しく接する様子。",
        "相手の立場を考え、控えめに意見を述べる様子。",
        "言動に気品があり、上品で落ち着いた様子。"
    ],
    "note": "無礼な態度・言動 — бракує ввічливості й поваги до співрозмовника。"
}
new_quizzes["v_644"] = {
    "byExample": {
        "調査結果が異なれば、結論も当然変わってくる。": {
            "correct": "調査結果が違えば、結論も自然に変わるのが当たり前であること。",
            "wrong": [
                "調査結果が異なっても、結論を変える必要はないこと。",
                "調査結果を確認する前に、結論を決めておくこと。",
                "調査結果にかかわらず、同じ結論を選ぶこと。"
            ],
            "note": "当然変わってくる — результати природно впливають на висновок; це очікуваний наслідок。"
        },
        "当然、顧客の個人情報は厳重に管理されなければならない。": {
            "correct": "特別に説明しなくても、そうするのが自然で当然であること。",
            "wrong": [
                "個人情報の管理が望ましいが、必須ではないこと。",
                "個人情報の管理方法が、まだ決まっていないこと。",
                "個人情報を管理する必要性が、まだ明らかでないこと。"
            ],
            "note": "当然、〜なければならない — звісно, це належить робити; тут ідеться про самоочевидний обов’язок。"
        }
    }
}

new_quizzes["v_663"] = {
    "byExample": {
        "今月の経費が予算をオーバーしたため、原因を精査する必要がある。": {
            "correct": "決められた予算の上限を超えること。",
            "wrong": [
                "予算の範囲内に収まり、上限を超えないこと。",
                "支出の予定を立て、必要な金額を見積もること。",
                "予算を別の用途に振り替え、配分を変えること。"
            ],
            "note": "予算をオーバーする — перевищити затверджений бюджет。"
        },
        "時間をオーバーして会議が長引き、予定していた議題を消化できなかった。": {
            "correct": "決められた時間や予定の範囲を超えること。",
            "wrong": [
                "決められた時間内に会議を終えること。",
                "会議の開始時刻を予定より早めること。",
                "議題を減らして所要時間を短くすること。"
            ],
            "note": "時間をオーバーする — перевищити відведений час。ここでは「大げさ」の意味ではない。"
        }
    }
}
new_quizzes["v_1631"] = {
    "correct": "条件や程度が釣り合い、ふさわしいこと。",
    "wrong": [
        "条件や能力に対して不足し、見合っていないこと。",
        "条件や程度を必要以上に超えていること。",
        "相手の希望に合わせて、内容を変更すること。"
    ],
    "note": "相応する — відповідати умовам або рівню; не означає просто змінювати щось на чиєсь прохання。"
}

added_quiz_keys = {"v_2734", "v_544", "v_550", "v_552", "v_557", "v_588", "v_599", "v_644", "v_663", "v_1631"}

candidate = base
old_blocks, new_blocks = {}, {}
for name, value in [
    ("VOCAB_POS_BY_ID", new_pos),
    ("VOCAB_DETAILS_BY_ID", new_details),
    ("REVIEWED_MEANING_QUIZZES", new_quizzes),
]:
    candidate, old_literal, new_literal = replace_json_const(candidate, name, value)
    old_blocks[name] = old_literal
    new_blocks[name] = new_literal

if candidate.count(OLD_TITLE) != 1:
    raise RuntimeError("expected v228 title marker was not found exactly once")
candidate = candidate.replace(OLD_TITLE, NEW_TITLE, 1)

reverse = candidate.replace(NEW_TITLE, OLD_TITLE, 1)
for name in ["REVIEWED_MEANING_QUIZZES", "VOCAB_DETAILS_BY_ID", "VOCAB_POS_BY_ID"]:
    if reverse.count(new_blocks[name]) != 1:
        raise RuntimeError(f"cannot reverse {name} exactly")
    reverse = reverse.replace(new_blocks[name], old_blocks[name], 1)
if reverse != base:
    raise RuntimeError("v229 patch is not exactly reversible to v228")

# The only changed detail records are 644 and 3345; the only POS change is 2734;
# meaning-quiz additions are limited to the eight explicitly listed C11 overrides plus ID3345 byExample.
for key in before_details:
    if key not in {"644", "3345"} and before_details[key] != new_details[key]:
        raise RuntimeError(f"unexpected detail change at {key}")
for key in before_pos:
    if key != "2734" and before_pos[key] != new_pos[key]:
        raise RuntimeError(f"unexpected POS change at {key}")
for key in before_quizzes:
    if key != "v_3345" and before_quizzes[key] != new_quizzes[key]:
        raise RuntimeError(f"unexpected meaning-quiz change at {key}")
if set(new_quizzes) - set(before_quizzes) != added_quiz_keys:
    raise RuntimeError("unexpected added/removed reviewed meaning-quiz keys")
for name, before in [
    ("DEFAULT_VOCAB", vocab),
    ("GRAMMAR_DETAILS_BY_ID", grammar),
    ("VOCAB_AUDITED_PAIRS", pairs),
    ("REVIEWED_READING_OPTIONS", reading_overrides),
    ("VOCAB_KANA_EXAMPLE_TARGETS", kana_targets),
    ("REVIEWED_EXAMPLE_TARGETS", example_targets),
]:
    if extract_json_const(candidate, name)[3] != before:
        raise RuntimeError(f"protected block changed: {name}")

out_bytes = candidate.encode("utf-8")
OUT.write_bytes(out_bytes)
digest = hashlib.sha256(out_bytes).hexdigest()
blob_sha = hashlib.sha1(b"blob " + str(len(out_bytes)).encode() + b"\0" + out_bytes).hexdigest()

prepare = {
    "pass": True,
    "base_version": "v228",
    "base_main_sha": "bd66e3b3f01ae669bb4f3305d3f6652efb5d42f3",
    "base_html": BASE.name,
    "base_sha256": base_sha,
    "base_bytes": len(base_bytes),
    "candidate_version": "v229",
    "candidate_sha256": digest,
    "candidate_blob_sha": blob_sha,
    "candidate_bytes": len(out_bytes),
    "vocabulary_records": len(vocab),
    "grammar_records": len(grammar),
    "lexical_pairs": len(pairs),
    "unique_vocabulary_ids": len({int(x["id"]) for x in vocab}),
    "scope_ids": [2734, 544, 550, 552, 557, 588, 599, 644, 663, 1631, 3337, 3345],
    "pos_updates": {"2734": {"before": ["動詞"], "after": ["連体詞"]}},
    "detail_updates": {
        "644": ["examples[0]", "examples[1]", "exampleTranslations[0]", "exampleTranslations[1]", "usage"],
        "3345": ["examples[1]", "exampleTranslations[1]", "usage"]
    },
    "meaning_quiz_updates": {
        "v_3337": {"byExample_keys_before": sorted(old_3337_by_example), "byExample_keys_after": sorted(by_example_3337)},
        "v_3345": {"old_byExample_key": old_sentence, "new_byExample_key": new_sentence, "global_correct_updated": True},
        "added": sorted(added_quiz_keys)
    },
    "protected": {
        "DEFAULT_VOCAB": True,
        "GRAMMAR_DETAILS_BY_ID": True,
        "VOCAB_AUDITED_PAIRS": True,
        "REVIEWED_READING_OPTIONS": True,
        "VOCAB_KANA_EXAMPLE_TARGETS": True,
        "REVIEWED_EXAMPLE_TARGETS": True,
        "storage_keys_and_learning_engine": "byte-identical outside the three JSON blocks and document title"
    },
    "exact_rollback": True,
    "full_card_credit_pending_browser_and_manual_quiz_review": True
}
(WORK / "prepare-results.json").write_text(json.dumps(prepare, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

updates = [
    {"op":"replace","block":"VOCAB_POS_BY_ID","path":["2734"],"before":["動詞"],"after":["連体詞"],"reason":"ID2734 examples are the lexicalized attributive きたる; the display/quiz POS map must not label it as ordinary 動詞."},
    {"op":"replace","block":"VOCAB_DETAILS_BY_ID","path":["644","examples","exampleTranslations","usage"],"before":{"examples":old_644["examples"],"exampleTranslations":old_644["exampleTranslations"],"usage":old_644["usage"]},"after":{"examples":new_details["644"]["examples"],"exampleTranslations":new_details["644"]["exampleTranslations"],"usage":new_details["644"]["usage"]}},
    {"op":"replace","block":"VOCAB_DETAILS_BY_ID","path":["3345","examples[1]","exampleTranslations[1]","usage"],"before":{"examples[1]":old_3345["examples"][1],"exampleTranslations[1]":old_3345["exampleTranslations"][1],"usage":old_3345["usage"]},"after":{"examples[1]":new_details["3345"]["examples"][1],"exampleTranslations[1]":new_details["3345"]["exampleTranslations"][1],"usage":new_details["3345"]["usage"]}},
    {"op":"replace","block":"REVIEWED_MEANING_QUIZZES","path":["v_3345","correct","wrong","note"],"before":{"correct":old_3345_quiz["correct"],"wrong":old_3345_quiz["wrong"],"note":old_3345_quiz["note"]},"after":{"correct":new_quizzes["v_3345"]["correct"],"wrong":new_quizzes["v_3345"]["wrong"],"note":new_quizzes["v_3345"]["note"]}},
    {"op":"replace","block":"REVIEWED_MEANING_QUIZZES","path":["v_3345","byExample",old_sentence],"before":old_payload,"after":by_example[new_sentence]},
    {"op":"replace","block":"REVIEWED_MEANING_QUIZZES","path":["v_3337","byExample"],"before":old_3337_by_example,"after":by_example_3337}
]

for key in sorted(added_quiz_keys):
    updates.append({
        "op": "add",
        "block": "REVIEWED_MEANING_QUIZZES",
        "path": [key],
        "after": new_quizzes[key],
        "reason": "C11 manual meaning quiz: remove answer-length clues and/or use context-specific options for the card's selected sense."
    })

(WORK / "updates.json").write_text(json.dumps(updates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
checkpoint = {
    "checkpoint": "v229-c11-pos-map",
    "created": "2026-11-14",
    "base_main_sha": prepare["base_main_sha"],
    "base_html": BASE.name,
    "base_html_sha256": base_sha,
    "scope": prepare["scope_ids"],
    "prior_checkpoint": "work/v229-c11-pos-map",
    "prior_main_status": "v228 published; 28 C11 blockers; author credit 3885/3914",
    "guardrails": [
        "retain 3914 vocabulary records, 130 grammar constructions, 859 lexical pairs and every stable ID",
        "no changes to DEFAULT_VOCAB, grammar, lexical pairs, reading overrides, target tables or learning algorithms",
        "no changes to progress-storage keys or state schema",
        "only ID2734 POS map, ID644/3345 content, ID3345 byExample payload, and ten scoped reviewed meaning-quiz overrides are candidates",
        "do not force reading/cloze distractors where fewer than three valid choices exist",
        "keep v153 pilot credit limited to its documented ID121-320 scope"
    ],
    "status": "candidate prepared; awaiting Chromium and semantic quiz review before registry credit or publication",
    "candidate_sha256": digest,
    "candidate_blob_sha": blob_sha,
    "candidate_bytes": len(out_bytes)
}
(WORK / "checkpoint.json").write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(prepare, ensure_ascii=False, indent=2))
