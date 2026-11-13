# v203 — C10 source review

Base: published v202, main commit `8a878ed079adb567915d42bdd126a0fa337c8abe`, HTML SHA-256 `39aa398f92db161d4c396038d588872b2fabb9fc9c45713a5e530f5a03bae14c`, blob `6a8afed90faff63054e15a180d680957101851ef`.

All eleven reviewed cards were pending in the register. Individual v153 pilot notes and hashes were checked in:
- `completion/v153-cards-1081-1180.tsv` (1153, 1157, 1158, 1169, 1173, 1175, 1178)
- `completion/v153-cards-1181-1280.tsv` (1182, 1194, 1195, 1196)

## Source-specific notes

- **検挙 (1175):** National Police Agency, Police White Paper 2024, glossary §4(2), defines 検挙件数 as the number of cases the police have cleared/processed and explicitly includes cases solved in the current year even if first recorded earlier. The case-count and person-count examples are therefore translated as separate police statistical counts, not as arrests. The card's own Japanese definition also states that 検挙 does not necessarily involve arrest. The current direct source check supports the case-count definition; no claim about guilt is made.
- **検事 (1178):** the v153 pilot cites the Ministry of Justice for the office title and 司法試験. Direct reopening of that source returned HTTP 403 in this run; the pilot citation is retained, but is not marked as freshly revalidated here. The Japanese example correction is limited to the criminal-procedure term 被告人.
- **結核 (1158):** the v153 pilot cites WHO terminology for the disease. Direct reopening of that PDF returned HTTP 403 in this run; the pilot citation is retained, but is not marked as freshly revalidated here.
- **All cards:** no new external source was invented. The v153 note hash is retained as the provenance pointer for each card.

No quiz, comparison, POS or progress-storage behavior is changed. The single Japanese example edit is only the 被告 → 被告人 terminology correction in ID1178.
