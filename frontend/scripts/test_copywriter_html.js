const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  page.on('console', msg => console.log('console:', msg.type(), msg.text()));
  page.on('pageerror', err => console.log('pageerror:', err.message));
  await page.goto('http://127.0.0.1:3002/copywriter.html');
  await page.waitForTimeout(2000);
  await page.click('button[id^="btn-gen-"]');
  await page.waitForTimeout(8000);
  await page.screenshot({ path: '/tmp/copywriter_html_gen.png', fullPage: true });
  console.log('screenshot saved');
  await browser.close();
})();
