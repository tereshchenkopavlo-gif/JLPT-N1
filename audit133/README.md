# Відтворення UI-випуску v133

Основа — повний кореневий v132 з перевіреним SHA-256. `localization.json` містить службові заміни. `build.py` захищає JSON-дані й таблиці порівнянь від замін, локалізує решту, додає `navigation.js`, панелі карток і presentation-only заголовки старих пояснень.

```sh
python3 audit133/build.py
python3 audit133/check.py
node --check audit133/app.js
npm install --no-save playwright@1.56.1
npx playwright install --with-deps chromium
node audit133/ui.cjs
node audit133/comparison.cjs
node audit133/browser-functional.cjs
node audit133/session-completion.cjs
python3 audit133/publish.py
```

Для візуального огляду потрібен японський CJK-шрифт. Скріншот зберігається в /tmp і не публікується. UI-тест тимчасово затримує `getCardData` всередині браузера для перевірки гонки; випуск не містить тестового інструментування. TouchEvents синтетичні, не фізичні жести.

`publish.py` вимагає точного SHA-256, результатів інваріантів, UI та порівнянь для тієї самої збірки. Після всіх перевірок готує повний HTML у корені, звіт, README й PROJECT_STATUS. Остаточно звірити blob SHA HTML і звіту з main.
