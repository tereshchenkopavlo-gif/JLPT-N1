# v200 C10 author-review checkpoint

Base: published v199 at main commit `4ec8f84ad32bb2b17c1081942ae2fb14d96c6b67`, HTML SHA-256 `c81d7624557b2193bd6bc7939c93e200b054323f4b845f19921d70924a9ab280`.

Scope: IDs 1075, 1077, 1080, 1081, 1083, 1085, 1087, 1088, 1090, 1092, 1094, 1095. All 12 were pending in the register. Pilot v153 evidence is available for 1075, 1077 and 1080; no matching pilot file was found for the other nine.

Author decisions: two fixed_rechecked and ten reviewed without change; three exact field updates in two cards. No Japanese example, POS map, ID, quiz payload/target, comparison pair, learning engine or progress-storage code is changed.

The workflow must reproduce v200 from the exact v199 base, validate all three field preimages and the review register, run Chromium at 360/412/1280 with storage round-trip, then publish only exact verified release artifacts under a strict main-HEAD guard. The work branch must not be merged.
