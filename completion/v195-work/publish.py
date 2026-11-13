import hashlib, json, shutil, subprocess
from pathlib import Path

ROOT=Path.cwd().resolve()
EXPECTED_MAIN="cb65740b4f8720c02f952811bae38844e36a2419"
HTML_PATH="JLPT_N1_ukrainian_reading_v195.html"
PUBLISH_PATHS=[
 HTML_PATH,"JLPT_N1_v195_audit.md","README.md","PROJECT_STATUS.md","completion/BACKLOG.md",
 "completion/review-register.csv","completion/v195-acceptance.tsv","completion/v195-c10-review.tsv",
 "completion/v195-prepare-results.json","completion/v195-browser-results.json",
 "completion/v195-registry-results.json","completion/v195-source-review.md"
]

def run(*args,cwd=ROOT,capture=True):
 return subprocess.run(args,cwd=cwd,check=True,stdout=subprocess.PIPE if capture else None,stderr=subprocess.PIPE if capture else None,text=capture)

run("git","fetch","origin","main")
main_sha=run("git","rev-parse","origin/main").stdout.strip()
if main_sha!=EXPECTED_MAIN:
 raise SystemExit(f"Refusing publication: main moved from {EXPECTED_MAIN} to {main_sha}")

prepare=json.loads((ROOT/"completion/v195-work/prepare-results.json").read_text(encoding="utf-8"))
registry=json.loads((ROOT/"completion/v195-work/registry-results.json").read_text(encoding="utf-8"))
browser=json.loads((ROOT/"completion/v195-work/browser-results.json").read_text(encoding="utf-8"))
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

worktree=Path("/tmp/jlpt-n1-v195-main")
if worktree.exists():shutil.rmtree(worktree)
run("git","worktree","add","--detach",str(worktree),"origin/main")
for rel in PUBLISH_PATHS:
 blob=subprocess.run(["git","show",f"HEAD:{rel}"],cwd=ROOT,check=True,stdout=subprocess.PIPE).stdout
 if rel in {"JLPT_N1_v195_audit.md","README.md","PROJECT_STATUS.md","completion/BACKLOG.md"}:
  text=blob.decode("utf-8").replace("__V195_SHA256__",digest).replace("__V195_BYTES__",str(size))
  blob=text.encode("utf-8")
 dst=worktree/rel
 dst.parent.mkdir(parents=True,exist_ok=True)
 dst.write_bytes(blob)

run("git","config","user.name","github-actions[bot]",cwd=worktree)
run("git","config","user.email","41898282+users.noreply.github.com",cwd=worktree)
run("git","add","--",*PUBLISH_PATHS,cwd=worktree)
if subprocess.run(["git","diff","--cached","--quiet"],cwd=worktree).returncode==0:
 raise SystemExit("Refusing empty v195 publication")
run("git","commit","-m","Publish verified JLPT N1 v195 C10 audit",cwd=worktree,capture=False)
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
print(f"PASS published v195 commit={commit} blob={published_blob} sha256={digest} bytes={size}")
