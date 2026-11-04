"""Derive minimal evidence without republishing the complete raw learning payload."""
from pathlib import Path
import json,re,hashlib,csv,collections
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'review20261105'
raw=json.loads((P/'probe.json').read_text());sha=hashlib.sha256((ROOT/'JLPT_N1_ukrainian_reading_v141.html').read_bytes()).hexdigest();assert raw['sha256']==sha
rows=raw['readingEligibility']['rows'];guarded=[x for x in rows if x['reason']!='eligible'];assert len(rows)==3914 and len(guarded)==1482
def subtype(x):
 if x['reason']!='reading_not_single_hiragana':return ''
 if re.search('[／/・、,]',x['reading']):return 'multiple_readings'
 return 'empty_reading_field'if not x['reading']else'phrase_punctuation'
def cohort(x):
 w=x['word'];r=x['reading']
 if not re.search('[一-鿿]',w):return 'context_meaning'
 if re.search('[〜～・／/]',w):return 'complete_word_or_variant'
 if re.search('[／/・、,]',r):return 'sense_bound_reading'
 if not re.fullmatch('[ぁ-ゟー]+',r):return 'phrase_bound_reading'
 return 'open_kana_recall'
with (P/'reading-guarded.csv').open('w',newline='')as f:
 writer=csv.DictWriter(f,fieldnames=['id','technicalReason','reasonSubtype','candidateCount','proposalGroup','semanticReview'],lineterminator='\n');writer.writeheader()
 for x in guarded:writer.writerow(dict(id=x['id'],technicalReason=x['reason'],reasonSubtype=subtype(x),candidateCount=x['candidateCount'],proposalGroup=cohort(x),semanticReview='not_approved_per_item'))
decisions={}
for line in (P/'grammar-decisions.tsv').read_text().splitlines():
 id,flags,note=line.split('\t',2);assert int(id)not in decisions;decisions[int(id)]=dict(flags=[]if flags=='-'else flags.split(','),note=note)
assert set(decisions)==set(range(1,131));cases=[]
def h(s):return hashlib.sha256(s.encode()).hexdigest()
for r in raw['grammarCases']:
 d=decisions[r['id']];assert r['targetFound']and len(r['choices'])==len(set(r['choices']))==4
 cases.append(dict(caseId=f"g:{r['id']}:e0:seed20261105",id=r['id'],word=r['word'],exampleIndex=0,route=r['route'],sentenceSha256=h(r['sentence']),promptSha256=h(r['prompt']),choiceSha256=[h(c)for c in r['choices']],answer=r['answer'],correctSha256=h(r['correct']),explainSha256=h(r['explain']),flags=d['flags'],observation=d['note'],status='revision_needed'if d['flags']else'no_issue_found_in_this_fixed_case',fullCardCredit=False))
counts=collections.Counter(c['status']for c in cases);flags=collections.Counter(f for c in cases for f in c['flags'])
report=dict(date='2026-11-05',sha256=sha,seed=raw['seed'],reviewType='author_case_review',independentReview=False,scope='One fixed first-example meaning question per grammar ID; not second examples or all candidate draws. Raw strings are reproducible from the unchanged public v141 and seed; only hashes/IDs and original editorial notes stored here.',cases=cases,statusCounts=dict(counts),flagCounts=dict(flags),routes=dict(collections.Counter(r['route']for r in cases)),runtimeChanges=0,fullCardCredits=0,newAcceptanceRegisterCredits=0)
(P/'grammar-findings.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
with (ROOT/'completion/physical-device-results-template.csv').open('w',newline='')as f:
 fields=['device','model','os','browser','browserVersion','openMethod','candidateSha256','scenario','status','testedAt','observation','evidence','defectId'];w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader()
 for device in ['Android','Windows']:
  for i in range(1,17):w.writerow(dict(device=device,candidateSha256=sha,scenario=f'P{i:02}',status='not_run'))
summary=dict(date='2026-11-05',baseCommit=raw['baseCommit'],sha256=sha,browser=raw['browser'],readingTechnicalReasons=dict(collections.Counter(x['reason']for x in guarded)),readingFormatSubtypes=dict(collections.Counter(subtype(x)for x in guarded if subtype(x))),proposalGroups=dict(collections.Counter(cohort(x)for x in guarded)),guardedIds=1482,eligibleIds=2432,grammarCases=130,grammarStatusCounts=dict(counts),grammarFlagCounts=dict(flags),physicalCasesNotRun=32,runtimeChanges=0,acceptanceRegisterChanges=0)
(P/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary,ensure_ascii=False))
