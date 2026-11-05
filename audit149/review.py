"""Field-specific author decisions; structural checks do not establish linguistic correctness."""
from pathlib import Path
import json,re,hashlib,runpy,csv
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit149';a=runpy.run_path(str(P/'author.py'));old=(ROOT/'JLPT_N1_ukrainian_reading_v148.html').read_text();new=(ROOT/'release149/JLPT_N1_ukrainian_reading_v149.html').read_text()
def data(s,n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
reasons={
104:'Негаразди й чорний одяг показують однорідність. Прибрано широке ототожнення з だらけ.',
105:'Мастило й багнюка є речовинами. Переклад прибирає непідтверджену деталь про все тіло.',
106:'Іронічність і весняний характер показані формою めいた. Переклад відновлює відтінок подібності.',
107:'Три приклади послідовно показують вагу, учасників і ціну. Уточнено місце збору.',
108:'Обидва приклади показують спільний ефект чинників. Сприятливість залежить від результату.',
109:'Рішення спирається на перебіг подій або думку експертів. Обидва переклади зберігають цю опору.',
110:'ようやく і ついに позначають завершеність очікування. 経て задає проміжний процес.',
111:'Відрядження й зайнятість можуть бути справжніми. Перевірено словникове значення приводу.',
112:'Розрізнено два названі випадки й узагальнення 何であれ. Висновок поширюється на всі варіанти.',
113:'У першому прикладі погляд нецілеспрямований. У другому важлива інформація випадково долинає.',
114:'Умови й атмосфера, якість і ціна є рисами для спільної оцінки. Обидва приклади позитивні.',
115:'Варіанти є способами зв’язку або надсилання. Вибір не обмежений двома пунктами.',
116:'Обидві пари чергують активну й пасивну дію. Окремо наведено чергування без взаємності.',
117:'Писання й стирання та сміх і плач показують повторювані цикли. Негативна оцінка не обов’язкова.',
118:'Перший приклад зіставляє сміливість і безрозсудність, другий удачу й іронію. Збережено риторичну оцінку.',
119:'День і ніч, внутрішній і зовнішній ринки охоплюють контрастний діапазон.',
120:'Зайнятість задає вимогу, а робота наодинці — перевагу. Продовження визначає оцінку.',
121:'Мовець представляє власну дію як отриману можливість. У другому прикладі дозвіл названо прямо.',
122:'Перевіряє викладач, користь отримує мовець. Переклад 添削 зберігає перевірку й виправлення.',
123:'Заповнення й утримання від фотографування є проханнями. Виправлено українське формулювання першого.',
124:'Підметом є шанований діяч. У двох прикладах це відвідування й участь.',
125:'У першому реченні мовець визнає клопіт іншої особи. У другому お寄せいただく оформлює отримання дії.',
126:'Їжа й кава показують два значення одного шанобливого дієслова. Усталене お召し上がりになる збережено.',
127:'Одяг і вподобання належать до різних сполук із 召す. Відмінність від 召し上がる пояснено в парі.',
128:'Матеріали й місця перебувають у підготовленому стані. Виконавця дії не названо.',
129:'Напрямок у першому прикладі встановлює こちら. Другий приклад встановлює час прибуття.',
130:'Подяка й вибачення стосуються минулої нагоди. Загальне пояснення залишає можливим інший час.',
}
rows=[];g=data(new,'GRAMMAR_DETAILS_BY_ID');previous=data(old,'GRAMMAR_DETAILS_BY_ID');words={x['id']:x for x in data(new,'GRAMMAR')}
for id in a['CARD_IDS']:
 d=g[str(id)];b=previous[str(id)];assert len(d['examples'])==len(d['exampleTranslations'])==(3 if id==107 else 2)
 rows.append(dict(kind='grammar',key=str(id),word=words[id]['w'],beforeSha256=digest(b),afterSha256=digest(d),changedFields=[k for k in d if d[k]!=b[k]],reviewedFields=['Japanese definition m','Ukrainian meaning and connection/use/constraints t','related labels s','both Japanese examples','both Ukrainian example translations','existing topical category and tags (retained, not future JLPT reclassification)'],rationale=reasons[id],examples=[dict(index=i,japanese=ja,ukrainian=uk,decision='translation_corrected'if uk!=b['exampleTranslations'][i]else'retained_after_author_reading')for i,(ja,uk)in enumerate(zip(d['examples'],d['exampleTranslations']))],metadataDecision='Stable ID, heading, category, tags and inherited page g retained. Book-page accuracy/provenance not accepted by this linguistic review.',independentReview=False))
pairs=data(new,'GRAMMAR_AUDITED_PAIRS');before=data(old,'GRAMMAR_AUDITED_PAIRS');pairrows=[];register=list(csv.DictReader((ROOT/'completion/review-register.csv').open()))
for i in a['PAIR_IDS']:
 r=next(x for x in register if x['kind']=='grammar_pair'and x['baselineLocation']==f'GRAMMAR_AUDITED_PAIRS[{i}]');common,connection,difference,ja1,uk1,ja2,uk2,swap=a['PAIRS'][i]
 pairrows.append(dict(kind='grammar_pair',key=r['key'],index=i,labels=pairs[i][:2],beforeSha256=digest(before[i]),afterSha256=digest(pairs[i]),reviewedFields=['shared meaning','connection of both forms','semantic/register distinction','Japanese examples and Ukrainian translations','substitution limits'],decision='rewritten_and_author_reviewed',common=common,connection=connection,difference=difference,examples=[dict(japanese=ja1,ukrainian=uk1),dict(japanese=ja2,ukrainian=uk2)],substitution=swap,independentReview=False))
report=dict(version=149,sha256=hashlib.sha256(new.encode()).hexdigest(),reviewType='author_editorial_review',independentReview=False,grammarCards=27,grammarExampleTranslationsRead=55,grammarPairs=9,changedUkrainianExampleTranslations=10,newQuizCredits=0,newRegisterCredits=36,exclusions=['independent expert acceptance','physical-device acceptance','source/page/provenance clearance','new exhaustive taxonomy or JLPT level assignment','all other unreviewed cards and pairs'],rows=rows,pairs=pairrows)
(P/'editorial-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Author decisions: 27 cards /55 examples; 9 pairs; not independent')
