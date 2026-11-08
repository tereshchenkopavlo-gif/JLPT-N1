# Відтворення й докази v159

Основа — точна v158. Повний HTML: 6932144 байти, SHA-256 `f86e9a1cb11a371d58dfe0dd642a13a49310fdb3fecc23f45036af5ad0381309`. updates.json зберігає 25 before/after і джерела; scope.json — точний обсяг.

Відтворення: `python3 audit159/apply.py JLPT_N1_ukrainian_reading_v158.html /tmp/JLPT_N1_v159.html`. Потрібні Python і Node, нова ціль. technical-results.json: точний rollback, 25 полів, JS-синтаксис, вісім рендерів перекладів. За межами перелічених полів і заголовка версії байти незмінні.

[Workflow](https://github.com/tereshchenkopavlo-gif/JLPT-N1/blob/c16d70efe62f3baaab988af8bd34329939b363b0/.github/workflows/v159-checkpoint.yml), успішний [run 42458212664](https://github.com/tereshchenkopavlo-gif/JLPT-N1/actions/runs/42458212664), artifact 13608965526. Усі шість кінцевих звітів мають SHA-256 випуску: 21 картка ×3 ширини =63 відкриття; шість POS ×4 класи ×3 ширини =72 перевірки; нова примітка 手さばき／手つき в обох картках на трьох ширинах; регресія попередньої пари 分担／分配; backup/import/reload; повна сесія; 12 сценаріїв 比較.

editorial-review.json містить технічний перелік цілей, не незалежну експертизу. Авторське приймання — completion/v159-acceptance.tsv: змінені поля повторно прочитані в японському контексті, незмінені звірені з поіменними доказами v157/v158. Це Linux Chromium; фізичний Android/Windows, незалежна експертиза, генеровані вправи й правове приймання окремі.
