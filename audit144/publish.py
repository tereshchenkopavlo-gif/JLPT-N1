"""Gate complete v144 publication and narrow author acceptance of 261 examples."""
from pathlib import Path
import json,hashlib,shutil,re
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit144';html=ROOT/'release144/JLPT_N1_ukrainian_reading_v144.html';summary=json.loads((P/'build-summary.json').read_text());sha=hashlib.sha256(html.read_bytes()).hexdigest()
assert sha==summary['sha256']=='901ce33485bf5d42e928324c54f02d77661dc5d82456680693fb486e372e17d4'
r={n:json.loads((P/f'{n}-results.json').read_text())for n in ['invariant','meaning','presentation','ui','functional','session','comparison','grammar','scope','coverage']}
assert all(x['sha256']==sha for x in r.values())
assert len(r['invariant']['checks'])==23 and all(x['pass_']for x in r['invariant']['checks']) and r['invariant']['previousFilesChecked']==439
assert r['meaning']['pass'] and r['meaning']['generationCases']==3164 and r['meaning']['renderedCases']==2373
assert all(x['pass']for x in r['meaning']['generated']+r['meaning']['rendered']) and not r['meaning']['errors']
assert len(r['meaning']['unknownContextGuard'])==122 and all(x['unknownNote']==''and x['headwordNote']for x in r['meaning']['unknownContextGuard'])
assert all(len(r[n]['results'])==3 and all(x['pass']for x in r[n]['results'])for n in ['presentation','functional'])
assert len(r['ui']['checks'])==3 and all(all(v for k,v in x.items()if k!='width')for x in r['ui']['checks'])
assert r['session']['pass'] and len(r['comparison']['results'])==12 and all(x['pass']for x in r['comparison']['results'])
assert r['grammar']['pass'] and len(r['grammar']['results'])==12 and all(x['pass']for x in r['grammar']['results'])
assert r['scope']['pass'] and not r['scope']['automaticGrammarIds'] and len(r['scope']['savedFirstIds'])==114 and len(r['scope']['exactReviewedFirstIds'])==16
assert r['scope']['guardedReadingPools']==1482 and r['scope']['guardedIdsAndCandidateCountsUnchanged']
assert r['coverage']['pass'] and r['coverage']['grammarCards']==130 and r['coverage']['grammarContexts']==261 and r['coverage']['automaticCurrentContexts']==0 and all(x['pass']for x in r['coverage']['results'])
review=json.loads((P/'editorial-review.json').read_text());catalog=json.loads((P/'grammar-coverage.json').read_text())
assert review['sha256']==catalog['sha256']==sha and review['reviewedCards']==62 and review['sets']==49 and review['contexts']==124 and review['newPayloads']==91 and review['retainedExactContexts']==33
assert catalog['cards']==130 and catalog['contexts']==261 and catalog['routeCounts']=={'saved_set':224,'exact_reviewed':37}and catalog['exactOrigins']=={'C04':27,'C05':10}and not catalog['independentReview']
previous=json.loads((ROOT/'completion/C11-grammar-v143-result.json').read_text());assert previous['cumulativeResolvedPriorCases']==67
result=dict(version=144,sha256=sha,subcriterion='C11-G-current-example-meaning',status='author_review_complete_for_current_examples',C11Overall='in_progress',reviewType='author_editorial_review',independentReview=False,grammarCards=130,currentGrammarExamples=261,currentSavedContexts=224,currentExactContexts=37,exactOrigins={'C04':27,'C05':10},automaticCurrentGrammarContexts=0,newSetCards=49,reviewedCardsThisVersion=62,reviewedContextsThisVersion=124,newPayloads=91,retainedExactContextsThisVersion=33,retainedExactOriginsThisVersion={'C04':23,'C05':10},g95Reread=2,priorDiagnosticCasesResolved=67,priorEvidence='completion/C11-grammar-v143-result.json',catalog='audit144/grammar-coverage.json',warning='Author acceptance concerns meaning questions for exactly the current 261 examples. It does not accept all card fields, grammar senses, comparisons, external sentences or physical devices.',registerReviewed=325,registerPending=5517,newRegisterCredits=0,newFullCardCredits=0,generationCases=3164,renderedCases=2373,remainingC11=['Automatic vocabulary meaning contexts outside saved sets','Linguistic quality of reading alternative pools; alternative proposal for 1482 remains unimplemented','Semantic uniqueness of eligible cloze questions','Controlled handling of custom/unknown contexts'],sources='audit144/sources.md')
(ROOT/'completion/C11-grammar-v144-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
provenance=dict(version=144,sha256=sha,status='not_cleared_for_public_product',inheritedFrom='Full v143 / '+summary['baseSha256'],newMaterial='91 original quiz payloads: 91 correct answers, 273 wrong alternatives, 91 Ukrainian notes. New saved-set keys for 49 existing grammar cards; 42 byExample overrides.',newQuizKeys=summary['newGrammarKeys'],retainedExactContexts=33,retainedOrigins={'C04_v137':23,'C05_v139':10},fieldSources='audit144/author.py; audit144/sources.md',inheritedMaterial='All card examples, translations, definitions, prior sets and exact-target forms remain unchanged and retain provenance uncertainty. Semantic editing and author review do not clear rights.',publicExposure='Complete v144 plus audit sources added to public main; work/v144-checkpoint retains an unfinished draft. Old main HTML, other branches, reachable history and Actions packages remain in the separate rights-audit scope.',historicalInventory='review20261105/public-inventory.json is a frozen v141 snapshot, not current v144 counts.',actionsArtifacts='No upload-artifact step in v144 publisher; old ZIP contents not verified.',visibilityOrHistoryRewrite=False,changedPairs=0,changedCardFields={},independentReview=False)
(P/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
shutil.copyfile(html,ROOT/html.name)
ids=[int(x['key'][2:])for x in review['rows']]
(ROOT/'JLPT_N1_v144_audit.md').write_text(f'''# Аудит JLPT N1 v144 — 5 листопада 2026, Asia/Tokyo

Повний `{html.name}`, {html.stat().st_size} байтів; SHA-256 `{sha}`. Основа — повний v143, release commit 0025ba705060c6afddc193eb9880424203b0e613, SHA-256 {summary['baseSha256']}. Старі версії збережено. Незавершений checkpoint work/v144-checkpoint / 3c917db8d98b6898c5c77948a676a9f82aad03e2 зберігав джерела до браузерної перевірки; у ньому назва exact-маршруту ще не розділяла C04/C05. Це не готовий реліз.

## Авторський обсяг цієї партії

**62 картки /124 контексти**, обидва чинні приклади: {', '.join('g'+str(i)for i in ids)}. Прочитано ключ, усі три альтернативи й пояснення кожного питання. **91 новий payload**, **33 точні набори збережено** після повторного прочитання. Додано **49** ключів REVIEWED_MEANING_QUIZZES і **42** byExample. Сім карток мають один новий та один раніше точний контекст; 13 карток мають лише раніше точні контексти й не отримали зайвого дубліката saved-set. Для g4/g51/g86 базовий payload стосується другого прикладу; перший обслуговує чинний exact-набір.

[editorial-review.json](audit144/editorial-review.json) містить точні речення, варіанти, примітки, походження й причини збереження. [author.py](audit144/author.py) — нові дані, None зберігає exact-контекст. [sources.md](audit144/sources.md) відділяє словникові факти від авторської оцінки.

Збережені **33 =23 C04 +10 C05**. Походження звірено з v137: початковий C04 мав 27 граматичних exact-контекстів. Десять додаткових — обидва приклади g120/g123/g124/g125/g127 з C05/v139. У всьому чинному банку тепер **37 exact =27 C04 +10 C05**. Старі технічні звіти називали весь цей маршрут «C04» як скорочення; історичні файли не переписані, новий реєстр уточнює походження.

## Змістові розмежування

- Поступка, мінімальна межа, несправджене очікування й додаткова позитивна оцінка: g1/g3/g4/g5/g13/g14/g15/g19. Визнаний факт не підмінено умовним припущенням; «важко» не названо абсолютною неможливістю.
- Обмеження, єдиний вихід, тривалий стан, початок серії й приблизний ступінь: g16/g20/g22/g23/g29/g30. Менша частота нездужань не стала нульовою, участь не названа достатньою гарантією успіху, приблизна верхня оцінка не стала нижньою межею.
- Нереалізована можливість і докір, схильність, поганий підсумок, скромність або зневага: g32–g38. ごとき окремо про себе й іншого; минулий невиконаний крок не перетворено на майбутню гарантію.
- Сила почуття, нестерпність і надмірність, негайна дія, момент/результат, паралельні діяльності й подвійна мета: g49/g50/g51/g53/g56/g57/g59/g64/g65/g66/g85. ところ має різні контекстні значення; かたわら не означає фізично «поруч» або дії в одну секунду. Значення にたえない57/85 відділені, ID збережені.
- Необхідна умова, обставини, залежність від результату й відповідність: g68/g70/g71/g74/g75/g76/g77. Намір/очікування/можливість не стали доконаним фактом; розгляд санкцій не названо вже виконаним покаранням.
- Подолання перешкоди, відсутність стримування, легкість висновку, непотрібність, суб’єктивна нестерпність, вигляд/гіпербола й власний спосіб: g79/g80/g81/g83/g84/g86/g93/g94/g100/g101/g102. Необов’язковість не дорівнює забороні; майже плаче/зал наче тріскає не доводить реальних сліз/руйнування.
- Оцінний перелік, вагання між назвами та敬語: g106/g114/g118/g120–g127. Якість і ціна — два аспекти оцінки, без вигаданої конкретної ціни; прохання, дозвіл, власна дія й послуга іншої особи не змішані.

Додатково перечитано обидва незмінні g95-контексти; значення обставин збережене, без додавання нових прикладів чи нового приймального кредиту.

## Замкнений облік grammar meaning

[grammar-coverage.json](audit144/grammar-coverage.json) об’єднує поіменні авторські докази v142/v143/v144 та g95: **130 конструкцій /261 чинний приклад**, кожен рівно один раз. **224 saved +37 exact**, автоматичних серед цих контекстів **0**. Попередні payload й речення звірені за точними значеннями/хешами. Це вузьке завершення **авторського перегляду meaning-питань для чинних прикладів**.

Це **не незалежна експертиза**, не повне приймання визначень, приєднання, стилю, класифікації, перекладів і порівнянь усіх карток та не перевірка всіх можливих значень чи майбутніх речень. Складність для реальних учнів не виміряна. Технічний PASS не створює мовного доказу сам по собі.

## Незмінність і технічні перевірки

Змінено лише JSON REVIEWED_MEANING_QUIZZES і номер версії. JSON тепер **381**, runtime **382** з inline g95; byExample **262**. Усі 332 попередні JSON-набори, зокрема 265 лексичних, збережені. REVIEWED_EXAMPLE_TARGETS, картки, приклади, переклади, читання, POS, aliases, ID, UI, CSS, алгоритм і сховище незмінні. Нових/змінених порівнянь **0**, перелік порожній; 859/92/41 пар збережені. База — **3914 слів, 130 конструкцій, 160 текстів (99/61), 381 питання читання**.

- **23 групи інваріантів**, точний дозволений diff, JS-синтаксис; **439** попередніх файлів за Git blob-хешами збережено. Три поточні документи стану виключені з незмінного baseline, історичні звіти й реєстри не виключені.
- **3164 фактичні генерації**: **791 контекст ×4 позиції** ключа. Це 530 лексичних +всі 261 граматичні. Зіставлено точні речення/варіанти/ключі/пояснення й цільове виділення. Випадковість контролюється лише у тесті.
- **2373 фактичні покази**: ті самі 791 контекст ×360/412/1280px, натискання хибного варіанта, правильний feedback, видимі пояснення, без переповнення чи JS-помилок. **122** guard-перевірки невідомих контекстів: шість лексичних +116 граматичних saved-наборів.
- Окремо звірено точний payload усіх **261** граматичних контекстів із консолідованим авторським каталогом, включно з незмінним g95. Перші 130 питань: **114 saved /16 exact-reviewed /0 automatic**; серед 16 exact-перших — 11 C04 /5 C05. Ці цифри — технічне підтвердження маршруту, не незалежне мовне приймання.
- Reading-фільтр зберіг ті самі **1482 ID й кожну кількість альтернатив**; **2432** допустимі пули. Семантичної придатності всіх пулів не заявлено, новий механізм не ввімкнений.
- POS/пошук/фільтри/гортання/клавіші/свайпи, backup/import/reload; повна сесія ({r['session']['pages']} сторінок, {r['session']['answers']} відповідей, {r['session']['graded']} оцінок); 12 сценаріїв теми/масштабу 比較 й 12 показів незмінних карток v142. Chromium {r['meaning']['browser']}, Linux; фізичні Android/Windows не тестувалися. Візуально оглянуто g36/g64/g93/g127 із японським шрифтом.

Десять audit144/*-results.json прив’язані до SHA цього HTML. [coverage.py](audit144/coverage.py) зберігає посилання на попередні авторські докази, а не оголошує їх незалежно перевіреними повторно.

## Реєстр і залишок

[Результат C11-G](completion/C11-grammar-v144-result.json): авторський meaning-аудит чинних граматичних прикладів завершений у наведеній межі; **C11 загалом in_progress**. Попередні 67 конкретних зауважень збережені як опрацьовані у v142/v143. completion/review-register.csv **не змінений**: **325 reviewed /5517 pending із 5842 різнорідних позицій**, нових повнокарткових кредитів **0**. Приймання питання не є прийманням усієї картки.

Наступні ділянки — звірка решти граматичних полів/порівнянь із історичними доказами, автоматичні лексичні meaning-контексти поза збереженими наборами, reading-пули й однозначність cloze. C07/C08/C09/C10/C18, решта 40 текстів, C16 фізичне приймання й походження відкриті. Пропозицію для 1482, Learning Engine й N5–N1 не реалізовано. [Походження змін](audit144/provenance.json) не очищає старих публічних матеріалів; нічого не видалено й історію не переписано.

[Відтворення](audit144/README.md). Наступна повна основа — v144.
''')
p=ROOT/'PROJECT_STATUS.md';s=p.read_text();s=re.sub(r'Оновлено 5 листопада 2026, Asia/Tokyo\..*?\n\n3914',f'Оновлено 5 листопада 2026, Asia/Tokyo. Актуальна **v144**. Повний `{html.name}`, {html.stat().st_size} байтів; SHA-256 `{sha}`. Аудит JLPT_N1_v144_audit.md, відтворення audit144/README.md. Основа — v143 / commit 0025ba705060c6afddc193eb9880424203b0e613. Старі випуски збережено.\n\n3914',s,count=1,flags=re.S)
section='''## Виконано у v144 — meaning для всіх чинних граматичних прикладів

Решта 62 картки /124 контексти: 91 новий payload і 33 збережені точні набори (23 C04 /10 C05). Додано 49 saved-set і 42 byExample; картки, приклади, переклади, 332 попередні JSON-набори, exact-форми, ID, прогрес, UI та алгоритм незмінні. Окремо перечитано два незмінні g95-контексти. Це авторський перегляд, не незалежна експертиза.

Консолідовано точні докази для **130 конструкцій /261 чинного прикладу**: 224 saved +37 exact (27 C04 /10 C05), **0 automatic**. Вузький авторський meaning-аудит для цих прикладів завершено; повні картки, всі значення, приєднання/класифікація/порівняння цим не зараховані. Докази: audit144/grammar-coverage.json та completion/C11-grammar-v144-result.json. Старі технічні exact_C04 — скорочена назва маршруту; походження уточнено в новому каталозі без переписування історії.

23 інваріанти /439 попередніх файлів; 3164 генерації /2373 покази (791 контекст), 122 guard-перевірки, звірка всіх 261 payload, backup/import/reload, повна сесія й 比較 пройдені. Reading-фільтр зберіг ті самі 1482 ID/кількості альтернатив. Linux Chromium не є фізичним Android/Windows. **C11 загалом відкрито**: автоматичні лексичні meaning, reading-пули, cloze та контроль невідомих контекстів. Повні граматичні поля/порівняння звіряти з історичними доказами далі; не починати аудит з нуля. Приймальний реєстр лишається 325 reviewed /5517 pending, нових повнокарткових кредитів 0. Наступна основа — повний v144.

'''
if '## Виконано у v144' in s:s=s.split('## Виконано у v144',1)[0]+'## Виконано у v143'+s.split('## Виконано у v143',1)[1]
s=s.replace('## Виконано у v143',section+'## Виконано у v143',1);p.write_text(s)
p=ROOT/'completion/BACKLOG.md';s=p.read_text().replace('Поточний HTML — v143','Поточний HTML — v144');start=s.index('| C11 |');end=s.index('\n',start)
s=s[:start]+'| C11 | 2 | **in_progress** — grammar meaning для чинних прикладів авторськи завершено у v144 | 130 конструкцій /261 приклад: 224 saved +37 exact (27 C04 /10 C05), automatic 0. Вузький author review, не повні картки/всі значення/незалежна експертиза. Партія v144: 62 картки /124 контексти, 91 новий payload +33 збереження, 3164 генерації/2373 покази. audit144/grammar-coverage.json, completion/C11-grammar-v144-result.json; попередні v141/v142/v143 збережені. **Залишок:** автоматичні лексичні meaning поза збереженими наборами, reading-пули, cloze, контроль невідомих контекстів. 325/5517 збережено; решта граматичних полів/порівнянь — C10/C18. |'+s[end:];p.write_text(s)
p=ROOT/'README.md';s=p.read_text();history=s[s.index('Нижче збережено історичний журнал'):]
p.write_text(f'''# JLPT N1 — тренажер з японським інтерфейсом

**Актуальна v144:** [повний HTML](JLPT_N1_ukrainian_reading_v144.html) · [аудит](JLPT_N1_v144_audit.md).

Завершено авторську перевірку питань на значення для **всіх 261 чинного граматичного прикладу /130 конструкцій**. У цій партії — 91 новий набір варіантів і 33 збережені точні набори; попередні докази об’єднано без обнулення. Для цих прикладів автоматичний добір альтернатив більше не використовується.

3914 слів, 130 конструкцій, 160 текстів, 381 питання читання. Базу, ID, сумісність прогресу, картки, приклади й інтерфейс збережено. Весь наскрізний аудит ще триває: повні поля карток, інші вправи, фізичне й незалежне мовне приймання залишаються окремими задачами. Деталі — PROJECT_STATUS.md та audit144/. SHA-256 `{sha}`.

[Пропозиція для 1482 записів](strategy/READING_ASSESSMENT_PROPOSAL.md) · [фізичний Android/Windows-план](completion/PHYSICAL_DEVICE_TEST_PLAN.md) · [ризики вже опублікованих HTML](strategy/PUBLISHED_HTML_RISK_REVIEW.md). Нова навчальна архітектура не реалізована; походження/правова придатність не очищені мовним аудитом.

Попередні [v143](JLPT_N1_ukrainian_reading_v143.html), [v142](JLPT_N1_ukrainian_reading_v142.html), [v128](JLPT_N1_ukrainian_reading_v128.html) збережено. Перед відкриттям іншого HTML зробіть резервну копію прогресу в 設定.

'''+history)
print(json.dumps(dict(version=144,sha256=sha,bytes=html.stat().st_size,currentGrammarMeaningAuthorReview='130 cards /261 current examples',newPayloads=91,retainedExact=33,C11Overall='in_progress',registerUnchanged=True)))
