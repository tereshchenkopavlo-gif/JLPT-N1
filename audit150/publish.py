"""Accept only hash-bound reports, then publish full HTML and additive author credits."""
from pathlib import Path
import json,hashlib,shutil,re,csv,io,subprocess,collections
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit150';html=ROOT/'release150/JLPT_N1_ukrainian_reading_v150.html';sha=hashlib.sha256(html.read_bytes()).hexdigest();summary=json.loads((P/'build-summary.json').read_text());assert sha==summary['sha256']=='02fa1c3e6bdcf44b8bf3a50afd39b55287567b8ed63da9da55a6b4d29de85c84'
r={n:json.loads((P/f'{n}-results.json').read_text())for n in ['invariant','meaning','presentation','ui','functional','session','comparison','vocab','scope','coverage']};assert all(x['sha256']==sha for x in r.values())
assert len(r['invariant']['checks'])==23 and all(x['pass_']for x in r['invariant']['checks'])and r['invariant']['previousFilesChecked']==656
assert r['meaning']['pass']and r['meaning']['generationCases']==3164 and r['meaning']['renderedCases']==2373 and not r['meaning']['errors']
assert all(x['pass']for x in r['meaning']['generated']+r['meaning']['rendered'])and len(r['meaning']['unknownContextGuard'])==122 and all(x['unknownNote']==''and x['headwordNote']for x in r['meaning']['unknownContextGuard'])
assert all(len(r[n]['results'])==3 and all(x['pass']for x in r[n]['results'])for n in ['presentation','functional'])
assert len(r['ui']['checks'])==3 and all(all(v for k,v in x.items()if k!='width')for x in r['ui']['checks'])
assert r['session']['pass']and len(r['comparison']['results'])==12 and all(x['pass']for x in r['comparison']['results'])
assert r['vocab']['pass'] and len(r['vocab']['results']) == 90 and all(x['pass'] for x in r['vocab']['results'])
assert r['scope']['pass']and not r['scope']['automaticGrammarIds']and len(r['scope']['savedFirstIds'])==114 and len(r['scope']['exactReviewedFirstIds'])==16 and r['scope']['guardedReadingPools']==1482 and r['scope']['guardedIdsAndCandidateCountsUnchanged']
assert r['coverage']['pass']and r['coverage']['grammarCards']==130 and r['coverage']['grammarContexts']==261 and r['coverage']['automaticCurrentContexts']==0 and all(x['pass']for x in r['coverage']['results'])
review=json.loads((P/'editorial-review.json').read_text());assert review['sha256']==sha and review['vocabCards']==30 and review['examplesRead']==60 and not review['independentReview']
# Recreate from the frozen register, retaining every prior row and all 547 credits.
base=json.loads((P/'baseline-integrity.json').read_text())['commit'];oldcsv=subprocess.check_output(['git','show',base+':completion/review-register.csv'],cwd=ROOT,text=True);rows=list(csv.DictReader(io.StringIO(oldcsv)));targets={(x['kind'],x['key'])for x in review['rows']};assert len(targets)==30
for row in rows:
 if(row['kind'],row['key'])in targets:
  assert row['finalReview']=='pending'
  row['finalReview']='reviewed';row['evidence']=f'audit150/editorial-review.json:{row["kind"]}:{row["key"]}; author linguistic review, not independent; provenance/physical excluded'
assert collections.Counter(x['finalReview']for x in rows)=={'reviewed':577,'pending':5265}
grammar_rows = [row for row in rows if row['kind'] == 'grammar']
pair_rows = [row for row in rows if row['kind'] == 'grammar_pair']
assert {row['key'] for row in grammar_rows} == {str(i) for i in range(1, 131)}
assert {row['key'] for row in pair_rows} == {str(i) for i in range(92)}
assert len(grammar_rows) == 130 and len(pair_rows) == 92
assert all(row['finalReview'] == 'reviewed' and row['evidence'] for row in grammar_rows + pair_rows)

with(ROOT/'completion/review-register.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys(),lineterminator='\n');w.writeheader();w.writerows(rows)



result = dict(
    version=150, sha256=sha, status='partial_author_review', criteria=['C10','C18'],
    vocabIds=summary['vocabIds'], vocabCards=30, examplesRead=60, vocabCardsEdited=18,
    changedExampleTranslations=13, newRegisterCredits=30, previousReviewed=547,
    registerReviewed=577, registerPending=5265, remainingVocabularyCards=3884,
    cumulativeGrammarCards=130, cumulativeGrammarPairs=92,
    independentReview=False, fullAuditComplete=False, evidence='audit150/editorial-review.json',
)
(ROOT/'completion/C10-C18-v150-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
provenance = dict(
    version=150, sha256=sha, base='v149 / '+summary['baseSha256'],
    status='not_cleared_for_public_product',
    newMaterial='Original edits to Japanese definitions, Ukrainian explanations and translations of inherited examples.',
    inheritedMaterial='Japanese example sentences and pair material retained. Origin remains under review.',
    evidence='audit150/editorial-review.json', sources='audit150/sources.md',
    publicExposure='v150 HTML and audit in main, work/v150-checkpoint, older HTML and reachable Git history. Historical Actions packages remain in scope.',
    historicalInventory='review20261105/public-inventory.json is a frozen v141 snapshot.',
    newActionsArtifacts=False, independentReview=False,
)
(P/'provenance.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2)+'\n')
shutil.copyfile(html, ROOT/html.name)

audit = f'''# Аудит JLPT N1 v150

5 листопада 2026, Asia/Tokyo. Повний HTML має {html.stat().st_size} байтів і SHA-256 `{sha}`. Основа v149, commit `{base}`, SHA-256 `{summary['baseSha256']}`. Робочий знімок збережено в work/v150-checkpoint, commit d57310d778d6450248901c140e626e9f7c88695b.

Перша словникова партія охопила **30 карток, ID 1–30, і 60 прикладів**. Перевірено читання, частину мови, японську дефініцію, українське значення, вживання, пов’язані слова й переклади. У 18 картках відредаговано одне або кілька полів. Для решти зафіксовано рішення зберегти вміст. [Поіменні рішення](audit150/editorial-review.json)

- Для 依存 підтверджено いそん та いぞん і додано обидва варіанти до пояснення. Ключ вправ зберігає いぞん.
- В 運営 охоплено ведення роботи установи й проведення заходу. В 運用 розглянуто практичне застосування системи та управління коштами.
- У 横顔 розрізнено профіль обличчя й маловідомі риси людини. У першому перекладі 取材 передано як збирання матеріалу, у другому збережено образ профілю.
- Уточнено **13 українських перекладів**. Зокрема, 保護 в прикладі з 家出 передано без припущення про формальну опіку, а 不具合 у прикладі з 過程 — як виробничий збій.

Три статті デジタル大辞泉 звірено за прямими посиланнями. Загальний пошук повернув помилку. Для решти карток зафіксовано авторський контекстний перегляд. Словникові пари мають окремі рядки в реєстрі. [Джерела й межі](audit150/sources.md)

До реєстру додано **30 авторських результатів**. Разом 577 reviewed і 5265 pending серед 5842 різнорідних рядків. Перегляд словникових карток охопив 30 із 3914, наступна картка має ID 31. Усі 130 граматичних карток і 92 порівняння зберігають попередні результати.

Технічна перевірка охопила 23 групи інваріантів, 656 попередніх файлів, 90 показів карток на трьох ширинах, 3164 генерації й 2373 покази зворотного зв’язку. Звірено 261 граматичний контекст, 1482 записи reading-фільтра, навігацію, імпорт і експорт прогресу та повну сесію. HTML містить 3914 слів, 130 конструкцій, 160 текстів і 381 питання читання. Незалежне мовне приймання, фізичні Android/Windows та походження матеріалів залишаються відкритими. [Облік походження](audit150/provenance.json)
'''
(ROOT/'JLPT_N1_v150_audit.md').write_text(audit)

def original(path):
    return subprocess.check_output(['git','show',base+':'+path], cwd=ROOT, text=True)

readme = original('README.md')
history = readme[readme.index('Нижче збережено історичний журнал'):]
(ROOT/'README.md').write_text(f'''# JLPT N1 — тренажер з японським інтерфейсом

Актуальна **v150**. [Повний HTML]({html.name}) · [Аудит](JLPT_N1_v150_audit.md)

Переглянуто перші 30 словникових карток і 60 прикладів. Уточнено 13 перекладів та пояснення читань 依存 і двох значень 横顔. У реєстрі 577 авторських результатів і 5265 рядків очікують перегляду. [Докази](audit150/editorial-review.json)

3914 слів, 130 конструкцій, 160 текстів і 381 питання читання. SHA-256 `{sha}`. Перед переходом до іншого HTML збережіть резервну копію прогресу в 設定. [Попередня v149](JLPT_N1_ukrainian_reading_v149.html)

'''+history)
status = original('PROJECT_STATUS.md')
status = re.sub(r'Оновлено 5 листопада 2026, Asia/Tokyo\..*?\n\n3914',
    f'Оновлено 5 листопада 2026, Asia/Tokyo. Актуальна **v150**. Повний `{html.name}`, {html.stat().st_size} байтів. SHA-256 `{sha}`. Аудит JLPT_N1_v150_audit.md. Основа v149 / {base}.\n\n3914',
    status, count=1, flags=re.S)
section = '''## Виконано у v150 — словникові картки 1–30

Авторський перегляд 30 карток і 60 прикладів. Відредаговано 18 карток та 13 перекладів. У реєстрі 577 reviewed і 5265 pending. Словникових карток переглянуто 30 із 3914. Наступний ID 31. Докази наведено в audit150/editorial-review.json.

23 групи інваріантів, 656 попередніх файлів і 90 показів словникових карток. Перевірено 261 граматичний контекст, 1482 записи reading-фільтра, відновлення прогресу та повну сесію.

'''
(ROOT/'PROJECT_STATUS.md').write_text(status.replace('## Виконано у v149',section+'## Виконано у v149',1))
backlog = original('completion/BACKLOG.md').replace('Поточний HTML — v149','Поточний HTML — v150')
for key, extra in {
    'C10': ' v150 відкриває словниковий етап і додає 30 карток. Поточний підсумок реєстру 577/5265.',
    'C18': ' У v150 переглянуто картки 1–30. Доказ completion/C10-C18-v150-result.json.',
}.items():
    start = backlog.index('| '+key+' |')
    end = backlog.index('\n',start)
    backlog = backlog[:end-1]+extra+' |'+backlog[end:]
(ROOT/'completion/BACKLOG.md').write_text(backlog)
print(f'v150 {sha}, 30 new author decisions, 577 reviewed and 5265 pending')
