"""Build the two-card experiment in a separate output directory."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

from scan import ROOT, constant

BASELINE = ROOT / 'JLPT_N1_ukrainian_reading_v152.html'
BASELINE_SHA = '4e4e6ab182ba0dd2fe52580d7f58a3bd3ee89cbabb669ac0d521bd0f9c6341e3'


def replace_constant(html, name, value):
    start = re.search(r'\bconst ' + name + r'\s*=\s*', html).end()
    _, end = json.JSONDecoder().raw_decode(html, start)
    return html[:start] + json.dumps(value, ensure_ascii=False, separators=(',', ':')) + html[end:]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    raw = BASELINE.read_bytes()
    assert sha256(raw).hexdigest() == BASELINE_SHA
    html = raw.decode()
    details = constant(html, 'VOCAB_DETAILS_BY_ID')
    pos = constant(html, 'VOCAB_POS_BY_ID')
    card = details['230']
    old_example = card['examples'][0]
    card.update(
        m='少し前の、ある一日を指す語。',
        t='днями, нещодавно',
        usage='Часовий іменник із прислівниковим уживанням. 先日、… — днями, 先日の会議 — нещодавня нарада. Позначає конкретний недавній день без фіксованого проміжку. 先般 формальніше, 過日 книжне. У картці 3890 те саме слово показано в офіційному мовленні.',
    )
    card['examples'][0] = '先日、駅前で偶然、大学時代の友人に会いました。'
    card['exampleTranslations'][0] = 'Днями біля станції я випадково зустрів друга з університетських часів.'
    assert old_example not in json.dumps(constant(html, 'REVIEWED_MEANING_QUIZZES').get('v_230', {}), ensure_ascii=False)
    assert old_example not in constant(html, 'VOCAB_KANA_EXAMPLE_TARGETS').get('先日', {})

    changed = replace_constant(html, 'VOCAB_DETAILS_BY_ID', details)
    pos['255'] = ['名詞', '副詞']
    experiment = replace_constant(changed, 'VOCAB_POS_BY_ID', pos)
    experiment_shell, original_shell = experiment, html
    for name in ('VOCAB_DETAILS_BY_ID', 'VOCAB_POS_BY_ID'):
        experiment_shell = replace_constant(experiment_shell, name, None)
        original_shell = replace_constant(original_shell, name, None)
    assert experiment_shell == original_shell
    args.out.mkdir(parents=True, exist_ok=True)
    for name, content in [('trial-230.html', changed), ('trial-230-255.html', experiment)]:
        output = args.out / name
        output.write_text(content, encoding='utf-8')
        print(name, sha256(output.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
