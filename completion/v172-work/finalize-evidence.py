#!/usr/bin/env python3
"""Create exact acceptance evidence and update only the 18 reviewed registry rows."""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path
import re

SOURCE = Path("JLPT_N1_ukrainian_reading_v171.html")
TARGET = Path("JLPT_N1_ukrainian_reading_v172.html")
REGISTRY = Path("completion/review-register.csv")
UPDATES = Path("completion/v172-work/updates.json")
IDS = [3701,3710,3716,3723,3724,3725,3736,3739,3742,3745,3747,3753,3757]
PAIRS = [
    ("817:3702:3710",817,"3702","3710","related","〜員 позначає членство/належність до організації, а 〜者 — особу за дією, станом або роллю; 社員 і 参加者 не взаємозамінні."),
    ("819:3706:3723",819,"3706","3723","related","〜感 позначає відчуття чи враження, 〜観 — погляди або спосіб мислення; 安心感 і 価値観 демонструють різні семантичні типи."),
    ("821:3725:3726",821,"3725","3726","confusable","〜圏 — територіальна сфера/діапазон, 〜権 — право або повноваження; 徒歩圏 і 決定権 різняться і написанням, і значенням."),
    ("822:3736:3737",822,"3736","3737","related","〜隊 — організований загін із завданням, 〜陣 — сукупність людей у певній ролі; 救助隊 і 取材陣 не є повними синонімами."),
    ("823:3742:3759",823,"3742","3759","related","お手上げ — стан повного безсилля знайти вихід, 手を焼く — мати значні труднощі; перше не є простим синонімом другого.")
]

def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

def block(html, name):
    match = re.search(r"const " + re.escape(name) + r"\s*=\s*", html)
    if not match:
        raise ValueError(name)
    start = match.end()
    value, end = json.JSONDecoder().raw_decode(html, start)
    if compact(value) != html[start:end]:
        raise ValueError("Unexpected serialization: " + name)
    return value

def digest(value):
    return hashlib.sha256(compact(value).encode("utf-8")).hexdigest()

def main():
    before_html = SOURCE.read_text(encoding="utf-8")
    after_html = TARGET.read_text(encoding="utf-8")
    before_cards = block(before_html, "VOCAB_DETAILS_BY_ID")
    after_cards = block(after_html, "VOCAB_DETAILS_BY_ID")
    before_pos = block(before_html, "VOCAB_POS_BY_ID")
    after_pos = block(after_html, "VOCAB_POS_BY_ID")
    updates = json.loads(UPDATES.read_text(encoding="utf-8"))
    fields = {}
    for edit in updates:
        if edit["op"] == "set" and edit["block"] == "VOCAB_DETAILS_BY_ID":
            fields.setdefault(edit["path"][0], []).append(".".join(map(str,edit["path"][1:])))
        elif edit["op"] == "set" and edit["block"] == "VOCAB_POS_BY_ID":
            fields.setdefault(edit["path"][0], []).append("POS")
        elif edit["op"] == "rename_key":
            fields.setdefault("3757", []).append("VOCAB_KANA_EXAMPLE_TARGETS")
    with Path("completion/v172-acceptance.tsv").open("w",encoding="utf-8",newline="") as f:
        w=csv.writer(f,delimiter="\t",lineterminator="\n")
        w.writerow(["id","headword","card_before_sha256","card_after_sha256","pos_before","pos_after","changed_fields","prior_evidence","decision"])
        for id in IDS:
            card_before,card_after=before_cards[str(id)],after_cards[str(id)]
            pos_before,pos_after=before_pos.get(str(id),[]),after_pos.get(str(id),[])
            if card_before==card_after and pos_before==pos_after:
                raise ValueError(f"No reviewed change for {id}")
            prior=next((e["evidence"] for e in updates if e.get("path",[None])[0]==str(id)), "")
            w.writerow([id,card_after["w"],digest(card_before),digest(card_after),"・".join(pos_before),"・".join(pos_after),"; ".join(fields.get(str(id),[])),prior,"fixed_rechecked after exact field review and browser regression"])
    with Path("completion/v172-pair-review.tsv").open("w",encoding="utf-8",newline="") as f:
        w=csv.writer(f,delimiter="\t",lineterminator="\n")
        w.writerow(["pair_id","index","a","b","type","decision","rationale","evidence"])
        for key,index,a,b,kind,rationale in PAIRS:
            w.writerow([key,index,a,b,kind,"reviewed",rationale,f"JLPT_N1_ukrainian_reading_v171.html:VOCAB_AUDITED_PAIRS[{index}]; author pair review"])
    lines=REGISTRY.read_text(encoding="utf-8").splitlines()
    changed_cards=changed_pairs=0
    new=[]
    for line in lines:
        if not line or line.startswith("kind,"):
            new.append(line); continue
        fields_csv=line.split(",",4)
        if len(fields_csv)<4:
            raise ValueError("Malformed registry row")
        kind,id,key,status=fields_csv[:4]
        if kind=="vocab" and id in {str(x) for x in IDS}:
            if status!="pending":
                raise ValueError(f"Unexpected card status for {id}: {status}")
            evidence=f'"completion/v172-acceptance.tsv#{id}; author recheck and browser regression"'
            new.append(",".join([kind,id,key,"fixed_rechecked",evidence]))
            changed_cards+=1
        elif kind=="vocab_pair" and id in {p[0] for p in PAIRS}:
            if status!="pending":
                raise ValueError(f"Unexpected pair status for {id}: {status}")
            evidence=f'"completion/v172-pair-review.tsv#{id}; author pair review"'
            new.append(",".join([kind,id,key,"reviewed",evidence]))
            changed_pairs+=1
        else:
            new.append(line)
    if changed_cards!=13 or changed_pairs!=5:
        raise ValueError(f"Registry rows changed: cards={changed_cards}, pairs={changed_pairs}")
    REGISTRY.write_text("\n".join(new)+"\n",encoding="utf-8")
    counts={}
    for line in new[1:]:
        if line:
            status=line.split(",",4)[3]
            counts[status]=counts.get(status,0)+1
    expected={"reviewed":3874,"fixed_rechecked":14,"pending":1954}
    if counts!=expected:
        raise ValueError(f"Unexpected registry counts: {counts}")
    result={"card_acceptances":changed_cards,"pair_reviews":changed_pairs,"registry_counts":counts,"pass":True}
    Path("completion/v172-work/registry-results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))

if __name__=="__main__":
    main()
