# v230 C11 preaudit — 12 remaining POS/quiz blockers

**Base:** v229, main commit `1c3b14522784509c22069dda9fbb08f418475d99`, HTML SHA-256 `e5e298e9f5efcf45c7cfd1fe83ab9ce5a19dcde13759482d54e3b8313bd92dab`.

Scope: `3363, 3375, 3417, 3441, 3444, 3525, 3561, 3565, 3569, 3594, 3636, 3646`.

No card data, POS-map, quiz payloads or review-register rows were changed in this preaudit. No author credit is applied yet.

## Initial dictionary/POS signals

- **3363 相当** — current POS-map 副詞; Digital Daijisen lists 名・形動 and 副. Current examples mix 相当な時間 (形動/nominal modifier) and 相当疲れる (副詞). Keep the card's selected "considerable degree" sense separate from the separate equivalence/対応 sense.
- **3375 当面** — current POS-map 副詞; Digital Daijisen lists 名詞 and says it is also used adverbially. 当面の課題 is nominal; 当面は is adverbial. Likely add 名詞 only if the card's sense and quiz scope support it.
- **3417 だぶだぶ** — current POS-map 副詞; Digital Daijisen lists 副詞 and 形動, and Nikkoku also records a noun sense for liquid. This card is specifically about loose clothing; do not import the unrelated liquid noun sense.
- **3441 とろとろ** — current POS-map 副詞; Digital Daijisen lists 副詞 and 形動. The two examples represent soft/viscous texture and light dozing; check whether both are represented by the card's selected sense.
- **3444 どろどろ** — current POS-map 副詞; Digital Daijisen explicitly lists 副詞・形動. Current examples include どろどろにぬかるむ and どろどろした人間関係.
- **3525 オートマチック** — current POS-map 名詞; Digital Daijisen lists 名詞 and 形動. The examples use オートマチックの車 and オートマチックに行われる; the latter is adjectival/adverbial.
- **3561 ジャンボ** — current POS-map 名詞; Digital Daijisen lists 名・形動. The card examples are nominal compounds, while usage also records ジャンボなN.
- **3565 タイムリー** — current POS-map 名詞; Digital Daijisen lists 形動 for "timely" and a noun abbreviation for タイムリーヒット. The card's examples use タイムリーな情報 / タイムリーだった, so the primary sense is adjectival.
- **3569 コマーシャル** — current POS-map 名詞; Digital Daijisen gives a noun advertising sense and a productive commercial/promotional modifier; Nikkoku records 形動. Review whether the current card includes the adjectival use or only the advertising noun.
- **3594 ストレート** — current POS-map 名詞; Digital Daijisen lists 名・形動. The current examples use ストレートに伝える and ストレートな表現.
- **3636 プライベート** — current POS-map 名詞; current examples are nominal, but usage also gives プライベートなN. Dictionary confirmation is still pending; do not infer a POS change from the usage note alone.
- **3646 モダン** — current POS-map 名詞; both current examples use モダンなN. Dictionary confirmation and quiz/pool impact are pending.

## Questions for the full C11 pass

1. Which POS labels belong to the exact sense represented by each card, rather than to unrelated senses in a broad dictionary entry?
2. Do category labels, POS-map labels and actual inflected examples agree?
3. Do all meaning questions have one defensible answer and three plausible, comparable distractors?
4. Do visible readings, word length, POS names or usage notes reveal the answer?
5. What happens to reading/cloze eligibility if POS-map is corrected?
6. Are exact-sentence byExample payloads required when the same word has multiple meanings?

The source review is preliminary, not a final decision. No v153 pilot credit applies because every ID is above 320.
