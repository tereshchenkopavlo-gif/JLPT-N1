# v182 pre-audit notes

## Why v180 is superseded

The v180 diagnostic simulated ID255 直接 and ID327 浮気 as both 名詞 + ナ形. That assumption was incorrect for 直接. The NINJAL dictionary entry distinguishes 直接 (名・副) from 直接的 (形動). The current card examples also distinguish 直接に/直接会う and 直接の原因 from 直接的な影響. Therefore v182 must simulate ID255 as 名詞 + 副詞 and ID327 as 名詞 + ナ形.

## Full-card recheck scope

ID255 and ID327 are pending in the vocabulary register. Their definitions, readings, Japanese examples and Ukrainian translations have been inspected against the current v181 HTML. No linguistic defect in those fields was identified in this pre-review; the known open issue is POS metadata and the dependent reading quiz. Do not award full-card credit until the corrected POS and reading pool are verified and the cards are rechecked after the patch.

ID1819 内訳 and ID359 本気 are already author-reviewed; their reading-pool behavior is included only to preserve quiz eligibility, not to change their full-card credit.

## Proposed options

The proposed overrides use existing, verified database readings and have three distinct wrong options each:
- ID255 直接 / ちょくせつ: ちょうせつ, ちょうせい, ちくせき.
- ID327 浮気 / うわき: いしき, いせき, うつわ. The historical reading ふき is excluded.
- ID1819 内訳 / うちわけ: うちがわ, うつわ, うわき.

These are proposals only. The browser diagnostic must recompute all 3914 reading pools with the corrected POS, verify the three overrides, and prove that no previously eligible pool falls below the three-distractor threshold. If any additional pool loses eligibility, stop before applying POS changes and design a reviewed override for that target.

## Guardrails

No HTML data, POS, reading override, review-register row, user progress, learning code or Git history is changed by the diagnostic. It records a candidate only. Author acceptance and technical regression remain separate; independent acceptance is still outstanding.
