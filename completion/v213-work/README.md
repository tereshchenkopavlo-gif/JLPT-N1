# v213 C10 author-review checkpoint

Base: published v212 at main commit 8c61eeb6cce2e8455467f45ad4f80a660d30e597, HTML SHA-256 a0dd07bc265bb549b648ec3dcc02fa836f5ee59449a92cbdcc53c682bdc28bb5.

Scope: twelve pending cards 1528, 1529, 1539, 1541, 1542, 1548, 1551, 1554, 1558, 1625, 1628, 1631 with individual v153 pilot evidence. Eleven cards receive thirteen exact field updates; three Japanese definitions are refined. One POS correction for ID1631 is deferred: adding ナ形 would reduce automatic reading candidates from 60 to 2 and cloze candidates from 2269 to 65 under the current exact-POS matching. POS map and learning logic remain unchanged.

Protected: 3914 vocabulary records and IDs, 130 grammar records, 859 comparison pairs, POS map, quiz targets/payloads, learning engine and progress storage. Baseline register: all 3916/369/1562; vocabulary 3347/367/200. Target after v213: all 3916/380/1551; vocabulary 3347/378/189. Author credit target: 3725/3914.

The workflow must reproduce v213 from exact published v212, validate thirteen field preimages and the exact eleven-card change set, preserve all protected data, run Chromium at 360/412/1280 with storage round-trip, then publish only exact verified artifacts under a strict main-HEAD guard. The work branch must not be merged.
