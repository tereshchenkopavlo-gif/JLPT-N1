from pathlib import Path
import subprocess,json,hashlib,csv,re
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'review20261105';BASE='571aa092d256e682ad16873b7462dcc263cf62d8'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(name,value):
 assert value,name
 checks.append(dict(name=name,pass_=True))
check('Published v141 HTML bytes unchanged',digest(ROOT/'JLPT_N1_ukrainian_reading_v141.html')=='08e016a95f1786f243c29f54289edf5dd65aac4c43c9ff863b25c9f0422f75a3')
allowed={'AGENTS.md','PROJECT_STATUS.md','README.md','completion/BACKLOG.md','strategy/README.md','strategy/PROVENANCE_REVIEW.md','strategy/LEARNING_METHODOLOGY.md'}
unchanged=0
for line in subprocess.check_output(['git','ls-tree','-r',BASE],cwd=ROOT,text=True).splitlines():
 meta,path=line.split('\t',1);blob=meta.split()[2]
 if path in allowed:continue
 actual=subprocess.check_output(['git','hash-object',str(ROOT/path)],text=True).strip()
 assert actual==blob,path
 unchanged+=1
check('All other baseline files preserved, including HTML, IDs, audit reports and acceptance register',unchanged>100)
paths=[P/'reading-guarded.csv',P/'summary.json',P/'grammar-findings.json',P/'public-inventory.json',P/'proposed-grammar-questions.json',ROOT/'completion/physical-device-results-template.csv']
expected={str(p):digest(p)for p in paths}
for name in ['derive.py','drafts.py','public_inventory.py']:subprocess.run(['python',str(P/name)],check=True,cwd=ROOT,stdout=subprocess.DEVNULL)
check('Derived snapshots match committed evidence and individual author decisions',expected=={str(p):digest(p)for p in paths})
summary=json.loads((P/'summary.json').read_text());guarded=list(csv.DictReader((P/'reading-guarded.csv').open()));finding=json.loads((P/'grammar-findings.json').read_text());api=json.loads((P/'api-state.json').read_text());public=json.loads((P/'public-inventory.json').read_text());drafts=json.loads((P/'proposed-grammar-questions.json').read_text())
check('1482 unique guarded vocabulary IDs and five proposed cohorts',len(guarded)==len({x['id']for x in guarded})==1482 and sum(summary['proposalGroups'].values())==1482 and len(summary['proposalGroups'])==5)
check('Reading filter reasons and format subtypes exactly reconstructed',summary['readingTechnicalReasons']=={'fewer_than_three_filtered_candidates':717,'reading_not_single_hiragana':173,'no_hidden_kanji':551,'marked_or_multiple_headword':41} and summary['readingFormatSubtypes']=={'multiple_readings':83,'empty_reading_field':68,'phrase_punctuation':22})
check('130 fixed cases, 67 flagged, no card or register acceptance claimed',len(finding['cases'])==130 and finding['statusCounts']=={'no_issue_found_in_this_fixed_case':63,'revision_needed':67} and not finding['independentReview']and finding['newAcceptanceRegisterCredits']==0 and all(not r['fullCardCredit']for r in finding['cases']))
check('Six content drafts remain uninstalled',len(drafts['drafts'])==6 and all(not r['approvedForRuntime']and r['status']=='draft_not_installed'and len(set([r['correct'],*r['wrong']]))==4 for r in drafts['drafts']))
check('Public copies inventory is a frozen exposure record, not clearance',public['mainHtmlCount']==23 and public['historyUniqueBlobs']==24 and public['branchHeadHtmlOccurrences']==150 and len(public['fetchedHeads'])==8 and public['notClearedByThisInventory']and all(r['rightsStatus']=='not_cleared'for r in public['mainFiles']))
arts=[a for r in api['actions']['artifactRuns']for a in r['artifacts']]
check('Actions metadata coverage: 243 indexed runs, 67 queried runs, 66 unexpired archives',api['actions']['totalRuns']==len(api['actions']['runIndex'])==243 and api['actions']['queriedArtifactRuns']==len(api['actions']['artifactRuns'])==67 and len(arts)==66 and not any(x['expired']for x in arts) and not api['actions']['archiveContentsInspected'])
physical=list(csv.DictReader((ROOT/'completion/physical-device-results-template.csv').open()))
check('Physical-device matrix is an unexecuted template',len(physical)==32 and all(x['status']=='not_run'and not x['testedAt']and not x['evidence']for x in physical))
register=list(csv.DictReader((ROOT/'completion/review-register.csv').open()))
check('Previous 325 accepted evidence rows not reset or expanded',len(register)==5842 and sum(x['finalReview']=='reviewed'for x in register)==325)
report=dict(date='2026-11-05',baseCommit=BASE,sha256=summary['sha256'],checks=checks,baselineFilesPreserved=unchanged,pass_=True,scope='Technical integrity of documentary/diagnostic work only; not linguistic acceptance, physical-device results or legal clearance.')
(P/'validation-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('PASS',len(checks),'evidence-integrity checks;',unchanged,'baseline files unchanged')
