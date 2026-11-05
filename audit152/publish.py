"""Accept only hash-bound reports, then publish full HTML and additive author credits."""
from pathlib import Path
import json,hashlib,shutil,re,csv,io,subprocess,collections
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit152';html=ROOT/'release152/JLPT_N1_ukrainian_reading_v152.html';sha=hashlib.sha256(html.read_bytes()).hexdigest();summary=json.loads((P/'build-summary.json').read_text());assert sha==summary['sha256']=='4e4e6ab182ba0dd2fe52580d7f58a3bd3ee89cbabb669ac0d521bd0f9c6341e3'
r={n:json.loads((P/f'{n}-results.json').read_text())for n in ['invariant','meaning','presentation','ui','functional','session','comparison','vocab','scope','coverage']};assert all(x['sha256']==sha for x in r.values())
assert len(r['invariant']['checks'])==23 and all(x['pass_']for x in r['invariant']['checks'])and r['invariant']['previousFilesChecked']==728
assert r['meaning']['pass']and r['meaning']['generationCases']==3164 and r['meaning']['renderedCases']==2373 and not r['meaning']['errors']
assert all(x['pass']for x in r['meaning']['generated']+r['meaning']['rendered'])and len(r['meaning']['unknownContextGuard'])==122 and all(x['unknownNote']==''and x['headwordNote']for x in r['meaning']['unknownContextGuard'])
assert all(len(r[n]['results'])==3 and all(x['pass']for x in r[n]['results'])for n in ['presentation','functional'])
assert len(r['ui']['checks'])==3 and all(all(v for k,v in x.items()if k!='width')for x in r['ui']['checks'])
assert r['session']['pass']and len(r['comparison']['results'])==12 and all(x['pass']for x in r['comparison']['results'])
assert r['vocab']['pass'] and len(r['vocab']['results']) == 180 and all(x['pass'] for x in r['vocab']['results'])
assert r['scope']['pass']and not r['scope']['automaticGrammarIds']and len(r['scope']['savedFirstIds'])==114 and len(r['scope']['exactReviewedFirstIds'])==16 and r['scope']['guardedReadingPools']==1482 and r['scope']['guardedIdsAndCandidateCountsUnchanged']
assert r['coverage']['pass']and r['coverage']['grammarCards']==130 and r['coverage']['grammarContexts']==261 and r['coverage']['automaticCurrentContexts']==0 and all(x['pass']for x in r['coverage']['results'])
review=json.loads((P/'editorial-review.json').read_text());assert review['sha256']==sha and review['vocabCards']==60 and review['examplesRead']==120 and not review['independentReview']
# Recreate from the frozen register, retaining every prior row and all 607 credits.
base=json.loads((P/'baseline-integrity.json').read_text())['commit'];oldcsv=subprocess.check_output(['git','show',base+':completion/review-register.csv'],cwd=ROOT,text=True);rows=list(csv.DictReader(io.StringIO(oldcsv)));targets={(x['kind'],x['key'])for x in review['rows']};assert len(targets)==60
for row in rows:
 if(row['kind'],row['key'])in targets:
  assert row['finalReview']=='pending'
  row['finalReview']='reviewed';row['evidence']=f'audit152/editorial-review.json:{row["kind"]}:{row["key"]}; author linguistic review, not independent; provenance/physical excluded'
assert collections.Counter(x['finalReview']for x in rows)=={'reviewed':667,'pending':5175}
grammar_rows = [row for row in rows if row['kind'] == 'grammar']
pair_rows = [row for row in rows if row['kind'] == 'grammar_pair']
assert {row['key'] for row in grammar_rows} == {str(i) for i in range(1, 131)}
assert {row['key'] for row in pair_rows} == {str(i) for i in range(92)}
assert len(grammar_rows) == 130 and len(pair_rows) == 92
assert all(row['finalReview'] == 'reviewed' and row['evidence'] for row in grammar_rows + pair_rows)

with(ROOT/'completion/review-register.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys(),lineterminator='\n');w.writeheader();w.writerows(rows)



result = dict(
    version=152, sha256=sha, status='partial_author_review', criteria=['C10','C18'],
    vocabIds=summary['vocabIds'], vocabCards=60, examplesRead=120, vocabCardsEdited=31,
    changedExampleTranslations=23, newRegisterCredits=60, previousReviewed=607,
    registerReviewed=667, registerPending=5175, remainingVocabularyCards=3794,
    cumulativeGrammarCards=130, cumulativeGrammarPairs=92,
    independentReview=False, fullAuditComplete=False, evidence='audit152/editorial-review.json',
)
(ROOT/'completion/C10-C18-v152-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
provenance = dict(
    version=152, sha256=sha, base='v151 / '+summary['baseSha256'],
    status='not_cleared_for_public_product',
    newMaterial='Original edits to Japanese definitions, Ukrainian explanations and translations of inherited examples.',
    inheritedMaterial='Japanese example sentences and pair material retained. Origin remains under review.',
    evidence='audit152/editorial-review.json', sources='audit152/sources.md',
    publicExposure='v152 HTML and audit in main, work/v152-checkpoint, older HTML and reachable Git history. Historical Actions packages remain in scope.',
    historicalInventory='review20261105/public-inventory.json is a frozen v141 snapshot.',
    newActionsArtifacts=False, independentReview=False,
)
(P/'provenance.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2)+'\n')
shutil.copyfile(html, ROOT/html.name)

audit = f'''# Аудит JLPT N1 v152

5 листопада 2026, Asia/Tokyo. Повний HTML має {html.stat().st_size} байтів і SHA-256 `{sha}`. Основа v151, commit `{base}`, SHA-256 `{summary['baseSha256']}`. Робочий знімок збережено в work/v152-checkpoint, commit f960a8981b710d54d05c93b8b71e46d21f18530e.

Ця словникова партія охопила **60 карток, ID 61–120, і 120 прикладів**. Перевірено читання, частину мови, японську дефініцію, українське значення, вживання, пов’язані слова й переклади. У 31 картці відредаговано одне або кілька полів. Для решти зафіксовано рішення зберегти вміст. [Поіменні рішення](audit152/editorial-review.json)

- Для 共存 підтверджено きょうそん і きょうぞん. Для 減速 звірено і зниження швидкості, і дію того, хто її знижує.
- У 更新 уточнено, як слово передає оновлення відомостей, продовження договору та встановлення нового рекорду.
- Для 行為 уточнено значення окремого вчинку чи дії, зокрема дії організації, та частковий перетин з 行動. У 語学 відокремлено вивчення мов від володіння ними, яке називає 語学力.
- Уточнено **23 українські переклади**. Зокрема, у 協力 збережено умову успіху без додавання минулого часу, а в 口座 — неправомірність самого відкриття рахунку без припущення про подальші операції.

Чотири статті デジタル大辞泉 звірено за прямими посиланнями. Загальний пошук повернув помилку. Для решти карток зафіксовано авторський контекстний перегляд. Словникові пари мають окремі рядки в реєстрі. [Джерела й межі](audit152/sources.md)

До реєстру додано **60 авторських результатів**. Разом 667 reviewed і 5175 pending серед 5842 різнорідних рядків. Перегляд словникових карток охопив 120 із 3914, наступна картка має ID 121. Усі 130 граматичних карток і 92 порівняння зберігають попередні результати.

Технічна перевірка охопила 23 групи інваріантів, 728 попередніх файлів, 180 показів карток на трьох ширинах, 3164 генерації й 2373 покази зворотного зв’язку. Звірено 261 граматичний контекст, 1482 записи reading-фільтра, навігацію, імпорт і експорт прогресу та повну сесію. HTML містить 3914 слів, 130 конструкцій, 160 текстів і 381 питання читання. Незалежне мовне приймання, фізичні Android/Windows та походження матеріалів залишаються відкритими. [Облік походження](audit152/provenance.json)
'''
(ROOT/'JLPT_N1_v152_audit.md').write_text(audit)

def original(path):
    return subprocess.check_output(['git','show',base+':'+path], cwd=ROOT, text=True)

readme = original('README.md')
history = readme[readme.index('Нижче збережено історичний журнал'):]
(ROOT/'README.md').write_text(f'''# JLPT N1 — тренажер з японським інтерфейсом

Актуальна **v152**. [Повний HTML]({html.name}) · [Аудит](JLPT_N1_v152_audit.md)

Переглянуто словникові картки 61–120 і 120 прикладів. Уточнено 23 переклади та пояснення 共存, 減速, 更新 і 行為. У реєстрі 667 авторських результатів і 5175 рядків очікують перегляду. [Докази](audit152/editorial-review.json)

3914 слів, 130 конструкцій, 160 текстів і 381 питання читання. SHA-256 `{sha}`. Перед переходом до іншого HTML збережіть резервну копію прогресу в 設定. [Попередня v151](JLPT_N1_ukrainian_reading_v151.html)

'''+history)
status = original('PROJECT_STATUS.md')
status = re.sub(r'Оновлено 5 листопада 2026, Asia/Tokyo\..*?\n\n3914',
    f'Оновлено 5 листопада 2026, Asia/Tokyo. Актуальна **v152**. Повний `{html.name}`, {html.stat().st_size} байтів. SHA-256 `{sha}`. Аудит JLPT_N1_v152_audit.md. Основа v151 / {base}.\n\n3914',
    status, count=1, flags=re.S)
section = '''## Виконано у v152 — словникові картки 61–120

Авторський перегляд 60 карток і 120 прикладів. Відредаговано 31 картку та 23 переклади. У реєстрі 667 reviewed і 5175 pending. Словникових карток переглянуто 120 із 3914. Наступний ID 121. Докази наведено в audit152/editorial-review.json.

23 групи інваріантів, 728 попередніх файлів і 180 показів словникових карток. Перевірено 261 граматичний контекст, 1482 записи reading-фільтра, відновлення прогресу та повну сесію.

'''
(ROOT/'PROJECT_STATUS.md').write_text(status.replace('## Виконано у v151',section+'## Виконано у v151',1))
backlog = original('completion/BACKLOG.md').replace('Поточний HTML — v151','Поточний HTML — v152')
for key, extra in {
    'C10': ' v152 додає 60 словникових карток. Поточний підсумок реєстру 667/5175.',
    'C18': ' У v152 переглянуто картки 61–120. Доказ completion/C10-C18-v152-result.json.',
}.items():
    start = backlog.index('| '+key+' |')
    end = backlog.index('\n',start)
    backlog = backlog[:end-1]+extra+' |'+backlog[end:]
(ROOT/'completion/BACKLOG.md').write_text(backlog)
print(f'v152 {sha}, 60 new author decisions, 667 reviewed and 5175 pending')
