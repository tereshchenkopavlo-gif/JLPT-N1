"""Field-specific author decisions; structural checks do not establish linguistic correctness."""
from pathlib import Path
import json,re,hashlib,runpy,csv
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit146';a=runpy.run_path(str(P/'author.py'));old=(ROOT/'JLPT_N1_ukrainian_reading_v145.html').read_text();new=(ROOT/'release146/JLPT_N1_ukrainian_reading_v146.html').read_text()
def data(s,n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
reasons={
33:'困る залишає перспективу неозначеною. Переклад не нав’язує адресата другої особи.',
34:'У першому реченні きらいがある безпосередньо йде після 軽視する. Виправлено сферу схильності.',
35:'Перший приклад має 始末となった, другий 始末だ. Обидва підсумовують прикрий розвиток.',
36:'私ごときが та 素人ごときに розрізняють самоприменшення і зневагу. のごとき у порівнянні має іншу функцію.',
37:'В обох реченнях є емоційна оцінка, хоча в другому мова про ціни. Знято вимогу постійної поведінки.',
38:'Запізнення та пропущене порушення зіставлено з умовно терпимим варіантом.',
39:'せんがため виражає мету. Слова про будь-яку ціну не випливають з першого речення.',
40:'回復すべく та 開拓すべく вводять мету. 徹底し直した описує повторне посилення контролю, без твердження про завершену перевірку.',
41:'Повтор дії оцінює закономірність. といえる збережено як висновок мовця.',
42:'望む й 期待する стосуються шансів на результат. Заборона з прикладів не випливає.',
43:'Обидва речення формулюють заборону, зокрема напис для сторонніх.',
44:'Осуд оцінює висловлювання посадовця й поведінку вчителя з огляду на роль.',
45:'書面 позначає спосіб відповіді, 誠意 — ставлення. Уточнено дефініцію для обох контекстів.',
46:'Один приклад зіставляє ринки, інший денні вулиці й нічний офісний квартал.',
47:'Ціна й скасування турніру є вимушеними кроками. Розмежовано пасивну й каузативну моделі.',
48:'Тиск названо через стан здоров’я і спротив. 強行した позначає здійснення виходу попри спротив.',
49:'Обидва контексти передають ступінь почуття через іменники на さ.',
50:'不誠実 і 危険 підтверджують негативний підсилювач. Розрізнено крайній ступінь та перехід межі.',
51:'やみません і やまない показують різний ступінь ввічливості того самого побажання.',
52:'Обурення й співчуття є реакціями. Речення не встановлюють подальшого вчинку.',
53:'У першому прикладі とは завершує вислів, у другому вводить оцінку майстерності. Дефініція охоплює обидва.',
54:'Орієнтиром є попередній рік або пріоритет прибутку. Друге речення порівнює цінність, а не числову величину.',
55:'Мужність і людська причина катастрофи стверджені риторичним запитанням. Переклади зберігають цей тон.',
56:'悪びれない передано через відсутність каяття. Обидва випадки оцінюють порушення допустимої межі.',
}
rows=[];g=data(new,'GRAMMAR_DETAILS_BY_ID');previous=data(old,'GRAMMAR_DETAILS_BY_ID');words={x['id']:x for x in data(new,'GRAMMAR')}
for id in a['CARD_IDS']:
 d=g[str(id)];b=previous[str(id)];assert len(d['examples'])==len(d['exampleTranslations'])==2
 rows.append(dict(kind='grammar',key=str(id),word=words[id]['w'],beforeSha256=digest(b),afterSha256=digest(d),changedFields=[k for k in d if d[k]!=b[k]],reviewedFields=['Japanese definition m','Ukrainian meaning and connection/use/constraints t','related labels s','both Japanese examples','both Ukrainian example translations','existing topical category and tags (retained, not future JLPT reclassification)'],rationale=reasons[id],examples=[dict(index=i,japanese=ja,ukrainian=uk,decision='translation_corrected'if uk!=b['exampleTranslations'][i]else'retained_after_author_reading')for i,(ja,uk)in enumerate(zip(d['examples'],d['exampleTranslations']))],metadataDecision='Stable ID, heading, category, tags and inherited page g retained. Book-page accuracy/provenance not accepted by this linguistic review.',independentReview=False))
pairs=data(new,'GRAMMAR_AUDITED_PAIRS');before=data(old,'GRAMMAR_AUDITED_PAIRS');pairrows=[];register=list(csv.DictReader((ROOT/'completion/review-register.csv').open()))
for i in a['PAIR_IDS']:
 r=next(x for x in register if x['kind']=='grammar_pair'and x['baselineLocation']==f'GRAMMAR_AUDITED_PAIRS[{i}]');common,connection,difference,ja1,uk1,ja2,uk2,swap=a['PAIRS'][i]
 pairrows.append(dict(kind='grammar_pair',key=r['key'],index=i,labels=pairs[i][:2],beforeSha256=digest(before[i]),afterSha256=digest(pairs[i]),reviewedFields=['shared meaning','connection of both forms','semantic/register distinction','Japanese examples and Ukrainian translations','substitution limits'],decision='rewritten_and_author_reviewed',common=common,connection=connection,difference=difference,examples=[dict(japanese=ja1,ukrainian=uk1),dict(japanese=ja2,ukrainian=uk2)],substitution=swap,independentReview=False))
report=dict(version=146,sha256=hashlib.sha256(new.encode()).hexdigest(),reviewType='author_editorial_review',independentReview=False,grammarCards=24,grammarExampleTranslationsRead=48,grammarPairs=17,changedUkrainianExampleTranslations=9,newQuizCredits=0,newRegisterCredits=41,exclusions=['independent expert acceptance','physical-device acceptance','source/page/provenance clearance','new exhaustive taxonomy or JLPT level assignment','all other unreviewed cards and pairs'],rows=rows,pairs=pairrows)
(P/'editorial-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Author decisions: 24 cards /48 examples; 17 pairs; not independent')
