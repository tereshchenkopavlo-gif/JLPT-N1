"""Release only after all SHA-bound technical gates. Never credits whole cards."""
from pathlib import Path
import json,hashlib,shutil,csv,re
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit142';html=ROOT/'release142/JLPT_N1_ukrainian_reading_v142.html';summary=json.loads((P/'build-summary.json').read_text());sha=hashlib.sha256(html.read_bytes()).hexdigest()
assert sha==summary['sha256']=='b2064d5a6201bfea593b9a131e56b38ed44347bf74ba820b769120bfc04e57be'
r={n:json.loads((P/f'{n}-results.json').read_text())for n in ['invariant','meaning','presentation','ui','functional','session','comparison','grammar']}
assert all(x['sha256']==sha for x in r.values())
assert len(r['invariant']['checks'])==20 and all(x['pass_']for x in r['invariant']['checks'])
assert r['meaning']['pass'] and r['meaning']['generationCases']==2260 and r['meaning']['renderedCases']==1695
assert all(x['pass']for x in r['meaning']['generated']+r['meaning']['rendered']) and not r['meaning']['errors']
assert all(x['unknownNote']==''and x['headwordNote']for x in r['meaning']['unknownContextGuard'])
assert all(len(r[n]['results'])==3 and all(x['pass']for x in r[n]['results'])for n in ['presentation','functional'])
assert len(r['ui']['checks'])==3 and all(all(v for k,v in x.items()if k!='width')for x in r['ui']['checks'])
assert r['session']['pass'] and len(r['comparison']['results'])==12 and all(x['pass']for x in r['comparison']['results'])
assert r['grammar']['pass'] and len(r['grammar']['results'])==12 and all(x['pass']for x in r['grammar']['results'])
review=json.loads((P/'editorial-review.json').read_text());assert review['sha256']==sha and review['sets']==16 and review['contexts']==33 and not review['independentReview']
ids=[int(x['key'][2:])for x in review['rows']];prior=json.loads((ROOT/'review20261105/grammar-findings.json').read_text());flagged=[x for x in prior['cases']if x['status']=='revision_needed'];assert len(flagged)==67 and set(ids)<={x['id']for x in flagged}
fixed=[]
for row in review['rows']:
 old=next(x for x in flagged if x['id']==int(row['key'][2:]));c=row['contexts'][0]
 assert hashlib.sha256(c['sentence'].encode()).hexdigest()==old['sentenceSha256']
 fixed.append(dict(caseId=old['caseId'],id=old['id'],previousFlags=old['flags'],previousStatus=old['status'],status='replaced_with_author_reviewed_context_set',sentenceSha256=old['sentenceSha256'],newPayloadSha256=c['payloadSha256'],evidence=f"audit142/editorial-review.json:{row['key']}:e0",fullCardCredit=False))
remaining=[x['caseId']for x in flagged if x['id']not in ids];assert len(remaining)==51
result=dict(version=142,sha256=sha,reviewType='author_editorial_review',independentReview=False,newGrammarSets=16,contexts=33,firstExampleFindingsResolved=16,fixedCases=fixed,remainingPriorFlaggedCases=remaining,remainingPriorFlaggedCount=51,previousNoIssueFoundInOneDraw=63,warning='Historical one-draw observations are not full linguistic acceptance. Other draws/unreviewed examples still need audit.',previousQuizEvidence='completion/C11-saved-sets-result.json',registerReviewed=325,registerPending=5517,newFullCardCredits=0,newRegisterCredits=0,generationCases=2260,renderedCases=1695)
(ROOT/'completion/C11-grammar-v142-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
provenance=dict(version=142,sha256=sha,status='not_cleared_for_public_product',inheritedFrom='Full v141, SHA-256 '+summary['baseSha256'],newMaterial='Original project question options and Ukrainian notes for 33 inherited sentences; five revised definition fields on four cards.',newQuizKeys=summary['newGrammarKeys'],changedCardFields=summary['changedCardFields'],fieldSources='audit142/author.py; audit142/sources.md',inheritedSentences='Unchanged; origin uncertainty retained. No claim of rights clearance through rewriting.',publicExposure='This release adds the complete v142 HTML and audit sources on main. Existing public main files, other branches, reachable history and Actions artifacts remain subject to strategy/PUBLISHED_HTML_RISK_REVIEW.md. Its frozen v141 inventory is historical, not a current v142 count.',historicalInventory='review20261105/public-inventory.json',actionsArtifacts='No upload-artifact step in v142 workflow; old ZIP contents have not been checked.',visibilityOrHistoryChanges=False,reviewType='author_editorial_review',independentReview=False,changedPairs=0)
(P/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
shutil.copyfile(html,ROOT/html.name)
(ROOT/'JLPT_N1_v142_audit.md').write_text(f'''# Аудит JLPT N1 v142 — 5 листопада 2026, Asia/Tokyo

Повний `{html.name}`, {html.stat().st_size} байтів; SHA-256 `{sha}`. Основа — v141 / release commit 571aa092d256e682ad16873b7462dcc263cf62d8, SHA-256 {summary['baseSha256']}; уточнення плану за main 63e95bbe950855cd21edcb2591296101d5a1d3cf. Старі випуски збережено. Незавершений checkpoint: work/v142-checkpoint / 83352684266b85a43f010fe239acf9895e9b88fd; він не є готовим HTML і містить ранню редакцію одного дистрактора g11.

## Змістовий обсяг C11

**16 граматичних записів, 33 чинні приклади:** g8 とあって, g9 ばこそ, g10 ゆえ, g11 こととて, g27 を限りに, g28 に至るまで, g41 べくして, g61 が早いか, g62 なり, g63 ながら, g72 ならいざしらず, g89 ずじまい, g96 にして, g107 からある・からいる・からする, g126 召し上がる, g130 その節は. Для g107 перевірено всі **три** приклади; для решти — обидва. У кожному наборі прочитано ключ, усі три альтернативи й українську примітку. [Точні речення, рішення й payload-хеші](audit142/editorial-review.json); [авторські дані](audit142/author.py); [фактичні джерела та межі](audit142/sources.md).

Це **авторський мовний перегляд**, не незалежна експертиза. Варіанти описують несумісні прочитання тієї самої ситуації: причина/наслідок/мета, початок/кінець/строк рішення, негайна/попередня/відкладена дія, поступка/одночасність, невиконання/виконання, вік/поєднання ролей, кількість/поріг, шаноблива/власна скромна дія, минула/майбутня/поточна нагода. Не використано близький правильний парафраз як безумовно хибний. У варіантах немає назв перевірюваних форм, посилань чи довідкових правил. Емпірична складність і діагностична сила для реальних учнів ще не виміряні.

Додано 16 наборів у чинний REVIEWED_MEANING_QUIZZES і 17 byExample-відгалужень, **без зміни алгоритму**. Разом JSON має 281 набір; runtime — 282 з раніше наявним g95; byExample — 173. Усі 265 лексичних наборів v141 збережені. Точні C04-відповідності мають попередній пріоритет. Невідомі сторонні речення не отримують нових контекстних приміток автоматично.

## Визначення карток — п’ять полів

| ID | Поле | Уточнення |
|---|---|---|
| g28 | m | Охоплення до межі включно; не вимагає «екстремального» кінцевого елемента. |
| g72 | m | Перший випадок залишено осторонь; без безумовного схвалення. |
| g89 | m | Дія так і не відбулася; реальна активна спроба не обов’язкова. |
| g130 | m, t | Часова відсилка, а не вся подяка. Обидва приклади про минуле; інші контексти можуть бути про майбутнє. |

Приклади, їхні переклади, усі інші поля карток і читання незмінні. Змінених/нових порівнянь **0**, перелік порожній; збережено 859/92/41 пар. Обсяг незмінний: 3914 слів, 130 конструкцій, 99 середніх/61 довгий =160 текстів, 381 питання читання. ID, ключі й формат прогресу збережені.

## Технічні докази

- **20 груп інваріантів**, JS-синтаксис і точний дозволений diff. Увесь runtime, UI, CSS і зберігання байтово незмінні, крім номера версії; змінено лише два JSON-поля даних.
- **2260 генерацій**: 565 контекстів ×4 позиції ключа. З них 33 нові граматичні, 530 раніше прийнятих лексичних і 2 незмінні g95. Перевірено точні речення, варіанти, ключі й примітки; керування випадковістю є лише в тесті.
- **1695 фактичних показів із хибною відповіддю й поясненням**: ті самі 565 контекстів ×360/412/1280px; рівно один правильний/хибний маркер, видима примітка, без горизонтального переповнення та помилок JS.
- Чотири змінені картки показано на трьох ширинах: 12 сценаріїв. Збережено перевірки POS, гортання/клавіш/свайпів, пошуку/фільтрів, порівняння, backup/import/reload. Повна сесія: {r['session']['pages']} сторінок, {r['session']['answers']} відповідей, {r['session']['graded']} оцінок. Типографіка 比較 — 12 сценаріїв теми/масштабу. Chromium {r['meaning']['browser']}, Linux; фактичне Android/Windows-приймання не виконано.

Автоматичний PASS доводить технічну відповідність авторським даним, а не семантичну якість сам по собі. Звіти `audit142/*-results.json` прив’язані до точного SHA повного HTML. Візуально оглянуто приклади g63/g107/g130 і картку g130 з японським шрифтом.

## Залишок і незмінні обмеження

[Окремий результат C11](completion/C11-grammar-v142-result.json) посилається на 16 точних перших випадків із review20261105, замінених новими авторськими наборами; з **67** позначених випадків **51** залишається відкритим. Старі 63 «без знайденої проблеми» стосувалися лише конкретного draw v141, не всіх наступних генерацій. Історичний звіт не переписано. Нові другі/третій контексти зафіксовано додатково.

Приймальний реєстр лишається **325 reviewed /5517 pending із 5842 різнорідних позицій**: жодної повної картки автоматично не зараховано й знаменник не збільшено. C11 загалом відкрито: решта граматичних колізій, інші автоматичні meaning-питання, reading-пули й семантична однозначність cloze. C07/C08/C09/C10/C18 та решта 40 текстів також не закриті.

Пропозиція для 1482 записів не впроваджена, Learning Engine/N5–N1 не перебудовано. [Фізичний план](completion/PHYSICAL_DEVICE_TEST_PLAN.md) залишається невиконаним. [Походження змін](audit142/provenance.json) не очищає успадкованих чи раніше опублікованих матеріалів; реєстр публічних ризиків v141 лишається історичним знімком. Нічого не видалено, видимість та історію не змінено.

Наступна ділянка C11: решта причинних/обмежувальних колізій g2/g6/g7/g12/g17/g18/g21/g25/g26, далі довідкові підказки й дублікати дистракторів за 51 case ID. [Відтворення](audit142/README.md).
''')
p=ROOT/'PROJECT_STATUS.md';s=p.read_text();s=s.replace('Актуальна **v141** (HTML опубліковано 4 листопада; у цій партії не змінений). Повний `JLPT_N1_ukrainian_reading_v141.html`, 6784138 байтів; SHA-256 `08e016a95f1786f243c29f54289edf5dd65aac4c43c9ff863b25c9f0422f75a3`. Аудит JLPT_N1_v141_audit.md, відтворення audit141/README.md. Основа v140 / commit c82e3b18361a6396969220f385760cffff4c8ed4.',f'Актуальна **v142**. Повний `{html.name}`, {html.stat().st_size} байтів; SHA-256 `{sha}`. Аудит JLPT_N1_v142_audit.md, відтворення audit142/README.md. Основа — v141; попередній main 63e95bbe950855cd21edcb2591296101d5a1d3cf.')
s=re.sub(r'Оновлено 5 листопада 2026, Asia/Tokyo\..*?\n\n3914',f'Оновлено 5 листопада 2026, Asia/Tokyo. Актуальна **v142**. Повний `{html.name}`, {html.stat().st_size} байтів; SHA-256 `{sha}`. Аудит JLPT_N1_v142_audit.md, відтворення audit142/README.md. Основа — v141; попередній main 63e95bbe950855cd21edcb2591296101d5a1d3cf. Старі випуски збережено.\n\n3914',s,count=1,flags=re.S)
section=f'''## Виконано у v142 — адресний C11

16 нових граматичних meaning-наборів /33 приклади, включно з усіма трьома g107. Точні ID: {', '.join('g'+str(i)for i in ids)}. Причинні та часові парафрази відділено; розділено значення ながら/にして, прибрано назви форм і довідкові підказки з варіантів. П’ять полів визначень g28/g72/g89/g130 уточнено; приклади/переклади, 265 лексичних наборів і всі інші картки збережені. Це авторський перегляд, не незалежна експертиза.

20 інваріантів, JS-синтаксис, 2260 генерацій/1695 показів (565 контекстів), чотири змінені картки на трьох ширинах; backup/import/reload, повна сесія, 12 сценаріїв 比較 пройдено. Це Linux Chromium, не фактичний Android/Windows. Алгоритм, UI, сховище, склад бази та ID незмінні.

Із 67 зауважень знімка review20261105 замінено 16 точних перших випадків; **51 лишається відкритим**. Доказ: completion/C11-grammar-v142-result.json та audit142/editorial-review.json. Повні картки не зараховано: попередні **325 reviewed /5517 pending** у completion/review-register.csv збережені. C11 загалом не закрито. Наступна основа — повний v142; наступні колізії — g2/g6/g7/g12/g17/g18/g21/g25/g26, потім решта підказок/дублікатів.

'''
if '## Виконано у v142' in s:
 s=s.split('## Виконано у v142',1)[0]+'## Виконано у v141'+s.split('## Виконано у v141',1)[1]
s=s.replace('## Виконано у v141',section+'## Виконано у v141',1)
s=s.replace('Шість оригінальних чернеток наступних виправлень не встановлено.','На дату цього історичного знімка шість оригінальних чернеток не були встановлені; v142 замінив їх остаточними наборами серед 16 виправлень, зі звіркою всіх прикладів.')
s=s.replace('Поточний повний HTML і всі попередні звіти збережено; новий номер для документаційної партії не створювався.','Документаційна партія 5.11 зберегла v141 без нового номера; наступний адресний випуск v142 описано вище. Попередні HTML та звіти збережено.')
p.write_text(s)
p=ROOT/'completion/BACKLOG.md';s=p.read_text().replace('Поточний HTML — v141','Поточний HTML — v142');s=s.replace('Шість чернеток не встановлено; повні картки не зараховано.','У v142 встановлено 16 нових наборів /33 контексти; 16 із 67 точних перших випадків замінено, 51 відкритий. П’ять полів g28/g72/g89/g130 уточнено. completion/C11-grammar-v142-result.json, audit142/editorial-review.json; 2260 генерацій/1695 показів. Повні картки не зараховано, 325/5517 збережено.');p.write_text(s)
p=ROOT/'README.md';s=p.read_text();history=s[s.index('Нижче збережено історичний журнал'):]
p.write_text(f'''# JLPT N1 — тренажер з японським інтерфейсом

**Актуальна v142:** [повний HTML](JLPT_N1_ukrainian_reading_v142.html) · [аудит](JLPT_N1_v142_audit.md).

Виправлено C11 для 16 граматичних записів у 33 прикладах: однозначні контекстні відповіді без довідкових підказок. Уточнено визначення に至るまで, ならいざしらず, ずじまい та その節は. Усі 265 раніше перевірених лексичних наборів збережені.

3914 слів, 130 конструкцій, 160 текстів, 381 питання читання. ID, прогрес, оформлення й навчальний механізм збережено. Аудит ще триває: 51 із 67 позначених граматичних випадків лишається відкритим. Звіти й межі — PROJECT_STATUS.md та audit142/. SHA-256 `{sha}`.

[Пропозиція для 1482 записів](strategy/READING_ASSESSMENT_PROPOSAL.md) · [фізичний Android/Windows-план](completion/PHYSICAL_DEVICE_TEST_PLAN.md) · [ризики вже опублікованих HTML](strategy/PUBLISHED_HTML_RISK_REVIEW.md) · [історичний знімок 5.11](review20261105/README.md). Нові механізми не впроваджені; фізичне й правове приймання відкрито.

Попередні [v141](JLPT_N1_ukrainian_reading_v141.html), [v140](JLPT_N1_ukrainian_reading_v140.html), [v128](JLPT_N1_ukrainian_reading_v128.html) збережено. Перед відкриттям іншого HTML зробіть резервну копію прогресу в 設定.

'''+history)
print(json.dumps(dict(version=142,sha256=sha,bytes=html.stat().st_size,newGrammarSets=16,contexts=33,remainingFlagged=51,registerUnchanged=True)))
