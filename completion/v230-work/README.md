# v230 C11 POS and meaning review

Base: exact published v229 HTML from current main HEAD `5354a748fe8ae147ae81f54f82da07e00ccccddc`; HTML SHA-256 `e5e298e9f5efcf45c7cfd1fe83ab9ce5a19dcde13759482d54e3b8313bd92dab`.

The manual author review is prepared for 12 cards and 24 exact example contexts. The candidate changes only 12 scoped POS-map entries and 11 context-specific meaning-quiz keys (22 contexts); ID3363's two existing reviewed contexts are retained. No vocabulary records, grammar, examples, translations, lexical pairs, reading overrides, target tables, learning logic or storage keys are changed.

1. `python3 completion/v230-work/prepare.py` reproduces the candidate from exact v229 HTML.
2. `node --check completion/v230-work/diagnose.cjs`.
3. The current main workflow runs deterministic preparation, Chromium verification, pool-impact checks and registry finalization.
4. The workflow saves the full candidate HTML and evidence to this branch only.
5. Publish only exact verified blobs to main after rechecking main HEAD; do not merge this diverged work branch wholesale.

The v153 pilot covers only IDs 121–320; none of this scope qualifies for pilot credit. ID3636 has lower-confidence secondary POS sourcing explicitly recorded in source-review.md. Independent linguistic, physical-device and provenance/legal acceptance remain separate.
