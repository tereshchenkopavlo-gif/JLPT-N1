const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const d=JSON.parse(fs.readFileSync(0,'utf8'));
function engine(data){return vm.runInNewContext(`const REVIEWED_EXAMPLE_TARGETS=${JSON.stringify(data.targets||[])};${data.helper||''};({${data.method}})`,{VOCAB_KANA_EXAMPLE_TARGETS:data.forms},{timeout:1000})}
const old=engine(d.old),now=engine(d.now),changed=[],unmarked=[],single=[];let examples=0;
for(const [kind,cards,db,oldDb] of [['v',d.v,d.vd,d.oldVd],['g',d.g,d.gd,d.gd]])for(const card of cards)for(const [index,sentence] of db[card.id].examples.entries()){
 examples++;const a=old.markTarget(oldDb[card.id].examples[index],kind,card.w),b=now.markTarget(sentence,kind,card.w);
 const spans=[...b.s.matchAll(/\u0001([^\u0002]*)\u0002/g)].map(x=>x[1]);
 if(!b.found)unmarked.push({kind,id:card.id,index});
 if(spans.some(x=>[...x].length===1))single.push({kind,id:card.id,index});
 if(a.s!==b.s||a.found!==b.found)changed.push({kind,id:card.id,index,oldFound:a.found,newFound:b.found,spans});
}
assert.equal(examples,8089);assert.equal(unmarked.length,0);assert.equal(single.length,526);assert.equal(changed.length,30);
for(const row of changed)assert(d.now.targets.some(r=>r.kind===row.kind&&r.id===row.id&&r.exampleIndex===row.index));
const lookup=vm.runInNewContext(`const REVIEWED_EXAMPLE_TARGETS=${JSON.stringify(d.now.targets)};${d.now.helper};reviewedExampleTarget`);
for(const r of d.now.targets){assert.equal(lookup(r.sentence+'追記',r.kind,r.word),null);assert.equal(lookup(r.sentence,r.kind,r.word+'別'),null);assert.equal(lookup(r.sentence,r.kind==='v'?'g':'v',r.word),null)}
process.stdout.write(JSON.stringify({sha256:d.sha256,examples,unmarked,singleCharacterCandidates:single.length,changed,exactScopeNegativeChecks:d.now.targets.length*3,pass:true},null,2));
