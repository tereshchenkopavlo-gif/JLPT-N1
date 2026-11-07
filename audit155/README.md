# Докази випуску v155

Основа — точний опублікований v154. `updates.json` містить 24 адресні зміни до/після з посиланнями на попередні авторські рішення. `scope.json` визначає обсяг та нові зарахування; `completion/v155-acceptance.tsv` містить хеші карток і зіставлень.

Відтворення: `python3 audit155/apply.py JLPT_N1_ukrainian_reading_v154.html /tmp/JLPT_N1_v155.html`. Потрібні Python 3 та Node; ціль має бути новим файлом. Очікуваний SHA-256: `39a765cc1b0e7e24ac353b06a647218db86fc99a790c99979ca12539b5a6d6d8`.

Браузерні сценарії збережені поруч. `prepare-review.py` готує лише метадані технічної перевірки; назва `editorial-review.json` успадкована і НЕ означає незалежного мовного приймання. Для повторення браузерних тестів використовуються Node, Playwright 1.56.1 та Chromium: команди й середовище зафіксовані в [workflow](https://github.com/tereshchenkopavlo-gif/JLPT-N1/blob/dcb2d5ad279d8cdd283a91f09cb553169319a9cb/.github/workflows/v155-checkpoint.yml). JSON-результати завантажено з успішного [run 42404596912](https://github.com/tereshchenkopavlo-gif/JLPT-N1/actions/runs/42404596912), artifact 13586454937.

22 картки ×3 ширини =66 відкриттів; три перевірки backup/import/reload; одна повна сесія; 12 сценаріїв 比較. Усі чотири результати містять SHA-256 точної опублікованої збірки. Це Linux Chromium 141.0.7390.37, не фізичний Android/Windows і не незалежний мовний аудит. Примітки AUTO_VOCAB_COMPARISONS перевірені як дані; чинний фільтр синонімів може не показувати їх у UI. Фільтр не змінювався.
