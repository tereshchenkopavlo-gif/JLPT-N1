import hashlib,json,re,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[2]
raw=(root/'JLPT_N1_ukrainian_reading_v229_C12m.html').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='ec79b4a2866ad2246c774798641ba04468ea520e05712781d704971968572dc2'
s=raw.decode(); start=re.search(r'const readingBank\s*=\s*',s).end()
bank,end=json.JSONDecoder().raw_decode(s,start)
rows=json.loads((root/'completion/c12-ir17/drafts.json').read_text())
assert len(bank['medium'])==112 and len(bank['long'])==71 and len(rows)==1
previous=bank['long'][70]
assert rows[0]['id']==previous['id']
assert rows[0]['uk']!=previous['uk']
assert {**rows[0],'uk':previous['uk']}==previous
bank['long'][70]=rows[0]
payload=json.dumps(bank,ensure_ascii=False,separators=(',',':'))
candidate=s[:start]+payload+s[end:]
assert candidate[:start]+s[start:end]+candidate[start+len(payload):]==s
out=root/'completion/c12-ir17/JLPT_N1_C12_candidate_UNACCEPTED.html'
out.write_bytes(candidate.encode())
scripts=re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',candidate,re.S)
for i,script in enumerate(scripts):
 tmp=root/'completion/c12-ir17'/f'.syntax-{i}.js'
 tmp.write_text(script)
 result=subprocess.run(['node','--check',str(tmp)],capture_output=True,text=True)
 tmp.unlink()
 assert result.returncode==0,result.stderr
report=dict(status='unaccepted integration candidate',base='v229-C12m',baseSha256=hashlib.sha256(raw).hexdigest(),candidateSha256=hashlib.sha256(out.read_bytes()).hexdigest(),candidateBytes=out.stat().st_size,medium=112,long=71,newTexts=0,newQuestions=0,exactRollback=True,otherReadingsPreserved=True,otherHtmlBytesPreserved=True,nodeSyntax=True,registryCredit=0,browserVerification='pending',independentReview='pending')
(root/'completion/c12-ir17/integration-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report))
