const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
function pools(v, baselinePos=false){
 const h=fs.readFileSync('JLPT_N1_ukrainian_reading_v'+v+'.html','utf8');
 const line=(s)=>h.split('\n').find(x=>x.startsWith(s));
 const base=fs.readFileSync('JLPT_N1_ukrainian_reading_v229.html','utf8');
 const data=['DEFAULT_VOCAB','VOCAB_DETAILS_BY_ID','VOCAB_POS_BY_ID','REVIEWED_READING_OPTIONS'].map(k=>baselinePos&&k==='VOCAB_POS_BY_ID'?base.split('\n').find(x=>x.startsWith('const '+k+' =')):line('const '+k+' =')).join('\n');
 const f=h.slice(h.indexOf('function readingFrame('),h.indexOf('function readingGlossaryEntryHtml('));
 return vm.runInThisContext('(() => {'+data+'\n'+line('function vocabPartOfSpeech(')+'\n'+f+`
 const ACTIVE_VOCAB=DEFAULT_VOCAB;
 return DEFAULT_VOCAB.map(word=>{
   const item={kind:'v',id:String(word.id),word};
   return [word.id,JSON.stringify(quizReadingOptions(item)),JSON.stringify(clozeWordCandidates(item))];
 });})()`);
}
const a=pools(229),b=pools(230,true),scope=new Set([3363,3375,3417,3441,3444,3525,3561,3565,3569,3594,3636,3646]);
assert.equal(a.length,b.length);
const reading=[],cloze=[];
for(let i=0;i<a.length;i++){
 assert.equal(a[i][0],b[i][0]);
 for(const [k,out] of [[1,reading],[2,cloze]]) if(a[i][k]!==b[i][k]){
  const x=JSON.parse(a[i][k]),y=JSON.parse(b[i][k]),xs=new Set(x),ys=new Set(y);
  out.push({id:a[i][0],before:x.length,after:y.length,eligibleChanged:(x.length>=3)!==(y.length>=3),removed:x.filter(z=>!ys.has(z)),added:y.filter(z=>!xs.has(z))});
 }
}
const summary={records:a.length};
for(const [tag,rows] of [['reading',reading],['cloze',cloze]]) summary[tag]={changed:rows.length,outside:rows.filter(x=>!scope.has(x.id)).length,eligibility:rows.filter(x=>x.eligibleChanged).map(x=>x.id),sample:rows.filter(x=>!scope.has(x.id)).slice(0,3)};
assert.equal(a.length,3914); assert.equal(reading.length,0); assert.equal(cloze.length,0);
console.log(JSON.stringify(summary));
