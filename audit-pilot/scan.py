"""Read-only vocabulary inventory and field/dependency fingerprints for the pilot."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import time
import unicodedata

ROOT = Path(__file__).resolve().parent.parent
POS = set('イ形 ナ形 代名詞 副助詞 副詞 動詞 名詞 四字熟語 定型表現 慣用句 接尾語 接続詞 接頭語 連体詞 連語'.split())
KANA = re.compile(r'[ぁ-ゖァ-ヺー・ 　]+\Z')

def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()

def constant(html, name):
    match = re.search(r'\bconst '+re.escape(name)+r'\s*=\s*', html)
    if not match:
        raise ValueError(f'Missing {name}')
    return json.JSONDecoder().raw_decode(html, match.end())[0]

def normalize(value):
    return unicodedata.normalize('NFKC', value).strip().replace('～', '〜')

def strings(value):
    return isinstance(value, list) and all(isinstance(x, str) and x.strip() for x in value)

def scan(path):
    raw = path.read_bytes()
    html = raw.decode()
    names = ('DEFAULT_VOCAB VOCAB_DETAILS_BY_ID VOCAB_POS_BY_ID VOCAB_HEADWORD_ALIASES '
             'VOCAB_AUDITED_PAIRS AUTO_ANTONYM_PAIRS REVIEWED_EXAMPLE_TARGETS '
             'VOCAB_KANA_EXAMPLE_TARGETS REVIEWED_READING_OPTIONS REVIEWED_MEANING_QUIZZES readingBank')
    data = {name: constant(html, name) for name in names.split()}
    words = data['DEFAULT_VOCAB']
    details = data['VOCAB_DETAILS_BY_ID']
    parts = data['VOCAB_POS_BY_ID']
    ids = Counter(str(x['id']) for x in words)
    index = defaultdict(set)
    readings = defaultdict(set)
    example_owners = defaultdict(set)
    duplicate_candidates = defaultdict(set)
    errors = defaultdict(set)
    signals = defaultdict(set)
    dependencies = defaultdict(dict)
    graph = defaultdict(set)
    external = defaultdict(list)
    ambiguous = defaultdict(dict)
    link_errors = []
    by_id = {str(x['id']): x for x in words}

    def connect(a, b):
        if a != b:
            graph[a].add(b)
            graph[b].add(a)

    for key, entry in by_id.items():
        index[normalize(entry['w'])].add(key)
        readings[normalize(entry['r'])].add(key)
        card = details.get(key, {})
        duplicate_candidates[digest([normalize(entry['w']), normalize(entry['r']), card.get('m'), card.get('t')])].add(key)
        examples = card.get('examples', [])
        if strings(examples):
            for sentence in examples:
                example_owners[normalize(sentence)].add(key)

    for alias_key, alias in enumerate(data['VOCAB_HEADWORD_ALIASES']):
        key = str(alias['id'])
        entry = by_id.get(key)
        if not entry or (entry['w'], entry['r']) != (alias['word'], alias['reading']):
            link_errors.append(['alias_target', alias_key, key])
            if entry:
                errors[key].add('alias_target')
            continue
        index[normalize(alias['oldWord'])].add(key)
        dependencies[key][f'alias:{alias_key}'] = alias
        signals[key].add('legacy_alias')

    seen_pairs = set()
    for i, pair in enumerate(data['VOCAB_AUDITED_PAIRS']):
        a, b = str(pair['a']), str(pair['b'])
        identity = (tuple(sorted((a,b))), pair['type'])
        invalid = (a not in by_id or b not in by_id or a == b
                   or pair['type'] not in {'near','related','confusable'}
                   or not str(pair.get('note','')).strip())
        if invalid or identity in seen_pairs:
            code = 'invalid_pair' if invalid else 'duplicate_pair'
            link_errors.append([code, i, a, b])
            for key in {a,b} & ids.keys():
                errors[key].add(code)
            continue
        seen_pairs.add(identity)
        connect(a, b)
        for key in (a,b):
            other = b if key == a else a
            dependencies[key][f'pair:{i}'] = [
                pair, by_id[other]['w'], by_id[other]['r'], parts.get(other),
                {field:details.get(other,{}).get(field) for field in ('m','t','usage')},
            ]
            if pair['type'] in {'near','confusable'}:
                signals[key].add('contrast_or_close_pair')

    for i, pair in enumerate(data['AUTO_ANTONYM_PAIRS']):
        endpoints = [index.get(normalize(x),set()) for x in pair]
        if any(len(group) != 1 for group in endpoints):
            link_errors.append(['antonym_resolution', i, [sorted(x) for x in endpoints]])
        for key in set().union(*endpoints):
            dependencies[key][f'antonym:{i}'] = pair

    for key, quiz in data['REVIEWED_READING_OPTIONS'].items():
        entry = by_id.get(key)
        if not entry or (entry['w'], entry['r']) != (quiz['word'], quiz['correct']):
            link_errors.append(['reading_override_mismatch', key])
            if entry:
                errors[key].add('reading_override_mismatch')
        if entry:
            dependencies[key]['reading_override'] = quiz

    for label, quiz in data['REVIEWED_MEANING_QUIZZES'].items():
        if not label.startswith('v_'):
            continue
        key = label[2:]
        if key not in by_id:
            link_errors.append(['meaning_override_orphan', label])
            continue
        dependencies[key]['meaning_override'] = quiz
        for sentence in quiz.get('byExample', {}):
            if sentence not in details.get(key, {}).get('examples', []):
                # Some routes intentionally cover non-card contexts.
                signals[key].add('meaning_override_external_context')

    for i, target in enumerate(data['REVIEWED_EXAMPLE_TARGETS']):
        if target['kind'] != 'v':
            continue
        key = str(target['id'])
        if key not in by_id:
            link_errors.append(['exact_target_orphan', i, key])
            continue
        dependencies[key][f'exact_target:{i}'] = target
        if key not in index.get(normalize(target['word']), set()):
            errors[key].add('exact_target_label')
        sentence = target['sentence']
        if not all(form in sentence for form in target['forms']):
            errors[key].add('exact_target_form_absent')
        if sentence not in details.get(key, {}).get('examples', []):
            signals[key].add('exact_target_external_context')

    for label, contexts in data['VOCAB_KANA_EXAMPLE_TARGETS'].items():
        owners = index.get(normalize(label), set())
        if not owners:
            link_errors.append(['kana_target_headword_unresolved', label])
        for key in owners:
            dependencies[key]['kana_target:'+label] = contexts
            for sentence, form in contexts.items():
                if form not in sentence:
                    errors[key].add('kana_target_form_absent')

    for bank, texts in data['readingBank'].items():
        for text_index, passage in enumerate(texts):
            for note_index, note in enumerate(passage.get('contextNotes', [])):
                if note.get('kind') != 'v':
                    continue
                key = str(note.get('id'))
                route = f'reading_note:{bank}:{text_index}:{note_index}'
                if key not in by_id:
                    link_errors.append(['reading_note_orphan', route, key])
                    continue
                dependencies[key][route] = [note, passage.get('ja')]
                if key not in index.get(normalize(note.get('label', '')), set()):
                    signals[key].add('reading_note_label_check')
                if not note.get('quote') or note['quote'] not in passage.get('ja',''):
                    signals[key].add('reading_note_quote_check')
    for group in duplicate_candidates.values():
        if len(group) > 1:
            for key in group:
                signals[key].add('duplicate_candidate')

    for key, entry in by_id.items():
        card = details.get(key, {})
        pos = parts.get(key)
        if ids[key] != 1:
            errors[key].add('duplicate_id')
        if card.get('w') != entry['w']:
            errors[key].add('headword_mismatch')
        if not strings(pos) or not set(pos) <= POS or len(set(pos)) != len(pos):
            errors[key].add('invalid_pos')
            pos = []
        if not KANA.fullmatch(normalize(entry['r'])):
            signals[key].add('reading_format')
        if entry['s'] == 'する' and '名詞' not in pos:
            signals[key].add('suru_pos_check')
        if entry['s'] == 'な' and 'ナ形' not in pos:
            signals[key].add('na_pos_check')
        if len(pos) > 1:
            signals[key].add('multiple_pos')
        if len(index[normalize(entry['w'])]) > 1:
            signals[key].add('shared_headword')
        if len(readings[normalize(entry['r'])]) > 1:
            signals[key].add('shared_reading')
        for field in ('m','t','usage'):
            if not isinstance(card.get(field),str) or not card[field].strip():
                errors[key].add('missing_'+field)
        meaning, usage = card.get('t',''), card.get('usage','')
        if re.search(r'[;；]', meaning) or re.search(r'переносн|інше значення|друге значення|два значення', meaning+' '+usage, re.I):
            signals[key].add('sense_or_usage_split')
        if re.search(r'книжн|розмовн|зневажл|архаїч|шанобл|іроніч|груб|формальніш|офіційн', usage, re.I):
            signals[key].add('register')
        if re.search(r'контекст|читання.*(?:／| або | і )', usage, re.I):
            signals[key].add('context_or_reading')
        if pos and ('名詞' in pos and '動詞' not in pos and re.match(r'^[а-яіїєґ-]+ти(?:ся)?(?:[ ;,]|$)', meaning, re.I)):
            signals[key].add('noun_gloss_possible_verb')
        if re.match(r'^Іменник\b', usage) and '名詞' not in pos:
            signals[key].add('usage_pos_conflict')
        examples, translations = card.get('examples'), card.get('exampleTranslations')
        if not strings(examples) or not examples or not strings(translations) or len(examples) != len(translations):
            errors[key].add('example_translation_alignment')
        elif any(len(example_owners[normalize(x)]) > 1 for x in examples):
            signals[key].add('shared_example')
        labels = card.get('s')
        if not strings(labels):
            errors[key].add('invalid_related_labels')
            continue
        for label in labels:
            owners = index.get(normalize(label),set())
            if not owners:
                external[key].append(label)
            elif len(owners) > 1:
                ambiguous[key][label] = sorted(owners, key=int)
                signals[key].add('ambiguous_related_label')
            elif key in owners:
                signals[key].add('self_related_label')
            else:
                other = next(iter(owners))
                connect(key, other)
                dependencies[key]['related:'+label] = [other, details.get(other, {}).get('m'),
                                                      details.get(other, {}).get('t'), parts.get(other),
                                                      by_id[other]['r']]

    history = {}
    for version in (150,151,152):
        report = ROOT/f'audit{version}'/'editorial-review.json'
        for row in json.loads(report.read_text())['rows']:
            if row['kind'] == 'vocab':
                history[row['key']] = (row, f'audit{version}/editorial-review.json')
    with (ROOT/'completion/review-register.csv').open() as handle:
        reviewed = {r['key'] for r in csv.DictReader(handle) if r['kind']=='vocab' and r['finalReview']=='reviewed'}
    rows = {}
    for key, entry in by_id.items():
        card = details.get(key,{})
        proof, source = history.get(key, ({},None))
        card_hash = digest(card)
        inherited = key in reviewed and card_hash == proof.get('afterSha256') and (
            proof.get('reading') == entry['r'] and proof.get('partsOfSpeech') == parts.get(key)
            and proof.get('suruMarker') == entry['s'] and proof.get('word') == entry['w'])
        risk = 'high' if errors[key] or len(signals[key]) >= 4 else 'medium' if len(signals[key]) >= 2 else 'low'
        rows[key] = dict(word=entry['w'], risk=risk, errors=sorted(errors[key]), signals=sorted(signals[key]),
                         status=dict(technical='issues' if errors[key] else 'scanned',
                                     linguistic='inherited_author' if inherited else 'pending',
                                     independent='pending', furtherReview=bool(errors[key] or signals[key] or not inherited)),
                         historicalEvidence=source, unresolvedLabels=sorted(set(external[key])),
                         ambiguousLabels=ambiguous[key],
                         fieldHashes={name:digest(value) for name,value in card.items()},
                         hashes=dict(form=digest([entry,parts.get(key)]),
                                     meaning=digest([card.get(x) for x in ('m','t','usage','s')]),
                                     examples=digest([card.get('examples'),card.get('exampleTranslations')]),
                                     dependencies=digest(dependencies[key]), card=card_hash),
                         neighbors=sorted(graph[key],key=int))
    return dict(sha256=hashlib.sha256(raw).hexdigest(), total=len(rows), rows=rows,
                integrity=dict(expected_count=3914, duplicate_ids=sorted(k for k,n in ids.items() if n>1),
                               detail_missing=sorted(ids.keys()-details.keys()), detail_orphans=sorted(details.keys()-ids.keys()),
                               pos_missing=sorted(ids.keys()-parts.keys()), pos_orphans=sorted(parts.keys()-ids.keys())),
                links=link_errors,
                scopeExclusions=['runtime/browser behavior','provenance and independent acceptance',
                                 'runtime routing of reading notes and automatic distractor semantics'])

def summarize(rows):
    return dict(cards=len(rows), risk=dict(Counter(x['risk'] for x in rows)),
                technicalIssues=sum(bool(x['errors']) for x in rows),
                errors=dict(Counter(e for x in rows for e in x['errors'])),
                signals=dict(Counter(e for x in rows for e in x['signals'])),
                inherited=sum(x['status']['linguistic']=='inherited_author' for x in rows),
                withUnresolvedLabels=sum(bool(x['unresolvedLabels']) for x in rows),
                withAmbiguousLabels=sum(bool(x['ambiguousLabels']) for x in rows))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--html', type=Path, default=ROOT/'JLPT_N1_ukrainian_reading_v152.html')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--previous', type=Path, help='Previous inventory.json for changed-field routing')
    args = parser.parse_args()
    start = time.perf_counter()
    report = scan(args.html)
    elapsed = time.perf_counter()-start
    args.out.mkdir(parents=True,exist_ok=True)
    rows = report['rows']
    pilot = {str(i):rows[str(i)] for i in range(121,321)}
    summary = dict(sha256=report['sha256'], full=summarize(rows.values()), pilot=summarize(pilot.values()),
                   integrity=report['integrity'], linkIssueCounts=dict(Counter(x[0] for x in report['links'])),
                   scanSeconds=round(elapsed,3), exclusions=report['scopeExclusions'])
    for name, payload in [('inventory',report),('pilot-200',pilot),('summary',summary)]:
        (args.out/f'{name}.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    if args.previous:
        previous = json.loads(args.previous.read_text())['rows']
        delta = {}
        for key in sorted(rows.keys() | previous.keys(), key=int):
            if key not in previous or key not in rows:
                delta[key] = {'card': 'added' if key in rows else 'removed'}
                continue
            current, old = rows[key], previous[key]
            fields = sorted(name for name in current['fieldHashes'].keys() | old['fieldHashes'].keys()
                            if current['fieldHashes'].get(name) != old['fieldHashes'].get(name))
            scopes = sorted(name for name in current['hashes'] if current['hashes'][name] != old['hashes'][name])
            if fields or scopes:
                delta[key] = {'fields':fields,'scopes':scopes}
        (args.out/'changes.json').write_text(json.dumps(delta,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
