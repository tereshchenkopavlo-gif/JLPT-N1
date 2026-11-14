# v229 C11 source review

**Date:** 14 November 2026. **Scope:** IDs 2734, 544, 550, 552, 557, 588, 599, 644, 663, 1631, 3337, 3345. Sources below are lexical cross-checks, not a substitute for checking the actual card examples and app-specific quiz pools.

## Dictionary evidence and app decisions

- **2734 来る（きたる）:** Digital Daijisen's attributive sense before a date/event is 連体詞, not the ordinary verb くる. Both card examples are 来る三月一日に and 来るべき社会の変化. Correct the displayed/quiz POS map to 連体詞. Keep the internal category `DEFAULT_VOCAB.c` unchanged because it participates in automatic meaning-distractor grouping; test the reading/cloze consequences rather than silently changing that separate field. [Kotobank / Digital Daijisen](https://kotobank.jp/word/%E6%9D%A5%E3%82%8B-474513)
- **544 いい加減:** the dictionary has adjectival and adverbial use; both selected examples are いい加減な + noun, so ナ形 remains the canonical card/quiz class. The adverbial/degree use remains in usage. [Kotobank](https://kotobank.jp/word/%E5%A5%BD%E5%8A%A0%E6%B8%9B-2004689)
- **550 わがまま:** 名・形動 are recorded, but both selected examples are わがままな + noun; retain ナ形 as the canonical class and keep noun collocations in usage. [Kotobank](https://kotobank.jp/word/%E6%88%91%E3%81%8C%E5%84%98-664668)
- **552 確か:** 形動 and adverbial uses are recorded; the selected examples are 確かな + noun. Retain ナ形; usage separately explains 確かに and the recollective sentence use. [Kotobank](https://kotobank.jp/word/%E7%A2%BA%E3%81%8B-560354)
- **557 結構:** 名詞, 形動 and 副詞 uses are recorded; both selected examples use the adjectival/predicative 形動 sense. Retain ナ形; the adverbial use in 結構難しい remains in usage. [Kotobank](https://kotobank.jp/word/%E7%B5%90%E6%A7%8B-490460)
- **588 独特:** 名・形動 are recorded; the examples use 独特な. Retain ナ形 and explain の/な alternation in usage. [Kotobank](https://kotobank.jp/word/%E7%8B%AC%E7%89%B9-582817)
- **599 無礼:** 名・形動 are recorded; the examples use 無礼な. Retain ナ形; the noun collocation 無礼を詫びる remains in usage. [Kotobank](https://kotobank.jp/word/%E7%84%A1%E7%A4%BC-589872)
- **644 当然:** the dictionary records noun/adjectival/adverbial functions. The current card's 副詞 map is retained, but both examples are changed to clear adverbial use (当然変わってくる; 当然、…管理されなければならない). Usage distinguishes the supplemental 形動 forms 当然の結果 / 当然だ. [Kotobank](https://kotobank.jp/word/%E5%BD%93%E7%84%B6-580778)
- **663 オーバー:** 名詞・スル and 形動 uses are recorded. Both selected examples are noun + する (オーバーした / オーバーして); retain 名詞 and the explicit する marker. The な use remains in usage. [Kotobank](https://kotobank.jp/word/%E3%81%8A%E3%83%BC%E3%81%B0%E3%83%BC-3208656)
- **1631 相応:** 名詞 and 形動/スル functions are recorded. Both examples use 相応する / 相応した with the explicit する marker; retain 名詞 as the canonical quiz class and keep adjectival collocations in usage. [Kotobank](https://kotobank.jp/word/%E7%9B%B8%E5%BF%9C-89139)
- **3337 一切:** 名詞 and 副詞 functions are recorded. The selected examples use 一切関与しておりません and 一切こちらで負担いたします; the reviewed positive-context quiz payload is distinct from the negative use. Retain 副詞; usage keeps 費用の一切 as the noun construction. [Kotobank](https://kotobank.jp/word/%E4%B8%80%E5%88%87-434113)
- **3345 散々:** both 副詞 and 形動 use are recorded. Keep 副詞 as the canonical class by using adverbial examples (散々議論を重ねる; 散々に批判される); retain 散々な結果 as a supplementary 形動 example in usage, not as a second quiz POS tag. Update the byExample meaning payload for the changed sentence. [Kotobank](https://kotobank.jp/word/%E6%95%A3%E6%95%A3-513494)

## Limits

No rows from the v153 pilot cover these IDs: its accepted scope is ID121–320. No pilot credit is carried into this batch. The v182 POS/reading-pool review is used as a method precedent: test the actual pool impact before changing tags, and do not add tags that make four-option pools unusable. This is an author review, not independent linguistic acceptance.
