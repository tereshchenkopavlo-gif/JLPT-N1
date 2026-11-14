# v231 source review — remaining C11 POS blockers

Retrieved 2026-11-15. This is author-source review, not independent acceptance.

## ID3652 — ユニーク

The card's selected sense is “unique / distinctive”; both supplied examples use the attributive form `ユニークな`. The secondary JLPTMatome entry classifies it as a na-adjective and lists `ユニークな`, `ユニークで`, and `ユニークに` forms: https://www.jlptmatome.com/lessons/n4/vocabulary/249-%E3%83%A6%E3%83%8B%E3%83%BC%E3%82%AF

Decision: change the app POS label from `名詞` to `ナ形` for this selected sense. Confidence: medium, because the retrieved source is secondary and a primary Kotobank entry was not located in this pass. Do not infer a separate noun sense from nominalized `ユニークさ`.

## ID3654 — ブロック

Digital Daijisen in Kotobank labels `ブロック` as `[名](スル)`; its listed senses include a city block/area and preventing an opponent's action in sports: https://kotobank.jp/word/%E3%81%B6%E3%82%8D%E3%81%A4%E3%81%8F-1588534

Decision: retain `名詞`. The app's existing POS convention keeps `名詞(スル)` entries under `名詞`; do not add a separate `動詞` label solely because one example uses `ブロックして`. Confidence: high.

## ID3677 — ルーズ

Digital Daijisen in Kotobank labels the selected “untidy / lax” sense `[形動]`. The same page's 精選版 日本国語大辞典 identifies that sense as `形容動詞ナリ活用` and lists a separate noun sense for an archery release: https://kotobank.jp/word/%E3%82%8B%E3%83%BC%E3%81%9A-3220632

Decision: change `名詞` to `ナ形`. Exclude the unrelated archery noun sense because the card's meaning and both examples concern lax time/money management. Confidence: high.

## ID3679 — ワンマン

Digital Daijisen in Kotobank describes a person who ignores others' opinions and acts as they wish; the 精選版 日本国語大辞典 labels the core sense `名詞 (形動)`. The page also describes the compound-forming element meaning “one / only one”: https://kotobank.jp/word/%E3%82%8F%E3%82%93%E3%81%BE%E3%82%93-2875500

The separate `ワンマン経営` entry defines management where the president does not listen to employees' opinions and acts autocratically: https://kotobank.jp/word/%E3%82%8F%E3%82%93%E3%81%BE%E3%82%93%E7%B5%8C%E5%96%B6-670052

Decision: change `名詞` to `名詞・ナ形`. The noun use is supported by the dictionary entry; `ワンマンな社長` is direct attributive 形動 use in the card example. Confidence: high.

## Pilot boundary

The v153 pilot's documented accepted scope is IDs 121–320. None of IDs 3652, 3654, 3677 or 3679 is covered; pilot credit is zero.
