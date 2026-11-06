"""Bind sampled editorial decisions to v152 and prepare the 200-card queue."""
import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
from scan import ROOT, constant, digest

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    inventory = json.loads((args.out/'inventory.json').read_text())
    rows = inventory['rows']
    html = (ROOT/'JLPT_N1_ukrainian_reading_v152.html').read_text()
    cards = constant(html,'VOCAB_DETAILS_BY_ID')
    entries = {str(row['id']):row for row in constant(html,'DEFAULT_VOCAB')}
    pos = constant(html,'VOCAB_POS_BY_ID')
    pairs = constant(html,'VOCAB_AUDITED_PAIRS')
    with (here/'editorial.tsv').open() as handle:
        decisions = list(csv.DictReader(handle,delimiter='\t'))
    seen = set()
    groups = defaultdict(list)
    manual = {}
    for item in decisions:
        key = item['id']
        assert key not in seen and 121 <= int(key) <= 320
        seen.add(key)
        assert entries[key]['r'] == item['reading'] and pos[key] == item['pos'].split(' і ')
        card = cards[key]
        assert digest(card) == rows[key]['hashes']['card']
        assert len(card['examples']) == len(card['exampleTranslations']) == 2
        groups[item['group']].append(key)
        manual[key] = dict(item, word=card['w'], risk=rows[key]['risk'],
                           hashes=rows[key]['hashes'], fieldHashes=rows[key]['fieldHashes'],
                           reviewScope=['reading','pos','definition','meaning','usage','related labels',
                                        'two Japanese examples','two Ukrainian translations'],
                           examples=[dict(japanese=ja,ukrainian=uk)
                                     for ja,uk in zip(card['examples'],card['exampleTranslations'])])
    pair_indexes = [34,36,40,50,51,62,63,64,73]
    pair_evidence = []
    for index in pair_indexes:
        pair = pairs[index]
        left, right = str(pair['a']), str(pair['b'])
        assert left in seen and right in seen and groups[manual[left]['group']] == groups[manual[right]['group']]
        pair_evidence.append(dict(index=index, a=left, b=right, type=pair['type'],
                                  sha256=digest(pair), scope='consistency with sampled cards',
                                  independent=False))
    todo = {str(i) for i in range(121,321)} - seen
    priority = {'high':0, 'medium':1, 'low':2}
    queue = []
    # Keep related neighbors together without absorbing an entire large component.
    while todo:
        seed = min(todo, key=lambda key:(priority[rows[key]['risk']],int(key)))
        todo.remove(seed)
        batch = [seed]
        frontier = set(rows[seed]['neighbors']) & todo
        while frontier and len(batch) < 8:
            neighbor = min(frontier,key=lambda key:(priority[rows[key]['risk']],int(key)))
            todo.remove(neighbor)
            batch.append(neighbor)
            frontier = (frontier | set(rows[neighbor]['neighbors'])) & todo
        queue.append(batch)
    assert sum(map(len,queue)) + len(seen) == 200
    counts = Counter((row['risk'],row['disposition']) for row in manual.values())
    for key,row in manual.items():
        status = rows[key]['status']
        status['linguistic'] = 'pilot_review_complete' if row['disposition'] == 'retain' else (
            'pilot_revision_proposed' if row['disposition'] == 'edit' else 'pilot_follow_up')
        status['furtherReview'] = row['disposition'] != 'retain' or bool(rows[key]['signals'])
    result = dict(sha256=inventory['sha256'], pilotSize=200, languageRead=len(manual),
                  remainingPilotLanguage=200-len(manual), independentRead=0,
                  counts={risk:{d:counts[risk,d] for d in ('retain','edit','follow_up')}
                          for risk in ('high','medium','low')},
                  editorialGroups=groups, nextQueue=queue, pairCrossChecks=pair_evidence,
                  decisions=manual)
    (args.out/'editorial-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    (args.out/'pilot-200.json').write_text(json.dumps({str(i):rows[str(i)] for i in range(121,321)},
                                                   ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('pilotSize','languageRead','remainingPilotLanguage',
                                           'independentRead','counts')},ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
