# v229 C11 POS-map review

1. `python3 completion/v229-work/prepare.py` reproduces the candidate from the exact published v228 HTML SHA.
2. `node --check completion/v229-work/browser.cjs`.
3. Install Playwright/Chromium as in `.github/workflows/v229-c11-pos-map.yml`.
4. `node completion/v229-work/browser.cjs` compares before/after POS, reading/cloze pools, meaning-option structure, rendered cards, progress-storage round-trip/restore and 360/412/1280 px layout.
5. Review `meaning-quiz-diagnostics.json` manually before changing the review register or publishing. The workflow intentionally does not grant C11 credit or publish main.
