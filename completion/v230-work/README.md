# v230 C11 POS and meaning review

Review base: published v229 HTML from main HEAD `5354a748fe8ae147ae81f54f82da07e00ccccddc`; latest status-only main HEAD `afb7f3aa5ebe3d16b1a66e6aabec1648b9cb0dba` (HTML unchanged); HTML SHA-256 `e5e298e9f5efcf45c7cfd1fe83ab9ce5a19dcde13759482d54e3b8313bd92dab`.

## Review state

- Manual author review: 12/12 cards and 24/24 exact example contexts.
- POS-map changes scoped to 12 entries; 11 new context-specific meaning-quiz keys cover 22 contexts; ID3363's two existing reviewed contexts are retained.
- Static preflight: exact example binding and distinct-option checks pass; maximum correct/distractor length ratio is 1.4667 against a 1.5 limit.
- Source review: `source-review.md`; ID3636 retains an explicitly lower-confidence secondary-source note.
- v153 pilot credit: zero; this scope is outside the documented pilot IDs 121–320.

## Technical status — BLOCKED BY CLOZE AVAILABILITY REGRESSION

Run 43652194837 reproduced the candidate from the exact v229 HTML and completed Chromium diagnostics. All 12 cards rendered; 24/24 meaning contexts passed structure, length and exact-override checks; 12/12 visible POS labels matched; responsive 360/412/1280, storage round-trip and zero-page-error checks passed. The finalizer intentionally failed because 22 previously available cloze contexts across 11 cards are suppressed by the new REVIEWED_MEANING_QUIZZES keys. ID3363 already had a reviewed meaning key in v229, so it adds no new loss. ID3375 also loses reading-pool eligibility (4→0) after the POS-map change. See cloze-availability-review.md and the committed browser/pool diagnostics. Do not apply registry credit or publish v230.

The work branch is intentionally diverged from main. Do not merge it wholesale. A user decision is required before proceeding: either accept meaning-only quiz coverage for the affected cards, or explicitly approve a learning-engine change to retain cloze alongside reviewed meaning quizzes. Any engine change must be separately reviewed and rerun through all regression checks.

Independent linguistic acceptance, Android/Windows device tests and provenance/legal acceptance remain separate.
