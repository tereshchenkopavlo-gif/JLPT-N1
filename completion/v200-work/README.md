# v200 C10 author-review checkpoint

Base: published v199 at main commit `4ec8f84ad32bb2b17c1081942ae2fb14d96c6b67`, HTML SHA-256 `c81d7624557b2193bd6bc7939c93e200b054323f4b845f19921d70924a9ab280`.

Corrected scope: only IDs 1077, 1087, 1088, 1090, 1092, 1094 and 1095 were pending. All seven have v153 pilot evidence in the existing files `v153-cards-981-1080.tsv` and `v153-cards-1081-1180.tsv`. IDs1075, 1080, 1081, 1083 and 1085 were already reviewed and are excluded.

Author decisions: all seven fixed_rechecked, nine exact field updates. One Japanese example is corrected (ID1092, example 0); all other Japanese examples are preserved. No POS map, ID, quiz payload/target, comparison pair, learning engine or progress-storage code is changed.

The first draft scope included five already-reviewed cards; the register and pilot evidence were used to remove them before running any workflow. The corrected workflow passed: nine field preimages, protected data, exact rollback, registry update, seven-card Chromium render checks at 360/412/1280, storage round-trip and no page errors. One Japanese example (ID1092, example 0) was corrected; all other examples were preserved. v200 was published to main in commit `c8ff6ac3404a60d36a288be541e64da7c421534e` (SHA-256 `d3563bf1f9601d8b87b5508e979116dfde07a8135cd46311d0626c8a1aac7d1a`, 6,945,306 bytes). PR #25 was closed without merging; the work branch and evidence are preserved.
