# v194 — C10 source review

Base: published v193, main commit `79254c60d84f8dba5d58979b10c44b33aa575a0c`, HTML SHA-256 `e5876cbc6e1799bf5aa8e4d4c6a07ee6cde1a14ffbdf5605cc1359d8623141c8`.

The v153 pilot rows for IDs883–906 were used as hypotheses. All 12 current cards were reread from the full v193 HTML.

## POS classification: ID903 我々

- The current HTML already provides a separate `代名詞` option in the `cardPos` filter.
- `getCardPool()` filters vocabulary by `vocabPartOfSpeech(id).includes(selectedPos)`; therefore the existing POS map can route this card without a UI or learning-engine change.
- Benesse's school-grammar explanation treats 代名詞 as a type of 名詞; WordRabbit notes that classification systems may either include pronouns under 名詞 or separate them. The app already exposes the separate filter, so this project assigns 我々 to `代名詞` and tests that it appears in that filter and not in `名詞`.
- Sources: Benesse, 「形式名詞・代名詞・連体詞の違い」 (https://www.benesse.jp/kyouiku/teikitest/chu/japanese/japanese/c00496.html); WordRabbit, 「名詞の種類・分類方法・代名詞」 (https://wordrabbit.jp/grammar/noun). This is a project taxonomy choice, not a claim about an official JLPT POS list.

## Card-specific reasoning

- 883: 塩加減 is the amount/degree of salt seasoning, not merely the number of salt units.
- 884: 加味 retains both literal flavour addition and figurative consideration of an extra factor.
- 885: 曲折 means complications/turns in the course of events; the translation should preserve that they are still expected before the bill is passed.
- 888: 意見を述べようとしない conveys unwillingness/refusal to express an opinion, stronger than merely not trying.
- 890: distinguish the act of imagining/creating something nonexistent from the resulting fictional thing; 架空の is the ordinary adjectival construction.
- 893: 火災報知機 is the detector/device, not necessarily the whole alarm system; 毎年定期的に is not “regularly every year” twice.
- 894: 本格的に means full-scale/full-fledged operation, not necessarily maximum capacity.
- 900: 資金繰り concerns securing/managing funds for current expenses and payments.
- 901: 過疎 describes the state of a sparsely populated region and its effects; 過疎化 names the process.
- 905: 高齢の親 does not force plural parents; 介護人材 is more naturally “care professionals/workforce”.
- 906: 慎重に検討する is naturally “carefully weigh/consider”, not the literal “consider the question whether”.

No Japanese example, ID, quiz target, comparison pair or progress-storage logic is changed.
