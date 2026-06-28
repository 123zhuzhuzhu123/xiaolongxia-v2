const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('http://127.0.0.1:3001/contents');
  await page.waitForTimeout(5000);
  await page.screenshot({ path: '/tmp/contents_page.png', fullPage: true });
  console.log('screenshot saved');
  await browser.close();
})();
