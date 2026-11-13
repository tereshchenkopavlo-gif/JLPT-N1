# v197 C10 author-review checkpoint

Base: published v196 at main commit `895b72a7dff52ac30deec0e882cbb1e2d9c6268c`, HTML SHA-256 `0bef35afbc589b4b57312e40a56c87ba3512f504071070e820849529510c7fe5`.

Scope: IDs 973, 974, 978, 986, 989, 990, 991, 993, 995, 1004, 1008, 1013. The v153 pilot rows for 973, 974 and 978 were reread; no matching v153 file was found for the remaining nine cards.

Author decisions: five fixed_rechecked and seven reviewed without change. There are five exact field updates in five cards. No Japanese example, POS map, ID, quiz payload/target, comparison pair, learning engine or progress-storage code is changed.

The workflow must reproduce v197 from the exact v196 base, validate all five field preimages and the review register, run Chromium at 360/412/1280 with storage round-trip, then publish only exact verified release artifacts under a strict main-HEAD guard. The work branch must not be merged.
