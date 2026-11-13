"""Prepare browser acceptance from the existing v152 checks and pilot build."""
import argparse
import json
from pathlib import Path

from trial import BASELINE, CARD_EDITS, DEFINITION_EDITS, ROOT, TRANSLATION_EDITS
from scan import constant
from hashlib import sha256


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('candidate', type=Path)
    args = parser.parse_args()
    candidate = args.candidate.resolve()
    baseline = BASELINE.read_text()
    html = candidate.read_text()
    digest = sha256(candidate.read_bytes()).hexdigest()
    ids = set(CARD_EDITS) | set(DEFINITION_EDITS) | set(TRANSLATION_EDITS) | {'230'}
    originals = constant(baseline, 'VOCAB_DETAILS_BY_ID')
    cards = constant(html, 'VOCAB_DETAILS_BY_ID')
    vocabulary = constant(html, 'DEFAULT_VOCAB')
    grammar = constant(html, 'GRAMMAR')
    pos = constant(html, 'VOCAB_POS_BY_ID')
    assert len(vocabulary) == len(cards) == 3914
    assert len(grammar) == 130
    assert cards.keys() == originals.keys()
    assert {key for key in cards if cards[key] != originals[key]} == ids
    for key in ('DEFAULT_VOCAB', 'VOCAB_POS_BY_ID', 'GRAMMAR', 'GRAMMAR_DETAILS_BY_ID', 'VOCAB_AUDITED_PAIRS'):
        assert constant(html, key) == constant(baseline, key)
    previous = constant(baseline, 'REVIEWED_MEANING_QUIZZES')
    current = constant(html, 'REVIEWED_MEANING_QUIZZES')
    assert current.keys() - previous.keys() == {'v_264', 'v_293'}
    assert all(current.get(key) == value for key, value in previous.items())

    rows = [
        dict(key=str(word['id']), word=word['w'], reading=word['r'], partsOfSpeech=pos[str(word['id'])])
        for word in vocabulary if str(word['id']) in ids
    ]
    assert len(rows) == 80
    out = candidate.parent
    review = out / 'acceptance-review.json'
    review.write_text(json.dumps(dict(sha256=digest, rows=rows), ensure_ascii=False))
    for source, replacements in {
        'vocab-browser.cjs': {
            'audit152/editorial-review.json': str(review),
            'audit152/vocab-results.json': str(out / 'acceptance-vocab.json'),
            '60 vocabulary cards': '80 vocabulary cards',
        },
        'session-completion.cjs': {
            'audit152/session-results.json': str(out / 'acceptance-session.json'),
            'PASS v152': 'PASS candidate',
        },
    }.items():
        script = (ROOT / 'audit152' / source).read_text()
        replacements['release152/JLPT_N1_ukrainian_reading_v152.html'] = str(candidate)
        for old, new in replacements.items():
            assert old in script
            script = script.replace(old, new)
        (out / source).write_text(script)
    print(f'{digest} · {len(vocabulary)} vocabulary · {len(grammar)} grammar · {len(rows)} changed cards')


if __name__ == '__main__':
    main()
