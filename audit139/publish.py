from pathlib import Path
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit139';html=ROOT/'release139/JLPT_N1_ukrainian_reading_v139.html'
expected='e18ab0ee3ec3a56dced31b9abb6ec4813d92c102f93f20922e3dc05718d1dd17'
assert hashlib.sha256(html.read_bytes()).hexdigest()==expected
reports={n:json.loads((P/f'{n}-results.json').read_text()) for n in ['invariant','scan','targets-browser','identity','presentation','ui','functional','session','comparison']}
assert all(x['sha256']==expected for x in reports.values())
assert all(x['pass_'] for x in reports['invariant']['checks'])
assert reports['scan']['pass'] and reports['scan']['singleCharacterCandidates']==289 and len(reports['scan']['changed'])==238
assert reports['targets-browser']['generatorCases']==5004 and reports['targets-browser']['renderings']==1090 and all(x['pass'] for x in reports['targets-browser']['results'])
assert reports['identity']['pass'] and reports['identity']['importedProgress']['status']=='S' and reports['identity']['importedProgress']['timesShown']==4
assert reports['session']['pass'] and len(reports['comparison']['results'])==12 and all(x['pass'] for x in reports['comparison']['results'])
# Other scripts exit nonzero on any assertion; ensure their expected width results exist.
assert len(reports['presentation']['results'])==3
summary=json.loads((P/'build-summary.json').read_text());rows=json.loads((P/'targets.json').read_text());decisions=json.loads((P/'adjudications.json').read_text())['rows']
ids={k:sorted({x['id'] for x in decisions if x['kind']==k}) for k in ['v','g']}
proof=dict(version=139,sha256=expected,scope='Author review of all 526 target-boundary candidates; not all fields of affected cards or independent legal/linguistic review.',candidateIds=ids,reviewedExamples=526,decisions=summary['decisions'],newExactMappings=237,changedExamples=238,retainedSingleCharacterResults=289,zeroUnmarked=True,newContextQuizSets=10,evidence=['audit139/adjudications.json','audit139/scan-results.json','audit139/targets-browser-results.json','audit139/sources.md'])
(ROOT/'completion/C05-result.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
(ROOT/'completion/C06-result.json').write_text(json.dumps(dict(version=139,sha256=expected,id=716,oldWord='恵',word='恵み',reading='めぐみ',category='名詞(その他)',progressIdentity='v:716 unchanged',scope='Built-in word spelling/header/explanation and generated exercises; user custom vocab not silently migrated.',evidence=['audit139/sources.md','audit139/identity-results.json','audit139/invariant-results.json']),ensure_ascii=False,indent=2)+'\n')
shutil.copyfile(html,ROOT/html.name)
(ROOT/'JLPT_N1_v139_audit.md').write_text(f'''# Аудит JLPT N1 v139 — випуск 4 листопада 2026, Asia/Tokyo

Повний HTML: `JLPT_N1_ukrainian_reading_v139.html`, {html.stat().st_size} байтів; SHA-256 `{expected}`.
Основа — v138, SHA-256 `6f7ea6a3d4ca30e8a9cc6ffad31994d99e925809fa4d4b94fe2bf28349027dfc`, main `236317fe0f9b47d4afceea2d02bf20fdbdf36c75`.

## C05: завершено вузький перегляд усіх 526 кандидатів

Авторський перегляд стосується тотожності цільового слова/конструкції в прикладі та меж виділення. Початкові 306 «shortened/embedded» складалися з **222 обрізаних дієслівних форм і 84 коректних афіксів**; окремо перевірено 210 іменникових прикладів і 10 граматичних. 526 не названо 526 помилками.

- **237 адресних відповідностей**: 222 дієслівні форми, 10 повних граматичних конструкцій, 5 випадків звичайного написання/повторення (恵み×2, 並み×2, 峰々). Словникові заголовки не підставляються буквально замість цих відмінених форм у cloze; питання на читання прямо називає заголовок (`見出し語`).
- **Один приклад замінено:** v790:1 (індекс від нуля), 情報網 із читанням もう → переносне 捜査の網 із читанням あみ. Повний новий приклад і український переклад — у build.py. Збережено окремий суфікс 〜網 ID3733.
- **288 виділень збережено**, оскільки ціль — повне однознакове слово/морфема. Доказ для кожного кандидата: [adjudications.json](audit139/adjudications.json). Повний scan має 289 однознакових результатів: 288 збережених плюс новий коректний 網; їх не оголошено помилками.

ID всіх розглянутих C05-карток (включно зі збереженнями), **не повний аудит усіх їхніх полів**:

Лексика: {', '.join(map(str,ids['v']))}.

Граматика: {', '.join(map(str,ids['g']))}.

Змінено відображення прикладів на 160 картках; точні 237 mappings та один новий приклад перелічені по kind/ID/exampleIndex. **Наявні 30 C04-записів байтово збережені**; загальний exact-реєстр — 267. Для нових записів без `quiz` збережене попереднє повне meaning-пояснення; помилкового порожнього пояснення не введено.

## C06: 恵み й контекстні питання

У вбудованій картці **ID716** виправлено заголовок 恵 → 恵み, уточнено переклад/usage й наявну категорію 名詞(その他). Читання めぐみ, POS 名詞, ID, обидва приклади/переклади й ключ прогресу збережено. [identity-results.json](audit139/identity-results.json) перевіряє справжній експорт backup v138 з тестовим прогресом ID716 → імпорт у v139 → reload → картку/POS та порівняння за старими ID. Власні CSV-набори користувача не перейменовуються автоматично.

Для g120/123/124/125/127 підготовлено **10 авторських контекстних наборів** (правильна дефініція, 3 хибні варіанти, українське пояснення). Розмежовано ситуаційне なら…で, прохання/ввічливу заборону з 願う, напрям дії くださる/いただく і «одягати» проти «подобатися» у 召す. Це 10 нових коротких контекстних вправ, не нові питання читання. Усі 10 ключів/30 альтернатив прочитані за реченнями. Джерела й межі: [sources.md](audit139/sources.md).

## Незмінний обсяг і регресії

3914 слів, 130 конструкцій, 160 текстів (99/61), 381 питання читання. Усі тексти/питання читання, граматичні визначення, POS-map, старі 265 meaning-наборів та kana-targets незмінні. Нових/змінених порівнянь **0**, список порожній: 859 лексичних/92 граматичні/41 антонімічна пара збережені. CSS/типографіка 比較 v138, гортання, фільтри й формат прогресу незмінні. Нових зовнішніх runtime-залежностей немає.

Перевірено 18 груп інваріантів, синтаксис JS і реальні старий/новий markTarget на всіх **8089** прикладах: 0 unmarked, рівно 238 дозволених змін. **801 негативна перевірка** області exact-реєстру (повне речення/тип/заголовок).

Chromium {reports['targets-browser']['browser']}: **5004 генерації** (556 контекстів ×3 ширини ×3 позиції вибору типу), **1090 відображень із відповіддю**, ключ/пояснення/виділення/overflow. 556 — усі 526 C05 +30 C04; випадкові комбінації C11 не оголошені вичерпаними. Окремо: консервація тексту/POS/фільтри/порівняння на 360/412/1280px, кнопки/клавіші/свайпи/запізніле відкриття, backup/import/reload, 12 комбінацій теми/масштабу/ширини 比較 та повна звичайна сесія ({reports['session']['pages']} сторінок, {reports['session']['answers']} відповідей, {reports['session']['graded']} оцінювань). Успішні звіти містять фінальний SHA-256.

Локальний мовний/технічний прохід розпочато 1 листопада; остаточний CI gate й випуск — 4 листопада. Робочий незавершений checkpoint `work/v139-checkpoint` / `9d42ed8f1351b49e935425ecab24b10e9414c839` відокремлено від релізу. Візуально оглянуто приклади ご足労いただき, дві форми 破る і 恵み; CJK-шрифт доступний у тестовому середовищі. Фізичні Android/iOS/ПК не тестувалися. Відтворення — [audit139/README.md](audit139/README.md).

## Нове стратегічне доручення 4 листопада

Підготовлено [strategy/](strategy/README.md): знімок стану; попередній реєстр 14198 одиниць походження/ризиків і 13 груп джерел; рекомендації власної класифікації/legacy-міграції; окремий документ «Методологія ефективного навчання JLPT». Нова стратегія не змінює runtime. Масштабне розширення до майбутніх 4000+/150+, перенесення N1/N2, спільні ID, 文法マップ та навчальний scheduler не реалізовані.

Збережено історичні мовні аудити; вони не є правовим очищенням. Старий користувацький дозвіл на книгу не вважається дозволом правовласника. Інвентаризація джерел попередня: повного зіставлення з книгою/юридичного висновку немає. Повний текст/аудіо відео PIVOT недоступні для завершальної звірки; перевірено метадані/опис, незалежні наукові праці розглянуті окремо. Це явно відкритий залишок C21.

C05/C06 закриті в зазначеному вузькому обсязі. C07, C11, повний C18 та решта поточного наскрізного аудиту відкриті. Повний finalReview карток не зараховано лише за точні spans. Межа 120/80 читань лишається чинною. Увесь N1 або майбутній публічний JLPT App не оголошено завершеним.
''')
p=ROOT/'completion/BACKLOG.md';s=p.read_text().replace('Поточний HTML — v138;','Поточний HTML — v139;')
for id,line in [('C05','| C05 | 2 | **done** — 526 кандидатів переглянуто у v139 | 237 точних форм, 1 новий приклад 網, 288 збережень; 8089 scan: 0 unmarked, 289 коректних однознакових результатів, 238 адресних змін. 5004 генерації/1090 показів; completion/C05-result.json, audit139/adjudications.json. Вузький авторський перегляд цільових меж, не повних карток/C11 і не правове очищення. |'),('C06','| C06 | 2 | **done** — 恵み ID716 у v139 | Виправлено заголовок/категорію/usage; ID, читання めぐみ й прогрес збережені. Справжній v138 backup → v139 import/reload/card/comparison, completion/C06-result.json, audit139/identity-results.json. Власні CSV-словники не мігруються автоматично. |')]:
 a=s.index('| '+id+' |');b=s.index('\n',a);s=s[:a]+line+s[b:]
p.write_text(s)
p=ROOT/'completion/README.md';s=p.read_text();prefix='**Поточне доповнення:**'
a=s.index(prefix);b=s.index('\n\n',a);s=s[:a]+'''**Поточне доповнення:** C04 закрито у v137; C05/C06 — у v139. Нові докази C05-result.json, C06-result.json та audit139/. Історичні baseline/target-diagnostics/target-triage за v135/v136 не переписані: поточний scan має 0 unmarked і 289 коректних однознакових результатів. Нова стратегія 4.11 — [strategy/README.md](../strategy/README.md); вона не запускає перебудову бази/алгоритмів.''' +s[b:];p.write_text(s)
(ROOT/'PROJECT_STATUS.md').write_text(f'''# PROJECT_STATUS.md — JLPT N1

Оновлено 4 листопада 2026, Asia/Tokyo. Актуальна **v139**, наступна основа — повний v139.

## Файли й точний стан

`JLPT_N1_ukrainian_reading_v139.html`, {html.stat().st_size} байтів, SHA-256 `{expected}`; аудит `JLPT_N1_v139_audit.md`, відтворення audit139/README.md. Основа v138 SHA-256 `6f7ea6a3d4ca30e8a9cc6ffad31994d99e925809fa4d4b94fe2bf28349027dfc`. Попередні повні версії збережено.

3914 слів/130 конструкцій, 99 середніх/61 довгий =160 текстів, 381 питання читання. 859 лексичних/92 граматичні/41 антонімічна пара, змін/доданих пар 0. Нових текстів немає; до чинної межі 120/80 залишок 21/19.

## Закритий пакет v139

C05: усі 526 цільових кандидатів розглянуто поіменно — 237 адресних форм, 1 новий приклад 網, 288 збережень. Скан 8089: 0 unmarked, 289 коректних однознакових результатів. C06: звичайний заголовок 恵み ID716 з незмінними ID/читанням/прогресом; перевірено перенесення справжнього backup v138. 10 нових контекстних наборів g120/123/124/125/127. C04 збережено без змін. Це вузький авторський перегляд меж/контекстів, не повна нова перевірка всіх полів 160 карток.

Пройдено інваріанти/синтаксис, 5004 генерації/1090 показів на 360/412/1280px, POS/навігацію/порівняння, backup/import/reload, повну сесію та 12 сценаріїв 比較. Звіти прив’язані до SHA. Робочий checkpoint work/v139-checkpoint відокремлено від релізу. Фізичні пристрої не тестувалися.

## Нова стратегія й документи

[Стратегічний пакет](strategy/README.md), [знімок](strategy/STATE_SNAPSHOT.md), [походження/ризики](strategy/PROVENANCE_REVIEW.md), [класифікація](strategy/CLASSIFICATION_ROADMAP.md), [методологія](strategy/LEARNING_METHODOLOGY.md). Кінцева мета — незалежний публічний JLPT App N5–N1. Зараз — завершити наскрізний аудит чинних 3914/130, без масового перенесення/додавання/видалення або зміни алгоритмів/UI. Майбутні 4000+/150+ — орієнтири після аудиту й архітектурного погодження.

Попередній provenance-облік 14198 одиниць не є юридичним очищенням; початкові матеріали книги потребують поелементного з’ясування. Старий користувацький дозвіл не замінює права правовласника. Методологія відділяє наукові дані від пропозицій і фактичного коду: календарного SRS зараз немає, S/G/X — простіша черга. Повна звірка аудіо/транскрипції відео ще відкрита; незалежні дослідження перевірені окремо. Реалізацію нових механізмів не розпочато.

## Залишок і наступний крок

- C07: 先日230/3890 — ролі/дублювання зі збереженням ID, потім C11 автоматичних meaning/reading/cloze і альтернатив. C18 — повний редакторський перегляд структури/POS/пунктуації; значення にたえない57/85 перевіряти незалежно від номера в книзі.
- Звірка історичних доказів у завершальному реєстрі: 5842 позиції, зараховано 60 авторських перевірок v135; 5782 pending — це не заперечення минулого аудиту. C04/C05 не зараховують цілі картки автоматично.
- Незалежний наскрізний мовний аудит; старі 23 довгі/69 питань і карта 46 початкових читань. Усі 381 питань і автоматичні альтернативи потребують приймальних доказів у своїх межах.
- Практичний смартфон/ПК, шрифти й file://. Незавершена сесія після reload не відновлюється; завершений прогрес зберігається. Інтегроване читання випадкове, збіг із усіма цілями сесії не гарантований.
- C20 походження/правові ризики та C21 поглиблення методології ведуться супровідно; широкий публічний продукт має окремий критерій готовності. Без автоматичної перебудови, дозволів від імені правовласників або видалення історії.

Чинні completion/PLAN.md і BACKLOG.md; попередні baseline/triage не переписані. Продовжувати великими якісними партіями, зараховувати перевірені докази без обнулення й не заявляти весь проєкт завершеним. Публікація кожного випуску — повний HTML/аудит у main зі звіркою Git blob SHA.
''')
p=ROOT/'README.md';old=p.read_text();history=old[old.index('Нижче збережено історичний журнал'):]
p.write_text(f'''# JLPT N1 — тренажер з японським інтерфейсом

**Актуальна v139:** [повний HTML](JLPT_N1_ukrainian_reading_v139.html) · [аудит](JLPT_N1_v139_audit.md).

Виправлено обрізані форми в прикладах і виділення граматики, 恵み зі збереженням ID/прогресу, додано 10 контекстних наборів. C05/C06 закриті у вузькому зазначеному обсязі. Збережено типографіку 比較 v138, POS-фільтр і гортання. 3914 слів, 130 конструкцій, **160 текстів і 381 питання читання**.

[Нова стратегія JLPT App N5–N1](strategy/README.md) · [Методологія ефективного навчання JLPT](strategy/LEARNING_METHODOLOGY.md) · [Походження й ризики](strategy/PROVENANCE_REVIEW.md) · [Майбутня класифікація](strategy/CLASSIFICATION_ROADMAP.md). Це підготовчі документи; масової перебудови/перенесення бази або нових алгоритмів немає. Поточний наскрізний аудит N1 триває.

[План](completion/PLAN.md) · [Backlog](completion/BACKLOG.md) · [Стан](PROJECT_STATUS.md) · [Відтворення](audit139/README.md). SHA-256: `{expected}`. Межа читання 120/80, залишок 21/19. Попередні [v138](JLPT_N1_ukrainian_reading_v138.html), [v137](JLPT_N1_ukrainian_reading_v137.html), [v128](JLPT_N1_ukrainian_reading_v128.html) збережено. Перед відкриттям іншого HTML зробіть резервну копію прогресу в 設定.

'''+history)
print(json.dumps(dict(version=139,sha256=expected,bytes=html.stat().st_size)))
