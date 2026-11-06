"""Prepare v153 or stage it once candidate acceptance reports are available."""
import argparse
import json
from hashlib import sha256
from pathlib import Path

from trial import ROOT

VERSION_MARKER = '学習アプリ · v152'
CANDIDATE_SHA = 'a17955719de8780f5c89b30fdff9fe67ef24f66887f4ab4c3bd6a2e9f13726b1'
RELEASE_NAME = 'JLPT_N1_ukrainian_reading_v153.html'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=Path)
    parser.add_argument('--stage', action='store_true')
    args = parser.parse_args()
    source = args.directory / 'trial-editorial.html'
    assert sha256(source.read_bytes()).hexdigest() == CANDIDATE_SHA
    html = source.read_text(encoding='utf-8')
    assert html.count(VERSION_MARKER) == 1
    data = html.replace(VERSION_MARKER, '学習アプリ · v153').encode()
    digest = sha256(data).hexdigest()
    (args.directory / RELEASE_NAME).write_bytes(data)
    print(digest, len(data))
    if not args.stage:
        return

    vocab = json.loads((args.directory / 'acceptance-vocab.json').read_text())
    session = json.loads((args.directory / 'acceptance-session.json').read_text())
    assert all(result['pass'] and result['sha256'] == digest for result in (vocab, session))
    assert len(vocab['results']) == 240 and all(row['pass'] for row in vocab['results'])
    assert all(session[key] > 0 for key in ('pages', 'answers', 'graded', 'storedBytes'))

    run = 'https://github.com/tereshchenkopavlo-gif/JLPT-N1/pull/1/checks'
    audit = f"""# Аудит JLPT N1 v153

Основа — v152. Повний HTML містить 3914 слів, 130 граматичних конструкцій і 160 текстів для читання. Обсяг бази й ідентифікатори збережено. Розмір файла — {len(data)} байтів. SHA-256 — `{digest}`.

Авторський пілот охопив 200 словникових карток, ID 121–320. У цьому випуску змінено 80 карток. Уточнено японські визначення, українські значення, примітки та переклади. Для 展開 і 破壊 додано чотири контекстні завдання. Збережено чинну класифікацію 直接 після перевірки добору альтернатив. Для 同士 уточнено визначення зі збереженням позначки частини мови. У цьому випуску офіційний реєстр аудиту збережено як у v152. [Пілот і поіменні рішення](https://github.com/tereshchenkopavlo-gif/JLPT-N1/tree/work/vocab-audit-pilot/audit-pilot)

Перевірки точного HTML v153 охопили 240 відкриттів карток на трьох ширинах, чотири контекстні завдання та повну навчальну сесію зі збереженням прогресу після перезавантаження. Незалежна мовна оцінка, перевірка на фізичних Android і Windows та аудит походження матеріалів залишаються окремими етапами. [Браузерні перевірки]({run})
"""
    (ROOT / RELEASE_NAME).write_bytes(data)
    (ROOT / 'JLPT_N1_v153_audit.md').write_text(audit, encoding='utf-8')
    readme = ROOT / 'README.md'
    old = readme.read_text(encoding='utf-8')
    header, history = old.split('Нижче збережено історичний журнал', 1)
    title = header.splitlines()[0]
    readme.write_text(f"""{title}

Актуальна **v153**. [Повний HTML]({RELEASE_NAME}) · [Аудит](JLPT_N1_v153_audit.md)

Уточнено 80 словникових карток і додано чотири контекстні завдання. 3914 слів, 130 конструкцій, 160 текстів і 381 питання читання. SHA-256 `{digest}`. Перед переходом до іншого HTML збережіть резервну копію прогресу в 設定. [Попередня v152](JLPT_N1_ukrainian_reading_v152.html)

Нижче збережено історичний журнал{history}""", encoding='utf-8')
    status = ROOT / 'PROJECT_STATUS.md'
    old = status.read_text(encoding='utf-8')
    title, _, history = old.split('\n\n', 2)
    status.write_text(f"""{title}

Оновлено 6 листопада 2026, Asia/Tokyo. Актуальна **v153**. Повний `{RELEASE_NAME}`, {len(data)} байтів. SHA-256 `{digest}`. [Аудит](JLPT_N1_v153_audit.md)

## Виконано у v153

Пілот охопив ID 121–320. Випуск містить правки у 80 картках і чотири контекстні вправи. Перевірено 240 показів карток, повну сесію та збереження прогресу. Офіційний реєстр збережено на рівні v152.

{history}""", encoding='utf-8')


if __name__ == '__main__':
    main()
