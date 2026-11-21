"""Reconcile six received reviews and stage explicit, reviewable language changes."""
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT / "completion/independent"
OUT = DIR / "adjudications/20261121"
OUT.mkdir(parents=True, exist_ok=True)
DATE = "2026-11-21"
MAIN = "ba5b1717e5bffeb1e02bf662e04817a8407ff023"
BASE_PATH = "JLPT_N1_ukrainian_reading_v229_C12g.html"

def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True).encode()).hexdigest()

def save(path, data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")

queue = json.loads((DIR/"queue.json").read_text())
packages, reports, original, owner = {}, {}, {}, {}
TARGETS = {"IR-20261120-02", *[f"IR-20261121-{n:02d}" for n in range(3,8)]}
for row in [r for r in queue["packages"] if r["package_id"] in TARGETS]:
    id = row["package_id"]
    packet = json.loads((DIR/row["path"]).read_text())
    report_path = DIR/"reviews"/(id+"-ChatGPT-20261121.json")
    report = json.loads(report_path.read_text())
    assert report["package_id"] == id
    assert report["sources_sha256"] == packet["sources_sha256"] == digest(packet["cases"])
    assert hashlib.sha256((DIR/row["path"]).read_bytes()).hexdigest() == row["package_sha256"]
    assert {c["case_id"] for c in report["cases"]} == {c["case_id"] for c in packet["cases"]}
    packages[id], reports[id] = packet, report
    for c in packet["cases"]:
        assert c["case_id"] not in original
        original[c["case_id"]] = copy.deepcopy(c["fields"])
        owner[c["case_id"]] = id
revised = copy.deepcopy(original)
decisions = []

def decide(case_id, finding_index, decision, reason, changed_paths):
    id = owner[case_id]
    case = next(c for c in reports[id]["cases"] if c["case_id"] == case_id)
    finding = case["findings"][finding_index]
    decisions.append({"finding_id":id+"/"+case_id+"/"+str(finding_index+1),
                      "package_id":id,"case_id":case_id,"finding_index":finding_index,
                      "reviewer_finding":finding,"decision":decision,"rationale":reason,
                      "changed_paths":changed_paths,"review_path":"reviews/"+id+"-ChatGPT-20261121.json"})

def meaning(id, index, wrong, note):
    entry = revised[id]["meaning_quiz"]["byExample"]
    sentence = list(entry)[index]
    entry[sentence]["wrong"] = wrong
    entry[sentence]["note"] = note

def choices(id, index, replacements, explanation):
    q = revised[id]["questions"][index]
    answer = q["answer"]
    assert answer not in replacements
    for n, value in replacements.items():
        q["choices"][n] = value
    q["explain"] = explanation
    assert len(set(q["choices"])) == 4

meaning("v_3375",0,[
    "長く追求すべき理想として、継続的に掲げる課題であること。",
    "他の課題を進めるための、前提となる条件であること。",
    "生じた問題への対処よりも、原因の究明を優先すること。"],
    "当面 описує завдання теперішнього етапу. Саме слово не визначає довготривалої ідеальної мети, передумови інших робіт чи переваги пошуку причин над дією.")
decide("v_3375",0,"accepted","The original contrasts are heavily signposted by distant time references; replace with competing task roles while retaining the immediate-task key.",["meaning_quiz.byExample[0].wrong","meaning_quiz.byExample[0].note"])
meaning("v_3652",1,[
    "従来の研究を精密に検証し、結果の確かさを高めているさま。",
    "複数分野の知見を網羅し、研究の全体像を示しているさま。",
    "研究の成果が高く評価され、学界で広く認められているさま。"],
    "ユニーク вказує на самобутність дослідження. Точність перевірки, широта огляду й визнання результатів самі по собі не означають оригінальності.")
decide("v_3652",0,"accepted","Verification precision, breadth and recognition are plausible research evaluations but do not define distinctiveness.",["meaning_quiz.byExample[1].wrong","meaning_quiz.byExample[1].note"])
revised["v_3417"]["details"]["t"] = "мішкуватий, завеликий, надміру просторий"
revised["v_3417"]["details"]["exampleTranslations"][0] = "Костюм, що дістався від старшого брата, був завеликим, і лінія плечей на ньому була спущена."
decide("v_3417",0,"accepted","The card definition and usage require excess looseness; qualifying просторiй aligns the Ukrainian gloss with both.",["details.t"])
decide("v_3417",1,"accepted","Clarify that 肩 refers to the suit's shoulder fit and include the older-brother information.",["details.exampleTranslations[0]"])
meaning("v_3444",1,[
    "関係者の役割が細かく分かれ、連絡の手順が複雑なさま。",
    "意見の違いが表に出て、激しく議論を交わしているさま。",
    "互いに距離を置き、必要な仕事の話に限って接するさま。"],
    "どろどろした関係 описує переплетення важких почуттів і прихованих суперечностей. Організаційна складність, відкрита дискусія та стримана дистанція передають інші властивості стосунків.")
decide("v_3444",0,"accepted","Replace positive opposites with administrative complexity, overt disagreement and emotional distance; none defines entangled negative emotions.",["meaning_quiz.byExample[1].wrong","meaning_quiz.byExample[1].note"])
decide("v_3525",0,"rejected","The は topic and が subject are coherent: this device has a mechanism in which temperature adjustment is automatic. The shorter alternative is possible, but no grammatical, semantic or referential error was demonstrated. Preserve the exact example, translation and byExample binding.",[])
meaning("v_3565",0,[
    "依頼を受けてから提供するまでの時間が短いさま。",
    "決められた間隔を守って、継続的に提供されるさま。",
    "内容の新しさを重視して、最新情報をそろえているさま。"],
    "タイムリー — доречний саме тоді, коли інформація потрібна. Це не лише швидка відповідь, регулярність або новизна змісту.")
meaning("v_3565",1,[
    "発表から反響が出るまでの時間が短いさま。",
    "内容を定期的に更新し、新しい情報を載せているさま。",
    "季節ごとの予定に沿って、一定の時期に掲載されるさま。"],
    "Тут タイムリー — відповідний поточній ситуації та інтересу саме в цей момент. Швидкість реакції, оновлення змісту й календарна регулярність не визначають цієї доречності.")
decide("v_3565",0,"accepted","Distinguish situational timeliness from response speed, freshness and scheduled periodicity. Retain both correct keys and do not label the earlier keys linguistically wrong.",["meaning_quiz.byExample[0].wrong","meaning_quiz.byExample[0].note","meaning_quiz.byExample[1].wrong","meaning_quiz.byExample[1].note"])

id = "m-c12-20261120-03"
revised[id]["ja"] = revised[id]["ja"].replace("装置の異常を知らせる表示灯がある。","装置の異常を光と音で知らせる警告装置がある。",1)
revised[id]["uk"] = revised[id]["uk"].replace("є індикатор несправності обладнання.","є пристрій, що попереджає про несправність обладнання світлом і звуком.",1).replace("через зламаний датчик він почав часто спрацьовувати помилково.","через зламаний датчик попередження почали часто спрацьовувати помилково.",1)
decide(id,0,"accepted","Introduce both signal modalities before the later sound-silencing action; synchronize the first Ukrainian sentences.",["ja","uk"])
choices(id,1,{
    0:"漏れた場合の対処を説明するため、危険性の評価をいったん保留すること。",
    1:"漏れる確率の高さを測り、その数値を報告すること。",
    3:"漏れることを避けにくい通常の事態として、作業の予定に組み込むこと。"},
    "ようものなら подає можливий витік із тривогою щодо тяжких наслідків. Це не нейтральний план дій, кількісна оцінка ймовірності чи звичайна запланована подія.")
decide(id,1,"accepted","Alternatives now distinguish risk stance, measured likelihood and neutral planning instead of present/past negations.",["questions[1].choices","questions[1].explain"])
id = "m-c12-20261120-04"
choices(id,0,{
    0:"保存されたコピーの扱いを閲覧者に任せ、資料館は原本の保存に専念すべきだと伝えること。",
    2:"歴史的な価値を確かめた後なら、個人情報の範囲は公開後に調整できると伝えること。",
    3:"画像の匿名化を先に済ませれば、説明文の確認は展示開始後に進められると伝えること。"},
    "Йдеться про перевірку змісту та меж публікації до відкриття виставки. Директор не передає відповідальність відвідувачам і не пропонує відкладати перевірку персональних даних чи пояснення.")
decide(id,0,"accepted","Replace absolute bans with competing allocations of responsibility and timing of the two checks.",["questions[0].choices","questions[0].explain"])
id = "l-c12-20261120-01"
revised[id]["uk"] = revised[id]["uk"].replace("Несправності, пов’язані з безпекою, передаватимуть професіоналам.","За несправностей, пов’язаних із безпекою, скеровуватимуть до спеціалізованих майстерень.")
decide(id,0,"accepted","専門の店 identifies a specialist service location; the more specific Ukrainian wording preserves this referral.",["uk"])
id = "l-c12-20261121-02"
decide(id,0,"rejected","The text explicitly uses a metaphor for repeated movement between observation and discussion. The process and Ukrainian translation agree. Replacing it by trips between a meeting room and the site would add a physical movement not stated in the source; retain the coherent metaphor and record stylistic uncertainty rather than declaring a grammar error.",[])
choices(id,0,{
    1:"完成予想図の明るさを実際の景色と比べ、外観の評価を先に固める必要があったから。",
    2:"説明会で集まった要望を全て案に加え、必要な設備の数を決めるため。",
    3:"搬入と休憩のうち、どちらを広場の唯一の用途にするか住民の投票で決めるため。"},
    "Місце оглядали в різні години, щоб зіставити план із різними способами користування. Це не лише оцінка вигляду, не автоматичне додавання всіх вимог і не голосування за один-єдиний вид використання.")
decide(id,1,"accepted","Keep the temporal and functional conditions in the key, while alternatives target appearance, aggregation and choosing one use.",["questions[0].choices","questions[0].explain"])
id = "m-c12-20261121-05"
choices(id,1,{
    0:"よく質問が出る作業について、担当者自身が索引の説明を加えながら新人に実演した。",
    1:"質問の多い三つの作業について、新人に口頭で方法を聞き、索引との一致を調べた。",
    2:"よく質問が出る作業ではなく、索引で探しやすい三つの作業を選んで新人に試してもらった。"},
    "ないまでも визнає обмежений обсяг перевірки. Новачкам дали лише посібник для трьох робіт, які часто викликають запитання. Усна демонстрація, опитування замість практичного використання та відбір за простотою пошуку змінюють описаний метод.")
decide(id,0,"accepted","All alternatives describe bounded tests; they differ in who supplies help, the test method and selection criterion.",["questions[1].choices","questions[1].explain"])
id = "m-c12-20261121-06"
choices(id,0,{
    1:"当時の情報を個人別に整理し、担当者の判断力を次回の配置に反映できるようにすること。",
    2:"問題への対応を定型化し、次回は状況の違いを検討せず同じ手順を選べるようにすること。",
    3:"問題の経緯より結論を短く残し、申し送りの時間を減らせるようにすること。"},
    "Записи зберігають доступну тоді інформацію й обставини рішення для наступної команди. Їх відділяють від особистого оцінювання; механічне повторення рішення та скорочення історії до короткого висновку не є вказаною метою.")
decide(id,0,"accepted","Use realistic competing record purposes: staff placement, rigid procedure and concise handover; the key retains learning from decision context.",["questions[0].choices","questions[0].explain"])
id = "l-c12-20261121-07"
old = "結局出さずじまいになった手紙もある"
new = "結局、返事を書かずじまいになった手紙もある"
revised[id]["ja"] = revised[id]["ja"].replace(old,new,1)
revised[id]["contextNotes"][0]["quote"] = new
revised[id]["contextNotes"][0]["meaning"] = "на деякі листи так і не написав відповіді, попри намір це зробити"
revised[id]["uk"] = revised[id]["uk"].replace("на деякі листи так і не відповів.","на деякі листи так і не написав відповіді.",1)
decide(id,0,"partially_accepted","出さずじまい does not presuppose that a reply was already written, so the categorical error claim is rejected. Accept editorial clarification: naming 返事を書く aligns the postponement and the later Ukrainian mention of unwritten replies. Retain the reviewer's severity separately; classify this as clarification.",["ja","contextNotes[0].quote","contextNotes[0].meaning"])
decide(id,1,"accepted","Synchronize the Ukrainian sentence with the explicit writing action; the final paragraph already mentions unwritten replies.",["uk"])
id = "l-c12-20261121-08"
revised[id]["ja"] = revised[id]["ja"].replace("聞くともなく聞いていた波に","聞くともなく聞いていた波の音に",1)
revised[id]["contextNotes"][0]["quote"] = "聞くともなく聞いていた波の音"
revised[id]["contextNotes"][0]["meaning"] = "шум хвиль, який раніше слухав мимохідь, не зосереджуючись на ньому"
decide(id,0,"accepted","Clarify the sound as the object of hearing for a teaching example; retain the already accurate Ukrainian translation. The earlier metonymy is not classified as ungrammatical.",["ja","contextNotes[0].quote","contextNotes[0].meaning"])
id = "m-c12-20261121-09"
choices(id,0,{
    1:"地図の公園や川の名前を覚えるより、道順を一つに決めて歩く方が町に慣れやすいこと。",
    2:"同じ道でも一人で歩くより同僚と歩く方が、景色そのものを美しく感じられること。",
    3:"帰宅する道を長くすれば、買い物などの用事も毎回その途中で済ませられること。"},
    "Оповідач побачив зв’язок уже відомих місць із повсякденними маршрутами. Фіксація одного шляху, краса краєвиду завдяки компанії та гарантована зручність кожного довшого маршруту не передають цього відкриття.")
decide(id,0,"accepted","Keep plausible route and perception claims instead of relocation and learning every road at once.",["questions[0].choices","questions[0].explain"])
id = "m-c12-20261121-10"
revised[id]["uk"] = revised[id]["uk"].replace("ледь не запізнилися на їжу","ледь не запізнилися до початку трапези",1)
decide(id,0,"accepted","Use idiomatic Ukrainian for a scheduled meal without inventing breakfast, lunch or dinner.",["uk"])
id = "m-c12-20261121-12"
choices(id,1,{
    0:"世話の効果を早く確かめるため、状態が変わらなくても別の対処を重ねる練習。",
    1:"植物の状態を記録すれば、専門知識を増やさずに原因を絞り込めると確信する経験。",
    2:"観察するより世話の手順を一定に保つ方が、変化の理由を捉えやすいと知る経験。"},
    "Оповідач вчиться поєднувати турботу зі спостереженням і очікуванням. Нові втручання до появи ефекту, впевненість у самодостатності записів та перевага незмінної процедури над спостереженням не є його висновком.")
decide(id,0,"accepted","Use nearby but mistaken conclusions about successive interventions, confidence from records and fixed routines.",["questions[1].choices","questions[1].explain"])

assert len(decisions) == 21
for id, fields in revised.items():
    if id.startswith("v_"):
        for q in fields["meaning_quiz"]["byExample"].values():
            assert len(set([q["correct"],*q["wrong"]])) == 4
            lengths = [len(s) for s in [q["correct"],*q["wrong"]]]
            assert max(lengths)/min(lengths) <= 1.5, (id,lengths)
    else:
        for q in fields["questions"]:
            assert len(set(q["choices"])) == 4 and 0 <= q["answer"] < 4
            assert q["evidence"] in fields["ja"]
        for note in fields["contextNotes"]:
            assert note["quote"] in fields["ja"], (id,note["quote"])
        assert [q["answer"] for q in fields["questions"]] == [q["answer"] for q in original[id]["questions"]]
        for a,b in zip(fields["questions"],original[id]["questions"]):
            assert a["choices"][a["answer"]] == b["choices"][b["answer"]]
changed = [{"case_id":id,"package_id":owner[id],"before":original[id],"after":fields}
           for id,fields in revised.items() if fields != original[id]]
save(OUT/"decisions.json",decisions)
save(OUT/"patches.json",changed)
save(OUT/"reviewed-materials.json",revised)
summary = {"packages":6,"cases":len(original),"findings":21,
           "accepted":sum(d["decision"]=="accepted" for d in decisions),
           "partially_accepted":sum(d["decision"]=="partially_accepted" for d in decisions),
           "rejected":sum(d["decision"]=="rejected" for d in decisions),
           "changed_cases":len(changed),"reading_keys_preserved":True,
           "independent_recheck_for_changed_fields":"pending","main_base_sha":MAIN}
save(OUT/"summary.json",summary)
print(json.dumps(summary))

# Integrate only card text fields and reading content into the current release.
# Meaning/POS changes for the high-risk C11 branches remain separate payloads.
base = subprocess.check_output(["git","show",MAIN+":"+BASE_PATH]).decode()
def block(text, name):
    start = re.search(r"const\s+"+name+r"\s*=\s*",text).end()
    value, end = json.JSONDecoder().raw_decode(text,start)
    return value,start,end
bank,bs,be = block(base,"readingBank")
details,ds,de = block(base,"VOCAB_DETAILS_BY_ID")
assert len(bank["medium"])==109 and len(bank["long"])==65
drift, bank_changes = [], []
for level in bank:
    for i,row in enumerate(bank[level]):
        id = row.get("id")
        if id not in revised or id.startswith("v_"):
            continue
        mismatches = [k for k in original[id] if row.get(k)!=original[id][k]]
        if mismatches:
            assert id in ["m-c12-20261119-01","m-c12-20261119-02"] and mismatches==["questions"], (id,mismatches)
        drift.append({"case_id":id,"source_main_differences":mismatches,
                      "explanation":"IR01 corrections already passed IR02; integrate verified reviewed text" if mismatches else "reviewed source matches current main"})
        if row != revised[id]:
            bank_changes.append(id)
            bank[level][i] = copy.deepcopy(revised[id])
old_details = copy.deepcopy(details)
for id in ["3375","3417"]:
    key = "v_"+id
    assert details[id]["examples"] == revised[key]["details"]["examples"]
    for field in ["t","exampleTranslations"]:
        details[id][field] = copy.deepcopy(revised[key]["details"][field])
candidate = base
for start,end,value in sorted([(bs,be,bank),(ds,de,details)],reverse=True):
    candidate = candidate[:start]+json.dumps(value,ensure_ascii=False,separators=(",",":"))+candidate[end:]
for name in ["DEFAULT_VOCAB","GRAMMAR_DETAILS_BY_ID","VOCAB_POS_BY_ID",
             "REVIEWED_MEANING_QUIZZES","REVIEWED_READING_OPTIONS","VOCAB_AUDITED_PAIRS"]:
    assert block(candidate,name)[0] == block(base,name)[0], name
(OUT/"candidate_UNACCEPTED.html").write_text(candidate)
reverse = candidate
for name in ["readingBank","VOCAB_DETAILS_BY_ID"]:
    _,start,end = block(reverse,name)
    _,base_start,base_end = block(base,name)
    reverse = reverse[:start]+base[base_start:base_end]+reverse[end:]
assert reverse == base, "Exact rollback outside edited blocks failed"
for i,script in enumerate(re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",candidate,re.S)):
    import tempfile
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder)/f"script-{i}.js"
        path.write_text(script)
        subprocess.run(["node","--check",str(path)],check=True)
save(OUT/"c11-meaning-overlays.json",{id:fields["meaning_quiz"] for id,fields in revised.items()
     if id.startswith("v_") and fields["meaning_quiz"] != original[id]["meaning_quiz"]})
save(OUT/"source-drift.json",drift)
save(OUT/"candidate-validation.json",{
    "base_commit":MAIN,"base_path":BASE_PATH,
    "base_sha256":hashlib.sha256(base.encode()).hexdigest(),
    "candidate_sha256":hashlib.sha256(candidate.encode()).hexdigest(),
    "vocabulary":3914,"grammar":130,"medium":len(bank["medium"]),"long":len(bank["long"]),
    "reading_changes":bank_changes,"card_text_ids":[3375,3417],
    "protected_blocks_equal":True,"c11_overlays_not_applied":True,
    "exact_rollback":True,"javascript_syntax":True,
    "browser_acceptance":"pending","independent_recheck":"pending"})

# Append the received review once; hash checks retain the original files.
for row in [r for r in queue["packages"] if r["package_id"] in TARGETS]:
    id = row["package_id"]
    path = "reviews/"+id+"-ChatGPT-20261121.json"
    ref = {"path":path,"sha256":hashlib.sha256((DIR/path).read_bytes()).hexdigest()}
    if not any(x["path"]==path for x in row["reviews"]):
        row["reviews"].append(ref)
    else:
        assert ref in row["reviews"]
    own = [d for d in decisions if d["package_id"]==id]
    for status in ["reviewed_with_issues","corrections_pending"]:
        if not any(h["status"]==status for h in row["history"]):
            row["history"].append({"status":status,"date":DATE,
                                   "evidence":"adjudications/20261121/decisions.json"})
    row["status"]="corrections_pending"
    row["notes"]=f"Received review validated; {len(own)} findings adjudicated. Revised fields require recheck; see adjudications/20261121/decisions.json."
save(DIR/"queue.json",queue)
register = json.loads((DIR/"acceptance-register.json").read_text())
def leaf_paths(value,prefix):
    if isinstance(value,dict):
        return [p for k,v in value.items() for p in leaf_paths(v,prefix+"."+k)]
    if isinstance(value,list):
        return [p for i,v in enumerate(value) for p in leaf_paths(v,prefix+f"[{i}]")]
    return [prefix]
def get_simple(fields,path):
    value = fields
    for token in re.findall(r"[^.\[\]]+",path):
        value = value[int(token)] if isinstance(value,list) else value[token]
    return value
for id,report in reports.items():
    for case in report["cases"]:
        cid = case["case_id"]
        for field in case["checked_fields"]:
            old = get_simple(original[cid],field)
            new = get_simple(revised[cid],field)
            entry = {"package_id":id,"case_id":cid,"reviewed_field":field,
                     "source_sha256":packages[id]["sources_sha256"],
                     "reviewed_value_sha256":digest(old),"reviewer_verdict":case["verdict"],
                     "status":"independent_reviewed_original" if old==new else "revised_pending_independent_review",
                     "exclusions":case["unchecked_fields"],
                     "evidence":"completion/independent/reviews/"+id+"-ChatGPT-20261121.json",
                     "adjudication":"adjudications/20261121/decisions.json",
                     "scope_note":"Only the reported source field is credited. Changed values have no recheck credit."}
            if old!=new:
                entry["recheck_required"]=True
            key = (id,cid,field,entry["evidence"])
            if not any((x.get("package_id"),x.get("case_id"),x.get("reviewed_field"),x.get("evidence"))==key for x in register):
                register.append(entry)
        for field in case["unchecked_fields"]:
            entry = {"package_id":id,"case_id":cid,"reviewed_field":field,
                     "status":"not_reviewed",
                     "evidence":"completion/independent/reviews/"+id+"-ChatGPT-20261121.json"}
            key=(id,cid,field,entry["evidence"])
            if not any((x.get("package_id"),x.get("case_id"),x.get("reviewed_field"),x.get("evidence"))==key for x in register):
                register.append(entry)
save(DIR/"acceptance-register.json",register)
lines=["# Черга незалежного мовного аудиту JLPT N1","",
       "Шість рецензій IR02–IR07 отримано, звірено та розглянуто. Виправлені матеріали готуються до повторного перегляду. Повного незалежного приймання змінених полів ще немає.","",
       "| Пакет | Статус | Рецензії |","|---|---|---|"]
for row in queue["packages"]:
    links=" · ".join(f"[ChatGPT]({r['path']})" for r in row["reviews"]) or "Очікується"
    lines.append(f"| [{row['package_id']}]({row['path']}) | {row['status']} | {links} |")
lines+=["","Контрольні суми пакетів, SHA джерел, checksums рецензій і історія — [queue.json](queue.json).",
        "","[Розгляд 21 зауваження](adjudications/20261121/decisions.json) · [Реєстр полів](acceptance-register.json) · [Правила](README.md)",
        "","Основний аудит і C12 продовжуються під час очікування незалежних висновків."]
(DIR/"QUEUE.md").write_text("\n".join(lines)+"\n")
