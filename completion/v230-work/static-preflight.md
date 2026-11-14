# v230 — static author-review preflight

Base main HEAD: `5354a748fe8ae147ae81f54f82da07e00ccccddc`

Base HTML SHA-256: `e5e298e9f5efcf45c7cfd1fe83ab9ce5a19dcde13759482d54e3b8313bd92dab`

## Scope and decisions

- 12 C11 blocker cards reviewed: 3363, 3375, 3417, 3441, 3444, 3525, 3561, 3565, 3569, 3594, 3636, 3646.
- 12 POS-map entries are changed in the candidate specification only; no card record, ID, example, translation, grammar item, lexical pair, reading override, target table, storage key or learning-engine rule is changed.
- 11 new context-specific meaning-quiz keys cover 22 contexts; the two existing reviewed ID3363 contexts are retained.
- All 24 authored contexts bind to the exact example strings in the v229 data.
- Each context has one correct option and three distinct distractors. Maximum correct/distractor length ratio: 1.4667; threshold: 1.5; remaining length warnings: 0.
- The source review is recorded separately in `source-review.md`. ID3636 has lower-confidence secondary POS evidence explicitly disclosed.
- v153 pilot credit is zero because all scoped IDs are outside the documented pilot range 121–320.

## Acceptance boundary

This document records static author-review preflight only. It is not a deterministic-build result, browser/Chromium result, pool-impact acceptance, independent linguistic acceptance or release approval.

The dedicated workflow trigger and verification PR have not returned an observable workflow run or commit status in this session. Therefore:
- no registry credit is applied;
- no candidate HTML is declared technically verified;
- no v230 release is published to main.

Next step: obtain a reproducible build, verify all 12 rendered cards, responsive widths, storage round-trip, JavaScript errors, reading/cloze pool effects and exact rollback; only then finalize the registry and publish exact verified blobs.
