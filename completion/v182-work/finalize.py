import csv
import json
import shutil
from collections import Counter
from pathlib import Path

WORK = Path("completion/v182-work")
prepare = json.loads((WORK / "prepare-results.json").read_text(encoding="utf-8"))
browser = json.loads((WORK / "browser-results.json").read_text(encoding="utf-8"))
diagnostic = json.loads(Path("completion/v180-c11-diagnostics.json").read_text(encoding="utf-8"))
html_sha = prepare["candidate_sha256"]

if not prepare.get("pass") or not prepare.get("exact_rollback"):
    raise RuntimeError("v182 deterministic preparation failed")
if not browser.get("pass") or browser.get("candidate_sha256") != html_sha:
    raise RuntimeError("v182 browser regression failed or SHA mismatch")
if browser.get("reading_pool_count") != 23 or browser.get("reading_pool_min_options", 0) < 3 or browser.get("automatic_pool_checks") != 20:
    raise RuntimeError("v182 reading-pool regression totals changed")
if len(browser.get("manual_overrides", [])) != 3 or not all(x.get("unique") for x in browser["manual_overrides"]):
    raise RuntimeError("v182 manual reading overrides failed uniqueness")
if browser.get("pos_tradeoff", {}).get("currentClozeCandidates") != 64 or browser.get("pos_tradeoff", {}).get("combinedClozeCandidates") != 2:
    raise RuntimeError("v182 POS/cloze tradeoff result changed")
if browser.get("combined_pos_pool_impact", {}).get("changedPoolCount") != 0:
    raise RuntimeError("unexpected reading-pool impact from hypothetical extra 副詞 tag")
if browser.get("storage", {}).get("sentinelRoundTrip") is not True or browser.get("storage", {}).get("storageRestored") is not True:
    raise RuntimeError("progress storage round-trip failed")
if browser.get("pageErrors") != [] or any(x.get("overflow") for x in browser.get("responsive", [])):
    raise RuntimeError("browser page errors or responsive overflow")
if prepare.get("vocabulary_records") != 3914 or prepare.get("unique_vocabulary_ids") != 3914 or prepare.get("grammar_records") != 130 or prepare.get("lexical_pairs") != 859:
    raise RuntimeError("v182 data counts changed")
if not diagnostic.get("pass") or len(diagnostic.get("data", {}).get("readingPools", {}).get("pools", [])) != 23:
    raise RuntimeError("v180 diagnostic evidence missing or incomplete")

# Build the individual pool review from the frozen v180 diagnostic and v182 browser decisions.
manual = {int(x["id"]): x["wrong"] for x in browser["manual_overrides"]}
pools = diagnostic["data"]["readingPools"]["pools"]
with Path("completion/v182-reading-pool-review.tsv").open("w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f, delimiter="\t", lineterminator="\n")
    writer.writerow(["id", "word", "reading", "before_count", "before_options", "automatic_after_count", "automatic_after_options", "manual_override", "final_wrong_count", "decision", "note"])
    for p in pools:
        pid = int(p["id"])
        item = next((x for x in browser["manual_overrides"] if int(x["id"]) == pid), None)
        before = p["before"]["automaticOptions"]
        after = p["after"]["automaticOptions"]
        if pid in manual:
            decision = "manual_override_reviewed"
            note = "Three unique verified distractors stored in REVIEWED_READING_OPTIONS; exact target reading excluded."
            final_wrong = manual[pid]
        elif pid == 359:
            decision = "automatic_pool_gained"
            note = "Correct POS for 浮気 adds うわき as a third valid distractor for 本気."
            final_wrong = after
        else:
            decision = "automatic_pool_retained"
            note = "Three or more unique automatic distractors retained; browser matched the frozen diagnostic."
            final_wrong = after
        writer.writerow([pid, p["word"], p["reading"], len(p["before"]["automaticOptions"]), " / ".join(before), len(after), " / ".join(after), " / ".join(manual.get(pid, [])), len(final_wrong), decision, note])

register_path = Path("completion/review-register.csv")
with register_path.open(encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)
if fieldnames != ["kind", "key", "baselineLocation", "finalReview", "evidence"]:
    raise RuntimeError(f"unexpected review-register schema: {fieldnames}")
before = Counter(r["finalReview"] for r in rows)
if before.get("reviewed") != 3893 or before.get("fixed_rechecked") != 59 or before.get("pending") != 1892:
    raise RuntimeError(f"unexpected pre-v182 register counts: {dict(before)}")

for card_id in ("255", "327"):
    matches = [r for r in rows if r["kind"] == "vocab" and r["key"] == card_id]
    if len(matches) != 1 or matches[0]["finalReview"] != "pending":
        raise RuntimeError(f"vocab ID {card_id} is not exactly one pending row")
    matches[0]["finalReview"] = "fixed_rechecked"
    matches[0]["evidence"] = f"completion/v182-c10-review.tsv#{card_id}; POS/usage corrected and full card fields rechecked; v182 HTML SHA-256={html_sha}"

for key, card_id, word, reading in [
    ("r_255", "255", "直接", "ちょくせつ"),
    ("r_327", "327", "浮気", "うわき"),
    ("r_1819", "1819", "内訳", "うちわけ")
]:
    if any(r["kind"] == "reviewed_reading_quiz" and r["key"] == key for r in rows):
        raise RuntimeError(f"reading quiz {key} already exists")
    rows.append({
        "kind": "reviewed_reading_quiz",
        "key": key,
        "baselineLocation": f"REVIEWED_READING_OPTIONS.{card_id}",
        "finalReview": "reviewed",
        "evidence": f"completion/v182-reading-pool-review.tsv#{card_id}; three distinct verified distractors for {word}/{reading}; v182 HTML SHA-256={html_sha}"
    })

after = Counter(r["finalReview"] for r in rows)
if after.get("reviewed") != 3896 or after.get("fixed_rechecked") != 61 or after.get("pending") != 1890 or len(rows) != 5847:
    raise RuntimeError(f"unexpected post-v182 register counts: {dict(after)}, rows={len(rows)}")
kind_counts = Counter(r["kind"] for r in rows)
expected_kinds = {"vocab":3914,"grammar":130,"vocab_pair":859,"grammar_pair":92,"antonym_pair":41,"reading":160,"reading_question":381,"reviewed_meaning_quiz":267,"reviewed_reading_quiz":3}
for kind, expected in expected_kinds.items():
    if kind_counts.get(kind) != expected:
        raise RuntimeError(f"unexpected object count for {kind}: {kind_counts.get(kind)} != {expected}")
vocab_counts = Counter(r["finalReview"] for r in rows if r["kind"] == "vocab")
if vocab_counts.get("reviewed") != 3327 or vocab_counts.get("fixed_rechecked") != 60 or vocab_counts.get("pending") != 527:
    raise RuntimeError(f"unexpected vocabulary slice counts: {dict(vocab_counts)}")

with register_path.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)

shutil.copyfile(WORK / "prepare-results.json", "completion/v182-prepare-results.json")
shutil.copyfile(WORK / "browser-results.json", "completion/v182-browser-results.json")

registry = {
    "pass": True,
    "total_objects": len(rows),
    "status_counts": dict(after),
    "kind_counts": dict(kind_counts),
    "vocabulary_status_counts": dict(vocab_counts),
    "author_vocabulary_credit": 3387,
    "reviewed_meaning_quiz": 267,
    "reviewed_reading_quiz": 3,
    "v182_added": {
        "vocab_fixed_rechecked": [255, 327],
        "reviewed_reading_quiz": ["r_255", "r_327", "r_1819"]
    },
    "no_duplicate_rows": True,
    "html_sha256": html_sha
}
Path("completion/v182-registry-results.json").write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

with Path("completion/v182-c10-review.tsv").open("w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f, delimiter="\t", lineterminator="\n")
    writer.writerow(["id","word","reading","pos_before","pos_after","fields_rechecked","decision","source","note"])
    writer.writerow(["255","直接","ちょくせつ","名詞","名詞|ナ形","definition; reading; 2 Japanese examples; 2 Ukrainian translations; usage","fixed_rechecked","Kotobank Digital Daijisen; NINJAL cross-check","Daijisen supports 名・形動 and 直接な（の）交渉; adverbial use is recorded in usage. Adding 副詞 as a third app POS tag would reduce cloze candidates from 64 to 2, so the app retains 名詞+ナ形."])
    writer.writerow(["327","浮気","うわき","名詞","名詞|ナ形","definition; reading; 2 Japanese examples; 2 Ukrainian translations; usage","fixed_rechecked","Kotobank Digital Daijisen","Modern うわき is 名・形動; historical ふき is not used as a distractor."])

with Path("completion/v182-acceptance.tsv").open("w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f, delimiter="\t", lineterminator="\n")
    writer.writerow(["object_type","id","decision","credit_effect","evidence"])
    writer.writerow(["vocab","255","fixed_rechecked","+1 accepted vocabulary card","completion/v182-c10-review.tsv#255"])
    writer.writerow(["vocab","327","fixed_rechecked","+1 accepted vocabulary card","completion/v182-c10-review.tsv#327"])
    writer.writerow(["reviewed_reading_quiz","r_255","reviewed","no additional card credit","completion/v182-reading-pool-review.tsv#255"])
    writer.writerow(["reviewed_reading_quiz","r_327","reviewed","no additional card credit","completion/v182-reading-pool-review.tsv#327"])
    writer.writerow(["reviewed_reading_quiz","r_1819","reviewed","no additional card credit","completion/v182-reading-pool-review.tsv#1819"])

audit = f"""# JLPT N1 v182 — авторський аудит і технічне приймання

Дата: 13 листопада 2026 року.

## Авторські рішення

- ID255 直接: POS виправлено з 名詞 на 名詞 + ナ形; usage уточнено, додано формальне 直接な交渉 та розмежовано 直接の / 直接的な. Повністю повторно перевірено дефініцію, читання, обидва японські приклади, українські переклади й usage. Зараховано fixed_rechecked.
- ID327 浮気: POS виправлено з 名詞 на 名詞 + ナ形; usage уточнено для іменникового, な-прикметникового та する-вживання. Повністю повторно перевірено дефініцію, читання, обидва японські приклади й переклади. Зараховано fixed_rechecked.
- ID1819 内訳: картка не змінювалася; додано лише reading-quiz override. Повнокартковий credit не змінюється.
- ID359 本気: картка не змінювалася; після POS-корекції 浮気 автоматичний пул отримує うわき як додатковий дистрактор. Повнокартковий credit не змінюється.

## POS джерела й обмеження тренажера

Kotobank Digital Daijisen позначає 直接 як 名・形動, наводить 直接な（の）交渉 і зазначає прислівникове вживання. NINJAL CHOKUSETSU позначає 直接 як 名・副 і розрізняє 直接的 як 形動. Це різні словникові класифікації, а не доказ помилки одного джерела. У тренажері збережено 名詞 + ナ形, а прислівникове вживання зафіксовано в usage. Окремий браузерний тест показав: cloze-пул має 64 кандидати з поточним набором POS, але лише 2, якщо додати 副詞 як третій тег; це нижче мінімуму 3. Тому третій тег не додано, щоб не погіршити чинний механізм вправ. Це app-specific рішення, не твердження, що 直接 не може мати прислівникового вживання.

## Reading-pool review

Перевірено всі 23 пули з v180 діагностики. 20 автоматичних пулів зберегли мінімум три унікальні дистрактори; ID359 отримав うわき як третій варіант; для ID255, ID327 та ID1819 збережено три ручні overrides. Усі дистрактори — реальні читання інших наявних карток, не дорівнюють правильному читанню. Browser підтвердив мінімум три опції в усіх пулах, унікальність і виключення правильної відповіді. Повний перелік: completion/v182-reading-pool-review.tsv.

## Технічні перевірки

- Детермінований patch має точний rollback до v181; змінено лише два POS-значення, два usage-поля, три записи REVIEWED_READING_OPTIONS і заголовок версії.
- Збережено 3914 словникових записів та ID, 130 граматичних конструкцій, 859 лексичних пар, алгоритми reading/cloze і progress storage.
- Chromium: 23 reading-пули, 20 автоматичних перевірок, 3 ручні overrides; cloze ID255/327/359 — 64 кандидати, ID1819 — 2270; обидва приклади ID255/327 зберегли literal cloze eligibility.
- Перевірено контрольний запис progress storage, відсутність JS-помилок і горизонтального переповнення на 360/412/1280 px.
- Реєстр: 5847 об'єктів; 3896 reviewed /61 fixed_rechecked /1890 pending. Словниковий зріз: 3327 /60 /527. Авторський credit: 3387/3914. Reviewed meaning quiz: 267; reviewed reading quiz: 3.

## Джерела

- Kotobank Digital Daijisen, 直接: https://kotobank.jp/word/%E7%9B%B4%E6%8E%A5-569297
- NINJAL CHOKUSETSU: https://mmsrv.ninjal.ac.jp/kamus/data/item315.html
- Kotobank Digital Daijisen, 浮気: https://kotobank.jp/word/%E6%B5%AE%E6%B0%97-442377
- Kotobank Digital Daijisen, 内訳: https://kotobank.jp/word/%E5%86%85%E8%A8%B3-440704

## Межі приймання

Це авторський аудит і технічна регресія, не незалежне лінгвістичне приймання. Фізичне Android/Windows та правове/походження приймання залишаються відкритими.
"""
Path("JLPT_N1_v182_audit.md").write_text(audit, encoding="utf-8")

readme_path=Path("README.md")
readme=readme_path.read_text(encoding="utf-8")
history_marker="Нижче збережено історичний журнал v18–v26; він не описує поточний стан."
if history_marker not in readme:
    raise RuntimeError("README history marker missing")
history=readme[readme.index(history_marker):]
header=f"""# JLPT N1 — тренажер з японським інтерфейсом

Актуальна v182. Виправлено POS і usage для ID255 直接 та ID327 浮気; збережено три reviewed reading-quiz overrides для ID255/327/1819. [Повний HTML](JLPT_N1_ukrainian_reading_v182.html) · [Аудит](JLPT_N1_v182_audit.md)

Збережено 3914 словникових записів, 130 граматичних конструкцій і 859 лексичних пар. Авторський credit — 3387/3914; реєстр — 3896 reviewed /61 fixed_rechecked /1890 pending; reviewed meaning quiz — 267; reviewed reading quiz — 3. Незалежне, фізичне й правове/походження приймання не завершені.

Докази v182: completion/v182-prepare-results.json, completion/v182-browser-results.json, completion/v182-registry-results.json, completion/v182-reading-pool-review.tsv.

"""
readme_path.write_text(header+history,encoding="utf-8")

status_path=Path("PROJECT_STATUS.md")
status=status_path.read_text(encoding="utf-8")
current_marker="## Поточний випуск v181"
archive_marker="## Архівований випуск v179"
if current_marker not in status or archive_marker not in status:
    raise RuntimeError("PROJECT_STATUS v181/archive markers missing")
ci,ai=status.index(current_marker),status.index(archive_marker)
archived_v181=status[ci:ai].replace("## Поточний випуск v181","## Архівований випуск v181",1).strip()
older=status[ai:]
status_header=f"""# PROJECT_STATUS.md — JLPT N1

Оновлено 13 листопада 2026. Актуальна v182 у main. Повний HTML — {prepare['candidate_bytes']:,} байт, SHA-256 {html_sha}. [Повний HTML](JLPT_N1_ukrainian_reading_v182.html) · [Аудит](JLPT_N1_v182_audit.md).

## Поточний випуск v182 — C10/C11 POS і reading quiz

- ID255 直接: 名詞 + ナ形 за Kotobank Digital Daijisen; NINJAL також фіксує прислівникову класифікацію. У тренажері adverbial use записано в usage; окремий 副詞 тег не додано, бо він знижує cloze pool з 64 до 2, нижче мінімуму 3.
- ID327 浮気: 名詞 + ナ形 за Kotobank Digital Daijisen.
- Повні картки ID255/327 повторно перевірено й зараховано fixed_rechecked. Авторський credit збільшився на дві картки до 3387/3914.
- Додано три reviewed reading-quiz overrides для ID255, ID327 та ID1819. ID1819 не отримує нового повнокарткового credit; ID359 отримав автоматичний дистрактор うわき.
- Перевірено 23 reading-пули: 20 автоматичних пулів збережено, три ручні overrides пройшли; усі мають мінімум три дистрактори.

Реєстр — 3896 reviewed /61 fixed_rechecked /1890 pending; словниковий зріз — 3327 /60 /527; reviewed meaning quiz — 267; reviewed reading quiz — 3. Збережено 3914 словникових записів та ID, 130 граматичних конструкцій і 859 лексичних пар.

Технічні докази: completion/v182-prepare-results.json, completion/v182-browser-results.json, completion/v182-reading-pool-review.tsv, completion/v182-registry-results.json. Прогрес користувача й алгоритми навчання не змінювалися; patch має точний rollback до v181. Історичні докази пілота v153 збережено; ID121–320 не починалися повторно з нуля.

Робоча гілка — work/v182-c11-reading-pool-review; наступна дія — продовжити C10 з наступного pending checkpoint у реєстрі, не дублюючи активну роботу. Незалежне лінгвістичне, фізичне Android/Windows і правове/походження приймання не завершені. v182 — проміжний випуск, не кандидат 1.0.

"""
status_path.write_text(status_header+archived_v181+"\n\n"+older,encoding="utf-8")

backlog_path=Path("completion/BACKLOG.md")
backlog=backlog_path.read_text(encoding="utf-8")
lines=backlog.splitlines()
if len(lines)<4:
    raise RuntimeError("BACKLOG unexpectedly short")
lines[2]=f"Оновлено 13 листопада 2026 (Asia/Tokyo). [Критерії й порядок](PLAN.md). Поточний HTML — v182, SHA-256 {html_sha}; початкова інвентаризація зафіксована на v135. C04 закрито окремим звітом, C27 виконано у v171, історичні дані не переписано."
for i,line in enumerate(lines):
    if line.startswith("| C10 |"):
        lines[i]="| C10 | 1 | in_progress — авторський аудит 3914 словникових карток; повний охват ще не завершено | v182: ID255 直接 і ID327 浮気 повністю повторно перевірено, обидві fixed_rechecked. Авторський credit 3387/3914; словниковий зріз 3327 reviewed /60 fixed_rechecked /527 pending. Для 直接 збережено app POS 名詞+ナ形; NINJAL альтернативу 副詞 зафіксовано в usage, окремий тег не додано через падіння cloze pool до 2 (<3). Наступне: продовжити з наступного pending checkpoint, не повторюючи прийняті діапазони. Незалежне приймання відкрите. |"
    if line.startswith("| C11 |"):
        lines[i]="| C11 | 2 | in_progress — grammar meaning для чинних прикладів авторськи завершено у v144 | v181: ID2433 そびえる — два context-specific meaning payload; reviewed meaning quiz 267. v182: три reviewed reading-quiz overrides для ID255 直接, ID327 浮気 та ID1819 内訳; перевірено 23 reading-пули, 20 автоматичних перевірок і три ручні overrides; ID359 本気 отримав うわき автоматично. Докази: completion/v182-reading-pool-review.tsv, completion/v182-browser-results.json. Залишок: інші автоматичні meaning/reading-пули, cloze, невідомі контексти. Незалежне приймання відкрите. |"
backlog="\n".join(lines)+"\n"
open_marker=chr(96)+"open"+chr(96)+" — робота ще потрібна;"
summary="v182 — C10: ID255 і ID327 fixed_rechecked (+2 author credit); C11: 3 reviewed reading-quiz overrides для ID255/327/1819; 23 reading-пули перевірено, 20 автоматичних і 3 ручні пройшли; ID359 отримав うわき. Author credit 3387/3914; реєстр 3896/61/1890. Джерела POS для 直接 розходяться між Daijisen і NINJAL; app POS лишено 名詞+ナ形 через cloze 64→2 при додаванні 副詞."
if open_marker not in backlog:
    raise RuntimeError("BACKLOG open marker missing")
backlog=backlog.replace(open_marker,summary+"\n\n"+open_marker,1)
backlog_path.write_text(backlog,encoding="utf-8")

c10_path=Path("completion/C10-followup-255-327-20261113.md")
c10_path.write_text("""# C10 follow-up — ID255 and ID327

## v182 decision — 13 November 2026

- ID255 直接: POS corrected to 名詞 + ナ形; usage records formal 直接な交渉 and the adverbial use. Kotobank Digital Daijisen labels it 名・形動 and gives 直接な（の）交渉. NINJAL CHOKUSETSU labels 直接 名・副. These are differing dictionary classifications. The app retains 名詞+ナ形 and records adverbial use in usage because adding 副詞 as a third tag reduces cloze candidates from 64 to 2, below the minimum three. This is an app-specific compatibility decision, not a claim that the NINJAL classification is wrong.
- ID327 浮気: POS corrected to 名詞 + ナ形; the modern うわき is 名・形動 in Digital Daijisen. The card usage note covers 浮気な人.
- Both full cards were rechecked (definition, reading, examples, translations and usage) and moved from pending to fixed_rechecked.

Sources:
- Kotobank Digital Daijisen, 直接: https://kotobank.jp/word/%E7%9B%B4%E6%8E%A5-569297
- NINJAL CHOKUSETSU: https://mmsrv.ninjal.ac.jp/kamus/data/item315.html
- Kotobank Digital Daijisen, 浮気: https://kotobank.jp/word/%E6%B5%AE%E6%B0%97-442377
""",encoding="utf-8")

c11_path=Path("completion/C11-followup-255-327-20261113.md")
if c11_path.exists():
    c11_text=c11_path.read_text(encoding="utf-8")
else:
    c11_text="# C11 follow-up — ID255 and ID327\n"
c11_text += """

## v182 reading-quiz acceptance — 13 November 2026

Three reviewed reading-quiz overrides were added for ID255 直接, ID327 浮気 and ID1819 内訳. Each contains three distinct readings already present in the vocabulary database. ID359 本気 gains うわき automatically after the POS correction. The 23 affected pools were checked; 20 automatic pools retain the minimum and the three manual overrides pass uniqueness and correct-answer exclusion. No reading algorithm was changed. See v182-reading-pool-review.tsv and v182-browser-results.json.
"""
c11_path.write_text(c11_text,encoding="utf-8")

checkpoint= json.loads((WORK/"checkpoint.json").read_text(encoding="utf-8"))
checkpoint.update({
    "status":"verified; ready for publication to main",
    "candidate_html":"JLPT_N1_ukrainian_reading_v182.html",
    "candidate_sha256":html_sha,
    "candidate_bytes":prepare["candidate_bytes"],
    "author_vocabulary_credit":3387,
    "register_counts":{"reviewed":3896,"fixed_rechecked":61,"pending":1890},
    "vocabulary_counts":{"reviewed":3327,"fixed_rechecked":60,"pending":527},
    "reviewed_meaning_quiz":267,
    "reviewed_reading_quiz":3,
    "reading_pool_count":23,
    "manual_reading_overrides":3,
    "cloze_pos_tradeoff":{"current":64,"with_extra_adverb_tag":2}
})
(WORK/"checkpoint.json").write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

print(json.dumps({"pass":True,"registry":registry,"html_sha256":html_sha},ensure_ascii=False,indent=2))
