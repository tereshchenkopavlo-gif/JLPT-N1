# v130 — функціональні перевірки навчальної сесії

Дата: 2026-10-31. Підтверджений успішний GitHub Actions: https://github.com/tereshchenkopavlo-gif/JLPT-N1/actions/runs/41175691039 (коміт `0b858d65`).

На екранах 360, 412 і 1280 px Chromium успішно: починає сесію кнопкою `#btnStartSession`, пропускає навчальний вступ, відкриває реальний `#passageArea`, бачить по 3 питання з 4 варіантами, вибирає варіант кожного питання, перевіряє появу непорожнього пояснення `.qexplain`, виставляє S у трьох `.raterow` і перевіряє, що `#btnPassageNext` став активним. Не було `pageerror`.

Це верифікація **інтерактивної механіки**, а не правильності мовних пояснень або дистракторів: перший варіант відповіді обирався незалежно від правильності. Окремо тестувати правильну/неправильну відповідь і зміни CSS стану. Перевірка переходу кнопкою «次へ進む» додана комітом `b1a3f4a0` і очікує окремого результату CI.

У попередньому підтвердженому запуску https://github.com/tereshchenkopavlo-gif/JLPT-N1/actions/runs/41175376617 пройшов також експорт → імпорт → перезавантаження **непорожнього списку порівнянь**, створеного через кнопку на картці, і синтетичних непорожніх записів для лексики та граматики (усі три ширини). 

Стан: реліз v130 ще не опубліковано як фінальний самостійний HTML-файл.

## Full-session completion (confirmed)

GitHub Actions [run 41176110807](https://github.com/tereshchenkopavlo-gif/JLPT-N1/actions/runs/41176110807), commit `f8db012f`: **success**. In a live Chromium session at 412 px, the test completed 6 passages, selected 15 answers, graded 18 visible rating rows, reached the completion screen, verified the nonempty summary (`S判定:10件　G判定:0件　X判定:0件`), returned home, checked persisted localStorage (1022 bytes), and reloaded to confirm saved data remained available. This is a verified UI / storage flow, not an audit of every Japanese answer's correctness or of score semantics.

Also validated per-question answer feedback markers: one `correct` choice per question and `correct` or `wrong` styling on the selected choice across screen widths 360, 412, and 1280 px.
