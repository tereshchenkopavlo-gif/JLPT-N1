# Відтворення v137 — C04

```sh
python3 audit137/build.py
python3 audit137/check.py
node --check audit137/app.js
npm install --no-save playwright@1.56.1
npx playwright install --with-deps chromium
node audit137/targets-browser.cjs
node audit137/presentation.cjs
node audit137/ui.cjs
node audit137/browser-functional.cjs
node audit137/session-completion.cjs
python3 audit137/publish.py
```

Основа — повний v136. author.py містить 30 точних контекстних записів; build.py змінює тільки другий приклад/переклад v210, додає точні відповідності й контекстні питання та обмежує непридатний cloze/читання саме в цих реченнях. check.py виконує реальні старий/новий markTarget через scan.cjs для всіх 8089 прикладів. Первісні completion/target-diagnostics.json та triage лишаються історичними даними v135/v136; актуальний результат — audit137/scan-results.json і completion/C04-result.json після успішного gate.

targets-browser.cjs тестово керує Math.random лише для вибору кожного справжнього прикладу й типу питання: 30 контекстів ×3 ширини ×3 режими =270 генерацій, 90 показів/відповідей через renderPassage. У фінальному HTML тестових гачків немає. Окрема повна сесія запускається звичайною кнопкою без інструментації. Потрібний CJK-шрифт; скріншоти g18 і v447 на 412px пишуться в /tmp.

Перед публікацією потрібні успішні звіти з SHA-256 остаточного HTML. Зберігати повний новий HTML та аудит у main й звірити Git blob SHA. Авторський змістовий перегляд, технічний scan і браузерні сценарії мають різний обсяг; [джерела й межі](sources.md). Наступний пакет — C05, 526 однознакових кандидатів; C18 і всі інші незавершені задачі не закриті автоматично.
