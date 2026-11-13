import hashlib,json,shutil,subprocess
from pathlib import Path
ROOT=Path.cwd().resolve()
EXPECTED_MAIN="4f261c2650caacd2d328f6109ca34e713fb6dd6d"
HTML_PATH="JLPT_N1_ukrainian_reading_v212.html"
PUBLISH_PATHS=[HTML_PATH,"JLPT_N1_v212_audit.md","README.md","PROJECT_STATUS.md","completion/BACKLOG.md","completion/review-register.csv","completion/v212-acceptance.tsv","completion/v212-c10-review.tsv","completion/v212-field-changes.tsv","completion/v212-pair-review.tsv","completion/v212-pair-changes.tsv","completion/v212-source-review.md","completion/v212-prepare-results.json","completion/v212-browser-results.json","completion/v212-registry-results.json"]
def run(*args,cwd=ROOT,capture=True):
 return subprocess.run(args,cwd=cwd,check=True,stdout=subprocess.PIPE if capture else None,stderr=subprocess.PIPE if capture else None,text=capture)
run("git","fetch","origin","main");main=run("git","rev-parse","origin/main").stdout.strip()
if main!=EXPECTED_MAIN:raise SystemExit(f"Refusing publication: main moved from {EXPECTED_MAIN} to {main}")
prepare=json.loads((ROOT/"completion/v212-work/prepare-results.json").read_text(encoding="utf-8"))
registry=json.loads((ROOT/"completion/v212-work/registry-results.json").read_text(encoding="utf-8"))
browser=json.loads((ROOT/"completion/v212-work/browser-results.json").read_text(encoding="utf-8"))
if not(prepare.get("pass") and registry.get("pass") and browser.get("pass")):raise SystemExit("Refusing publication: acceptance results did not pass")
data=(ROOT/HTML_PATH).read_bytes();digest=hashlib.sha256(data).hexdigest();size=len(data)
if digest!=prepare["candidate_sha256"] or size!=prepare["candidate_bytes"]:raise SystemExit("candidate digest/size mismatch")
wt=Path("/tmp/jlpt-n1-v212-main")
if wt.exists():shutil.rmtree(wt)
run("git","worktree","add","--detach",str(wt),"origin/main")
for rel in PUBLISH_PATHS:
 blob=subprocess.run(["git","show",f"HEAD:{rel}"],cwd=ROOT,check=True,stdout=subprocess.PIPE).stdout
 if rel in {"JLPT_N1_v212_audit.md","README.md","PROJECT_STATUS.md","completion/BACKLOG.md"}:
  text=blob.decode("utf-8").replace("__V212_SHA256__",digest).replace("__V212_BYTES__",str(size))
  if rel=="README.md":
   text=text.replace("Актуальна **v211** у main після guarded-публікації. Кандидат v212 у work/v212-c10-next-pending.","Актуальна **v212** у main після guarded-публікації.")
   text=text.replace("Кандидат v212:","Опубліковано v212:")
   text=text.replace("Докази v211:","Докази v212:")
   text=text.replace("completion/v211-","completion/v212-")
   text=text.replace("JLPT_N1_v211","JLPT_N1_v212")
   text=text.replace("JLPT_N1_ukrainian_reading_v211.html","JLPT_N1_ukrainian_reading_v212.html")
   text=text.replace("JLPT_N1_v211_audit.md","JLPT_N1_v212_audit.md")
  elif rel=="PROJECT_STATUS.md":
   text=text.replace("Оновлено 13 листопада 2026. Актуальна **v211** у main. Кандидат **v212** у гілці work/v212-c10-next-pending, ще не опублікований. Повний HTML v211 — 6948888 байти, SHA-256 c4e10162669b9b0634c9b04b9d1986895ec96d628a02514f2a9a2352989b5f68.","Оновлено 13 листопада 2026. Актуальна **v212** у main після guarded-публікації. Повний HTML — "+size+" байти, SHA-256 "+digest+". [Повний HTML](https://github.com/tereshchenkopavlo-gif/JLPT-N1/blob/main/JLPT_N1_ukrainian_reading_v212.html) · [Аудит](https://github.com/tereshchenkopavlo-gif/JLPT-N1/blob/main/JLPT_N1_v212_audit.md).")
   text=text.replace("Підготовлено 15 точних змін","Внесено 15 точних змін")
   text=text.replace("Очікуваний авторський credit після приймання","Авторський credit після v212")
   text=text.replace("## Поточний кандидат v212 — C10 авторський аудит","## Опублікований випуск v212 — C10 авторський аудит")
   text=text.replace("Кандидат v212 ще не зібрано; після детермінованої перевірки й Chromium acceptance публікувати лише точні артефакти в main, робочу гілку не зливати.",f"Опублікований HTML v212: {size} байти, SHA-256 {digest}. Deterministic build, registry та Chromium acceptance успішні; робочу гілку не зливати.")
  elif rel=="completion/BACKLOG.md":
   text=text.replace("Поточний HTML — v211, SHA-256 c4e10162669b9b0634c9b04b9d1986895ec96d628a02514f2a9a2352989b5f68; початкова інвентаризація зафіксована на v135.",f"Поточний HTML — v212, SHA-256 {digest}; початкова інвентаризація зафіксована на v135.")
   text=text.replace("v212 candidate:","v212 опубліковано:")
 if rel=="JLPT_N1_v212_audit.md":
  text=text.replace("Кандидат v212:","Опублікований v212:")
  text=text.replace("## Межі",f"## Публікація\n\nОпубліковано в main із SHA-256 {digest}, {size} байт. Deterministic prepare, registry і Chromium acceptance успішні.\n\n## Межі")
 blob=blob if not (rel in {"JLPT_N1_v212_audit.md","README.md","PROJECT_STATUS.md","completion/BACKLOG.md"}) else text.encode("utf-8")
 dst=wt/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(blob)
run("git","config","user.name","github-actions[bot]",cwd=wt);run("git","config","user.email","41898282+users.noreply.github.com",cwd=wt)
run("git","add","--",*PUBLISH_PATHS,cwd=wt)
if subprocess.run(["git","diff","--cached","--quiet"],cwd=wt).returncode==0:raise SystemExit("empty v212 publication")
run("git","commit","-m","Publish verified JLPT N1 v212 C10 audit",cwd=wt,capture=False)
commit=run("git","rev-parse","HEAD",cwd=wt).stdout.strip();run("git","push","origin","HEAD:main",cwd=wt,capture=False);run("git","fetch","origin","main")
published=run("git","rev-parse","origin/main",cwd=wt).stdout.strip();blob=run("git","rev-parse",f"origin/main:{HTML_PATH}",cwd=wt).stdout.strip()
if published!=commit or blob!=run("git","rev-parse",f"HEAD:{HTML_PATH}",cwd=ROOT).stdout.strip():raise SystemExit("published commit/blob mismatch")
if hashlib.sha256((wt/HTML_PATH).read_bytes()).hexdigest()!=digest or len((wt/HTML_PATH).read_bytes())!=size:raise SystemExit("published HTML digest/size mismatch")
print(f"PASS published v212 commit={commit} blob={blob} sha256={digest} bytes={size}")
