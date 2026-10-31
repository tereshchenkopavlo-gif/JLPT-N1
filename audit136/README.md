# Відтворення v136

Основа — повний v135. Нові джерела — build.py, runtime.js, style.css і presentation.json. Дані карток/прикладів/питань і механізм навчальних сесій зберігаються; POS — окремий реєстр подання.

```sh
python3 audit136/build.py
python3 audit136/check.py
node --check audit136/app.js
npm install --no-save playwright@1.56.1
npx playwright install --with-deps chromium
node audit136/presentation.cjs
node audit136/ui.cjs
node audit136/browser-functional.cjs
node audit136/session-completion.cjs
python3 audit136/publish.py
```

Для візуального перегляду потрібний CJK-шрифт (CI: fonts-noto-cjk). presentation.cjs перевіряє збереження текстів після форматування, усі варіанти фільтра, їх поєднання з пошуком/темою/S/G/X, навігацію, порівняння та reload на 360/412/1280px. Скріншоти в /tmp: v136-regulation, v136-title, v136-grammar, v136-list. Старий UI-тест адаптовано до окремого блоку приєднання й нових заголовків без 【】; перевірки гортання, гонки відповідей та оцінювання збережено.

publish.py вимагає точну контрольну суму фінального HTML і відповідних звітів. Публікація повного HTML/аудиту/README/PROJECT_STATUS — лише після успішного gate. План і критерій C18 — completion/PLAN.md та BACKLOG.md. Джерело макета й межі авторського перегляду — sources.md. Фізичні пристрої не замінюються вузьким Chromium.
