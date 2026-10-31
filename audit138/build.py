from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'audit138';R=ROOT/'release138';R.mkdir(exist_ok=True)
old=(ROOT/'JLPT_N1_ukrainian_reading_v137.html').read_text();assert hashlib.sha256(old.encode()).hexdigest()=='005adcfb62d8fa81774b4008e61171db7277ba0e99f0129dac0962b793058dce'
style=(P/'style.css').read_text()
new=old.replace('</style>',style+'\n</style>',1).replace('学習アプリ · v137','学習アプリ · v138')
# Exact scope: one CSS insertion and the visible version. All data and JS are byte-identical.
assert new.replace(style+'\n</style>','</style>',1).replace('学習アプリ · v138','学習アプリ · v137')==old
assert new.split('<script>',1)[1]==old.split('<script>',1)[1]
(R/'JLPT_N1_ukrainian_reading_v138.html').write_text(new);(P/'app.js').write_text(new.split('<script>',1)[1].split('</script>',1)[0])
report=dict(sha256=hashlib.sha256(new.encode()).hexdigest(),bytes=len(new.encode()),scope='CSS only in comparison view; version title',allDataAndJSUnchanged=True)
(P/'build-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report))
