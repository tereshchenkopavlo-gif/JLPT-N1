"""Field-specific author decisions; structural checks do not establish linguistic correctness."""
from pathlib import Path
import json,re,hashlib,runpy,csv
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit145';a=runpy.run_path(str(P/'author.py'));old=(ROOT/'JLPT_N1_ukrainian_reading_v144.html').read_text();new=(ROOT/'release145/JLPT_N1_ukrainian_reading_v145.html').read_text()
def data(s,n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
reasons={
1:'В обох прикладах перешкода не змінює намір; відділено намір-поступку від Vるようが; прибрано зайву хвилю в посиланні たとえ.',
2:'Перевірено позитивну й негативну альтернативи тієї самої дії; наведено різні приєднання まい, без помилкового 意向形 перед まい.',
3:'Визнання факту й обмеження висновку; у прикладах не спростовано відновлення економіки чи фаховість експерта.',
4:'Перешкода не доводить виконаної спроби; обидва переклади виправлено з фактичної спроби/нормативної заборони на неможливість.',
5:'Розрізнено спростоване очікування й визнаний факт; другий приклад має な-прикметник без だ перед か.',
6:'Статус чи близькість не скасовує обмеження; збережено книжний регістр без заяви про абсолютну незамінність із とはいえ.',
7:'Припущення марної дії; た не є доказом минулого або фізичної можливості. だろう у перекладах лишається припущенням.',
8:'Особлива причина пояснює чергу й розпродаж; відмежовано умовну готовність とあれば, без правила про виключно минулий час.',
9:'Причина емоційно виділена; ば не перетворює вже наявну причину на майбутню умову і не доводить єдину можливу причину.',
10:'Два іменні/であるがゆえ контексти; приєднання до V/イ形 не поширено механічно на Nだ; перевірено ゆえの перед графіком і тиском.',
11:'Пояснення зі сподіванням на розуміння; друга причина пояснює пам’ять і не вимагає формального вибачення. Nの /ナな розділено.',
12:'Відповідальність перед іншими, не фізична перешкода; 気が引ける — вагання, не вже виконана понаднормова робота.',
13:'Обидва кількісні мінімуми поєднано з категоричною забороною; не дозволено довільний Nたりとも.',
14:'Друга частина — мінімум, який теж важкий; おぼつかない／困難 смислово негативні без необхідності форми ない.',
15:'Перша перевага зберігається; увага до другої не означає відсутності першої чи виміряного числового перевищення.',
16:'Чекання й рішуче просування; のみ позначає обмеження, не самостійний доказ безвиході чи гарантію успіху.',
17:'想像するだに та 夢にだに — різні сталі будови; сон у другому не буквальна подія; сучасна сполучуваність обмежена.',
18:'Прочитано обидва значення: готовність подати заяву і лише виконана процедура; Vた не пояснено як майбутній намір.',
19:'Дієслівна ситуація номіналізована через こと; 想像 — іменник дії, не ます-основа; ですら збережено.',
20:'Людинаいない проти шляхуない; だろう лишається припущенням; оцінка єдиного придатного вибору, не просте крім.',
21:'Виділено своєрідну майстерність і гостинність; оцінний наголос не є незалежним доказом фізичної унікальності.',
22:'Переломна подія і тривалий наступний стан; не два разові факти й не незмінність на все життя.',
23:'Перший виступ/презентація запускає серію; тур і конкуренція не вимагають тотожності всіх наступних подій.',
24:'Обидва приклади — офіційна часова межа, не засіб; точний час задано у другому прикладі, не словом 本日 загалом.',
25:'Припущення анулює зусилля чи завершує справу; не буквальне до того часу й не ствердження вже здійсненої події.',
26:'Не змішано умовне た з минулим; かねない в першому зберігає ризик, другий описує звичну втрату контролю.',
27:'今日を限りに — сьогодні останній день, а не автоматично від початку сьогодні; завершення, не строк рішення.',
28:'Діапазон охоплює етапи або деталі; кінцева точка не мусить бути екстремальною чи фізичним місцем.',
29:'Оцінка рівня/величини; せいぜい посилює межу. Прибрано непідтверджений майбутній час з перекладу другого прикладу.',
30:'Поширення не виключає першу групу; не потрібна ієрархія оцінок на відміну від акценту もさることながら.',
31:'Крайній випадок на тлі інших, часто критичний. 二十日以上 включає двадцять: виправлено на щонайменше.',
32:'Обидва приклади — нереалізована краща можливість; це не вичерпує всіх поступових значень ものを.',
57:'Слухати й дивитися нестерпно; 正視 — іменна сполука. Посилання ② виправлено на фактичний заголовок; написання 堪 не визначає сенсу.',
85:'Формальна подяка й жаль; не заперечення почуття і не довільний іменник емоції. Японські колокації звужено до типових.'}
rows=[];g=data(new,'GRAMMAR_DETAILS_BY_ID');previous=data(old,'GRAMMAR_DETAILS_BY_ID');words={x['id']:x for x in data(new,'GRAMMAR')}
for id in a['CARD_IDS']:
 d=g[str(id)];b=previous[str(id)];assert len(d['examples'])==len(d['exampleTranslations'])==2
 rows.append(dict(kind='grammar',key=str(id),word=words[id]['w'],beforeSha256=digest(b),afterSha256=digest(d),changedFields=[k for k in d if d[k]!=b[k]],reviewedFields=['Japanese definition m','Ukrainian meaning and connection/use/constraints t','related labels s','both Japanese examples','both Ukrainian example translations','existing topical category and tags (retained, not future JLPT reclassification)'],rationale=reasons[id],examples=[dict(index=i,japanese=ja,ukrainian=uk,decision='translation_corrected'if uk!=b['exampleTranslations'][i]else'retained_after_author_reading')for i,(ja,uk)in enumerate(zip(d['examples'],d['exampleTranslations']))],metadataDecision='Stable ID, heading, category, tags and inherited page g retained. Book-page accuracy/provenance not accepted by this linguistic review.',independentReview=False))
pairs=data(new,'GRAMMAR_AUDITED_PAIRS');before=data(old,'GRAMMAR_AUDITED_PAIRS');pairrows=[];register=list(csv.DictReader((ROOT/'completion/review-register.csv').open()))
for i in a['PAIR_IDS']:
 r=next(x for x in register if x['kind']=='grammar_pair'and x['baselineLocation']==f'GRAMMAR_AUDITED_PAIRS[{i}]');common,connection,difference,ja1,uk1,ja2,uk2,swap=a['PAIRS'][i]
 pairrows.append(dict(kind='grammar_pair',key=r['key'],index=i,labels=pairs[i][:2],beforeSha256=digest(before[i]),afterSha256=digest(pairs[i]),reviewedFields=['shared meaning','connection of both forms','semantic/register distinction','Japanese examples and Ukrainian translations','substitution limits'],decision='rewritten_and_author_reviewed',common=common,connection=connection,difference=difference,examples=[dict(japanese=ja1,ukrainian=uk1),dict(japanese=ja2,ukrainian=uk2)],substitution=swap,independentReview=False))
report=dict(version=145,sha256=hashlib.sha256(new.encode()).hexdigest(),reviewType='author_editorial_review',independentReview=False,grammarCards=34,grammarExampleTranslationsRead=68,grammarPairs=37,changedUkrainianExampleTranslations=4,newQuizCredits=0,newRegisterCredits=71,exclusions=['independent expert acceptance','physical-device acceptance','source/page/provenance clearance','new exhaustive taxonomy or JLPT level assignment','all other unreviewed cards and pairs'],rows=rows,pairs=pairrows)
(P/'editorial-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Author decisions: 34 cards /68 examples; 37 pairs; not independent')
