# JLPT N1 v130 — release candidate audit (2026-10-31)

## Baseline and invariants
- Preserve v129 SHA-256 `5006238a087812b294c776b02951ebdb6eeb5fcfd6d950b41ec9f`; all 76 old reading texts and 185 old questions byte-identical in parsed structures.
- Vocab 3914 and grammar 130 unchanged; CSS, logic, and storage code unchanged except displayed version string.
- Add 16 medium + 8 long original passages with 56 new questions (224 options). Total 59 medium + 41 long = **100** passages; **241** questions.
- New QA confirms 24 distinct passages, unique IDs, 4 distinct nonblank options per question, keys in [0,3], Japanese evidence quotes present, and Ukrainian explanations/paragraph alignment.

## Confirmed live browser tests
- Three viewport sizes (360/412/1280): startup, navigation, nonempty vocab/grammar and a *real UI-created comparison entry* exported, imported and preserved after reload: https://github.com/tereshchenkopavlo-gif/JLPT-N1/actions/runs/41175376617
- Exercises on all viewport sizes: start teaching, skip to questions, answer 3 questions, reveal explanations, grade 3 learning items, and advance: https://github.com/tereshchenkopavlo-gif/JLPT-N1/actions/runs/41175782504
- Feedback: answer styles expose one correct answer; selected answer marked correct or wrong: https://github.com/tereshchenkopavlo-gif/JLPT-N1/actions/runs/41175920335
- Complete real session at 412px: 6 passages, 15 answers, 18 ratings, completion summary, back home, storage persists reload: https://github.com/tereshchenkopavlo-gif/JLPT-N1/actions/runs/41176110807

## Editorial review scope
- All 24 new passages and 56 new questions were read in an initial editorial pass, documented in `audit130/EDITORIAL_REVIEW_PART1.md` through `PART6.md`.
- Literal evidence checks are not a proof of semantically correct keys, natural Japanese, faithful Ukrainian translation, or well-balanced distractors. Independent linguistic verification of all 241 existing+new questions has **not** been completed.
- Browser tests verify app flow, **not** real-device compatibility or educational appropriateness of every generated question.

## Publication decision
**Candidate / NOT YET RELEASED.** The full HTML is generated into `release130/JLPT_N1_ukrainian_reading_v130.html` by `python3 audit130/build.py` in GitHub Actions; it is currently downloadable only as an unverified workflow artifact. Do not call v130 published in main until the versioned complete HTML, audit and README/PROJECT_STATUS.md have actually been committed and their Git blob digests verified.

## Immediate release tasks
1. Review and resolve editorial questions or document them explicitly.
2. Build and verify the standalone HTML from a known commit; calculate SHA-256 and Git blob SHA.
3. Publish entire HTML and audit in main as v130; update README and PROJECT_STATUS.md; verify on a fresh clone.
