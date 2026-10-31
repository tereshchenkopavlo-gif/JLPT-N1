# Відтворення v131

Основа — повний кореневий v130 із перевіркою SHA-256. `medium_a.py`–`medium_c.py`, `long_a.py`–`long_c.py` — авторські тексти, переклади, питання й точні цитати. `notes.py` доповнює контекстну карту. `author.py` визначає схему. Початкова правильна відповідь у джерелі — перша; build переставляє варіанти, а генератор застосунку перемішує їх у кожній сесії.

```sh
python3 audit131/build.py
python3 audit131/invariants.py
python3 audit131/content-integrity.py
node --check audit131/app.js
npm install --no-save playwright@1.56.1
npx playwright install --with-deps chromium
node audit131/browser-smoke.cjs
node audit131/readings-browser.cjs
node audit131/browser-functional.cjs
node audit131/session-completion.cjs
python3 audit131/publish.py
```

`readings-browser.cjs` перехоплює тільки тестову копію HTML, щоб обрати конкретний індекс. Генерація, перестановка відповідей, відображення, обробники кліків і глосарій лишаються справжніми. Інші три сценарії відкривають повний HTML без інструментації. Скріншоти зберігаються в /tmp і не включаються до репозиторію. Для візуальної перевірки японського потрібен встановлений CJK-шрифт.

`publish.py` перевіряє відомий SHA-256 та результати gate, копіює повний HTML у корінь і готує актуальний звіт, README та PROJECT_STATUS. Старі звіти не переписуються. Публікація в main вважається завершеною лише після наявності повного HTML і звіту та звірки їх Git blob SHA.

Мовна перевірка: [EDITORIAL_REVIEW.md](EDITORIAL_REVIEW.md). Автоматичні перевірки не сертифікують змістову правильність і складність JLPT. Карта [coverage.json](coverage.json) містить тільки відібрані контекстні появи; тип `reviewed_context_occurrence` не означає прямого тестування всіх значень.
