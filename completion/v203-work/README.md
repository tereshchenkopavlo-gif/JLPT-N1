# v203 C10 author-review checkpoint

Base: published v202 at main commit `8a878ed079adb567915d42bdd126a0fa337c8abe`, HTML SHA-256 `39aa398f92db161d4c396038d588872b2fabb9fc9c45713a5e530f5a03bae14c`.

Scope: eleven pending cards 1153, 1157, 1158, 1169, 1173, 1175, 1178, 1182, 1194, 1195 and 1196. All eleven have v153 pilot evidence and are assigned fixed_rechecked after the deterministic patch. Fourteen exact field updates are expected, including one narrowly scoped Japanese example correction for ID1178.

A separate item in the selected interval is deferred under safety policy and is not included in this checkpoint. It remains pending; no content is reproduced.

Protected: 3914 vocabulary records and IDs, 130 grammar records, 859 comparison pairs, POS map, quiz targets/payloads, learning engine and progress storage. Baseline register: all 3914/254/1679; vocabulary 3345/253/316. Target after v203: all 3914/265/1668; vocabulary 3345/264/305. Author credit target: 3609/3914.

The workflow must reproduce v203 from exact published v202, validate all fourteen preimages and the one Japanese-example postimage, run Chromium at 360/412/1280 with storage round-trip, then publish only exact verified artifacts under a strict main-HEAD guard. The work branch must not be merged.
