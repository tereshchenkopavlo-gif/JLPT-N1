# v229 C11 pre-audit notes

**Baseline:** published v228, main commit `bd66e3b3f01ae669bb4f3305d3f6652efb5d42f3` (workflow infrastructure commit); HTML SHA-256 `189e4f570d61556cbc9073cf67cc106958e44706b9feeecd1c51abbc096ff5e8`.

**Scope:** 12 blocked cards: 2734, 544, 550, 552, 557, 588, 599, 644, 663, 1631, 3337, 3345.

## Initial findings

- ID2734 来る is the lexicalized attributive reading きたる in both examples. Digital Daijisen classifies this sense as 連体詞. The current display/quiz POS map says 動詞. The internal category field `DEFAULT_VOCAB.c` is also used by the meaning-distractor grouping, so it must not be changed without a separate pool analysis. Candidate POS-map correction only: 連体詞.
- IDs 544 いい加減, 550 わがまま, 552 確か, 557 結構, 588 独特, 599 無礼: the selected examples consistently use the primary な-adjectival function; supplementary noun/adverbial uses are already described in usage. The POS map is a canonical quiz/display class, not an exhaustive list of every dictionary entry label. No extra POS tags are proposed.
- ID644 当然: the current map is 副詞 but both current examples use 当然の + noun. Replace with two clear adverbial examples so the card's displayed/quiz POS matches the examples; preserve the 副詞 pool.
- ID663 オーバー and ID1631 相応: current examples use the noun + する construction, consistent with the noun POS map and explicit する marker. Do not add 形動 as a second quiz tag without a separate pool justification.
- ID3337 一切: both examples are adverbial; the positive-context reviewed byExample payload distinguishes 一切負担する from the negative construction. The noun use remains documented in usage. Keep the current 副詞 map.
- ID3345 散々: current second example uses 散々な as a な-adjectival form while the first is adverbial. Replace the second with an unambiguous adverbial example and update its exact byExample meaning payload; retain the supplementary 形動 use in usage.

The browser run must quantify every affected reading/cloze pool, inspect all meaning-option sets, verify card rendering, storage round-trip/restore, and responsive widths. No C11 credit or main publication until the diagnostics have been reviewed.

## First diagnostic review: quiz distractors

The first Chromium run exposed answer-length cues and context drift in automatic meaning quizzes for IDs 2734, 544, 552, 557, 588, 599, 663 and 1631. Added only scoped reviewed payloads for these eight cards; ID557 and ID663 use byExample payloads because the two examples instantiate distinct senses. ID550 and ID644 automatic options were balanced and semantically distinct. Existing reviewed options for ID3337 and ID3345 were retained. The next browser run must assert three unique wrong answers, correct-answer exclusion and max/min option length <= 1.5 for every example.
