import hashlib,json,re,subprocess
from pathlib import Path

root=Path(__file__).resolve().parents[2]
raw=(root/'JLPT_N1_ukrainian_reading_v229_C12o.html').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='37b55105d6589a2f6e82118ba389401e028821a071ee52add6d8c478605382fb'
s=raw.decode(); start=re.search(r'const readingBank\s*=\s*',s).end()
bank,end=json.JSONDecoder().raw_decode(s,start)
rows=json.loads((root/'completion/c12-batch15/drafts.json').read_text())
assert len(bank['medium'])==114 and len(bank['long'])==71 and len(rows)==2
old=json.loads(json.dumps(bank)); ids={x['id'] for xs in bank.values() for x in xs if 'id' in x}
for row in rows:
 assert row['id'] not in ids
 ids.add(row['id'])
 assert len(row['questions'])==2
 for q in row['questions']:
  assert len(set(q['choices']))==4 and 0<=q['answer']<4 and q['evidence'] in row['ja']
 for note in row['contextNotes']: assert note['quote'] in row['ja']
bank['medium'].extend(rows)
payload=json.dumps(bank,ensure_ascii=False,separators=(',',':'))
candidate=s[:start]+payload+s[end:]
assert candidate[:start]+s[start:end]+candidate[start+len(payload):]==s
assert bank['medium'][:-2]==old['medium'] and bank['long']==old['long']
out=root/'completion/c12-batch15/JLPT_N1_C12_candidate_UNACCEPTED.html'
out.write_bytes(candidate.encode())
scripts=re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',candidate,re.S)
for i,script in enumerate(scripts):
 tmp=root/'completion/c12-batch15'/f'.syntax-{i}.js'
 tmp.write_text(script)
 result=subprocess.run(['node','--check',str(tmp)],capture_output=True,text=True)
 tmp.unlink()
 assert result.returncode==0,result.stderr
fixtures=[{'level':'medium','count':len(bank['medium']),'index':bank['medium'].index(row),'row':row} for row in rows]
(root/'completion/c12-batch15/browser-fixtures.json').write_text(json.dumps(fixtures,ensure_ascii=False))
report=dict(status='unaccepted integration candidate',base='v229-C12o',baseSha256=hashlib.sha256(raw).hexdigest(),candidateSha256=hashlib.sha256(out.read_bytes()).hexdigest(),candidateBytes=out.stat().st_size,medium=116,long=71,newTexts=2,newQuestions=4,exactRollback=True,previousReadingsPreserved=True,otherHtmlBytesPreserved=True,nodeSyntax=True,registryCredit=0,browserVerification='pending',independentReview='pending')
(root/'completion/c12-batch15/integration-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report))
