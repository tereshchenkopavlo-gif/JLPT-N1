# JLPT N1 v181 — C11 context-specific meaning quiz review

**Дата:** 13 листопада 2026. **Основа:** v179, SHA-256 359490152e9d4c7ae86cc746e2b69d132922946767890bc7aa7be6f5cdef2ba8. **Кандидат:** v181, SHA-256 6a090e7e8108e37d1ec2ccf0b2ccbef88c54b04927d2d3f0bc1829bdfe4fd028 (6,940,562 байт).

## Авторський перегляд

Для вже авторськи прийнятої картки **ID2433 そびえる** додано два окремі meaning-набори, прив'язані до точних прикладів:

- 市の中心部には、高さ二百メートルの超高層ビルがそびえている。
- 雪をいただいた山々が、湖の向こうにそびえて見える。

Автоматичні meaning-дистрактори до v181 бралися з віддалених значень інших карток і не перевіряли знання саме そびえる. Нові варіанти зосереджені на просторовому значенні «дуже високо стояти/височіти» та зіставляють висоту, положення й форму споруди або рельєфу. Для кожного прикладу є одна правильна відповідь, три різні хибні відповіді та українське контекстне пояснення.

**Це приймання двох контекстних наборів питань, а не повторне повнокарткове приймання ID2433.** Авторський credit словника не змінено.

## Cloze та точне виділення

Обидва речення містять форму **そびえて**, а не словникову форму **そびえる**. Чинна перевірка literal cloze вимагає точного збігу виділеної форми з headword, тому cloze для цих двох речень не був доступний і до v181. Додавання збережених meaning-наборів не забрало доступну вправу: Chromium відтворив false до й після для обох контекстів. Точне виділення そびえて збережено.

## Технічні перевірки

Детермінований preparer підтвердив основу v179, точний SHA кандидата, повний rollback і єдину зміну даних у REVIEWED_MEANING_QUIZZES.v_2433 плюс заголовок версії. Не змінювалися 3914 словникових записів, 130 граматичних конструкцій, 859 лексичних пар, ID, POS, reading overrides, навчальна логіка та код збереження прогресу. Chromium перевірив обидва контексти через quizMeaningOptions і generateOfflinePassage, чотири унікальні варіанти, правильний ключ, пояснення, точне виділення, cloze eligibility та контрольний sentinel прогресу. Перевірено ширини 360, 412 і 1280 px без горизонтального переповнення.

Докази: completion/v181-prepare-results.json, completion/v181-browser-results.json, completion/v181-registry-results.json, completion/v181-c11-review.tsv, completion/v181-acceptance.tsv.

## Облік і межі

- Авторський credit словника: **3385/3914**, без змін.
- Завершальний реєстр: **3893 reviewed / 59 fixed_rechecked / 1892 pending**.
- Збережені reviewed meaning quiz: **267** (додано один об'єкт із двома контекстними payload).
- ID255/327 залишаються відкритими POS/reading-питаннями. Діагностика v180 відтворила 23 змінені reading-пули; три цілі втрачають поріг трьох дистракторів (ID255, ID327, ID1819), один набуває його (ID359). POS і reading overrides у v181 не змінювалися.
- Незалежне лінгвістичне, фізичне та правове/походження приймання не виконані. v181 — проміжний випуск, не кандидат 1.0.

## Джерела

# v181 C11 — source review for ID2433 そびえる

**Accessed:** 13 November 2026.

## Lexical basis

- Shogakukan Digital Daijisen via Kotobank, 聳える: https://kotobank.jp/word/%E8%81%B3%E3%81%88%E3%82%8B-555102
  - The contemporary sense is an intransitive verb: mountains, buildings, etc. stand very high; the entry gives examples involving a sacred peak and high-rise housing.
  - This supports the existing card definition “山や建物などが、非常に高く立っている。” and the Ukrainian gloss “височіти, здійматися”.
- The exact v179 card examples are preserved. Both contain the inflected form そびえて, which is already bound to the headword by VOCAB_KANA_EXAMPLE_TARGETS. No example text or target mapping was changed.

## Question design

- Building context: the correct option expresses a building standing very high relative to its surroundings. The three distractors describe a lower position, equal height with surrounding buildings, and horizontal spread.
- Mountain context: the correct option expresses a mountain standing very high relative to its surroundings. The distractors describe a low valley-like position, a low rounded hill, and a flat continuation at ground level.
- All four options in each context are distinct and comparable in grammatical form and approximate length. The Ukrainian note identifies the contextual sense and explains the contrast.
- The existing automatic candidates for そびえる included unrelated meanings from other cards (e.g. twisting, shifting position, irritation, protection, following a route). The saved context-specific sets replace those unrelated options only for the two exact examples.

## Cloze boundary

The existing literal-cloze gate requires the marked span to equal the dictionary headword. Here the reviewed exact form is そびえて, not そびえる, so literal cloze was already unavailable for both examples. The saved meaning entry also excludes cloze for that card under the existing rule, but the before/after diagnostic confirms that no previously available cloze route is lost. No code or learning mechanism was changed.

## Related open diagnostic

v180 reproduced the exact reading algorithm after the proposed POS additions for ID255/327. It changed 23 pools, caused ID255, ID327 and ID1819 to fall below three automatic distractors, and gave ID359 a third distractor. No POS or reading override changes are included in v181. The full diagnostic is preserved as completion/v180-c11-diagnostics.json and remains diagnostic evidence, not author acceptance.

