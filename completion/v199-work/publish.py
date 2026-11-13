import hashlib, json, shutil, subprocess
from pathlib import Path

ROOT=Path.cwd().resolve()
EXPECTED_MAIN="9c7b78a20481cca0b48b17a82a52f193e76c21c7"
HTML_PATH="JLPT_N1_ukrainian_reading_v199.html"
PUBLISH_PATHS=[
 HTML_PATH,"JLPT_N1_v199_audit.md","README.md","PROJECT_STATUS.md","completion/BACKLOG.md",
 "completion/review-register.csv","completion/v199-acceptance.tsv","completion/v199-c10-review.tsv",
 "completion/v199-prepare-results.json","completion/v199-browser-results.json",
 "completion/v199-registry-results.json","completion/v199-source-review.md"
]

def run(*args,cwd=ROOT,capture=True):
 return subprocess.run(args,cwd=cwd,check=True,stdout=subprocess.PIPE if capture else None,stderr=subprocess.PIPE if capture else None,text=capture)

run("git","fetch","origin","main")
main_sha=run("git","rev-parse","origin/main").stdout.strip()
if main_sha!=EXPECTED_MAIN:
 raise SystemExit(f"Refusing publication: main moved from {EXPECTED_MAIN} to {main_sha}")

prepare=json.loads((ROOT/"completion/v199-work/prepare-results.json").read_text(encoding="utf-8"))
registry=json.loads((ROOT/"completion/v199-work/registry-results.json").read_text(encoding="utf-8"))
browser=json.loads((ROOT/"completion/v199-work/browser-results.json").read_text(encoding="utf-8"))
if not (prepare.get("pass") and registry.get("pass") and browser.get("pass")):
 raise SystemExit("Refusing publication: one or more acceptance results did not pass")

data=(ROOT/HTML_PATH).read_bytes()
digest=hashlib.sha256(data).hexdigest()
size=len(data)
if digest!=prepare["candidate_sha256"] or size!=prepare["candidate_bytes"]:
 raise SystemExit(f"Candidate digest/size mismatch: {digest} / {size}")
expected_blob=run("git","rev-parse",f"HEAD:{HTML_PATH}").stdout.strip()

for rel in PUBLISH_PATHS:
 if subprocess.run(["git","cat-file","-e",f"HEAD:{rel}"],cwd=ROOT).returncode:
  raise SystemExit("Missing committed publication file: "+rel)

worktree=Path("/tmp/jlpt-n1-v199-main")
if worktree.exists():shutil.rmtree(worktree)
run("git","worktree","add","--detach",str(worktree),"origin/main")
for rel in PUBLISH_PATHS:
 blob=subprocess.run(["git","show",f"HEAD:{rel}"],cwd=ROOT,check=True,stdout=subprocess.PIPE).stdout
 if rel in {"JLPT_N1_v199_audit.md","README.md","PROJECT_STATUS.md","completion/BACKLOG.md"}:
  text=blob.decode("utf-8").replace("__V199_SHA256__",digest).replace("__V199_BYTES__",str(size))
  if rel=="README.md":
   text=text.replace("Опублікована в main версія — v198. Кандидат v199 у робочій гілці work/v199-c10-next-pending; ще не опублікований.","Актуальна v199 у main після успішного guarded-приймання.")
  elif rel=="PROJECT_STATUS.md":
   text=text.replace("Опублікована в main версія — **v198**. Кандидат **v199** у гілці work/v199-c10-next-pending; guarded-приймання та публікація ще очікуються.","Актуальна **v199** у main після успішного guarded-приймання.")
   text=text.replace("blob/work/v199-c10-next-pending/JLPT_N1_ukrainian_reading_v199.html","blob/main/JLPT_N1_ukrainian_reading_v199.html")
   text=text.replace("blob/work/v199-c10-next-pending/JLPT_N1_v199_audit.md","blob/main/JLPT_N1_v199_audit.md")
  elif rel=="completion/BACKLOG.md":
   text=text.replace("Поточний опублікований HTML у main — v198, SHA-256 32c0bf74d083db74576d53a249ec1858352f20efcea9a72dd3c80daf3a17a39c. Кандидат v199 у work/v199-c10-next-pending, SHA-256 "+digest+"; публікація очікує guarded-приймання.","Поточний HTML — v199, SHA-256 "+digest+"; початкова інвентаризація зафіксована на v135.")
  blob=text.encode("utf-8")
 dst=worktree/rel
 dst.parent.mkdir(parents=True,exist_ok=True)
 dst.write_bytes(blob)

run("git","config","user.name","github-actions[bot]",cwd=worktree)
run("git","config","user.email","41898282+actions@users.noreply.github.com",cwd=worktree)
run("git","add","--",*PUBLISH_PATHS,cwd=worktree)
if subprocess.run(["git","diff","--cached","--quiet"],cwd=worktree).returncode==0:
 raise SystemExit("Refusing empty v199 publication")
run("git","commit","-m","Publish verified JLPT N1 v199 C10 audit",cwd=worktree,capture=False)
commit=run("git","rev-parse","HEAD",cwd=worktree).stdout.strip()
run("git","push","origin","HEAD:main",cwd=worktree,capture=False)
run("git","fetch","origin","main")
published=run("git","rev-parse","origin/main").stdout.strip()
published_blob=run("git","rev-parse",f"origin/main:{HTML_PATH}").stdout.strip()
published_data=(worktree/HTML_PATH).read_bytes()
if published!=commit or published_blob!=expected_blob:
 raise SystemExit("Published commit/blob verification mismatch")
if hashlib.sha256(published_data).hexdigest()!=digest or len(published_data)!=size:
 raise SystemExit("Published HTML digest/size verification mismatch")
print(f"PASS published v199 commit={commit} blob={published_blob} sha256={digest} bytes={size}")
