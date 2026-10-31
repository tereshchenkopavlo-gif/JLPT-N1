const { chromium }=require('playwright');
const { pathToFileURL }=require('node:url');
const path=require('node:path');
const url=pathToFileURL(path.resolve('release130/JLPT_N1_ukrainian_reading_v130.html')).href;
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:412,height:900}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(url);
  await page.locator('.nav-tab[data-view="cards"]').click();
  const snapshot=async(label)=>console.log('INTERACTION-DIAGNOSTIC '+JSON.stringify({label,...await page.evaluate(()=>({
   activeView:document.querySelector('.view.active')?.id,
   visibleButtons:[...document.querySelectorAll('.view.active button')].filter(x=>x.getClientRects().length).slice(0,40).map(x=>({id:x.id,text:x.innerText.trim().slice(0,60),className:x.className})),
   clickableItems:[...document.querySelectorAll('.view.active [onclick],.view.active [data-id],.view.active .item,.view.active .card-item')].slice(0,20).map(x=>({tag:x.tagName,id:x.id,className:String(x.className).slice(0,80),text:x.innerText?.trim().slice(0,60)})),
   visibleText:document.querySelector('.view.active')?.innerText.slice(0,700),
   compareStorage:localStorage.getItem('jlptN1CompareListUA_v1')
  }))})));
  await snapshot('cards-start');
  const candidates=page.locator('#view-cards [data-id],#view-cards .card-item,#view-cards .word-card,#view-cards .word-row');
  if(await candidates.count()){await candidates.first().click();await snapshot('after-first-card')}
  await page.locator('.nav-tab[data-view="compare"]').click();
  await snapshot('compare');
  console.log('INTERACTION-DIAGNOSTIC-ERRORS '+JSON.stringify(errors));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
