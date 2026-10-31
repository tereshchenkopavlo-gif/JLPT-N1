// v130 browser smoke tests for both mobile and desktop; not a linguistic review.
const { chromium } = require('playwright');
const { pathToFileURL } = require('node:url');
const path = require('node:path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const fileUrl = pathToFileURL(path.resolve('release130/JLPT_N1_ukrainian_reading_v130.html')).href;
  try {
    for (const width of [360, 412, 1280]) {
      const page = await browser.newPage({ viewport: { width, height: 900 } });
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto(fileUrl, { waitUntil: 'load', timeout: 60000 });
      await page.waitForTimeout(350);
      const result = await page.evaluate(() => {
        if (typeof readingBank === 'undefined') throw new Error('readingBank not initialized');
        const medium = readingBank.medium.length;
        const long = readingBank.long.length;
        const questions = [...readingBank.medium, ...readingBank.long].reduce((n, r) => n + r.questions.length, 0);
        const fresh = [...readingBank.medium, ...readingBank.long].filter(r => r.source === 'original_v130');
        const ids = new Set(fresh.map(r => r.id));
        const newQuestions = fresh.reduce((n, r) => n + r.questions.length, 0);
        const documentWidth = document.documentElement.scrollWidth;
        const viewportWidth = document.documentElement.clientWidth;
        return { medium, long, questions, fresh: fresh.length, newQuestions, ids: ids.size,
          documentWidth, viewportWidth, bodyChars: document.body.innerText.trim().length };
      });
      if (result.medium !== 59 || result.long !== 41 || result.questions !== 241 ||
          result.fresh !== 24 || result.newQuestions !== 56 || result.ids !== 24)
        throw new Error('Wrong content counts at width ' + width + ': ' + JSON.stringify(result));
      if (result.bodyChars < 100) throw new Error('App is blank at width ' + width);
      if (result.documentWidth > result.viewportWidth + 2)
        throw new Error('Horizontal overflow at width ' + width + ': ' + JSON.stringify(result));
      if (errors.length) throw new Error('JavaScript errors at width ' + width + ': ' + errors.join(' | '));
      console.log('PASS v130 browser smoke:', width, JSON.stringify(result));
      await page.close();
    }
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
