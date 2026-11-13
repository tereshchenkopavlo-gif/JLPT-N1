# v198 C10 author-review checkpoint

Base: published v197 at main commit `65ab0e9a5ee81bc0d8dd6cc37be70d3cbccbf715`, HTML SHA-256 `d158eb7d7a619718e982ad4117f603f208339178d47ec0417c2adeab238c1620`.

Corrected scope: only IDs 1015, 1016, 1026 and 1027 were pending. The full v153 pilot file confirms that IDs1018, 1021, 1023, 1024, 1025, 1030, 1031 and 1034 were already reviewed; they are excluded and not credited again.

Author decisions: four fixed_rechecked, four exact field updates. No Japanese example, POS map, ID, quiz payload/target, comparison pair, learning engine or progress-storage code is changed.

The first workflow attempt correctly stopped at the register guard when it encountered an already-reviewed ID. The scope was corrected to four pending cards; the corrected workflow passed and v198 was published to main in commit `9c12c0736835a259bf723c161e02be12d23d31a3` (SHA-256 `32c0bf74d083db74576d53a249ec1858352f20efcea9a72dd3c80daf3a17a39c`, 6,945,040 bytes). PR #23 was closed without merging; the work branch and evidence are preserved. The workflow must reproduce v198 from the exact v197 base, validate four field preimages and the review register, run Chromium at 360/412/1280 with storage round-trip, then publish only exact verified release artifacts under a strict main-HEAD guard. The work branch must not be merged.
