# v230 C11 POS and meaning review

Base: published v229 HTML from main HEAD `5354a748fe8ae147ae81f54f82da07e00ccccddc`; HTML SHA-256 `e5e298e9f5efcf45c7cfd1fe83ab9ce5a19dcde13759482d54e3b8313bd92dab`.

## Review state

- Manual author review: 12/12 cards and 24/24 exact example contexts.
- POS-map changes scoped to 12 entries; 11 new context-specific meaning-quiz keys cover 22 contexts; ID3363's two existing reviewed contexts are retained.
- Static preflight: exact example binding and distinct-option checks pass; maximum correct/distractor length ratio is 1.4667 against a 1.5 limit.
- Source review: `source-review.md`; ID3636 retains an explicitly lower-confidence secondary-source note.
- v153 pilot credit: zero; this scope is outside the documented pilot IDs 121–320.

## Technical status — NOT ACCEPTED YET

The push/PR verification attempt has not returned an observable workflow run or commit status. Do not infer a CI or Chromium pass, do not apply registry credit, and do not publish v230 to main until a reproducible deterministic build, pool-impact calculation and browser verification are evidenced.

The work branch is intentionally diverged from main. Do not merge it wholesale. Once the candidate is verified, transfer only exact verified blobs and evidence to main after rechecking the main HEAD.

Independent linguistic acceptance, Android/Windows device tests and provenance/legal acceptance remain separate.
