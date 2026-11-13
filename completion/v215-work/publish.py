import hashlib,json,shutil,subprocess,re
from pathlib import Path
ROOT=Path.cwd().resolve()
EXPECTED_MAIN="5ff0a3ab9ba8aea733ca3b10d5422b18266bddf9"
HTML_PATH="JLPT_N1_ukrainian_reading_v215.html"
PUBLISH_PATHS=[HTML_PATH,"JLPT_N1_v215_audit.md","README.md","PROJECT_STATUS.md","completion/BACKLOG.md","completion/review-register.csv","completion/v215-acceptance.tsv","completion/v215-c10-review.tsv","completion/v215-field-changes.tsv","completion/v215-pair-review.tsv","completion/v215-source-review.md","completion/v215-prepare-results.json","completion/v215-browser-results.json","completion/v215-registry-results.json"]
def run(*args,cwd=ROOT,capture=True):
 return subprocess.run(args,cwd=cwd,check=True,stdout=subprocess.PIPE if capture else None,stderr=subprocess.PIPE if capture else None,text=capture)
run("git","fetch","origin","main")
main=run("git","rev-parse","origin/main").stdout.strip()
if main!=EXPECTED_MAIN: raise SystemExit(f"Refusing publication: main moved from {EXPECTED_MAIN} to {main}")
prepare=json.loads((ROOT/"completion/v215-work/prepare-results.json").read_text(encoding="utf-8"))
registry=json.loads((ROOT/"completion/v215-work/registry-results.json").read_text(encoding="utf-8"))
browser=json.loads((ROOT/"completion/v215-work/browser-results.json").read_text(encoding="utf-8"))
if not(prepare.get("pass") and registry.get("pass") and browser.get("pass")): raise SystemExit("Refusing publication: acceptance results did not pass")
data=(ROOT/HTML_PATH).read_bytes(); digest=hashlib.sha256(data).hexdigest(); size=len(data)
blob_sha=hashlib.sha1(b"blob "+str(size).encode()+b"\0"+data).hexdigest()
if digest!=prepare["candidate_sha256"] or size!=prepare["candidate_bytes"]: raise SystemExit("candidate digest/size mismatch")
wt=Path("/tmp/jlpt-n1-v215-main")
if wt.exists(): shutil.rmtree(wt)
run("git","worktree","add","--detach",str(wt),"origin/main")
summary="v215 — C10: 12 pending-карток (1019, 1028, 1078, 1082, 1089, 1093, 1191, 1255, 1258, 1260, 1270, 1272) авторськи зараховано як fixed_rechecked; внесено 13 точних змін у 12 картках. Додатково переглянуто 11 pending-пар (255, 256, 276, 277, 281, 282, 303, 316, 324, 339, 345) без зміни їхнього тексту. Авторський credit 3749/3914; реєстр після v215 3929/404/1514, словниковий зріз 3347/402/165, vocab_pair 31/1/827. Усі 12 карток мають індивідуальні докази пілота v153. Deterministic build, registry, Python/Node syntax та Chromium acceptance (360/412/1280 px, storage round-trip, 0 page errors) пройшли. Незалежне, фізичне й правове/походження приймання залишаються окремими відкритими етапами."
for rel in PUBLISH_PATHS:
 raw=subprocess.run(["git","show",f"HEAD:{rel}"],cwd=ROOT,check=True,stdout=subprocess.PIPE).stdout
 if rel in {"JLPT_N1_v215_audit.md","README.md","PROJECT_STATUS.md","completion/BACKLOG.md"}:
  content=raw.decode("utf-8")
  if rel=="JLPT_N1_v215_audit.md":
   content=content.replace("__V215_SHA256__",digest).replace("__V215_BYTES__",str(size)).replace("__V215_BLOB__",blob_sha)
  elif rel=="README.md":
   content=content.replace("Актуальна опублікована редакція: v214.","Актуальна опублікована редакція: v215.")
   content=content.replace("Повний автономний HTML v214","Повний автономний HTML v215").replace("JLPT_N1_ukrainian_reading_v214.html","JLPT_N1_ukrainian_reading_v215.html")
   content=content.replace("Авторський аудит v214","Авторський аудит v215").replace("JLPT_N1_v214_audit.md","JLPT_N1_v215_audit.md")
   section="## Стан випуску v215\n\n"+summary+f"\n\nHTML v215: {size} байтів; SHA-256 {digest}; Git blob {blob_sha}.\n"
   content=content.replace("## Стан випуску v214",section+"\n## Історичний випуск v214",1)
  elif rel=="PROJECT_STATUS.md":
   old="Оновлено 14 листопада 2026. Актуальна **v214** у main після guarded-публікації. Повний HTML v214 — 6949689 байтів, SHA-256 0436bb8dc402e85eab47c442e094c1b725c3e97302500f559bd5b1fe944225b8, Git blob 9ca4fcc6dc6f0db7eaaebed232cc684868dfb5b2."
   new=f"Оновлено 14 листопада 2026. Актуальна **v215** у main після guarded-публікації. Повний HTML v215 — {size} байтів, SHA-256 {digest}, Git blob {blob_sha}."
   if old not in content: raise SystemExit("PROJECT_STATUS v214 marker mismatch")
   content=content.replace(old,new,1)
   section=f"## Опублікований випуск v215 — C10 авторський аудит\n\n- Перевірено 12 pending-карток: 1019, 1028, 1078, 1082, 1089, 1093, 1191, 1255, 1258, 1260, 1270, 1272; усі 12 зараховано як fixed_rechecked.\n- Внесено 13 точних змін; японські приклади й POS-map не змінювалися. Переглянуто 11 порівняльних пар без зміни тексту.\n- Авторський credit після v215 — 3749/3914. Реєстр: 3929/404/1514 загалом, 3347/402/165 у словнику, 31/1/827 для пар.\n- HTML v215: {size} байтів, SHA-256 {digest}, Git blob {blob_sha}. Deterministic build, registry, Python/Node syntax та Chromium acceptance успішні.\n- Незалежне лінгвістичне, фізичне Android/Windows та правове/походження приймання залишаються відкритими.\n"
   content=content.replace("## Опублікований випуск v214 — C10 авторський аудит",section+"\n## Опублікований випуск v214 — C10 авторський аудит",1)
  else:
   content=content.replace("Поточний HTML — v214, SHA-256 0436bb8dc402e85eab47c442e094c1b725c3e97302500f559bd5b1fe944225b8;","Поточний HTML — v215, SHA-256 "+digest+";",1)
   content=content.replace("\nv214 — C10:","\n"+summary+f" HTML: {size} bytes; SHA-256 {digest}; blob {blob_sha}.\n\nv214 — C10:",1)
  raw=content.encode("utf-8")
 dst=wt/rel; dst.parent.mkdir(parents=True,exist_ok=True); dst.write_bytes(raw)
run("git","config","user.name","github-actions[bot]",cwd=wt)
run("git","config","user.email","41898282+users.noreply.github.com",cwd=wt)
run("git","add","--",*PUBLISH_PATHS,cwd=wt)
if subprocess.run(["git","diff","--cached","--quiet"],cwd=wt).returncode==0: raise SystemExit("empty v215 publication")
run("git","commit","-m","Publish verified JLPT N1 v215 C10 audit",cwd=wt,capture=False)
commit=run("git","rev-parse","HEAD",cwd=wt).stdout.strip()
run("git","push","origin","HEAD:main",cwd=wt,capture=False)
run("git","fetch","origin","main")
published=run("git","rev-parse","origin/main",cwd=wt).stdout.strip()
published_blob=run("git","rev-parse",f"origin/main:{HTML_PATH}",cwd=wt).stdout.strip()
if published!=commit or published_blob!=blob_sha: raise SystemExit("published commit/blob mismatch")
if hashlib.sha256((wt/HTML_PATH).read_bytes()).hexdigest()!=digest: raise SystemExit("published HTML SHA mismatch")
print(f"PASS published v215 commit={commit} blob={published_blob} sha256={digest} bytes={size}")
