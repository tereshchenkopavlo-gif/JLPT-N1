"""Read-only exposure inventory, not a similarity scanner or legal clearance."""
from pathlib import Path
import subprocess,json,re,hashlib,collections
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'review20261105'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True)
base='571aa092d256e682ad16873b7462dcc263cf62d8'
api=json.loads((P/'api-state.json').read_text());refs=[('origin/'+x['name'],x['sha'])for x in api['branches']]
assert dict(refs)['origin/main']==base
current=[];heads=[]
for ref,sha in refs:
 heads.append(dict(ref=ref,commit=sha))
 for line in git('ls-tree','-rl',sha).splitlines():
  meta,path=line.split('\t',1);mode,typ,blob,size=meta.split()
  if path.lower().endswith(('.html','.htm','.zip','.pdf')):current.append(dict(ref=ref,commit=sha,path=path,blob=blob,bytes=int(size)))
history={}
for line in git('log',*[x[1]for x in refs],'--raw','--no-abbrev','--no-renames','--pretty=format:','--','*.html','*.htm','*.zip','*.pdf').splitlines():
 if not line.startswith(':'):continue
 meta,path=line.split('\t',1);_,_,old,new,status=meta.split()
 for blob in [old,new]:
  if set(blob)=={'0'}:continue
  history.setdefault((blob,path),set()).add(status)
visible={(x['blob'],x['path'])for x in current};records=[]
for (blob,path),changes in sorted(history.items(),key=lambda x:(x[0][1],x[0][0])):
 item=dict(path=path,blob=blob,bytes=int(git('cat-file','-s',blob).strip()),atFetchedBranchHead=(blob,path)in visible,seenChangeTypes=sorted(changes))
 if not item['atFetchedBranchHead']:
  for commit in git('log',*[x[1]for x in refs],'--format=%H','--',path).splitlines():
   try:found=git('rev-parse',commit+':'+path).strip()
   except subprocess.CalledProcessError:continue
   if found==blob:item['exampleCommit']=commit;break
 records.append(item)
main=[x for x in current if x['ref']=='origin/main'];main_data=[]
def read(n,s):
 m=re.search(r'const '+n+r'\s*=\s*',s)
 if not m:return None
 try:return json.JSONDecoder().raw_decode(s[m.end():])[0]
 except ValueError:return None
for row in main:
 raw=subprocess.check_output(['git','cat-file','blob',row['blob']],cwd=ROOT);s=raw.decode('utf-8');v=read('DEFAULT_VOCAB',s);g=read('GRAMMAR',s);bank=read('readingBank',s)
 main_data.append(dict(**row,sha256=hashlib.sha256(raw).hexdigest(),vocabCount=len(v)if v is not None else None,grammarCount=len(g)if g is not None else None,readingCount=sum(map(len,bank.values()))if isinstance(bank,dict)else None,embeddedVocabularyDetails='VOCAB_DETAILS_BY_ID' in s,embeddedGrammarDetails='GRAMMAR_DETAILS_BY_ID' in s,rightsStatus='not_cleared',priority='P1',decision='field-by-field origin review required; no infringement finding'))
summary=dict(date='2026-11-05',baseCommit=base,repository='tereshchenkopavlo-gif/JLPT-N1',scope='Frozen public branch heads from api-state.json and their reachable Git changes of HTML/HTM/ZIP/PDF. Not a crawl of mirrors, user downloads, deleted refs or archive contents. Actions metadata is separate.',fetchedHeads=heads,mainHtmlCount=sum(x['path'].endswith('.html')for x in main),mainHtmlUniqueBlobs=len({x['blob']for x in main if x['path'].endswith('.html')}),branchHeadHtmlOccurrences=sum(x['path'].endswith('.html')for x in current),uniqueHtmlBlobsAtHeads=len({x['blob']for x in current if x['path'].endswith('.html')}),historyPathBlobPairs=len(records),historyUniqueBlobs=len({x['blob']for x in records}),historyOnlyPathBlobPairs=sum(not x['atFetchedBranchHead']for x in records),mainNonHtmlPackages=[x for x in main if not x['path'].endswith('.html')],tags=api['tags'],mainFiles=main_data,branchFiles=current,historyFiles=records,notClearedByThisInventory=True)
(P/'public-inventory.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items()if k not in ['mainFiles','branchFiles','historyFiles','fetchedHeads']},ensure_ascii=False))
