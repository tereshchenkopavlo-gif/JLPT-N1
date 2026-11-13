#!/usr/bin/env python3
import hashlib,json,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];W=ROOT/"completion"/"v179-work"
def git(args,cwd=ROOT,check=True):
 p=subprocess.run(["git",*args],cwd=cwd,text=True,capture_output=True,check=False)
 if check and p.returncode: raise RuntimeError(p.stderr[-3000:])
 return p.stdout.strip()
def need(x,m):
 if not x: raise RuntimeError(m)
def main():
 marker=json.loads((W/"PUBLISH").read_text(encoding="utf-8"))
 prep=json.loads((W/"prepare-results.json").read_text(encoding="utf-8"))
 browser=json.loads((W/"browser-results.json").read_text(encoding="utf-8"))
 reg=json.loads((W/"registry-results.json").read_text(encoding="utf-8"))
 need(git(["branch","--show-current"])=="work/v179-c11-context-quiz-review","Wrong branch")
 html=ROOT/"JLPT_N1_ukrainian_reading_v179.html";h=hashlib.sha256(html.read_bytes()).hexdigest()
 need(prep.get("pass") is True and h==prep["candidate_sha256"],"Candidate HTML hash mismatch")
 need(browser.get("pass") is True and browser.get("sha256")==h,"Chromium evidence mismatch")
 need(reg.get("pass") is True and reg.get("author_credit")=="3385/3914","Registry totals mismatch")
 need(reg.get("registry_counts")=={"reviewed":3892,"fixed_rechecked":59,"pending":1892},"Registry totals mismatch")
 need(reg.get("reviewed_meaning_quizzes")==266,"Meaning quiz count mismatch")
 git(["fetch","origin","main"]);actual=git(["rev-parse","origin/main"])
 need(actual==marker["expected_main_sha"],"main moved; guarded publication aborted: "+actual)
 exists=subprocess.run(["git","cat-file","-e","origin/main:JLPT_N1_ukrainian_reading_v179.html"],cwd=ROOT,capture_output=True,check=False)
 need(exists.returncode!=0,"v179 already exists on main")
 parent=Path(tempfile.mkdtemp(prefix="jlpt-v179-"));temp=parent/"main";added=False
 try:
  git(["worktree","add","--detach",str(temp),"origin/main"]);added=True
  mapping={
   html:"JLPT_N1_ukrainian_reading_v179.html",
   ROOT/"JLPT_N1_v179_audit.md":"JLPT_N1_v179_audit.md",
   ROOT/"README.md":"README.md",
   ROOT/"PROJECT_STATUS.md":"PROJECT_STATUS.md",
   ROOT/"completion"/"BACKLOG.md":"completion/BACKLOG.md",
   ROOT/"completion"/"review-register.csv":"completion/review-register.csv",
   ROOT/"completion"/"v179-c11-review.tsv":"completion/v179-c11-review.tsv",
   ROOT/"completion"/"v179-reading-pool-impact.json":"completion/v179-reading-pool-impact.json",
   ROOT/"completion"/"v179-acceptance.tsv":"completion/v179-acceptance.tsv",
   ROOT/"completion"/"v179-prepare-results.json":"completion/v179-prepare-results.json",
   ROOT/"completion"/"v179-browser-results.json":"completion/v179-browser-results.json",
   ROOT/"completion"/"v179-registry-results.json":"completion/v179-registry-results.json",
   ROOT/"completion"/"v179-source-review.md":"completion/v179-source-review.md",
   ROOT/"completion"/"C11-followup-2433-2468-20261113.md":"completion/C11-followup-2433-2468-20261113.md",
   ROOT/"completion"/"C11-followup-255-327-20261113.md":"completion/C11-followup-255-327-20261113.md",
   ROOT/".github"/"workflows"/"v179-c11.yml":".github/workflows/v179-c11.yml"
  }
  paths=[]
  for src,dst in mapping.items():
   out=temp/dst;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,out);paths.append(dst)
  status=temp/"PROJECT_STATUS.md";lines=status.read_text(encoding="utf-8").splitlines()
  lines[2]="Оновлено 13 листопада 2026. Актуальна **v179**. Опубліковано в main після успішних детермінованих і Chromium-перевірок. Повний JLPT_N1_ukrainian_reading_v179.html, "+format(len(html.read_bytes()),",").replace(",", " ")+" байт, SHA-256 "+h+". [Аудит](JLPT_N1_v179_audit.md)"
  status.write_text("\n".join(lines)+"\n",encoding="utf-8")
  git(["config","user.name","github-actions[bot]"],cwd=temp);git(["config","user.email","41898282+actions@users.noreply.github.com"],cwd=temp)
  git(["add","--",*paths,"PROJECT_STATUS.md"],cwd=temp)
  diff=subprocess.run(["git","diff","--cached","--quiet"],cwd=temp,check=False);need(diff.returncode!=0,"No publication changes")
  git(["commit","-m","Publish verified JLPT N1 v179 C11 meaning-quiz release"],cwd=temp)
  commit=git(["rev-parse","HEAD"],cwd=temp);git(["push","origin","HEAD:main"],cwd=temp);git(["fetch","origin","main"])
  need(git(["rev-parse","origin/main"])==commit,"Post-push main mismatch")
  remote=subprocess.run(["git","show","origin/main:JLPT_N1_ukrainian_reading_v179.html"],cwd=ROOT,capture_output=True,check=True).stdout
  need(hashlib.sha256(remote).hexdigest()==h,"Published HTML differs from candidate")
  print(json.dumps({"pass":True,"main_commit":commit,"html_sha256":h,"html_bytes":len(remote),"files":paths+["PROJECT_STATUS.md"]},ensure_ascii=False,indent=2))
 finally:
  if added: git(["worktree","remove","--force",str(temp)],check=False)
  shutil.rmtree(parent,ignore_errors=True)
if __name__=="__main__": main()
