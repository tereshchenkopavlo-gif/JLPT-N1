# v180 — C11 meaning-choice and reading-pool diagnostics

## Exact base
- Main: `0efb016eac498c35559b0f14a929360b8db46eb0` (published v179).
- HTML: `JLPT_N1_ukrainian_reading_v179.html`, SHA-256 `359490152e9d4c7ae86cc746e2b69d132922946767890bc7aa7be6f5cdef2ba8`.
- Previous work checkpoint: `work/v179-c11-context-quiz-review` at `d55542503d39373084b8f9a6ec4fb361a9d27545`; its guarded publisher has already published v179. Do not merge that PR wholesale.
- Older diagnostic branch `work/v179-c11-reading-diagnostics` is preserved; its reading-pool findings are carried forward, not treated as new acceptance.

## Work in this checkpoint
1. Inspect the two automatic meaning-question payloads for ID2433 `そびえる`, their distractor plausibility, exact target/marking configuration, and interaction with cloze generation.
2. Inspect the actual runtime schema and lookup paths for `REVIEWED_MEANING_QUIZZES`, `REVIEWED_EXAMPLE_TARGETS`, and `VOCAB_KANA_EXAMPLE_TARGETS`. Test whether a contextual saved meaning set can be added without changing cloze availability or the engine. Do not change data in this diagnostic pass.
3. Reproduce the v179 reading-pool diagnosis using the exact v179 runtime. Enumerate source words/IDs for all changed candidates across the 23 affected pools, not only the eligibility counts. Review the losses for ID255, ID327, ID1819 and gain for ID359.
4. Preserve 3914 vocabulary records, 130 grammar records, stable IDs, all learning logic, progress keys and Git history.

## Acceptance boundary
This checkpoint is diagnostic only. No HTML, POS, reading override, saved quiz, scoring, or progress change is authorized here. A later content-only correction may be proposed if the existing schema supports it without disabling a valid task type. Any engine change remains outside the approved scope.
