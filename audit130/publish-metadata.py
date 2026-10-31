"""Create release files only after all gate checks have passed in CI."""
from pathlib import Path
import hashlib,json,shutil
root=Path(__file__).resolve().parent.parent
source=root/'release130/JLPT_N1_ukrainian_reading_v130.html'
target=root/'JLPT_N1_ukrainian_reading_v130.html'
assert source.is_file() and source.stat().st_size>5_000_000
shutil.copyfile(source,target)
sha=hashlib.sha256(target.read_bytes()).hexdigest()
data=json.loads((root/'audit130/build-summary.json').read_text())
assert data['sha256']==sha
assert data['texts']=={'medium':59,'long':41} and data['totalQuestions']==241 and data['newQuestions']==56
report=f"""# Аудит JLPT N1 v130 — 31 жовтня 2026

**Повний автономний HTML:** `JLPT_N1_ukrainian_reading_v130.html` (`{target.stat().st_size}` байтів).

**SHA-256:** `{sha}`

Вихідна база: v129 із незмінним словником (3914 слів), граматикою (130 конструкцій), CSS і логікою збереження прогресу. Додано 16 середніх і 8 довгих текстів з 56 запитаннями. Усього: **59 середніх + 41 довгий текст, 241 запитання**.

**Перевірки:** код та інваріанти структури; збереження 76 попередніх текстів і 185 запитань; усі 24 тексти й 56 питань пройшли первинний редакторський перегляд; Chromium-перевірки трьох розмірів екрана, відповідей, пояснень, повного циклу сесії, експорту, імпорту та збереження прогресу.

Деталі: [підсумковий звіт](audit130/RELEASE_CANDIDATE_AUDIT.md), [редакторські звіти](audit130/EDITORIAL_REVIEW_PART1.md), [функціональні тести](audit130/SESSION_FUNCTIONAL_VERIFICATION.md).

**Обмеження:** первинний редакторський перегляд не дорівнює незалежному експертному аудиту всіх 241 питань. Фізичний смартфон не тестувався. Роботу над корпусом текстів, лексикою і граматикою продовжуємо.
"""
(root/'JLPT_N1_v130_audit.md').write_text(report)
readme=root/'README.md'
s=readme.read_text()
start=s.index('> **v130 у перевірці:**')
end=s.index('\n\n',start)
s=s[:start]+f'> **Актуальна версія v130:** [повний HTML](JLPT_N1_ukrainian_reading_v130.html), [аудит](JLPT_N1_v130_audit.md). 100 текстів, 241 запитання. SHA-256: `{sha}`.'+s[end:]
s=s.replace('Поточна редакція: [v129 — повний HTML](JLPT_N1_ukrainian_reading_v129.html), [аудит v129](JLPT_N1_v129_audit.md).','Поточна редакція: [v130 — повний HTML](JLPT_N1_ukrainian_reading_v130.html), [аудит v130](JLPT_N1_v130_audit.md).\n\nПопередня версія: [v129 — повний HTML](JLPT_N1_ukrainian_reading_v129.html), [аудит v129](JLPT_N1_v129_audit.md).')
readme.write_text(s)
status=root/'PROJECT_STATUS.md'
s=status.read_text()
marker='> **2026-10-31 — v130 release candidate'
start=s.index(marker)
end=s.index('\n\n',start)
s=s[:start]+f'> **2026-10-31 — v130 опубліковано.** [HTML](JLPT_N1_ukrainian_reading_v130.html), [аудит](JLPT_N1_v130_audit.md); 100 текстів, 241 питання. SHA-256: `{sha}`. Первинний редакторський перегляд нових матеріалів і автоматизовані браузерні перевірки завершені; незалежний повний мовний аудит банку триває.'+s[end:]
status.write_text(s)
print(json.dumps({'file':str(target),'bytes':target.stat().st_size,'sha256':sha},ensure_ascii=False))
