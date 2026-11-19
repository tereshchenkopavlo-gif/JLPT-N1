import json,re,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2]
s=(root/'completion/C12-reading-plan.md').read_text()
base=(root/'JLPT_N1_ukrainian_reading_v229.html').read_text()
bank=json.JSONDecoder().raw_decode(base,re.search(r'const readingBank\s*=\s*',base).end())[0]
sections=[s.split('**仮題 — 点検を省いた代償**')[1].split('## Другий')[0],s.split('**川の変化を記録する**')[1]]
rows=[]
for i,(title,part,answers) in enumerate(zip(['点検を省いた代償','川の変化を記録する'],sections,[[0,2],[1,3]]),1):
 ja=part.split('**問')[0].strip()
 uk=part.split('**Переклад')[1].split('**',1)[1].split('Контексти чернетки')[0].split('Статус обох')[0].strip().lstrip('.').strip()
 qs=[]
 for n,q in enumerate(re.split(r'\*\*問[^—]*— ',part)[1:]):
  prompt,body=q.split('**',1)
  choices=re.findall(r'^\d\. (.+)$',body,re.M)
  key=body.split('Ключ — ')[1].split('.',1)[0]
  assert int(key)-1==answers[n] and len(choices)==len(set(choices))==4
  explain=body.split('Ключ — ')[1].split('**Переклад')[0].strip().split('. ',1)[1]
  evidence=re.search('Опора — 「([^」]+)」',explain).group(1)
  assert evidence in ja
  qs.append(dict(prompt=prompt.strip(),choices=choices,answer=answers[n],explain=explain,evidence=evidence))
 assert len(qs)==2 and ja and uk
 assert not any(x['title']==title for xs in bank.values() for x in xs)
 notes=([('35','〜始末','観客を一時退場させる始末だった','небажаний підсумок інциденту'),('43','〜べからず','許可なく設定を変えるべからず','формальна заборона самовільної зміни налаштувань'),('44','〜あるまじき','施設の運営に携わる者としてあるまじき行為','неприпустимість учинку з огляду на відповідальність людини')] if i==1 else [('90','～ないでは（ずには）おかない','向き合い方を変えずにはおかない','переконаність у неминучому впливі відкриттів на ставлення мешканців')])
 assert all(quote in ja for _,_,quote,_ in notes)
 rows.append(dict(id=f'm-c12-20261119-{i:02}',title=title,ja=ja,uk=uk,questions=qs,contextNotes=[dict(kind='g',id=k,label=l,quote=q,meaning=m) for k,l,q,m in notes]))
out=root/'completion/c12-work'
(out/'reading-candidates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
report=dict(status='checkpoint awaiting integration and browser verification',texts=2,questions=4,grammarAnchors=4,baselineMedium=len(bank['medium']),baselineLong=len(bank['long']),registryCredit=0,payloadSha256=hashlib.sha256((out/'reading-candidates.json').read_bytes()).hexdigest())
(out/'draft-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report))
