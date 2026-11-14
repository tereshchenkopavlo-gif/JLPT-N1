# v229 C11 POS-map review

1. `python3 completion/v229-work/prepare.py` reproduces the candidate from the exact published v228 HTML SHA.
2. `node --check completion/v229-work/browser.cjs`.
3. Install Playwright/Chromium as in `.github/workflows/v229-c11-pos-map.yml`.
4. `node completion/v229-work/browser.cjs` compares before/after POS, reading/cloze pools, meaning-option structure, rendered cards, progress-storage round-trip/restore and 360/412/1280 px layout.
5. Manual author review is recorded in `semantic-review.json` (24/24 contexts; independent_review=false). Workflow 43621856689 passed; `finalize.py` updated the review register to 3897/3914 author credit. Published to main in commit `650379afed99e00da1b868720a937d506de8302a`; exact HTML SHA-256 `e5e298e9f5efcf45c7cfd1fe83ab9ce5a19dcde13759482d54e3b8313bd92dab` and blob `1c90476d78ae832ccecbcdfbfb93cc83b99474eb` verified.
