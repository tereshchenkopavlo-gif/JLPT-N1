# Відтворення v132

Основа — повний кореневий v131 із перевіркою SHA-256. `medium_a.py`–`medium_d.py` та `long_a.py`–`long_d.py` містять авторські тексти, переклади, питання, альтернативи та цитати. `notes.py` додає лише вручну дібрані контекстні значення. `author.py` визначає схему. У джерелі правильна відповідь стоїть першою; build переставляє варіанти, а генератор застосунку знову перемішує їх у сесії, зберігаючи ключ.

```sh
python3 audit132/build.py
python3 audit132/invariants.py
python3 audit132/content-integrity.py
node --check audit132/app.js
npm install --no-save playwright@1.56.1
npx playwright install --with-deps chromium
node audit132/browser-smoke.cjs
node audit132/readings-browser.cjs
node audit132/browser-functional.cjs
node audit132/session-completion.cjs
python3 audit132/publish.py
```

`readings-browser.cjs` вибирає конкретний текст тільки в перехопленій браузером тестовій копії HTML. Генератор, renderer, перестановка ключів, обробники відповідей і глосарій лишаються справжніми. У випуску немає тестових гачків. Три інші сценарії відкривають неінструментований файл. Скріншоти — у /tmp; для японського візуального огляду потрібен CJK-шрифт.

`publish.py` перевіряє відомий SHA-256 і відповідність йому браузерного звіту, потім додає повний HTML у корінь і готує актуальні audit/README/PROJECT_STATUS. Старі звіти не змінюються. Публікацію вважати завершеною лише після звірки Git blob SHA HTML і звіту з main.

[EDITORIAL_REVIEW.md](EDITORIAL_REVIEW.md) відокремлює авторський змістовий перегляд від автоматичних перевірок. [coverage.json](coverage.json) — 85 опрацьованих появ, а [direct-question-links.json](direct-question-links.json) — лише три прямі питання. Ширше покриття карток із цих кількостей не випливає.
