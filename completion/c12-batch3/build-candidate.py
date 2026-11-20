import hashlib,json,re,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[2]
raw=(root/'JLPT_N1_ukrainian_reading_v229_C12b.html').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='d4d38ebd380cbb054fc97d631abbc455f093808df97e1e24eb6f27a198b1a0c7'
s=raw.decode(); start=re.search(r'const readingBank\s*=\s*',s).end()
bank,end=json.JSONDecoder().raw_decode(s,start)
rows=json.loads((root/'completion/c12-batch3/drafts.json').read_text())
assert len(bank['medium'])==103 and len(bank['long'])==61 and len(rows)==1
old=json.loads(json.dumps(bank)); ids={x['id'] for xs in bank.values() for x in xs if 'id' in x}
for row in rows:
 assert row['id'] not in ids
 ids.add(row['id'])
 assert len(row['questions'])==3
 for q in row['questions']:
  assert len(set(q['choices']))==4 and 0<=q['answer']<4 and q['evidence'] in row['ja']
 for q in row['contextNotes']: assert q['quote'] in row['ja']
bank['long'].extend(rows)
payload=json.dumps(bank,ensure_ascii=False,separators=(',',':'))
candidate=s[:start]+payload+s[end:]
assert candidate[:start]+s[start:end]+candidate[start+len(payload):]==s
assert bank['medium']==old['medium'] and bank['long'][:-1]==old['long']
out=root/'completion/c12-batch3/JLPT_N1_C12_candidate_UNACCEPTED.html'
out.write_bytes(candidate.encode())
scripts=re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',candidate,re.S)
for i,script in enumerate(scripts):
 tmp=root/'completion/c12-batch3'/f'.syntax-{i}.js'
 tmp.write_text(script)
 result=subprocess.run(['node','--check',str(tmp)],capture_output=True,text=True)
 tmp.unlink()
 assert result.returncode==0,result.stderr
report=dict(status='unaccepted integration candidate',base='v229-C12b',baseSha256=hashlib.sha256(raw).hexdigest(),candidateSha256=hashlib.sha256(out.read_bytes()).hexdigest(),candidateBytes=out.stat().st_size,medium=103,long=62,newTexts=1,newQuestions=3,exactRollback=True,previousReadingsPreserved=True,otherHtmlBytesPreserved=True,nodeSyntax=True,registryCredit=0,browserVerification='pending',independentReview='pending')
(root/'completion/c12-batch3/integration-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report))
