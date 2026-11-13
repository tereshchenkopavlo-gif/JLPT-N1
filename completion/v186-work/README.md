# v186 C10 author-review checkpoint — verification passed

Base: published v185, HTML SHA-256 `0cc48969700d238c27e7c3d4f18773ab31508257b0b11a544e5b15f83a178042`.

Scope: 565, 571, 572, 579, 586, 588, 590, 593, 595, 597, 599 and 609. The v153 pilot rows were used as hypotheses; every current field and both examples were reread.

Author decisions: 10 fixed/rechecked (565, 571, 572, 579, 586, 590, 593, 595, 597, 609); 2 remain pending for C11 POS/quiz review (588, 599). Ten exact field updates across ten cards. No Japanese example, POS map, quiz target, pair, learning algorithm or progress-storage code was changed.

Candidate SHA-256: `75387f14bb77bfcc9f5d0ec224e5f4e6e14ba3d51465b0f435117d4f3af4351b`. Candidate blob SHA: `e1a9f85ea4bc80461c7684fb06c7e933c5bb6f21`.

The guarded push workflow reproduces v186 from exact v185, validates the register and exact rollback, runs Chromium card-rendering/responsive/storage tests, and then copies only the verified release files to main under an exact main-HEAD guard. The bulk work branch is not merged. PR #9 remains a draft audit/test vehicle.
