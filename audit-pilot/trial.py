"""Build the vocabulary experiments in a separate output directory."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

from scan import ROOT, constant

BASELINE = ROOT / 'JLPT_N1_ukrainian_reading_v152.html'
BASELINE_SHA = '4e4e6ab182ba0dd2fe52580d7f58a3bd3ee89cbabb669ac0d521bd0f9c6341e3'


DEFINITION_EDITS = {
    '122': '商品やサービスなどを、代金を払って手に入れること。',
    '131': '過去の出来事や状態をもう一度現すこと。また、同じ現象が再び起こること。',
    '144': '人や意見などに賛成して後押しすること。また、物を支えること。',
    '184': '規模や範囲を小さくすること。また、規模や範囲が小さくなること。',
    '203': '金融機関などを通じて、指定された口座に金銭を送ること。',
    '264': '活動などを広げて進めること。また、物事が進んで別の局面に移ること。',
    '267': '商品を売ったりサービスを提供したりする営業の場所や施設。',
    '268': '受け取った郵便物やメッセージを別の宛先に送ること。また、機器などの間でデータを送ること。',
    '293': '物を壊したり、環境や秩序などの成り立ちを損なったりすること。',
    '313': '複数のものを照らし合わせ、共通点や相違点を調べること。',
}


MEANING_TRIAL = {
    '264': {
        '同社は、海外市場に向けて積極的に事業を展開している。': {
            'correct': '海外市場に向けて事業を広げること。',
            'wrong': ['海外事業の成果を評価すること。', '海外市場の動向を調査すること。', '海外事業の運営を他社に任せること。'],
            'note': '事業を展開する — розгортати діяльність. Оцінювання, дослідження ринку й делегування можуть супроводжувати вихід на ринок, але позначають інші дії.',
        },
        '予想外の展開に、会場は騒然となった。': {
            'correct': '物事が進む中で生じた成り行き。',
            'wrong': ['物事を始めることになったきっかけ。', '物事を進めるために立てた計画。', '物事が終わった後に下した評価。'],
            'note': 'Тут — «поворот подій». Ідеться про те, як пішли події, а привід, план і оцінка стосуються інших етапів.',
        },
    },
    '293': {
        '森林の破壊は、地球環境に深刻な影響を及ぼす。': {
            'correct': '森林の成り立ちを大きく損なうこと。',
            'wrong': ['森林に入れる区域を狭めること。', '森林で利用する樹種を選ぶこと。', '森林を守る制度を整えること。'],
            'note': 'Тут 破壊 означає руйнування лісів. Обмеження доступу, добір видів і захист лісу описують інші дії.',
        },
        '古い慣習を破壊して、新しい仕組みを築く必要がある。': {
            'correct': '古い慣習を根本から成り立たなくすること。',
            'wrong': ['古い慣習の一部を手直しすること。', '古い慣習の由来を調べること。', '古い慣習を別の地域に広めること。'],
            'note': 'Тут ідеться про докорінне руйнування старих звичаїв. Часткові виправлення, дослідження походження й поширення звичаїв такого змісту не мають。',
        },
    },
}


TRANSLATION_EDITS = {
    '121': (0, 'Професор читає лекції з економіки в університеті.'),
    '128': (1, 'Саме у складних ситуаціях перевіряється справжня спроможність організації.'),
    '129': (1, 'Через плутанину між ліками зі схожими назвами хтось помилково прийняв не той препарат.'),
    '148': (1, 'Коли ми поглянули на проблему з іншого боку, її суть почала прояснюватися.'),
    '149': (1, 'Завдяки досвіду за кордоном мій кругозір значно розширився.'),
    '151': (1, 'Японія залежить від імпорту значної частини своїх енергоресурсів.'),
    '168': (0, 'Компанія, з якою ми багато років вели справи, раптово повідомила нам про припинення договору.'),
    '169': (1, 'Статтю завершили після неодноразового збирання матеріалів на місці.'),
    '182': (0, 'Цього фінансового року під час розподілу бюджету пріоритет віддадуть підготовці кадрів.'),
    '199': (1, 'Безлад триває, і поки неясно, коли його вдасться владнати.'),
    '201': (0, 'Дедалі більше працівників хочуть перейти на інший вид роботи.'),
    '202': (1, 'Він сумлінно виконує посадові обов’язки, і керівник йому дуже довіряє.'),
    '221': (0, 'Протидію низькій народжуваності визначили як першочергове завдання державної політики.'),
    '223': (0, 'Під час негласної перевірки викрили, хто саме вчиняв порушення.'),
    '235': (1, 'За підсумками підрахунку голосів того ж дня перемога чинного посадовця стала практично певною.'),
    '250': (1, 'Освоєння нових напрямів є рушієм зростання компанії.'),
    '256': (0, 'Підвищення мінімальної зарплати посилює фінансовий тиск на малі й середні підприємства.'),
    '259': (1, 'Ретельно розглянувши пропозицію, вирішать, чи її приймати.'),
    '260': (1, 'У відповідь на запит для підготовки матеріалу нам люб’язно надали цінну інформацію.'),
    '261': (1, 'Компанія представила конкретні числові цілі для відновлення діяльності.'),
    '266': (1, 'З оглядового майданчика видно всю міську забудову.'),
    '279': (0, 'Люди один за одним висловлювали глибоке співчуття постраждалим від стихії.'),
    '282': (1, 'Порядок проведення тендеру переглянули, щоб вигоду не отримували переважно окремі компанії.'),
    '286': (1, 'За відведений час важко відвідати всі заплановані об’єкти.'),
    '290': (0, 'Для старших покупців розробили товар із написами, які легко читати.'),
    '303': (0, 'Потрібно точно зрозуміти інформацію й, спираючись на неї, зважено ухвалити рішення.'),
}


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
    for key, definition in DEFINITION_EDITS.items():
        details[key]['m'] = definition
    definitions = replace_constant(changed, 'VOCAB_DETAILS_BY_ID', details)
    assert replace_constant(definitions, 'VOCAB_DETAILS_BY_ID', None) == replace_constant(html, 'VOCAB_DETAILS_BY_ID', None)
    quizzes = constant(html, 'REVIEWED_MEANING_QUIZZES')
    for key, examples in MEANING_TRIAL.items():
        entry = 'v_' + key
        assert entry not in quizzes
        assert set(examples) == set(details[key]['examples'])
        quizzes[entry] = {
            'correct': details[key]['m'],
            'wrong': ['物事の原因を明らかにすること。', '物事の価値を判断すること。', '物事の経緯を記録に残すこと。'],
            'note': '',
            'byExample': examples,
        }
    meaning = replace_constant(definitions, 'REVIEWED_MEANING_QUIZZES', quizzes)
    assert replace_constant(meaning, 'REVIEWED_MEANING_QUIZZES', None) == replace_constant(definitions, 'REVIEWED_MEANING_QUIZZES', None)
    for key, (index, translation) in TRANSLATION_EDITS.items():
        assert details[key]['exampleTranslations'][index] != translation
        details[key]['exampleTranslations'][index] = translation
    translations = replace_constant(meaning, 'VOCAB_DETAILS_BY_ID', details)
    assert replace_constant(translations, 'VOCAB_DETAILS_BY_ID', None) == replace_constant(meaning, 'VOCAB_DETAILS_BY_ID', None)
    previous_details = constant(meaning, 'VOCAB_DETAILS_BY_ID')
    assert details.keys() == previous_details.keys()
    assert {key for key in details if details[key] != previous_details[key]} == TRANSLATION_EDITS.keys()
    for key, (index, translation) in TRANSLATION_EDITS.items():
        previous_details[key]['exampleTranslations'][index] = translation
    assert details == previous_details
    args.out.mkdir(parents=True, exist_ok=True)
    for name, content in [
        ('trial-230.html', changed),
        ('trial-230-255.html', experiment),
        ('trial-definitions.html', definitions),
        ('trial-meaning.html', meaning),
        ('trial-translations.html', translations),
    ]:
        output = args.out / name
        output.write_text(content, encoding='utf-8')
        print(name, sha256(output.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
