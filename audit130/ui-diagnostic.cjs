const { chromium } = require('playwright');
const { pathToFileURL } = require('node:url');
const path = require('node:path');
(async()=>{
 const b=await chromium.launch({headless:true});
 try{
 const page=await b.newPage({viewport:{width:412,height:915}});
 const errs=[];page.on('pageerror',e=>errs.push(e.message));
 await page.goto(pathToFileURL(path.resolve('release130/JLPT_N1_ukrainian_reading_v130.html')).href);
 await page.waitForTimeout(250);
 const s=await page.evaluate(()=>({
  title:document.title,
  inputs:[...document.querySelectorAll('input')].map(e=>({id:e.id,type:e.type,accept:e.accept,outerHTML:e.outerHTML.slice(0,350)})),
  headings:[...document.querySelectorAll('h1,h2,h3')].slice(0,15).map(e=>({tag:e.tagName,text:e.innerText.slice(0,100)})),
  controls:[...document.querySelectorAll('button,[role="tab"],select,input[type="button"],a')].slice(0,90).map(e=>({tag:e.tagName,id:e.id,role:e.getAttribute('role'),text:(e.innerText||e.getAttribute('aria-label')||e.value||'').trim().slice(0,80),className:String(e.className).slice(0,100)})),
  htmlSample:document.body.innerHTML.slice(0,1800),
  errors:[] }));
 console.log('UI-DIAGNOSTIC '+JSON.stringify({...s,errors:errs}));
 if(errs.length)throw Error(errs.join('|'));
 }finally{await b.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
