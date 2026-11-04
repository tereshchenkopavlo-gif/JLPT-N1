from pathlib import Path
import json,hashlib,shutil,subprocess,re
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit141';html=ROOT/'release141/JLPT_N1_ukrainian_reading_v141.html'
summary=json.loads((P/'build-summary.json').read_text());sha=hashlib.sha256(html.read_bytes()).hexdigest()
assert sha==summary['sha256']=='08e016a95f1786f243c29f54289edf5dd65aac4c43c9ff863b25c9f0422f75a3'
r={n:json.loads((P/f'{n}-results.json').read_text())for n in ['invariant','meaning','presentation','ui','functional','session','comparison']}
assert all(x['sha256']==sha for x in r.values())
assert len(r['invariant']['checks'])==19 and all(x['pass_']for x in r['invariant']['checks'])
assert r['meaning']['pass'] and r['meaning']['generationCases']==2128 and r['meaning']['renderedCases']==1596
assert all(x['pass']for x in r['meaning']['generated']+r['meaning']['rendered']) and not r['meaning']['errors']
assert all(x['unknownNote']==''and x['headwordNote']for x in r['meaning']['unknownContextGuard'])
assert all(len(r[n]['results'])==3 and all(x['pass']for x in r[n]['results'])for n in ['presentation','functional'])
assert len(r['ui']['checks'])==3 and all(all(v for k,v in x.items()if k!='width')for x in r['ui']['checks'])
assert r['session']['pass'] and len(r['comparison']['results'])==12 and all(x['pass']for x in r['comparison']['results'])
subprocess.run(['python',str(P/'reconcile.py')],check=True,cwd=ROOT)
shutil.copyfile(html,ROOT/html.name)
review=json.loads((P/'editorial-review.json').read_text());changed=review['revised'];assert len(changed)==12
provenance=dict(version=141,sha256=sha,inheritedFrom='v140 / strategy snapshot v139 (historical)',status='not_cleared_for_public_product',reviewType='author_editorial_review',independentReview=False,changedQuizKeys=changed,changedCardFields=summary['changedCardFields'],newFieldsOrigin='Original project editorial revisions in audit141/author.py; factual sources checked in sources.md; no imported tasks/examples.',retainedSets=253,retainedMaterialOrigin='Inherited origin uncertainty retained; no claim that semantic review or rewriting clears rights.',changedPairs=0,changedReadings=0,sources='audit141/sources.md')
(P/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
result=dict(version=141,sha256=sha,scope='Saved meaning sets only; C11 overall remains in progress',savedVocabularySets=265,contexts=530,modifiedSets=12,retainedSets=253,exampleOverrides=156,additionalGrammarQuiz='g95, two contexts, unchanged',authorReview='audit141/editorial-review.json',independentReview=False,generationCases=2128,renderedCases=1596,creditedRegisterRows=265,remainingC11=['General automatic meaning candidates','Reading alternative pools','Cloze semantic uniqueness','Future/custom contexts'],provenance='audit141/provenance.json')
(ROOT/'completion/C11-saved-sets-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(ROOT/'JLPT_N1_v141_audit.md').write_text(f'''# Аудит JLPT N1 v141 — 4 листопада 2026, Asia/Tokyo

Повний `{html.name}`, {html.stat().st_size} байтів; SHA-256 `{sha}`. Основа — опублікований v140, commit c82e3b18361a6396969220f385760cffff4c8ed4, SHA-256 810af1aecf5a71b2fbd39b687e3ec310763317cb3f04821107cdeb983c31f537. Попередній HTML збережено. Незавершений checkpoint work/v141-checkpoint / 5dc0023a8878ce6f90465af078222bc435c4cb79 зберігав редакторські джерела до фінального gate, не готовий реліз.

## Авторський перегляд збережених вправ C11

Переглянуто **всі 265 збережених лексичних наборів REVIEWED_MEANING_QUIZZES**, обидва чинні приклади кожного: **530 контекстів**, правильні відповіді, три альтернативи й пояснення. У v140 було 151 byExample-відгалуження, тепер 156; це 421 окремий збережений payload (265 базових +156 відгалужень), що використовується в 530 контекстах. Кількість записів наборів не зросла. Окремо переглянуто незмінний runtime-набір g95 з двома прикладами: фактично у JS є 266 наборів, хоча початковий реєстр обліковує 265 JSON-записів. Повну граматичну картку g95 цим не зараховано.

Поіменні рішення й конкретні змістові розмежування — [decisions.tsv](audit141/decisions.tsv). [editorial-review.json](audit141/editorial-review.json) містить точні речення, усі варіанти, ключі, примітки, хеші до/після та рішення для кожного ID. Це нова **авторська редакторська перевірка**, не незалежна мовна експертиза і не автоматично підтверджена складність для всіх учнів. [Джерела та межі](audit141/sources.md) відділені від технічних тестів.

## Виправлення — 12 наборів

| ID | Рішення |
|---|---|
| v2200 放射能 | Наукове значення здатності випромінювати відділено від побутового перенесення на речовину; змінено лише примітку. |
| v2210 身代金 | Другий приклад має власний набір про викуп за повернення даних, а не звільнення заручника. Японське визначення картки доповнене вже наявним у usage розширеним значенням. Речення, переклади й usage збережені. |
| v2364 夜更かし | 徹夜 прибрано з хибних відповідей: близьке поняття не є надійною однозначною помилкою. Нові альтернативи — нічні пробудження, пізній підйом, денний сон. |
| v2399 うかがう | У питанні про お話をうかがう не протиставляються 聞く і 尋ねる як безумовно правильне/неправильне. Заміна однієї альтернативи та уточнення примітки. |
| v2764 揉む | てもらう показує отриману послугу, але не доводить окремого прохання. Змінено лише українську примітку. |
| v3158 善良 | У фіксованій сполуці про управителя — обачність, очікувана від відповідної ролі, а не занижений за особистими здібностями стандарт. |
| v3707 〜語 | Окремі набори для назви мови フランス語 та термінів 専門用語. |
| v3718 〜率 | Окремо частка працевлаштованих і відносна зміна цін щодо бази. Не дописано невказаний період або конкретний знаменник. |
| v3787 いらっしゃる | Окремі короткі ключі для 来る та いる замість спільного переліку двох значень. |
| v3817 頂く | ご意見 не обов’язково критичні зауваження; уточнено українську примітку. |
| v3820 させていただく | Власна дія подається як дозволена й корисна мовцеві; дозвіл може випливати з обставин, а не обов’язково бути названим прямо. |
| v3836 存じ上げる | Другий приклад перевіряє знання факту про наставника. Заперечення цього знання не доводить відсутності знайомства з людиною. |

**253 набори збережено.** Одне змінене поле словникової картки — `VOCAB_DETAILS_BY_ID[2210].m`. Решта визначень, читань, POS, заголовків, usage, прикладів і перекладів карток незмінні. Нових або змінених порівнянь **0**, перелік змінених пар порожній; збережено 859/92/41 пар. Усі 160 читань і 381 питання читання незмінні. Повний поіменний diff є в build-summary.json, author.py та editorial-review.json.

Виправлено область застосування базового набору: невідоме стороннє речення більше не успадковує прив’язану до першого прикладу примітку. Чинні byExample й точні C04-набори зберігають пріоритет. Для стороннього контексту лишається загальна евристика, не новий «перевірений» набір; її семантичний аудит залишається відкритим.

## Фактичні перевірки

- **19 груп інваріантів**, JS-синтаксис, точний дозволений diff. 3914/130, усі стабільні ID й дані прогресу збережені. Інші HTML/JS/CSS-байти, крім версії й вузької перевірки контексту, незмінні.
- **2128 фактичних генерацій:** 530 лексичних +2 граматичні контексти, кожен із ключем на кожній із чотирьох позицій. Зіставлено точні варіанти, ключ, вихідне речення та пояснення. Контроль перестановки лише у тестовому браузері.
- **1596 фактичних показів:** усі 532 контексти на 360/412/1280px; натискання хибної відповіді, рівно один правильний/хибний маркер, видима правильна примітка, без горизонтального переповнення та помилок JS. Окремо перевірено guard невідомого контексту для шести багатозначних слів.
- Chromium {r['meaning']['browser']}: POS/пошук/фільтри, картки, гортання/клавіші/свайпи/асинхронна навігація, порівняння, backup/import/reload на трьох ширинах; повна сесія — {r['session']['pages']} сторінок, {r['session']['answers']} відповідей, {r['session']['graded']} оцінок. 12 сценаріїв теми й масштабу 比較. Усі звіти прив’язані до SHA цього HTML. Візуально оглянуто виправлені 身代金, 率, 存じ上げる з японським шрифтом. Реальні Android/Windows не тестувалися.

## Приймальний реєстр і залишок

[Зарахування](completion/reconciled-v141.json): рівно 265 рядків `reviewed_meaning_quiz` отримали авторський доказ; попередні 60 доказів збережені. Разом **325 reviewed /5517 pending із 5842 різнорідних позицій**. Це не відсоток готовності й не 325 повністю перевірених карток. Додаткові g95-контексти не збільшували знаменник і не зараховувалися як повна картка.

**C11 загалом не закрито.** Наступна ділянка: загальні автоматичні meaning-набори поза цими 265, семантична однозначність cloze й правдоподібність reading-пулів; потрібний скінченний облік придатних і виключених випадків. C07, C08/C09, C10/C18, решта 40 текстів та приймання 1.0 залишаються відкритими. Історичні звіти, baseline та strategy snapshot v139 не переписані; [походження змін](audit141/provenance.json) не є правовим очищенням. Архітектуру N5–N1, scheduler і масове розширення не реалізовано.

[Відтворення](audit141/README.md). Наступна повна основа — v141.
''')
p=ROOT/'PROJECT_STATUS.md';tail=p.read_text().split('## Нова стратегія й документи',1)[1]
tail=tail.replace('5842 позиції, зараховано 60 авторських перевірок v135; 5782 pending','5842 позиції, зараховано 60 доказів v135 та 265 наборів вправ v141; 5517 pending')
p.write_text(f'''# PROJECT_STATUS.md — JLPT N1

Оновлено 4 листопада 2026, Asia/Tokyo. Актуальна **v141**. Повний `{html.name}`, {html.stat().st_size} байтів; SHA-256 `{sha}`. Аудит JLPT_N1_v141_audit.md, відтворення audit141/README.md. Основа v140 / commit c82e3b18361a6396969220f385760cffff4c8ed4. Старі випуски збережено.

3914 слів/130 конструкцій, 99 середніх/61 довгий =160 текстів, 381 питання; 859/92/41 пар. Обсяг незмінний, залишок 21/19 текстів.

## Виконано у v141

Авторський змістовий перегляд усіх 265 збережених лексичних meaning-наборів: 530 чинних контекстів, усі варіанти/ключі/примітки. Виправлено 12 наборів, 253 збережено; byExample 151→156. Окремо переглянуто незмінний runtime g95 (2 приклади), без зарахування повної граматичної картки. decisions.tsv та editorial-review.json містять точні ID, речення й рішення; sources.md відділяє фактичну зовнішню звірку від авторських оцінок.

Ключові виправлення: викуп за дані, близькі 夜更かし/徹夜 і 聞く/尋ねる, мова/термін, частка/темп зміни, приходити/перебувати, знання факту про людину. Визначення 身代金 доповнено розширеним значенням, вже наявним у usage. Лише це поле карток змінено; приклади/переклади, усі читання, порівняння, ID й сховище незмінні. Невідомі сторонні речення більше не отримують базову контекстну примітку автоматично.

Пройдено 19 інваріантів/JS-синтаксис, 2128 генерацій, 1596 показів із відповіддю та поясненням на трьох ширинах, POS/гортання/порівняння/backup/import/reload, повну сесію, 12 сценаріїв 比較. Контрольні суми звітів належать фінальному HTML. Це авторський/браузерний пакет, не незалежна експертиза всіх карток і не практичний Android/Windows.

Зараховано рівно 265 рядків вправ: разом 325 reviewed /5517 pending із 5842 різнорідних позицій. C11 лишається in_progress: загальні meaning/reading/cloze поза перевіреними наборами ще потребують семантичної перевірки. C04/C05/C06/C23 збережені. Наступна основа — повний v141.

## Нова стратегія й документи'''+tail)
p=ROOT/'completion/BACKLOG.md';s=p.read_text().replace('Оновлено 1 листопада 2026','Оновлено 4 листопада 2026').replace('Поточний HTML — v140','Поточний HTML — v141')
s=s.replace('Зараховано наявний авторський перегляд 18 текстів/42 питань v135, тобто 60 позицій.','Збережено 60 авторських доказів v135; у v141 додано 265 поіменно перевірених наборів meaning-вправ: 325 reviewed /5517 pending. Не зараховано повні картки.')
start=s.index('| C11 |');end=s.index('\n',start)
s=s[:start]+'| C11 | 2 | **in_progress** — збережені meaning-набори перевірено у v141 | Усі 265 наборів /530 прикладів: 12 виправлень, 253 збереження, 156 byExample; окремо runtime g95 (2 приклади). author review, не незалежна експертиза. 2128 генерацій/1596 показів; completion/C11-saved-sets-result.json, audit141/editorial-review.json, reconciled-v141.json. **Залишок:** загальні meaning-кандидати, reading-пули, семантична однозначність cloze й невідомі контексти. Увесь C11 не закрито. |'+s[end:]
s=s.replace('Перше зарахування:','Зарахування v141: [reconciled-v141.json](reconciled-v141.json), відтворення `python3 audit141/reconcile.py`: 265 збережених наборів, без зарахування повних карток; попередні 60 доказів не змінено. Разом 325 reviewed /5517 pending, це не загальний відсоток готовності.\n\nПерше зарахування:') if 'Зарахування v141:' not in s else s
p.write_text(s)
p=ROOT/'README.md';s=p.read_text();history=s[s.index('Нижче збережено історичний журнал'):]
p.write_text(f'''# JLPT N1 — тренажер з японським інтерфейсом

**Актуальна v141:** [повний HTML](JLPT_N1_ukrainian_reading_v141.html) · [аудит](JLPT_N1_v141_audit.md).

Переглянуто всі 265 збережених наборів питань на значення у 530 прикладах, виправлено 12. Точніше розмежовано контекстні значення й близькі альтернативи; додано окремі відповіді для викупу за дані, мови/термінів, частки/темпу зміни та інших багатозначних уживань. ID, прогрес, читання й оформлення збережено.

3914 слів, 130 конструкцій, 160 текстів, 381 питання читання. Поточний наскрізний аудит ще не завершено. Звіти, походження й межі — у PROJECT_STATUS.md та audit141/. SHA-256 `{sha}`.

Попередні [v140](JLPT_N1_ukrainian_reading_v140.html), [v139](JLPT_N1_ukrainian_reading_v139.html), [v128](JLPT_N1_ukrainian_reading_v128.html) збережено. Перед відкриттям іншого HTML зробіть резервну копію прогресу в 設定.

'''+history)
print(json.dumps(dict(version=141,sha256=sha,bytes=html.stat().st_size,reviewedRegisterPositions=325,pending=5517)))
