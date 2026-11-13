import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd().resolve()
EXPECTED_MAIN = "d68668354436e189add0c81475c5fd50432fcf8d"
EXPECTED_HTML_SHA256 = "75387f14bb77bfcc9f5d0ec224e5f4e6e14ba3d51465b0f435117d4f3af4351b"
EXPECTED_HTML_BYTES = 6942092
EXPECTED_HTML_BLOB = "e1a9f85ea4bc80461c7684fb06c7e933c5bb6f21"
HTML_PATH = "JLPT_N1_ukrainian_reading_v186.html"
PUBLISH_PATHS = [
    HTML_PATH,
    "JLPT_N1_v186_audit.md",
    "README.md",
    "PROJECT_STATUS.md",
    "completion/BACKLOG.md",
    "completion/review-register.csv",
    "completion/v186-acceptance.tsv",
    "completion/v186-c10-review.tsv",
    "completion/v186-prepare-results.json",
    "completion/v186-browser-results.json",
    "completion/v186-registry-results.json",
    "completion/v186-source-review.md",
]

def run(*args, cwd=ROOT, capture=True):
    return subprocess.run(
        args, cwd=cwd, check=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        text=capture
    )

run("git", "fetch", "origin", "main")
actual_main = run("git", "rev-parse", "origin/main").stdout.strip()
if actual_main != EXPECTED_MAIN:
    raise SystemExit(f"Refusing to publish: main moved from {EXPECTED_MAIN} to {actual_main}")

html = ROOT / HTML_PATH
data = html.read_bytes()
digest = hashlib.sha256(data).hexdigest()
if digest != EXPECTED_HTML_SHA256 or len(data) != EXPECTED_HTML_BYTES:
    raise SystemExit(f"Candidate digest/size mismatch: {digest} / {len(data)}")

for rel in PUBLISH_PATHS:
    result = subprocess.run(["git", "cat-file", "-e", f"HEAD:{rel}"], cwd=ROOT)
    if result.returncode:
        raise SystemExit(f"Missing committed publication file: {rel}")

worktree = Path("/tmp/jlpt-n1-v186-main")
if worktree.exists():
    shutil.rmtree(worktree)
run("git", "worktree", "add", "--detach", str(worktree), "origin/main")

for rel in PUBLISH_PATHS:
    blob = subprocess.run(
        ["git", "show", f"HEAD:{rel}"], cwd=ROOT,
        check=True, stdout=subprocess.PIPE
    ).stdout
    destination = worktree / rel
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(blob)

run("git", "config", "user.name", "github-actions[bot]", cwd=worktree)
run("git", "config", "user.email", "41898282+actions@users.noreply.github.com", cwd=worktree)
run("git", "add", "--", *PUBLISH_PATHS, cwd=worktree)
staged = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=worktree)
if staged.returncode == 0:
    raise SystemExit("Refusing empty publication commit")
run("git", "commit", "-m", "Publish verified JLPT N1 v186 C10 audit", cwd=worktree, capture=False)
commit = run("git", "rev-parse", "HEAD", cwd=worktree).stdout.strip()
run("git", "push", "origin", "HEAD:main", cwd=worktree, capture=False)
run("git", "fetch", "origin", "main")
published = run("git", "rev-parse", "origin/main").stdout.strip()
published_blob = run("git", "rev-parse", f"origin/main:{HTML_PATH}").stdout.strip()
published_html = (worktree / HTML_PATH).read_bytes()
published_digest = hashlib.sha256(published_html).hexdigest()
if published != commit:
    raise SystemExit(f"Main verification mismatch: expected {commit}, got {published}")
if published_blob != EXPECTED_HTML_BLOB:
    raise SystemExit(f"Published Git blob mismatch: {published_blob}")
if published_digest != EXPECTED_HTML_SHA256 or len(published_html) != EXPECTED_HTML_BYTES:
    raise SystemExit(f"Published HTML digest/size mismatch: {published_digest} / {len(published_html)}")
print(f"PASS published v186 commit={commit} blob={published_blob} sha256={published_digest} bytes={len(published_html)}")
