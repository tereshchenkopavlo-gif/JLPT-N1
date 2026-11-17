# v230 C11 POS and meaning review

Review base: published v229 HTML from main HEAD `5354a748fe8ae147ae81f54f82da07e00ccccddc`; latest status-only main HEAD `afb7f3aa5ebe3d16b1a66e6aabec1648b9cb0dba` (HTML unchanged); HTML SHA-256 `e5e298e9f5efcf45c7cfd1fe83ab9ce5a19dcde13759482d54e3b8313bd92dab`.

## Review state

- Manual author review: 12/12 cards and 24/24 exact example contexts.
- POS-map changes scoped to 12 entries; 11 new context-specific meaning-quiz keys cover 22 contexts; ID3363's two existing reviewed contexts are retained.
- Static preflight: exact example binding and distinct-option checks pass; maximum correct/distractor length ratio is 1.4667 against a 1.5 limit.
- Source review: `source-review.md`; ID3636 retains an explicitly lower-confidence secondary-source note.
- v153 pilot credit: zero; this scope is outside the documented pilot IDs 121–320.

## Reviewed-cloze gate — implementation candidate

The user approved a narrow engine change on 17 November 2026 with strict compatibility and quality conditions. The candidate therefore adds an exact-example `REVIEWED_CLOZE_QUIZZES` gate. It can coexist with a reviewed meaning key only when the exact example has three manually reviewed, distinct cloze distractors. Legacy cards continue through the existing random-pool path; cards with reviewed meaning keys stay meaning-only unless an exact reviewed cloze payload exists.

All 24 v230 contexts were manually assessed for cloze suitability. None proved a unique target against three high-quality alternatives: near-synonyms or other natural completions would make the answer ambiguous, while the automatic POS pools contain many unrelated words. Consequently v230 intentionally contains zero reviewed cloze payloads; the gate is inert, and no artificial task is created merely to preserve a count. The 22 newly suppressed contexts must be recorded as explicit linguistic rejections rather than accepted exercises.

Acceptance requires a whole-bank before/after Chromium comparison showing exactly those 22 documented suppressions and zero changes elsewhere, plus the existing meaning, POS, responsive, storage, rollback and registry checks. ID3375's reading pool remains 4→0 and must not be filled with invented readings. Do not apply registry credit or publish v230 until the new workflow succeeds.

The implementation branch `work/v230-reviewed-cloze-gate` is intentionally separate. Do not merge the older diverged branches wholesale.

Independent linguistic acceptance, Android/Windows device tests and provenance/legal acceptance remain separate.
