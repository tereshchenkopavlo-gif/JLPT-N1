from pathlib import Path
import json,re,hashlib,runpy,collections
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit144';s=(ROOT/'release144/JLPT_N1_ukrainian_reading_v144.html').read_text()
def data(n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
g=data('GRAMMAR_DETAILS_BY_ID');q=data('REVIEWED_MEANING_QUIZZES');targets=data('REVIEWED_EXAMPLE_TARGETS');words={x['id']:x['w']for x in data('GRAMMAR')};a=runpy.run_path(str(P/'author.py'))
RATIONALE={
1:'Збережено намір попри будь-які перешкоди; відсутності перешкод або умови їх наявності не стверджується.',
4:'Намір і зовнішня неможливість відділені від втрати бажання й добровільного скасування.',
24:'Обидва часові вирази — межі завершення, а не початок чи строк ухвалення рішення.',
45:'Письмовий засіб відповіді та щирий спосіб дії не підмінені часовою межею.',
49:'Минула заперечна форма виражає сильне почуття, не його відсутність; альтернативи змінюють оцінку або час.',
51:'Сильне побажання, а не безперервне промовляння чи встановлений результат відновлення.',
57:'Нестерпність змісту/видовища, а не погана чутність, відстань або достатність доказів; відділено ID85.',
80:'Відкрито заявляє без стримування; не тактовно замовчує й не чекає доведення правоти.',
85:'Підсилено вдячність/жаль; не відсутність почуття і не нестерпність видовища ID57. Винуватця події не встановлено.',
86:'Немає достатньої підстави для осуду, а не нездатність дорікнути або обов’язок осуджувати.',
94:'Власний для новачків погляд без примусу до тотожності досвідченим.',
101:'Новий масштаб діяльності тягне складніші вимоги; не лише миттєва наступна подія.',
106:'Відтінок іронії та весняні ознаки; не буквальне удавання, намір без вислову чи невизначеність наявності ознак.',
120:'Обставина прийнята як дана, з відповідними можливостями; не усунення обставини або гарантія успіху.',
121:'Власна дія в наданій нагоді; у другому прикладі дозвіл прямо названо. Не дія викладача й не майбутнє прохання.',
122:'Інша особа виконала дію, мовець отримав допомогу; не власна дія з дозволу іншого.',
123:'Виконавець — адресат. ご遠慮願います ввічливо вимагає утриматися від фотографування, не пропонує вільний вибір.',
124:'Дія іншої особи подається з повагою і вдячністю; не власний прихід мовця чи прохання скасувати участь.',
125:'Мовець отримує послугу іншої особи; умовне прохання про думку ще не означає її отримання.',
127:'Окремі значення одягати й подобатися не підміняють одне одного; отримання або замовлення форми не доведені.'}
rows=[]
for id in a['REVIEW_IDS']:
 key='g_'+str(id);contexts=[]
 for j,sentence in enumerate(g[str(id)]['examples']):
  exact=next((r for r in targets if r['kind']=='g'and r['id']==id and r['sentence']==sentence),None)
  payload=exact['quiz']if exact else q[key].get('byExample',{}).get(sentence,q[key])
  payload={k:payload[k]for k in ['correct','wrong','note']};options=[payload['correct'],*payload['wrong']]
  assert len(options)==len(set(options))==4
  assert all(not any(marker in x for marker in ['参照','接続','辞書形','基本形','【','〜','～'])for x in options)
  assert max(map(len,options))/min(map(len,options))<2.1
  contexts.append(dict(exampleIndex=j,sentence=sentence,source='exact_reviewed_retained'if exact else('byExample'if sentence in q[key].get('byExample',{})else'default'),**payload,payloadSha256=digest(payload),retainedRationale=RATIONALE[id]if exact else None,exactOrigin=('C05'if id in {120,123,124,125,127}else'C04')if exact else None))
 rows.append(dict(key=key,word=words[id],decision='retained_exact_only'if id not in a['IDS']else'authored_automatic_contexts_preserved_exact',rationale=RATIONALE.get(id,'Нові контекстні значення; українська примітка пояснює відмінність ключа від усіх трьох хибних прочитань.'),contexts=contexts))
counts=dict(collections.Counter(c['source']for r in rows for c in r['contexts']));assert counts=={'default':49,'exact_reviewed_retained':33,'byExample':42},counts
report=dict(version=144,reviewType='author_editorial_review',independentReview=False,sha256=hashlib.sha256(s.encode()).hexdigest(),reviewedCards=62,sets=49,contexts=124,newPayloads=91,retainedExactContexts=33,retainedOriginCounts={'C04':23,'C05':10},scope='All remaining grammar meaning contexts in current examples: new author data plus retained exact C04/C05. Not full cards, external examples or independent acceptance.',rows=rows,sourceCounts=counts,sources='audit144/sources.md')
(P/'editorial-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Author review: 62 cards /124 contexts; 91 new payloads /33 retained exact (23 C04 /10 C05)')
