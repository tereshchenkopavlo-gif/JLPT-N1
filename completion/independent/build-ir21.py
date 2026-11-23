#!/usr/bin/env python3
"""Build IR21 for the two original C12 batch-15 medium readings."""
import hashlib,json,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PACKAGE_ID='IR-20261123-21'
SOURCE_COMMIT='2bbd038fe5153afaf95da99b74c4a9ccdb5ea9ff'
SOURCE_PATH='completion/c12-batch15/drafts.json'
CASE_IDS=['m-c12-20261123-24','m-c12-20261123-25']
def canonical(v): return json.dumps(v,ensure_ascii=False,sort_keys=True).encode()
rows={x['id']:x for x in json.loads(subprocess.check_output(['git','show',f'{SOURCE_COMMIT}:{SOURCE_PATH}']))}
assert set(rows)==set(CASE_IDS)
cases=[{'case_id':cid,'kind':'reading','sources':[{'commit':SOURCE_COMMIT,'path':SOURCE_PATH}],'fields':rows[cid]} for cid in CASE_IDS]
sources_sha256=hashlib.sha256(canonical(cases)).hexdigest()
instructions=('Проведи незалежний мовний аудит вкладених матеріалів. Працюй лише з цим пакетом і фактично перевіреними словниковими джерелами. Не читай авторські звіти чи історію чату. Не припускай, що кожен матеріал містить помилку. Альтернативний коректний переклад сам по собі не є помилкою.\n'
'Перевір природність і зв’язність японського тексту, точність і природність українського перекладу та внутрішню узгодженість. Для кожного питання перевір усі варіанти, єдиність ключа, природність і правдоподібність distractors, а також підказки довжиною, граматичною формою чи логікою без знання тексту. Перевір точність пояснення й цитати evidence.\n'
'Зафіксуй кожне перевірене поле й кожне пропущене поле. Не видавай структурні тести за мовну перевірку. Не вигадуй джерела. Невпевненість явно позначай. Поверни один JSON, заповнивши return_template. checked_fields може містити назву верхнього поля лише якщо перевірено весь його вміст; інакше переліч точні шляхи та решту в unchecked_fields. Наведи evidence і proposed_change для кожного зауваження. Збережи package_id та sources_sha256.')
package={'schema_version':1,'package_id':PACKAGE_ID,'instructions':instructions,'sources_sha256':sources_sha256,'scope':{'vocab_ids':[],'meaning_contexts':0,'readings':2,'reading_questions':4},'cases':cases,'return_template':{'schema_version':1,'package_id':PACKAGE_ID,'sources_sha256':sources_sha256,'reviewer':{'system':'ChatGPT','session':'','reviewed_at':'','participated_in_authoring':False},'cases':[{'case_id':cid,'checked_fields':[],'unchecked_fields':['id','title','ja','uk','contextNotes','questions'],'verdict':'not_reviewed','findings':[]} for cid in CASE_IDS],'finding_format':{'field_path':'','severity':'minor|major|critical','confidence':'high|medium|low','claim':'','evidence':'','sources':[],'proposed_change':''},'allowed_verdicts':['pass','issues','uncertain','not_reviewed']}}
path=ROOT/f'packages/{PACKAGE_ID}.json'; path.write_text(json.dumps(package,ensure_ascii=False,indent=2)+'\n')
package_sha256=hashlib.sha256(path.read_bytes()).hexdigest()
qp=ROOT/'queue.json'; queue=json.loads(qp.read_text()); assert not any(x['package_id']==PACKAGE_ID for x in queue['packages'])
queue['packages'].append({'package_id':PACKAGE_ID,'path':f'packages/{PACKAGE_ID}.json','package_sha256':package_sha256,'sources_sha256':sources_sha256,'source_commits':[SOURCE_COMMIT],'status':'pending_review','predecessor':None,'scope':package['scope'],'reviews':[],'history':[{'status':'pending_review','date':'2026-11-23'}],'notes':'Two original C12 batch-15 medium readings and four questions from released v229-C12p.'})
qp.write_text(json.dumps(queue,ensure_ascii=False,indent=2)+'\n')
mp=ROOT/'QUEUE.md'; md=mp.read_text(); marker='| [IR-20261123-20]'; line='| [IR-20261123-21](packages/IR-20261123-21.json) | pending_review | 0 карток, 2 тексти, 4 питання | Очікується |\n'; pos=md.index('\n',md.index(marker))+1
md=md[:pos]+line+md[pos:]+('\n## IR-20261123-21\n\nДва оригінальні середні тексти C12 із випуску v229-C12p та чотири питання. Авторські оцінки в пакет не включено. Джерело — release commit `2bbd038fe5153afaf95da99b74c4a9ccdb5ea9ff`; Chromium 45164462017, branch data-check 45164461891 і main data-check 45165864126 успішні.\n')
mp.write_text(md)
print(json.dumps({'package_id':PACKAGE_ID,'package_sha256':package_sha256,'sources_sha256':sources_sha256}))
