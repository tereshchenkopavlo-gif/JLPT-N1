"""Accept only hash-bound reports, then publish full HTML and additive author credits."""
from pathlib import Path
import json,hashlib,shutil,re,csv,io,subprocess,collections
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit148';html=ROOT/'release148/JLPT_N1_ukrainian_reading_v148.html';sha=hashlib.sha256(html.read_bytes()).hexdigest();summary=json.loads((P/'build-summary.json').read_text());assert sha==summary['sha256']=='eedf3b91ec0fe31ec6a51414b36b4fbbab229b9feb6065402088fc6ccd6af60e'
r={n:json.loads((P/f'{n}-results.json').read_text())for n in ['invariant','meaning','presentation','ui','functional','session','comparison','grammar','scope','coverage']};assert all(x['sha256']==sha for x in r.values())
assert len(r['invariant']['checks'])==22 and all(x['pass_']for x in r['invariant']['checks'])and r['invariant']['previousFilesChecked']==584
assert r['meaning']['pass']and r['meaning']['generationCases']==3164 and r['meaning']['renderedCases']==2373 and not r['meaning']['errors']
assert all(x['pass']for x in r['meaning']['generated']+r['meaning']['rendered'])and len(r['meaning']['unknownContextGuard'])==122 and all(x['unknownNote']==''and x['headwordNote']for x in r['meaning']['unknownContextGuard'])
assert all(len(r[n]['results'])==3 and all(x['pass']for x in r[n]['results'])for n in ['presentation','functional'])
assert len(r['ui']['checks'])==3 and all(all(v for k,v in x.items()if k!='width')for x in r['ui']['checks'])
assert r['session']['pass']and len(r['comparison']['results'])==12 and all(x['pass']for x in r['comparison']['results'])
assert r['grammar']['pass']and len(r['grammar']['results'])==66 and len(r['grammar']['pairResults'])==36 and all(x['pass']for x in r['grammar']['results']+r['grammar']['pairResults'])
assert r['scope']['pass']and not r['scope']['automaticGrammarIds']and len(r['scope']['savedFirstIds'])==114 and len(r['scope']['exactReviewedFirstIds'])==16 and r['scope']['guardedReadingPools']==1482 and r['scope']['guardedIdsAndCandidateCountsUnchanged']
assert r['coverage']['pass']and r['coverage']['grammarCards']==130 and r['coverage']['grammarContexts']==261 and r['coverage']['automaticCurrentContexts']==0 and all(x['pass']for x in r['coverage']['results'])
review=json.loads((P/'editorial-review.json').read_text());assert review['sha256']==sha and review['grammarCards']==22 and review['grammarPairs']==12 and not review['independentReview']
# Recreate from the frozen register, retaining every prior row and all 477 credits.
base=json.loads((P/'baseline-integrity.json').read_text())['commit'];oldcsv=subprocess.check_output(['git','show',base+':completion/review-register.csv'],cwd=ROOT,text=True);rows=list(csv.DictReader(io.StringIO(oldcsv)));targets={(x['kind'],x['key'])for x in review['rows']+review['pairs']};assert len(targets)==34
for row in rows:
 if(row['kind'],row['key'])in targets:
  assert row['finalReview']=='pending'
  row['finalReview']='reviewed';row['evidence']=f'audit148/editorial-review.json:{row["kind"]}:{row["key"]}; author linguistic review, not independent; provenance/physical excluded'
assert collections.Counter(x['finalReview']for x in rows)=={'reviewed':511,'pending':5331}
with(ROOT/'completion/review-register.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys(),lineterminator='\n');w.writeheader();w.writerows(rows)


result = dict(
    version=148, sha256=sha, status='partial_author_review', criteria=['C10', 'C18'],
    grammarCards=22, grammarIds=summary['grammarIds'], grammarPairs=12,
    pairIndices=summary['pairIndices'], grammarExamplesRead=44, changedExampleTranslations=11,
    newRegisterCredits=34, previousReviewed=477, registerReviewed=511, registerPending=5331,
    totalHeterogeneousRegisterRows=5842, independentReview=False, fullAuditComplete=False,
    grammarContextsPreserved=261, evidence='audit148/editorial-review.json',
    remainingGrammarCards=27, remainingGrammarPairs=9,
)
(ROOT/'completion/C10-C18-v148-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')

provenance = dict(
    version=148, sha256=sha, base='v147 / '+summary['baseSha256'],
    status='not_cleared_for_public_product',
    newMaterial='Original grammar explanations and pair notes, revised translations and normalized Japanese spelling in pair 66.',
    inheritedMaterial='Japanese card examples and most comparison examples retained. Origin remains under review.',
    evidence='audit148/editorial-review.json', sources='audit148/sources.md',
    publicExposure='v148 HTML and audit in main, work/v148-checkpoint, older HTML and reachable Git history. Historical Actions packages remain in scope.',
    historicalInventory='review20261105/public-inventory.json is a frozen v141 snapshot.',
    newActionsArtifacts=False, independentReview=False,
)
(P/'provenance.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2)+'\n')
shutil.copyfile(html, ROOT/html.name)
audit = f'''# Аудит JLPT N1 v148

5 листопада 2026, Asia/Tokyo. Повний HTML має {html.stat().st_size} байтів і SHA-256 `{sha}`. Основа v147, commit `{base}`, SHA-256 `{summary['baseSha256']}`. Робочий знімок збережено в work/v148-checkpoint, commit 0b350ff49f575995d2b3fd7e864201c919c6b618.

Авторський перегляд охопив **22 картки g81–g84 і g86–g103**, їхні 44 японські прикладів з українськими перекладами та **12 порівнянь**. Індекси пар: {', '.join(map(str, summary['pairIndices']))}. Поіменні рішення й контрольні суми полів наведено в [editorial-review.json](audit148/editorial-review.json).

- У までもない й にあたらない розмежовано зайву дію та брак підстав для реакції. Для ないまでも уточнено роль поступки й силу вимоги в продовженні.
- У ずにはすまない та ずにはおかない розділено необхідність владнати справу, сильний вплив і рішучий намір. У перекладі прикладу з фільмом збережено прогноз だろう.
- У にして розділено часовий орієнтир і поєднання ролей. У たる者 пояснено, що норму поведінки задає продовження.
- У んばかり враховано образний ступінь і враження близької події. У に足る відокремлено відповідність критерію від моральної оцінки.
- Уточнено шість японських дефініцій та одинадцять українських перекладів.

Реєстр отримав **34 нові авторські результати**. Разом 511 reviewed і 5331 pending серед 5842 різнорідних рядків. У граматичній частині реєстру залишаються 27 карток і 9 пар. Попередні 477 результатів збережено. Три джерела відкрито напряму й звірено для に越したことはない, ずにはおかない та にして. Загальний пошук повернув помилку, а стаття 足る на goo була недоступна. [Джерела й межі](audit148/sources.md)

Технічна перевірка охопила 22 групи інваріантів, 584 файли попередніх випусків, 66 показів карток і 36 показів пари на трьох ширинах, 3164 генерації та 2373 покази зворотного зв’язку. Звірено маршрути 261 чинного граматичного контексту та 1482 записи reading-фільтра. Перевірено навігацію, експорт і відновлення прогресу, повну сесію та 12 сценаріїв 比較. Повний HTML містить 3914 слів, 130 конструкцій, 160 текстів і 381 питання читання.

Наступна партія починається з g104. C11 для решти типів вправ, незалежна експертиза, фізичні Android/Windows і походження матеріалів залишаються окремими відкритими перевірками. [Облік походження](audit148/provenance.json)
'''
(ROOT/'JLPT_N1_v148_audit.md').write_text(audit)

def original(path):
    return subprocess.check_output(['git', 'show', base+':'+path], cwd=ROOT, text=True)

readme = original('README.md')
history = readme[readme.index('Нижче збережено історичний журнал'):]
(ROOT/'README.md').write_text(f'''# JLPT N1 — тренажер з японським інтерфейсом

Актуальна **v148**. [Повний HTML]({html.name}) · [Аудит](JLPT_N1_v148_audit.md)

Переглянуто 22 граматичні картки g81–g84 і g86–g103 та 12 порівнянь. Розмежовано ずにはすまない і ずにはおかない та уточнено одинадцять перекладів. У реєстрі 511 авторських результатів і 5331 рядків очікують перегляду. [Докази](audit148/editorial-review.json)

3914 слів, 130 конструкцій, 160 текстів і 381 питання читання. SHA-256 `{sha}`. Перед переходом до іншого HTML збережіть резервну копію прогресу в 設定. [Попередня v147](JLPT_N1_ukrainian_reading_v147.html)

'''+history)
status = original('PROJECT_STATUS.md')
status = re.sub(r'Оновлено 5 листопада 2026, Asia/Tokyo\..*?\n\n3914', f'Оновлено 5 листопада 2026, Asia/Tokyo. Актуальна **v148**. Повний `{html.name}`, {html.stat().st_size} байтів. SHA-256 `{sha}`. Аудит JLPT_N1_v148_audit.md. Основа v147 / {base}.\n\n3914', status, count=1, flags=re.S)
section = '''## Виконано у v148 — g81–g84, g86–g103 та пов’язані порівняння

Авторський перегляд 22 карток, 44 прикладів і 12 порівнянь. Уточнено шість японських дефініцій і одинадцять українських перекладів. 34 нові результати довели реєстр до **511 reviewed /5331 pending**. Залишок граматичної частини реєстру — 27 карток і 9 пар. Докази наведено в audit148/editorial-review.json.

22 групи інваріантів, 584 попередні файли, 66 показів карток і 36 показів пар. Перевірено 261 граматичний контекст, 1482 записи reading-фільтра, відновлення прогресу, повну сесію та 比較. Наступна партія починається з g104. C11, C16, незалежна експертиза та походження матеріалів залишаються відкритими.

'''
(ROOT/'PROJECT_STATUS.md').write_text(status.replace('## Виконано у v147',section+'## Виконано у v147',1))
backlog = original('completion/BACKLOG.md').replace('Поточний HTML — v147','Поточний HTML — v148')
for key, extra in {
    'C10': ' v148 додає 22 картки та 12 пар. Поточний підсумок реєстру 511/5331. Доказ completion/C10-C18-v148-result.json.',
    'C18': ' У v148 перевірено g81–g84 і g86–g103 і 12 пов’язаних пар. Залишок граматичної частини реєстру 27 карток і 9 пар.',
}.items():
    start = backlog.index('| '+key+' |')
    end = backlog.index('\n',start)
    backlog = backlog[:end-1]+extra+' |'+backlog[end:]
(ROOT/'completion/BACKLOG.md').write_text(backlog)
print(f'v148 {sha}, 34 new author decisions, 511 reviewed and 5331 pending')
