const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),d=JSON.parse(fs.readFileSync(0,'utf8'));
const engine=data=>vm.runInNewContext(`const REVIEWED_EXAMPLE_TARGETS=${JSON.stringify(data.targets)};${data.helper};({${data.method}})`,{VOCAB_KANA_EXAMPLE_TARGETS:data.forms});
const old=engine(d.old),now=engine(d.now),changes=[];let count=0,single=0;
for(const [kind,cards,db]of [['v',d.v,d.vd],['g',d.g,d.gd]])for(const card of cards)for(const [index,s]of db[card.id].examples.entries()){
 count++;const oldWord=kind==='v'?d.oldV.find(v=>v.id===card.id).w:card.w,a=old.markTarget(s,kind,oldWord),b=now.markTarget(s,kind,card.w);
 assert(b.found,`${kind}:${card.id}:${index}`);const spans=[...b.s.matchAll(/\u0001([^\u0002]*)\u0002/g)].map(x=>x[1]);if(spans.some(x=>x.length===1))single++;
 if(a.s!==b.s){assert.equal(kind,'v');assert(d.aliasIds.includes(card.id));changes.push({kind,id:card.id,index,spans});}
}
assert.equal(count,8089);process.stdout.write(JSON.stringify({sha256:d.sha256,pass:true,examples:count,unmarked:0,singleCharacterResults:single,changedExamples:changes.length,changes},null,2));
