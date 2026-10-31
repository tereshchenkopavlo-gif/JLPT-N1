// Execute the unmodified markTarget method extracted from the pinned application.
// This diagnoses matching only: a matched character is not proof of the correct sense.
const vm=require('node:vm'),fs=require('node:fs');
const input=JSON.parse(fs.readFileSync(0,'utf8'));
const engine=vm.runInNewContext('({'+input.method+'})',{VOCAB_KANA_EXAMPLE_TARGETS:input.forms},{timeout:1000});
const result={examples:0,byKind:{v:0,g:0},unmarked:[],singleCharacter:[]};
for(const [kind,cards,details] of [['v',input.v,input.vd],['g',input.g,input.gd]]){
 for(const card of cards){
  for(const [exampleIndex,sentence] of details[card.id].examples.entries()){
   result.examples++;result.byKind[kind]++;
   const marked=engine.markTarget(sentence,kind,card.w);
   const spans=[...marked.s.matchAll(/\u0001([^\u0002]*)\u0002/g)].map(x=>x[1]);
   const row={kind,id:card.id,word:card.w,exampleIndex,sentence,spans};
   if(!marked.found)result.unmarked.push(row);
   if(spans.some(s=>[...s].length===1))result.singleCharacter.push(row);
  }
 }
}
process.stdout.write(JSON.stringify(result));
