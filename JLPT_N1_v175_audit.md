# JLPT N1 v175 — C10 follow-up audit

Дата: 13 листопада 2026 (Asia/Tokyo). Тип: **авторський перегляд дев’яти pending карток і п’яти лексичних пар + технічна регресія змінених полів**. Не незалежне мовне приймання, не правове/походження приймання і не фізичне приймання.

## Основа та контрольний файл

- Основа main перед v175: commit `7384ad7af1de8172f079768117fc7507af83eaf4` (v174).
- SHA-256 основи: `a012b3d50685353354417e89f4d6ab2767c8003ce1d77b4ff84ef85c77ed8c20`.
- Повний HTML v175: __V175_BYTES__ байт.
- SHA-256 v175: `__V175_SHA256__`.
- 3914 словникових записів, 130 граматичних конструкцій, 859 лексичних пар; усі ID та порядок збережено.

## Авторський перегляд

| ID | Рішення | Поля |
|---:|---|---|
| 3802 | fixed_rechecked | `exampleTranslations[1]` |
| 3803 | reviewed без зміни | — |
| 3807 | fixed_rechecked | `usage`, `exampleTranslations[0]` |
| 3808 | fixed_rechecked | `exampleTranslations[0]` |
| 3809 | fixed_rechecked | `exampleTranslations[1]` |
| 3810 | fixed_rechecked | `t` |
| 3812 | fixed_rechecked | `exampleTranslations[1]` |
| 3814 | fixed_rechecked | `usage` |
| 3816 | fixed_rechecked | `t`, `exampleTranslations[1]` |

Разом 10 точних змін у 8 картках; одна картка переглянута без зміни. Причини й джерела: [C10 follow-up](completion/C10-followup-3802-3816-20261113.md).

## Лексичні пари

П’ять пар переглянуто без зміни: 836, 838, 840, 841, 843. Доказ: `completion/v175-pair-review.tsv`. Їхні дані й примітки не змінювалися.

## Технічні перевірки

Детермінований preparer: точна основа v174, лише зазначені 10 полів, незмінні кількості й ID, точний rollback, синтаксис усіх inline JS. Chromium: дев’ять карток, десять полів, п’ять пар; відображення при 360/412/1280 px; контрольний sentinel сховища прогресу. Деталі в `completion/v175-prepare-results.json` та `completion/v175-browser-results.json`.

## Межі приймання

Авторський credit після v175 — 3351/3914. Реєстр: 3881 reviewed / 27 fixed_rechecked / 1934 pending. C10 залишається відкритим. Незалежне мовне приймання, походження/правове приймання та фізичне тестування не виконані. Інші відкриті задачі C07, C11, C12, C14, C16, C17 не закриваються цим пакетом.

Наступні pending ID: __NEXT_PENDING_IDS__.
