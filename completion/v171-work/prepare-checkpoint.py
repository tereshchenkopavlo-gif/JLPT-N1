import hashlib
import json
import re
from pathlib import Path

BASE = Path("JLPT_N1_ukrainian_reading_v170.html")
OUT = Path("JLPT_N1_v171_checkpoint.html")
BASE_SHA256 = "e28958926e93343f47395910f243772e1ce2c13052cfa5fd8f4c3ede6cae7f51"
NEW_T = (
    "Неодмінно спричинити реакцію або твердо вирішити, що дія відбудеться.\n"
    "Приєднання: Vない＋ではおかない／V未然形＋ずにはおかない（する→せず）\n"
    "【用法】 Обидва основні приклади демонструють зовнішній ефект: кінцівка фільму неминуче зворушує глядачів, а холодне ставлення викликає неприязнь. Друге вживання — тверда рішучість самого діяча:\n"
    "私は、この不正を最後まで追及せずにはおかない。 — Я неодмінно доведу справу про це порушення до кінця.\n"
    "【制約】 У першому прикладі だろう позначає прогноз. ずにはいられない виражає внутрішній імпульс, коли суб'єкт не може стриматися від дії; це не взаємозамінна форма:\n"
    "彼女の話を聞いて、私は笑わずにはいられなかった。 — Почувши її розповідь, я не міг стримати сміху."
)

def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, got {count}")
    return text.replace(old, new, 1)

def extract_details(text):
    marker = "const GRAMMAR_DETAILS_BY_ID = "
    pos = text.index(marker) + len(marker)
    details, _ = json.JSONDecoder().raw_decode(text[pos:])
    return details

def main():
    original = BASE.read_bytes()
    base_hash = hashlib.sha256(original).hexdigest()
    if base_hash != BASE_SHA256:
        raise RuntimeError(f"base HTML changed: {base_hash}")
    text = original.decode("utf-8")
    original_details = extract_details(text)
    if len(original_details) != 130:
        raise RuntimeError("expected 130 grammar records")
    old_t = original_details["90"]["t"]

    text = replace_once(
        text,
        '<title>JLPT N1 — ウクライナ語対応学習アプリ · v170</title>',
        '<title>JLPT N1 — ウクライナ語対応学習アプリ · v171</title>',
        "title",
    )

    model_end = """  return {translation,usage:displayUsageText(usage,kind)};
}
function studyProseHtml(value)"""
    model_new = r"""  return {translation,usage:displayUsageText(usage,kind)};
}
function splitGrammarUsage(value) {
  const text = String(value || '');
  const match = /(^|\n)(?=【(?:用法|制約|文体)】)/u.exec(text);
  if (!match) return {before:text.trim(),after:''};
  const splitAt = match.index + (match[1] ? match[1].length : 0);
  return {before:text.slice(0,splitAt).trim(),after:text.slice(splitAt).trim()};
}
function studyProseHtml(value)"""
    text = replace_once(text, model_end, model_new, "split helper")

    study_line = "  const study = cardStudyModel(kind, data);"
    text = replace_once(
        text,
        study_line,
        study_line + "\n  const usageParts = kind === 'g' ? splitGrammarUsage(study.usage) : {before:study.usage, after:''};",
        "card usage split",
    )

    dollar = "$"
    tick = chr(96)
    old_markup = "\n".join([
        "    " + dollar + "{study.usage ? " + tick + '<div class="fc-section-label">用法・接続</div><div class="fc-trans" lang="uk">' + dollar + "{studyTextHtml(study.usage)}</div>" + tick + " : ''}",
        "    " + dollar + "{renderAutoRecommendations(kind, id, data, opts)}",
        '    <div class="fc-section-label">例文</div>',
        '    <ul class="fc-examples">' + dollar + "{examplesHtml}</ul>",
    ])
    new_markup = "\n".join([
        "    " + dollar + "{usageParts.before ? " + tick + '<div class="fc-section-label" ' + dollar + "{kind === 'g' ? 'data-grammar-layout=\"before\"' : ''}" + '>用法・接続</div><div class="fc-trans" lang="uk">' + dollar + "{studyTextHtml(usageParts.before)}</div>" + tick + " : ''}",
        "    " + dollar + "{kind === 'g' ? '' : renderAutoRecommendations(kind, id, data, opts)}",
        '    <div class="fc-section-label" ' + dollar + "{kind === 'g' ? 'data-grammar-layout=\"examples\"' : ''}" + '>例文</div>',
        '    <ul class="fc-examples">' + dollar + "{examplesHtml}</ul>",
        "    " + dollar + "{kind === 'g' && usageParts.after ? " + tick + '<div class="fc-section-label" data-grammar-layout="after">補足・制約</div><div class="fc-trans" lang="uk">' + dollar + "{studyTextHtml(usageParts.after)}</div>" + tick + " : ''}",
        "    " + dollar + "{kind === 'g' ? renderAutoRecommendations(kind, id, data, opts) : ''}",
    ])
    text = replace_once(text, old_markup, new_markup, "card layout")

    comp_start = text.index("function renderComparison() {")
    comp_end = text.index("\ndocument.getElementById('btnClearCompare')", comp_start)
    comp_new = r"""function renderComparison() {
  const list = document.getElementById('compareList'); if (!list) return;
  const items = getComparisonKeys().map(compareItemForKey).filter(Boolean);
  document.getElementById('compareGuides').innerHTML = comparisonGuidesHtml(items);
  list.setAttribute('aria-label', '比較リスト：' + items.length + '件／上限30件');
  if (!items.length) {
    list.innerHTML = '<div class="compare-empty">比較リストは空です。<br>語彙・文法のカードを開き、「＋ 比較リストに追加」を押してください。<br>30件まで追加できます。</div>';
    document.getElementById('btnClearCompare').style.display = 'none'; return;
  }
  document.getElementById('btnClearCompare').style.display = '';
  list.innerHTML = items.map((it, i) => {
    const study = cardStudyModel(it.kind,it);
    const usageParts = it.kind === 'g' ? splitGrammarUsage(study.usage) : {before:study.usage,after:''};
    const usageBefore = usageParts.before
      ? '<div class="compare-ua"><div class="study-subheading" ' + (it.kind === 'g' ? 'data-grammar-layout="before"' : '') + '>用法・接続</div>' + studyTextHtml(usageParts.before) + '</div>'
      : '';
    const usageAfter = it.kind === 'g' && usageParts.after
      ? '<div class="compare-ua"><div class="study-subheading" data-grammar-layout="after">補足・制約</div>' + studyTextHtml(usageParts.after) + '</div>'
      : '';
    const synonyms = it.synonyms.length ? '<div class="compare-jp"><b>類似・関連表現：</b> ' + it.synonyms.join('、') + '</div>' : '';
    const examples = it.examples.length
      ? '<div class="compare-jp ' + (it.kind === 'g' ? 'grammar-examples' : '') + '"><b>例文：</b><ol>' + (it.kind === 'g' ? grammarExamplesHtml(it.id, it.examples) : vocabExamplesHtml(it.id, it.examples)) + '</ol></div>'
      : '';
    return '<article class="compare-entry">' +
      '<div class="compare-type">' + (it.kind === 'g' ? '文法' : '語彙') + ' · ' + (i + 1) + '</div>' +
      '<h3>' + escapeLex(it.label) + ' ' + wordPosHtml(it) + '</h3>' +
      (it.reading ? '<div class="compare-jp">' + it.reading + '</div>' : '') +
      '<div class="compare-ua">' + (studyTextHtml(study.translation) || 'ウクライナ語訳は未登録です') + '</div>' +
      (it.meaning ? '<div class="compare-jp"><b>日本語の説明：</b> ' + it.meaning + '</div>' : '') +
      usageBefore +
      (it.kind === 'g' ? '' : synonyms) +
      examples +
      usageAfter +
      (it.kind === 'g' ? synonyms : '') +
      '<button class="remove-compare" data-remove-key="' + it.key + '">リストから削除</button>' +
      '</article>';
  }).join('');
  list.querySelectorAll('[data-remove-key]').forEach(btn => btn.addEventListener('click', () => {
    if (saveComparisonKeys(getComparisonKeys().filter(k => k !== btn.dataset.removeKey))) renderComparison();
  }));
}"""
    text = text[:comp_start] + comp_new + text[comp_end:]

    marker = "const GRAMMAR_DETAILS_BY_ID = "
    details_pos = text.index(marker) + len(marker)
    details, _ = json.JSONDecoder().raw_decode(text[details_pos:])
    details["90"]["t"] = NEW_T
    field_start = text.index('"90":{', details_pos)
    t_marker = text.index('"t":', field_start) + len('"t":')
    old_value, old_end = json.JSONDecoder().raw_decode(text[t_marker:])
    if old_value != old_t:
        raise RuntimeError("unexpected previous g90 translation")
    new_value = json.dumps(NEW_T, ensure_ascii=False, separators=(",", ":"))
    text = text[:t_marker] + new_value + text[t_marker + old_end:]

    updated_details = extract_details(text)
    if updated_details != details or len(updated_details) != 130:
        raise RuntimeError("grammar data mismatch after patch")
    for item_id, item in updated_details.items():
        value = item.get("t", "")
        match = re.search(r"(?m)^(?=【(?:用法|制約|文体)】)", value)
        if not match:
            raise RuntimeError(f"no after-example analysis block for grammar {item_id}")
        before = value[:match.start()].strip()
        after = value[match.start():].strip()
        if "Приєднання:" not in before and "Форма:" not in before:
            raise RuntimeError(f"no connection block for grammar {item_id}")
        if not after.startswith("【"):
            raise RuntimeError(f"bad analysis split for grammar {item_id}")

    if text.count("v170") != 0 or text.count("v171") != 1:
        raise RuntimeError("version title mismatch")
    for marker in ['data-grammar-layout="before"', 'data-grammar-layout="examples"', 'data-grammar-layout="after"']:
        if marker not in text:
            raise RuntimeError("missing layout marker " + marker)

    OUT.write_text(text, encoding="utf-8")
    out_bytes = OUT.read_bytes()
    result = {
        "base_sha256": base_hash,
        "checkpoint_sha256": hashlib.sha256(out_bytes).hexdigest(),
        "checkpoint_bytes": len(out_bytes),
        "grammar_records": len(updated_details),
        "split_before_after": 130,
        "g90_examples": [
            "私は、この不正を最後まで追及せずにはおかない。",
            "彼女の話を聞いて、私は笑わずにはいられなかった。",
        ],
        "pass": True,
    }
    Path("completion/v171-work/prepare-results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
