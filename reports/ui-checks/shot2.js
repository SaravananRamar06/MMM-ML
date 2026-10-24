const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1600, height: 1000 }, colorScheme: 'dark' });
  await p.route('**/*', (r) => (r.request().method() === 'GET' ? r.continue() : r.abort()));
  await p.addInitScript(() => { localStorage.setItem('room-sidebar', 'rail'); localStorage.setItem('room-density', 'compact'); localStorage.setItem('room-context', 'shown'); localStorage.setItem('room-palette', 'ocean'); });
  await p.goto('http://127.0.0.1:8765/', { waitUntil: 'networkidle' }); await p.waitForTimeout(1500);
  await p.click('#view-toggle'); await p.waitForTimeout(300);
  await p.screenshot({ path: 'variant.png' });
  console.log(JSON.stringify(await p.evaluate(() => ({ feedW: document.getElementById('feed').getBoundingClientRect().width, vis: [...document.querySelectorAll('#feed .message')].filter((e) => { const r = e.getBoundingClientRect(); return r.top < innerHeight && r.bottom > 0; }).length, grouped: document.querySelectorAll('#feed .message.grouped').length, taH: document.getElementById('message').getBoundingClientRect().height }))));
  await b.close();
})();
