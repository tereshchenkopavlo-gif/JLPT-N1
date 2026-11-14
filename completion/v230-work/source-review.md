# v230 C11 — preliminary source review

All citations below are lexical evidence for POS and sense distinctions, not proof that the app must adopt every dictionary POS for every card.

| ID | Headword | Source and preliminary finding |
|---:|---|---|
| 3363 | 相当 | [Digital Daijisen via Kotobank](https://kotobank.jp/word/%E7%9B%B8%E5%BD%93-552955): 名・形動 and 副; card examples mix adjectival 相当な and adverbial 相当疲れる. |
| 3375 | 当面 | [Digital Daijisen via Kotobank](https://kotobank.jp/word/%E5%BD%93%E9%9D%A2-581512): 名詞（サ変） with adverbial use; examples 当面の課題 and 当面は are both licensed. |
| 3417 | だぶだぶ | [Digital Daijisen / Nikkoku via Kotobank](https://kotobank.jp/word/%E3%81%A0%E3%81%B6%E3%81%A0%E3%81%B6-562334): 副詞 and 形動; Nikkoku also has a liquid-related noun sense, outside this card's clothing meaning. |
| 3441 | とろとろ | [Digital Daijisen via Kotobank](https://kotobank.jp/word/%E3%81%A8%E3%82%8D%E3%81%A8%E3%82%8D-586493): 副詞 and 形動; texture and light-dozing uses are distinct sub-senses. |
| 3444 | どろどろ | [Digital Daijisen via Kotobank](https://kotobank.jp/word/%E3%81%A9%E3%82%8D%E3%81%A9%E3%82%8D-586494): 副詞・形動; viscous/muddy and tangled-emotional senses need separate context checks. |
| 3525 | オートマチック | [Digital Daijisen / Nikkoku via Kotobank](https://kotobank.jp/word/%E3%81%8A%E3%83%BC%E3%81%A8%E3%81%BE%E3%81%A1%E3%81%A4%E3%81%く-3208645): 名詞 and 形動. |
| 3561 | ジャンボ | [Digital Daijisen via Kotobank](https://kotobank.jp/word/%E3%81%98%E3%82%84%E3%82%93%E3%81%BC-3181782): 名・形動; giant object and giant-sized quality. |
| 3565 | タイムリー | [Digital Daijisen / Nikkoku via Kotobank](https://kotobank.jp/word/%E3%81%9F%E3%81%84%E3%82%80%E3%82%8A%E3%83%BC-3213612): 形動 for timely; 名詞 for abbreviation タイムリーヒット. |
| 3569 | コマーシャル | [Digital Daijisen / Nikkoku via Kotobank](https://kotobank.jp/word/%E3%81%93%E3%81%BE%E3%83%BC%E3%81%97%E3%82%84%E3%82%8B-3151926): noun advertising message and commercial/promotional modifier; Nikkoku records a 形動 use. |
| 3594 | ストレート | [Digital Daijisen / Nikkoku via Kotobank](https://kotobank.jp/word/%E3%81%99%E3%81%A8%E3%82%8C%E3%83%BC%E3%81%A8-3182233): 名・形動; direct/straight and other specialized noun senses. |
| 3636 | プライベート | [Kaikki/Wiktionary Japanese](https://kaikki.org/jawiktionary/%E6%97%A5%E6%9C%AC%E8%AA%9E/meaning/%E3%83%97/%E3%83%97%E3%83%A9/%E3%83%97%E3%83%A9%E3%82%A4%E3%83%99%E3%83%BC%E3%83%88.html) records both noun and 形容動詞 use; this is secondary evidence, so a primary dictionary check remains desirable. |
| 3646 | モダン | [JLearn](https://jlearn.net/dictionary/%E3%83%A2%E3%83%80%E3%83%B3) lists both na-adjective and noun; this is secondary evidence, so a primary dictionary check remains desirable. |

The next pass must open each dictionary entry directly and verify the precise sense and POS, not extrapolate from the broad entry. Any POS-map change must be followed by pool impact and exact-sentence quiz review.


## Diagnostic evidence added

- [v230 browser results](browser-results.json): 24 contexts; structure pass; two length-cue warnings, both ID3444; only ID3363 has existing reviewed overrides (2 contexts).
- [v230 meaning diagnostics](meaning-quiz-diagnostics.json) and [pool counts](pool-impact.json) preserve the automatic output for manual review.
- Kotobank confirms mixed POS for だぶだぶ, とろとろ, どろどろ, オートマチック, ジャンボ, タイムリー, コマーシャル, ストレート, 相当 and 当面. These broad entries must be narrowed to the exact card sense and actual example functions.
