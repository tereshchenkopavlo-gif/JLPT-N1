# Відтворення й докази v157

Основа — точна v156. Кінцевий HTML має 6930348 байтів, SHA-256 `96a4d5f2d4754aa720dd50bee6e539ecc5dc3354c82ed0c1fa14dc0e2293667b`. `updates.json` містить 22 before/after з джерелами й попередніми висновками; scope.json — точний обсяг.

Відтворення: `python3 audit157/apply.py JLPT_N1_ukrainian_reading_v156.html /tmp/JLPT_N1_v157.html`. Потрібні Python і Node, ціль — новий файл. technical-results.json фіксує точний rollback до початкових байтів, 22 поля, JS-синтаксис та показ 11 перекладів. Незмінність усіх інших даних і функцій перевірена точним зворотним порівнянням.

[Workflow](https://github.com/tereshchenkopavlo-gif/JLPT-N1/blob/6341e163ebe625dc7f0a416e0d12b461d69d77d0/.github/workflows/v157-checkpoint.yml), успішний [run 42441002273](https://github.com/tereshchenkopavlo-gif/JLPT-N1/actions/runs/42441002273), artifact 13601628091. Усі кінцеві JSON-звіти містять SHA-256 випуску. 20 карток ×3 ширини =60 відкриттів; сім POS ×4 класи ×3 ширини =84 адресні перевірки включення/виключення; регресія двобічної пари 分担／分配; backup/import/reload на трьох ширинах, одна повна сесія та 12 сценаріїв 比較.

Незалежного мовного й фізичного приймання не виконано: це Linux Chromium. `editorial-review.json` має успадковану назву, але містить лише метадані для технічного показу. Авторські висновки й хеші повних даних карток та POS — completion/v157-acceptance.tsv. Генеровані варіанти вправ і походження/правове приймання окремі.
