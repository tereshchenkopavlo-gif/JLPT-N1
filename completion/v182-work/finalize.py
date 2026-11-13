import csv
import json
import shutil
from collections import Counter
from pathlib import Path

WORK = Path("completion/v182-work")
prepare = json.loads((WORK / "prepare-results.json").read_text(encoding="utf-8"))
browser = json.loads((WORK / "browser-results.json").read_text(encoding="utf-8"))
diag = json.loads((WORK / "diagnostics.json").read_text(encoding="utf-8"))
html_sha = prepare["candidate_sha256"]

if not prepare.get("pass") or not prepare.get("exact_rollback"):
    raise RuntimeError("v182 prepare check failed")
if not browser.get("pass") or browser.get("sha256") != html_sha:
    raise RuntimeError("v182 browser check failed or SHA mismatch")
if not diag.get("pass") or diag.get("remainingLostAfterOverrides") != []:
    raise RuntimeError("v182 corrected-POS diagnostic failed")
if diag.get("changedPoolCount") != 23 or len(diag.get("lostEligibility", [])) != 3 or len(diag.get("gainedEligibility", [])) != 1:
    raise RuntimeError("v182 reading-pool diagnostic totals changed unexpectedly")
if prepare["vocabulary_records"] != 3914 or prepare["unique_vocabulary_ids"] != 3914 or prepare["grammar_records"] != 130 or prepare["lexical_pairs"] != 859:
    raise RuntimeError("v182 data integrity counts changed")
if browser["counts"] != {"vocabulary": 3914, "uniqueVocabIds": 3914, "grammar": 130, "lexicalPairs": 859, "posEntries": 3914, "readingOverrides": 4}:
    raise RuntimeError("v182 browser data counts changed")
if browser["remainingLostAfterOverrides"] != []:
    raise RuntimeError("v182 browser confirms remaining reading-pool losses")

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
    matches[0]["evidence"] = f"completion/v182-c10-review.tsv#{card_id}; POS corrected and full card fields rechecked; v182 HTML SHA-256={html_sha}"

reading_entries = [
    ("r_255", "255", "直接", "ちょくせつ"),
    ("r_327", "327", "浮気", "うわき"),
    ("r_1819", "1819", "内訳", "うちわけ")
]
for key, card_id, word, reading in reading_entries:
    if any(r["kind"] == "reviewed_reading_quiz" and r["key"] == key for r in rows):
        raise RuntimeError(f"reading quiz {key} is already registered")
    rows.append({
        "kind": "reviewed_reading_quiz",
        "key": key,
        "baselineLocation": f"REVIEWED_READING_OPTIONS.{card_id}",
        "finalReview": "reviewed",
        "evidence": f"completion/v182-reading-pool-review.tsv#{card_id}; three unique verified distractors; target {word}/{reading}; v182 HTML SHA-256={html_sha}"
    })

after = Counter(r["finalReview"] for r in rows)
if after.get("reviewed") != 3896 or after.get("fixed_rechecked") != 61 or after.get("pending") != 1890 or len(rows) != 5847:
    raise RuntimeError(f"unexpected post-v182 register counts: {dict(after)}, rows={len(rows)}")
kind_counts = Counter(r["kind"] for r in rows)
expected_kinds = {"vocab": 3914, "grammar": 130, "vocab_pair": 859, "grammar_pair": 92, "antonym_pair": 41, "reading": 160, "reading_question": 381}
for kind, expected_count in expected_kinds.items():
    if kind_counts.get(kind) != expected_count:
        raise RuntimeError(f"unexpected object count for {kind}: {kind_counts.get(kind)} != {expected_count}")
if kind_counts.get("reviewed_meaning_quiz") != 267 or kind_counts.get("reviewed_reading_quiz") != 3:
    raise RuntimeError(f"unexpected reviewed quiz counts: {dict(kind_counts)}")
vocab_counts = Counter(r["finalReview"] for r in rows if r["kind"] == "vocab")
if vocab_counts.get("reviewed") != 3327 or vocab_counts.get("fixed_rechecked") != 60 or vocab_counts.get("pending") != 527:
    raise RuntimeError(f"unexpected vocabulary slice counts: {dict(vocab_counts)}")

with register_path.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)

shutil.copyfile(WORK / "diagnostics.json", "completion/v182-diagnostics.json")
shutil.copyfile(WORK / "reading-pool-review.tsv", "completion/v182-reading-pool-review.tsv")
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

audit = f"""# JLPT N1 v182 — авторський аудит і технічне приймання

Дата: 13 листопада 2026 року.

## Обсяг і рішення

- **ID255 直接**: POS виправлено з 名詞 на 名詞 + 副詞. NINJAL CHOKUSETSU розрізняє 直接 (名・副) і 直接的 (形動); приклади 直接お問い合わせください та 直接の原因 узгоджуються з іменниковим і прислівниковим уживанням. Дефініцію, читання, два японські приклади, українські переклади й usage повторно перевірено. Статус fixed_rechecked.
- **ID327 浮気**: POS виправлено з 名詞 на 名詞 + ナ形. Kotobank Digital Daijisen позначає сучасне うわき як 名・形動. Дефініцію, читання, приклади, переклади й usage повторно перевірено. Статус fixed_rechecked. Історичне ふき не використано як неправильний варіант.
- **ID1819 内訳**: картку не змінено; додано лише reading-quiz override, щоб зберегти три дистрактори після POS-корекції 浮気. Повнокартковий credit не змінюється.
- **ID359 本気**: картку не змінено; після POS-корекції 浮気 автоматичний пул отримує うわき як додатковий дистрактор. Повнокартковий credit не змінюється.

## Reading-pool review

Після точного моделювання виправлених POS для всіх 3914 словникових записів змінилися 23 пули: три втратили мінімум три автоматичні дистрактори, один отримав додатковий варіант, решта зберегли поріг. Три ручні override для ID255, ID327 та ID1819 відновлюють мінімум; залишкових втрат немає. Усі дистрактори — різні читання наявних словникових записів, не рівні правильному читанню. Повний перелік: completion/v182-reading-pool-review.tsv; машинна діагностика: completion/v182-diagnostics.json.

## Технічні перевірки

- Детермінований patch має точний rollback до v181; змінено тільки два POS-значення, три записи REVIEWED_READING_OPTIONS і заголовок версії.
- Збережено 3914 словникових записів, 3914 унікальних ID, 130 граматичних конструкцій, 859 лексичних пар і всі тексти карток.
- Chromium підтвердив POS для ID255/327/1819/359, точні три дистрактори для кожного override, чотири унікальні варіанти з правильною відповіддю, відновлення контрольного стану progress storage, відсутність JS-помилок і горизонтального переповнення на 360/412/1280 px.
- review-register.csv: 5847 об'єктів; 3896 reviewed /61 fixed_rechecked /1890 pending. Словниковий зріз: 3327 /60 /527. Авторський словниковий credit: 3387/3914. Reviewed meaning quiz: 267; reviewed reading quiz: 3.

## Джерела

- NINJAL, CHOKUSETSU: https://mmsrv.ninjal.ac.jp/kamus/data/item315.html
- Shogakukan Digital Daijisen via Kotobank, 浮気: https://kotobank.jp/word/%E6%B5%AE%E6%B0%97-442377
- Shogakukan Digital Daijisen via Kotobank, 内訳: https://kotobank.jp/word/%E5%86%85%E8%A8%B3-440704

## Межі приймання

Це авторський аудит і технічна регресія, не незалежне лінгвістичне приймання. Фізичне Android/Windows, правове й повне джерельне приймання залишаються відкритими.
"""
Path("JLPT_N1_v182_audit.md").write_text(audit, encoding="utf-8")

readme_path = Path("README.md")
readme = readme_path.read_text(encoding="utf-8")
history_marker = "Нижче збережено історичний журнал v18–v26; він не описує поточний стан."
if history_marker not in readme:
    raise RuntimeError("README history marker missing")
history = readme[readme.index(history_marker):]
readme_header = f"""# JLPT N1 — тренажер з японським інтерфейсом

Актуальна v182. У v182 уточнено POS для ID255 直接 та ID327 浮気 і збережено три перевірені reading-quiz пули для ID255/327/1819. [Повний HTML](JLPT_N1_ukrainian_reading_v182.html) · [Аудит](JLPT_N1_v182_audit.md)

Збережено 3914 словникових записів, 130 граматичних конструкцій і 859 лексичних пар. Авторський credit — 3387/3914; завершальний реєстр — 3896 reviewed /61 fixed_rechecked /1890 pending; reviewed meaning quiz — 267; reviewed reading quiz — 3. Незалежне, фізичне та правове/походження приймання не завершені.

Докази v182: [підготовка](completion/v182-prepare-results.json), [Chromium](completion/v182-browser-results.json), [реєстр](completion/v182-registry-results.json), [23 reading-пули](completion/v182-reading-pool-review.tsv).

"""
readme_path.write_text(readme_header + history, encoding="utf-8")

status_path = Path("PROJECT_STATUS.md")
status = status_path.read_text(encoding="utf-8")
current_marker = "## Поточний випуск v181"
archive_marker = "## Архівований випуск v179"
if current_marker not in status or archive_marker not in status:
    raise RuntimeError("PROJECT_STATUS v181/archive markers missing")
ci, ai = status.index(current_marker), status.index(archive_marker)
archived_v181 = status[ci:ai].replace("## Поточний випуск v181", "## Архівований випуск v181", 1).strip()
older = status[ai:]
status_header = f"""# PROJECT_STATUS.md — JLPT N1

Оновлено 13 листопада 2026. Актуальна v182 у main. Повний HTML — {prepare['candidate_bytes']:,} байт, SHA-256 {html_sha}. [Повний HTML](JLPT_N1_ukrainian_reading_v182.html) · [Аудит](JLPT_N1_v182_audit.md).

## Поточний випуск v182 — POS і reading-quiz

- **ID255 直接**: 名詞 + 副詞 за NINJAL; 直接的 є окремою 形動 формою.
- **ID327 浮気**: 名詞 + ナ形 за Kotobank Digital Daijisen; історичне ふき не використовується як дистрактор.
- Повторно перевірено повні картки ID255/327; обидві зараховано як fixed_rechecked. Авторський credit збільшився на дві картки до 3387/3914.
- Додано три reviewed reading-quiz overrides для ID255, ID327 та ID1819. ID1819 не отримує нового повнокарткового credit; ID359 отримав додатковий автоматичний варіант うわき.
- Після коректної POS-симуляції змінилися 23 reading-пули: 3 втратили мінімум, 1 отримав варіант; три ручні override відновили всі попередньо доступні пули. Залишкових втрат немає.

Завершальний реєстр — 3896 reviewed /61 fixed_rechecked /1890 pending; словниковий зріз — 3327 /60 /527; reviewed meaning quiz — 267; reviewed reading quiz — 3. Збережено 3914 словникових записів і унікальних ID, 130 граматичних конструкцій та 859 лексичних пар.

Технічні докази: completion/v182-prepare-results.json, completion/v182-browser-results.json, completion/v182-diagnostics.json, completion/v182-reading-pool-review.tsv, completion/v182-registry-results.json. Авторський аудит і технічна регресія не є незалежним прийманням. Прогрес користувача та код навчальної логіки не змінювалися; patch має точний rollback до v181.

Історичні докази пілота v153 та попередніх випусків збережено; ID121–320 не починалися повторно з нуля. Робоча гілка — work/v181-c11-id2433-quiz-review; наступний крок — продовжити C10/C11 із найсвіжішого pending checkpoint у реєстрі, не перезапускаючи вже зараховані діапазони.

Незалежне лінгвістичне, фізичне Android/Windows і правове/походження приймання не виконані. v182 — проміжний випуск, не кандидат 1.0.

"""
status_path.write_text(status_header + archived_v181 + "\n\n" + older, encoding="utf-8")

backlog_path = Path("completion/BACKLOG.md")
backlog = backlog_path.read_text(encoding="utf-8")
lines = backlog.splitlines()
if len(lines) < 4:
    raise RuntimeError("BACKLOG unexpectedly short")
lines[2] = f"Оновлено 13 листопада 2026 (Asia/Tokyo). [Критерії й порядок](PLAN.md). Поточний HTML — v182, SHA-256 {html_sha}; початкова інвентаризація зафіксована на v135. C04 закрито окремим звітом, C27 виконано у v171, історичні дані не переписано."
for i, line in enumerate(lines):
    if line.startswith("| C10 |"):
        lines[i] = "| C10 | 1 | in_progress — авторський аудит 3914 словникових карток; повний охват ще не завершений | v182: ID255 直接 виправлено на 名詞+副詞 за NINJAL; ID327 浮気 — на 名詞+ナ形 за Kotobank. Обидві картки повністю повторно перевірено й зараховано fixed_rechecked. Словниковий зріз 3327 reviewed /60 fixed_rechecked /527 pending; author credit 3387/3914. Наступне: продовжити з наступного pending checkpoint у реєстрі, не повторюючи вже прийняті діапазони. Незалежне приймання відкрите. |"
    if line.startswith("| C11 |"):
        lines[i] = "| C11 | 2 | in_progress — grammar meaning для чинних прикладів авторськи завершено у v144 | v181: ID2433 そびえる — два context-specific meaning payload; reviewed meaning quiz 267. v182: додано три reviewed reading-quiz overrides для ID255 直接, ID327 浮気 та ID1819 内訳; automatic POS simulation змінив 23 пули, 3 втратили поріг, 1 отримав варіант; три overrides відновили всі раніше доступні пули. Reviewed reading quiz 3. ID359 本気 отримав автоматичний варіант うわき. Докази: completion/v182-reading-pool-review.tsv, completion/v182-diagnostics.json, completion/v182-browser-results.json. Залишок: інші автоматичні meaning/reading-пули, cloze, невідомі контексти. Незалежне приймання відкрите. |"
backlog = "\n".join(lines) + "\n"
open_marker = chr(96) + "open" + chr(96) + " — робота ще потрібна;"
summary = f"v182 — C10: ID255 і ID327 fixed_rechecked (+2 author credit); C11: 3 reviewed reading-quiz overrides для ID255/327/1819; усі 23 змінені пули перевірено, залишкових втрат eligibility немає. Author credit 3387/3914; реєстр 3896/61/1890. Докази: v182-acceptance.tsv, v182-c10-review.tsv, v182-reading-pool-review.tsv, v182-browser-results.json, v182-registry-results.json, JLPT_N1_v182_audit.md."
if open_marker not in backlog:
    raise RuntimeError("BACKLOG open marker missing")
backlog = backlog.replace(open_marker, summary + "\n\n" + open_marker, 1)
backlog_path.write_text(backlog, encoding="utf-8")

c10_path = Path("completion/C10-followup-255-327-20261113.md")
c10_text = """# C10 follow-up — ID255 and ID327

## v182 decision — 13 November 2026

- **ID255 直接**: corrected POS to 名詞 + 副詞. NINJAL CHOKUSETSU labels 直接 as 名・副 and distinguishes 直接的 as 形動. The two existing examples and Ukrainian translations were rechecked; no example or translation edit was required.
- **ID327 浮気**: corrected POS to 名詞 + ナ形. Kotobank Digital Daijisen labels modern うわき as 名・形動; the card usage note already contains 浮気な人. The two examples and Ukrainian translations were rechecked; no example or translation edit was required.
- Both vocabulary rows moved from pending to fixed_rechecked. This adds two author-accepted cards; it is not independent acceptance.

Sources:
- NINJAL CHOKUSETSU: https://mmsrv.ninjal.ac.jp/kamus/data/item315.html
- Kotobank Digital Daijisen, 浮気: https://kotobank.jp/word/%E6%B5%AE%E6%B0%97-442377

Technical dependency:
- Corrected POS changed 23 reading pools. Three targets fell below three automatic distractors; one target gained a distractor. Manual reading overrides for ID255, ID327 and ID1819 restore all previously eligible pools. Full evidence: v182-reading-pool-review.tsv and v182-diagnostics.json.
"""
c10_path.write_text(c10_text, encoding="utf-8")

c11_path = Path("completion/C11-followup-255-327-20261113.md")
if c11_path.exists():
    c11_text = c11_path.read_text(encoding="utf-8")
else:
    c11_text = "# C11 follow-up — ID255 and ID327\n"
c11_addendum = """

## v182 addendum — reading quiz, 13 November 2026

The corrected POS simulation and author review produced three saved reading-quiz overrides: ID255 直接 (ちょくせつ), ID327 浮気 (うわき), and ID1819 内訳 (うちわけ). Each has three distinct distractors drawn from existing vocabulary readings. The historical reading ふき is excluded. ID359 本気 gains うわき automatically and needs no override.

The corrected POS changes affect 23 reading pools: three lose the three-distractor threshold and one gains eligibility. The three overrides restore every previously eligible pool; no residual loss remains. No full-card credit is added for ID1819 or ID359.

Evidence: JLPT_N1_v182_audit.md, v182-reading-pool-review.tsv, v182-browser-results.json.
"""
c11_path.write_text(c11_text + c11_addendum, encoding="utf-8")

checkpoint = json.loads((WORK / "checkpoint.json").read_text(encoding="utf-8"))
checkpoint.update({
    "status": "verified; ready for publication to main",
    "candidate_html": "JLPT_N1_ukrainian_reading_v182.html",
    "candidate_sha256": html_sha,
    "candidate_bytes": prepare["candidate_bytes"],
    "author_vocabulary_credit": 3387,
    "register_counts": {"reviewed": 3896, "fixed_rechecked": 61, "pending": 1890},
    "vocabulary_counts": {"reviewed": 3327, "fixed_rechecked": 60, "pending": 527},
    "reviewed_reading_quiz": 3,
    "reviewed_meaning_quiz": 267,
    "remaining_lost_reading_pools": 0
})
(WORK / "checkpoint.json").write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({"pass": True, "registry": registry, "html_sha256": html_sha}, ensure_ascii=False, indent=2))
