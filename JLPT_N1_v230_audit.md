# JLPT N1 v230 — C11 POS and meaning-quiz audit

## Decision

12 previously blocked cards were manually reviewed for POS/sense alignment and 24 exact example contexts. All 12 are fixed_rechecked after POS-map reconciliation and context-specific meaning overrides. This is an author review, not independent acceptance.

- 12 cards: 3363, 3375, 3417, 3441, 3444, 3525, 3561, 3565, 3569, 3594, 3636, 3646.
- 12 POS-map updates.
- 11 new reviewed meaning-quiz keys, covering 22 contexts.
- ID3363's two existing v141 contexts were retained and rechecked for binding and answer-length balance; they were not counted as new override creation.
- 24/24 browser override checks, three unique distractors, correct-answer exclusion, and max/min length ratio <=1.5.
- No changes to vocabulary records, grammar, examples, translations, lexical pairs, reading overrides, target tables, or storage keys.
- The reviewed-cloze gate is present but inert in v230: it can activate only for an exact byExample payload. All 24 scoped cloze contexts were manually reviewed; none received a payload because the sentences did not prove a unique target against three high-quality distractors.
- The 22 contexts newly suppressed by reviewed meaning keys are therefore documented rejections, not silently lost exercises. A whole-bank Chromium comparison confirms zero cloze-behavior changes outside those 22 contexts.
- No v153 pilot credit: all IDs are outside the documented 121–320 pilot range.

## Card-level decisions

| ID | Entry | POS map after | Context handling |
|---:|---|---|---|
| 3363 | 相当 | 副詞・ナ形 | Existing global degree override retained; both examples checked |
| 3375 | 当面 | 名詞・副詞 | Separate byExample payloads for 当面の課題 and 当面は |
| 3417 | だぶだぶ | 副詞・ナ形 | Clothing looseness; both examples checked |
| 3441 | とろとろ | 副詞・ナ形 | Soft/melted food vs shallow dozing separated |
| 3444 | どろどろ | 副詞・ナ形 | Muddy material vs tangled human relationships separated |
| 3525 | オートマチック | 名詞・ナ形 | Automatic-transmission car vs automatic operation separated |
| 3561 | ジャンボ | 名詞・ナ形 | Extra-large size in both contexts |
| 3565 | タイムリー | ナ形 | Well-timed contexts |
| 3569 | コマーシャル | 名詞・ナ形 | Broadcast advertisement contexts |
| 3594 | ストレート | 名詞・ナ形 | Direct/forthright expression contexts |
| 3636 | プライベート | 名詞・ナ形 | Private/personal life; source confidence limitation documented |
| 3646 | モダン | 名詞・ナ形 | Contemporary style, distinct from merely new or briefly fashionable |

## Technical verification

Chromium workflow checks 3914 vocabulary records, 130 grammar constructions, 859 lexical pairs, unique stable IDs, protected data blocks, exact example-key binding, 12 rendered cards, POS labels, all 24 reviewed quiz contexts, option uniqueness/length balance, reading/cloze pool impact, responsive widths 360/412/1280, storage round-trip/restore, and zero page errors. Linux Chromium is not a physical Android/Windows test.

## Registry

Author credit after this batch: 3909/3914. Remaining blocked: 3652, 3654, 3677, 3679. ID1510 remains pending safety hold and was not assessed. Independent linguistic acceptance, physical Android/Windows acceptance, and provenance/legal review remain open.
