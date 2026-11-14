# v230 C11 next blockers

Base: v229 published in main. This branch is a preaudit checkpoint only.

1. Read `checkpoint.json` and `preaudit-notes.md`.
2. Inspect all 12 cards in v229 and their existing meaning quiz payloads.
3. Verify each POS/sense with Japanese dictionaries; do not apply broad dictionary POS blindly.
4. Measure reading/cloze pool impact before any POS-map change.
5. Review exact example-context meaning options and byExample bindings.
6. Only after manual decisions, prepare the deterministic patch, browser checks and registry transition.
7. Keep author review, technical tests and independent acceptance separate.

Baseline diagnostics run 43622947862 succeeded: 12 cards rendered, 24 contexts structurally valid, but two answer-length outliers in ID3444; only ID3363 has existing reviewed overrides. Reading pool: ID3375 has 4 candidates, other 11 have 0; cloze pools all remain eligible. No application data or registry rows have been changed in this checkpoint. No credit has been granted. Pilot v153 does not cover these IDs (121–320 only).
