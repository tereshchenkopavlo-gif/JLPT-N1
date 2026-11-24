import hashlib,json,re,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[2]
raw=(root/'JLPT_N1_ukrainian_reading_v229_C12s.html').read_bytes(); assert hashlib.sha256(raw).hexdigest()=='d4605e825f2724986ab128930bb010074d3254dcb4e4569cd7632b6da641e1ef'
s=raw.decode(); start=re.search(r'const readingBank\s*=\s*',s).end(); bank,end=json.JSONDecoder().raw_decode(s,start); rows=json.loads((root/'completion/c12-batch19/drafts.json').read_text())
assert len(bank['medium'])==120 and len(bank['long'])==72 and len(rows)==1; old=json.loads(json.dumps(bank)); ids={x['id'] for xs in bank.values() for x in xs if 'id' in x}
for row in rows:
 assert row['id'] not in ids and len(row['questions'])==3
 for q in row['questions']: assert len(set(q['choices']))==4 and 0<=q['answer']<4 and q['evidence'] in row['ja']
 for note in row['contextNotes']: assert note['quote'] in row['ja']
bank['long'].extend(rows); payload=json.dumps(bank,ensure_ascii=False,separators=(',',':')); candidate=s[:start]+payload+s[end:]
assert candidate[:start]+s[start:end]+candidate[start+len(payload):]==s and bank['medium']==old['medium'] and bank['long'][:-1]==old['long']
out=root/'completion/c12-batch19/JLPT_N1_C12_candidate_UNACCEPTED.html'; out.write_bytes(candidate.encode())
for i,script in enumerate(re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',candidate,re.S)):
 tmp=root/'completion/c12-batch19'/f'.syntax-{i}.js'; tmp.write_text(script); result=subprocess.run(['node','--check',str(tmp)],capture_output=True,text=True); tmp.unlink(); assert result.returncode==0,result.stderr
fixtures=[{'level':'long','count':len(bank['long']),'index':bank['long'].index(row),'row':row} for row in rows]; (root/'completion/c12-batch19/browser-fixtures.json').write_text(json.dumps(fixtures,ensure_ascii=False))
report=dict(status='unaccepted integration candidate',base='v229-C12s',baseSha256=hashlib.sha256(raw).hexdigest(),candidateSha256=hashlib.sha256(out.read_bytes()).hexdigest(),candidateBytes=out.stat().st_size,medium=120,long=73,newTexts=1,newQuestions=3,exactRollback=True,previousReadingsPreserved=True,otherHtmlBytesPreserved=True,nodeSyntax=True,registryCredit=0,browserVerification='pending',independentReview='pending'); (root/'completion/c12-batch19/integration-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(report))
