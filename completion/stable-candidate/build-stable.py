"""Build the N1 release candidate from its pinned source."""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

source, output = map(Path, sys.argv[1:])
raw = source.read_bytes()
assert hashlib.sha256(raw).hexdigest() == "06a7d463257c83816b28532a261d0be42728386655722c8c58a2231b28f174c7"
html = raw.decode()
changes = [
    ("let ACTIVE_VOCAB = [...DEFAULT_VOCAB];", """let ACTIVE_VOCAB = [...DEFAULT_VOCAB];
const DEFERRED_SESSION_VOCAB = new Set([
  1510, 3363, 3375, 3417, 3441, 3444, 3525, 3561, 3565,
  3569, 3594, 3636, 3646, 3652, 3654, 3677, 3679
]);
function isSessionVocab(id) {
  return !DEFERRED_SESSION_VOCAB.has(Number(id));
}
function sessionVocabCount() {
  return ACTIVE_VOCAB.filter(word => isSessionVocab(word.id)).length;
}"""),
    ("const source=it.kind==='g'?GRAMMAR:ACTIVE_VOCAB;", "const source=it.kind==='g'?GRAMMAR:ACTIVE_VOCAB.filter(word => isSessionVocab(word.id));"),
    ("ACTIVE_VOCAB.filter(x=>x.id!==v.id", "ACTIVE_VOCAB.filter(x=>isSessionVocab(x.id)&&x.id!==v.id"),
    ("ACTIVE_VOCAB.filter(v=>v.id!==item.word.id", "ACTIVE_VOCAB.filter(v=>isSessionVocab(v.id)&&v.id!==item.word.id"),
    ("const defs = items.map(it =>", "const defs = items.filter(it => it.kind !== 'v' || isSessionVocab(it.id)).map(it =>"),
    ("for (const id of Object.keys(state.vp || {})) {", "for (const id of Object.keys(state.vp || {})) {\n          if (!isSessionVocab(id)) continue;"),
    ("for (const [id, p] of Object.entries(state.vp)) {", "for (const [id, p] of Object.entries(state.vp)) {\n    if (!isSessionVocab(id)) continue;"),
    ("ACTIVE_VOCAB.filter(w => !state.vp[w.id])", "ACTIVE_VOCAB.filter(w => isSessionVocab(w.id) && !state.vp[w.id])"),
    ("const dueCount = Object.values(state.vp)", "const sessionProgress = Object.entries(state.vp).filter(([id]) => isSessionVocab(id)).map(([, progress]) => progress);\n  const dueCount = sessionProgress"),
    ("const sVocab = Object.values(state.vp)", "const sVocab = sessionProgress"),
    ("const vocabTarget = state.meta.vocabTarget || 2400;", "const vocabTarget = Math.min(state.meta.vocabTarget || 2400, (sessionVocabCount() || 1));"),
    ("登録済み ${ACTIVE_VOCAB.length.toLocaleString()}語", "出題対象 ${sessionVocabCount().toLocaleString()}語"),
    ("getElementById('vocabTotalLabel').textContent = ACTIVE_VOCAB.length", "getElementById('vocabTotalLabel').textContent = sessionVocabCount()"),
    ("Math.max(1, ACTIVE_VOCAB.length)", "Math.max(1, sessionVocabCount())"),
    ("getElementById('vocabTargetMaxLabel').textContent = ACTIVE_VOCAB.length", "getElementById('vocabTargetMaxLabel').textContent = sessionVocabCount()"),
]
for old, new in changes:
    assert old in html and new not in html, (old, new)
    html = html.replace(old, new)
rollback = html
for old, new in reversed(changes):
    rollback = rollback.replace(new, old)
assert rollback.encode() == raw
for script in re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", html, re.S):
    subprocess.run(["node", "--check"], text=True, input=script, check=True)
output.write_bytes(html.encode())
print(hashlib.sha256(html.encode()).hexdigest())
