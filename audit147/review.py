"""Field-specific author decisions; structural checks do not establish linguistic correctness."""
from pathlib import Path
import json,re,hashlib,runpy,csv
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit147';a=runpy.run_path(str(P/'author.py'));old=(ROOT/'JLPT_N1_ukrainian_reading_v146.html').read_text();new=(ROOT/'release147/JLPT_N1_ukrainian_reading_v147.html').read_text()
def data(s,n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
reasons={
58:'光栄 і 感激 позначають урочисту оцінку та сильне почуття. Відокремлено усталену сполуку 若気の至り.',
59:'Вхід керівника і дзвінок задають межу швидкого переходу. У другому прикладі підмети різні.',
60:'Обидві ситуації повторюються, а результат першої дії нівелюється. У першому перекладі відновлено повторюваність.',
61:'Піднімання ролети й рух покупців показують різні підмети. Швидкість реакції не створює шкали між формами.',
62:'В обох прикладах діяч спільний. 一方的に не гарантує буквальної заборони іншим говорити.',
63:'知りながら виражає поступку, 聞きながら — одночасність. Розділено моделі приєднання.',
64:'У першому прикладі ところ задає момент дзвінка, у другому вводить результат перевірки. Пару 81 приведено до цього обсягу.',
65:'Робота й викладання, дослідження й наставництво можуть чергуватися в межах тривалого періоду.',
66:'Доповідь і консультація, подяка й привітання поєднані в одному візиті. Ієрархія цілей лишається контекстною.',
67:'気分転換 означає зміну обстановки. Виправлено переклад відпочинку й пояснено спільну нагоду.',
68:'Співпраця і зусилля подані як необхідні умови. Перша умова стосується минулого результату.',
69:'できない виражає неможливість, べきではない — оцінку належного. Друга частина визначає модальність.',
70:'Особлива умова може вести до готовності або вимушеного рішення. У першому прикладі є せざるを得ない.',
71:'Критика й викриття становлять вагомі підстави для реакції. Обов’язковість задає продовження.',
72:'Перший випадок відкладено вбік. У перекладі приватної розмови прибрано приписаний дозвіл.',
73:'漏洩しよう показує неволеву подію. かねない у другому реченні зберігає ризик.',
74:'Клієнти є основою компанії. Здоров’я має пріоритет перед роботою, а переклад не зводиться до буквальної здатності працювати.',
75:'Перебіг і результат задають умову. У другому перекладі повернено можливість розгляду стягнення.',
76:'Зіставлено узгодження з реальними умовами й опору на факти. Пара を踏まえて уточнює різницю акцентів.',
77:'Спосіб погляду чи застосування впливає на оцінку. У другому перекладі збережено припущення だろう.',
78:'Побоювання й спротив є зовнішніми реакціями. 事業者 не обов’язково є підрядником.',
79:'Холод і критика не зупиняють дії. Опис рішучості не встановлює успішного завершення.',
80:'Перший приклад є самовихвалянням, другий запереченням провини. Прибрано категоричний переклад «без сорому».',
}
rows=[];g=data(new,'GRAMMAR_DETAILS_BY_ID');previous=data(old,'GRAMMAR_DETAILS_BY_ID');words={x['id']:x for x in data(new,'GRAMMAR')}
for id in a['CARD_IDS']:
 d=g[str(id)];b=previous[str(id)];assert len(d['examples'])==len(d['exampleTranslations'])==2
 rows.append(dict(kind='grammar',key=str(id),word=words[id]['w'],beforeSha256=digest(b),afterSha256=digest(d),changedFields=[k for k in d if d[k]!=b[k]],reviewedFields=['Japanese definition m','Ukrainian meaning and connection/use/constraints t','related labels s','both Japanese examples','both Ukrainian example translations','existing topical category and tags (retained, not future JLPT reclassification)'],rationale=reasons[id],examples=[dict(index=i,japanese=ja,ukrainian=uk,decision='translation_corrected'if uk!=b['exampleTranslations'][i]else'retained_after_author_reading')for i,(ja,uk)in enumerate(zip(d['examples'],d['exampleTranslations']))],metadataDecision='Stable ID, heading, category, tags and inherited page g retained. Book-page accuracy/provenance not accepted by this linguistic review.',independentReview=False))
pairs=data(new,'GRAMMAR_AUDITED_PAIRS');before=data(old,'GRAMMAR_AUDITED_PAIRS');pairrows=[];register=list(csv.DictReader((ROOT/'completion/review-register.csv').open()))
for i in a['PAIR_IDS']:
 r=next(x for x in register if x['kind']=='grammar_pair'and x['baselineLocation']==f'GRAMMAR_AUDITED_PAIRS[{i}]');common,connection,difference,ja1,uk1,ja2,uk2,swap=a['PAIRS'][i]
 pairrows.append(dict(kind='grammar_pair',key=r['key'],index=i,labels=pairs[i][:2],beforeSha256=digest(before[i]),afterSha256=digest(pairs[i]),reviewedFields=['shared meaning','connection of both forms','semantic/register distinction','Japanese examples and Ukrainian translations','substitution limits'],decision='rewritten_and_author_reviewed',common=common,connection=connection,difference=difference,examples=[dict(japanese=ja1,ukrainian=uk1),dict(japanese=ja2,ukrainian=uk2)],substitution=swap,independentReview=False))
report=dict(version=147,sha256=hashlib.sha256(new.encode()).hexdigest(),reviewType='author_editorial_review',independentReview=False,grammarCards=23,grammarExampleTranslationsRead=46,grammarPairs=17,changedUkrainianExampleTranslations=10,newQuizCredits=0,newRegisterCredits=40,exclusions=['independent expert acceptance','physical-device acceptance','source/page/provenance clearance','new exhaustive taxonomy or JLPT level assignment','all other unreviewed cards and pairs'],rows=rows,pairs=pairrows)
(P/'editorial-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Author decisions: 23 cards /46 examples; 17 pairs; not independent')
