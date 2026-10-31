# Відтворення v134

Основа — повний кореневий v133. `changes.json` містить дозволені зміни usage двох карток і note чотирьох пар. Індекси пар починаються з нуля; ID карток збережені. `candidates.json` — результат пошуку в 859 парах, `logic-review.json` — прицільний авторський перегляд 40 кандидатів. Результат «retained» стосується логічного переходу, а не повної мовної сертифікації.

```sh
python3 audit134/build.py
python3 audit134/check.py
node --check audit134/app.js
npm install --no-save playwright@1.56.1
npx playwright install --with-deps chromium
node audit134/pairs.cjs
node audit134/ui.cjs
node audit134/browser-functional.cjs
node audit134/session-completion.cjs
python3 audit134/publish.py
```

`pairs.cjs` перевіряє фактичний показ восьми карток і тих самих чотирьох приміток у 比較, usage та збереження списку після reload. UI-регресія успадкована від v133; синтетичні TouchEvents не є фізичними жестами. Скріншоти з CJK-шрифтом зберігаються в /tmp.

`publish.py` вимагає відомого SHA-256 й відповідності йому звітів. Після gate копіює весь HTML у корінь, готує звіт, README й PROJECT_STATUS. Перед завершенням звірити blob SHA HTML і звіту з main. [Джерела](sources.md); книга 日本語の森 не використовувалася.
