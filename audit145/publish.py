"""Accept only hash-bound reports, then publish full HTML and additive author credits."""
from pathlib import Path
import json,hashlib,shutil,re,csv,io,subprocess,collections
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit145';html=ROOT/'release145/JLPT_N1_ukrainian_reading_v145.html';sha=hashlib.sha256(html.read_bytes()).hexdigest();summary=json.loads((P/'build-summary.json').read_text());assert sha==summary['sha256']=='80cc4a3d35ad2257b1b38afc1ad566066db0797409892b10697a84e35cf21d47'
r={n:json.loads((P/f'{n}-results.json').read_text())for n in ['invariant','meaning','presentation','ui','functional','session','comparison','grammar','scope','coverage']};assert all(x['sha256']==sha for x in r.values())
assert len(r['invariant']['checks'])==22 and all(x['pass_']for x in r['invariant']['checks'])and r['invariant']['previousFilesChecked']==475
assert r['meaning']['pass']and r['meaning']['generationCases']==3164 and r['meaning']['renderedCases']==2373 and not r['meaning']['errors']
assert all(x['pass']for x in r['meaning']['generated']+r['meaning']['rendered'])and len(r['meaning']['unknownContextGuard'])==122 and all(x['unknownNote']==''and x['headwordNote']for x in r['meaning']['unknownContextGuard'])
assert all(len(r[n]['results'])==3 and all(x['pass']for x in r[n]['results'])for n in ['presentation','functional'])
assert len(r['ui']['checks'])==3 and all(all(v for k,v in x.items()if k!='width')for x in r['ui']['checks'])
assert r['session']['pass']and len(r['comparison']['results'])==12 and all(x['pass']for x in r['comparison']['results'])
assert r['grammar']['pass']and len(r['grammar']['results'])==102 and len(r['grammar']['pairResults'])==111 and all(x['pass']for x in r['grammar']['results']+r['grammar']['pairResults'])
assert r['scope']['pass']and not r['scope']['automaticGrammarIds']and len(r['scope']['savedFirstIds'])==114 and len(r['scope']['exactReviewedFirstIds'])==16 and r['scope']['guardedReadingPools']==1482 and r['scope']['guardedIdsAndCandidateCountsUnchanged']
assert r['coverage']['pass']and r['coverage']['grammarCards']==130 and r['coverage']['grammarContexts']==261 and r['coverage']['automaticCurrentContexts']==0 and all(x['pass']for x in r['coverage']['results'])
review=json.loads((P/'editorial-review.json').read_text());assert review['sha256']==sha and review['grammarCards']==34 and review['grammarPairs']==37 and not review['independentReview']
# Recreate from the frozen register, retaining every prior row and all 325 credits.
base=json.loads((P/'baseline-integrity.json').read_text())['commit'];oldcsv=subprocess.check_output(['git','show',base+':completion/review-register.csv'],cwd=ROOT,text=True);rows=list(csv.DictReader(io.StringIO(oldcsv)));targets={(x['kind'],x['key'])for x in review['rows']+review['pairs']};assert len(targets)==71
for row in rows:
 if(row['kind'],row['key'])in targets:
  assert row['finalReview']=='pending'
  row['finalReview']='reviewed';row['evidence']=f'audit145/editorial-review.json:{row["kind"]}:{row["key"]}; author linguistic review, not independent; provenance/physical excluded'
assert collections.Counter(x['finalReview']for x in rows)=={'reviewed':396,'pending':5446}
with(ROOT/'completion/review-register.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys(),lineterminator='\n');w.writeheader();w.writerows(rows)
result=dict(version=145,sha256=sha,status='partial_author_review',criteria=['C10','C18'],grammarCards=34,grammarIds=summary['grammarIds'],grammarPairs=37,pairIndices=summary['pairIndices'],grammarExamplesRead=68,changedExampleTranslations=4,newRegisterCredits=71,previousReviewed=325,registerReviewed=396,registerPending=5446,totalHeterogeneousRegisterRows=5842,independentReview=False,fullAuditComplete=False,meaningCoverageInherited='audit144/grammar-coverage.json:130 grammar/261 current contexts; payloads unchanged and rerouted in audit145/coverage-results.json',evidence='audit145/editorial-review.json',remaining=['96 grammar register cards','55 grammar pairs','pending vocabulary and other register rows','C11 vocabulary meaning /reading pools /cloze','physical Android/Windows acceptance','independent expertise','source and legal clearance'])
(ROOT/'completion/C10-C18-v145-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(P/'provenance.json').write_text(json.dumps(dict(version=145,sha256=sha,status='not_cleared_for_public_product',base='v144 / '+summary['baseSha256'],newMaterial='Original Ukrainian explanations for 34 existing grammar cards and structured notes for 37 existing pairs; 9 Japanese definitions clarified; 4 inherited Ukrainian example translations revised.',inherited='All Japanese card examples, most pair Japanese examples and all quiz data retained; origin unresolved. Semantic editing/translation/reordering do not remove inherited rights uncertainty.',sources='audit145/sources.md',review='audit145/editorial-review.json',publicExposure='Complete v145 and audit sources on main; unfinished work/v145-checkpoint / cee84426e91160a1e6b63fa5380624a6169b83d1. Existing HTML versions, reachable history/branches and historical Actions packages remain in separate rights audit.',historicalInventory='review20261105/public-inventory.json remains a frozen v141 snapshot, not current counts.',newActionsArtifacts=False,oldActionsContentsVerified=False,visibilityChanged=False,historyRewritten=False,materialsDeleted=False,independentReview=False),ensure_ascii=False,indent=2)+'\n')
shutil.copyfile(html,ROOT/html.name)
(ROOT/'JLPT_N1_v145_audit.md').write_text(f'''# Аудит JLPT N1 v145 — 5 листопада 2026, Asia/Tokyo

Повний [{html.name}]({html.name}), {html.stat().st_size} байтів; SHA-256 `{sha}`. Основа — повний v144 / commit {base}, SHA-256 {summary['baseSha256']}. Старі випуски й докази збережено. Окремий незавершений checkpoint: work/v145-checkpoint / cee84426e91160a1e6b63fa5380624a6169b83d1.

## Авторський мовний обсяг

**34 граматичні картки:** g1–g32, g57, g85. Прочитано японське значення, український переклад, приєднання, вживання, обмеження/стиль, пов’язані назви, обидва японські приклади та їхні переклади — **68 пар речень**. Поточні тематичні категорії й теги збережено як робочі групи; майбутньої класифікації N5–N1 не виконано. Номери сторінок книги не прийняті як перевірені джерела. Рішення по кожному ID — audit145/editorial-review.json.

**37 порівнянь:** індекси {', '.join(map(str,summary['pairIndices']))}. Для кожного звірено спільне значення, приєднання обох форм, різницю, приклади/переклади та межі заміни. Єдині розділи: 共通点・接続・違い・例文・置き換え. Структурний тест сам по собі не є мовним аудитом; окремі авторські рішення збережено в JSON.

Уточнено すら: 想像 — іменник дії, а не ます-основа. У たが最後 ризик із かねない не перетворено на гарантований наслідок. У たところで た не доводить минулого виконання чи фізичної можливості. Відділено обидва значення にたえない й виправлено посилання g57→g85 без переставляння ID. Уточнено приєднання まい／ゆえ／こととて, не змішано Vる/Vたまでのことだ; ならでは не описано як об’єктивний доказ абсолютної унікальності.

**Чотири виправлені українські переклади:** g4/e0 — неможливість без вигаданої здійсненої спроби; g4/e1 — неможливість, не тільки заборона; g29/e1 — приблизна оцінка без доданого майбутнього часу; g31/e0 — 二十日以上 = щонайменше двадцять, включно з двадцятьма. Японські речення всіх карток не змінено.

## Реєстр і межі приймання

Додано **71 авторський результат**: 34 grammar +37 grammar_pair. Попередні **325** збережено без змін; разом **396 reviewed /5446 pending** із 5842 різнорідних рядків. Це не відсоток повної готовності й не незалежна експертиза. У поточному завершальному реєстрі лишаються 96 граматичних карток і 55 порівнянь; історичні перевірки поза цим реєстром не оголошено нульовими. Повний наскрізний аудит відкрито.

Досягнення v144 — авторське meaning-приймання всіх **130 конструкцій /261 чинного контексту** — збережено: 224 saved +37 exact (27 C04 /10 C05), automatic 0. Жодного нового quiz-payload у v145. Новий SHA-каталог переносить попередні точні докази й звіряє незмінність; він не приписує новий мовний перегляд старим питанням. C11 загалом лишається відкритим для лексики, reading-пулів і cloze.

## Технічна перевірка

22 групи інваріантів; Git blob-звірка **475** попередніх заморожених файлів; усі попередні credits збережено. JS-синтаксис, **3164 генерації /2373 покази feedback**, 122 перевірки невідомих контекстів, точні payload усіх 261 граматичних прикладів. Нові поля відображено у **102** сценаріях карток і **111** сценаріях фактично вибраних пар на ширинах 360/412/1280. Українські переклади японських прикладів показані окремими рядками. Перевірено японські підписи, навігацію, експорт/імпорт/reload прогресу, завершену сесію та 12 сценаріїв типографіки/тем 比較. Звіти *-results.json прив’язані до цього SHA.

Незмінні 3914 слів /130 конструкцій /160 текстів /381 питання, ID/категорії/теги, алгоритми, сховище, інтерфейс, усі quiz-набори й exact-targets. Reading-фільтр лишив ті самі **1482 ID та кількості кандидатів**; альтернативну методику не реалізовано. Linux Chromium не є фізичним Android/Windows: C16 залишається відкритим.

## Походження й наступна робота

Нові пояснення написано для застосунку; зовнішні джерела використано для окремих мовних фактів (audit145/sources.md), без імпорту вправ чи абзаців. Походження успадкованих речень/структури не з’ясовано. Перефразування й виправлення перекладу не є правовим очищенням. Оцінка вже публічних HTML включає новий v145, старі випуски, робочу гілку, досяжну історію та старі Actions-пакети; заморожений v141 inventory не видається за поточний. Видимість, історію й склад матеріалів не змінено; юридичних висновків немає.

Наступне — решта полів граматичних карток і порівнянь, збереження старих авторських доказів, далі інші C11-контексти. Незалежна експертиза, фізичне приймання та права мають окремі результати й не закриті цим випуском. Нова архітектура залишається проєктуванням.
''')
# Always derive current documentation from the frozen published base for idempotence.
def original(path):return subprocess.check_output(['git','show',base+':'+path],cwd=ROOT,text=True)
p=ROOT/'PROJECT_STATUS.md';s=original('PROJECT_STATUS.md');s=re.sub(r'Оновлено 5 листопада 2026, Asia/Tokyo\..*?\n\n3914',f'Оновлено 5 листопада 2026, Asia/Tokyo. Актуальна **v145**. Повний `{html.name}`, {html.stat().st_size} байтів; SHA-256 `{sha}`. Аудит JLPT_N1_v145_audit.md, відтворення audit145/README.md. Основа — повний v144 / {base}. Старі випуски збережено.\n\n3914',s,count=1,flags=re.S)
section='''## Виконано у v145 — поля граматичних карток і порівняння

Авторськи прочитано й відредаговано 34 картки (g1–g32/g57/g85), 68 японських прикладів із перекладами та 37 порівнянь. Розділено значення/приєднання/вживання/обмеження; пари мають 共通点・接続・違い・例文・置き換え. Виправлено すら, модальність たが最後／かねない, зв’язок g57→g85, чотири переклади (зокрема 二十日以上). Докладні поіменні рішення — audit145/editorial-review.json.

71 новий авторський рядок реєстру: 34 grammar +37 grammar_pair; попередні 325 незмінні, разом **396 reviewed /5446 pending** із 5842 різнорідних рядків. У поточному завершальному реєстрі ще 96 граматичних карток і 55 пар; історичні докази не обнулено. Це не незалежна експертиза, не правове/фізичне приймання й не повне завершення аудиту.

22 групи інваріантів /475 попередніх файлів; 3164 генерації /2373 покази; 102 сценарії нових карток і 111 вибраних пар; навігація, backup/import/reload, повна сесія й теми 比較. Усі quiz-набори/261 граматичний контекст v144, ID, алгоритм, прогрес і склад бази незмінні. Ті самі 1482 reading guards. C11/C16 та незалежне/правове приймання відкриті. Далі — решта полів граматичних карток і порівнянь. Наступна основа — повний v145.

'''
s=s.replace('## Виконано у v144',section+'## Виконано у v144',1);p.write_text(s)
s=original('completion/BACKLOG.md').replace('Поточний HTML — v144','Поточний HTML — v145')
for key,extra in [('C10',' v145: 34 граматичні картки/68 прикладів авторськи перевірено, 37 пар звірено; 71 новий credit, 396 reviewed /5446 pending. Доказ completion/C10-C18-v145-result.json; незалежне приймання відкрите.'),('C18',' v145: 34 картки й 37 порівнянь мають окремі змістові авторські рішення та єдині секції; g57→g85 виправлено, значення не визначаються написанням 堪. Решта 96 карток/55 пар у поточному реєстрі відкрита.')]:
 start=s.index('| '+key+' |');end=s.index('\n',start);line=s[start:end];s=s[:start]+line[:-1]+extra+' |'+s[end:]
# Prior counts in C11 were historical; describe their preservation and current tally explicitly.
start=s.index('| C11 |');end=s.index('\n',start);line=s[start:end].replace('325/5517 збережено','325 старих credits збережено; у v145 після окремого C10/C18 — 396/5446');s=s[:start]+line+s[end:];(ROOT/'completion/BACKLOG.md').write_text(s)
s=original('README.md');history=s[s.index('Нижче збережено історичний журнал'):]
(ROOT/'README.md').write_text(f'''# JLPT N1 — тренажер з японським інтерфейсом

**Актуальна v145:** [повний HTML]({html.name}) · [аудит](JLPT_N1_v145_audit.md).

Уніфіковано й авторськи перевірено **34 граматичні картки та 37 порівнянь**: значення, приєднання, обмеження, приклади й межі заміни. Уточнено すら, たが最後, にたえない та чотири українські переклади прикладів. Рішення по кожній картці/парі — audit145/editorial-review.json.

Попередній meaning-аудит усіх **130 конструкцій /261 чинного прикладу** збережено без зміни quiz-наборів. Реєстр — **396 reviewed /5446 pending**; це різнорідні авторські результати, а не відсоток завершення всього аудиту. Незалежне мовне, фізичне Android/Windows та правове приймання відкриті.

3914 слів, 130 конструкцій, 160 текстів, 381 питання читання. ID, сумісність прогресу, алгоритм та інтерфейс збережено. SHA-256 `{sha}`. Відтворення — audit145/README.md.

[Пропозиція для 1482 записів](strategy/READING_ASSESSMENT_PROPOSAL.md) · [фізичний план](completion/PHYSICAL_DEVICE_TEST_PLAN.md) · [ризики публічних HTML](strategy/PUBLISHED_HTML_RISK_REVIEW.md). Нову архітектуру не реалізовано. Мовне редагування не очищає права на успадковані матеріали.

Попередні [v144](JLPT_N1_ukrainian_reading_v144.html), [v143](JLPT_N1_ukrainian_reading_v143.html), [v128](JLPT_N1_ukrainian_reading_v128.html) збережено. Перед переходом до іншого HTML збережіть резервну копію прогресу в 設定.

'''+history)
print(json.dumps(dict(version=145,sha256=sha,bytes=html.stat().st_size,newAuthorCredits=71,reviewed=396,pending=5446,fullAuditComplete=False)))
