import hashlib,json,shutil,subprocess,re
from pathlib import Path
ROOT=Path.cwd().resolve()
EXPECTED_MAIN="59e621fed204052574e2349752c338fab17598e8"
HTML_PATH="JLPT_N1_ukrainian_reading_v215.html"
PUBLISH_PATHS=[HTML_PATH,"JLPT_N1_v215_audit.md","README.md","PROJECT_STATUS.md","completion/BACKLOG.md","completion/review-register.csv","completion/v215-acceptance.tsv","completion/v215-c10-review.tsv","completion/v215-field-changes.tsv","completion/v215-source-review.md","completion/v215-prepare-results.json","completion/v215-browser-results.json","completion/v215-registry-results.json"]
def run(*args,cwd=ROOT,capture=True):
 return subprocess.run(args,cwd=cwd,check=True,stdout=subprocess.PIPE if capture else None,stderr=subprocess.PIPE if capture else None,text=capture)
run("git","fetch","origin","main")
main=run("git","rev-parse","origin/main").stdout.strip()
if main!=EXPECTED_MAIN: raise SystemExit(f"Refusing publication: main moved from {EXPECTED_MAIN} to {main}")
prepare=json.loads((ROOT/"completion/v215-work/prepare-results.json").read_text(encoding="utf-8"))
registry=json.loads((ROOT/"completion/v215-work/registry-results.json").read_text(encoding="utf-8"))
browser=json.loads((ROOT/"completion/v215-work/browser-results.json").read_text(encoding="utf-8"))
expected_ids=[1019,1028,1078,1082,1089,1093,1191,1255,1258,1260,1270,1272,1276,1280,1285,1290,1292,1293,1296]
if not(prepare.get("pass") and registry.get("pass") and browser.get("pass")): raise SystemExit("Refusing publication: acceptance results did not pass")
if prepare.get("fixed_rechecked")!=expected_ids or prepare.get("author_credit_after")!=3756 or browser.get("reviewed_card_count")!=19: raise SystemExit("unexpected v215 scope or author credit")
if registry.get("after",{}).get("all")!={"reviewed":3918,"fixed_rechecked":411,"pending":1518,"total":5847}: raise SystemExit("unexpected registry target")
data=(ROOT/HTML_PATH).read_bytes(); digest=hashlib.sha256(data).hexdigest(); size=len(data)
blob_sha=hashlib.sha1(b"blob "+str(size).encode()+b"\0"+data).hexdigest()
if digest!=prepare["candidate_sha256"] or size!=prepare["candidate_bytes"]: raise SystemExit("candidate digest/size mismatch")
wt=Path("/tmp/jlpt-n1-v215-main")
if wt.exists(): shutil.rmtree(wt)
run("git","worktree","add","--detach",str(wt),"origin/main")
summary="v215 — C10: 19 pending-карток (1019, 1028, 1078, 1082, 1089, 1093, 1191, 1255, 1258, 1260, 1270, 1272, 1276, 1280, 1285, 1290, 1292, 1293, 1296) авторськи зараховано як fixed_rechecked; внесено 21 точну зміну у 19 картках, зокрема дві японські дефініції. Для ID1280 збережено POS 名詞 після словникової звірки прислівникового вживання 再三. Лексичні пари не переглядалися й не змінювалися. Авторський credit 3756/3914; реєстр після v215 3918/411/1518, словниковий зріз 3347/409/158, vocab_pair 20/1/838."
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
   content=re.sub(r"\n## Кандидат v215\n.*$", "", content, flags=re.S)
   content=content.replace("## Стан випуску v214","## Історичний випуск v214",1)
   section="## Стан випуску v215\n\n"+summary+f"\n\nHTML v215: {size} байтів; SHA-256 {digest}; Git blob {blob_sha}.\n"
   content=content.replace("## Історичний випуск v214",section+"\n## Історичний випуск v214",1)
  elif rel=="PROJECT_STATUS.md":
   old="Оновлено 14 листопада 2026. Актуальна **v214** у main. Кандидат **v215** у гілці work/v215-c10-next-pending, ще не опублікований. Повний HTML v214 — 6949689 байтів, SHA-256 0436bb8dc402e85eab47c442e094c1b725c3e97302500f559bd5b1fe944225b8, Git blob 9ca4fcc6dc6f0db7eaaebed232cc684868dfb5b2."
   new=f"Оновлено 14 листопада 2026. Актуальна **v215** у main після guarded-публікації. Повний HTML v215 — {size} байтів, SHA-256 {digest}, Git blob {blob_sha}."
   if old not in content: raise SystemExit("PROJECT_STATUS v214 marker mismatch")
   content=content.replace(old,new,1)
   content=re.sub(r"## Поточний кандидат v215 — C10 авторський аудит\n.*?(?=## Опублікований випуск v214)", "", content, flags=re.S)
   section=f"## Опублікований випуск v215 — C10 авторський аудит\n\n- Перевірено 19 pending-карток: 1019, 1028, 1078, 1082, 1089, 1093, 1191, 1255, 1258, 1260, 1270, 1272, 1276, 1280, 1285, 1290, 1292, 1293, 1296; усі 19 зараховано як fixed_rechecked.\n- Внесено 21 точну зміну у 19 картках; уточнено дві японські дефініції. ID1280 збережено з POS 名詞; лексичні пари не переглядалися й не змінювалися.\n- Авторський credit після v215 — 3756/3914. Реєстр: 3918/411/1518 загалом, 3347/409/158 у словнику, 20/1/838 для пар.\n- HTML v215: {size} байтів, SHA-256 {digest}, Git blob {blob_sha}. Deterministic build, registry, Python/Node syntax та Chromium acceptance успішні.\n- Незалежне лінгвістичне, фізичне Android/Windows та правове/походження приймання залишаються відкритими.\n"
   content=content.replace("## Опублікований випуск v214",section+"\n## Опублікований випуск v214",1)
  else:
   content=content.replace("Поточний HTML — v214, SHA-256 0436bb8dc402e85eab47c442e094c1b725c3e97302500f559bd5b1fe944225b8;","Поточний HTML — v215, SHA-256 "+digest+";",1)
   content=content.replace("\nv214 — C10:","\n"+summary+f" HTML: {size} байтів; SHA-256 {digest}; blob {blob_sha}.\n\nv214 — C10:",1)
   lines=content.splitlines()
   row="| C10 | 1 | in_progress — авторський аудит 3914 словникових карток; повний обсяг ще не завершено | v215 опубліковано: 19 карток fixed_rechecked, 21 точна зміна, дві японські дефініції; авторський credit 3756/3914. Докази: JLPT_N1_v215_audit.md, v215-acceptance.tsv, v215-c10-review.tsv, v215-field-changes.tsv, v215-source-review.md, v215-prepare-results.json, v215-browser-results.json, v215-registry-results.json. Deterministic build, registry, Python/Node syntax і Chromium acceptance успішні; лексичні пари не змінювалися. Незалежне, фізичне й правове/походження приймання відкрите. |"
   lines=[row if x.startswith("| C10 |") else x for x in lines]
   content="\n".join(lines)+"\n"
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
