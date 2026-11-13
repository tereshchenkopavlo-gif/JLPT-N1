# v182 source review — POS and reading-pool follow-up

**Date:** 13 November 2026.

## ID255 直接

- National Institute for Japanese Language and Linguistics, CHOKUSETSU entry: https://mmsrv.ninjal.ac.jp/kamus/data/item315.html
  - The entry labels 直接 as 名・副 (noun/adverb), and distinguishes 直接的 as 形動. The card's own examples support this: 直接お問い合わせください is adverbial; 直接の原因 is noun + の. The second example uses 直接的な, a separate derived adjective, not the base word 直接.
  - Proposed app POS: 名詞 + 副詞. Do not add ナ形.
- Current headword and reading: 直接・ちょくせつ. The card definition, examples, translations and usage note are internally consistent; its POS metadata is the open C10 item.

## ID327 浮気

- Shogakukan Digital Daijisen via Kotobank: https://kotobank.jp/word/%E6%B5%AE%E6%B0%97-442377
  - The entry labels modern うわき as 名・形動 (noun/na-adjective), including examples such as うわきな性分 and うわきな人. This supports 名詞 + ナ形. The card's usage note already records 浮気な人.
  - The same Kotobank page separately records historical ふき as an older noun reading. Do not use ふき as a wrong option: it is a real historical reading, not a safe distractor for the modern headword.
- Current headword and reading: 浮気・うわき. The two current examples and Ukrainian translations are semantically consistent; the POS metadata is the open C10 item.

## ID1819 内訳 and ID359 本気

- Shogakukan Digital Daijisen via Kotobank, 内訳: https://kotobank.jp/word/%E5%86%85%E8%A8%B3-440704
  - The entry gives うちわけ and the meaning of itemized contents. Keep it noun-only.
- ID359 本気 remains 名詞 + ナ形. After 浮気 is correctly marked as 名詞 + ナ形, うわき becomes a valid same-POS reading distractor for ほんき; it is not a reading of 本気.

## Proposed reading overrides (diagnostic only)

- ID255 直接: ちょうせつ (調節), ちょうせい (調整), ちくせき (蓄積).
- ID327 浮気: いしき (意識), いせき (遺跡), うつわ (器).
- ID1819 内訳: うちがわ (内側), うつわ (器), うわき (浮気).

Each proposed distractor is a verified reading already present in the vocabulary database, distinct from the target reading. The diagnostic will verify all affected pools under the corrected POS, not reuse the v180 hypothetical result. No POS, reading override or card content is changed by this source review.
