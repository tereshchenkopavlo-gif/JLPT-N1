import hashlib,json,shutil,subprocess
from pathlib import Path
ROOT=Path.cwd().resolve()
EXPECTED_MAIN="__CURRENT_MAIN_HEAD__"
HTML_PATH="JLPT_N1_ukrainian_reading_v214.html"
PUBLISH_PATHS=[
 HTML_PATH,"JLPT_N1_v214_audit.md","README.md","PROJECT_STATUS.md","completion/BACKLOG.md",
 "completion/review-register.csv","completion/v214-acceptance.tsv","completion/v214-c10-review.tsv",
 "completion/v214-field-changes.tsv","completion/v214-pair-review.tsv","completion/v214-source-review.md",
 "completion/v214-prepare-results.json","completion/v214-browser-results.json","completion/v214-registry-results.json"
]
def run(*args,cwd=ROOT,capture=True):
 return subprocess.run(args,cwd=cwd,check=True,stdout=subprocess.PIPE if capture else None,stderr=subprocess.PIPE if capture else None,text=capture)
run("git","fetch","origin","main")
main=run("git","rev-parse","origin/main").stdout.strip()
if main!=EXPECTED_MAIN: raise SystemExit(f"Refusing publication: main moved from {EXPECTED_MAIN} to {main}")
prepare=json.loads((ROOT/"completion/v214-work/prepare-results.json").read_text(encoding="utf-8"))
registry=json.loads((ROOT/"completion/v214-work/registry-results.json").read_text(encoding="utf-8"))
browser=json.loads((ROOT/"completion/v214-work/browser-results.json").read_text(encoding="utf-8"))
if not(prepare.get("pass") and registry.get("pass") and browser.get("pass")): raise SystemExit("Refusing publication: acceptance results did not pass")
data=(ROOT/HTML_PATH).read_bytes()
digest=hashlib.sha256(data).hexdigest(); size=len(data)
blob_sha=hashlib.sha1(b"blob "+str(size).encode()+b"\0"+data).hexdigest()
if digest!=prepare["candidate_sha256"] or size!=prepare["candidate_bytes"]: raise SystemExit("candidate digest/size mismatch")
wt=Path("/tmp/jlpt-n1-v214-main")
if wt.exists(): shutil.rmtree(wt)
run("git","worktree","add","--detach",str(wt),"origin/main")
text_paths={"JLPT_N1_v214_audit.md","README.md","PROJECT_STATUS.md","completion/BACKLOG.md"}
for rel in PUBLISH_PATHS:
 blob=subprocess.run(["git","show",f"HEAD:{rel}"],cwd=ROOT,check=True,stdout=subprocess.PIPE).stdout
 if rel in text_paths:
  content=blob.decode("utf-8")
  content=content.replace("__V214_SHA256__",digest).replace("__V214_BYTES__",str(size)).replace("__V214_BLOB__",blob_sha)
  if rel=="README.md":
   content=content.replace("Актуальна опублікована редакція: v213.","Актуальна опублікована редакція: v214.")
   content=content.replace("## Кандидат v214","## Стан випуску v214")
   content=content.replace("Кандидат v214 у гілці work/v214-c10-next-pending:","Опубліковано v214:")
  elif rel=="PROJECT_STATUS.md":
   content=content.replace("Актуальна **v213** у main. Кандидат **v214** у гілці work/v214-c10-next-pending, ще не опублікований.","Актуальна **v214** у main після guarded-публікації.")
   content=content.replace("## Поточний кандидат v214","## Опублікований випуск v214")
   content=content.replace("Підготовлено 13 точних змін","Внесено 13 точних змін")
   content=content.replace("Очікуваний авторський credit після v214","Авторський credit після v214")
   content=content.replace("Кандидат v214 ще не зібрано; deterministic build, перевірка реєстру та Chromium acceptance очікують запуску.",f"Опублікований HTML v214: {size} байтів, SHA-256 {digest}, Git blob {blob_sha}. Deterministic build, registry та Chromium acceptance успішні.")
  elif rel=="completion/BACKLOG.md":
   content=content.replace("v214 candidate:","v214 опубліковано:")
  elif rel=="JLPT_N1_v214_audit.md":
   content=content.replace("Кандидат v214:","Опублікований v214:")
  blob=content.encode("utf-8")
 dst=wt/rel; dst.parent.mkdir(parents=True,exist_ok=True); dst.write_bytes(blob)
run("git","config","user.name","github-actions[bot]",cwd=wt)
run("git","config","user.email","41898282+users.noreply.github.com",cwd=wt)
run("git","add","--",*PUBLISH_PATHS,cwd=wt)
if subprocess.run(["git","diff","--cached","--quiet"],cwd=wt).returncode==0: raise SystemExit("empty v214 publication")
run("git","commit","-m","Publish verified JLPT N1 v214 C10 audit",cwd=wt,capture=False)
commit=run("git","rev-parse","HEAD",cwd=wt).stdout.strip()
run("git","push","origin","HEAD:main",cwd=wt,capture=False)
run("git","fetch","origin","main")
published=run("git","rev-parse","origin/main",cwd=wt).stdout.strip()
published_blob=run("git","rev-parse",f"origin/main:{HTML_PATH}",cwd=wt).stdout.strip()
if published!=commit or published_blob!=blob_sha: raise SystemExit("published commit/blob mismatch")
published_data=(wt/HTML_PATH).read_bytes()
if hashlib.sha256(published_data).hexdigest()!=digest or len(published_data)!=size: raise SystemExit("published HTML digest/size mismatch")
print(f"PASS published v214 commit={commit} blob={published_blob} sha256={digest} bytes={size}")
