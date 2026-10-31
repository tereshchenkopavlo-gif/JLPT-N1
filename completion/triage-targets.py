"""Record technical causes seen in all 30 unmarked examples; no HTML changes."""
import json
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parent;scan=json.loads((P/'target-diagnostics.json').read_text())
# Exact alternatives below are observed strings, not approved universal substitutions.
causes={
('v',210):('related_expression','У реченні 日進月歩; буквального 進歩 поспіль немає.','Змістово вирішити, чи замінити приклад прямим уживанням 進歩, чи залишити лише як споріднений вислів; не робити cloze по випадкових окремих 進 і 歩.'),
('v',447):('kana_spelling','Заголовок 繋がる, речення з つながった / つながらず.','Звірити значення й точні повні форми в кожному реченні; додати адресні відповідності для цих прикладів, перевірити вибір у сесії.'),
('g',1):('conjugated_pattern','У прикладі 立ちはだかろうが; рядка ようが немає.','Зіставити реалізовану вольову форму зі значенням; перевірити адресне виділення та питання.'),
('g',4):('conjugated_two_part_pattern','Приклад 向かおうにも向かえなく; буквальні частини ようにも / ない не збігаються.','Перевірити обидві частини конструкції й точні межі форми, без виділення випадкового ない.'),
('g',18):('formal_ending_variant','Приклад закінчується したまでのことである, а не までのことだ.','Зіставити минуле вживання з поясненням і забезпечити вибір цього прикладу без заміни його іншим значенням.'),
('g',24):('label_number_and_polite_variant','Мітка ① потрапляє в частину пошуку; у першому прикладі також をもちまして.','Відокремити службовий номер від форми; поіменно перевірити обидва часові вживання й ввічливий варіант.'),
('g',26):('voiced_past_form','飲んだが最後 містить だが最後, заголовок — たが最後.','Зіставити минулу форму та межі конструкції; адресно перевірити приклад.'),
('g',45):('label_number','У заголовку をもって②, у реченнях — をもって без ②.','Відокремити номер значення від форми й перевірити саме інструментальне вживання.'),
('g',49):('past_ending','У реченнях といったらなかった замість заголовкового といったらない.','Перевірити минуле закінчення та контекст; не відкидати приклади тільки через буквальну невідповідність.'),
('g',51):('polite_ending','У прикладі 願ってやみません, заголовок てやまない.','Зіставити ввічливу заперечну форму з поясненням і точними межами виділення.'),
('g',57):('label_number_kanji_and_past','Заголовок にたえない①; приклади に堪えなかった / にたえない.','Прибрати вплив номера лише для пошуку; окремо перевірити написання, минулу форму й значення нестерпності.'),
('g',80):('negative_continuative','У реченні てはばからず; заголовок てはばからない.','Перевірити продовжувальну заперечну форму й відповідність значення.'),
('g',85):('label_number_and_polite_variant','Заголовок にたえない②; приклади にたえません / にたえない.','Відокремити номер і перевірити емоційне значення обох речень, не змішуючи з ID57.'),
('g',86):('intervening_particle','У прикладі にはあたらない; у заголовку にあたらない.','Перевірити функцію は і відповідність прикладу, потім адресне виділення.'),
('g',92):('expanded_question_ending','Приклад ないものだろうか, заголовок ないものか.','Зіставити розширений питальний кінець з бажанням знайти спосіб; не підміняти категоричною відмовою.'),
('g',94):('adnominal_variant','Приклад 新人なりの視点, заголовок なりに.','Звірити атрибутивне なりの з обсягом пояснення й питанням, позначити конкретне вживання.'),
('g',101):('conditional_variant','У реченні ともなれば; у заголовку ともなると.','Перевірити варіант умовного приєднання й межі перевірюваного значення.'),
('g',106):('conjugated_verb','У двох прикладах めいた, у заголовку めく.','Зіставити відмінені форми з дієсловом та значенням, задати адресні відповідності.'),
('g',108):('preceding_particle_variant','У прикладі 支援が相まって; у заголовку と相まって.','Перевірити синтаксис が相まって та відповідність прикладу обсягу картки.'),
('g',121):('polite_conjugation','У прикладах させていただきます / させていただきました, заголовок させていただく.','Звірити ввічливі форми, дозвіл/користь і конкретний контекст, потім перевірити межі виділення.'),
('g',122):('continuative_conjugation','У прикладах ていただき; у заголовку ていただく.','Звірити продовжувальне приєднання й конкретне значення, перевірити форму в сесії.')
}
rows=[]
for r in scan['unmarked']:
 c,observation,action=causes[(r['kind'],r['id'])]
 rows.append({**r,'category':c,'technicalObservation':observation,'nextAction':action,'status':'triaged_pending_semantic_decision_and_runtime_fix','htmlChanged':False})
assert len(rows)==30 and len({(r['kind'],r['id'],r['exampleIndex']) for r in rows})==30
single=[]
for r in scan['singleCharacter']:
 c='exact_one_character_headword' if r['kind']=='v' and r['spans']==[r['word']] and len(r['word'])==1 else ('grammar_fragment' if r['kind']=='g' else 'shortened_or_embedded_vocabulary_match')
 single.append({**r,'technicalClass':c,'semanticStatus':'not_adjudicated'})
result=dict(htmlSha256=scan['htmlSha256'],scope='technical triage only; no semantic pass or HTML fix claimed',unmarked=rows,singleCharacterClassCounts=dict(Counter(r['technicalClass'] for r in single)),singleCharacter=single)
(P/'target-triage.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print('30 unmarked cases triaged; single-character groups:',result['singleCharacterClassCounts'])
