#!/usr/bin/env python3
import csv,hashlib,json,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];W=ROOT/"completion"/"v177-work"
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
 need(git(["branch","--show-current"])=="work/v177-c10-pos-followups","Wrong branch")
 html=ROOT/"JLPT_N1_ukrainian_reading_v177.html";h=hashlib.sha256(html.read_bytes()).hexdigest()
 need(prep.get("pass") is True and h==prep["checkpoint_sha256"],"HTML hash mismatch")
 need(browser.get("pass") is True and browser.get("sha256")==h,"Browser evidence mismatch")
 need(reg.get("pass") is True and reg.get("author_credit")=="3373/3914","Registry evidence mismatch")
 need(reg.get("registry_counts")=={"reviewed":3890,"fixed_rechecked":48,"pending":1904},"Registry totals mismatch")
 git(["fetch","origin","main"])
 actual=git(["rev-parse","origin/main"])
 need(actual==marker["expected_main_sha"],"main moved: "+actual)
 target="JLPT_N1_ukrainian_reading_v177.html"
 exists=subprocess.run(["git","cat-file","-e","origin/main:"+target],cwd=ROOT,text=True,capture_output=True,check=False)
 need(exists.returncode!=0,"v177 already exists on main")
 parent=Path(tempfile.mkdtemp(prefix="jlpt-v177-"));temp=parent/"main";added=False
 try:
  git(["worktree","add","--detach",str(temp),"origin/main"]);added=True
  copies={
   html:target,
   ROOT/"JLPT_N1_v177_audit.md":"JLPT_N1_v177_audit.md",
   ROOT/"completion"/"v177-acceptance.tsv":"completion/v177-acceptance.tsv",
   ROOT/"completion"/"v177-pair-review.tsv":"completion/v177-pair-review.tsv",
   ROOT/"completion"/"C10-followup-364-416-20261113.md":"completion/C10-followup-364-416-20261113.md",
   ROOT/"completion"/"review-register.csv":"completion/review-register.csv",
   ROOT/"README.md":"README.md",ROOT/"PROJECT_STATUS.md":"PROJECT_STATUS.md",
   ROOT/"completion"/"BACKLOG.md":"completion/BACKLOG.md",
   W/"prepare.py":"completion/v177-work/prepare.py",
   W/"browser.cjs":"completion/v177-work/browser.cjs",
   W/"finalize-evidence.py":"completion/v177-work/finalize-evidence.py",
   W/"write-docs.py":"completion/v177-work/write-docs.py",
   W/"publish-main.py":"completion/v177-work/publish-main.py",
   W/"updates.json":"completion/v177-work/updates.json",
   W/"pair-review.tsv":"completion/v177-work/pair-review.tsv",
   W/"prepare-results.json":"completion/v177-prepare-results.json",
   W/"browser-results.json":"completion/v177-browser-results.json",
   W/"registry-results.json":"completion/v177-registry-results.json",
   W/"candidate.json":"completion/v177-work/candidate.json",
   W/"checkpoint.json":"completion/v177-work/checkpoint.json",
   W/"preaudit-notes.md":"completion/v177-work/preaudit-notes.md",
   ROOT/".github"/"workflows"/"v177-c10.yml":".github/workflows/v177-c10.yml"
  }
  paths=[]
  for src,dst in copies.items():
   out=temp/dst;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,out);paths.append(dst)
  git(["config","user.name","github-actions[bot]"],cwd=temp)
  git(["config","user.email","41898282+actions@users.noreply.github.com"],cwd=temp)
  git(["add","--",*paths],cwd=temp)
  diff=subprocess.run(["git","diff","--cached","--quiet"],cwd=temp,check=False)
  need(diff.returncode!=0,"No changes to publish")
  git(["commit","-m","Publish verified JLPT N1 v177 C10 follow-up release"],cwd=temp)
  commit=git(["rev-parse","HEAD"],cwd=temp)
  git(["push","origin","HEAD:main"],cwd=temp)
  git(["fetch","origin","main"])
  need(git(["rev-parse","origin/main"])==commit,"Post-push main mismatch")
  remote=subprocess.run(["git","show","origin/main:"+target],cwd=ROOT,capture_output=True,check=True).stdout
  need(hashlib.sha256(remote).hexdigest()==h,"Published HTML differs from candidate")
  print(json.dumps({"pass":True,"main_commit":commit,"html_sha256":h,"html_bytes":len(remote),"files":paths},ensure_ascii=False,indent=2))
 finally:
  if added: git(["worktree","remove","--force",str(temp)],check=False)
  shutil.rmtree(parent,ignore_errors=True)
if __name__=="__main__":main()
