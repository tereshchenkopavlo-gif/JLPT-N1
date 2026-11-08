# Відтворення й докази v161

9 листопада 2026, Asia/Tokyo. Основа — точна v160. Повний HTML: 6932842 байти, SHA-256 `66d890eccd9477035f133eadcd0cb8300eb0daac2b13ef73edf2c8753e89fbfb`. Вісім before/after в updates.json, точний обсяг у scope.json.

Відтворення: `python3 audit161/apply.py JLPT_N1_ukrainian_reading_v160.html /tmp/JLPT_N1_v161.html`. Потрібні Python і Node, нова ціль. Exact rollback доводить незмінність байтів за межами восьми полів і заголовка версії. Пройшли JS-синтаксис, 3914/130, стабільність ID й чотири рендери перекладів.

[Workflow](https://github.com/tereshchenkopavlo-gif/JLPT-N1/blob/4a2e7e033a9977b564b0e5505e3b5583771e4430/.github/workflows/v161-checkpoint.yml), успішний [run 42492782483](https://github.com/tereshchenkopavlo-gif/JLPT-N1/actions/runs/42492782483), artifact 13622242861. Сім звітів із точним SHA-256: 27 відкриттів дев’яти карток, шість показів зміненої примітки в обох напрямах, 120 технічних генерацій meaning для двох визначень, backup/import/reload, повна сесія, 12 сценаріїв 比較.

Дев’ятий ID2694 у цій версії перевірено лише як партнера примітки: повної картки це не зараховує. Чотири різні відповіді не доводять семантичної якості автоматичних distractors; C11 відкрито. editorial-review.json — технічні метадані, не незалежна експертиза. Авторське приймання восьми карток — completion/v161-acceptance.tsv. Linux Chromium не закриває фізичний Android/Windows. Незалежне й правове приймання окремі.
