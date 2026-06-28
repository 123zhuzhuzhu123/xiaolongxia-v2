const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  page.on('console', msg => console.log('console:', msg.type(), msg.text()));
  page.on('pageerror', err => console.log('pageerror:', err.message));
  await page.goto('http://127.0.0.1:3001/dashboard', { timeout: 60000 });
  await page.waitForTimeout(5000);
  await page.screenshot({ path: '/tmp/dashboard_page.png', fullPage: true });
  console.log('screenshot saved');
  await browser.close();
})();
