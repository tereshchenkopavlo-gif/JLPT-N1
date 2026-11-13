# v195 C10 author-review checkpoint

Base: published v194 at main commit `cb65740b4f8720c02f952811bae38844e36a2419`, HTML SHA-256 `0933cf494010d2c4a8ff3f200d35882d3773f59395193b68ea48604b8a8bfba9`.

Scope: IDs 911, 914, 915, 920, 922, 927, 928, 932, 933, 934, 936, 941. The v153 pilot rows were reread and used as hypotheses.

Author decisions: 11 fixed_rechecked and one reviewed without change (ID911). There are 11 exact field updates in 11 cards. The Japanese examples, POS map, IDs, quiz payloads/targets, comparison pairs, learning engine and progress-storage code remain unchanged.

The workflow must reproduce v195 from the exact v194 base, validate all 11 field preimages and the review register, run Chromium at 360/412/1280 with storage round-trip, then publish only exact verified release artifacts under a strict main-HEAD guard. The work branch must not be merged.
