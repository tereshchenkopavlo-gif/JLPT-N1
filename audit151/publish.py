"""Accept only hash-bound reports, then publish full HTML and additive author credits."""
from pathlib import Path
import json,hashlib,shutil,re,csv,io,subprocess,collections
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit151';html=ROOT/'release151/JLPT_N1_ukrainian_reading_v151.html';sha=hashlib.sha256(html.read_bytes()).hexdigest();summary=json.loads((P/'build-summary.json').read_text());assert sha==summary['sha256']=='8344b61d1e84b6d9251218bc2334c9336bb2409cdd9a36f8307a349d6d4e57b7'
r={n:json.loads((P/f'{n}-results.json').read_text())for n in ['invariant','meaning','presentation','ui','functional','session','comparison','vocab','scope','coverage']};assert all(x['sha256']==sha for x in r.values())
assert len(r['invariant']['checks'])==23 and all(x['pass_']for x in r['invariant']['checks'])and r['invariant']['previousFilesChecked']==692
assert r['meaning']['pass']and r['meaning']['generationCases']==3164 and r['meaning']['renderedCases']==2373 and not r['meaning']['errors']
assert all(x['pass']for x in r['meaning']['generated']+r['meaning']['rendered'])and len(r['meaning']['unknownContextGuard'])==122 and all(x['unknownNote']==''and x['headwordNote']for x in r['meaning']['unknownContextGuard'])
assert all(len(r[n]['results'])==3 and all(x['pass']for x in r[n]['results'])for n in ['presentation','functional'])
assert len(r['ui']['checks'])==3 and all(all(v for k,v in x.items()if k!='width')for x in r['ui']['checks'])
assert r['session']['pass']and len(r['comparison']['results'])==12 and all(x['pass']for x in r['comparison']['results'])
assert r['vocab']['pass'] and len(r['vocab']['results']) == 90 and all(x['pass'] for x in r['vocab']['results'])
assert r['scope']['pass']and not r['scope']['automaticGrammarIds']and len(r['scope']['savedFirstIds'])==114 and len(r['scope']['exactReviewedFirstIds'])==16 and r['scope']['guardedReadingPools']==1482 and r['scope']['guardedIdsAndCandidateCountsUnchanged']
assert r['coverage']['pass']and r['coverage']['grammarCards']==130 and r['coverage']['grammarContexts']==261 and r['coverage']['automaticCurrentContexts']==0 and all(x['pass']for x in r['coverage']['results'])
review=json.loads((P/'editorial-review.json').read_text());assert review['sha256']==sha and review['vocabCards']==30 and review['examplesRead']==60 and not review['independentReview']
# Recreate from the frozen register, retaining every prior row and all 577 credits.
base=json.loads((P/'baseline-integrity.json').read_text())['commit'];oldcsv=subprocess.check_output(['git','show',base+':completion/review-register.csv'],cwd=ROOT,text=True);rows=list(csv.DictReader(io.StringIO(oldcsv)));targets={(x['kind'],x['key'])for x in review['rows']};assert len(targets)==30
for row in rows:
 if(row['kind'],row['key'])in targets:
  assert row['finalReview']=='pending'
  row['finalReview']='reviewed';row['evidence']=f'audit151/editorial-review.json:{row["kind"]}:{row["key"]}; author linguistic review, not independent; provenance/physical excluded'
assert collections.Counter(x['finalReview']for x in rows)=={'reviewed':607,'pending':5235}
grammar_rows = [row for row in rows if row['kind'] == 'grammar']
pair_rows = [row for row in rows if row['kind'] == 'grammar_pair']
assert {row['key'] for row in grammar_rows} == {str(i) for i in range(1, 131)}
assert {row['key'] for row in pair_rows} == {str(i) for i in range(92)}
assert len(grammar_rows) == 130 and len(pair_rows) == 92
assert all(row['finalReview'] == 'reviewed' and row['evidence'] for row in grammar_rows + pair_rows)

with(ROOT/'completion/review-register.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys(),lineterminator='\n');w.writeheader();w.writerows(rows)



result = dict(
    version=151, sha256=sha, status='partial_author_review', criteria=['C10','C18'],
    vocabIds=summary['vocabIds'], vocabCards=30, examplesRead=60, vocabCardsEdited=18,
    changedExampleTranslations=12, newRegisterCredits=30, previousReviewed=577,
    registerReviewed=607, registerPending=5235, remainingVocabularyCards=3854,
    cumulativeGrammarCards=130, cumulativeGrammarPairs=92,
    independentReview=False, fullAuditComplete=False, evidence='audit151/editorial-review.json',
)
(ROOT/'completion/C10-C18-v151-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
provenance = dict(
    version=151, sha256=sha, base='v150 / '+summary['baseSha256'],
    status='not_cleared_for_public_product',
    newMaterial='Original edits to Japanese definitions, Ukrainian explanations and translations of inherited examples.',
    inheritedMaterial='Japanese example sentences and pair material retained. Origin remains under review.',
    evidence='audit151/editorial-review.json', sources='audit151/sources.md',
    publicExposure='v151 HTML and audit in main, work/v151-checkpoint, older HTML and reachable Git history. Historical Actions packages remain in scope.',
    historicalInventory='review20261105/public-inventory.json is a frozen v141 snapshot.',
    newActionsArtifacts=False, independentReview=False,
)
(P/'provenance.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2)+'\n')
shutil.copyfile(html, ROOT/html.name)

audit = f'''# Аудит JLPT N1 v151

5 листопада 2026, Asia/Tokyo. Повний HTML має {html.stat().st_size} байтів і SHA-256 `{sha}`. Основа v150, commit `{base}`, SHA-256 `{summary['baseSha256']}`. Робочий знімок збережено в work/v151-checkpoint, commit 6d7bb805dd73e34d3a7a1e50496d8ea7525ed858.

Ця словникова партія охопила **30 карток, ID 31–60, і 60 прикладів**. Перевірено читання, частину мови, японську дефініцію, українське значення, вживання, пов’язані слова й переклади. У 18 картках відредаговано одне або кілька полів. Для решти зафіксовано рішення зберегти вміст. [Поіменні рішення](audit151/editorial-review.json)

- У 回復 і 拡大 японська дефініція тепер охоплює і зміну стану, і дію того, хто спричиняє зміну.
- У 回収 уточнено значення збирання, відкликання продукції та повернення виданих коштів. Для 学歴 уточнено освітню біографію.
- Для 簡易 звірено іменникову й прикметникову ролі. Для 機関 уточнено відмінність між установою та двигуном.
- Уточнено **12 українських перекладів**. Для 規格外 збережено нижчу ціну без припущення про оголошену знижку. Для 規制 точніше передано посилення обмежень на викиди.

Три статті デジタル大辞泉 звірено за прямими посиланнями. Загальний пошук повернув помилку. Для решти карток зафіксовано авторський контекстний перегляд. Словникові пари мають окремі рядки в реєстрі. [Джерела й межі](audit151/sources.md)

До реєстру додано **30 авторських результатів**. Разом 607 reviewed і 5235 pending серед 5842 різнорідних рядків. Перегляд словникових карток охопив 60 із 3914, наступна картка має ID 61. Усі 130 граматичних карток і 92 порівняння зберігають попередні результати.

Технічна перевірка охопила 23 групи інваріантів, 692 попередніх файли, 90 показів карток на трьох ширинах, 3164 генерації й 2373 покази зворотного зв’язку. Звірено 261 граматичний контекст, 1482 записи reading-фільтра, навігацію, імпорт і експорт прогресу та повну сесію. HTML містить 3914 слів, 130 конструкцій, 160 текстів і 381 питання читання. Незалежне мовне приймання, фізичні Android/Windows та походження матеріалів залишаються відкритими. [Облік походження](audit151/provenance.json)
'''
(ROOT/'JLPT_N1_v151_audit.md').write_text(audit)

def original(path):
    return subprocess.check_output(['git','show',base+':'+path], cwd=ROOT, text=True)

readme = original('README.md')
history = readme[readme.index('Нижче збережено історичний журнал'):]
(ROOT/'README.md').write_text(f'''# JLPT N1 — тренажер з японським інтерфейсом

Актуальна **v151**. [Повний HTML]({html.name}) · [Аудит](JLPT_N1_v151_audit.md)

Переглянуто словникові картки 31–60 і 60 прикладів. Уточнено 12 перекладів і пояснення 回収, 回復 та 簡易. У реєстрі 607 авторських результатів і 5235 рядків очікують перегляду. [Докази](audit151/editorial-review.json)

3914 слів, 130 конструкцій, 160 текстів і 381 питання читання. SHA-256 `{sha}`. Перед переходом до іншого HTML збережіть резервну копію прогресу в 設定. [Попередня v150](JLPT_N1_ukrainian_reading_v150.html)

'''+history)
status = original('PROJECT_STATUS.md')
status = re.sub(r'Оновлено 5 листопада 2026, Asia/Tokyo\..*?\n\n3914',
    f'Оновлено 5 листопада 2026, Asia/Tokyo. Актуальна **v151**. Повний `{html.name}`, {html.stat().st_size} байтів. SHA-256 `{sha}`. Аудит JLPT_N1_v151_audit.md. Основа v150 / {base}.\n\n3914',
    status, count=1, flags=re.S)
section = '''## Виконано у v151 — словникові картки 31–60

Авторський перегляд 30 карток і 60 прикладів. Відредаговано 18 карток та 12 перекладів. У реєстрі 607 reviewed і 5235 pending. Словникових карток переглянуто 60 із 3914. Наступний ID 61. Докази наведено в audit151/editorial-review.json.

23 групи інваріантів, 692 попередніх файли і 90 показів словникових карток. Перевірено 261 граматичний контекст, 1482 записи reading-фільтра, відновлення прогресу та повну сесію.

'''
(ROOT/'PROJECT_STATUS.md').write_text(status.replace('## Виконано у v150',section+'## Виконано у v150',1))
backlog = original('completion/BACKLOG.md').replace('Поточний HTML — v150','Поточний HTML — v151')
for key, extra in {
    'C10': ' v151 додає 30 словникових карток. Поточний підсумок реєстру 607/5235.',
    'C18': ' У v151 переглянуто картки 31–60. Доказ completion/C10-C18-v151-result.json.',
}.items():
    start = backlog.index('| '+key+' |')
    end = backlog.index('\n',start)
    backlog = backlog[:end-1]+extra+' |'+backlog[end:]
(ROOT/'completion/BACKLOG.md').write_text(backlog)
print(f'v151 {sha}, 30 new author decisions, 607 reviewed and 5235 pending')
