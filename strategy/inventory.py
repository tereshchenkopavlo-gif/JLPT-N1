"""Read-only inventory of current release and sidecar provenance candidates.
Does not modify runtime IDs, source HTML, historical audits or finalReview states.
"""
from pathlib import Path
import json,re,hashlib,csv,collections
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'strategy';html=ROOT/'JLPT_N1_ukrainian_reading_v139.html'
if not html.exists():html=ROOT/'release139/JLPT_N1_ukrainian_reading_v139.html'
s=html.read_text();sha=hashlib.sha256(html.read_bytes()).hexdigest()
assert sha=='e18ab0ee3ec3a56dced31b9abb6ec4813d92c102f93f20922e3dc05718d1dd17'
def get(n):return json.JSONDecoder().raw_decode(s[re.search(r'const '+n+r'\s*=\s*',s).end():])[0]
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
rows=[]
def add(kind,key,path,value,status='unknown',evidence='',action='field_source_reconstruction_then_rights_review'):
 rows.append(dict(kind=kind,key=key,fieldPath=path,contentSha256=digest(value),originStatus=status,evidence=evidence,rightsStatus='not_cleared_for_public_product',nextAction=action))
vs,gs=get('DEFAULT_VOCAB'),get('GRAMMAR')
for kind,cards,name in [('v',vs,'VOCAB_DETAILS_BY_ID'),('g',gs,'GRAMMAR_DETAILS_BY_ID')]:
 db=get(name)
 for card in cards:
  id=str(card['id']);d=db[id];add('vocab' if kind=='v' else 'grammar',f'{kind}:{id}',f'{name}[{id}]',dict(header=card,details=d))
  for i,ja in enumerate(d['examples']):
   ua=d.get('exampleTranslations',[]);add('example_pair',f'{kind}:{id}:example:{i}',f'{name}[{id}].examples[{i}]',dict(ja=ja,uk=ua[i] if i<len(ua) else None))
for name,kind in [('VOCAB_AUDITED_PAIRS','vocab_pair'),('GRAMMAR_AUDITED_PAIRS','grammar_pair'),('AUTO_ANTONYM_PAIRS','antonym_pair')]:
 for i,x in enumerate(get(name)):add(kind,f'{kind}:{i}',f'{name}[{i}]',x)
for key,x in get('REVIEWED_MEANING_QUIZZES').items():add('meaning_quiz',key,f'REVIEWED_MEANING_QUIZZES[{key}]',x)
for i,x in enumerate(get('REVIEWED_EXAMPLE_TARGETS')):add('exact_mapping',f"{x['kind']}:{x['id']}:example:{x['exampleIndex']}",f'REVIEWED_EXAMPLE_TARGETS[{i}]',x,'authored_claim','audit137/author.py' if i<30 else 'audit139/author.py','confirm_authorship_and_underlying_example_origin')
readings=get('readingBank');qcount=0;claimcounts=collections.Counter()
for level,items in readings.items():
 for i,x in enumerate(items):
  key=x.get('id',f'legacy:{level}:{i}');m=re.match(r'[ml](\d+)-',key);version=m[1] if m else None
  evidence=f'JLPT_N1_v{version}_audit.md; audit{version}/' if version else 'completion/reading-inventory.json; original source unresolved'
  status='authored_claim' if version else 'unknown';claimcounts[status]+=1
  add('reading',key,f'readingBank.{level}[{i}]',x,status,evidence,'confirm_independent_creation_and_sources' if version else 'source_comparison_or_independent_replacement_permission_review')
  for qi,q in enumerate(x['questions']):qcount+=1;add('reading_question',f'{key}:q:{qi}',f'readingBank.{level}[{i}].questions[{qi}]',q,status,evidence)
# Preserve later human decisions when the source unit is byte-equivalent.
prior={}
if (P/'asset-register.csv').exists():
 for r in csv.DictReader((P/'asset-register.csv').open()):prior[(r['kind'],r['key'])]=r
for row in rows:
 if row['kind']=='example_pair' and row['key'] in ['v:210:example:1','v:790:example:1']:
  row['originStatus']='authored_claim';row['evidence']='audit137/author.py' if row['key'].startswith('v:210:') else 'audit139/build.py'
 previous=prior.get((row['kind'],row['key']))
 if previous and previous['contentSha256']==row['contentSha256']:
  for field in ['originStatus','evidence','rightsStatus','nextAction']:row[field]=previous[field]
with (P/'asset-register.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
register=list(csv.DictReader((ROOT/'completion/review-register.csv').open()));statusCounts=dict(collections.Counter(x['finalReview'] for x in register))
snapshot=dict(asOf='2026-11-04 Asia/Tokyo',publishedBaseline=dict(version=138,commit='236317fe0f9b47d4afceea2d02bf20fdbdf36c75',sha256='6f7ea6a3d4ca30e8a9cc6ffad31994d99e925809fa4d4b94fe2bf28349027dfc'),preparedRelease=dict(version=139,sha256=sha,localChecks='audit139/',publicationStatus='See PROJECT_STATUS.md and GitHub main; snapshot preserves pre-publication state'),counts=dict(vocab=len(vs),grammar=len(gs),vocabExamples=7828,grammarExamples=261,medium=len(readings['medium']),long=len(readings['long']),readingQuestions=qcount,vocabPairs=len(get('VOCAB_AUDITED_PAIRS')),grammarPairs=len(get('GRAMMAR_AUDITED_PAIRS')),antonymPairs=len(get('AUTO_ANTONYM_PAIRS')),storedMeaningQuizzes=len(get('REVIEWED_MEANING_QUIZZES')),exactMappings=len(get('REVIEWED_EXAMPLE_TARGETS')),contextQuizSets=sum('quiz'in x for x in get('REVIEWED_EXAMPLE_TARGETS'))),remainingReadingSlots=dict(medium=21,long=19),finalReviewRegister=dict(rows=len(register),statuses=statusCounts,scope='Final acceptance evidence, not a reset of historical author audits; narrow C04/C05 fixes do not close whole cards.'),provenanceInventory=dict(units=len(rows),byKind=dict(collections.Counter(x['kind'] for x in rows)),readingOriginClaims=dict(claimcounts),rightsCleared=sum(x['rightsStatus']=='cleared_for_defined_use' for x in rows),scope='Preliminary origin/rights triage, no book-wide comparison or legal clearance'),runtimeChangedByStrategy=False)
assert (len(vs),len(gs),qcount,len(rows))==(3914,130,381,14198)
(P/'snapshot.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(units=len(rows),statuses=statusCounts,byKind=snapshot['provenanceInventory']['byKind'])))
