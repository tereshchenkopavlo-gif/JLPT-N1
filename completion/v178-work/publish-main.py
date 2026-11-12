#!/usr/bin/env python3
import hashlib,json,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];W=ROOT/"completion"/"v178-work"
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
 need(git(["branch","--show-current"])=="work/v178-c10-next-pending","Wrong branch")
 html=ROOT/"JLPT_N1_ukrainian_reading_v178.html";h=hashlib.sha256(html.read_bytes()).hexdigest()
 need(prep.get("pass") is True and h==prep["checkpoint_sha256"],"HTML hash mismatch")
 need(browser.get("pass") is True and browser.get("sha256")==h,"Browser evidence mismatch")
 need(reg.get("pass") is True and reg.get("author_credit")=="3385/3914","Registry evidence mismatch")
 need(reg.get("registry_counts")=={"reviewed":3891,"fixed_rechecked":59,"pending":1892},"Registry totals mismatch")
 git(["fetch","origin","main"])
 actual=git(["rev-parse","origin/main"])
 need(actual==marker["expected_main_sha"],"main moved; publication aborted: "+actual)
 target="JLPT_N1_ukrainian_reading_v178.html"
 exists=subprocess.run(["git","cat-file","-e","origin/main:"+target],cwd=ROOT,text=True,capture_output=True,check=False)
 need(exists.returncode!=0,"v178 already exists on main")
 parent=Path(tempfile.mkdtemp(prefix="jlpt-v178-"));temp=parent/"main";added=False
 try:
  git(["worktree","add","--detach",str(temp),"origin/main"]);added=True
  copies={
   html:target,
   ROOT/"JLPT_N1_v178_audit.md":"JLPT_N1_v178_audit.md",
   ROOT/"completion"/"v178-acceptance.tsv":"completion/v178-acceptance.tsv",
   ROOT/"completion"/"review-register.csv":"completion/review-register.csv",
   ROOT/"completion"/"C10-followup-421-449-20261113.md":"completion/C10-followup-421-449-20261113.md",
   ROOT/"completion"/"v178-source-review.md":"completion/v178-source-review.md",
   ROOT/"README.md":"README.md",ROOT/"PROJECT_STATUS.md":"PROJECT_STATUS.md",
   ROOT/"completion"/"BACKLOG.md":"completion/BACKLOG.md",
   W/"prepare.py":"completion/v178-work/prepare.py",
   W/"browser.cjs":"completion/v178-work/browser.cjs",
   W/"finalize-evidence.py":"completion/v178-work/finalize-evidence.py",
   W/"write-docs.py":"completion/v178-work/write-docs.py",
   W/"publish-main.py":"completion/v178-work/publish-main.py",
   W/"updates.json":"completion/v178-work/updates.json",
   W/"author-decisions.tsv":"completion/v178-work/author-decisions.tsv",
   W/"source-review.md":"completion/v178-work/source-review.md",
   W/"scope.tsv":"completion/v178-work/scope.tsv",
   W/"checkpoint.json":"completion/v178-work/checkpoint.json",
   W/"preaudit-notes.md":"completion/v178-work/preaudit-notes.md",
   W/"prepare-results.json":"completion/v178-work/prepare-results.json",
   W/"browser-results.json":"completion/v178-work/browser-results.json",
   W/"registry-results.json":"completion/v178-work/registry-results.json",
   W/"candidate.json":"completion/v178-work/candidate.json",
   ROOT/"completion"/"v178-prepare-results.json":"completion/v178-prepare-results.json",
   ROOT/"completion"/"v178-browser-results.json":"completion/v178-browser-results.json",
   ROOT/"completion"/"v178-registry-results.json":"completion/v178-registry-results.json",
   ROOT/".github"/"workflows"/"v178-c10.yml":".github/workflows/v178-c10.yml"
  }
  paths=[]
  for src,dst in copies.items():
   out=temp/dst;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,out);paths.append(dst)
  status=temp/"PROJECT_STATUS.md"
  lines=status.read_text(encoding="utf-8").splitlines()
  lines[2]="Оновлено 13 листопада 2026. Актуальна **v178**. Опубліковано в main після успішних детермінованих і Chromium-перевірок; release commit збережено в Git history. Повний JLPT_N1_ukrainian_reading_v178.html, "+format(len(html.read_bytes()),",").replace(",", " ")+" байт, SHA-256 "+h+". [Аудит](JLPT_N1_v178_audit.md)"
  status.write_text("\n".join(lines)+"\n",encoding="utf-8")
  git(["config","user.name","github-actions[bot]"],cwd=temp)
  git(["config","user.email","41898282+actions@users.noreply.github.com"],cwd=temp)
  git(["add","--",*paths],cwd=temp)
  git(["add","--","PROJECT_STATUS.md"],cwd=temp)
  diff=subprocess.run(["git","diff","--cached","--quiet"],cwd=temp,check=False)
  need(diff.returncode!=0,"No changes to publish")
  git(["commit","-m","Publish verified JLPT N1 v178 C10 follow-up release"],cwd=temp)
  commit=git(["rev-parse","HEAD"],cwd=temp)
  git(["push","origin","HEAD:main"],cwd=temp)
  git(["fetch","origin","main"])
  need(git(["rev-parse","origin/main"])==commit,"Post-push main mismatch")
  remote=subprocess.run(["git","show","origin/main:"+target],cwd=ROOT,capture_output=True,check=True).stdout
  need(hashlib.sha256(remote).hexdigest()==h,"Published HTML differs from candidate")
  print(json.dumps({"pass":True,"main_commit":commit,"html_sha256":h,"html_bytes":len(remote),"files":paths+["PROJECT_STATUS.md"]},ensure_ascii=False,indent=2))
 finally:
  if added: git(["worktree","remove","--force",str(temp)],check=False)
  shutil.rmtree(parent,ignore_errors=True)
if __name__=="__main__":main()
