"""Record field-level author decisions, including retained content."""
import hashlib
import json
from pathlib import Path
import re
import runpy

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / 'audit152'
author = runpy.run_path(str(AUDIT / 'author.py'))
base = (ROOT / 'JLPT_N1_ukrainian_reading_v151.html').read_text()
html = (ROOT / 'release152' / 'JLPT_N1_ukrainian_reading_v152.html').read_text()

def data(text, name):
    start = re.search(r'const '+name+r'\s*=\s*', text).end()
    return json.JSONDecoder().raw_decode(text[start:])[0]

def digest(card):
    encoded = json.dumps(card, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(encoded).hexdigest()

previous = data(base, 'VOCAB_DETAILS_BY_ID')
current = data(html, 'VOCAB_DETAILS_BY_ID')
entries = {entry['id']: entry for entry in data(html, 'DEFAULT_VOCAB')}
parts_of_speech = data(html, 'VOCAB_POS_BY_ID')
rows = []
for card_id in author['CARD_IDS']:
    key = str(card_id)
    old, new = previous[key], current[key]
    entry = entries[card_id]
    assert entry['w'] == new['w']
    assert author['REASONS'][card_id].startswith(entry['r']+', 名詞')
    assert parts_of_speech[key] == (['名詞', 'ナ形'] if card_id == 113 else ['名詞'])
    assert len(new['examples']) == len(new['exampleTranslations']) == 2
    rows.append(dict(
        kind='vocab', key=key, word=entry['w'], reading=entry['r'],
        partsOfSpeech=parts_of_speech[key], suruMarker=entry['s'],
        reviewedFields=['reading', 'part of speech', 'Japanese definition', 'Ukrainian meaning', 'usage', 'related labels', 'examples and translations'],
        beforeSha256=digest(old), afterSha256=digest(new),
        changedFields=[field for field in new if new[field] != old[field]],
        rationale=author['REASONS'][card_id],
        examples=[
            dict(index=index, japanese=ja, ukrainian=uk,
                 decision='translation_corrected' if uk != old['exampleTranslations'][index] else 'retained_after_author_reading')
            for index, (ja, uk) in enumerate(zip(new['examples'], new['exampleTranslations']))
        ],
    ))
report = dict(version=152, sha256=hashlib.sha256(html.encode()).hexdigest(),
              reviewType='author_editorial_review', independentReview=False,
              vocabCards=len(rows), examplesRead=sum(len(row['examples']) for row in rows),
              vocabCardsChanged=sum(bool(row['changedFields']) for row in rows),
              changedUkrainianExampleTranslations=len(author['TRANSLATIONS']),
              newRegisterCredits=len(rows), rows=rows)
(AUDIT / 'editorial-review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(f"Author decisions: {report['vocabCards']} vocabulary cards / {report['examplesRead']} examples, {report['vocabCardsChanged']} cards edited")
