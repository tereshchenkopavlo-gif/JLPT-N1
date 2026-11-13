# v207 C10 author-review checkpoint

Base: published v206 at main commit `bc44e36f9f3c3e3db3f9a8a03f2c7b9d2a0b8c1e`, HTML SHA-256 `c2ec95102d848b728d352393863fbb4604b29dec864950529cd93f7a5b4c56fd`.

Scope: twelve pending cards 1351, 1352, 1353, 1354, 1358, 1359, 1362, 1363, 1370, 1372, 1373 and 1375. All twelve have v153 pilot evidence. Sixteen exact field updates are proposed in eleven cards; ID1354 is reviewed without change. No Japanese examples, POS values, quiz targets or learning mechanisms change.

Protected: 3914 vocabulary records and IDs, 130 grammar records, 859 comparison pairs, POS map, quiz targets/payloads, learning engine and progress storage. Baseline register: all 3915/300/1632; vocabulary 3346/299/269. Target after v207: all 3916/311/1620; vocabulary 3347/310/257. Author credit target: 3657/3914.

The workflow must reproduce v207 from exact published v206, validate sixteen preimages and the exact eleven-card change set, preserve the no-change review for ID1354 and all protected data, run Chromium at 360/412/1280 with storage round-trip, then publish only exact verified artifacts under a strict main-HEAD guard. The work branch must not be merged.
