# Відтворення v142 — 16 граматичних наборів /33 контексти

```sh
python3 audit142/build.py
python3 audit142/check.py
node --check audit142/app.js
npm install --no-save playwright@1.56.1
npx playwright install --with-deps chromium
# Для візуального огляду потрібен японський шрифт, наприклад fonts-noto-cjk.
node audit142/meaning-browser.cjs
node audit142/grammar-browser.cjs
node audit142/presentation.cjs
node audit142/ui.cjs
node audit142/browser-functional.cjs
node audit142/session-completion.cjs
node audit142/comparison-browser.cjs
python3 audit142/publish.py
```

build.py спирається на повний опублікований v141 з фіксованим SHA. author.py — оригінальні варіанти/українські примітки та п’ять редакцій визначень; приклади не змінені. review.py фіксує рішення в editorial-review.json. Це відтворення явно прийнятих авторських рішень, а не автоматична незалежна мовна експертиза. sources.md містить фактичну зовнішню звірку та межі.

meaning-browser.cjs перевіряє 33 нові контексти й незмінні 530 лексичних +2 g95: 565 ×4 позиції =2260 генерацій; 565 ×3 ширини =1695 показів із хибною відповіддю та правильним поясненням. g107 має три приклади. Випадковість контролюється лише в тесті; runtime не змінюється. grammar-browser.cjs окремо показує чотири змінені картки. Інші сценарії з audit141 повторно виконуються для нового SHA. Linux Chromium не є фізичним Android/Windows.

publish.py перевіряє всі SHA-bound звіти й точний обсяг перед копіюванням повного HTML у корінь, написанням аудиту та оновленням README/PROJECT_STATUS/BACKLOG. completion/review-register.csv не переписується: 325/5517 збережено. Окремий C11-grammar-v142-result.json зв’язує 16 нових наборів із точними попередніми зауваженнями; залишає 51 case ID відкритим. Історичні знімки не змінені.

CHECKPOINT.md і гілка work/v142-checkpoint — незавершене збереження джерел до браузерного gate. Нові runtime-залежності, навчальний алгоритм для 1482, SRS або N5–N1-архітектура не реалізовані. provenance.json відділяє авторське походження змін від відкритого походження успадкованих матеріалів і вже публічних копій.
