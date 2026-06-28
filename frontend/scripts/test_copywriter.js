const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  page.on('console', msg => console.log('console:', msg.type(), msg.text()));
  page.on('pageerror', err => console.log('pageerror:', err.message));
  await page.goto('http://127.0.0.1:3001/copywriter');
  await page.waitForTimeout(15000);
  await page.screenshot({ path: '/tmp/copywriter_long.png', fullPage: true });
  console.log('screenshot saved');
  await browser.close();
})();
