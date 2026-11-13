#!/usr/bin/env python3
import json,shutil
from pathlib import Path
W=Path("completion/v179-work")
def main():
 prep=json.loads((W/"prepare-results.json").read_text(encoding="utf-8"))
 browser=json.loads((W/"browser-results.json").read_text(encoding="utf-8"))
 reg=json.loads((W/"registry-results.json").read_text(encoding="utf-8"))
 if not (prep.get("pass") and browser.get("pass") and reg.get("pass")): raise ValueError("Evidence incomplete")
 h=prep["candidate_sha256"];size=prep["candidate_bytes"]
 audit=f"""# JLPT N1 v179 — C11 context-specific meaning quiz review

**Дата:** 13 листопада 2026. **Основа:** v178, SHA-256 {prep["base_sha256"]}. **Кандидат:** v179, SHA-256 {h} ({size} байт).

## Авторський перегляд

У v179 додано два авторськи перевірені контекстні набори значення для **ID2468 下す** — окремо для 判決を下す і 決断を下す. Обидва приклади вже мали точні записи в REVIEWED_EXAMPLE_TARGETS; додано лише quiz.correct, три відмінні quiz.wrong та українську примітку. Форми виділення прикладів і структура запитань не змінювалися.

- 裁判所は、被告に対して厳しい判決を下した。 — правильна відповідь описує винесення судового рішення; дистрактори відмежовують розгляд доказів, скасування вже винесеного рішення та виконання вироку.
- 経営陣は、慎重な検討の末に撤退という決断を下した。 — правильна відповідь описує остаточне рішення після розгляду; дистрактори відмежовують продовження розгляду варіантів, відкладення та відкликання рішення.

ID2433 そびえる переглянуто, але автоматичні набори не замінено. Точний example override для цього kana-only headword вимкнув би наявний cloze-маршрут за чинною логікою; механізм вправ не змінювався. Поточні автоматичні варіанти збережено в completion/v179-browser-results.json; позиція лишається відкритою.

## C10-залежності та reading-пули

ID255 直接 та ID327 浮気 не змінювалися й залишаються pending. Діагностика запропонованих POS 名詞 + ナ形 показала 23 змінені reading-пули; три записи втрачають поріг трьох дистракторів (ID255, ID327, ID1819), один набуває його (ID359). Детальні before/after — completion/v179-reading-pool-impact.json і completion/C11-followup-255-327-20261113.md. Жодних POS або reading-override змін у v179 не внесено.

## Технічні перевірки

Детермінований preparer підтвердив точну основу v178, два payload, повний rollback та незмінність 3914 словникових записів, 130 граматичних конструкцій, 859 лексичних пар, усіх ID, POS, reading overrides, збережених meaning-наборів і коду прогресу. Chromium перевірив обидва контексти, точне виділення 下した, чотири унікальні варіанти, збереження автоматичних наборів ID2433, картки й приклади при 360, 412 та 1280 px. Контрольний sentinel прогресу не змінився.

## Облік і межі приймання

Авторський credit словника не змінюється: **3385/3914**. Завершальний реєстр: **3892 reviewed /59 fixed_rechecked /1892 pending**; словниковий зріз: **3327 /58 /529**; лексичні пари: **18 reviewed /841 pending**; saved meaning quiz: **266**. У C11 зараховано один об'єкт reviewed_meaning_quiz (ID2468) із двома контекстними payload.

Це авторське приймання двох наборів запитань і технічна регресія, не повний аудит картки та не незалежне приймання. Незалежне лінгвістичне, фізичне та правове/походження приймання не виконані. v179 — проміжний випуск, не кандидат 1.0.

## Джерела

- completion/v179-source-review.md — точні словникові звірки й межі використання джерел.
- completion/v179-c11-review.tsv — поіменні рішення для ID2433/2468.
- completion/v179-reading-pool-impact.json — відтворювана діагностика POS/reading залежності.
"""
 Path("JLPT_N1_v179_audit.md").write_text(audit,encoding="utf-8")
 Path("completion/C11-followup-2433-2468-20261113.md").write_text(audit,encoding="utf-8")
 shutil.copyfile(W/"prepare-results.json",Path("completion/v179-prepare-results.json"))
 shutil.copyfile(W/"browser-results.json",Path("completion/v179-browser-results.json"))
 shutil.copyfile(W/"registry-results.json",Path("completion/v179-registry-results.json"))
 shutil.copyfile(W/"source-review.md",Path("completion/v179-source-review.md"))
 sp=Path("PROJECT_STATUS.md");status=sp.read_text(encoding="utf-8")
 if "Актуальна **v178**." not in status: raise ValueError("Unexpected PROJECT_STATUS baseline")
 lines=status.splitlines()
 lines[2]=f"Оновлено 13 листопада 2026. Актуальна **v179**. Опубліковано в main після успішних детермінованих і Chromium-перевірок. Повний JLPT_N1_ukrainian_reading_v179.html, {size:,} байт, SHA-256 {h}. [Аудит](JLPT_N1_v179_audit.md)"
 status="\n".join(lines)+"\n"
 old="## Поточний випуск v178 — C10 follow-up"
 if old not in status: raise ValueError("Missing v178 section")
 status=status.replace(old,"## Архівований випуск v178 — C10 follow-up",1)
 section=f"""## Поточний випуск v179 — C11 context-specific meaning quiz

Додано два авторськи перевірені контекстні meaning-набори ID2468 下す. Авторський credit — 3385/3914 (без змін); завершальний реєстр — 3892 reviewed /59 fixed_rechecked /1892 pending; словниковий зріз — 3327 /58 /529; лексичні пари — 18 /841; reviewed meaning quiz — 266.

Детермінований preparer підтвердив точну основу v178, два payload, повний rollback і незмінність 3914 слів, 130 конструкцій, 859 пар, ID, POS та reading overrides. Chromium перевірив обидва контексти, унікальність чотирьох варіантів, точне виділення прикладів і картки при 360, 412 та 1280 px; автоматичні набори ID2433 не змінилися, sentinel прогресу не змінився. Докази: JLPT_N1_v179_audit.md, completion/v179-c11-review.tsv, completion/v179-acceptance.tsv, completion/v179-prepare-results.json, completion/v179-browser-results.json, completion/v179-registry-results.json.

Робоча гілка — work/v179-c11-context-quiz-review. ID2433 залишається відкритим через взаємодію точного example override з cloze; ID255/327 залишаються C10/C11 POS-reading залежностями, оскільки запропоновані POS змінюють 23 пули й знижують поріг для ID1819. Діагностика: completion/v179-reading-pool-impact.json. Жодних змін POS, reading-алгоритму або прогресу не внесено.

C10 і C11 не завершено. Незалежне лінгвістичне, фізичне та правове/походження приймання не виконані. v179 — проміжний випуск, не кандидат 1.0.

"""
 marker="## Архівований випуск v178 — C10 follow-up"
 idx=status.index(marker);status=status[:idx]+section+status[idx:]
 sp.write_text(status,encoding="utf-8")
 rp=Path("README.md");readme=rp.read_text(encoding="utf-8");split="\n## Контрольна версія"
 if split not in readme: raise ValueError("README structure mismatch")
 rest=readme.split(split,1)[1]
 intro="""# JLPT N1 — тренажер з японським інтерфейсом

Актуальна v179. У v179 додано два авторськи перевірені контекстні meaning-набори для ID2468 下す. [Повний HTML](JLPT_N1_ukrainian_reading_v179.html) · [Аудит](JLPT_N1_v179_audit.md)

Збережено 3914 словникових записів, 130 граматичних конструкцій і 859 лексичних пар. Авторський credit — 3385/3914; завершальний реєстр — 3892 reviewed /59 fixed_rechecked /1892 pending. Незалежне, фізичне та правове/походження приймання не завершені.

Нижче збережено історичний журнал v18–v26; він не описує поточний стан.
"""
 rp.write_text(intro+split+rest,encoding="utf-8")
 bp=Path("completion/BACKLOG.md");backlog=bp.read_text(encoding="utf-8");lines=backlog.splitlines()
 for i,line in enumerate(lines):
  if line.startswith("| C11 |"):
   lines[i]=line[:-1].rstrip()+" v179: один новий reviewed_meaning_quiz (ID2468) із двома exact context payload; saved meaning quiz — 266. ID2433 лишається pending через cloze-залежність; ID255/327 — через 23 змінені reading-пули при запропонованому POS. Докази completion/v179-c11-review.tsv, completion/v179-reading-pool-impact.json, completion/v179-browser-results.json, JLPT_N1_v179_audit.md. Незалежне приймання відкрите. |"
   break
 else: raise ValueError("C11 backlog row missing")
 for i,line in enumerate(lines):
  if line.startswith("| C10 |"):
   lines[i]=line[:-1].rstrip()+" v179 не зараховує ID255/327 і не змінює POS; діагностика C11 збережена в completion/C11-followup-255-327-20261113.md. |"
   break
 backlog="\n".join(lines)+"\n"
 if "## C11 follow-up ID2468 — 13 листопада 2026" not in backlog:
  backlog+="\n## C11 follow-up ID2468 — 13 листопада 2026\n\nДодано два авторськи перевірені context-specific meaning payload для 判決を下す і 決断を下す; один новий об'єкт reviewed_meaning_quiz, загалом 266. ID2433 не змінено, щоб не вимикати його cloze без окремого рішення. ID255/327 лишаються pending; POS-reading side effects описані в completion/C11-followup-255-327-20261113.md. Це не незалежне приймання.\n"
 bp.write_text(backlog,encoding="utf-8")
 candidate={"checkpoint":"v179-c11-context-quiz","base_html_sha256":prep["base_sha256"],"candidate_html_sha256":h,"work_branch":"work/v179-c11-context-quiz-review","scope":["ID2468 example 0 meaning quiz","ID2468 example 1 meaning quiz"],"author_credit":"3385/3914","registry_counts":reg["registry_counts"],"vocabulary_counts":reg["vocabulary_counts"],"independent_acceptance":False}
 (W/"candidate.json").write_text(json.dumps(candidate,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 cp=json.loads((W/"checkpoint.json").read_text(encoding="utf-8"));cp.update({"candidate_sha256":h,"candidate_bytes":size,"tests_status":"deterministic and Chromium passed","status":"verified candidate; guarded main publication completed"})
 (W/"checkpoint.json").write_text(json.dumps(cp,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("Documentation prepared for v179",h)
if __name__=="__main__": main()
