# v199 C10 author-review checkpoint

Base: published v198 at main commit `d88e12379756dc01a05a44454c15475f9136930a`, HTML SHA-256 `32c0bf74d083db74576d53a249ec1858352f20efcea9a72dd3c80daf3a17a39c`.

Scope: IDs 1042, 1043, 1044, 1046, 1048, 1061, 1063, 1066, 1067, 1072, 1073, 1074. All 12 were pending in the register and have v153 pilot evidence in `completion/v153-cards-981-1080.tsv`.

Author decisions: all 12 fixed_rechecked, 15 exact field updates across 12 cards. No Japanese example, POS map, ID, quiz payload/target, comparison pair, learning engine or progress-storage code is changed.

The workflow must reproduce v199 from the exact v198 base, validate all 15 field preimages and the review register, run Chromium at 360/412/1280 with storage round-trip, then publish only exact verified release artifacts under a strict main-HEAD guard. Usage annotations are validated directly from the stored card data; the current card-detail view does not render that field, so it is not asserted as visible UI text. The work branch must not be merged.
