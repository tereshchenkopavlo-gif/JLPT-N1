"""Additional content-integrity checks for v131 (NOT an expert language review)."""
import json, re, unicodedata
from pathlib import Path
p=Path("audit131")
items=json.loads((p/"new-readings.json").read_text(encoding="utf-8"))
assert len(items)==18
errors=[]
seen_prompts=set()
stats={"texts":len(items),"questions":0,"choices":0,"evidence_in_source":0,"paragraphs_matched":0,"unique_prompts":0}
def norm(s):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC",s)).strip()
for x in items:
    where=x["id"]
    ja=x["ja"].strip();uk=x["uk"].strip()
    if not re.search(r"[ぁ-んァ-ン一-龯]",ja): errors.append(f"{where}: no Japanese characters")
    if not re.search(r"[іїєґ]",uk,re.I): errors.append(f"{where}: missing Ukrainian characters")
    if not x["title"].strip(): errors.append(f"{where}: empty title")
    if len(ja.split("\n\n"))!=len(uk.split("\n\n")): errors.append(f"{where}: translation paragraph mismatch")
    else: stats["paragraphs_matched"]+=1
    for idx,q in enumerate(x["questions"],1):
        ref=f"{where}/q{idx}"
        stats["questions"]+=1
        answers=q["choices"];stats["choices"]+=len(answers)
        if q["answer"] not in range(4): errors.append(f"{ref}: invalid key")
        if len(answers)!=4: errors.append(f"{ref}: not four answers");continue
        if any(not norm(v) for v in answers): errors.append(f"{ref}: blank option")
        if len(set(map(norm,answers)))!=4: errors.append(f"{ref}: repeated options")
        if not norm(q["prompt"]) or not norm(q["explain"]): errors.append(f"{ref}: missing prompt/explanation")
        if not re.search(r"[іїєґ]",q["explain"],re.I): errors.append(f"{ref}: missing Ukrainian explanation")
        if q["evidence"] not in ja: errors.append(f"{ref}: supporting quote absent")
        else: stats["evidence_in_source"]+=1
        key=norm(q["prompt"])
        if key in seen_prompts: errors.append(f"{ref}: repeated question prompt")
        else: seen_prompts.add(key);stats["unique_prompts"]+=1
assert stats["questions"]==42 and stats["choices"]==168,stats
report={"status":"passed" if not errors else "failed","counts":stats,
"scope":"Form, completeness and literal quotation only; does not validate answer semantics, language quality, distractor plausibility or user interaction.",
"errors":errors}
(p/"content-integrity-results.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(report,ensure_ascii=False,indent=2))
if errors: raise SystemExit(1)
