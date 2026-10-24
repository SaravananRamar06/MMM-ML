const { chromium } = require('playwright');
(async () => {
  const [, , name = 'room', width = '1600', height = '1000', mood = 'calm', theme = 'light'] = process.argv;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: +width, height: +height }, colorScheme: theme });
  // Safety: never let the screenshot session post anything.
  await page.route('**/*', (r) => (r.request().method() === 'GET' ? r.continue() : r.abort()));
  await page.addInitScript(([m]) => { try { localStorage.setItem('room-mood', m); } catch (e) {} }, [mood]);
  await page.goto('http://127.0.0.1:8765/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `${name}.png` });
  const m = await page.evaluate(() => {
    const r = (s) => { const e = document.querySelector(s); if (!e) return null; const b = e.getBoundingClientRect(); return [Math.round(b.x), Math.round(b.y), Math.round(b.width), Math.round(b.height)]; };
    const msgs = [...document.querySelectorAll('#feed .message')].map((e) => e.getBoundingClientRect()).filter((b) => b.top < innerHeight && b.bottom > 0);
    return { sidebar: r('.sidebar'), topbar: r('.topbar'), heading: r('.page-heading'), tools: r('.conversation-tools'), filters: r('#ai-filters'), latest: r('#latest-message'), feed: r('#feed'), firstMsg: r('#feed .message'), composer: r('#composer'), context: r('.context-pane'), visibleMessages: msgs.length };
  });
  console.log(JSON.stringify(m));
  await browser.close();
})();
