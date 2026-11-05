"""Verify that the pilot catches deliberately injected faults and dependency edits."""
from pathlib import Path
import json
import re
import tempfile
from scan import ROOT, constant, scan

source = ROOT/'JLPT_N1_ukrainian_reading_v152.html'
html = source.read_text()
baseline = scan(source)
assert baseline['total'] == 3914
assert sum(row['status']['linguistic']=='inherited_author' for row in baseline['rows'].values()) == 120

def replace_constant(text,name,value):
    start = re.search(r'\bconst '+name+r'\s*=\s*',text).end()
    _,end = json.JSONDecoder().raw_decode(text,start)
    return text[:start] + json.dumps(value,ensure_ascii=False,separators=(',',':')) + text[end:]

with tempfile.TemporaryDirectory() as directory:
    test = Path(directory)/'mutated.html'
    cards = constant(html,'VOCAB_DETAILS_BY_ID')
    cards['1']['exampleTranslations'][0] += ' [test]'
    cards['121']['exampleTranslations'].pop()
    cards['123']['w'] = 'TEST'
    modified = replace_constant(html,'VOCAB_DETAILS_BY_ID',cards)
    pos = constant(html,'VOCAB_POS_BY_ID')
    pos['122'] = ['TEST']
    modified = replace_constant(modified,'VOCAB_POS_BY_ID',pos)
    pairs = constant(html,'VOCAB_AUDITED_PAIRS')
    first = pairs[0]
    first['note'] += ' [test]'
    pairs.append({'a':'129','b':'999999','type':'near','note':'[test]'})
    modified = replace_constant(modified,'VOCAB_AUDITED_PAIRS',pairs)
    test.write_text(modified)
    checked = scan(test)
    actual,old = checked['rows'],baseline['rows']
    assert actual['1']['status']['linguistic'] == 'pending'
    assert actual['1']['hashes']['examples'] != old['1']['hashes']['examples']
    assert actual['1']['hashes']['form'] == old['1']['hashes']['form']
    assert actual['1']['fieldHashes']['m'] == old['1']['fieldHashes']['m']
    assert 'example_translation_alignment' in actual['121']['errors']
    assert 'invalid_pos' in actual['122']['errors']
    assert 'headword_mismatch' in actual['123']['errors']
    assert 'invalid_pair' in actual['129']['errors']
    for endpoint in (first['a'], first['b']):
        assert actual[endpoint]['hashes']['dependencies'] != old[endpoint]['hashes']['dependencies']
        assert actual[endpoint]['hashes']['card'] == old[endpoint]['hashes']['card']
    assert actual['300']['hashes'] == old['300']['hashes']
    counterpart = first['b']
    changed_cards = constant(html,'VOCAB_DETAILS_BY_ID')
    changed_cards[counterpart]['t'] += ' [test]'
    test.write_text(replace_constant(html,'VOCAB_DETAILS_BY_ID',changed_cards))
    linked = scan(test)['rows']
    assert linked[first['a']]['hashes']['dependencies'] != old[first['a']]['hashes']['dependencies']
    assert linked[first['a']]['hashes']['card'] == old[first['a']]['hashes']['card']
    assert source.read_text() == html

print('PASS: review invalidation, unchanged fields, pair dependency propagation, malformed POS and alignment, headword mismatch, broken pair, untouched card and baseline')
