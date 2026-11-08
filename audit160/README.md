# Відтворення й докази v160

Основа — точна v159. Повний HTML: 6932653 байти, SHA-256 `2806c4733c2e203a5a5ec5a2fd5d3535e5fc5559a77d65b4c7f6ade6be6b9f21`. updates.json зберігає 23 before/after і первинні поіменні докази; scope.json — точний обсяг.

Відтворення: `python3 audit160/apply.py JLPT_N1_ukrainian_reading_v159.html /tmp/JLPT_N1_v160.html`. Потрібні Python і Node, нова ціль. technical-results.json: точний rollback, JS-синтаксис, вісім рендерів. За межами 23 полів і заголовка версії байти незмінні.

[Workflow](https://github.com/tereshchenkopavlo-gif/JLPT-N1/blob/4cdc0b88dd775e9a098fdeb3ccf35dc650897239/.github/workflows/v160-checkpoint.yml), успішний [run 42474263967](https://github.com/tereshchenkopavlo-gif/JLPT-N1/actions/runs/42474263967), artifact 13614583514. Усі шість кінцевих JSON-звітів містять SHA-256 випуску: 21 картка ×3 ширини =63 відкриття; 120 генерацій meaning-payload для двох змінених визначень; backup/import/reload на трьох ширинах; повна сесія; 12 сценаріїв 比較. POS і пари незмінні, нової правки фільтра немає.

definition-quiz-results.json перевіряє працездатність залежного добору: чотири різні рядки, коректний формат; це не семантичне приймання всіх автоматичних альтернатив. editorial-review.json — технічний перелік цілей, не незалежна експертиза. Авторське приймання — completion/v160-acceptance.tsv: змінене повторно прочитано, незмінене звірено з поіменними висновками. Це Linux Chromium; фізичний Android/Windows, незалежна експертиза, C11 і походження окремі.
