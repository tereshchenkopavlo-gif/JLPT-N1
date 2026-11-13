# v194 C10 author-review checkpoint

Base: published v193 at main commit `79254c60d84f8dba5d58979b10c44b33aa575a0c`, HTML SHA-256 `e5876cbc6e1799bf5aa8e4d4c6a07ee6cde1a14ffbdf5605cc1359d8623141c8`.

Scope: IDs 883, 884, 885, 888, 890, 893, 894, 900, 901, 903, 905, 906. The v153 pilot rows were reread and used as hypotheses.

Author decisions: all 12 cards fixed_rechecked; 13 exact text-field updates plus one POS-map update for ID903. The existing 代名詞 filter is reused; no UI or learning-engine change is made. No Japanese example, ID, quiz payload/target, comparison pair or progress-storage code is changed.

The workflow must reproduce v194 from the exact v193 base, validate all 13 text preimages and the ID903 POS preimage, update the register, run Chromium at 360/412/1280 including 代名詞/名詞 filter checks and storage round-trip, then publish only exact verified paths under a strict main-HEAD guard. The work branch must not be merged.
