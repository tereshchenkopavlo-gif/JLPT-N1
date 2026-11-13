# v183 — C10 author review, IDs 454–483

Date: 13 November 2026. Exact baseline: published v182, SHA-256 `53f8dd4153cab99850d9291dbd1343a58908b2dadb877f0c3a9f223ef6e54031`. Scope: the first 12 pending vocabulary rows in `completion/review-register.csv`; IDs 454, 455, 458, 459, 461, 464, 466, 470, 472, 477, 479, 483.

## Decisions

| ID | Word | Decision | Rationale |
|---:|---|---|---|
| 454 | 向く | fixed_rechecked | Corrected the Ukrainian POS/meaning translation: the old phrase mixed incompatible cases (“для справи або людині”). The revised wording separates “be suitable for a person” and “be suitable for work/a task”. Both examples remain valid. |
| 455 | 広まる | reviewed | Intransitive spreading is consistently represented in the definition, both examples and the distinction from 広める / 普及する. No change. |
| 458 | 合わす | reviewed | Rechecked the transitive 五段 forms, the colloquial/less neutral register note, and both examples. The existing Ukrainian translation of 声を合わす is acceptable in context; no new change. Historical audit log records an earlier fixed pass, but no unsupported new fixed credit is inferred from that label alone. |
| 459 | 込める | reviewed | Both “put feelings into an action” examples and the Ukrainian translations remain semantically aligned. No change. |
| 461 | 仕上げる | reviewed | Transitive 一段 usage, final-completion meaning and both work/product examples are aligned. No change. |
| 464 | 謝る | reviewed | Apology is distinguished from 誤る; particles and examples support admitting fault and apologizing. No change. |
| 466 | 従う | fixed_rechecked | Improved the second Ukrainian example translation to express a flexible adjustment as circumstances change, rather than the awkward “змін ситуації спосіб реагування”. |
| 470 | 招く | reviewed | The two senses (invite a person / bring about a result) are separated by the examples. “Often unfavorable” is a tendency, not an absolute restriction. No change. |
| 472 | 触れる | fixed_rechecked | Rephrased the second example translation. “Знайомство з твором дало нове відкриття” was an unnatural calque; the revision expresses encountering a work and discovering something new. |
| 477 | 親しむ | fixed_rechecked | Refined the Ukrainian head translation to avoid reducing 親しむ to “get used to”; the dictionary senses include close association and repeated contact that makes something familiar. Improved the nature example translation accordingly. |
| 479 | 震わせる | fixed_rechecked | Clarified the transitive Ukrainian meaning (cause something to tremble / deeply move someone) and replaced the awkward shoulder construction in the first example translation. |
| 483 | 生じる | reviewed | The current note correctly distinguishes the usual intransitive use from attested transitive use; both examples are natural and the translations are accurate. No change. |

## Source checks

- Kotobank / Digital Daijisen, 親しむ: https://kotobank.jp/word/%E8%A6%AA%E3%81%97%E3%82%80-520480 — close relations with people; repeated contact with things such as reading and nature.
- Kotobank / Digital Daijisen, 触れる: https://kotobank.jp/word/%E8%A7%A6%E3%82%8C%E3%82%8B-622378 — light contact, mentioning a topic, and encountering/coming into contact with an event or thing.
- Kotobank / 精選版 日本国語大辞典, 生じる: https://kotobank.jp/word/%E7%94%9F%E3%81%98%E3%82%8B-532096 — records both intransitive and transitive use; the card's qualification is retained.
- Kotobank / Digital Daijisen, 招く: https://kotobank.jp/word/%E6%8B%9B%E3%81%8F-451667 — inviting/bringing someone and causing an outcome, often an undesirable one, while also recording positive collocations.
- Cambridge Japanese–English, 震わせる: https://dictionary.cambridge.org/ja/dictionary/japanese-english/%E9%9C%87%E3%82%8F%E3%81%9B%E3%82%8B — identifies it as transitive and illustrates a voice trembling with anger.
- Kotobank / Digital Daijisen, 合わせる: https://kotobank.jp/word/%E5%90%88%E3%81%9B%E3%82%8B-428938 — supports the core “bring into agreement / join together” meaning relevant to 合わす; the card's specific 合わす examples were separately re-read.

## Change boundary

Only seven Ukrainian fields across five cards were edited: ID454, 466, 472, 477, 479. No Japanese example, headword, reading, POS tag, synonym relation, quiz target, reading/meaning override, grammar record, pair, ID, application function, or progress-storage code was changed. The deterministic preparation verifies an exact rollback to v182.

This is author linguistic review plus technical regression, not independent expert acceptance, physical-device acceptance, or legal/provenance clearance.
