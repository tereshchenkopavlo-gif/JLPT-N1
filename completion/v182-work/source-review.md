# v182 — C11 reading-pool and POS source review

**Date:** 13 November 2026. **Baseline:** published v181, SHA-256 `32c6f482db1e98dd1f98deb0197324a037fbd1a1bae8d5dd4b4f7123f126da7f`. **Scope:** the 23 reading pools reproduced by `completion/v180-c11-diagnostics.json` after the proposed POS corrections for ID255 and ID327.

## POS decisions

- **ID255 直接 — add `ナ形` alongside `名詞`.** Shogakukan's Digital Daijisen on Kotobank labels 直接 `[名・形動]` and gives `相手国政府への直接な（の）交渉`; it also notes adverbial use. The card's existing examples and core meaning remain valid. Its usage note is expanded to distinguish `直接な交渉` (formal attributive use) from the more usual `直接の` / `直接的な` patterns. Source: https://kotobank.jp/word/%E7%9B%B4%E6%8E%A5-569297
- **ID327 浮気 — add `ナ形` alongside `名詞`.** Digital Daijisen labels 浮気 `[名・形動]` and gives `浮気な性分` and `浮気な人`; the card already uses `浮気な人` in its usage note. The note is made explicit about noun, na-adjectival and `する` use. Source: https://kotobank.jp/word/%E6%B5%AE%E6%B0%97-442377
- **ID1819 内訳** remains a noun. Kotobank gives the reading `うちわけ` and the itemized-breakdown sense. Source: https://kotobank.jp/word/%E5%86%85%E8%A8%B3-440704
- **ID359 本気** remains `名詞・ナ形`. The new `うわき` distractor is a genuine noun reading of 浮気, not a fabricated kana string. Source: https://kotobank.jp/word/%E6%B5%AE%E6%B0%97-442377

## Manual reading overrides

The existing `REVIEWED_READING_OPTIONS` field is used; no quiz function or learning mechanism is changed.

- **ID255 直接 / ちょくせつ:** `ちょうせつ` (ID1724 調節), `ちょうせい` (ID1723 調整), `がくせつ` (ID950 学説). These are all four-mora readings and visually/phonologically close to the target. Dictionary checks: 調節 https://kotobank.jp/word/%E8%AA%BF%E7%AF%80-97980 ; 調整 https://kotobank.jp/word/%E8%AA%BF%E6%95%B4-568677 ; 学説 https://kotobank.jp/word/%E5%AD%A6%E8%AA%AC-460446 .
- **ID327 浮気 / うわき:** `いしき` (ID4 意識), `いせき` (ID832 遺跡), `うつわ` (ID709 器). All are three mora and are existing vocabulary readings. Dictionary checks: 意識 https://kotobank.jp/word/%E6%84%8F%E8%AD%98-30519 ; 遺跡 https://kotobank.jp/word/%E9%81%BA%E8%B7%A1-166323 ; 器 https://kotobank.jp/word/%E5%99%A8-440939 .
- **ID1819 内訳 / うちわけ:** `うちがわ` (ID285 内側), `うつわ` (ID709 器), `うわき` (ID327 浮気). These are existing noun readings, all three/four mora, and all begin with `う`; `浮気` remains a noun even though its POS set also includes `ナ形`. Dictionary checks: 内側 https://kotobank.jp/word/%E5%86%85%E5%81%B4-440313 ; 器 https://kotobank.jp/word/%E5%99%A8-440939 ; 浮気 https://kotobank.jp/word/%E6%B5%AE%E6%B0%97-442377 .

## Review of all 23 affected pools

The v180 diagnostic reproduces the current `quizReadingOptions` function with the two proposed POS additions. Twenty pools retain at least three automatic distractors; ID359 gains a third (`うわき`); ID255, ID327 and ID1819 require the three explicit, reviewed overrides above. The retained automatic pools were checked for unique kana options, exclusion of the correct reading, the existing kanji-frame match, exact POS-set match, length difference no greater than one mora, and edit distance 1–2. No automatic option set is accepted solely because a structural count passes; the 23 individual decisions and candidate IDs are recorded in `completion/v182-reading-pool-review.tsv`.

## Cloze and data boundaries

The existing cloze algorithm is unchanged. Exact candidate counts for the four affected targets are recorded in `v182-prepare-results.json`; all remain comfortably above the minimum of three. Both examples for ID255 and ID327 retain literal cloze eligibility. The three manual reading overrides and two POS/usage field corrections do **not** grant full-card credit. No vocabulary, grammar, lexical-pair, ID, example, user-progress or storage record is removed or migrated. This is author review, not independent acceptance.


## NINJAL cross-check and app-specific POS decision

An additional authoritative source was checked after the initial Daijisen review:

- NINJAL CHOKUSETSU: https://mmsrv.ninjal.ac.jp/kamus/data/item315.html — labels 直接 as 名・副 and distinguishes 直接的 as 形動.
- Shogakukan Digital Daijisen via Kotobank: https://kotobank.jp/word/%E7%9B%B4%E6%8E%A5-569297 — labels 直接 as 名・形動, gives 直接な（の）交渉, and notes adverbial use.

These are differing but valid dictionary classifications, not evidence that one source is simply wrong. The app keeps the explicit 名詞 + ナ形 tag because Daijisen supplies a direct attributive example and the existing usage note also records adverbial use. A separate browser simulation tests adding 副詞 as a third tag. The browser measured 64 cloze candidates with the selected 名詞 + ナ形 set and only 2 if 副詞 is added as a third POS tag. The hypothetical third tag changed no reading pools, but it would reduce cloze candidates below the minimum three, so it is not adopted in this release; adverbial use remains documented in the usage note. This is an app-specific compatibility decision, not a universal claim that 直接 cannot be adverbial.

The v182 browser regression records the exact current and hypothetical cloze counts and the reading-pool impact of the hypothetical third tag. No learning algorithm is changed.
