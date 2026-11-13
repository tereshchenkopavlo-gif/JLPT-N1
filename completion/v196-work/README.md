# v196 C10 author-review checkpoint

Base: published v195 at main commit `8450aebd945d424e4726092942f2e176be0d8d0a`, HTML SHA-256 `b3a8a841cf573596b3e50eed3230e038833cbd5147a1fba4939fca80eb460ff3`.

Scope: IDs 943, 944, 949, 951, 952, 956, 960, 961, 963, 965, 968, 969. The v153 pilot rows were reread and used as hypotheses.

Author decisions: all 12 cards fixed_rechecked; 16 exact field updates in 12 cards. No Japanese example, POS map, ID, quiz payload/target, comparison pair, learning engine or progress-storage code is changed.

The workflow must reproduce v196 from the exact v195 base, validate all 16 field preimages and the review register, run Chromium at 360/412/1280 with storage round-trip, then publish only exact verified release artifacts under a strict main-HEAD guard. The work branch must not be merged.
