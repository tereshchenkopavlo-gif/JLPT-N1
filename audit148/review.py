"""Field-specific author decisions; structural checks do not establish linguistic correctness."""
from pathlib import Path
import json,re,hashlib,runpy,csv
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit148';a=runpy.run_path(str(P/'author.py'));old=(ROOT/'JLPT_N1_ukrainian_reading_v147.html').read_text();new=(ROOT/'release148/JLPT_N1_ukrainian_reading_v148.html').read_text()
def data(s,n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
reasons={
81:'想像 і 推察 оцінюють легкість висновку. У другому прикладі だろう зберігає припущення.',
82:'Запас харчів і перевірка договору подані як бажані заходи. Словникова звірка підтверджує перевагу варіанта.',
83:'Повторна перевірка й повторне пояснення зайві в конкретних умовах. Форма оцінює потребу в дії.',
84:'Шум і гнітюче відчуття викликають суб’єктивне нарікання. Написання 叶わない має інше значення.',
86:'Виправлено дефініцію, щоб охопити підстави для докору й подиву. Обидві форми з は і без нього представлені.',
87:'Вища планка поступається нижчій. Гарантія якості й виплата частинами мають різну модальність присудка.',
88:'Перше речення припускає готовність, друге визнає певну слушність. Подвійне заперечення лишає згоду обережною.',
89:'Відсутня дія може належати й іншій стороні. У другому прикладі так і не надійшла відповідь.',
90:'Зворушення і неприязнь є реакціями на зовнішній вплив. Переклад першого речення зберігає прогноз だろう.',
91:'Відповідальність і вибачення мають владнати наслідки ситуації. Необхідність не підтверджує виконання.',
92:'Обидва питання шукають спосіб розв’язання проблеми. Закінчення ものだろうか пом’якшує запит.',
93:'У першому прикладі вигляд нагадує людину перед плачем. У другому розкол зали є перебільшенням гучності.',
94:'なりに описує спосіб або міру, なりの означує погляд. Нижчий рівень не є обов’язковим.',
95:'Криза та економічне середовище задають тло. У парі 67 поступку окремо виражає も.',
96:'Вік і дві ролі є окремими моделями. У перекладі відновлено активний заклик до реформи.',
97:'奔流 є образом перебігу змін, а かのごとく описує поведінку так, ніби нічого не сталося.',
98:'Підвищення і перевірка оцінені як належні. У першому реченні підвищення ще не підтверджене.',
99:'たる者 називає носія ролі. Вимога самодисципліни та відповідальності стоїть у присудку.',
100:'Керівництво і фахівці подані як можливі винятки, до яких теж застосовується оцінка.',
101:'Посада і вихід на ринки задають масштаб вимог. У другому прикладі йдеться про реагування на правові вимоги.',
102:'Безсилля підлеглих і брак нагляду є вигідними обставинами. 理不尽 передано як несправедливість вимог.',
103:'Висока оцінка й довіра є критеріями. Форма може стояти перед іменником або бути присудком.',
}
rows=[];g=data(new,'GRAMMAR_DETAILS_BY_ID');previous=data(old,'GRAMMAR_DETAILS_BY_ID');words={x['id']:x for x in data(new,'GRAMMAR')}
for id in a['CARD_IDS']:
 d=g[str(id)];b=previous[str(id)];assert len(d['examples'])==len(d['exampleTranslations'])==2
 rows.append(dict(kind='grammar',key=str(id),word=words[id]['w'],beforeSha256=digest(b),afterSha256=digest(d),changedFields=[k for k in d if d[k]!=b[k]],reviewedFields=['Japanese definition m','Ukrainian meaning and connection/use/constraints t','related labels s','both Japanese examples','both Ukrainian example translations','existing topical category and tags (retained, not future JLPT reclassification)'],rationale=reasons[id],examples=[dict(index=i,japanese=ja,ukrainian=uk,decision='translation_corrected'if uk!=b['exampleTranslations'][i]else'retained_after_author_reading')for i,(ja,uk)in enumerate(zip(d['examples'],d['exampleTranslations']))],metadataDecision='Stable ID, heading, category, tags and inherited page g retained. Book-page accuracy/provenance not accepted by this linguistic review.',independentReview=False))
pairs=data(new,'GRAMMAR_AUDITED_PAIRS');before=data(old,'GRAMMAR_AUDITED_PAIRS');pairrows=[];register=list(csv.DictReader((ROOT/'completion/review-register.csv').open()))
for i in a['PAIR_IDS']:
 r=next(x for x in register if x['kind']=='grammar_pair'and x['baselineLocation']==f'GRAMMAR_AUDITED_PAIRS[{i}]');common,connection,difference,ja1,uk1,ja2,uk2,swap=a['PAIRS'][i]
 pairrows.append(dict(kind='grammar_pair',key=r['key'],index=i,labels=pairs[i][:2],beforeSha256=digest(before[i]),afterSha256=digest(pairs[i]),reviewedFields=['shared meaning','connection of both forms','semantic/register distinction','Japanese examples and Ukrainian translations','substitution limits'],decision='rewritten_and_author_reviewed',common=common,connection=connection,difference=difference,examples=[dict(japanese=ja1,ukrainian=uk1),dict(japanese=ja2,ukrainian=uk2)],substitution=swap,independentReview=False))
report=dict(version=148,sha256=hashlib.sha256(new.encode()).hexdigest(),reviewType='author_editorial_review',independentReview=False,grammarCards=22,grammarExampleTranslationsRead=44,grammarPairs=12,changedUkrainianExampleTranslations=11,newQuizCredits=0,newRegisterCredits=34,exclusions=['independent expert acceptance','physical-device acceptance','source/page/provenance clearance','new exhaustive taxonomy or JLPT level assignment','all other unreviewed cards and pairs'],rows=rows,pairs=pairrows)
(P/'editorial-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Author decisions: 22 cards /44 examples; 12 pairs; not independent')
