# v181 C11 — source review for ID2433 そびえる

**Accessed:** 13 November 2026.

## Lexical basis

- Shogakukan Digital Daijisen via Kotobank, 聳える: https://kotobank.jp/word/%E8%81%B3%E3%81%88%E3%82%8B-555102
  - The contemporary sense is an intransitive verb: mountains, buildings, etc. stand very high; the entry gives examples involving a sacred peak and high-rise housing.
  - This supports the existing card definition “山や建物などが、非常に高く立っている。” and the Ukrainian gloss “височіти, здійматися”.
- The exact v179 card examples are preserved. Both contain the inflected form そびえて, which is already bound to the headword by VOCAB_KANA_EXAMPLE_TARGETS. No example text or target mapping was changed.

## Question design

- Building context: the correct option expresses a building standing very high relative to its surroundings. The three distractors describe a lower position, equal height with surrounding buildings, and horizontal spread.
- Mountain context: the correct option expresses a mountain standing very high relative to its surroundings. The distractors describe a low valley-like position, a low rounded hill, and a flat continuation at ground level.
- All four options in each context are distinct and comparable in grammatical form and approximate length. The Ukrainian note identifies the contextual sense and explains the contrast.
- The existing automatic candidates for そびえる included unrelated meanings from other cards (e.g. twisting, shifting position, irritation, protection, following a route). The saved context-specific sets replace those unrelated options only for the two exact examples.

## Cloze boundary

The existing literal-cloze gate requires the marked span to equal the dictionary headword. Here the reviewed exact form is そびえて, not そびえる, so literal cloze was already unavailable for both examples. The saved meaning entry also excludes cloze for that card under the existing rule, but the before/after diagnostic confirms that no previously available cloze route is lost. No code or learning mechanism was changed.

## Related open diagnostic

v180 reproduced the exact reading algorithm after the proposed POS additions for ID255/327. It changed 23 pools, caused ID255, ID327 and ID1819 to fall below three automatic distractors, and gave ID359 a third distractor. No POS or reading override changes are included in v181. The full diagnostic is preserved as completion/v180-c11-diagnostics.json and remains diagnostic evidence, not author acceptance.
