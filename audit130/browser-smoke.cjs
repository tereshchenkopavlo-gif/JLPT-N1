// Automated v130 browser smoke test. Does not certify linguistic accuracy.
const { chromium } = require('playwright');
const { pathToFileURL } = require('node:url');
const path = require('node:path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => {
    if (message.type() === 'error') errors.push(message.text());
  });
  const file = path.resolve('release130/JLPT_N1_ukrainian_reading_v130.html');
  try {
    await page.goto(pathToFileURL(file).href, { waitUntil: 'load', timeout: 45000 });
    await page.waitForTimeout(750);
    const data = await page.evaluate(() => {
      const bank = typeof readingBank === 'undefined' ? null : readingBank;
      if (!bank) throw new Error('readingBank not accessible: script failed to initialize');
      const medium = bank.medium?.length ?? 0;
      const long = bank.long?.length ?? 0;
      const questions = [...(bank.medium || []), ...(bank.long || [])].reduce((n, x) => n + (x.questions || []).length, 0);
      const hasApplication = document.body?.innerText?.trim().length > 100;
      return { medium, long, questions, hasApplication };
    });
    if (JSON.stringify([data.medium, data.long, data.questions]) !== JSON.stringify([59, 41, 241]))
      throw new Error('Incorrect reading counts: ' + JSON.stringify(data));
    if (!data.hasApplication) throw new Error('Application body is blank');
    if (errors.length) throw new Error('Browser errors: ' + errors.join(' | '));
    console.log('PASS v130 browser smoke', JSON.stringify(data));
  } finally {
    await browser.close();
  }
})().catch(err => { console.error(err); process.exitCode = 1; });
