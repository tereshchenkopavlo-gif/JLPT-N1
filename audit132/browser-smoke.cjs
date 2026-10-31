// v132 browser smoke tests for both mobile and desktop; not a linguistic review.
const { chromium } = require('playwright');
const { pathToFileURL } = require('node:url');
const path = require('node:path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const fileUrl = pathToFileURL(path.resolve('release132/JLPT_N1_ukrainian_reading_v132.html')).href;
  try {
    for (const width of [360, 412, 1280]) {
      const page = await browser.newPage({ viewport: { width, height: 900 } });
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto(fileUrl, { waitUntil: 'load', timeout: 60000 });
      await page.waitForTimeout(350);
      const result = await page.evaluate(() => {
        // readingBank is scoped inside the application's script, not a window property.
        // Inspect the embedded JSON without assuming the application exports its internals.
        const source = Array.from(document.scripts, x => x.textContent || '').find(x => x.includes('const readingBank = {'));
        if (!source) throw new Error('Embedded readingBank source not found');
        const match = source.match(/const readingBank\s*=\s*(\{[^\n]*\});/);
        if (!match) throw new Error('Embedded readingBank JSON not found');
        const bank = JSON.parse(match[1]);
        const medium = bank.medium.length;
        const long = bank.long.length;
        const questions = [...bank.medium, ...bank.long].reduce((n, r) => n + r.questions.length, 0);
        const fresh = [...bank.medium, ...bank.long].filter(r => r.source === 'original_v132');
        const ids = new Set(fresh.map(r => r.id));
        const newQuestions = fresh.reduce((n, r) => n + r.questions.length, 0);
        const documentWidth = document.documentElement.scrollWidth;
        const viewportWidth = document.documentElement.clientWidth;
        return { medium, long, questions, fresh: fresh.length, newQuestions, ids: ids.size,
          documentWidth, viewportWidth, bodyChars: document.body.innerText.trim().length };
      });
      if (result.medium !== 87 || result.long !== 55 || result.questions !== 339 ||
          result.fresh !== 24 || result.newQuestions !== 56 || result.ids !== 24)
        throw new Error('Wrong content counts at width ' + width + ': ' + JSON.stringify(result));
      if (result.bodyChars < 100) throw new Error('App is blank at width ' + width);
      if (result.documentWidth > result.viewportWidth + 2)
        throw new Error('Horizontal overflow at width ' + width + ': ' + JSON.stringify(result));
      if (errors.length) throw new Error('JavaScript errors at width ' + width + ': ' + errors.join(' | '));
      console.log('PASS v132 browser smoke:', width, JSON.stringify(result));
      await page.close();
    }
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
