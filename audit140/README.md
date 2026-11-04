# Відтворення v140 — відгуки користувача 4 листопада

```sh
python3 audit140/build.py
python3 audit140/check.py
node --check audit140/app.js
npm install --no-save playwright@1.56.1
npx playwright install --with-deps chromium
node audit140/browser.cjs
node audit140/generator.cjs
node audit140/presentation.cjs
node audit140/ui.cjs
node audit140/browser-functional.cjs
node audit140/session-completion.cjs
node audit140/comparison-browser.cjs
python3 audit140/publish.py
```

Основа — повний v139 з точним SHA. author.py/gloss-proposals.json містять редакторські рішення, runtime.js — невеликі зміни генерації/глосарія. Жодного автоматичного масового імпорту чи нового scheduler немає. Будівник створює повний release140/HTML і поіменні aliases/glossary-review/reading-options JSON. Робочий checkpoint work/v140-checkpoint відокремлено від релізу.

check/scan: інваріанти даних і фактичний markTarget на 8089 прикладах. browser: пул читань усіх 3914 записів, 286 фактичних карток, сумісність точних legacy w/r/id, старий прогрес/порівняння після reload, 著しい на трьох ширинах та фактичні глосарії всіх 160 читань/400 лексичних приміток. generator: 1128 контекстів (526 C05, 30 C04, 572 приклади нормалізованих ナ形) ×3 позиції вибору типу =3384 генерації. Для кожного cloze перевіряється точне буквальне відновлення речення правильним варіантом. Перемішування в тесті контролює Math.random лише для вибору прикладу/типу; у HTML тестових гачків немає.

Окремі сценарії UI/POS/гортання, порівнянь 2/3/4, ліміту, backup/import/reload, повної звичайної сесії, 12 тем/масштабів/ширин. Потрібен CJK-шрифт для візуального огляду; реальні Android/Windows цими тестами не замінено.

Усі звіти мають фінальний SHA-256. Повторне виконання publisher використовує саме результати фактичного прогону; випадкові лічильники сесії не переносити з іншого запуску. Нові джерела/межі — sources.md; невирішені мовні питання генерації — C11. Повний HTML/аудит і оновлені документи публікуються в main та звіряються за Git blob SHA.
