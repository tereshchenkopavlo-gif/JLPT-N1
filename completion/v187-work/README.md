# v187 C10 author-review checkpoint

Base: published v186 at main commit `9a9e61a59cbddb5f9e51f896728b50f471137be7`, HTML SHA-256 `75387f14bb77bfcc9f5d0ec224e5f4e6e14ba3d51465b0f435117d4f3af4351b`.

Scope: IDs 615, 616, 618, 624, 629, 644, 651, 654, 663, 664, 672, 674. The v153 pilot files were reread and used as hypotheses.

Author decisions: 9 fixed_rechecked; ID624 reviewed without change; ID644 and ID663 remain pending for C11 POS/quiz impact. Thirteen exact field updates across ten cards. No Japanese example, POS map, quiz target, comparison pair, learning algorithm or progress-storage code is changed.

The workflow must reproduce the candidate from the exact v186 base, validate exact rollback and register, run Chromium at 360/412/1280 with storage round-trip, then publish only the exact verified paths under a strict main-HEAD guard. The work branch must not be merged.
