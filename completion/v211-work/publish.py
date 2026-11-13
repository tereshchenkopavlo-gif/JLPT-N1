import hashlib,json,shutil,subprocess
from pathlib import Path
ROOT=Path.cwd().resolve()
EXPECTED_MAIN="2934b17b1210583dd8de876bb0219133dee13b17"
HTML_PATH="JLPT_N1_ukrainian_reading_v211.html"
PUBLISH_PATHS=[HTML_PATH,"JLPT_N1_v211_audit.md","README.md","PROJECT_STATUS.md","completion/BACKLOG.md","completion/review-register.csv","completion/v211-acceptance.tsv","completion/v211-c10-review.tsv","completion/v211-field-changes.tsv","completion/v211-source-review.md","completion/v211-prepare-results.json","completion/v211-browser-results.json","completion/v211-registry-results.json"]
def run(*args,cwd=ROOT,capture=True):
 return subprocess.run(args,cwd=cwd,check=True,stdout=subprocess.PIPE if capture else None,stderr=subprocess.PIPE if capture else None,text=capture)
run("git","fetch","origin","main");main=run("git","rev-parse","origin/main").stdout.strip()
if main!=EXPECTED_MAIN:raise SystemExit(f"Refusing publication: main moved from {EXPECTED_MAIN} to {main}")
prepare=json.loads((ROOT/"completion/v211-work/prepare-results.json").read_text(encoding="utf-8"))
registry=json.loads((ROOT/"completion/v211-work/registry-results.json").read_text(encoding="utf-8"))
browser=json.loads((ROOT/"completion/v211-work/browser-results.json").read_text(encoding="utf-8"))
if not(prepare.get("pass") and registry.get("pass") and browser.get("pass")):raise SystemExit("Refusing publication: acceptance results did not pass")
data=(ROOT/HTML_PATH).read_bytes();digest=hashlib.sha256(data).hexdigest();size=len(data)
if digest!=prepare["candidate_sha256"] or size!=prepare["candidate_bytes"]:raise SystemExit("candidate digest/size mismatch")
wt=Path("/tmp/jlpt-n1-v211-main")
if wt.exists():shutil.rmtree(wt)
run("git","worktree","add","--detach",str(wt),"origin/main")
for rel in PUBLISH_PATHS:
 blob=subprocess.run(["git","show",f"HEAD:{rel}"],cwd=ROOT,check=True,stdout=subprocess.PIPE).stdout
 if rel in {"JLPT_N1_v211_audit.md","README.md","PROJECT_STATUS.md","completion/BACKLOG.md"}:
  text=blob.decode("utf-8").replace("__V211_SHA256__",digest).replace("__V211_BYTES__",str(size))
  if rel=="README.md":
   text=text.replace("Актуальна **v210** у main після guarded-публікації. Кандидат v211 у work/v211-c10-next-pending.","Актуальна **v211** у main після guarded-публікації.")
   text=text.replace("JLPT_N1_ukrainian_reading_v210.html","JLPT_N1_ukrainian_reading_v211.html")
   text=text.replace("JLPT_N1_v210_audit.md","JLPT_N1_v211_audit.md")
  elif rel=="PROJECT_STATUS.md":
   text=text.replace("Актуальна **v210** у main. Кандидат **v211** у гілці work/v211-c10-next-pending, ще не опублікований.","Актуальна **v211** у main після guarded-публікації.")
   text=text.replace("## Поточний кандидат v211 — C10 авторський аудит","## Опублікований випуск v211 — C10 авторський аудит")
   text=text.replace("Кандидат v211 ще не зібрано; після детермінованої перевірки й Chromium acceptance публікувати лише точні артефакти в main, робочу гілку не зливати.",f"Опублікований HTML v211: {size} байти, SHA-256 {digest}. Deterministic build, registry та Chromium acceptance успішні; робочу гілку не зливати.")
  elif rel=="completion/BACKLOG.md":
   text=text.replace("Поточний HTML — v210, SHA-256 ced09771cf3ca0a2fdeba08691768f27a8f62b41c56353aacafee21be08f1474; початкова інвентаризація зафіксована на v135.",f"Поточний HTML — v211, SHA-256 {digest}; початкова інвентаризація зафіксована на v135.")
 blob=blob if not (rel in {"JLPT_N1_v211_audit.md","README.md","PROJECT_STATUS.md","completion/BACKLOG.md"}) else text.encode("utf-8")
 dst=wt/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(blob)
run("git","config","user.name","github-actions[bot]",cwd=wt);run("git","config","user.email","41898282+users.noreply.github.com",cwd=wt)
run("git","add","--",*PUBLISH_PATHS,cwd=wt)
if subprocess.run(["git","diff","--cached","--quiet"],cwd=wt).returncode==0:raise SystemExit("empty v211 publication")
run("git","commit","-m","Publish verified JLPT N1 v211 C10 audit",cwd=wt,capture=False)
commit=run("git","rev-parse","HEAD",cwd=wt).stdout.strip();run("git","push","origin","HEAD:main",cwd=wt,capture=False);run("git","fetch","origin","main")
published=run("git","rev-parse","origin/main",cwd=wt).stdout.strip();blob=run("git","rev-parse",f"origin/main:{HTML_PATH}",cwd=wt).stdout.strip()
if published!=commit or blob!=run("git","rev-parse",f"HEAD:{HTML_PATH}",cwd=ROOT).stdout.strip():raise SystemExit("published commit/blob mismatch")
if hashlib.sha256((wt/HTML_PATH).read_bytes()).hexdigest()!=digest or len((wt/HTML_PATH).read_bytes())!=size:raise SystemExit("published HTML digest/size mismatch")
print(f"PASS published v211 commit={commit} blob={blob} sha256={digest} bytes={size}")
