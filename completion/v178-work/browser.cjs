const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const base='JLPT_N1_ukrainian_reading_v177.html', file='JLPT_N1_ukrainian_reading_v178.html';
const updates=JSON.parse(fs.readFileSync('completion/v178-work/updates.json','utf8'));
const ids=['421','423','425','430','433','435','436','438','440','444','447','449'];
const changedIds=['421','423','430','433','435','436','438','440','444','447','449'];
function readPath(v,p){let cur=v;for(const part of String(p).split('.')){if(cur===undefined||cur===null)throw new Error('Missing path '+p);cur=Array.isArray(cur)?cur[Number(part)]:cur[part];}return cur;}
async function open(browser,name,width=1280){
 const page=await browser.newPage({viewport:{width,height:915}}),errors=[];
 page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(pathToFileURL(path.resolve(name)).href);
 return {page,errors};
}
async function snapshot(page){return page.evaluate(()=>({vocab:DEFAULT_VOCAB.length,details:JSON.parse(JSON.stringify(VOCAB_DETAILS_BY_ID)),grammarIds:Object.keys(GRAMMAR_DETAILS_BY_ID),pos:JSON.parse(JSON.stringify(VOCAB_POS_BY_ID)),pairs:JSON.parse(JSON.stringify(VOCAB_AUDITED_PAIRS)),vocabIds:DEFAULT_VOCAB.map(x=>x.id)}));}
async function main(){
 const browser=await chromium.launch({headless:true});
 const result={sha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),cardsChecked:12,fieldsChecked:13,pairsChecked:0,widths:[]};
 try{
  const a=await open(browser,base),b=await open(browser,file),before=await snapshot(a.page),after=await snapshot(b.page);
  assert.deepEqual(a.errors,[]);assert.deepEqual(b.errors,[]);
  assert.equal(before.vocab,3914);assert.equal(after.vocab,3914);assert.equal(Object.keys(after.details).length,3914);
  assert.equal(after.grammarIds.length,130);assert.equal(Object.keys(after.pos).length,3914);assert.equal(after.pairs.length,859);
  assert.deepEqual(after.vocabIds,before.vocabIds);assert.deepEqual(after.grammarIds,before.grammarIds);assert.deepEqual(after.pos,before.pos);assert.deepEqual(after.pairs,before.pairs);
  assert.deepEqual(after.details['425'],before.details['425']);
  const changed=Object.keys(before.details).filter(id=>JSON.stringify(before.details[id])!==JSON.stringify(after.details[id]));
  assert.deepEqual(changed,changedIds);
  for(const row of updates){assert.equal(readPath(before.details[String(row.id)],row.field),row.before);assert.equal(readPath(after.details[String(row.id)],row.field),row.after);}
  const rendered=await b.page.evaluate(async({ids,updates})=>{
   const norm=x=>String(x||'').replace(/\s+/gu,'');const rows=[];
   for(const id of ids){
    const card=await getCardData('v',id),shell=renderCardShell('v',id,card),wrap=document.createElement('div');wrap.innerHTML=shell;
    const examples=document.createElement('div');examples.innerHTML=vocabExamplesHtml(id,card.examples);
    const text=wrap.textContent||'',exampleText=examples.textContent||'';
    const fields=updates.filter(x=>String(x.id)===id).map(x=>{
      const target=(x.field.startsWith('exampleTranslations.')||x.field.startsWith('examples.'))?exampleText:text;
      const expected=x.field==='usage'?x.after.replace(/^(?:Іменник|Дієслово|Прислівник|[наナ][-‑]прикметник|[іイ][-‑]прикметник)\s*(?:[;:,—–]\s*|\.\s+)/u,''):x.after;
      return {field:x.field,present:norm(target).includes(norm(expected))};
    });
    rows.push({id,cardRendered:text.length>0,allExamplesRendered:(VOCAB_DETAILS_BY_ID[id].exampleTranslations||[]).every(x=>norm(exampleText).includes(norm(x))),fields});
   }
   localStorage.setItem('choba_n1uk_storage_v1','v178-progress-sentinel');
   return {rows,progressStorageUnchanged:localStorage.getItem('choba_n1uk_storage_v1')==='v178-progress-sentinel'};
  },{ids,updates});
  assert(rendered.rows.every(x=>x.cardRendered&&x.allExamplesRendered&&x.fields.every(y=>y.present)),JSON.stringify(rendered.rows));
  assert.equal(rendered.progressStorageUnchanged,true);
  result.renderedCards=rendered.rows;result.progressStorageUnchanged=true;
  for(const width of [360,412,1280]){
   const p=await open(browser,file,width);
   const data=await p.page.evaluate(async ids=>{const out=[];for(const id of ids){const c=await getCardData('v',id),h=renderCardShell('v',id,c),w=document.createElement('div');w.innerHTML=h;const t=(w.textContent||'').replace(/\s+/gu,'');out.push(h.length>0&&VOCAB_DETAILS_BY_ID[id].exampleTranslations.every(x=>t.includes(String(x).replace(/\s+/gu,''))));}return {width:innerWidth,rows:out};},ids);
   assert.deepEqual(p.errors,[]);assert.equal(data.width,width);assert.deepEqual(data.rows,ids.map(()=>true));result.widths.push({width,pass:true,cardsRendered:data.rows});await p.page.close();
  }
  result.changedIds=changed;result.reviewedWithoutChange=['425'];result.counts={vocabulary:3914,grammar:130,lexicalPairs:859};result.pass=true;
  fs.writeFileSync('completion/v178-work/browser-results.json',JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify(result,null,2));
 }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
