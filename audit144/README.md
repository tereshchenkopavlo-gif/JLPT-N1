# Відтворення v144 — замкнений grammar meaning /261 приклад

```sh
python3 audit144/build.py
python3 audit144/check.py
python3 audit144/coverage.py
node --check audit144/app.js
npm install --no-save playwright@1.56.1
npx playwright install --with-deps chromium
# Потрібен японський шрифт, наприклад fonts-noto-cjk, для візуального огляду.
node audit144/meaning-browser.cjs
node audit144/coverage-browser.cjs
node audit144/scope-browser.cjs
node audit144/grammar-browser.cjs
node audit144/presentation.cjs
node audit144/ui.cjs
node audit144/browser-functional.cjs
node audit144/session-completion.cjs
node audit144/comparison-browser.cjs
python3 audit144/publish.py
```

Основа — повний v143 із фіксованим SHA. author.py: 49 ключів, 91 новий payload, 42 byExample. None залишає раніше перевірений exact-контекст; для трьох карток базовий новий payload — другий приклад, перший має exact-пріоритет. review.py читає фактичний пріоритет і документує 62 картки /124 контексти: 91 новий +33 збережені (23 C04 /10 C05). Картки й речення не змінюються. sources.md відділяє авторські оцінки від прочитаних джерел.

coverage.py поєднує незмінні докази v142/v143 з поточними та окремо перечитаним g95: усі 130 граматичних записів /261 приклад, без повторного зарахування. grammar-coverage.json містить sentence/payload-хеші й посилання на авторський доказ. coverage-browser.cjs перевіряє точне зіставлення з фактичним runtime, включно з g95. 224 saved /37 exact (27 C04 /10 C05), automatic 0. Старі назви exact_C04 у технічних звітах не оголошено точним походженням усіх пізніших наборів і не переписано.

meaning-browser.cjs: 791 контекст (530 словникових +261 граматичний) ×4 позиції =3164 генерації; ×3 ширини =2373 покази з хибною відповіддю й правильним поясненням; 122 негативні guard-перевірки. Випадковість контролюється лише в тесті. scope-browser.cjs окремо звіряє перші 130 граматичних питань і ті самі 1482 reading-ID/кількості альтернатив. grammar-browser.cjs — регресія незмінних карток v142, не нові зміни. Решта перевіряє представлення, навігацію, зберігання, порівняння й повну сесію. Linux Chromium не закриває фізичний Android/Windows.

baseline-integrity.json — Git blob-хеші 439 попередніх файлів із v143, крім трьох поточних документів стану. check.py перевіряє їх без мережі, точний diff застосунку й попередні кредити. publish.py вимагає 10 SHA-bound звітів і консолідований авторський каталог, потім публікує повний HTML/аудит та оновлює поточний стан. Повторний запуск не дублює розділ статусу. completion/review-register.csv, старі HTML й аудити не переписуються.

CHECKPOINT.md / work/v144-checkpoint — незавершені джерела до gate, не реліз. Вузький авторський meaning-аудит чинних граматичних прикладів завершений; **C11 загалом, повний граматичний аудит, незалежна експертиза, фізичне й правове приймання ще відкриті**. Пропозицію для 1482, scheduler, Learning Engine або N5–N1-міграцію не реалізовано.
