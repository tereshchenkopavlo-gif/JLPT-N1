import hashlib,json,shutil,subprocess
from pathlib import Path
ROOT=Path.cwd().resolve()
EXPECTED_MAIN="1019e4e9b5ddad6392515906929deea88bbc5bdd"
HTML_PATH="JLPT_N1_ukrainian_reading_v202.html"
PUBLISH_PATHS=[HTML_PATH,"JLPT_N1_v202_audit.md","README.md","PROJECT_STATUS.md","completion/BACKLOG.md","completion/review-register.csv","completion/v202-acceptance.tsv","completion/v202-c10-review.tsv","completion/v202-prepare-results.json","completion/v202-browser-results.json","completion/v202-registry-results.json","completion/v202-source-review.md"]
def run(*args,cwd=ROOT,capture=True):
 return subprocess.run(args,cwd=cwd,check=True,stdout=subprocess.PIPE if capture else None,stderr=subprocess.PIPE if capture else None,text=capture)
run("git","fetch","origin","main");main=run("git","rev-parse","origin/main").stdout.strip()
if main!=EXPECTED_MAIN:raise SystemExit(f"Refusing publication: main moved from {EXPECTED_MAIN} to {main}")
prepare=json.loads((ROOT/"completion/v202-work/prepare-results.json").read_text(encoding="utf-8"))
registry=json.loads((ROOT/"completion/v202-work/registry-results.json").read_text(encoding="utf-8"))
browser=json.loads((ROOT/"completion/v202-work/browser-results.json").read_text(encoding="utf-8"))
if not(prepare.get("pass") and registry.get("pass") and browser.get("pass")):raise SystemExit("Refusing publication: acceptance results did not pass")
data=(ROOT/HTML_PATH).read_bytes();digest=hashlib.sha256(data).hexdigest();size=len(data)
if digest!=prepare["candidate_sha256"] or size!=prepare["candidate_bytes"]:raise SystemExit("candidate digest/size mismatch")
expected_blob=run("git","rev-parse",f"HEAD:{HTML_PATH}").stdout.strip()
for rel in PUBLISH_PATHS:
 if subprocess.run(["git","cat-file","-e",f"HEAD:{rel}"],cwd=ROOT).returncode:raise SystemExit("missing publication file "+rel)
wt=Path("/tmp/jlpt-n1-v202-main")
if wt.exists():shutil.rmtree(wt)
run("git","worktree","add","--detach",str(wt),"origin/main")
for rel in PUBLISH_PATHS:
 blob=subprocess.run(["git","show",f"HEAD:{rel}"],cwd=ROOT,check=True,stdout=subprocess.PIPE).stdout
 if rel in {"JLPT_N1_v202_audit.md","README.md","PROJECT_STATUS.md","completion/BACKLOG.md"}:
  text=blob.decode("utf-8").replace("__V202_SHA256__",digest).replace("__V202_BYTES__",str(size))
  if rel=="README.md":text=text.replace("Опублікована в main версія — v201. Кандидат v202 у робочій гілці work/v202-c10-next-pending; ще не опублікований.","Актуальна v202 у main після успішного guarded-приймання.")
  elif rel=="PROJECT_STATUS.md":
   text=text.replace("Опублікована в main версія — **v201**. Кандидат **v202** у гілці work/v202-c10-next-pending; guarded-приймання та публікація ще очікуються.","Актуальна **v202** у main після успішного guarded-приймання.")
   text=text.replace("blob/work/v202-c10-next-pending/JLPT_N1_ukrainian_reading_v202.html","blob/main/JLPT_N1_ukrainian_reading_v202.html")
   text=text.replace("blob/work/v202-c10-next-pending/JLPT_N1_v202_audit.md","blob/main/JLPT_N1_v202_audit.md")
  elif rel=="completion/BACKLOG.md":
   text=text.replace("Поточний опублікований HTML у main — v201, SHA-256 ab7369a2ff4af2a74b79111713ad14b19d1dd4ae4519c15580a8e2e25674ce34. Кандидат v202 у work/v202-c10-next-pending, SHA-256 "+digest+"; публікація очікує guarded-приймання.","Поточний HTML — v202, SHA-256 "+digest+"; початкова інвентаризація зафіксована на v135.")
  blob=text.encode("utf-8")
 dst=wt/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(blob)
run("git","config","user.name","github-actions[bot]",cwd=wt);run("git","config","user.email","41898282+actions@users.noreply.github.com",cwd=wt)
run("git","add","--",*PUBLISH_PATHS,cwd=wt)
if subprocess.run(["git","diff","--cached","--quiet"],cwd=wt).returncode==0:raise SystemExit("empty v202 publication")
run("git","commit","-m","Publish verified JLPT N1 v202 C10 audit",cwd=wt,capture=False)
commit=run("git","rev-parse","HEAD",cwd=wt).stdout.strip();run("git","push","origin","HEAD:main",cwd=wt,capture=False);run("git","fetch","origin","main")
published=run("git","rev-parse","origin/main").stdout.strip();blob=run("git","rev-parse",f"origin/main:{HTML_PATH}").stdout.strip()
if published!=commit or blob!=expected_blob:raise SystemExit("published commit/blob mismatch")
if hashlib.sha256((wt/HTML_PATH).read_bytes()).hexdigest()!=digest or len((wt/HTML_PATH).read_bytes())!=size:raise SystemExit("published HTML digest/size mismatch")
print(f"PASS published v202 commit={commit} blob={blob} sha256={digest} bytes={size}")
