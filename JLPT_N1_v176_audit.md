# JLPT N1 v176 — C10 follow-up audit

**Release:** v176  
**Base:** published v175  
**HTML:** JLPT_N1_ukrainian_reading_v176.html  
**SHA-256:** __HTML_SHA256__  
**Bytes:** __HTML_BYTES__

## Scope and decisions

Author-reviewed 12 pending vocabulary cards: 255, 278, 327, 330, 332, 335, 339, 347, 349, 350, 353, 355. Ten cards were corrected in ten exact fields and rechecked: 278, 330, 332, 335, 339, 347, 349, 350, 353, 355. IDs 255 and 327 remain pending because the more complete POS classification reduces the existing reading-choice pool below the required three distractors. No learning mechanism or POS data was changed.

Four lexical pairs were reviewed without content changes: 72 (293/353), 81 (339/341), 85 (349/350), and 167 (658/335).

## Exact changes

- ID278 同士: clarified the noun meaning and N＋同士 suffixal relation; kept the noun POS label.
- ID330 舞台: corrected the Ukrainian translation of 下町 in the Edo-period context.
- ID332 復習: distinguished 学び直し from ordinary review in the usage note.
- ID335 物語: corrected the tense of 戦時下に生きた.
- ID339 分解: expanded the Japanese definition to cover both dividing and becoming divided.
- ID347 保管: broadened the Japanese definition to include proper storage without requiring custody of another person's item.
- ID349 補給: made the fuel-supply translation idiomatic.
- ID350 補充: made the stock-replenishment translation idiomatic.
- ID353 崩壊: expanded the Japanese definition to include institutions and systems.
- ID355 法律: translated 罰則が科されることがある as the possible imposition of sanctions.

## POS and reading-pool dependency

The v153 pilot already recorded that adding 副詞 to ID255 removed all six reading candidates. The v176 Chromium diagnostic used the exact quizReadingOptions function and current vocabulary pool:

| ID | Current POS | Proposed POS | Current choices | Proposed choices | Decision |
|---|---|---|---:|---:|---|
| 255 直接 | 名詞 | 名詞＋ナ形 | at least 3 | 0 | pending |
| 278 同士 | 名詞 | 名詞＋接尾語 | at least 3 | 0 | keep 名詞; suffixal use explained |
| 327 浮気 | 名詞 | 名詞＋ナ形 | at least 3 | 2 | pending |

A reading question requires at least three wrong options. The POS tags and quiz mechanism were not changed. IDs 255 and 327 remain open for a C11-compatible, evidence-based distractor decision; ID278 remains correctly represented as a noun with suffixal use.

## Technical checks

- 3914 vocabulary records and IDs preserved.
- 130 grammar records and IDs preserved.
- 859 lexical pairs preserved.
- POS map and reviewed quiz data blocks unchanged.
- Exact rollback to v175 reproduced.
- Inline scripts passed Node syntax checks.
- Chromium rendered all 12 reviewed cards and all examples at 360, 412, and 1280 px.
- All ten updated fields appeared in the rendered cards.
- Four reviewed lexical pairs remained byte-for-byte identical.
- Progress-storage sentinel remained unchanged.

## Acceptance boundary

This is an **author linguistic review** plus a targeted technical regression. It is **not independent linguistic acceptance**, **not legal/provenance acceptance**, and **not physical Android/Windows acceptance**. C10 and the agreed 1.0 completion plan remain open.
