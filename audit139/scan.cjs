const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const d=JSON.parse(fs.readFileSync(0,'utf8'));
function engine(data){return vm.runInNewContext(`const REVIEWED_EXAMPLE_TARGETS=${JSON.stringify(data.targets)};${data.helper};({${data.method}})`,{VOCAB_KANA_EXAMPLE_TARGETS:data.forms},{timeout:1000})}
const old=engine(d.old),now=engine(d.now),changed=[],unmarked=[],single=[];let examples=0;
const key=r=>`${r.kind}_${r.id}_${r.exampleIndex??r.index}`;
const decisions=new Map(d.decisions.map(r=>[key(r),r]));
for(const [kind,cards,db,oldDb] of [['v',d.v,d.vd,d.oldVd],['g',d.g,d.gd,d.gd]])for(const card of cards)for(const [index,sentence] of db[card.id].examples.entries()){
 examples++;const oldWord=kind==='v'?d.oldV.find(v=>v.id===card.id).w:card.w;
 const a=old.markTarget(oldDb[card.id].examples[index],kind,oldWord),b=now.markTarget(sentence,kind,card.w);
 const spans=[...b.s.matchAll(/\u0001([^\u0002]*)\u0002/g)].map(x=>x[1]);
 if(!b.found)unmarked.push({kind,id:card.id,index});
 if(spans.some(x=>[...x].length===1))single.push({kind,id:card.id,index});
 const decision=decisions.get(key({kind,id:card.id,index}));
 if(decision)assert.deepEqual(spans,decision.forms);
 if(a.s!==b.s||a.found!==b.found){assert(decision&&decision.decision!=='retain');changed.push({kind,id:card.id,index,oldFound:a.found,newFound:b.found,spans});}
 else if(decision)assert.equal(decision.decision,'retain');
}
assert.equal(examples,8089);assert.equal(unmarked.length,0);assert.equal(single.length,289);assert.equal(changed.length,238);assert.equal(decisions.size,526);
const lookup=vm.runInNewContext(`const REVIEWED_EXAMPLE_TARGETS=${JSON.stringify(d.now.targets)};${d.now.helper};reviewedExampleTarget`);
for(const r of d.now.targets){assert.equal(lookup(r.sentence+'追記',r.kind,r.word),null);assert.equal(lookup(r.sentence,r.kind,r.word+'別'),null);assert.equal(lookup(r.sentence,r.kind==='v'?'g':'v',r.word),null)}
process.stdout.write(JSON.stringify({sha256:d.sha256,examples,unmarked,singleCharacterCandidates:single.length,changed,reviewedCandidates:526,exactScopeNegativeChecks:d.now.targets.length*3,pass:true},null,2));
