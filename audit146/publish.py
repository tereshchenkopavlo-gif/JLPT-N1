"""Accept only hash-bound reports, then publish full HTML and additive author credits."""
from pathlib import Path
import json,hashlib,shutil,re,csv,io,subprocess,collections
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit146';html=ROOT/'release146/JLPT_N1_ukrainian_reading_v146.html';sha=hashlib.sha256(html.read_bytes()).hexdigest();summary=json.loads((P/'build-summary.json').read_text());assert sha==summary['sha256']=='c592db0746c94071ba6fed95bd8abb419b9d97636ffa3aea066d6b7e68703024'
r={n:json.loads((P/f'{n}-results.json').read_text())for n in ['invariant','meaning','presentation','ui','functional','session','comparison','grammar','scope','coverage']};assert all(x['sha256']==sha for x in r.values())
assert len(r['invariant']['checks'])==22 and all(x['pass_']for x in r['invariant']['checks'])and r['invariant']['previousFilesChecked']==512
assert r['meaning']['pass']and r['meaning']['generationCases']==3164 and r['meaning']['renderedCases']==2373 and not r['meaning']['errors']
assert all(x['pass']for x in r['meaning']['generated']+r['meaning']['rendered'])and len(r['meaning']['unknownContextGuard'])==122 and all(x['unknownNote']==''and x['headwordNote']for x in r['meaning']['unknownContextGuard'])
assert all(len(r[n]['results'])==3 and all(x['pass']for x in r[n]['results'])for n in ['presentation','functional'])
assert len(r['ui']['checks'])==3 and all(all(v for k,v in x.items()if k!='width')for x in r['ui']['checks'])
assert r['session']['pass']and len(r['comparison']['results'])==12 and all(x['pass']for x in r['comparison']['results'])
assert r['grammar']['pass']and len(r['grammar']['results'])==72 and len(r['grammar']['pairResults'])==51 and all(x['pass']for x in r['grammar']['results']+r['grammar']['pairResults'])
assert r['scope']['pass']and not r['scope']['automaticGrammarIds']and len(r['scope']['savedFirstIds'])==114 and len(r['scope']['exactReviewedFirstIds'])==16 and r['scope']['guardedReadingPools']==1482 and r['scope']['guardedIdsAndCandidateCountsUnchanged']
assert r['coverage']['pass']and r['coverage']['grammarCards']==130 and r['coverage']['grammarContexts']==261 and r['coverage']['automaticCurrentContexts']==0 and all(x['pass']for x in r['coverage']['results'])
review=json.loads((P/'editorial-review.json').read_text());assert review['sha256']==sha and review['grammarCards']==24 and review['grammarPairs']==17 and not review['independentReview']
# Recreate from the frozen register, retaining every prior row and all 396 credits.
base=json.loads((P/'baseline-integrity.json').read_text())['commit'];oldcsv=subprocess.check_output(['git','show',base+':completion/review-register.csv'],cwd=ROOT,text=True);rows=list(csv.DictReader(io.StringIO(oldcsv)));targets={(x['kind'],x['key'])for x in review['rows']+review['pairs']};assert len(targets)==41
for row in rows:
 if(row['kind'],row['key'])in targets:
  assert row['finalReview']=='pending'
  row['finalReview']='reviewed';row['evidence']=f'audit146/editorial-review.json:{row["kind"]}:{row["key"]}; author linguistic review, not independent; provenance/physical excluded'
assert collections.Counter(x['finalReview']for x in rows)=={'reviewed':437,'pending':5405}
with(ROOT/'completion/review-register.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys(),lineterminator='\n');w.writeheader();w.writerows(rows)

result = dict(
    version=146, sha256=sha, status='partial_author_review', criteria=['C10', 'C18'],
    grammarCards=24, grammarIds=summary['grammarIds'], grammarPairs=17,
    pairIndices=summary['pairIndices'], grammarExamplesRead=48, changedExampleTranslations=9,
    newRegisterCredits=41, previousReviewed=396, registerReviewed=437, registerPending=5405,
    totalHeterogeneousRegisterRows=5842, independentReview=False, fullAuditComplete=False,
    grammarContextsPreserved=261, evidence='audit146/editorial-review.json',
    remainingGrammarCards=72, remainingGrammarPairs=38,
)
(ROOT/'completion/C10-C18-v146-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')

provenance = dict(
    version=146, sha256=sha, base='v145 / '+summary['baseSha256'],
    status='not_cleared_for_public_product',
    newMaterial='Original grammar explanations and pair notes, revised translations and a completed Japanese example in pair 71.',
    inheritedMaterial='Japanese card examples and most pair examples retained. Origin remains under review.',
    evidence='audit146/editorial-review.json', sources='audit146/sources.md',
    publicExposure='v146 HTML and audit in main, work/v146-checkpoint, older HTML and reachable Git history. Historical Actions packages remain in scope.',
    historicalInventory='review20261105/public-inventory.json is a frozen v141 snapshot.',
    newActionsArtifacts=False, independentReview=False,
)
(P/'provenance.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2)+'\n')
shutil.copyfile(html, ROOT/html.name)
audit = f'''# Аудит JLPT N1 v146

5 листопада 2026, Asia/Tokyo. Повний HTML має {html.stat().st_size} байтів і SHA-256 `{sha}`. Основа v145, commit `{base}`, SHA-256 `{summary['baseSha256']}`. Незавершений робочий знімок збережено в work/v146-checkpoint, commit e36b194ae690f35637e23015a480cb1265bcb5c5.

Авторський перегляд охопив **24 картки g33–g56**, їхні 48 японських прикладів з українськими перекладами та **17 порівнянь**. Індекси пар: {', '.join(map(str, summary['pairIndices']))}. Поіменні рішення й контрольні суми полів наведено в [editorial-review.json](audit146/editorial-review.json).

- У 〜とは розмежовано завершення вислову на とは та продовження з оцінкою.
- Для 〜きらいがある уточнено сферу схильності у прикладі, а для 〜んがため відокремлено мету від жертви чи ризику, заданих контекстом.
- У 〜べく／〜べくして розмежовано мету дії та закономірність результату. У 〜べからず／〜あるまじき розділено припис і оцінку вчинку.
- У 〜をもって② враховано спосіб відповіді та ставлення під час дії. У 〜を余儀なくされる／〜を押して іменник називає відповідно вимушений крок або перешкоду.
- Уточнено дев’ять українських перекладів, зокрема значення 悪びれない та риторичний тон でなくてなんだろう. У порівнянні ごとき／のごとく перший приклад доповнено завершенням репліки.

Реєстр отримав **41 новий авторський результат**. Разом 437 reviewed і 5405 pending серед 5842 різнорідних рядків. Із граматичної партії в цьому реєстрі залишаються 72 картки й 38 пар. Історичні 396 результатів збережено. Зовнішня мовна звірка спиралася на раніше задокументовані джерела, оскільки нові звернення до вебсервісу завершилися помилкою. [Джерела й межі](audit146/sources.md)

Технічний звіт охоплює 22 групи інваріантів, 512 файлів попередніх випусків, 72 покази карток і 51 показ пари на трьох ширинах, 3164 генерації та 2373 покази зворотного зв’язку. Перевірено маршрути 261 чинного граматичного контексту, 1482 записи reading-фільтра, навігацію, імпорт та експорт прогресу, повну сесію і 12 сценаріїв 比較. База містить 3914 слів, 130 конструкцій, 160 текстів і 381 питання читання. Японські речення карток, ключі вправ, ID та формат прогресу звірено з v145.

Наступна партія починається з g58. C11 для решти типів вправ, незалежна експертиза, фізичні Android/Windows і походження матеріалів залишаються окремими відкритими перевірками. [Облік походження](audit146/provenance.json)
'''
(ROOT/'JLPT_N1_v146_audit.md').write_text(audit)

def original(path):
    return subprocess.check_output(['git', 'show', base+':'+path], cwd=ROOT, text=True)

readme = original('README.md')
history = readme[readme.index('Нижче збережено історичний журнал'):]
(ROOT/'README.md').write_text(f'''# JLPT N1 — тренажер з японським інтерфейсом

Актуальна **v146**. [Повний HTML]({html.name}) · [Аудит](JLPT_N1_v146_audit.md)

Перевірено 24 граматичні картки g33–g56 та 17 порівнянь. Уточнено емоційне 〜とは, відмінність мети від закономірного результату та дев’ять перекладів прикладів. У реєстрі 437 авторських результатів і 5405 рядків очікують перегляду. [Докази](audit146/editorial-review.json)

3914 слів, 130 конструкцій, 160 текстів і 381 питання читання. SHA-256 `{sha}`. Перед переходом до іншого HTML збережіть резервну копію прогресу в 設定. [Попередня v145](JLPT_N1_ukrainian_reading_v145.html)

'''+history)
status = original('PROJECT_STATUS.md')
status = re.sub(r'Оновлено 5 листопада 2026, Asia/Tokyo\..*?\n\n3914', f'Оновлено 5 листопада 2026, Asia/Tokyo. Актуальна **v146**. Повний `{html.name}`, {html.stat().st_size} байтів. SHA-256 `{sha}`. Аудит JLPT_N1_v146_audit.md. Основа v145 / {base}.\n\n3914', status, count=1, flags=re.S)
section = '''## Виконано у v146 — g33–g56 і пов’язані порівняння

Авторський перегляд 24 карток, 48 прикладів і 17 порівнянь. Уточнено п’ять японських дефініцій, дев’ять українських перекладів і структуру пояснень. Докази наведено в audit146/editorial-review.json. 41 новий рядок реєстру довів підсумок до **437 reviewed /5405 pending**. Залишок граматичної частини поточного реєстру — 72 картки й 38 пар.

22 групи інваріантів, 512 попередніх файлів, 72 покази карток і 51 показ пар. Перевірено 261 контекст граматичних вправ, 1482 reading guards, сумісність прогресу, повну сесію та 比較. Наступна партія починається з g58. C11, C16, незалежна експертиза та походження матеріалів залишаються відкритими.

'''
(ROOT/'PROJECT_STATUS.md').write_text(status.replace('## Виконано у v145',section+'## Виконано у v145',1))
backlog = original('completion/BACKLOG.md').replace('Поточний HTML — v145','Поточний HTML — v146')
for key, extra in {
    'C10': ' v146 додає 24 картки та 17 пар. Поточний підсумок реєстру 437/5405. Доказ completion/C10-C18-v146-result.json.',
    'C18': ' У v146 перевірено пояснення g33–g56 та 17 пов’язаних пар. Залишок граматичної частини реєстру 72 картки і 38 пар.',
}.items():
    start = backlog.index('| '+key+' |')
    end = backlog.index('\n',start)
    backlog = backlog[:end-1]+extra+' |'+backlog[end:]
(ROOT/'completion/BACKLOG.md').write_text(backlog)
print(f'v146 {sha}, 41 new author decisions, 437 reviewed and 5405 pending')
