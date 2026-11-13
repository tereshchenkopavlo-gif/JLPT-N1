# v182 C11 reading-pool review

Run from repository root:

1. `python3 completion/v182-work/apply.py` — reproduces the content-only v182 candidate from the exact published v181 SHA.
2. `node --check completion/v182-work/browser.cjs`
3. Install Playwright/Chromium as in `.github/workflows/v182-c11-reading.yml` and run `node completion/v182-work/browser.cjs`.
4. `python3 completion/v182-work/finalize.py` — writes the 23-pool review, field-level acceptance, registry and audit.

The workflow is scoped to the named work branch. It does not publish to `main`; publication is a separate guarded step after review of the resulting evidence.
