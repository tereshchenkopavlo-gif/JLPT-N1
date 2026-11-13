# v204 C10 author-review checkpoint

Base: published v203 at main commit `7a5bcfec47231c5501b98dbd16a77b2d97730b8b`, HTML SHA-256 `81b4e4fbda3be91325493c95c3c28324deac52f69cc230f16bd630db20929339`.

Scope: twelve pending cards 1198, 1202, 1214, 1218, 1236, 1237, 1239, 1241, 1246, 1248, 1249 and 1251. All twelve have v153 pilot evidence. Eleven cards have thirteen exact field updates; ID1202 is reviewed without change. The single Japanese example edit is ID1237 example index 1.

Protected: 3914 vocabulary records and IDs, 130 grammar records, 859 comparison pairs, POS map, quiz targets/payloads, learning engine and progress storage. Baseline register: all 3914/265/1668; vocabulary 3345/264/305. Target after v204: all 3915/276/1656; vocabulary 3346/275/293. Author credit target: 3621/3914.

古来 remains 名詞; adverbial use is standard and no POS/quiz-candidate change is made. 合席 remains the headword; usage already notes 相席 as the more common spelling, supported by Kotobank.

The workflow must reproduce v204 from exact published v203, validate thirteen preimages and the one Japanese-example postimage, preserve the no-change review for ID1202, run Chromium at 360/412/1280 with storage round-trip, then publish only exact verified artifacts under a strict main-HEAD guard. The work branch must not be merged.
