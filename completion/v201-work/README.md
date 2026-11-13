# v201 C10 author-review checkpoint

Base: published v200 at main commit `9d6d46dc87cabbfd495022d6f55b1dafe9581c48`, HTML SHA-256 `d3563bf1f9601d8b87b5508e979116dfde07a8135cd46311d0626c8a1aac7d1a`.

Scope: IDs 1097, 1100, 1102 and 1105. All four were pending and have individual v153 pilot evidence in `completion/v153-cards-1081-1180.tsv`. Eight other IDs from the wider selection were already reviewed and are excluded.

Author decisions: all four fixed_rechecked, four exact field updates in four cards. No Japanese example, POS map, ID, quiz payload/target, comparison pair, learning engine or progress-storage code is changed.

The workflow must reproduce v201 from the exact v200 base, validate all four field preimages and the review register, run Chromium at 360/412/1280 with storage round-trip, then publish only exact verified release artifacts under a strict main-HEAD guard. The work branch must not be merged.
