# JLPT N1 v229 — C11 POS-map and meaning-quiz audit

**Date:** 15 November 2026 (Asia/Tokyo)  
**Base:** v228, HTML SHA-256 `189e4f570d61556cbc9073cf67cc106958e44706b9feeecd1c51abbc096ff5e8`  
**Candidate:** v229, HTML SHA-256 `e5e298e9f5efcf45c7cfd1fe83ab9ce5a19dcde13759482d54e3b8313bd92dab`  
**Size:** 6,960,249 bytes · **Git blob:** `1c90476d78ae832ccecbcdfbfb93cc83b99474eb`  
**Dedicated workflow:** [43621856689](https://github.com/tereshchenkopavlo-gif/JLPT-N1/actions/runs/43621856689) — success.

## Scope and author decisions

12 C11 blockers were resolved as `fixed_rechecked` after reviewing 24 exact example contexts:

`2734, 544, 550, 552, 557, 588, 599, 644, 663, 1631, 3337, 3345`.

The decisions are authorial, not independent linguistic acceptance. The exact per-card decisions and pool effects are in [v229-c11-review.tsv](completion/v229-c11-review.tsv), [v229-acceptance.tsv](completion/v229-acceptance.tsv), [v229-semantic-review.md](completion/v229-semantic-review.md), and [v229-pool-impact.tsv](completion/v229-pool-impact.tsv).

## Content and POS changes

1. **ID2734 来る（きたる）:** corrected `VOCAB_POS_BY_ID` from `動詞` to `連体詞`. Digital Daijisen classifies the date/event-modifying きたる as 連体詞; it is distinct from ordinary くる. The canonical `DEFAULT_VOCAB.c` field was deliberately left unchanged because it also participates in automatic meaning-distractor grouping. The POS change reduces the reading pool from 6 to 0 and the cloze pool from 705 to 2. Both pools are now ineligible because they have fewer than three valid choices. No synthetic distractors or learning-algorithm changes were introduced.
2. **ID644 当然:** replaced both selected examples and translations with clear adverbial contexts, and clarified the usage note to distinguish 副詞 from supplemental 形動 forms such as 当然の結果 / 当然だ.
3. **ID3345 散々:** replaced the second example with 散々に批判される, updated its Ukrainian translation and usage note, and revised the global and byExample quiz payloads. 散々な結果 remains identified as a supplementary 形動 use.

Ten new reviewed meaning-quiz keys were added for IDs 1631, 2734, 544, 550, 552, 557, 588, 599, 644 and 663. Existing byExample payloads were updated for IDs 3337 and 3345. These changes separate context-specific senses and remove weak answer-length or context-drift cues.

## Meaning-quiz review

All 24 example contexts were manually reviewed for contextual key fit, distractor falsity and distinctness, ambiguity, semantic overlap and length cues. Chromium verified 24/24 reviewed overrides against the rendered quiz options. The structural and length diagnostics passed: each context had three unique distractors, the correct answer was excluded, and the max/min option-length ratio did not exceed 1.5.

## Technical verification

The dedicated v229 workflow passed all steps:
- deterministic reproduction from the exact v228 HTML;
- Python compilation of preparation/finalization scripts and Node syntax check;
- exact reversible patch back to v228;
- inventory: 3,914 vocabulary records, 130 grammar constructions, 859 lexical pairs, 3,914 unique vocabulary IDs;
- all 12 scoped cards rendered with expected POS, meaning, usage, examples and translations;
- meaning diagnostics: 24 contexts; reviewed override checks: 24/24;
- Chromium responsive checks at 360, 412 and 1280 px, with no horizontal overflow;
- storage round-trip and restore passed; zero page errors.

The browser evidence confirms unchanged `DEFAULT_VOCAB`, `GRAMMAR_DETAILS_BY_ID`, `VOCAB_AUDITED_PAIRS`, `REVIEWED_READING_OPTIONS`, `VOCAB_KANA_EXAMPLE_TARGETS`, `REVIEWED_EXAMPLE_TARGETS`, and storage keys. The app's learning engine and state schema were not changed.

## Registry after v229

- Overall: 4,017 reviewed / 487 fixed_rechecked / 1,327 pending / 16 blocked (5,847 objects).
- Vocabulary: 3,412 reviewed / 485 fixed_rechecked / 1 pending / 16 blocked.
- Lexical pairs: 54 reviewed / 1 fixed_rechecked / 804 pending.
- Author credit: **3,897 / 3,914**.

The remaining C11 blockers are: `3363, 3375, 3417, 3441, 3444, 3525, 3561, 3565, 3569, 3594, 3636, 3646, 3652, 3654, 3677, 3679`. ID1510 remains a separate pending safety hold and was not evaluated in this batch.

## Pilot and limitations

The documented v153 pilot scope is ID121–320. None of the v229 IDs falls within that scope, so no pilot credit was applied. Existing pilot evidence and historical audit rows were not rewritten.

This report records an author review and technical acceptance only. Independent linguistic acceptance, physical Android/Windows acceptance, and provenance/legal review remain open. The legacy v178 workflow also continues to fail separately; it did not invalidate the successful dedicated v229 workflow.
