#!/usr/bin/env python3
import csv,json,re
from pathlib import Path
W=Path("completion/v178-work")
def main():
 prep=json.loads((W/"prepare-results.json").read_text(encoding="utf-8"))
 reg=json.loads((W/"registry-results.json").read_text(encoding="utf-8"))
 browser=json.loads((W/"browser-results.json").read_text(encoding="utf-8"))
 if not prep.get("pass") or not reg.get("pass") or not browser.get("pass"): raise ValueError("Evidence incomplete")
 h=prep["checkpoint_sha256"]
 audit="""# JLPT N1 v178 — C10 author review, ID421–449

**Дата:** 13 листопада 2026. **Основа:** v177, SHA-256 """+prep["base_sha256"]+""". **Кандидат:** v178, SHA-256 """+h+""".

## Авторський мовний перегляд

Перевірено 12 раніше pending карток і всі наявні приклади. 11 карток виправлено у 13 точних полях і повторно звірено; ID425 прийнято без зміни після перевірки словникових значень та обох прикладів.

| ID | Картка | Рішення | Підсумок |
|---:|---|---|---|
| 421 | 解ける | fixed_rechecked | Розмежовано とける і ほどける; обидва приклади залишаються とける. |
| 423 | 改まる | fixed_rechecked | Уточнено зміну/поліпшення стану й формальність; пояснено 改善される та перехідне 一新する. |
| 425 | 外れる | reviewed | Прогноз не справдився; учасник вибув зі складу. Обидва приклади відповідають словниковим значенням; зміни не потрібні. |
| 430 | 寄せる | fixed_rechecked | Додано збирання в одному місці та надсилання думок/інформації. |
| 433 | 詰める | fixed_rechecked | Дефініцію доповнено ретельним обговоренням до узгодженого рішення. |
| 435 | 求める | fixed_rechecked | Український глос доповнено значенням знаходження відповіді/обчислення величини. |
| 436 | 許す | fixed_rechecked | Японський приклад і переклад синхронізовано: влада послаблює регулювання й дозволяє новий вхід. |
| 438 | 響く | fixed_rechecked | Обидва переклади зроблено природнішими для звукового й переносного контекстів. |
| 440 | 勤まる | fixed_rechecked | Уточнено 勤まる／務まる без штучно абсолютного розмежування; словникові значення перетинаються. |
| 444 | 傾ける | fixed_rechecked | 耳を傾ける передано як уважне вислуховування думок. |
| 447 | 繋がる | fixed_rechecked | Прибрано дублювання наслідку; залишено природне «Додзвонитися до нього не вдалося». |
| 449 | 嫌がる | fixed_rechecked | «Уникати» замінено на зовнішній вияв небажання — «неохоче береться». |

Пілот v153 використано як карту ризиків, а не як автоматичний вердикт. Усі 13 before-значень звірено з повним HTML v177; ID425 перевірено окремо й залишено без зміни.

## Технічні перевірки

Детермінований preparer підтвердив точну основу v177, 13 операцій, повний rollback, незмінність 3914 словникових записів, 130 граматичних конструкцій, 859 лексичних пар, усіх ID та POS. Chromium перевірив 12 карток, 13 полів і всі приклади при ширинах 360, 412 і 1280 px; помилок сторінки не зафіксовано; тестовий sentinel прогресу не змінився.

## Облік і межі приймання

Авторський credit — 3385/3914. Завершальний реєстр — 3891 reviewed /59 fixed_rechecked /1892 pending; словниковий зріз — 3327 reviewed /58 fixed_rechecked /529 pending; лексичні пари — 18 reviewed /841 pending.

Це авторський мовний перегляд і технічна регресія конкретного кандидата. **Незалежне лінгвістичне приймання, фізична перевірка пристроїв та правове/походження приймання не виконані.** v178 — проміжний випуск, не кандидат 1.0.

## Джерела

- Поіменна джерельна звірка: completion/v178-source-review.md.
- Пілот v153: completion/v153-cards-381-440.tsv та completion/v153-cards-441-500.tsv.
- Поіменні before/after та обґрунтування: completion/v178-work/updates.json.
"""
 Path("JLPT_N1_v178_audit.md").write_text(audit,encoding="utf-8")
 Path("completion/C10-followup-421-449-20261113.md").write_text(audit,encoding="utf-8")
 candidate={"checkpoint":"v178-c10-candidate","base_main_sha":"cb402c2c1180d046f801795652c770fdef31d5a9","work_branch":"work/v178-c10-next-pending","base_html":"JLPT_N1_ukrainian_reading_v177.html","base_sha256":prep["base_sha256"],"candidate_html":"JLPT_N1_ukrainian_reading_v178.html","candidate_sha256":h,"scope_ids":[421,423,425,430,433,435,436,438,440,444,447,449],"changed_ids":prep["changed_ids"],"reviewed_without_change":["425"],"operations":13,"structural_invariants":{"vocabulary":3914,"grammar":130,"lexical_pairs":859},"registry_counts":reg["registry_counts"],"author_credit":reg["author_credit"],"status":"verified candidate; publication guarded by exact main SHA"}
 (W/"candidate.json").write_text(json.dumps(candidate,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 cp=json.loads((W/"checkpoint.json").read_text(encoding="utf-8"))
 cp["base_main_sha"]="cb402c2c1180d046f801795652c770fdef31d5a9"
 cp["proposed_changed_ids"]=prep["changed_ids"]
 cp["registry_credit"]=12
 cp["tests_status"]="deterministic prepare and Chromium passed"
 cp["candidate_sha256"]=h
 cp["candidate_bytes"]=prep["checkpoint_bytes"]
 cp["status"]="verified candidate; guarded publication in progress"
 (W/"checkpoint.json").write_text(json.dumps(cp,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 sp=Path("PROJECT_STATUS.md");status=sp.read_text(encoding="utf-8")
 if "Актуальна **v177**." not in status: raise ValueError("Status version mismatch")
 lines=status.splitlines()
 lines[2]="Оновлено 13 листопада 2026. Кандидат **v178** пройшов авторські й технічні перевірки; публікація виконується лише за незмінної вершини main. Повний HTML-кандидат JLPT_N1_ukrainian_reading_v178.html, "+format(prep["checkpoint_bytes"],",").replace(",", " ")+" байт, SHA-256 "+h+". [Аудит](JLPT_N1_v178_audit.md)"
 status="\n".join(lines)+"\n"
 old="## Поточний випуск v177 — C10 follow-up"
 if old not in status: raise ValueError("v177 status section missing")
 status=status.replace(old,"## Архівований випуск v177 — C10 follow-up",1)
 insert="""## Поточний випуск v178 — C10 follow-up

Авторськи переглянуто 12 pending карток: 11 виправлено у 13 точних полях і повторно перевірено; ID425 прийнято без зміни. Авторський credit — 3385/3914; завершальний реєстр — 3891 reviewed /59 fixed_rechecked /1892 pending; словниковий зріз — 3327 /58 /529; лексичні пари — 18 reviewed /841 pending.

Детермінований preparer підтвердив точну основу v177, 13 операцій, повний rollback і незмінність 3914 слів, 130 конструкцій, 859 пар, ID та POS. Chromium перевірив 12 карток, усі приклади й 13 полів при 360, 412 і 1280 px; помилок сторінки не зафіксовано, sentinel прогресу не змінився. Докази: JLPT_N1_v178_audit.md, completion/v178-acceptance.tsv, completion/v178-prepare-results.json, completion/v178-browser-results.json, completion/v178-registry-results.json та completion/v178-source-review.md.

Робоча гілка — work/v178-c10-next-pending. ID255 і ID327 залишаються окремими C11-залежностями через якість reading-дистракторів. C10 не завершено; v178 — проміжний випуск, не кандидат 1.0. Незалежне мовне, фізичне та правове/походження приймання окремі й не виконані.

"""
 marker="## Архівований випуск v177 — C10 follow-up"
 idx=status.index(marker)
 status=status[:idx]+insert+status[idx:]
 sp.write_text(status,encoding="utf-8")
 rp=Path("README.md");readme=rp.read_text(encoding="utf-8");split="\n## Контрольна версія"
 if split not in readme: raise ValueError("README structure mismatch")
 rest=readme.split(split,1)[1]
 intro="# JLPT N1 — тренажер з японським інтерфейсом\n\nКандидат v178 пройшов авторські й технічні перевірки; публікація в main виконується за guarded gate. [Повний HTML після публікації](JLPT_N1_ukrainian_reading_v178.html) · [Аудит](JLPT_N1_v178_audit.md)\n\nУ v178 переглянуто 12 pending карток: 11 виправлено у 13 полях, ID425 прийнято без зміни. Збережено 3914 слів, 130 конструкцій і 859 лексичних пар. Авторський credit — 3385/3914; реєстр — 3891 reviewed /59 fixed_rechecked /1892 pending. Незалежне, фізичне та правове/походження приймання не завершені.\n\nНижче збережено історичний журнал v18–v26; він не описує поточний стан.\n"
 rp.write_text(intro+split+rest,encoding="utf-8")
 bp=Path("completion/BACKLOG.md");backlog=bp.read_text(encoding="utf-8")
 backlog=backlog.replace("Поточний HTML — v177, SHA-256 "+prep["base_sha256"],"Поточний HTML — v178, SHA-256 "+h,1)
 rows=backlog.splitlines()
 for i,line in enumerate(rows):
  if line.startswith("| C10 |"):
   if "v178 додає" not in line:
    tail=" v178 додає 11 fixed_rechecked та 1 reviewed картку (ID421–449), 13 точних операцій; авторський credit 3385/3914; реєстр 3891/59/1892. Докази completion/v178-acceptance.tsv, completion/v178-prepare-results.json, completion/v178-browser-results.json, completion/v178-registry-results.json, completion/v178-source-review.md та JLPT_N1_v178_audit.md. Незалежне й фізичне приймання окремі."
    rows[i]=line[:-1].rstrip()+tail+" |"
   break
 else: raise ValueError("C10 row missing")
 backlog="\n".join(rows)
 if "## C10 follow-up ID421–449 — 13 листопада 2026" not in backlog:
  backlog=backlog.rstrip()+"\n\n## C10 follow-up ID421–449 — 13 листопада 2026\n\nУ v178 авторськи переглянуто 12 pending карток: 11 виправлено у 13 точних полях і повторно перевірено; ID425 прийнято без зміни. Авторський credit 3385/3914; реєстр 3891 reviewed /59 fixed_rechecked /1892 pending. ID255/327 лишаються окремими C11-залежностями. Докази: completion/v178-acceptance.tsv, completion/v178-prepare-results.json, completion/v178-browser-results.json, completion/v178-registry-results.json, completion/v178-source-review.md, JLPT_N1_v178_audit.md. Це не незалежне, фізичне чи правове/походження приймання.\n"
 bp.write_text(backlog,encoding="utf-8")
 print("Documentation prepared for v178",h)
if __name__=="__main__": main()
