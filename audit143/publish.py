"""Gate complete v143 publication; keep all historical evidence and register credits."""
from pathlib import Path
import json,hashlib,shutil,re
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit143';html=ROOT/'release143/JLPT_N1_ukrainian_reading_v143.html';summary=json.loads((P/'build-summary.json').read_text());sha=hashlib.sha256(html.read_bytes()).hexdigest()
assert sha==summary['sha256']=='028c8ffc1f03bef57c9a833a86553eaee977678bb596526bfaab04cfa6a867f4'
r={n:json.loads((P/f'{n}-results.json').read_text())for n in ['invariant','meaning','presentation','ui','functional','session','comparison','grammar','scope']}
assert all(x['sha256']==sha for x in r.values())
assert len(r['invariant']['checks'])==22 and all(x['pass_']for x in r['invariant']['checks']) and r['invariant']['previousFilesChecked']==406
assert r['meaning']['pass'] and r['meaning']['generationCases']==2668 and r['meaning']['renderedCases']==2001
assert all(x['pass']for x in r['meaning']['generated']+r['meaning']['rendered']) and not r['meaning']['errors']
assert len(r['meaning']['unknownContextGuard'])==73 and all(x['unknownNote']==''and x['headwordNote']for x in r['meaning']['unknownContextGuard'])
assert all(len(r[n]['results'])==3 and all(x['pass']for x in r[n]['results'])for n in ['presentation','functional'])
assert len(r['ui']['checks'])==3 and all(all(v for k,v in x.items()if k!='width')for x in r['ui']['checks'])
assert r['session']['pass'] and len(r['comparison']['results'])==12 and all(x['pass']for x in r['comparison']['results'])
assert r['grammar']['pass'] and len(r['grammar']['results'])==12 and all(x['pass']for x in r['grammar']['results'])
assert r['scope']['pass'] and len(r['scope']['automaticGrammarIds'])==46 and r['scope']['firstGrammarCases']==130 and r['scope']['guardedReadingPools']==1482 and r['scope']['guardedIdsAndCandidateCountsUnchanged']
review=json.loads((P/'editorial-review.json').read_text());assert review['sha256']==sha and review['sets']==51 and review['contexts']==102 and review['newPayloads']==98 and review['retainedExactC04Contexts']==4 and not review['independentReview']
ids=[int(x['key'][2:])for x in review['rows']];prior=json.loads((ROOT/'review20261105/grammar-findings.json').read_text());previous=json.loads((ROOT/'completion/C11-grammar-v142-result.json').read_text());flagged=[x for x in prior['cases']if x['status']=='revision_needed'];assert len(flagged)==67 and set(ids)=={int(x.split(':')[1])for x in previous['remainingPriorFlaggedCases']}
fixed=[]
for row in review['rows']:
 old=next(x for x in flagged if x['id']==int(row['key'][2:]));c=row['contexts'][0]
 assert hashlib.sha256(c['sentence'].encode()).hexdigest()==old['sentenceSha256']
 fixed.append(dict(caseId=old['caseId'],id=old['id'],previousFlags=old['flags'],status='replaced_with_author_reviewed_context_set',resolvedIn=143,sentenceSha256=old['sentenceSha256'],newPayloadSha256=c['payloadSha256'],evidence=f"audit143/editorial-review.json:{row['key']}:e0",fullCardCredit=False))
all_fixed=previous['fixedCases']+fixed;assert len(all_fixed)==len({x['caseId']for x in all_fixed})==67
result=dict(version=143,sha256=sha,reviewType='author_editorial_review',independentReview=False,newGrammarSets=51,contexts=102,newPayloads=98,retainedExactC04Contexts=4,firstExampleFindingsResolvedThisVersion=51,previousResolvedVersion142=16,cumulativeResolvedPriorCases=67,remainingPriorFlaggedCount=0,remainingPriorFlaggedCases=[],fixedCases=all_fixed,C11Overall='in_progress',automaticFirstExampleGrammarIds=r['scope']['automaticGrammarIds'],automaticFirstExampleGrammarCases=46,previousNoIssueFoundInOneDraw=63,warning='Only the 67 known diagnostic cases are resolved by author review. The old 63 observations and current 46 automatic routes do not accept all grammar, all meanings, all draws, or full cards.',registerReviewed=325,registerPending=5517,newRegisterCredits=0,newFullCardCredits=0,generationCases=2668,renderedCases=2001,priorEvidence='completion/C11-grammar-v142-result.json',sources='audit143/sources.md')
(ROOT/'completion/C11-grammar-v143-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
provenance=dict(version=143,sha256=sha,status='not_cleared_for_public_product',inheritedFrom='Full v142 / '+summary['baseSha256'],newMaterial='98 original context-bound quiz payloads (98 keys, 294 wrong alternatives, 98 Ukrainian notes) for 51 existing grammar IDs; no sentence or card definition changes.',newQuizKeys=summary['newGrammarKeys'],retainedExactC04=[dict(id=i,exampleIndex=1,origin='Inherited exact C04 quiz, forms and precedence unchanged')for i in [18,26,92,108]],fieldSources='audit143/author.py and audit143/sources.md',inheritedMaterial='Examples, translations, prior sets, C04 content and all older material retain their provenance uncertainty; author review is not rights clearance.',publicExposure='Full v143 and audit sources added to public main; work/v143-checkpoint preserves an unfinished draft. Historical main HTML, branches, reachable history and Actions artifacts remain in scope of the separate rights audit.',historicalInventory='review20261105/public-inventory.json is a frozen v141 snapshot, not current v143 counts.',actionsArtifacts='No upload-artifact step in v143 publisher; old ZIP contents not checked.',visibilityOrHistoryRewrite=False,changedPairs=0,changedCardFields={},independentReview=False)
(P/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
shutil.copyfile(html,ROOT/html.name)
(ROOT/'JLPT_N1_v143_audit.md').write_text(f'''# Аудит JLPT N1 v143 — 5 листопада 2026, Asia/Tokyo

Повний `{html.name}`, {html.stat().st_size} байтів; SHA-256 `{sha}`. Основа — повний v142, release commit 8c83d4003a7d4516f617a236268cc094c232996a, SHA-256 {summary['baseSha256']}. Старі версії збережено. Незавершений checkpoint work/v143-checkpoint / 2a809bd3bb400f47c2aacc319a79ba67ace3b84c містив попередні чернетки, зокрема чотири згодом відхилені дублікати C04; це не готовий випуск.

## Авторський змістовий перегляд C11

**51 граматична картка, обидва приклади кожної — 102 контексти.** Точні ID: {', '.join('g'+str(i)for i in ids)}. В кожному контексті прочитано правильну відповідь, усі три альтернативи й пояснення. [editorial-review.json](audit143/editorial-review.json) містить речення, джерело виклику, значення, варіанти, примітки та payload-хеші. [author.py](audit143/author.py) — оригінальні редакторські дані; [sources.md](audit143/sources.md) — фактична словникова/зовнішня звірка й межі.

Написано **98 нових payload**: 51 базовий +47 точних byExample. У **чотирьох** других контекстах g18/g26/g92/g108 вже діють C04-набори; вони повторно прочитані та **збережені без змін** разом із формами й пріоритетом. Новий byExample не створює їхнього прихованого дубліката. Отже, це не 102 нові набори й не повторне зарахування старого C04.

Ключові розмежування:

- g2/g6/g7/g12: незмінний результат за альтернатив; відсутність винятку; марність спроби; стримувальний вплив соціального становища чи попередньої заяви.
- g17/g18/g21/g25/g26/g31: уявлення замість фактичної події, готовність діяти замість уже виконаного, особлива риса, зведення заходів нанівець, важко зупинний наслідок і крайній приклад. «夢にだに» не прочитано як буквальний нічний сон. かねない не перетворено на гарантовану втрату коштів.
- g39–g48: мета, відсутність шансів, заборона, негідність ролі, контраст, зовнішній примус і подолання перешкоди. Прибрано сторонні довідкові варіанти/посилання.
- g52/g54/g55/g58/g60/g67/g69/g73/g78/g82: сильне почуття, ступінь або пріоритет, риторичне твердження, повтор, поєднання нагоди, необхідна умова, умовне попередження, ігнорування реакції та бажаний вибір. Для に越したことはない немає двох однакових «не потрібно» дистракторів; бажане не оголошено обов’язковим.
- g87–g99: нижча вимога, обережне допущення, сильний вплив, відповідальність, прагнення знайти вихід, образне зіставлення й нормативна оцінка. Формальні заперечення не підміняють конкретного значення.
- g103–g129: гідність оцінки, суцільність/колір/бруд, поєднання чинників, урахування основи, проходження процесу, привід, незалежність від альтернатив, ненавмисність, вибір способу, повтор і敬語. Не додано причини зняття взуття, якої не було в реченні; не встановлено, хто підготував місця або матеріали.

Це **авторський мовний перегляд**, не незалежна експертиза. Успішне тестування не вимірює складність для реальних учнів і саме по собі не доводить семантичної якості.

## Обсяг змін і збереження

Змінено лише JSON `REVIEWED_MEANING_QUIZZES` та номер версії. Додано 51 запис: JSON **332**, runtime **333** із незмінним g95; byExample **220**. Усі 281 попередні JSON-набори збережено, включно з 265 лексичними й 16 граматичними v142; inline g95 та весь REVIEWED_EXAMPLE_TARGETS незмінні. Жодного поля карток, прикладу чи перекладу не змінено. Нових/змінених порівнянь **0**, перелік порожній; 859/92/41 пар збережені.

База незмінна: **3914 слів, 130 конструкцій, 160 текстів (99/61), 381 питання читання**; ID, POS, читання, aliases, сховище, прогрес, UI, алгоритм і CSS збережені. [baseline-integrity.json](audit143/baseline-integrity.json) перевіряє Git blob-хеші **406** попередніх файлів, зокрема всі старі HTML, аудити й реєстри; виняток — три поточні документи README/PROJECT_STATUS/BACKLOG, які оновлюються випуском.

## Технічні й браузерні докази

- **22 групи інваріантів**, точний дозволений diff і JS-синтаксис. Змістові рішення відділені від перевірки структури.
- **2668 генерацій**: 667 контекстів ×4 позиції правильної відповіді. Це 530 незмінних лексичних, 33 граматичні v142, 102 цієї партії та 2 g95. Зіставлено точні речення, варіанти, ключі, пояснення й фактичне виділення. Контроль випадковості — лише в тесті.
- **2001 фактичний показ із хибною відповіддю й поясненням**: ті самі 667 контекстів ×360/412/1280px. По одному правильному/хибному маркеру, видимі примітки, без горизонтального переповнення та помилок JS. **73** негативні перевірки невідомого контексту: шість словникових +67 граматичних наборів.
- Окремо відтворено перші приклади всіх **130** граматичних записів, seed 20261105: **68 saved /16 exact C04 /46 automatic**. Для автоматичних 46 це лише технічний облік маршруту/формату, не мовне приймання. Збережено **1482** відсіяні reading-ID та кожну кількість альтернатив, **2432** допустимі пули; не заявлено мовної придатності кожного.
- Повторно пройдено POS/пошук/фільтри/гортання/клавіші/свайпи, backup/import/reload, повну сесію ({r['session']['pages']} сторінок, {r['session']['answers']} відповідей, {r['session']['graded']} оцінок), 12 сценаріїв теми/масштабу 比較 та 12 показів незмінних карток попереднього випуску. Chromium {r['meaning']['browser']}, Linux. Візуально оглянуто g18/g54/g112 та g17/g82/g128/g129 з японським шрифтом. Фізичні Android/Windows не тестувалися.

Усі дев’ять `audit143/*-results.json` прив’язані до точного SHA цього HTML. Сканер маршрутів не названо новим мовним аудитом 130 карток.

## Прогрес і залишок

[Окремий результат](completion/C11-grammar-v143-result.json): **51** раніше відкрите перше питання замінено; разом із **16** v142 — усі **67** зауважень історичного знімка опрацьовані в їхніх конкретних межах. Історичні 63 «без знайденої проблеми» не перетворені на приймання всіх генерацій. Нові другі контексти враховано окремо; чотири C04 не зараховано вдруге.

**C11 загалом лишається in_progress.** Наступна ділянка — 46 граматичних перших прикладів, які досі мають automatic-маршрут, та інші не охоплені контексти C04-карток; їхні точні ID в scope-results.json. Далі автоматичні лексичні meaning, reading-пули й однозначність cloze. Не оголошено закритими повні картки, усі значення, довільні приклади або випадкові draw.

Реєстр completion/review-register.csv **не змінений**: **325 reviewed /5517 pending із 5842 різнорідних позицій**, нових повнокарткових кредитів 0. Попередні докази збережено. C07/C08/C09/C10/C18, решта 40 текстів, C16 фізичне приймання й походження/правова придатність відкриті. Пропозицію для 1482 не впроваджено, Learning Engine/N5–N1 не перебудовано. [Походження змін](audit143/provenance.json) не очищає старих публічних копій; нічого не видалено й історію не переписано.

[Відтворення](audit143/README.md). Наступна повна основа — v143.
''')
p=ROOT/'PROJECT_STATUS.md';s=p.read_text();s=re.sub(r'Оновлено 5 листопада 2026, Asia/Tokyo\..*?\n\n3914',f'Оновлено 5 листопада 2026, Asia/Tokyo. Актуальна **v143**. Повний `{html.name}`, {html.stat().st_size} байтів; SHA-256 `{sha}`. Аудит JLPT_N1_v143_audit.md, відтворення audit143/README.md. Основа — v142 / commit 8c83d4003a7d4516f617a236268cc094c232996a. Старі випуски збережено.\n\n3914',s,count=1,flags=re.S)
section=f'''## Виконано у v143 — решта 51 зауваження C11

Авторський перегляд 51 граматичної картки /102 контекстів: 98 нових payload, 4 точні C04-другі приклади (g18/g26/g92/g108) збережені. Додано 51 REVIEWED_MEANING_QUIZZES і 47 byExample; разом runtime 333, byExample 220. Значення всіх карток, приклади, переклади, 281 попередній JSON-набір, C04, ID, прогрес, UI та алгоритм незмінні. Це не незалежна експертиза.

22 інваріанти; 406 попередніх файлів за Git blob-хешами; 2668 генерацій /2001 показ (667 контекстів); 73 перевірки невідомих контекстів; backup/import/reload, повна сесія й 比較 пройдені. Технічний облік 130 перших граматичних питань: 68 saved /16 exact C04 /46 automatic. Reading-фільтр зберіг ті самі 1482 ID та кількості альтернатив. Linux Chromium не закриває фізичний Android/Windows.

Опрацьовано решту 51 із конкретних 67 зауважень review20261105; 16 виправлень v142 збережено. Докази — completion/C11-grammar-v143-result.json, audit143/editorial-review.json. **C11 загалом відкрито**: наступні 46 automatic-перших прикладів і неохоплені контексти C04, потім інші automatic meaning/reading/cloze. Поіменний технічний залишок — audit143/scope-results.json; 63 старі спостереження не названі повним прийманням. Приймальний реєстр лишається 325 reviewed /5517 pending; жодну повну картку автоматично не зараховано. Наступна основа — повний v143.

'''
if '## Виконано у v143' in s:s=s.split('## Виконано у v143',1)[0]+'## Виконано у v142'+s.split('## Виконано у v142',1)[1]
s=s.replace('## Виконано у v142',section+'## Виконано у v142',1)
s=s.replace('[Ризики наявного поширення](strategy/PUBLISHED_HTML_RISK_REVIEW.md): 23 HTML','[Історичний знімок ризиків v141](strategy/PUBLISHED_HTML_RISK_REVIEW.md): 23 HTML')
p.write_text(s)
p=ROOT/'completion/BACKLOG.md';s=p.read_text().replace('Поточний HTML — v142','Поточний HTML — v143');start=s.index('| C11 |');end=s.index('\n',start)
s=s[:start]+'| C11 | 2 | **in_progress** — v141/v142/v143, авторські набори | v141: усі 265 збережених лексичних наборів /530 контекстів; v142: 16 граматичних /33 контексти; v143: решта 51 діагностичний випадок /102 контексти (98 нових payload +4 незмінні C04). Разом 67 конкретних зауважень знімка review20261105 опрацьовані, історію не переписано. 2668 генерацій/2001 показ; completion/C11-grammar-v143-result.json, audit143/editorial-review.json. **Залишок:** 46 automatic-перших граматичних питань та неохоплені контексти C04; інші automatic meaning/reading/cloze. scope-results.json — технічні ID, не мовне приймання. Повні картки не зараховано, 325/5517 збережено; фізичне й незалежне мовне приймання окремо. |'+s[end:];p.write_text(s)
p=ROOT/'README.md';s=p.read_text();history=s[s.index('Нижче збережено історичний журнал'):]
p.write_text(f'''# JLPT N1 — тренажер з японським інтерфейсом

**Актуальна v143:** [повний HTML](JLPT_N1_ukrainian_reading_v143.html) · [аудит](JLPT_N1_v143_audit.md).

Опрацьовано решту 51 позначеного граматичного питання та обидва приклади відповідних карток: 102 контексти, 98 нових наборів варіантів і 4 збережені C04. Розмежовано намір/факт, можливий/неминучий наслідок, рекомендацію/обов’язок, образне значення/буквальне прочитання. Попередні набори, картки, ID, прогрес та інтерфейс збережені.

3914 слів, 130 конструкцій, 160 текстів, 381 питання читання. Аудит C11 ще триває: 67 відомих зауважень опрацьовані у v142–v143, але інші автоматичні набори потребують перегляду. Звіти й межі — PROJECT_STATUS.md та audit143/. SHA-256 `{sha}`.

[Пропозиція для 1482 записів](strategy/READING_ASSESSMENT_PROPOSAL.md) · [фізичний Android/Windows-план](completion/PHYSICAL_DEVICE_TEST_PLAN.md) · [ризики вже опублікованих HTML](strategy/PUBLISHED_HTML_RISK_REVIEW.md). Нові навчальні механізми не впроваджені; фізичне, незалежне мовне та правове приймання не завершені.

Попередні [v142](JLPT_N1_ukrainian_reading_v142.html), [v141](JLPT_N1_ukrainian_reading_v141.html), [v128](JLPT_N1_ukrainian_reading_v128.html) збережено. Перед відкриттям іншого HTML зробіть резервну копію прогресу в 設定.

'''+history)
print(json.dumps(dict(version=143,sha256=sha,bytes=html.stat().st_size,newSets=51,contexts=102,priorDiagnosticCasesResolved=67,C11Overall='in_progress',registerUnchanged=True)))
