"""Accept only hash-bound reports, then publish full HTML and additive author credits."""
from pathlib import Path
import json,hashlib,shutil,re,csv,io,subprocess,collections
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit147';html=ROOT/'release147/JLPT_N1_ukrainian_reading_v147.html';sha=hashlib.sha256(html.read_bytes()).hexdigest();summary=json.loads((P/'build-summary.json').read_text());assert sha==summary['sha256']=='35dc026700a64df05df04ea6303bcdf5524f94d7bdeb150685f5b2b0df8854f0'
r={n:json.loads((P/f'{n}-results.json').read_text())for n in ['invariant','meaning','presentation','ui','functional','session','comparison','grammar','scope','coverage']};assert all(x['sha256']==sha for x in r.values())
assert len(r['invariant']['checks'])==22 and all(x['pass_']for x in r['invariant']['checks'])and r['invariant']['previousFilesChecked']==548
assert r['meaning']['pass']and r['meaning']['generationCases']==3164 and r['meaning']['renderedCases']==2373 and not r['meaning']['errors']
assert all(x['pass']for x in r['meaning']['generated']+r['meaning']['rendered'])and len(r['meaning']['unknownContextGuard'])==122 and all(x['unknownNote']==''and x['headwordNote']for x in r['meaning']['unknownContextGuard'])
assert all(len(r[n]['results'])==3 and all(x['pass']for x in r[n]['results'])for n in ['presentation','functional'])
assert len(r['ui']['checks'])==3 and all(all(v for k,v in x.items()if k!='width')for x in r['ui']['checks'])
assert r['session']['pass']and len(r['comparison']['results'])==12 and all(x['pass']for x in r['comparison']['results'])
assert r['grammar']['pass']and len(r['grammar']['results'])==69 and len(r['grammar']['pairResults'])==51 and all(x['pass']for x in r['grammar']['results']+r['grammar']['pairResults'])
assert r['scope']['pass']and not r['scope']['automaticGrammarIds']and len(r['scope']['savedFirstIds'])==114 and len(r['scope']['exactReviewedFirstIds'])==16 and r['scope']['guardedReadingPools']==1482 and r['scope']['guardedIdsAndCandidateCountsUnchanged']
assert r['coverage']['pass']and r['coverage']['grammarCards']==130 and r['coverage']['grammarContexts']==261 and r['coverage']['automaticCurrentContexts']==0 and all(x['pass']for x in r['coverage']['results'])
review=json.loads((P/'editorial-review.json').read_text());assert review['sha256']==sha and review['grammarCards']==23 and review['grammarPairs']==17 and not review['independentReview']
# Recreate from the frozen register, retaining every prior row and all 437 credits.
base=json.loads((P/'baseline-integrity.json').read_text())['commit'];oldcsv=subprocess.check_output(['git','show',base+':completion/review-register.csv'],cwd=ROOT,text=True);rows=list(csv.DictReader(io.StringIO(oldcsv)));targets={(x['kind'],x['key'])for x in review['rows']+review['pairs']};assert len(targets)==40
for row in rows:
 if(row['kind'],row['key'])in targets:
  assert row['finalReview']=='pending'
  row['finalReview']='reviewed';row['evidence']=f'audit147/editorial-review.json:{row["kind"]}:{row["key"]}; author linguistic review, not independent; provenance/physical excluded'
assert collections.Counter(x['finalReview']for x in rows)=={'reviewed':477,'pending':5365}
with(ROOT/'completion/review-register.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys(),lineterminator='\n');w.writeheader();w.writerows(rows)


result = dict(
    version=147, sha256=sha, status='partial_author_review', criteria=['C10', 'C18'],
    grammarCards=23, grammarIds=summary['grammarIds'], grammarPairs=17,
    pairIndices=summary['pairIndices'], grammarExamplesRead=46, changedExampleTranslations=10,
    newRegisterCredits=40, previousReviewed=437, registerReviewed=477, registerPending=5365,
    totalHeterogeneousRegisterRows=5842, independentReview=False, fullAuditComplete=False,
    grammarContextsPreserved=261, evidence='audit147/editorial-review.json',
    remainingGrammarCards=49, remainingGrammarPairs=21,
)
(ROOT/'completion/C10-C18-v147-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')

provenance = dict(
    version=147, sha256=sha, base='v146 / '+summary['baseSha256'],
    status='not_cleared_for_public_product',
    newMaterial='Original grammar explanations and pair notes, revised translations and edited Japanese phrasing in pairs 21, 59 and 81.',
    inheritedMaterial='Japanese card examples and most comparison examples retained. Origin remains under review.',
    evidence='audit147/editorial-review.json', sources='audit147/sources.md',
    publicExposure='v147 HTML and audit in main, work/v147-checkpoint, older HTML and reachable Git history. Historical Actions packages remain in scope.',
    historicalInventory='review20261105/public-inventory.json is a frozen v141 snapshot.',
    newActionsArtifacts=False, independentReview=False,
)
(P/'provenance.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2)+'\n')
shutil.copyfile(html, ROOT/html.name)
audit = f'''# Аудит JLPT N1 v147

5 листопада 2026, Asia/Tokyo. Повний HTML має {html.stat().st_size} байтів і SHA-256 `{sha}`. Основа v146, commit `{base}`, SHA-256 `{summary['baseSha256']}`. Робочий знімок збережено в work/v147-checkpoint, commit 9e6bf533ff25b5830d48c7691f98e9d1da058f63.

Авторський перегляд охопив **23 картки g58–g80**, їхні 46 японських прикладів з українськими перекладами та **17 порівнянь**. Індекси пар: {', '.join(map(str, summary['pairIndices']))}. Поіменні рішення й контрольні суми полів наведено в [editorial-review.json](audit147/editorial-review.json).

- У ～ところ розділено момент події й висновок після перевірки. Порівняння з や否や тепер зіставляє саме ці вживання.
- У そばから підкреслено повторюваність. Для や否や, が早いか та なり пояснено типову будову й співвіднесення діячів.
- У かたがた, がてら та かたわら відокремлено дві справи в одній нагоді від тривалого поєднання занять.
- У ことなしに розділено неможливість з できない та оцінку належного з べきではない. Для ようものなら збережено відмінність ризику від певності.
- Уточнено п’ять японських дефініцій і десять українських перекладів. Зокрема, повернено умовність розгляду стягнення в いかんでは і припущення だろう в ようによっては.

Реєстр отримав **40 нових авторських результатів**. Разом 477 reviewed і 5365 pending серед 5842 різнорідних рядків. У граматичній частині реєстру залишаються 49 карток і 21 пара. Попередні 437 результатів збережено. Для がてら та ならいざしらず використано попередні словникові звірки. Новий зовнішній пошук завершився помилкою сервісу. [Джерела й межі](audit147/sources.md)

Технічна перевірка охопила 22 групи інваріантів, 548 файлів попередніх випусків, 69 показів карток і 51 показ пари на трьох ширинах, 3164 генерації та 2373 покази зворотного зв’язку. Звірено маршрути 261 чинного граматичного контексту та 1482 записи reading-фільтра. Перевірено навігацію, експорт і відновлення прогресу, повну сесію та 12 сценаріїв 比較. Повний HTML містить 3914 слів, 130 конструкцій, 160 текстів і 381 питання читання.

Наступна партія починається з g81. C11 для решти типів вправ, незалежна експертиза, фізичні Android/Windows і походження матеріалів залишаються окремими відкритими перевірками. [Облік походження](audit147/provenance.json)
'''
(ROOT/'JLPT_N1_v147_audit.md').write_text(audit)

def original(path):
    return subprocess.check_output(['git', 'show', base+':'+path], cwd=ROOT, text=True)

readme = original('README.md')
history = readme[readme.index('Нижче збережено історичний журнал'):]
(ROOT/'README.md').write_text(f'''# JLPT N1 — тренажер з японським інтерфейсом

Актуальна **v147**. [Повний HTML]({html.name}) · [Аудит](JLPT_N1_v147_audit.md)

Переглянуто 23 граматичні картки g58–g80 та 17 порівнянь. Уточнено два вживання ～ところ, повторюваність そばから та десять перекладів. У реєстрі 477 авторських результатів і 5365 рядків очікують перегляду. [Докази](audit147/editorial-review.json)

3914 слів, 130 конструкцій, 160 текстів і 381 питання читання. SHA-256 `{sha}`. Перед переходом до іншого HTML збережіть резервну копію прогресу в 設定. [Попередня v146](JLPT_N1_ukrainian_reading_v146.html)

'''+history)
status = original('PROJECT_STATUS.md')
status = re.sub(r'Оновлено 5 листопада 2026, Asia/Tokyo\..*?\n\n3914', f'Оновлено 5 листопада 2026, Asia/Tokyo. Актуальна **v147**. Повний `{html.name}`, {html.stat().st_size} байтів. SHA-256 `{sha}`. Аудит JLPT_N1_v147_audit.md. Основа v146 / {base}.\n\n3914', status, count=1, flags=re.S)
section = '''## Виконано у v147 — g58–g80 і пов’язані порівняння

Авторський перегляд 23 карток, 46 прикладів і 17 порівнянь. Уточнено п’ять японських дефініцій і десять українських перекладів. 40 нових результатів довели реєстр до **477 reviewed /5365 pending**. Залишок граматичної частини реєстру — 49 карток і 21 пара. Докази наведено в audit147/editorial-review.json.

22 групи інваріантів, 548 попередніх файлів, 69 показів карток і 51 показ пар. Перевірено 261 граматичний контекст, 1482 записи reading-фільтра, відновлення прогресу, повну сесію та 比較. Наступна партія починається з g81. C11, C16, незалежна експертиза та походження матеріалів залишаються відкритими.

'''
(ROOT/'PROJECT_STATUS.md').write_text(status.replace('## Виконано у v146',section+'## Виконано у v146',1))
backlog = original('completion/BACKLOG.md').replace('Поточний HTML — v146','Поточний HTML — v147')
for key, extra in {
    'C10': ' v147 додає 23 картки та 17 пар. Поточний підсумок реєстру 477/5365. Доказ completion/C10-C18-v147-result.json.',
    'C18': ' У v147 перевірено g58–g80 і 17 пов’язаних пар. Залишок граматичної частини реєстру 49 карток і 21 пара.',
}.items():
    start = backlog.index('| '+key+' |')
    end = backlog.index('\n',start)
    backlog = backlog[:end-1]+extra+' |'+backlog[end:]
(ROOT/'completion/BACKLOG.md').write_text(backlog)
print(f'v147 {sha}, 40 new author decisions, 477 reviewed and 5365 pending')
