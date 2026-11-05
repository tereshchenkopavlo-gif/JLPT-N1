"""Accept only hash-bound reports, then publish full HTML and additive author credits."""
from pathlib import Path
import json,hashlib,shutil,re,csv,io,subprocess,collections
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit149';html=ROOT/'release149/JLPT_N1_ukrainian_reading_v149.html';sha=hashlib.sha256(html.read_bytes()).hexdigest();summary=json.loads((P/'build-summary.json').read_text());assert sha==summary['sha256']=='4490611521fab2c9b713bfda7a39e327b9923e35ea16df5cca6aa1937b51ed38'
r={n:json.loads((P/f'{n}-results.json').read_text())for n in ['invariant','meaning','presentation','ui','functional','session','comparison','grammar','scope','coverage']};assert all(x['sha256']==sha for x in r.values())
assert len(r['invariant']['checks'])==22 and all(x['pass_']for x in r['invariant']['checks'])and r['invariant']['previousFilesChecked']==620
assert r['meaning']['pass']and r['meaning']['generationCases']==3164 and r['meaning']['renderedCases']==2373 and not r['meaning']['errors']
assert all(x['pass']for x in r['meaning']['generated']+r['meaning']['rendered'])and len(r['meaning']['unknownContextGuard'])==122 and all(x['unknownNote']==''and x['headwordNote']for x in r['meaning']['unknownContextGuard'])
assert all(len(r[n]['results'])==3 and all(x['pass']for x in r[n]['results'])for n in ['presentation','functional'])
assert len(r['ui']['checks'])==3 and all(all(v for k,v in x.items()if k!='width')for x in r['ui']['checks'])
assert r['session']['pass']and len(r['comparison']['results'])==12 and all(x['pass']for x in r['comparison']['results'])
assert r['grammar']['pass']and len(r['grammar']['results'])==81 and len(r['grammar']['pairResults'])==27 and all(x['pass']for x in r['grammar']['results']+r['grammar']['pairResults'])
assert r['scope']['pass']and not r['scope']['automaticGrammarIds']and len(r['scope']['savedFirstIds'])==114 and len(r['scope']['exactReviewedFirstIds'])==16 and r['scope']['guardedReadingPools']==1482 and r['scope']['guardedIdsAndCandidateCountsUnchanged']
assert r['coverage']['pass']and r['coverage']['grammarCards']==130 and r['coverage']['grammarContexts']==261 and r['coverage']['automaticCurrentContexts']==0 and all(x['pass']for x in r['coverage']['results'])
review=json.loads((P/'editorial-review.json').read_text());assert review['sha256']==sha and review['grammarCards']==27 and review['grammarPairs']==9 and not review['independentReview']
# Recreate from the frozen register, retaining every prior row and all 511 credits.
base=json.loads((P/'baseline-integrity.json').read_text())['commit'];oldcsv=subprocess.check_output(['git','show',base+':completion/review-register.csv'],cwd=ROOT,text=True);rows=list(csv.DictReader(io.StringIO(oldcsv)));targets={(x['kind'],x['key'])for x in review['rows']+review['pairs']};assert len(targets)==36
for row in rows:
 if(row['kind'],row['key'])in targets:
  assert row['finalReview']=='pending'
  row['finalReview']='reviewed';row['evidence']=f'audit149/editorial-review.json:{row["kind"]}:{row["key"]}; author linguistic review, not independent; provenance/physical excluded'
assert collections.Counter(x['finalReview']for x in rows)=={'reviewed':547,'pending':5295}
grammar_rows = [row for row in rows if row['kind'] == 'grammar']
pair_rows = [row for row in rows if row['kind'] == 'grammar_pair']
assert {row['key'] for row in grammar_rows} == {str(i) for i in range(1, 131)}
assert {row['key'] for row in pair_rows} == {str(i) for i in range(92)}
assert len(grammar_rows) == 130 and len(pair_rows) == 92
assert all(row['finalReview'] == 'reviewed' and row['evidence'] for row in grammar_rows + pair_rows)

with(ROOT/'completion/review-register.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys(),lineterminator='\n');w.writeheader();w.writerows(rows)


result = dict(
    version=149, sha256=sha, status='partial_author_review', criteria=['C10', 'C18'],
    grammarCards=27, grammarIds=summary['grammarIds'], grammarPairs=9,
    pairIndices=summary['pairIndices'], grammarExamplesRead=55, changedExampleTranslations=10,
    newRegisterCredits=36, previousReviewed=511, registerReviewed=547, registerPending=5295,
    totalHeterogeneousRegisterRows=5842, independentReview=False, fullAuditComplete=False,
    grammarContextsPreserved=261, evidence='audit149/editorial-review.json',
    remainingGrammarCards=0, remainingGrammarPairs=0, cumulativeGrammarCards=130, cumulativeGrammarPairs=92,
)
(ROOT/'completion/C10-C18-v149-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')

provenance = dict(
    version=149, sha256=sha, base='v148 / '+summary['baseSha256'],
    status='not_cleared_for_public_product',
    newMaterial='Original grammar explanations and pair notes, revised translations and completed Japanese sentence in pair 16.',
    inheritedMaterial='Japanese card examples and most comparison examples retained. Origin remains under review.',
    evidence='audit149/editorial-review.json', sources='audit149/sources.md',
    publicExposure='v149 HTML and audit in main, work/v149-checkpoint, older HTML and reachable Git history. Historical Actions packages remain in scope.',
    historicalInventory='review20261105/public-inventory.json is a frozen v141 snapshot.',
    newActionsArtifacts=False, independentReview=False,
)
(P/'provenance.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2)+'\n')
shutil.copyfile(html, ROOT/html.name)
audit = f'''# Аудит JLPT N1 v149

5 листопада 2026, Asia/Tokyo. Повний HTML має {html.stat().st_size} байтів і SHA-256 `{sha}`. Основа v148, commit `{base}`, SHA-256 `{summary['baseSha256']}`. Робочий знімок збережено в work/v149-checkpoint, commit 26b1f64925cd0553a6732d8819c3573e18304b98.

Авторський перегляд охопив **27 карток g104–g130**, їхні 55 японських прикладів з українськими перекладами та **9 порівнянь**. Індекси пар: {', '.join(map(str, summary['pairIndices']))}. Поіменні рішення й контрольні суми полів наведено в [editorial-review.json](audit149/editorial-review.json).

- У ずくめ й まみれ розділено однорідність та вкритість речовиною. У と相まって уточнено спільний ефект чинників.
- У ともなく відокремлено мимовільне сприйняття від невизначеного джерела. У つ〜つ і ては〜ては пояснено чергування дій.
- У させていただく та ていただく розмежовано власну дію за сприяння й отриману дію іншої особи. У くださる та いただく уточнено перспективу діяча й одержувача.
- У てございます пояснено стан після підготовки. У お越しになる напрямок визначає контекст.
- Уточнено вісім японських дефініцій і десять українських перекладів.

Реєстр отримав **36 нових авторських результатів**. Разом 547 reviewed і 5295 pending серед 5842 різнорідних рядків. У реєстрі завершено авторський перегляд усіх 130 граматичних карток і 92 граматичних пар. Попередні 511 результатів збережено. Звірено два розділи 文化庁 про 敬語 та словникову статтю 託ける. [Джерела й межі](audit149/sources.md)

Технічна перевірка охопила 22 групи інваріантів, 620 файлів попередніх випусків, 81 показ карток і 27 показів пари на трьох ширинах, 3164 генерації та 2373 покази зворотного зв’язку. Звірено маршрути 261 чинного граматичного контексту та 1482 записи reading-фільтра. Перевірено навігацію, експорт і відновлення прогресу, повну сесію та 12 сценаріїв 比較. Повний HTML містить 3914 слів, 130 конструкцій, 160 текстів і 381 питання читання.

Наступний етап авторського перегляду — словникові картки. C11 для решти типів вправ, незалежна експертиза, фізичні Android/Windows і походження матеріалів залишаються окремими відкритими перевірками. [Облік походження](audit149/provenance.json)
'''
(ROOT/'JLPT_N1_v149_audit.md').write_text(audit)

def original(path):
    return subprocess.check_output(['git', 'show', base+':'+path], cwd=ROOT, text=True)

readme = original('README.md')
history = readme[readme.index('Нижче збережено історичний журнал'):]
(ROOT/'README.md').write_text(f'''# JLPT N1 — тренажер з японським інтерфейсом

Актуальна **v149**. [Повний HTML]({html.name}) · [Аудит](JLPT_N1_v149_audit.md)

Переглянуто 27 граматичних карток g104–g130 та 9 порівнянь. Завершено авторський перегляд усіх 130 граматичних карток і 92 порівнянь. У реєстрі 547 авторських результатів і 5295 рядків очікують перегляду. [Докази](audit149/editorial-review.json)

3914 слів, 130 конструкцій, 160 текстів і 381 питання читання. SHA-256 `{sha}`. Перед переходом до іншого HTML збережіть резервну копію прогресу в 設定. [Попередня v148](JLPT_N1_ukrainian_reading_v148.html)

'''+history)
status = original('PROJECT_STATUS.md')
status = re.sub(r'Оновлено 5 листопада 2026, Asia/Tokyo\..*?\n\n3914', f'Оновлено 5 листопада 2026, Asia/Tokyo. Актуальна **v149**. Повний `{html.name}`, {html.stat().st_size} байтів. SHA-256 `{sha}`. Аудит JLPT_N1_v149_audit.md. Основа v148 / {base}.\n\n3914', status, count=1, flags=re.S)
section = '''## Виконано у v149 — g104–g130 та пов’язані порівняння

Авторський перегляд 27 карток, 55 прикладів і 9 порівнянь. Уточнено вісім японських дефініцій і десять українських перекладів. 36 нових результатів довели реєстр до **547 reviewed /5295 pending**. Авторський перегляд у реєстрі охопив усі 130 граматичних карток і 92 пари. Докази наведено в audit149/editorial-review.json.

22 групи інваріантів, 620 попередніх файлів, 81 показ карток і 27 показів пар. Перевірено 261 граматичний контекст, 1482 записи reading-фільтра, відновлення прогресу, повну сесію та 比較. Наступний етап авторського перегляду — словникові картки. C11, C16, незалежна експертиза та походження матеріалів залишаються відкритими.

'''
(ROOT/'PROJECT_STATUS.md').write_text(status.replace('## Виконано у v148',section+'## Виконано у v148',1))
backlog = original('completion/BACKLOG.md').replace('Поточний HTML — v148','Поточний HTML — v149')
for key, extra in {
    'C10': ' v149 додає 27 карток та 9 пар. Поточний підсумок реєстру 547/5295. Доказ completion/C10-C18-v149-result.json.',
    'C18': ' У v149 перевірено g104–g130 і 9 пов’язаних пар. Усі 130 граматичних карток і 92 пари пройшли авторський перегляд.',
}.items():
    start = backlog.index('| '+key+' |')
    end = backlog.index('\n',start)
    backlog = backlog[:end-1]+extra+' |'+backlog[end:]
(ROOT/'completion/BACKLOG.md').write_text(backlog)
print(f'v149 {sha}, 36 new author decisions, 547 reviewed and 5295 pending')
